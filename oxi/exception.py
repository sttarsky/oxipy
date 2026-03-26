from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from requests import HTTPError

_STATUS_MESSAGES: dict[int, str] = {
    401: "Unauthorized",
    403: "Forbidden",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}


class OxiAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        if self.status_code is not None:
            return f"OxiAPIError: {self.args[0]} (HTTP {self.status_code})"
        return f"OxiAPIError: {self.args[0]}"

    @classmethod
    def from_http_error(cls, e: "HTTPError", context: str = "") -> "OxiAPIError":
        status = e.response.status_code
        if status == 404:
            message = f"{context} not found" if context else "Not found"
        else:
            base = _STATUS_MESSAGES.get(status) or e.response.reason or f"HTTP {status}"
            message = f"{context}: {base}" if context else base
        return cls(message, status)
