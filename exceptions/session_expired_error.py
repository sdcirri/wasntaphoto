
from .app_error import AppError


class SessionExpiredError(AppError):
    status_code = 401
    detail = 'Session expired'
