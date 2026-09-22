"""Classe de base pour les moteurs."""
from __future__ import annotations
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..models import SearchResult

logger = logging.getLogger(__name__)


class SearchEngineClient(ABC):
    """Client abstrait avec cache, rate limiting et retries."""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.api_key = config.get("api_key") or config.get("api_id")
        self.api_secret = config.get("api_secret") or config.get("password")
        self.endpoint = config.get("endpoint", "")
        self.timeout = int(config.get("timeout", 30))
        self.cache_ttl = int(config.get("cache_ttl", 1800))
        self.rate_limit = float(config.get("rate_limit", 1.0))
        self.simulate = bool(config.get("simulate_on_missing_key", False))
        self.max_retries = int(config.get("max_retries", 3))
        self.backoff_factor = float(config.get("backoff_factor", 0.5))

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.get("user_agent", "UNCOVER-ECHO/3.0")
        })
        retry = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self._cache: Dict[str, tuple] = {}
        self._last_call = 0.0

    def _throttle(self):
        """Rate limiting simple (thread non-safe : un client par thread recommandé)."""
        elapsed = time.time() - self._last_call
        wait = (1.0 / self.rate_limit) - elapsed if self.rate_limit > 0 else 0
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.time()

    def _cache_get(self, key: str) -> Optional[List[SearchResult]]:
        if key in self._cache:
            ts, data = self._cache[key]
            if time.time() - ts < self.cache_ttl:
                return data
        return None

    def _cache_set(self, key: str, data: List[SearchResult]):
        self._cache[key] = (time.time(), data)

    def has_credentials(self) -> bool:
        return bool(self.api_key)

    @abstractmethod
    def _raw_search(self, query: str, limit: int) -> List[Dict]:
        """Retourne la liste brute (non normalisée) de résultats."""
        raise NotImplementedError

    def search(self, query: str, limit: int = 50) -> List[SearchResult]:
        """API publique avec cache, throttle et repli en simulation."""
        cache_key = f"{self.name}:{query}:{limit}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        if not self.has_credentials() and self.simulate:
            results = self._simulate(query, limit)
            self._cache_set(cache_key, results)
            return results

        if not self.has_credentials():
            logger.warning("[%s] Pas de credentials configurés, requête ignorée.", self.name)
            return []

        self._throttle()
        try:
            raw = self._raw_search(query, limit)
            results = [self._normalize(r) for r in raw]
        except requests.exceptions.Timeout:
            logger.error("[%s] Timeout après %ss", self.name, self.timeout)
            results = []
        except requests.exceptions.RequestException as e:
            logger.error("[%s] Erreur réseau : %s", self.name, e)
            results = []
        except (KeyError, ValueError, IndexError) as e:
            logger.error("[%s] Erreur de parsing de la réponse : %s", self.name, e)
            results = []

        self._cache_set(cache_key, results)
        return results

    @abstractmethod
    def _normalize(self, raw: Dict) -> SearchResult:
        raise NotImplementedError

    def _simulate(self, query: str, limit: int) -> List[SearchResult]:
        """Simulation par défaut — résultats clairement marqués `simulated=True`."""
        import random
        import hashlib
        seed = int(hashlib.md5(query.encode()).hexdigest(), 16)
        rng = random.Random(seed)

        products = [
            ("kubernetes", 6443, "v1.28.4"),
            ("docker", 2375, "24.0.7"),
            ("jenkins", 8080, "2.426.1"),
            ("prometheus", 9090, "v2.47.0"),
            ("grafana", 3000, "10.1.0"),
        ]
        out = []
        for _ in range(min(limit, 20)):
            ip = f"{rng.randint(1,255)}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}"
            prod, port, ver = rng.choice(products)
            year = rng.choice([2026, 2026, 2075, 2075, 2099])
            ts = f"{year}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}T00:00:00Z"
            out.append(SearchResult(
                engine=self.name, ip=ip, port=port,
                product=prod, version=ver, timestamp=ts,
                org=rng.choice(["Google Cloud", "AWS", "Azure", "OVH"]),
                data=f"{prod} {ver}", simulated=True,
            ))
        return out
