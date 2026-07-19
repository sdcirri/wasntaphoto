from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from argon2 import PasswordHasher

from sqlalchemy.exc import IntegrityError
from redis.asyncio import Redis
from hashlib import sha1
import secrets
import logging
import httpx
import time
import re

from exceptions import UsernameAlreadyTakenError, WeakPasswordError, BadAuthError, SessionExpiredError, FailedLoginError

from db.repositories import SessionRepository, UserRepository
from db.entities import UserModel, UserSessionModel

from exceptions.pwned_password_error import PwnedPasswordError


class AuthService:
    ph = PasswordHasher(
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        salt_len=16
    )
    logger = logging.getLogger('AuthService')
    user_repo: UserRepository
    session_repo: SessionRepository
    redis: Redis

    REDIS_HIBP_PREFIX = 'wasntaphoto:auth:hibp'
    REDIS_HIBP_TTL = 86400 * 7  # 7d
    REDIS_TOKEN_PREFIX = 'wasntaphoto:auth:tokens'
    REDIS_TOKEN_TTL = 60

    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository, redis: Redis) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.redis = redis

    async def hibp_lookup(self, password: str) -> bool:
        """
        Checks whether password was involved in a data breach
        calling the HIBP API
        :param password: plaintext password to be checked
        :return: whether password was found or not
        """
        sha1sum = sha1(password.encode()).hexdigest().upper()   # nosemgrep: python.lang.security.insecure-hash-algorithms.insecure-hash-algorithm-sha1 -- that's how HIBP API works ...
        prefix = sha1sum[:5]
        if (pwned := await self.redis.get(f'{self.REDIS_HIBP_PREFIX}:{prefix}')) is None:
            async with httpx.AsyncClient() as client:
                res = await client.get(f'https://api.pwnedpasswords.com/range/{prefix}')
                pwned = res.text
                await self.redis.set(f'{self.REDIS_HIBP_PREFIX}:{prefix}', pwned, ex=self.REDIS_HIBP_TTL)
        return any(prefix + l.split(':')[0].upper() == sha1sum for l in pwned.splitlines())

    @staticmethod
    def strong_password(password: str) -> bool:
        """
        Checks if the password is strong enough
        :param password: password to check
        :return: True if password is strong enough, False otherwise
        """
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        if not re.search(r'[^A-Za-z0-9]', password):
            return False
        return True

    async def yield_session(self, user_id: int) -> str:
        """
        Generates a valid session token
        :param user_id: user to be authorized
        :return: the token
        """
        while True:
            try:
                token = secrets.token_urlsafe(32)
                session = UserSessionModel(
                    user_id=user_id,
                    session_id=token,
                    valid_until=int(time.time()) + 604800   # 1 week
                )

                await self.session_repo.save(session)
                return token
            except IntegrityError:
                pass

    async def revoke_session(self, user_id: int, session: str) -> None:
        """
        Revokes a session token
        :param user_id: user whose session is to be revoked
        :param session: token to be revoked
        """
        if db_session := await self.session_repo.find_by_user_id_and_session_id(user_id, session):
            await self.session_repo.delete(db_session)
            await self.redis.delete(f'{self.REDIS_TOKEN_PREFIX}:{session}')

    async def login(self, username: str, password: str) -> str:
        """
        Validates user credentials and returns a bearer token
        for the requested user on valid credentials
        :param username: username
        :param password: password
        :return: the bearer token if the credentials are valid
        """
        if not (db_user := await self.user_repo.find_by_username(username)):
            raise FailedLoginError
        try:
            self.ph.verify(db_user.password, password)
        except VerifyMismatchError:
            raise FailedLoginError
        except (VerificationError, InvalidHashError):
            self.logger.getChild('login').critical(f'Malformed creds for user ID#{db_user.user_id}: "{db_user.password}"')
            raise FailedLoginError
        return await self.yield_session(db_user.user_id)

    async def register(self, username: str, password: str) -> str:
        """
        Registers a new user and issues an access token if the
        registration is successful. Currently, it may fail on two conditions:
            - username already taken
            - weak password
        :param username: new username
        :param password: chosen password
        :return: the new user's access token
        """
        if await self.user_repo.find_by_username(username):
            raise UsernameAlreadyTakenError

        if not self.strong_password(password):
            raise WeakPasswordError

        if await self.hibp_lookup(password):
            raise PwnedPasswordError

        db_user = UserModel(
            username=username,
            password=self.ph.hash(password)
        )
        db_user = await self.user_repo.save(db_user)
        return await self.yield_session(db_user.user_id)

    async def resolve_token(self, token: str) -> int:
        """
        Resolves a bearer token to the corresponding user ID, also
        prolonging the validity of the token
        :param token: bearer token
        :return: the corresponding user ID, if the token is valid
        """
        if cached := await self.redis.get(f'{self.REDIS_TOKEN_PREFIX}:{token}'):
            return int(cached)

        if not (session := await self.session_repo.find_by_id(token)):
            raise BadAuthError

        if session.valid_until < time.time():
            await self.session_repo.delete(session)
            raise SessionExpiredError

        session.valid_until = int(time.time()) + 604800
        await self.session_repo.save(session)
        await self.redis.set(f'{self.REDIS_TOKEN_PREFIX}:{token}', session.user_id, ex=self.REDIS_TOKEN_TTL)

        return session.user_id
