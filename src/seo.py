"""Optimisation SEO : métadonnées, données structurées, comptage."""

from __future__ import annotations

import html
import json
import re
from typing import Any

MOTIF_BALISE = re.compile(r"<[^>]+>")

# ------------------------------------------------- conformité Amazon : prix
#
# Le contrat Partenaires interdit d'afficher un prix qui ne provient pas de la
# Product Advertising API. Le prompt l'interdit déjà au rédacteur, mais un
# modèle peut glisser un montant malgré tout : on nettoie donc le contenu à
# chaque construction du site, avant publication. Aucun montant ne peut ainsi
# atteindre une page en ligne, même dans un article rédigé il y a des semaines.

_CHIFFRES = r"\d[\d\s.,]*"
_DEVISE = r"(?:€|EUR\b|euros?\b)"

# Locutions qui introduisent un montant : on les emporte avec lui, sinon la
# phrase reste bancale (« un budget de suffit largement »).
_AMORCE = (
    r"(?:\b(?:à partir de|aux alentours de|aux environs de|au-delà de|autour de|"
    r"sous la barre des|sous les|moins de|plus de|près de|jusqu'à|jusqu’à|"
    r"environ|compter|coûte|coûtent|vaut|valent|à|de|des|du|pour|dès|entre|vers)\s+)*"
)

MOTIF_MONTANT = re.compile(
    rf"{_AMORCE}{_CHIFFRES}\s*(?:et|à)\s*{_CHIFFRES}\s*{_DEVISE}"  # fourchette
    rf"|{_AMORCE}{_CHIFFRES}\s*{_DEVISE}"                          # montant simple
    rf"|(?:€|EUR)\s*{_CHIFFRES}\d",                                # symbole en tête
    re.IGNORECASE,
)

# Connecteur resté orphelin devant une ponctuation ou une fin de chaîne.
_ORPHELIN = re.compile(
    r"\s*\b(?:à partir|aux alentours|aux environs|au-delà|autour|sous|moins|plus|près|"
    r"jusqu|environ|entre|dès|vers|et|à|de|des|du|pour|d['’])"
    r"(?:\s+(?:de|à|des|les|qu['’]à|la barre des))?\s*(?=[,;:.…!?]|$)",
    re.IGNORECASE,
)

MOTIF_PHRASE = re.compile(r"(?<=[.!?…])\s+")
MOTIF_CLAUSE = re.compile(r"(?<=[,;:.!?…])\s+")


def _resserrer(texte: str) -> str:
    for _ in range(4):
        avant = texte
        texte = _ORPHELIN.sub("", texte)
        if texte == avant:
            break
    texte = re.sub(r"\(\s*\)|\[\s*\]", "", texte)
    texte = re.sub(r"[,;:]\s*([.!?…])", r"\1", texte)
    texte = re.sub(r"([,;:])\s*\1+", r"\1", texte)
    texte = re.sub(r"\s+([,.…])", r"\1", texte)
    # Typographie française : espace insécable avant les ponctuations doubles.
    texte = re.sub(r"\s*([;:!?])", " \\1", texte)
    texte = re.sub(r"\s{2,}", " ", texte)
    return texte.strip("  ,;:-–—\t\n")


def _nettoyer_chaine(texte: str) -> str:
    """Retire tout montant en euros en préservant un français correct.

    Trois filets successifs, du moins destructeur au plus sûr : on retire la
    phrase porteuse du montant ; sinon la proposition ; sinon le montant seul
    avec la locution qui l'introduisait.
    """
    if not texte or not MOTIF_MONTANT.search(texte):
        return texte

    for decoupe in (MOTIF_PHRASE, MOTIF_CLAUSE):
        morceaux = decoupe.split(texte)
        if len(morceaux) > 1:
            gardes = [m for m in morceaux if not MOTIF_MONTANT.search(m)]
            if gardes:
                return _resserrer(" ".join(gardes))

    return _resserrer(MOTIF_MONTANT.sub(" ", texte))


def retirer_montants(valeur: Any) -> Any:
    """Nettoie récursivement toute structure (dict, liste, chaîne)."""
    if isinstance(valeur, str):
        return _nettoyer_chaine(valeur)
    if isinstance(valeur, list):
        nettoyes = [retirer_montants(v) for v in valeur]
        # Une puce vidée de sa substance est retirée plutôt que laissée vide.
        return [v for v in nettoyes if not (isinstance(v, str) and not v.strip())]
    if isinstance(valeur, dict):
        return {cle: retirer_montants(v) for cle, v in valeur.items()}
    return valeur


def texte_brut(html_source: str) -> str:
    return MOTIF_BALISE.sub(" ", html_source)


def compter_mots(contenu: dict[str, Any]) -> int:
    """Nombre de mots réels de l'article (hors balises)."""
    morceaux: list[str] = [contenu.get("chapeau", ""), contenu.get("conclusion", "")]
    for section in contenu.get("sections", []):
        morceaux.append(section.get("titre", ""))
        morceaux.extend(section.get("paragraphes", []))
        morceaux.extend(section.get("liste", []) or [])
        encadre = section.get("encadre")
        if encadre:
            morceaux.append(encadre.get("texte", ""))
    for avis in contenu.get("avis_produits", []):
        morceaux.append(avis.get("verdict", ""))
        morceaux.append(avis.get("ideal_pour", ""))
        morceaux.extend(avis.get("points_forts", []))
        morceaux.extend(avis.get("points_faibles", []))
    for item in contenu.get("faq", []):
        morceaux.append(item.get("q", ""))
        morceaux.append(item.get("r", ""))
    return len(texte_brut(" ".join(m for m in morceaux if m)).split())


def tronquer(texte: str, longueur: int) -> str:
    texte = " ".join(texte.split())
    if len(texte) <= longueur:
        return texte
    coupe = texte[: longueur - 1].rsplit(" ", 1)[0]
    return coupe.rstrip(" ,;:") + "…"


def meta_description(contenu: dict[str, Any], sujet: dict[str, Any], limite: int) -> str:
    base = contenu.get("meta") or contenu.get("chapeau", "") or sujet["titre"]
    return tronquer(base, limite)


def titre_page(contenu: dict[str, Any], sujet: dict[str, Any], nom_site: str, limite: int) -> str:
    base = contenu.get("titre_seo") or sujet["titre"]
    base = tronquer(base, limite)
    suffixe = f" | {nom_site}"
    if len(base) + len(suffixe) <= 65:
        return base + suffixe
    return base


# ------------------------------------------------------ données structurées


def _jsonld(donnees: dict[str, Any]) -> str:
    return (
        '<script type="application/ld+json">'
        + json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )


def schema_article(article: dict[str, Any], config: dict[str, Any]) -> str:
    site = config["site"]
    url = f"{site['url']}/{article['slug']}/"
    return _jsonld(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article["titre_h1"][:110],
            "description": article["meta"],
            "inLanguage": site["langue"],
            "datePublished": article["date"],
            "dateModified": article.get("date_maj", article["date"]),
            "author": {"@type": "Organization", "name": site["auteur"], "url": site["url"]},
            "publisher": {
                "@type": "Organization",
                "name": site["nom"],
                "url": site["url"],
            },
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "url": url,
            "wordCount": article.get("mots", 0),
            "articleSection": article.get("categorie_nom", ""),
            "keywords": ", ".join([article["mot_cle"], *article.get("secondaires", [])]),
        }
    )


def schema_faq(article: dict[str, Any]) -> str:
    faq = article.get("faq") or []
    if not faq:
        return ""
    return _jsonld(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": item["r"]},
                }
                for item in faq
            ],
        }
    )


def schema_selection(article: dict[str, Any], produits: list[dict[str, Any]]) -> str:
    """ItemList : la sélection commentée, sans prix (interdits hors PA-API)."""
    if not produits:
        return ""
    return _jsonld(
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": article["titre_h1"],
            "numberOfItems": len(produits),
            "itemListOrder": "https://schema.org/ItemListOrderDescending",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": produit["nom"],
                    "description": produit.get("pour_qui", ""),
                }
                for i, produit in enumerate(produits, 1)
            ],
        }
    )


def schema_fil_ariane(article: dict[str, Any], config: dict[str, Any]) -> str:
    base = config["site"]["url"]
    return _jsonld(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Accueil", "item": base + "/"},
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": article.get("categorie_nom", "Guides"),
                    "item": f"{base}/categorie/{article['categorie']}/",
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": article["titre_h1"],
                    "item": f"{base}/{article['slug']}/",
                },
            ],
        }
    )


def schema_site(config: dict[str, Any]) -> str:
    site = config["site"]
    return _jsonld(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": site["nom"],
            "url": site["url"],
            "description": site["description"],
            "inLanguage": site["langue"],
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"{site['url']}/recherche/?q={{search_term_string}}",
                "query-input": "required name=search_term_string",
            },
        }
    )


# ------------------------------------------------------------------ en-tête


def balises_tete(
    titre: str,
    description: str,
    url_canonique: str,
    config: dict[str, Any],
    type_og: str = "article",
) -> str:
    site = config["site"]
    indexation = "index, follow" if config["seo"].get("indexation", True) else "noindex, nofollow"
    e = lambda t: html.escape(t, quote=True)  # noqa: E731
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="{indexation}">
<link rel="canonical" href="{e(url_canonique)}">
<meta property="og:type" content="{type_og}">
<meta property="og:site_name" content="{e(site['nom'])}">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="{e(titre)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(url_canonique)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titre)}">
<meta name="twitter:description" content="{e(description)}">
<meta name="theme-color" content="{e(site['couleur_principale'])}">
<link rel="alternate" type="application/rss+xml" title="{e(site['nom'])}" href="{e(site['url'])}/rss.xml">"""
