"""Client pour l'API FOFA."""
import base64
from urllib.parse import urlparse

from .base import SearchEngineClient
from ..models import SearchResult


class FOFAClient(SearchEngineClient):
    def _raw_search(self, query, limit):
        q_b64 = base64.b64encode(query.encode()).decode()
        resp = self.session.get(
            self.endpoint,
            params={
                "email": self.config.get("email"),
                "key": self.config.get("api_key"),
                "qbase64": q_b64,
                "size": min(limit, 100),
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise RuntimeError(data.get("errmsg", "Erreur FOFA"))
        return data.get("results", [])[:limit]

    def _normalize(self, raw):
        # FOFA renvoie une liste [host, ip, port, title, ...]
        host = raw[0] if isinstance(raw, list) and raw else ""
        ip, port = self._split_host_port(host)
        return SearchResult(
            engine="fofa",
            ip=ip,
            port=port,
            product=raw[3] if len(raw) > 3 else "unknown",
            version=str(raw[4]) if len(raw) > 4 else "",
            timestamp=None,
            org=raw[5] if len(raw) > 5 else "",
            data=raw[1] if len(raw) > 1 else "",
            raw={"raw": raw},
        )

    @staticmethod
    def _split_host_port(host: str):
        """Gère IPv4, IPv6 et URL."""
        if not host:
            return "", 0
        if "://" in host:
            p = urlparse(host)
            return p.hostname or "", p.port or 80
        if host.startswith("["):
            end = host.find("]")
            ip = host[1:end]
            port = int(host[end + 2:]) if len(host) > end + 2 else 0
            return ip, port
        if host.count(":") > 1:
            return host, 0
        if ":" in host:
            ip, p = host.rsplit(":", 1)
            try:
                return ip, int(p)
            except ValueError:
                return host, 0
        return host, 0
