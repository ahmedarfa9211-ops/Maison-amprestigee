"""Calendrier éditorial : quel sujet publier aujourd'hui, avec quels produits."""

from __future__ import annotations

import hashlib
import random
import re
import unicodedata
from datetime import date
from typing import Any


def slugifier(texte: str) -> str:
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = texte.lower().replace("'", "-").replace("’", "-")
    texte = re.sub(r"[^a-z0-9]+", "-", texte)
    return re.sub(r"-{2,}", "-", texte).strip("-")[:80]


class Calendrier:
    """File de sujets : les prioritaires d'abord, puis l'expansion combinatoire."""

    def __init__(self, sujets: dict[str, Any], produits: list[dict[str, Any]]):
        self.brut = sujets
        self.produits = produits
        self.categories = sujets["categories"]

    # ------------------------------------------------------------ expansion

    def _sujets_combines(self, annee: int) -> list[dict[str, Any]]:
        axes = self.brut["axes"]
        combines: list[dict[str, Any]] = []

        cibles = [("attribut", a) for a in axes["attributs"]]
        cibles += [("contexte", c) for c in axes["contextes"]]

        for genre, cible in cibles:
            for format_ in axes["formats"]:
                if genre == "contexte":
                    libelle = f"coiffeuse {cible['cle']}"
                    mot_cle = f"coiffeuse {cible['cle']}"
                else:
                    libelle = f"coiffeuse {cible['cle']}"
                    mot_cle = f"coiffeuse {cible['cle']}"

                titre = format_["gabarit"].format(attribut=libelle, annee=annee)
                titre = titre[0].upper() + titre[1:]
                identifiant = slugifier(f"{format_['prefixe']}-{cible['slug']}")

                combines.append(
                    {
                        "id": identifiant,
                        "titre": titre,
                        "mot_cle": mot_cle,
                        "secondaires": [
                            f"{mot_cle} avis",
                            f"acheter {mot_cle}",
                            f"{mot_cle} comparatif",
                        ],
                        "type": format_["type"],
                        "categorie": format_["categorie"],
                        "intention": format_["intention"],
                        "filtres": cible.get("filtres", []),
                    }
                )

        # Une question fréquente développée en article complet.
        for question in self.brut.get("questions_frequentes", []):
            combines.append(
                {
                    "id": slugifier("question-" + question),
                    "titre": question,
                    "mot_cle": question.rstrip(" ?").lower(),
                    "secondaires": [],
                    "type": "question",
                    "categorie": "questions",
                    "intention": "informationnelle",
                    "filtres": [],
                }
            )
        return combines

    def tous_les_sujets(self, annee: int | None = None) -> list[dict[str, Any]]:
        annee = annee or date.today().year
        vus: set[str] = set()
        file: list[dict[str, Any]] = []
        for sujet in self.brut["prioritaires"] + self._sujets_combines(annee):
            if sujet["id"] in vus:
                continue
            vus.add(sujet["id"])
            file.append(sujet)
        return file

    # ---------------------------------------------------------- sélection

    def prochain(self, deja_publies: list[str], sujet_force: str | None = None) -> dict[str, Any]:
        file = self.tous_les_sujets()
        if sujet_force:
            for sujet in file:
                if sujet["id"] == sujet_force:
                    return sujet
            raise SystemExit(f"Sujet inconnu : {sujet_force}")

        publies = set(deja_publies)
        for sujet in file:
            if sujet["id"] not in publies:
                return sujet

        # File épuisée : on repart sur le sujet le plus ancien, à réactualiser.
        rotation = file[len(publies) % len(file)]
        rotation = dict(rotation)
        rotation["id"] = f"{rotation['id']}-maj{date.today().year}"
        rotation["titre"] = f"{rotation['titre']} — mise à jour {date.today().year}"
        rotation["reactualisation"] = True
        return rotation

    # ----------------------------------------------------------- produits

    def produits_pour(self, sujet: dict[str, Any], nombre: int = 6) -> list[dict[str, Any]]:
        """Produits les plus pertinents pour le sujet, ordre stable et reproductible."""
        filtres = [f.lower() for f in sujet.get("filtres", [])]

        # Un accessoire (miroir d'appoint, tabouret, organiseur) ne doit jamais
        # ouvrir un comparatif de meubles : il ne concourt à armes égales que
        # si le sujet porte explicitement sur ce type de produit.
        SUJETS_ACCESSOIRES = {"accessoire", "organiseur", "tabouret", "rangement", "miroir", "led"}
        accessoires_pertinents = bool(SUJETS_ACCESSOIRES & set(filtres))

        def score(produit: dict[str, Any]) -> float:
            champs = (
                [produit.get("categorie", "")]
                + produit.get("tags", [])
                + produit.get("style", [])
                + produit.get("couleur", [])
                + [produit.get("gamme", "")]
            )
            champs = [str(c).lower() for c in champs]
            pertinence = sum(3 for f in filtres if f in champs)
            notes = produit.get("notes", {})
            qualite = sum(notes.values()) / max(len(notes), 1)
            total = pertinence * 10 + qualite
            if produit.get("categorie") == "accessoire" and not accessoires_pertinents:
                total -= 30
            return total

        # Graine déterministe : même sujet => même sélection, même ordre.
        graine = int(hashlib.md5(sujet["id"].encode()).hexdigest()[:8], 16)
        alea = random.Random(graine)

        # Exclusions éditoriales : un produit peut déclarer les angles de sujet
        # sur lesquels il n'a rien à faire (une coiffeuse de 60 kg n'a pas sa
        # place dans un comparatif « petit espace », même si elle est excellente).
        # Un produit en brouillon (ASIN enregistré mais fiche non documentée)
        # ne doit jamais partir en ligne : on le garde au catalogue, hors jeu.
        documentes = [p for p in self.produits if not p.get("brouillon")]

        eligibles = [
            p
            for p in documentes
            if not (set(f.lower() for f in p.get("exclut", [])) & set(filtres))
        ]
        if not eligibles:
            eligibles = list(documentes)

        classes = sorted(eligibles, key=lambda p: (-score(p), alea.random()))
        retenus = [p for p in classes if score(p) >= 10][:nombre]
        if len(retenus) < nombre:
            for produit in classes:
                if produit not in retenus:
                    retenus.append(produit)
                if len(retenus) >= nombre:
                    break
        return retenus[:nombre]

    # ------------------------------------------------------ maillage interne

    @staticmethod
    def articles_lies(
        sujet: dict[str, Any], publies: list[dict[str, Any]], nombre: int = 4
    ) -> list[dict[str, Any]]:
        """Articles existants les plus proches, pour le maillage interne."""
        mots_sujet = set(slugifier(sujet["mot_cle"]).split("-"))

        def proximite(article: dict[str, Any]) -> int:
            mots = set(slugifier(article.get("mot_cle", "")).split("-"))
            bonus = 2 if article.get("categorie") == sujet.get("categorie") else 0
            return len(mots_sujet & mots) + bonus

        candidats = [a for a in publies if a.get("id") != sujet.get("id")]
        candidats.sort(key=lambda a: (-proximite(a), a.get("date", "")), reverse=False)
        return candidats[:nombre]
