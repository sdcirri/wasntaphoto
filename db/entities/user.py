from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property
from sqlalchemy import BigInteger, String, select, func, Index

from ..engine import Base

from .following_relationship import FollowingRelationship


class UserModel(Base):
    """
    User DB persistence
    """
    __tablename__ = 'users'
    __table_args__ = (
        Index(
            'ix_users_username_trgm',
            'username',
            postgresql_using='gin',
            postgresql_ops={'username': 'gin_trgm_ops'}
        ),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    sessions = relationship('UserSessionModel', back_populates='user')
    followers = relationship(
        'FollowingRelationship',
        foreign_keys='FollowingRelationship.following_id',
        back_populates='following'
    )
    following = relationship(
        'FollowingRelationship',
        foreign_keys='FollowingRelationship.follower_id',
        back_populates='follower'
    )
    blocked = relationship(
        'BlockRelationship',
        foreign_keys='BlockRelationship.blocker_id',
        back_populates='blocker'
    )
    posts = relationship(
        'PostModel',
        back_populates='author'
    )

    followers_cnt = column_property(
        select(func.count())
            .where(FollowingRelationship.following_id == user_id)
            .correlate_except(FollowingRelationship)
            .scalar_subquery()
    )
    following_cnt = column_property(
        select(func.count())
            .where(FollowingRelationship.follower_id == user_id)
            .correlate_except(FollowingRelationship)
            .scalar_subquery()
    )
