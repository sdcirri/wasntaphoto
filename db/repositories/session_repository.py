from sqlalchemy import select

from db.entities import UserSessionModel

from .db_repository import DBRepository


class SessionRepository(DBRepository):
    """
    Repository for user sessions
    """

    async def find_all(self) -> list[UserSessionModel]:
        return list((await self.session.scalars(select(UserSessionModel))).all())

    async def find_by_id(self, session_id: str) -> UserSessionModel | None:
        return await self.session.scalar(
            select(UserSessionModel).where(UserSessionModel.session_id == session_id)
        )

    async def find_by_user_id(self, user_id: str) -> list[UserSessionModel]:
        return list((await self.session.scalars(
            select(UserSessionModel).where(UserSessionModel.user_id == user_id)
        )).all())

    async def save(self, session: UserSessionModel) -> None:
        await self.session.merge(session)

    async def delete(self, session: UserSessionModel) -> None:
       await self.session.delete(session)
