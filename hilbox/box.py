import requests
from typing import Any, Dict

class Box:
    """
    Generic REST‐over‐HTTP client for any HIL box.
    """

    def __init__(self, host: str, timeout: float = 5.0):
        self.base = host.rstrip('/')
        self.session = requests.Session()
        self.timeout = timeout

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST JSON payload to `host + path` and return parsed JSON response.
        """
        url = f"{self.base}{path}"
        r = self.session.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
