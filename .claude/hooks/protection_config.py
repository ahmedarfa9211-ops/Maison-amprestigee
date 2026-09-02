#!/usr/bin/env python3
"""
protection_config — hook PreToolUse (Edit | Write | MultiEdit)

Bloque la modification d'une config de linter / formateur / typeur existante.
Un agent qui bute sur une règle a tendance à désactiver la règle plutôt qu'à
corriger le code : la config se dégrade silencieusement. Ce hook le renvoie
vers la source.

Créer une config qui n'existe pas encore reste autorisé (bootstrap légitime).

Codes de sortie : 0 = autorise, 2 = bloque.
Échappatoire ponctuelle : HOOKS_ALLOW_CONFIG_EDIT=1

Adapté de affaan-m/ECC (MIT), réécrit en Python sans dépendances.
`pyproject.toml` est volontairement exclu : il porte aussi les métadonnées et
les dépendances du projet, le bloquer casserait les ajouts légitimes.
"""

import json
import os
import re
import sys

MAX_STDIN = 1024 * 1024

PROTEGES = {
    # Ruff
    "ruff.toml", ".ruff.toml",
    # Flake8 / pycodestyle
    ".flake8",
    # Pylint
    ".pylintrc", "pylintrc",
    # isort
    ".isort.cfg",
    # mypy / pyright
    "mypy.ini", ".mypy.ini", "pyrightconfig.json",
    # yapf
    ".style.yapf",
    # Fichiers partagés portant souvent la config d'outils Python
    "setup.cfg", "tox.ini",
    # ---- Outils JS/TS (au cas où le projet en gagnerait un jour) ----
    ".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json",
    ".eslintrc.yml", ".eslintrc.yaml",
    "eslint.config.js", "eslint.config.mjs", "eslint.config.cjs",
    ".prettierrc", ".prettierrc.js", ".prettierrc.json",
    ".prettierrc.yml", ".prettierrc.yaml",
    "prettier.config.js", "prettier.config.cjs",
    "biome.json", "biome.jsonc",
    "tsconfig.json",
    # Note : pour protéger aussi la config du site, ajouter "config.json" ici.
    # Laissé hors liste par défaut car l'éditer (couleurs, tag Amazon…) est un
    # geste courant et légitime.
}


def decider(brut: str, tronque: bool):
    # Sur un payload tronqué on refuse plutôt que de laisser passer.
    if tronque:
        return (2, f"BLOQUÉ : entrée du hook > {MAX_STDIN} octets. "
                   "Refus de contourner protection_config sur un payload tronqué.")

    if re.match(r"^(1|true|yes)$", str(os.environ.get("HOOKS_ALLOW_CONFIG_EDIT", "")), re.I):
        return (0, None)

    try:
        donnees = json.loads(brut) if brut.strip() else {}
    except (ValueError, TypeError):
        return (0, None)

    entree = donnees.get("tool_input") or {}
    chemin = entree.get("file_path") or entree.get("file") or ""
    if not chemin:
        return (0, None)

    base = os.path.basename(chemin)
    if base not in PROTEGES and base.lower() not in PROTEGES:
        return (0, None)

    # Le fichier existe-t-il ? lstat plutôt qu'un simple exists : un EACCES ne
    # doit pas se traduire par « absent » et affaiblir silencieusement la garde.
    existe = True
    try:
        os.lstat(chemin)
    except FileNotFoundError:
        existe = False
    except OSError:
        existe = True  # erreur d'accès : on suppose présent, on protège

    if not existe:
        return (0, None)  # création initiale = bootstrap légitime

    return (2,
            f"BLOQUÉ : modification de {base} refusée.\n"
            "Corrige le code source pour satisfaire la règle au lieu "
            "d'affaiblir la config.\n"
            "Si le changement est légitime : relance avec HOOKS_ALLOW_CONFIG_EDIT=1.")


def main():
    brut = sys.stdin.read(MAX_STDIN + 1)
    tronque = len(brut) > MAX_STDIN
    if tronque:
        brut = brut[:MAX_STDIN]
    code, message = decider(brut, tronque)
    if message:
        sys.stderr.write(message + "\n")
    sys.exit(code)


if __name__ == "__main__":
    main()
