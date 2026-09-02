#!/usr/bin/env python3
"""
verifier_traces_debug — hook Stop

Signale les débogueurs oubliés dans les fichiers Python édités pendant la
réponse : `breakpoint()`, `pdb`/`ipdb`/`pudb.set_trace()`, `import pdb`…

Pourquoi PAS `print()` ? La version JS d'origine traque `console.log`. Son
équivalent direct ici serait `print()`, mais ce projet est un outil en ligne
de commande où `print()` EST la sortie légitime (des dizaines d'occurrences
voulues). Le vrai bruit à éliminer avant un commit, ce sont les points d'arrêt
de débogage — jamais destinés à être livrés. C'est donc eux qu'on cible.

Avertit sur stderr, ne bloque jamais (code 0).

Différences avec la version d'ECC dont il s'inspire :
 - analyse ligne par ligne au lieu d'un `includes()` global : une ligne
   commentée ou une occurrence dans une chaîne ne déclenche plus de faux
   positif ;
 - donne le numéro de ligne et un extrait ;
 - se limite aux fichiers réellement édités pendant la session ;
 - échappatoire par ligne : commentaire `allow-debug`.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _fichiers_edites import lire_nouveaux_fichiers  # noqa: E402

# Fichiers où un point d'arrêt est attendu / sans conséquence
EXCLUS = [
    re.compile(r"(^|[\\/])test_.*\.py$", re.I),
    re.compile(r"_test\.py$", re.I),
    re.compile(r"[\\/]tests?[\\/]", re.I),
    re.compile(r"[\\/]scripts[\\/]", re.I),
    re.compile(r"conftest\.py$", re.I),
]

EXT_SOURCE = re.compile(r"\.pyi?$", re.I)

# breakpoint()  |  pdb/ipdb/pudb.set_trace()  |  import pdb/ipdb/pudb
MOTIF = re.compile(
    r"\bbreakpoint\s*\(\)"
    r"|\b(?:pdb|ipdb|pudb)\s*\.\s*set_trace\s*\("
    r"|\bimport\s+(?:pdb|ipdb|pudb)\b"
)

MAX_SIGNALES = 15


def _sans_chaines(ligne: str) -> str:
    """Retire commentaires et littéraux de chaîne courants avant la recherche.
    Volontairement approximatif : éliminer le gros des faux positifs, pas
    parser Python."""
    l = re.sub(r"\\.", "", ligne)          # échappements
    l = re.sub(r"'[^']*'", "''", l)         # 'chaîne'
    l = re.sub(r'"[^"]*"', '""', l)         # "chaîne"
    l = re.sub(r"#.*$", "", l)              # # commentaire
    return l


def scanner(chemin: str) -> list:
    try:
        with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
            texte = fh.read()
    except OSError:
        return []
    if len(texte) > 2 * 1024 * 1024:  # fichier généré, on passe
        return []

    trouves = []
    for i, ligne in enumerate(texte.split("\n"), start=1):
        if "allow-debug" in ligne:  # échappatoire explicite
            continue
        if MOTIF.search(_sans_chaines(ligne)):
            trouves.append((i, ligne.strip()[:100]))
    return trouves


def main():
    fichiers = [
        f for f in lire_nouveaux_fichiers("debug")
        if EXT_SOURCE.search(f) and not any(re.search(x, f) for x in EXCLUS)
    ]
    if not fichiers:
        return

    rapport = []
    total = 0
    for fichier in fichiers:
        trouves = scanner(fichier)
        if not trouves:
            continue
        total += len(trouves)
        try:
            rel = os.path.relpath(fichier, os.getcwd())
        except ValueError:
            rel = fichier
        for numero, extrait in trouves:
            rapport.append(f"  {rel}:{numero}  {extrait}")

    if total == 0:
        return

    sortie = (
        f"[hook] {total} débogueur(s) oublié(s) dans les fichiers édités :\n"
        + "\n".join(rapport[:MAX_SIGNALES]) + "\n"
    )
    if len(rapport) > MAX_SIGNALES:
        sortie += f"  … et {len(rapport) - MAX_SIGNALES} de plus\n"
    sortie += ("  (à retirer avant commit — ajoute un commentaire "
               "'allow-debug' pour en garder un)\n")
    sys.stderr.write(sortie)


try:
    main()
except Exception as err:  # un hook Stop ne doit jamais bloquer la réponse
    sys.stderr.write(f"[hook] verifier_traces_debug ignoré : {err}\n")
sys.exit(0)
