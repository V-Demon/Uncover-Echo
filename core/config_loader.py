"""Chargement et validation des configs YAML."""
from __future__ import annotations
import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict, Union


_ENV_PATTERN = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)\}')


def _expand_env(value: Any) -> Any:
    """Remplace ${VAR} par os.environ[VAR]. Laisse une chaîne vide si absente."""
    if isinstance(value, str):
        def repl(m):
            return os.environ.get(m.group(1), '')
        return _ENV_PATTERN.sub(repl, value)
    elif isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def load_yaml(path: Union[str, Path]) -> Dict:
    """Charge un YAML avec expansion des variables d'environnement."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config introuvable : {path}")
    try:
        with path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"YAML invalide dans {path} : {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"{path} doit contenir un mapping YAML au premier niveau")
    return _expand_env(data)


class ConfigBundle:
    """Bundle de toutes les configs, avec validation minimale au chargement."""

    REQUIRED_FILES = ("engines.yaml", "presets.yaml", "transients.yaml", "ui.yaml")

    def __init__(self, config_dir: Union[str, Path] = "config"):
        self.config_dir = Path(config_dir)
        missing = [f for f in self.REQUIRED_FILES if not (self.config_dir / f).exists()]
        if missing:
            raise FileNotFoundError(
                f"Fichiers de config manquants dans {self.config_dir} : {missing}"
            )

        self.engines = load_yaml(self.config_dir / "engines.yaml")
        self.presets = load_yaml(self.config_dir / "presets.yaml").get("presets", {})
        self.transients = load_yaml(self.config_dir / "transients.yaml")
        self.ui = load_yaml(self.config_dir / "ui.yaml")

        self._validate()

    def _validate(self) -> None:
        for name, cfg in self.engines.get("engines", {}).items():
            if cfg.get("enabled") and not cfg.get("endpoint") and "endpoint_search" not in cfg:
                raise ValueError(f"Moteur '{name}' activé sans endpoint défini")
        for name, preset in self.presets.items():
            if "queries" not in preset:
                raise ValueError(f"Preset '{name}' sans clé 'queries'")

    def get_preset(self, name: str) -> Dict:
        if name not in self.presets:
            raise ValueError(
                f"Preset '{name}' inconnu. Disponibles : {list(self.presets.keys())}"
            )
        return self.presets[name]

    def get_enabled_engines(self) -> list[str]:
        return [
            name for name, cfg in self.engines.get("engines", {}).items()
            if cfg.get("enabled")
        ]

    def get_engine_config(self, name: str) -> Dict:
        return self.engines.get("engines", {}).get(name, {})
