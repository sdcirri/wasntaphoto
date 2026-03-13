
from .app_error import AppError


class BadAuthError(AppError):
    status_code = 401
    detail = 'Bad authentication token'
