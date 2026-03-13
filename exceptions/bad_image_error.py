
from .app_error import AppError


class BadImageError(AppError):
    status_code = 400
    detail = 'Bad image'
