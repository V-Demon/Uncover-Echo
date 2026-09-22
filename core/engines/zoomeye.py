"""Client pour l'API ZoomEye."""
from .base import SearchEngineClient
from ..models import SearchResult


class ZoomEyeClient(SearchEngineClient):
    def __init__(self, name, config):
        super().__init__(name, config)
        self._token = None

    def _login(self):
        resp = self.session.post(
            self.config.get("endpoint_login"),
            json={
                "username": self.config.get("username"),
                "password": self.config.get("password"),
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        self._token = resp.json().get("access_token")
        self.session.headers.update({"API-KEY": self._token})

    def has_credentials(self) -> bool:
        return bool(self.config.get("username") and self.config.get("password"))

    def _raw_search(self, query, limit):
        if not self._token:
            self._login()
        resp = self.session.get(
            self.config.get("endpoint_search"),
            params={"query": query, "page": 1, "page_size": min(limit, 20)},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json().get("matches", [])[:limit]

    def _normalize(self, raw):
        info = raw.get("portinfo", {})
        return SearchResult(
            engine="zoomeye",
            ip=raw.get("ip", ""),
            port=int(info.get("port", 0)),
            product=info.get("product", "unknown"),
            version=str(info.get("version", "")),
            timestamp=raw.get("timestamp"),
            org=raw.get("org", ""),
            data=str(info.get("banner", ""))[:500],
            raw=raw,
        )
