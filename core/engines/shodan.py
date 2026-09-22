"""Client pour l'API Shodan."""
from .base import SearchEngineClient
from ..models import SearchResult


class ShodanClient(SearchEngineClient):
    def _raw_search(self, query, limit):
        resp = self.session.get(
            self.endpoint,
            params={"query": query, "key": self.api_key, "page": 1},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json().get("matches", [])[:limit]

    def _normalize(self, raw):
        return SearchResult(
            engine="shodan",
            ip=raw.get("ip_str", ""),
            port=int(raw.get("port", 0)),
            product=raw.get("product", "unknown"),
            version=str(raw.get("version", "")),
            timestamp=raw.get("timestamp"),
            org=raw.get("org", ""),
            data=str(raw.get("data", ""))[:500],
            raw=raw,
        )
