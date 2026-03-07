from sqlalchemy import BigInteger, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.engine import Base


class BlockRelationship(Base):
    """
    Blocking relationship between two users
    """
    __tablename__ = 'blocking'
    __table_args__ = (
        CheckConstraint('blocked_id != blocker_id', name='ck_no_self_block'),
    )

    blocked_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), primary_key=True)
    blocker_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), primary_key=True)

    blocked = relationship(
        'UserModel',
        foreign_keys=[blocked_id],
        uselist=False
    )

    blocker = relationship(
        'UserModel',
        foreign_keys=[blocker_id],
        uselist=False,
        back_populates='blocked'
    )
