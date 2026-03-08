from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey

from ..engine import Base


class PostLikeRelationship(Base):
    __tablename__ = 'post_like_relationship'

    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('posts.post_id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), primary_key=True)
