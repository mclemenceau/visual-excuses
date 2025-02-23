class VisualExcusesError(Exception):
    pass


class RequestError(VisualExcusesError):
    def __init__(self, status_code: int):
        self.status_code = status_code
        self.message = f"Request was not successful! Status code: {self.status_code}"
        super().__init__(self.message)

    def __str__(self):
        return self.message
