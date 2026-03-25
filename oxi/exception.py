from typing import Optional


class OxiAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        if self.status_code is not None:
            return f"OxiAPIError: {self.args[0]} (HTTP {self.status_code})"
        return f"OxiAPIError: {self.args[0]}"
