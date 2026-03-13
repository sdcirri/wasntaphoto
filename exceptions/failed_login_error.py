
from .app_error import AppError


class FailedLoginError(AppError):
    status_code = 403
    detail = 'Login failed'
