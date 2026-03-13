
from .app_error import AppError


class CommentNotFoundError(AppError):
    status_code = 404
    detail = 'Comment not found'
