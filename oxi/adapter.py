from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class OxiAdapter(HTTPAdapter):
    def __init__(
        self,
        timeout: int | None = None,
        max_retries: int = 3,
        *args,
        **kwargs,
    ):
        self.timeout = timeout
        retry = Retry(total=max_retries, backoff_factor=0.3)
        super().__init__(*args, max_retries=retry, **kwargs)

    def send(self, request, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)
