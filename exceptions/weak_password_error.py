
from .app_error import AppError


class WeakPasswordError(AppError):
    status_code = 400
    detail = 'Weak password'
