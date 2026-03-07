from sqlalchemy.orm import mapped_column, Mapped, relationship, column_property
from sqlalchemy import BigInteger, ForeignKey, String, DateTime, select, func
from datetime import datetime, timezone

from .like_relationship import LikeRelationship
from ..engine import Base


class PostModel(Base):
    __tablename__ = 'posts'

    post_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    caption: Mapped[str] = mapped_column(String(2048), nullable=True)
    pub_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    author = relationship('UserModel', uselist=False, back_populates='posts')

    like_cnt = column_property(
        select(func.count())
            .where(LikeRelationship.post_id == post_id)
            .correlate_except(LikeRelationship)
            .scalar_subquery()
    )
