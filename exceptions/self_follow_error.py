
from .app_error import AppError


class SelfFollowError(AppError):
    status_code = 400
    detail = 'Cannot target yourself'
