"""
_fichiers_edites — petit module partagé par les hooks Stop.
Python 3.9+, bibliothèque standard uniquement, aucune dépendance externe.

`accumuler_editions.py` (PostToolUse) écrit un chemin par ligne dans un
fichier temporaire propre à la session. Plusieurs hooks Stop veulent lire
cette liste, or si le premier à s'exécuter supprimait le fichier, les
suivants ne verraient rien — et l'ordre d'exécution des hooks n'est pas
garanti.

D'où le curseur : chaque consommateur mémorise sa propre position de lecture
dans un fichier `<accumulateur>.<nom du consommateur>`. Chacun ne voit donc
que ce qu'il n'a pas encore traité, indépendamment des autres et sans aucune
contrainte d'ordre.

Portage fidèle de la version Node d'origine (_edited-files.js).
"""

import hashlib
import os
import re
import tempfile


def fichier_accumulateur() -> str:
    """Chemin de l'accumulateur, propre à la session (ou au cwd à défaut)."""
    graine = os.environ.get("CLAUDE_SESSION_ID")
    if not graine:
        graine = hashlib.sha1(os.getcwd().encode("utf-8")).hexdigest()[:12]
    identifiant = re.sub(r"[^a-zA-Z0-9_-]", "_", graine)[:64]
    return os.path.join(tempfile.gettempdir(), f"edited-{identifiant}.txt")


def lire_nouveaux_fichiers(consommateur: str) -> list:
    """
    Fichiers ajoutés depuis le dernier passage de ce consommateur.
    Dédupliqués, existants, hors répertoires tiers / cache.

    consommateur : identifiant court et stable ("fmt", "debug"…).
    """
    fichier = fichier_accumulateur()
    cle = re.sub(r"[^a-z0-9_-]", "", str(consommateur), flags=re.I)
    curseur = f"{fichier}.{cle}"

    try:
        taille = os.stat(fichier).st_size
    except OSError:
        return []

    offset = 0
    try:
        with open(curseur, "r", encoding="utf-8") as fh:
            offset = int((fh.read().strip() or "0"))
    except (OSError, ValueError):
        pass  # premier passage

    if offset > taille:
        offset = 0  # accumulateur recréé entre-temps
    if offset == taille:
        return []

    try:
        with open(fichier, "r", encoding="utf-8") as fh:
            fh.seek(offset)
            morceau = fh.read()
    except OSError:
        return []

    try:
        with open(curseur, "w", encoding="utf-8") as fh:
            fh.write(str(taille))
    except OSError:
        pass  # non bloquant

    vus = set()
    resultat = []
    for ligne in morceau.split("\n"):
        chemin = ligne.strip()
        if not chemin or chemin in vus:
            continue
        vus.add(chemin)
        try:
            if not os.path.isfile(chemin):
                continue
        except OSError:
            continue
        parties = chemin.replace("\\", "/").split("/")
        if "node_modules" in parties or "__pycache__" in parties:
            continue
        if os.path.join(".claude", "plugins") in chemin:
            continue
        resultat.append(chemin)
    return resultat
