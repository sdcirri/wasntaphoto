from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..engine import Base


class CommentLikeRelationship(Base):
    __tablename__ = 'comment_like_relationship'

    comment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('comments.comment_id'), primary_key=True)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), primary_key=True)
