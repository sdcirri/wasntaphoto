from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, ForeignKey, String

from db.engine import Base


class UserSessionModel(Base):
    """
    Active user sessions
    """
    __tablename__ = 'user_sessions'

    session_id: Mapped[str] = mapped_column(String(43), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    valid_until: Mapped[int] = mapped_column(BigInteger, nullable=False)

    user = relationship('UserModel', back_populates='sessions', uselist=False)
