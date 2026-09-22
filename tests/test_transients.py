"""Tests unitaires pour TransientAnalyzer et FOFAClient._split_host_port."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.transients import TransientAnalyzer
from core.models import SearchResult
from core.engines.fofa import FOFAClient


BASE_CONFIG = {
    "enabled": True,
    "thresholds": {"critique": 0.4},
    "observation": {"annee_reference": 2075, "annee_min_passe": 1970},
    "signals": {
        "version_future": {"enabled": True, "regex": r"v?(\d{2,4})\.\d+"},
        "timestamp_futur": {"enabled": True},
        "cert_futur": {"enabled": True, "champs": ["not_valid_after"]},
        "incoherence_signature": {"enabled": True},
        "version_impossible": {"enabled": True},
    },
    "weights": {
        "version_future": 0.3, "timestamp_futur": 0.25, "cert_futur": 0.2,
        "incoherence_signature": 0.1, "version_impossible": 0.15,
    },
    "strates": {
        "present": [2026, 2027],
        "futur_lointain": [2051, 2099],
        "omega": [2100, 9999],
    },
}


def test_no_anomaly_on_normal_version():
    analyzer = TransientAnalyzer(BASE_CONFIG)
    r = SearchResult(engine="shodan", ip="1.2.3.4", port=6443,
                      product="kubernetes", version="v1.28.4")
    assert analyzer.analyze_one(r) is None


def test_detects_future_version():
    analyzer = TransientAnalyzer(BASE_CONFIG)
    r = SearchResult(engine="shodan", ip="1.2.3.4", port=2375,
                      product="docker", version="2075.1")
    anomaly = analyzer.analyze_one(r)
    assert anomaly is not None
    assert "version_future:2075" in anomaly.signals_detected


def test_disabled_analyzer_returns_empty():
    cfg = {**BASE_CONFIG, "enabled": False}
    analyzer = TransientAnalyzer(cfg)
    r = SearchResult(engine="shodan", ip="1.2.3.4", port=2375,
                      product="docker", version="2075.1")
    assert analyzer.analyze_batch([r]) == []


def test_fofa_split_host_port_ipv4():
    assert FOFAClient._split_host_port("1.2.3.4:8080") == ("1.2.3.4", 8080)


def test_fofa_split_host_port_ipv6():
    assert FOFAClient._split_host_port("[::1]:8080") == ("::1", 8080)


def test_fofa_split_host_port_url():
    ip, port = FOFAClient._split_host_port("https://example.com:8443/")
    assert ip == "example.com"
    assert port == 8443


def test_fofa_split_host_port_empty():
    assert FOFAClient._split_host_port("") == ("", 0)
