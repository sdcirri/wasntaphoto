
class AppError(Exception):
    status_code: int = 500
    detail: str = 'Internal Server Error'

    def __init__(self, detail: str | None = None, status_code: int | None = None) -> None:
        self.status_code = self.__class__.status_code if status_code is None else status_code
        self.detail = self.__class__.detail if detail is None else detail
        super().__init__(self.detail)
