"""Client pour l'API Censys."""
from .base import SearchEngineClient
from ..models import SearchResult


class CensysClient(SearchEngineClient):
    def _raw_search(self, query, limit):
        resp = self.session.post(
            self.endpoint,
            json={"q": query, "per_page": min(limit, 100)},
            auth=(self.config.get("api_id"), self.config.get("api_secret")),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json().get("result", {}).get("hits", [])[:limit]

    def _normalize(self, raw):
        services = raw.get("services", [{}])
        svc = services[0] if services else {}
        software = svc.get("software") or [{}]
        return SearchResult(
            engine="censys",
            ip=raw.get("ip", ""),
            port=int(svc.get("port", 0)),
            product=software[0].get("product", "unknown") if software else "unknown",
            version=software[0].get("version", "") if software else "",
            timestamp=raw.get("last_updated_at"),
            org=raw.get("autonomous_system", {}).get("name", ""),
            data=str(svc)[:500],
            raw=raw,
        )
