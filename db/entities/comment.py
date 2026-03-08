from sqlalchemy import BigInteger, ForeignKey, String, DateTime, select, func
from sqlalchemy.orm import Mapped, mapped_column, column_property, relationship
from datetime import datetime, timezone

from . import CommentLikeRelationship

from ..engine import Base


class Comment(Base):
    __tablename__ = 'comments'

    comment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('posts.post_id'), nullable=False)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    content: Mapped[str] = mapped_column(String(2048), nullable=False)
    pub_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    post = relationship('PostModel', uselist=False, back_populates='comments')
    author = relationship('UserModel', uselist=False)

    like_cnt = column_property(
        select(func.count())
        .where(CommentLikeRelationship.comment_id == comment_id)
        .correlate_except(CommentLikeRelationship)
        .scalar_subquery()
    )
