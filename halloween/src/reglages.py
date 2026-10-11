"""Chargement de la configuration et des données du projet."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DATA = RACINE / "data"
DOSSIER_SITE = RACINE / "site"
DOSSIER_ARTICLES = DOSSIER_DATA / "articles"

FICHIER_CONFIG = RACINE / "config.json"
FICHIER_PRODUITS = DOSSIER_DATA / "produits.json"
FICHIER_SUJETS = DOSSIER_DATA / "sujets.json"
FICHIER_ETAT = DOSSIER_DATA / "etat.json"


def _lire_json(chemin: Path) -> dict[str, Any]:
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def ecrire_json(chemin: Path, donnees: Any) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)


def charger_config() -> dict[str, Any]:
    """Config du projet, avec surcharge possible par variables d'environnement."""
    config = _lire_json(FICHIER_CONFIG)

    # Les variables d'environnement priment (pratique pour GitHub Actions).
    if os.environ.get("AMAZON_TAG"):
        config["affiliation"]["tag"] = os.environ["AMAZON_TAG"]
    if os.environ.get("SITE_URL"):
        config["site"]["url"] = os.environ["SITE_URL"].rstrip("/")
    if os.environ.get("SITE_NOM"):
        config["site"]["nom"] = os.environ["SITE_NOM"]
    if os.environ.get("MODE_REDACTION"):
        config["redaction"]["mode"] = os.environ["MODE_REDACTION"]

    config["site"]["url"] = config["site"]["url"].rstrip("/")
    return config


def charger_produits() -> list[dict[str, Any]]:
    return _lire_json(FICHIER_PRODUITS)["produits"]


def charger_sujets() -> dict[str, Any]:
    return _lire_json(FICHIER_SUJETS)


def charger_etat() -> dict[str, Any]:
    if FICHIER_ETAT.exists():
        return _lire_json(FICHIER_ETAT)
    return {"publies": [], "compteur": 0, "derniere_publication": None}


def sauver_etat(etat: dict[str, Any]) -> None:
    ecrire_json(FICHIER_ETAT, etat)


def articles_publies() -> list[dict[str, Any]]:
    """Tous les articles déjà rédigés, du plus récent au plus ancien."""
    DOSSIER_ARTICLES.mkdir(parents=True, exist_ok=True)
    articles = []
    for fichier in DOSSIER_ARTICLES.glob("*.json"):
        try:
            articles.append(_lire_json(fichier))
        except json.JSONDecodeError:
            print(f"  ! Article illisible ignoré : {fichier.name}")
    articles.sort(key=lambda a: (a.get("date", ""), a.get("id", "")), reverse=True)
    return articles


def sauver_article(article: dict[str, Any]) -> Path:
    DOSSIER_ARTICLES.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_ARTICLES / f"{article['date']}-{article['slug']}.json"
    ecrire_json(chemin, article)
    return chemin
