from . import AppError

class PwnedPasswordError(AppError):
    status_code = 400
    detail = 'Password was involved in a data breach!'
