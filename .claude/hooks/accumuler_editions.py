#!/usr/bin/env python3
"""
accumuler_editions — hook PostToolUse (Edit | Write | MultiEdit)

Note simplement le chemin du fichier édité dans un fichier temporaire.
Ne lance aucun outil : tout le travail est reporté aux hooks Stop. C'est ce
qui évite de relancer un formateur + un typeur après CHAQUE édition.

Ne bloque jamais, ne parle jamais.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _fichiers_edites import fichier_accumulateur  # noqa: E402

# Extensions suivies : Python d'abord, plus quelques formats de config/contenu
# que le projet manipule (le formatage/typage éventuel filtrera lui-même).
EXT = re.compile(r"\.(py|pyi|json|toml|cfg|ini|md|css|html|js|ts)$", re.I)


def main():
    brut = sys.stdin.read(1024 * 1024)
    try:
        donnees = json.loads(brut or "{}")
        entree = donnees.get("tool_input") or {}
        chemin = entree.get("file_path") or entree.get("file") or ""
        if chemin and EXT.search(chemin):
            with open(fichier_accumulateur(), "a", encoding="utf-8") as fh:
                fh.write(os.path.abspath(chemin) + "\n")
    except Exception:
        # silencieux par conception : un hook PostToolUse ne doit rien casser
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
