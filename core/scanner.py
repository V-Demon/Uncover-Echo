"""Orchestrateur multi-moteurs + analyse d'anomalies."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional

from .config_loader import ConfigBundle
from .models import ScanReport
from .transients import TransientAnalyzer
from .engines.shodan import ShodanClient
from .engines.censys import CensysClient
from .engines.fofa import FOFAClient
from .engines.zoomeye import ZoomEyeClient


ENGINE_REGISTRY = {
    "shodan": ShodanClient,
    "censys": CensysClient,
    "fofa": FOFAClient,
    "zoomeye": ZoomEyeClient,
}


class MultiEngineScanner:
    """Scanner multi-moteurs avec analyse d'anomalies intégrée."""

    def __init__(self, config: ConfigBundle):
        self.config = config
        self.transient_analyzer = TransientAnalyzer(config.transients)
        self.clients: Dict[str, object] = {}

        for name in config.get_enabled_engines():
            engine_cfg = config.get_engine_config(name)
            merged = {**config.engines.get("defaults", {}), **engine_cfg}
            cls = ENGINE_REGISTRY.get(name)
            if cls:
                self.clients[name] = cls(name, merged)

    def available_engines(self) -> List[str]:
        return list(self.clients.keys())

    # ------------------------------------------------------------------ #

    def scan(
        self,
        query: str,
        engines: Optional[List[str]] = None,
        limit: int = 50,
        preset_name: Optional[str] = None,
    ) -> ScanReport:
        """Scan générique avec une requête libre."""
        engines = [e for e in (engines or list(self.clients.keys())) if e in self.clients]
        report = ScanReport(
            scan_id=str(uuid.uuid4())[:8],
            started_at=datetime.now(timezone.utc).isoformat(),
            preset=preset_name,
            query=query,
            engines=engines,
        )

        for name in engines:
            client = self.clients[name]
            results = client.search(query, limit=limit)
            report.results_by_engine[name] = results

        self._analyze(report)
        report.finished_at = datetime.now(timezone.utc).isoformat()
        return report

    def scan_preset(
        self,
        preset_name: str,
        engines: Optional[List[str]] = None,
        limit: int = 50,
    ) -> ScanReport:
        """Scan via un preset défini dans config/presets.yaml."""
        preset = self.config.get_preset(preset_name)
        engines = [e for e in (engines or list(self.clients.keys())) if e in self.clients]

        report = ScanReport(
            scan_id=str(uuid.uuid4())[:8],
            started_at=datetime.now(timezone.utc).isoformat(),
            preset=preset_name,
            engines=engines,
            metadata={
                "description": preset.get("description", ""),
                "risk_level": preset.get("risk_level", "UNKNOWN"),
                "ports": preset.get("ports", []),
                "transients_only": preset.get("transients_only", False),
            },
        )

        for name in engines:
            client = self.clients[name]
            query = preset.get("queries", {}).get(name)
            if not query:
                continue
            results = client.search(query, limit=limit)
            report.results_by_engine[name] = results

        self._analyze(report)

        if preset.get("transients_only"):
            allowed_ips = {t.source_result.ip for t in report.transients if t.source_result}
            report.results_by_engine = {
                eng: [r for r in rs if r.ip in allowed_ips]
                for eng, rs in report.results_by_engine.items()
            }

        report.finished_at = datetime.now(timezone.utc).isoformat()
        return report

    def _analyze(self, report: ScanReport) -> None:
        all_results = [r for rs in report.results_by_engine.values() for r in rs]
        report.transients = self.transient_analyzer.analyze_batch(all_results)
