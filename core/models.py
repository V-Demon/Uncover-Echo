"""Modèles de données UNCOVER-ECHO."""
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    OMEGA = "OMEGA"       # anomalie hors-échelle


class TemporalStrate(str, Enum):
    PASSE_PROCHE = "passe_proche"
    PRESENT = "present"
    FUTUR_PROCHE = "futur_proche"
    FUTUR_LOINTAIN = "futur_lointain"
    OMEGA = "omega"
    INCONNU = "inconnu"


@dataclass
class SearchResult:
    """Résultat brut d'un moteur, normalisé."""
    engine: str
    ip: str
    port: int
    product: str = "unknown"
    version: str = ""
    timestamp: Optional[str] = None
    org: str = ""
    data: str = ""
    simulated: bool = False          # flag anti-confusion (données factices)
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TemporalAnomaly:
    """Anomalie de version/date détectée dans une bannière de service."""
    delta: float                      # score de distance normalisé (0..1)
    strate_origine: int               # année détectée dans la bannière
    strate_classe: TemporalStrate
    service_signature: str
    confidence: float                 # 0.0 -> 1.0
    signals_detected: List[str] = field(default_factory=list)
    source_result: Optional[SearchResult] = None

    @property
    def is_critical(self) -> bool:
        return self.delta < 0.4

    @property
    def is_omega(self) -> bool:
        return self.strate_classe == TemporalStrate.OMEGA

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['strate_classe'] = self.strate_classe.value
        d['is_critical'] = self.is_critical
        d['is_omega'] = self.is_omega
        return d


@dataclass
class ScanReport:
    """Rapport complet d'un scan."""
    scan_id: str
    started_at: str
    finished_at: Optional[str] = None
    preset: Optional[str] = None
    query: Optional[str] = None
    engines: List[str] = field(default_factory=list)
    results_by_engine: Dict[str, List[SearchResult]] = field(default_factory=dict)
    transients: List[TemporalAnomaly] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_results(self) -> int:
        return sum(len(r) for r in self.results_by_engine.values())

    @property
    def total_transients(self) -> int:
        return len(self.transients)

    def to_dict(self) -> Dict:
        return {
            'scan_id': self.scan_id,
            'started_at': self.started_at,
            'finished_at': self.finished_at,
            'preset': self.preset,
            'query': self.query,
            'engines': self.engines,
            'results_by_engine': {
                k: [r.to_dict() for r in v]
                for k, v in self.results_by_engine.items()
            },
            'transients': [t.to_dict() for t in self.transients],
            'summary': {
                'total_results': self.total_results,
                'total_transients': self.total_transients,
            },
            'metadata': self.metadata,
        }
