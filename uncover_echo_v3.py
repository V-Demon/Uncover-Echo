#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNCOVER-ECHO v3.1 — Multi-Engine OSINT Scanner
Agrège Shodan, Censys, FOFA et ZoomEye avec détection d'anomalies de
version/date dans les bannières de services.
"""
import argparse
import json
import logging
import sys
from pathlib import Path

from core.config_loader import ConfigBundle
from core.scanner import MultiEngineScanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="UNCOVER-ECHO v3.1")
    parser.add_argument("--gui", action="store_true", help="Mode interface graphique")
    parser.add_argument("--preset", help="Nom d'un preset défini dans config/presets.yaml")
    parser.add_argument("--query", "-q", help="Requête libre")
    parser.add_argument("--engine", "-e", nargs="+", help="Sous-ensemble de moteurs à interroger")
    parser.add_argument("--output", "-o", help="Chemin d'export JSON")
    parser.add_argument("--config-dir", default="config", help="Dossier de configuration")
    parser.add_argument("--limit", type=int, default=50, help="Nombre max de résultats par moteur")
    parser.add_argument("--no-anomalies", action="store_true",
                         help="Désactiver l'analyse d'anomalies de version/date")
    parser.add_argument("--verbose", "-v", action="store_true", help="Logs détaillés")
    return parser


def main():
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        config = ConfigBundle(args.config_dir)
    except (FileNotFoundError, ValueError) as e:
        print(f"Erreur de configuration : {e}", file=sys.stderr)
        sys.exit(1)

    if args.no_anomalies:
        config.transients["enabled"] = False

    if args.gui or (not args.preset and not args.query):
        import tkinter as tk
        from gui.app import UncoverEchoGUI
        root = tk.Tk()
        UncoverEchoGUI(root, config)
        root.mainloop()
        return

    scanner = MultiEngineScanner(config)

    try:
        if args.preset:
            report = scanner.scan_preset(args.preset, args.engine, limit=args.limit)
        else:
            report = scanner.scan(args.query, args.engine, limit=args.limit)
    except ValueError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)

    data = report.to_dict()
    print(json.dumps(data, indent=2, ensure_ascii=False))

    if args.output:
        Path(args.output).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8")
        print(f"\n[✓] Export : {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
