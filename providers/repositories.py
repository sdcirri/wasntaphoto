from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from db.repositories import UserRepository, SessionRepository, FollowRepository, BlockRepository, PostRepository, \
    PostLikeRepository, CommentRepository, CommentLikeRepository

from .db import get_db_session


def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)


def get_session_repository(db: AsyncSession = Depends(get_db_session)) -> SessionRepository:
    return SessionRepository(db)


def get_follow_repository(db: AsyncSession = Depends(get_db_session)) -> FollowRepository:
    return FollowRepository(db)


def get_block_repository(db: AsyncSession = Depends(get_db_session)) -> BlockRepository:
    return BlockRepository(db)


def get_post_repository(db: AsyncSession = Depends(get_db_session)) -> PostRepository:
    return PostRepository(db)


def get_post_like_repository(db: AsyncSession = Depends(get_db_session)) -> PostLikeRepository:
    return PostLikeRepository(db)


def get_comment_repository(db: AsyncSession = Depends(get_db_session)) -> CommentRepository:
    return CommentRepository(db)


def get_comment_like_repository(db: AsyncSession = Depends(get_db_session)) ->CommentLikeRepository:
    return CommentLikeRepository(db)
