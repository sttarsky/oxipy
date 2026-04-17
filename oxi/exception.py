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


def _looks_like_node_not_found_html(e: "HTTPError") -> bool:
    resp = getattr(e, "response", None)
    if resp is None:
        return False
    try:
        content_type = (resp.headers or {}).get("Content-Type", "")
    except Exception:
        content_type = ""
    if "text/html" not in (content_type or "").lower():
        return False
    try:
        body = (resp.text or "")[:20_000]
    except Exception:
        return False
    return (
        "Oxidized::NodeNotFound" in body
        or "NodeNotFound" in body
        or "<title>Oxidized::NodeNotFound" in body
    )


class OxiAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    def __str__(self):
        if self.status_code is not None:
            return f"OxiAPIError: {self.args[0]} (HTTP {self.status_code})"
        return f"OxiAPIError: {self.args[0]}"

    @classmethod
    def from_http_error(cls, e: "HTTPError", context: str = "") -> "OxiAPIError":
        resp = getattr(e, "response", None)
        status = resp.status_code if resp is not None else None

        if status == 500 and _looks_like_node_not_found_html(e):
            status = 404

        if status == 404:
            message = f"{context} not found" if context else "Not found"
        else:
            base = (
                (_STATUS_MESSAGES.get(status) if status is not None else None)
                or (resp.reason if resp is not None else None)
                or (f"HTTP {status}" if status is not None else "Request failed")
            )
            message = f"{context}: {base}" if context else base
        return cls(message, status)
