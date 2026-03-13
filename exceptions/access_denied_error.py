
from .app_error import AppError


class AccessDeniedError(AppError):
    status_code = 403
    detail = 'Access denied'
