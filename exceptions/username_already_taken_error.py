
from .app_error import AppError


class UsernameAlreadyTakenError(AppError):
    status_code = 409
    detail = 'Username already taken'
