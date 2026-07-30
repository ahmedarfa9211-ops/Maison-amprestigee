"""Rédaction de l'article du jour.

Deux modes :
  - "api"   : Claude rédige un texte unique (recommandé pour publier vraiment)
  - "local" : assemblage sans API, gratuit, pour tester ou dépanner

Dans les deux cas la sortie a la MÊME structure, et aucune URL n'est écrite
par le modèle : les liens sont fabriqués par src/affiliation.py.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from . import redaction_locale
from .sujets import slugifier

API_URL = "https://api.anthropic.com/v1/messages"
API_MODELES = "https://api.anthropic.com/v1/models"
VERSION_API = "2023-06-01"


# --------------------------------------------------------------------- API


def _appel_api(charge: dict[str, Any], cle: str, url: str = API_URL) -> dict[str, Any]:
    requete = urllib.request.Request(
        url,
        data=json.dumps(charge).encode("utf-8") if charge else None,
        headers={
            "x-api-key": cle,
            "anthropic-version": VERSION_API,
            "content-type": "application/json",
        },
        method="POST" if charge else "GET",
    )
    with urllib.request.urlopen(requete, timeout=600) as reponse:
        return json.loads(reponse.read().decode("utf-8"))


def modeles_disponibles(cle: str) -> list[str]:
    try:
        requete = urllib.request.Request(
            API_MODELES,
            headers={"x-api-key": cle, "anthropic-version": VERSION_API},
            method="GET",
        )
        with urllib.request.urlopen(requete, timeout=60) as reponse:
            donnees = json.loads(reponse.read().decode("utf-8"))
        return [m["id"] for m in donnees.get("data", [])]
    except Exception as erreur:  # noqa: BLE001
        print(f"  ! Impossible de lister les modèles : {erreur}")
        return []


def _modele_de_secours(cle: str) -> str | None:
    """Si le modèle configuré n'existe plus, on prend le meilleur Sonnet dispo."""
    modeles = modeles_disponibles(cle)
    for prefixe in ("claude-sonnet", "claude-opus", "claude-haiku", "claude-"):
        candidats = [m for m in modeles if m.startswith(prefixe)]
        if candidats:
            return sorted(candidats, reverse=True)[0]
    return None


# ------------------------------------------------------------------ PROMPT


def _fiche_produits(produits: list[dict[str, Any]]) -> str:
    lignes = []
    for i, p in enumerate(produits, 1):
        bloc = (
            f"{i}. id={p['id']} | nom exact = « {p['nom']} » | gamme : {p.get('gamme','')} | "
            f"styles : {', '.join(p.get('style', []))} | idéal pour : {p.get('pour_qui','')}\n"
            f"   atouts connus : {' / '.join(p.get('points_forts', []))}\n"
            f"   limites connues : {' / '.join(p.get('points_faibles', []))}"
        )
        specs = p.get("specs") or {}
        if specs:
            détail = " ; ".join(f"{cle} : {valeur}" for cle, valeur in specs.items())
            bloc += (
                f"\n   CARACTÉRISTIQUES VÉRIFIÉES (à exploiter précisément, "
                f"n'en invente aucune autre) : {détail}"
            )
        lignes.append(bloc)
    return "\n".join(lignes)


def construire_prompt(
    sujet: dict[str, Any],
    produits: list[dict[str, Any]],
    articles_lies: list[dict[str, Any]],
    config: dict[str, Any],
) -> str:
    objectif = config["publication"]["objectif_mots"]
    liens = "\n".join(f"- « {a['titre']} »" for a in articles_lies) or "- (aucun pour l'instant)"

    return f"""Tu es rédacteur SEO senior, spécialiste du mobilier de chambre et de l'aménagement d'intérieur. Tu écris pour un site français d'aide à l'achat sur une seule niche : la coiffeuse (meuble de maquillage).

# Article à écrire
Titre de travail : {sujet['titre']}
Mot-clé principal : {sujet['mot_cle']}
Mots-clés secondaires : {', '.join(sujet.get('secondaires', [])) or '(aucun)'}
Format : {sujet['type']}
Intention de recherche : {sujet['intention']}

# Produits du catalogue à traiter (dans cet ordre)
{_fiche_produits(produits)}

# Articles déjà publiés (à citer naturellement 2 à 4 fois dans le texte, par leur titre exact)
{liens}

# Exigences absolues
1. LONGUEUR : au minimum {objectif} mots de texte réel. C'est un plancher, pas une cible. Développe.
2. FRANÇAIS naturel, à la deuxième personne du pluriel, ton d'expert calme et concret. Zéro superlatif creux, zéro « dans le monde d'aujourd'hui », zéro phrase de remplissage.
3. CONCRET : donne des centimètres, des matériaux, des durées de montage, des gestes précis. Une hauteur de plateau de 75 cm, une profondeur de 40 cm, un tabouret 20 cm plus bas que le plateau : ce genre d'information est ce qui fait la valeur de l'article.
4. INTERDIT ABSOLU : n'écris jamais de prix, jamais de montant en euros, jamais d'URL, jamais de lien, jamais de note d'étoiles Amazon, jamais de nom de marque réelle. Parle des produits par leur « nom exact » donné ci-dessus, orthographié à l'identique — le système transforme ces mentions en liens.
5. SEO : place le mot-clé principal dans le titre, dans le chapeau, dans au moins deux titres de section (H2), et réparti naturellement dans le corps (densité raisonnable, jamais forcée). Utilise le champ lexical : dimensions, miroir, tiroirs, éclairage, tabouret, plateau, rangement, chambre, montage.
6. EXPÉRIENCE : intègre des observations d'usage réelles (ce qui gêne au quotidien, ce qu'on regrette après trois mois, ce qu'on vérifie avant de commander).
7. Ne mentionne jamais que tu es une IA, ne parle pas du processus de rédaction.

# Structure imposée
- 8 à 12 sections H2, chacune avec 3 à 6 paragraphes DENSES (4 phrases minimum par paragraphe).
- Au moins 3 sections doivent contenir une liste à puces utile (pas une liste de mots isolés : des puces d'une phrase complète).
- Un avis détaillé par produit du catalogue, dans l'ordre donné.
- Une FAQ de 8 questions que les gens tapent vraiment dans Google, avec des réponses de 3 à 5 phrases.
- Une conclusion qui tranche et recommande, sans relister tout l'article.

# Format de sortie
Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, sans balise de code. Schéma :

{{
  "titre_seo": "titre <title> de 55 caractères maximum, contenant le mot-clé",
  "titre_h1": "titre H1 de la page, différent du titre_seo, plus naturel",
  "meta": "méta-description de 150 caractères maximum, une promesse claire + le mot-clé",
  "chapeau": "paragraphe d'introduction de 90 à 130 mots qui pose le problème et annonce ce que l'article résout",
  "sections": [
    {{
      "titre": "Titre H2",
      "paragraphes": ["paragraphe 1", "paragraphe 2", "..."],
      "liste": ["puce complète", "..."],
      "encadre": {{"titre": "À retenir", "texte": "une information clé en 2 phrases"}}
    }}
  ],
  "avis_produits": [
    {{
      "produit_id": "identifiant exact du catalogue",
      "accroche": "en 8 mots, à qui ce modèle s'adresse",
      "verdict": "3 à 5 phrases d'analyse concrète",
      "points_forts": ["...", "...", "..."],
      "points_faibles": ["...", "..."],
      "ideal_pour": "une phrase"
    }}
  ],
  "faq": [{{"q": "question", "r": "réponse de 3 à 5 phrases"}}],
  "conclusion": "150 à 200 mots"
}}

Les champs "liste" et "encadre" sont facultatifs section par section. Écris maintenant, en visant la profondeur : un lecteur doit pouvoir commander sans consulter un autre site."""


# ---------------------------------------------------------------- RÉDACTION


def _extraire_json(texte: str) -> dict[str, Any]:
    texte = texte.strip()
    texte = re.sub(r"^```(?:json)?\s*", "", texte)
    texte = re.sub(r"\s*```$", "", texte)
    if not texte.startswith("{"):
        debut = texte.find("{")
        if debut == -1:
            raise ValueError("Aucun JSON trouvé dans la réponse.")
        texte = texte[debut:]
    fin = texte.rfind("}")
    if fin != -1:
        texte = texte[: fin + 1]
    return json.loads(texte)


def _rediger_api(
    sujet: dict[str, Any],
    produits: list[dict[str, Any]],
    articles_lies: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    cle = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not cle:
        raise RuntimeError("ANTHROPIC_API_KEY absente de l'environnement.")

    reglages = config["redaction"]
    modele = reglages["modele"]
    prompt = construire_prompt(sujet, produits, articles_lies, config)

    charge = {
        "model": modele,
        "max_tokens": reglages.get("max_tokens", 16000),
        "temperature": reglages.get("temperature", 1.0),
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "{"},  # force une sortie JSON
        ],
    }

    try:
        reponse = _appel_api(charge, cle)
    except urllib.error.HTTPError as erreur:
        detail = erreur.read().decode("utf-8", "ignore")
        if erreur.code in (400, 404) and "model" in detail.lower():
            secours = _modele_de_secours(cle)
            if not secours:
                raise
            print(f"  ! Modèle « {modele} » indisponible, bascule sur « {secours} ».")
            charge["model"] = secours
            reponse = _appel_api(charge, cle)
        else:
            raise RuntimeError(f"Erreur API {erreur.code} : {detail[:400]}") from erreur

    texte = "{" + "".join(bloc.get("text", "") for bloc in reponse.get("content", []))
    contenu = _extraire_json(texte)
    contenu["_source"] = f"api:{charge['model']}"
    return contenu


# ------------------------------------------------------------- ORCHESTRATION


def rediger(
    sujet: dict[str, Any],
    produits: list[dict[str, Any]],
    articles_lies: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    mode = config["redaction"]["mode"]

    if mode == "api":
        try:
            contenu = _rediger_api(sujet, produits, articles_lies, config)
        except Exception as erreur:  # noqa: BLE001
            print(f"  ! Rédaction API impossible ({erreur}). Bascule en mode local.")
            contenu = redaction_locale.rediger(sujet, produits, articles_lies, config)
    else:
        contenu = redaction_locale.rediger(sujet, produits, articles_lies, config)

    contenu.setdefault("titre_h1", sujet["titre"])
    contenu.setdefault("titre_seo", sujet["titre"])
    contenu.setdefault("meta", "")
    contenu.setdefault("slug", slugifier(sujet.get("mot_cle") or sujet["titre"]))
    return contenu


def completer_si_trop_court(
    contenu: dict[str, Any],
    mots_actuels: int,
    sujet: dict[str, Any],
    produits: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Ajoute des sections de fond tant que l'article n'atteint pas le plancher."""
    minimum = config["publication"]["minimum_mots"]
    if mots_actuels >= minimum:
        return contenu

    manquants = minimum - mots_actuels
    print(f"  + Article trop court de {manquants} mots : ajout de sections de fond.")
    supplements = redaction_locale.sections_supplementaires(sujet, produits, manquants)
    contenu["sections"] = list(contenu.get("sections", [])) + supplements
    return contenu
