from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from argon2 import PasswordHasher
import secrets
import logging
import time
import re

from exceptions import UsernameAlreadyTakenError, WeakPasswordError, BadAuthError, SessionExpiredError, FailedLoginError

from db.repositories import SessionRepository, UserRepository
from db.entities import UserModel, UserSessionModel


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

    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo

    @staticmethod
    def strong_password(password: str) -> bool:
        """
        Checks if the password is strong enough
        :param password: password to check
        :return: True if password is strong enough, False otherwise
        """
        # Also prevent too long passwords
        if len(password) < 8 or len(password) > 255:
            return False
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
        while (token := secrets.token_urlsafe(32)) in await self.session_repo.find_all():
            pass

        session = UserSessionModel(
            user_id=user_id,
            session_id=token,
            valid_until=int(time.time()) + 604800   # 1 week
        )
        await self.session_repo.save(session)
        return token

    async def revoke_session(self, session: str) -> None:
        """
        Revokes a session token
        :param session: token to be revoked
        """
        if db_session := await self.session_repo.find_by_id(session):
            await self.session_repo.delete(db_session)

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
        if not (session := await self.session_repo.find_by_id(token)):
            raise BadAuthError
        if session.valid_until < time.time():
            await self.session_repo.delete(session)
            raise SessionExpiredError

        session.valid_until = int(time.time()) + 604800
        await self.session_repo.save(session)

        return session.user_id
