from sqlalchemy import BigInteger, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.engine import Base


class FollowingRelationship(Base):
    """
    Following relationship between two users
    """
    __tablename__ = 'following'
    __table_args__ = (
        CheckConstraint('follower_id != following_id', name='ck_no_self_follow'),
    )

    follower_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), primary_key=True)
    following_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), primary_key=True)

    follower = relationship(
        'UserModel',
        foreign_keys=[follower_id],
        uselist=False,
        back_populates='following'
    )

    following = relationship(
        'UserModel',
        foreign_keys=[following_id],
        uselist=False,
        back_populates='followers'
    )
