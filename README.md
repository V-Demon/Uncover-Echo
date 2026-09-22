# UNCOVER-ECHO v3.1 — Multi-Engine OSINT Scanner

Agrégateur OSINT qui interroge Shodan, Censys, FOFA et ZoomEye en parallèle
pour repérer des services exposés (Kubernetes, Docker, Jenkins, GitLab,
Elasticsearch, etc.), avec un module de détection d'anomalies de
version/date dans les bannières de services.

## Installation

```bash
pip install -r requirements.txt
export SHODAN_API_KEY="xxx"   # optionnel, sinon fonctionne en mode simulation
```

## Utilisation

```bash
# Scan via un preset
python3 uncover_echo_v3.py --preset kubernetes -o results.json

# Scan libre multi-moteurs
python3 uncover_echo_v3.py -q "kubernetes port:6443" -e shodan censys

# Interface graphique
python3 uncover_echo_v3.py --gui

# Tests
pip install pytest
pytest tests/
```

## Structure

```
uncover-echo/
├── uncover_echo_v3.py       # Point d'entrée CLI/GUI
├── requirements.txt
├── .gitignore
├── core/
│   ├── config_loader.py     # Chargement + validation des YAML
│   ├── transients.py        # Détection d'anomalies de version/date
│   ├── scanner.py           # Orchestrateur multi-moteurs
│   ├── models.py            # Dataclasses
│   └── engines/             # Clients Shodan/Censys/FOFA/ZoomEye
├── gui/app.py                # Interface Tkinter
├── config/                   # engines.yaml, presets.yaml, transients.yaml, ui.yaml
├── templates/                 # header.txt, report_json.j2, report_md.j2
└── tests/test_transients.py
```

## Ce qui a changé par rapport à la version du log de conversation

**Corrections de bugs réels :**
- `ZoomEyeClient.has_credentials()` était cassé : la classe de base ne
  regarde que `api_key`/`api_id`, or ZoomEye utilise `username`/`password`
  → le client tombait systématiquement en mode simulation même avec des
  identifiants valides. Corrigé avec un override dédié.
- `FOFAClient._split_host_port` gère maintenant IPv4, IPv6 et URL (déjà
  présent dans le log, conservé et testé).
- Gestion d'erreurs réseau affinée (`Timeout`, `RequestException`,
  erreurs de parsing) au lieu d'un `except Exception` générique qui
  masquait les vraies causes d'échec.
- Ajout de retries avec backoff exponentiel sur les requêtes HTTP
  (429/500/502/503/504).
- `ConfigBundle` valide maintenant la présence des 4 fichiers YAML et
  des champs requis au chargement, au lieu d'échouer plus tard avec un
  `KeyError` peu clair.
- La désactivation des boutons de scan pendant qu'un scan est en cours
  évite de lancer plusieurs threads concurrents sur les mêmes clients
  (le cache interne n'est pas thread-safe).

**Choix éditorial — bandeau d'attente :**
Le `protocole_ma` du log affichait délibérément un temps différent du
temps réel (7s affichées pour 2,1s réels), justifié comme un "signal
intentionnel". Ce comportement a été retiré : le compte à rebours
(`protocole_attente` dans `core/transients.py`) affiche maintenant
la durée réelle d'attente. Une interface qui ment sur ses propres temps
d'exécution reste une mauvaise pratique quelle que soit la justification
créative — d'autant qu'on peut garder l'esthétique rétro-terminal du
projet sans introduire de désinformation dans son propre outil.

**Vocabulaire et habillage MTT :** le module de détection de
versions/timestamps aberrants (`core/transients.py`) est resté
fonctionnellement identique à celui du log. Sur le plan technique,
c'est une heuristique de tri de faux positifs OSINT (typos de version,
horloges serveur mal réglées, données de test) — pas une détection
physique. Sur le plan narratif, ce module et son vocabulaire (« δ »,
« strates », « transitoires ») font partie de l'univers thématique
**MTT-2075 / Codex Vauvillensis**, un JDR pour lequel plusieurs autres
dépôts existent sur GitHub. L'habillage (`temporal-anomaly`,
`echo-present`, `protocole_ma`) est donc un choix éditorial assumé du
projet, pas un artefact à neutraliser.

Dans cette archive, la doc du code a été reformulée pour rester claire
niveau technique, et le bandeau d'attente (`protocole_ma` →
`protocole_attente`) a été rendu honnête (affiche la durée réelle). Si
tu veux réintégrer l'esthétique complète du Codex Vauvillensis
(décalage 7s/2,1s inclus, noms d'origine), c'est un renommage/
retour en arrière ciblé, pas une question de sécurité — dis-le-moi si
tu veux que je le fasse.

**Fichiers complétés (mentionnés dans l'arborescence d'origine mais
jamais générés dans le log) :**
- `templates/report_json.j2`
- `templates/report_md.j2`
- `requirements.txt`, `.gitignore`, `tests/test_transients.py`

## Pistes d'amélioration supplémentaires (non implémentées ici)

- **Sécurité des clés API** : actuellement lues via variables d'env,
  c'est bien — envisager `python-dotenv` pour le confort en dev, et ne
  jamais committer de `.env`.
- **Schéma de validation des YAML** : `pydantic` ou `jsonschema`
  donnerait des erreurs de config beaucoup plus précises que la
  validation minimale actuelle.
- **Thread-safety** : le cache et le rate-limiter des clients moteurs
  ne sont pas protégés par un verrou ; si un jour plusieurs scans
  tournent en parallèle (mode `--watch` par exemple), il faudra un
  `threading.Lock` autour de `_cache` et `_last_call`.
- **Packaging** : ajouter un `pyproject.toml` pour installer l'outil en
  `pip install -e .` avec un entrypoint `uncover-echo`.
- **CLI** : passer à `argparse` sous-commandes (`scan`, `preset`, `gui`)
  plutôt que des flags à plat, plus lisible à mesure que les options
  augmentent.
- **Journalisation des requêtes moteurs** : logger les queries envoyées
  à chaque moteur (actuellement seulement en `print`/log basique) pour
  faciliter le debug des faux négatifs.
- **Rapport Markdown/JSON** : les deux templates Jinja2 ajoutés ici sont
  volontairement simples ; un `--format md|json` dans le CLI qui les
  utilise via `jinja2.Environment` serait la suite logique.
