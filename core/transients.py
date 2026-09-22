"""
Détection d'anomalies de version/date dans les bannières de services.

Heuristique de tri de faux positifs OSINT : un service dont la version ou
le timestamp annoncé est incohérent avec le présent (numéro de version
"impossible", certificat daté dans le futur, etc.) produit souvent un
signal utile pour repérer des honeypots, des données de test, ou des
horloges serveur mal réglées. Le score `delta` est une heuristique
normalisée entre 0 et 1, pas une mesure physique.
"""
from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import List, Optional, Dict

from .models import SearchResult, TemporalAnomaly, TemporalStrate


class TransientAnalyzer:
    """Analyseur d'anomalies de version/date dans les bannières."""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.thresholds = config.get("thresholds", {})
        self.observation = config.get("observation", {})
        self.signals_cfg = config.get("signals", {})
        self.weights = config.get("weights", {})
        self.strates_cfg = config.get("strates", {})

        self.strate_ref = int(self.observation.get("annee_reference", 2075))
        self.tolerance_jours = int(self.observation.get("tolerance_jours", 30))
        self.annee_min_passe = int(self.observation.get("annee_min_passe", 1970))
        self.seuil_critique = float(self.thresholds.get("critique", 0.4))

        self._now = datetime.now(timezone.utc)

    # ------------------------------------------------------------------ #
    # API publique
    # ------------------------------------------------------------------ #

    def analyze_batch(self, results: List[SearchResult]) -> List[TemporalAnomaly]:
        """Analyse une liste de résultats, retourne les anomalies triées par delta."""
        if not self.enabled:
            return []
        anomalies = []
        for r in results:
            anomaly = self.analyze_one(r)
            if anomaly is not None:
                anomalies.append(anomaly)
        return sorted(anomalies, key=lambda a: a.delta)

    def analyze_one(self, result: SearchResult) -> Optional[TemporalAnomaly]:
        """Analyse un résultat unique."""
        signals = []
        weighted_delta = 0.0
        total_weight = 0.0
        detected_years = []

        if self.signals_cfg.get("version_future", {}).get("enabled"):
            year = self._detect_version_year(result.version, result.product)
            if year and year > self._now.year + 1:
                signals.append(f"version_future:{year}")
                detected_years.append(year)
                w = self.weights.get("version_future", 0.3)
                weighted_delta += self._delta_from_year(year) * w
                total_weight += w

        if self.signals_cfg.get("timestamp_futur", {}).get("enabled") and result.timestamp:
            ts_year = self._parse_year(result.timestamp)
            if ts_year and ts_year > self._now.year:
                signals.append(f"timestamp_futur:{ts_year}")
                detected_years.append(ts_year)
                w = self.weights.get("timestamp_futur", 0.25)
                weighted_delta += self._delta_from_year(ts_year) * w
                total_weight += w

        if self.signals_cfg.get("cert_futur", {}).get("enabled"):
            cert_year = self._extract_cert_year(result.raw)
            if cert_year and cert_year > self._now.year + 1:
                signals.append(f"cert_futur:{cert_year}")
                detected_years.append(cert_year)
                w = self.weights.get("cert_futur", 0.2)
                weighted_delta += self._delta_from_year(cert_year) * w
                total_weight += w

        if self.signals_cfg.get("version_impossible", {}).get("enabled"):
            if self._is_impossible_version(result.version, result.product):
                signals.append("version_impossible")
                w = self.weights.get("version_impossible", 0.5)
                weighted_delta += 0.1 * w
                total_weight += w

        if self.signals_cfg.get("incoherence_signature", {}).get("enabled"):
            if self._has_incoherent_signature(result):
                signals.append("incoherence_signature")
                w = self.weights.get("incoherence_signature", 0.1)
                weighted_delta += 0.3 * w
                total_weight += w

        if not signals or total_weight == 0:
            return None

        delta = weighted_delta / total_weight
        strate_annee = max(detected_years) if detected_years else self._now.year
        strate_classe = self._classify_strate(strate_annee)
        confidence = min(1.0, 0.5 + 0.15 * len(signals))

        return TemporalAnomaly(
            delta=round(delta, 4),
            strate_origine=strate_annee,
            strate_classe=strate_classe,
            service_signature=f"{result.product}:{result.version}".strip(":"),
            confidence=round(confidence, 3),
            signals_detected=signals,
            source_result=result,
        )

    # ------------------------------------------------------------------ #
    # Détecteurs internes
    # ------------------------------------------------------------------ #

    def _detect_version_year(self, version: str, product: str) -> Optional[int]:
        if not version:
            return None
        cfg = self.signals_cfg.get("version_future", {})
        regex = cfg.get("regex", r'v?(\d{2,4})\.\d+')

        m = re.search(regex, version)
        if not m:
            return None
        try:
            num = int(m.group(1))
        except (ValueError, IndexError):
            return None

        if 1970 <= num <= 2099:
            return num
        if num >= 2100:
            return num
        return None

    def _parse_year(self, timestamp: str) -> Optional[int]:
        if not timestamp:
            return None
        m = re.search(r'(\d{4})', timestamp)
        return int(m.group(1)) if m else None

    def _extract_cert_year(self, raw: Dict) -> Optional[int]:
        if not raw:
            return None
        import json
        blob = json.dumps(raw, default=str)
        for field_name in self.signals_cfg.get("cert_futur", {}).get("champs", []):
            m = re.search(rf'"{field_name}"[^,]*?(\d{{4}})', blob)
            if m:
                year = int(m.group(1))
                if year > self._now.year + 1:
                    return year
        return None

    def _is_impossible_version(self, version: str, product: str) -> bool:
        if not version or not product:
            return False
        m = re.search(r'(\d{3,4})', version)
        if not m:
            return False
        num = int(m.group(1))
        return num >= 100

    def _has_incoherent_signature(self, result: SearchResult) -> bool:
        if not result.data or not result.product:
            return False
        data_lower = result.data.lower()
        product_lower = result.product.lower()
        if product_lower not in data_lower and len(result.product) > 3:
            known = ['ssh', 'http', 'ftp', 'smtp', 'mysql', 'redis', 'mongodb']
            for k in known:
                if k in data_lower and k not in product_lower:
                    return True
        return False

    def _delta_from_year(self, year: int) -> float:
        """Score de distance normalisé par rapport à l'année de référence."""
        distance = abs(year - self.strate_ref)
        delta = distance / 50.0
        return max(0.0, min(1.0, delta))

    def _classify_strate(self, year: int) -> TemporalStrate:
        for name, bounds in self.strates_cfg.items():
            if isinstance(bounds, list) and len(bounds) == 2:
                if bounds[0] <= year <= bounds[1]:
                    return TemporalStrate(name)
        return TemporalStrate.INCONNU


# ---------------------------------------------------------------------- #
# Bandeau d'attente pendant un scan
# ---------------------------------------------------------------------- #

async def protocole_attente(config: Dict, log_fn=None) -> None:
    """
    Affiche un compte à rebours pendant l'appel aux moteurs.

    La durée affichée correspond toujours à la durée réelle d'attente :
    ce n'est plus paramétrable pour diverger (voir README, section
    "Correctifs v3.1" — l'ancien `protocole_ma` affichait délibérément
    un temps différent du temps réel, ce qui a été retiré).
    """
    import asyncio
    cfg = config.get("protocole_attente", config.get("protocole_ma", {}))
    if not cfg.get("enabled", True):
        return

    duree_reelle = float(cfg.get("duree_reelle_sec", 2.1))
    message = cfg.get("message", "Interrogation des moteurs en cours...")

    if log_fn:
        log_fn(f"[*] {message}", "info")

    steps = max(1, round(duree_reelle))
    step = duree_reelle / steps
    for i in range(steps, 0, -1):
        if log_fn:
            log_fn(f"⏳ {i * step:.1f}s restantes...", "warning")
        await asyncio.sleep(step)

    if log_fn:
        log_fn("✓ Terminé.\n", "success")
