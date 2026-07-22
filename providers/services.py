from redis.asyncio import Redis
from fastapi import Depends
from minio import Minio

from db.repositories import UserRepository, SessionRepository, FollowRepository, BlockRepository, PostRepository, \
    PostLikeRepository, CommentRepository, CommentLikeRepository
from service import AuthService, UserService, PostService, CommentService
from service.storage_service import StorageService

from .repositories import get_user_repository, get_session_repository, get_follow_repository, get_block_repository, \
    get_post_repository, get_post_like_repository, get_comment_repository, get_comment_like_repository
from .minio import get_minio_client
from .redis import get_redis


def get_auth_service(
        user_repo: UserRepository = Depends(get_user_repository),
        session_repo: SessionRepository = Depends(get_session_repository),
        redis: Redis = Depends(get_redis)
) -> AuthService:
    return AuthService(user_repo, session_repo, redis)


def get_storage_service(minio_client: Minio = Depends(get_minio_client)) -> StorageService:
    return StorageService(minio_client)


def get_user_service(
        user_repo: UserRepository = Depends(get_user_repository),
        follow_repo: FollowRepository = Depends(get_follow_repository),
        block_repo: BlockRepository = Depends(get_block_repository),
        storage_service: StorageService = Depends(get_storage_service)
) -> UserService:
    return UserService(user_repo, follow_repo, block_repo, storage_service)


def get_post_service(
        user_repo: UserRepository = Depends(get_user_repository),
        post_repo: PostRepository = Depends(get_post_repository),
        like_repo: PostLikeRepository = Depends(get_post_like_repository),
        block_repo: BlockRepository = Depends(get_block_repository),
        storage_service: StorageService = Depends(get_storage_service)
) -> PostService:
    return PostService(post_repo, user_repo, like_repo, block_repo, storage_service)


def get_comment_service(
        comment_repo: CommentRepository = Depends(get_comment_repository),
        like_repo: CommentLikeRepository = Depends(get_comment_like_repository)
) -> CommentService:
    return CommentService(comment_repo, like_repo)
