from typing import TYPE_CHECKING

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


class OxiError(Exception):
    """Base class for every error raised by oxipy.

    Catch this to handle any oxipy-specific failure in one place.
    """


class OxiConnectionError(OxiError):
    """A genuine transport/HTTP failure returned by the Oxidized server.

    Covers real server errors (5xx), auth problems (401/403), timeouts, etc.
    ``status_code`` holds the HTTP status when one is available.
    """

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        if self.status_code is not None:
            return f"{self.message} (HTTP {self.status_code})"
        return self.message


class NodeNotFoundError(OxiError):
    """The node does not exist in Oxidized.

    Oxidized signals this inconsistently: ``/node/show`` answers with an HTML
    error page (HTTP 500, title ``Oxidized::NodeNotFound``) or, in a well-behaved
    setup, a plain 404. Both are normalized to this exception.
    """


class ConfigNotAvailableError(OxiError):
    """The node exists but Oxidized returned no configuration to parse.

    Happens when ``/node/fetch`` responds with the plain-text body
    ``node not found`` (HTTP 200): the request succeeded, there is simply no
    backup to work with.
    """


class ConfigParseError(OxiError):
    """A configuration was fetched but could not be turned into a ``Device``.

    Raised when the TTP template did not yield the required sections or when the
    parsed data failed pydantic validation (the original error is kept in
    ``__cause__``).
    """


class UnknownModelError(OxiError):
    """The requested device model is not present in the parser registry."""


class TemplateError(OxiError):
    """The TTP template is missing or structurally invalid."""


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


def error_from_http(e: "HTTPError", context: str = "") -> OxiError:
    """Translate a ``requests.HTTPError`` into the right oxipy exception.

    A missing node (real 404 or Oxidized's 500 + ``NodeNotFound`` HTML page) is
    reported as :class:`NodeNotFoundError`; anything else becomes an
    :class:`OxiConnectionError` carrying the HTTP status code.
    """
    resp = getattr(e, "response", None)
    status = resp.status_code if resp is not None else None

    if status == 404 or (status == 500 and _looks_like_node_not_found_html(e)):
        message = f"{context} not found" if context else "Node not found"
        return NodeNotFoundError(message)

    base = (
        (_STATUS_MESSAGES.get(status) if status is not None else None)
        or (resp.reason if resp is not None else None)
        or (f"HTTP {status}" if status is not None else "Request failed")
    )
    message = f"{context}: {base}" if context else base
    return OxiConnectionError(message, status)
