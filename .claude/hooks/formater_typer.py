#!/usr/bin/env python3
"""
formater_typer — hook Stop

Lit la liste des fichiers Python édités pendant la réponse (écrite par
accumuler_editions.py) puis, en UN seul passage, groupé par racine de projet :
  1. formate via ruff ou black — un appel par racine
  2. lance mypy — un appel par racine (si mypy est configuré)

Les erreurs de type partent sur stderr : Claude les voit et peut corriger.
Ne bloque jamais (code 0), même si un outil manque ou échoue.

Résolution des outils : binaire sur le PATH, puis `python3 -m <outil>`.
Jamais d'installation : si l'outil est absent, le hook ne fait rien, en
silence. Un projet sans ruff/black/mypy configuré ne déclenche donc rien.

Idée reprise de affaan-m/ECC (MIT), réécrite en Python sans dépendances.
"""

import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _fichiers_edites import lire_nouveaux_fichiers  # noqa: E402

BUDGET_MS = 120_000  # budget total, large marge sous le timeout Stop
EXT_PY = re.compile(r"\.pyi?$", re.I)


def remonter(depart: str, marqueurs, profondeur_max: int = 25):
    """Remonte l'arborescence jusqu'à trouver l'un des `marqueurs`."""
    dossier = os.path.dirname(os.path.abspath(depart))
    racine = os.path.abspath(os.sep)
    i = 0
    while dossier and dossier != racine and i < profondeur_max:
        for m in marqueurs:
            if os.path.exists(os.path.join(dossier, m)):
                return dossier
        dossier = os.path.dirname(dossier)
        i += 1
    return None


def grouper(fichiers, fn):
    groupes = {}
    for f in fichiers:
        cle = fn(f)
        if not cle:
            continue
        groupes.setdefault(cle, []).append(f)
    return groupes


def _pyproject_contient(racine: str, section: str) -> bool:
    chemin = os.path.join(racine, "pyproject.toml")
    try:
        with open(chemin, "r", encoding="utf-8") as fh:
            return section in fh.read()
    except OSError:
        return False


def detecter_formateur(racine: str):
    """ruff si présent, sinon black, sinon rien."""
    if (os.path.exists(os.path.join(racine, "ruff.toml"))
            or os.path.exists(os.path.join(racine, ".ruff.toml"))
            or _pyproject_contient(racine, "[tool.ruff]")):
        return "ruff"
    if _pyproject_contient(racine, "[tool.black]"):
        return "black"
    return None


def mypy_configure(racine: str) -> bool:
    if (os.path.exists(os.path.join(racine, "mypy.ini"))
            or os.path.exists(os.path.join(racine, ".mypy.ini"))
            or _pyproject_contient(racine, "[tool.mypy]")):
        return True
    for nom in ("setup.cfg", "tox.ini"):
        chemin = os.path.join(racine, nom)
        try:
            with open(chemin, "r", encoding="utf-8") as fh:
                if "[mypy]" in fh.read():
                    return True
        except OSError:
            pass
    return False


def lancer(racine, outil, args, timeout_ms):
    """
    Exécute un outil : binaire sur le PATH, puis `python3 -m <outil>`.
    Jamais d'installation. Renvoie None si introuvable partout.
    """
    candidats = []
    exe = shutil.which(outil)
    if exe:
        candidats.append([exe, *args])
    candidats.append([sys.executable, "-m", outil, *args])

    for argv in candidats:
        try:
            return subprocess.run(
                argv, cwd=racine, capture_output=True, text=True,
                timeout=timeout_ms / 1000.0,
            )
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            return None
    return None


def main():
    fichiers = [f for f in lire_nouveaux_fichiers("fmt") if EXT_PY.search(f)]
    if not fichiers:
        return

    marqueurs = ("pyproject.toml", "setup.cfg", "ruff.toml", ".git")
    par_projet = grouper(fichiers, lambda f: remonter(f, marqueurs))
    if not par_projet:
        return

    tranche = max(15_000, BUDGET_MS // max(1, len(par_projet) * 2))

    # --- 1. formatage ---
    for racine, groupe in par_projet.items():
        fmt = detecter_formateur(racine)
        if not fmt:
            continue
        rel = [os.path.relpath(f, racine) for f in groupe]
        args = (["format", *rel] if fmt == "ruff" else [*rel])
        r = lancer(racine, fmt, args, tranche)
        if r is not None and r.returncode == 0:
            sys.stderr.write(f"[hook] {fmt} : {len(rel)} fichier(s) formaté(s)\n")
        if fmt == "ruff":
            # correction automatique des règles sûres
            lancer(racine, "ruff", ["check", "--fix", *rel], tranche)

    # --- 2. typecheck ---
    for racine, groupe in par_projet.items():
        if not mypy_configure(racine):
            continue
        rel = [os.path.relpath(f, racine) for f in groupe]
        r = lancer(racine, "mypy", rel, tranche)
        if r is None:
            continue
        sortie = f"{r.stdout or ''}{r.stderr or ''}".strip()
        if r.returncode != 0 and sortie:
            lignes = [l for l in sortie.split("\n") if re.search(r":\d+:.*error:", l)]
            if lignes:
                bloc = "\n".join("  " + l for l in lignes[:20])
                extra = (f"\n  … et {len(lignes) - 20} de plus"
                         if len(lignes) > 20 else "")
                sys.stderr.write(
                    f"[hook] mypy — {len(lignes)} erreur(s) de type dans "
                    f"{os.path.basename(racine)} :\n{bloc}{extra}\n"
                )


try:
    main()
except Exception as err:  # un hook Stop ne doit jamais bloquer la réponse
    sys.stderr.write(f"[hook] formater_typer ignoré : {err}\n")
sys.exit(0)
