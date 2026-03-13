
from .app_error import AppError


class PostNotFoundError(AppError):
    status_code = 404
    detail = 'Post not found'
