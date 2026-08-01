#!/usr/bin/env python3
"""Publication quotidienne automatisée — blog d'affiliation « coiffeuse ».

Usage courant :
    python publier.py                 # rédige l'article du jour et reconstruit le site
    python publier.py --nombre 7      # rédige 7 articles d'un coup (amorçage)
    python publier.py --sujet meilleure-coiffeuse
    python publier.py --mode local    # sans appel API
    python publier.py --site          # reconstruit le site sans rien rédiger
    python publier.py --sujets 20     # affiche les 20 prochains sujets prévus
    python publier.py --produits      # état du catalogue et des liens affiliés
    python publier.py --verifier      # contrôle qualité du site généré
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone

from src import redacteur, seo, site
from src.affiliation import Affiliation
from src.reglages import (
    articles_publies,
    charger_config,
    charger_etat,
    charger_produits,
    charger_sujets,
    sauver_article,
    sauver_etat,
)
from src.sujets import Calendrier, slugifier

PARIS = timezone(timedelta(hours=2))  # Europe/Paris, heure d'été


def _date_du_jour(decalage: int = 0) -> str:
    return (datetime.now(PARIS).date() - timedelta(days=decalage)).isoformat()


def _slug_unique(base: str, existants: set[str]) -> str:
    slug = base or "guide"
    if slug not in existants:
        return slug
    i = 2
    while f"{slug}-{i}" in existants:
        i += 1
    return f"{slug}-{i}"


# ------------------------------------------------------------------ publication


def publier_un(
    config: dict,
    calendrier: Calendrier,
    sujet_force: str | None = None,
    date_publication: str | None = None,
) -> dict:
    etat = charger_etat()
    publies = articles_publies()
    slugs = {a["slug"] for a in publies}

    sujet = calendrier.prochain([a["id"] for a in publies], sujet_force)
    produits = calendrier.produits_pour(sujet, config["publication"]["produits_par_comparatif"])
    lies = calendrier.articles_lies(sujet, publies, config["publication"]["articles_lies"])

    print(f"→ Sujet : {sujet['titre']}")
    print(f"  Mot-clé : {sujet['mot_cle']} | Format : {sujet['type']} | {len(produits)} produit(s)")

    contenu = redacteur.rediger(sujet, produits, lies, config)

    # Conformité Amazon : on retire les montants AVANT de compter les mots,
    # pour que le plancher de longueur porte sur le texte réellement publié.
    contenu = seo.retirer_montants(contenu)

    mots = seo.compter_mots(contenu)
    contenu = redacteur.completer_si_trop_court(contenu, mots, sujet, produits, config)
    mots = seo.compter_mots(contenu)

    slug = _slug_unique(slugifier(contenu.get("slug") or sujet["mot_cle"]), slugs)
    jour = date_publication or _date_du_jour()

    article = {
        "id": sujet["id"],
        "slug": slug,
        "date": jour,
        "date_maj": jour,
        "titre_h1": contenu["titre_h1"],
        "titre_seo": contenu["titre_seo"],
        "meta": seo.meta_description(contenu, sujet, config["seo"]["longueur_max_meta"]),
        "mot_cle": sujet["mot_cle"],
        "secondaires": sujet.get("secondaires", []),
        "categorie": sujet["categorie"],
        "type": sujet["type"],
        "mots": mots,
        "filtres": sujet.get("filtres", []),
        "produits": [p["id"] for p in produits],
        "lies": [a["slug"] for a in lies],
        "faq": contenu.get("faq", []),
        # On stocke le CONTENU, pas le HTML : le rendu est refait à chaque
        # build, donc un changement de tag d'affiliation se propage à tout
        # l'historique d'articles.
        "contenu": contenu,
        "source": contenu.get("_source", "?"),
    }
    article["titre_page"] = seo.titre_page(
        contenu, sujet, config["site"]["nom"], config["seo"]["longueur_max_titre"]
    )
    article["jsonld_selection"] = seo.schema_selection(article, produits)

    chemin = sauver_article(article)

    etat.setdefault("publies", []).append(
        {"id": sujet["id"], "slug": slug, "date": jour, "mots": mots}
    )
    etat["compteur"] = etat.get("compteur", 0) + 1
    etat["derniere_publication"] = jour
    sauver_etat(etat)

    marque = "✓" if mots >= config["publication"]["minimum_mots"] else "!"
    print(f"  {marque} {mots} mots · /{slug}/ · rédaction {article['source']}")
    print(f"    {chemin.name}")
    return article


def regenerer(config: dict, calendrier: Calendrier, produit_id: str) -> int:
    """Réécrit les articles qui présentent un produit dont la fiche a changé.

    Les avis produits sont figés dans chaque article au moment de sa rédaction.
    Après avoir corrigé une fiche dans data/produits.json (nouvel ASIN, vraies
    caractéristiques…), cette commande remet les textes concernés à jour, en
    conservant la date de publication, l'URL et le sujet d'origine.
    """
    articles = articles_publies()
    produits_par_id = {p["id"]: p for p in charger_produits()}
    articles_par_slug = {a["slug"]: a for a in articles}

    if produit_id == "tous":
        cibles = articles
    else:
        if produit_id not in produits_par_id:
            print(f"Produit inconnu : {produit_id}")
            return 1
        cibles = [a for a in articles if produit_id in a.get("produits", [])]

    if not cibles:
        print("Aucun article ne présente ce produit.")
        return 0

    print(f"{len(cibles)} article(s) à réécrire.\n")
    for article in cibles:
        sujet = {
            "id": article["id"],
            "titre": article["titre_h1"],
            "mot_cle": article["mot_cle"],
            "secondaires": article.get("secondaires", []),
            "type": article["type"],
            "categorie": article["categorie"],
            "intention": "commerciale",
            "filtres": article.get("filtres", []),
        }
        # Si le sujet a gardé ses filtres, on refait la sélection : un produit
        # dont la fiche s'est enrichie peut désormais mériter sa place ici.
        if article.get("filtres"):
            produits = calendrier.produits_pour(
                sujet, config["publication"]["produits_par_comparatif"]
            )
            article["produits"] = [p["id"] for p in produits]
        else:
            produits = [
                produits_par_id[i] for i in article.get("produits", []) if i in produits_par_id
            ]
        lies = [articles_par_slug[s] for s in article.get("lies", []) if s in articles_par_slug]

        print(f"→ {article['titre_h1']}")
        contenu = redacteur.rediger(sujet, produits, lies, config)
        contenu = seo.retirer_montants(contenu)
        mots = seo.compter_mots(contenu)
        contenu = redacteur.completer_si_trop_court(contenu, mots, sujet, produits, config)
        mots = seo.compter_mots(contenu)

        article["contenu"] = contenu
        article["mots"] = mots
        article["faq"] = contenu.get("faq", [])
        article["date_maj"] = _date_du_jour()
        article["source"] = contenu.get("_source", "?")
        article["jsonld_selection"] = seo.schema_selection(article, produits)
        article.pop("html", None)
        sauver_article(article)
        print(f"  ✓ {mots} mots · /{article['slug']}/\n")

    site.construire()
    return 0


# ---------------------------------------------------------------- diagnostics


def afficher_sujets(calendrier: Calendrier, nombre: int) -> None:
    publies = {a["id"] for a in articles_publies()}
    file = [s for s in calendrier.tous_les_sujets() if s["id"] not in publies]
    print(f"File d'attente : {len(file)} sujets non publiés\n")
    for i, sujet in enumerate(file[:nombre], 1):
        jour = (datetime.now(PARIS).date() + timedelta(days=i - 1)).isoformat()
        print(f"{jour}  [{sujet['type']:<14}] {sujet['titre']}")
        print(f"             mot-clé : {sujet['mot_cle']}")


def afficher_produits(config: dict) -> None:
    aff = Affiliation(config)
    produits = charger_produits()
    directs = sum(1 for p in produits if p.get("asin"))
    brouillons = [p for p in produits if p.get("brouillon")]
    print(f"Catalogue : {len(produits)} produits — {directs} lien(s) direct(s), "
          f"{len(produits) - directs} lien(s) de recherche")
    print(f"            {len(brouillons)} brouillon(s) exclu(s) de la publication\n")
    if config["affiliation"]["tag"].startswith("VOTRE-TAG"):
        print("  ⚠ Tag d'affiliation non configuré (config.json → affiliation.tag)\n")
    for produit in produits:
        if produit.get("brouillon"):
            etat = "BROUILLON"
        elif produit.get("asin"):
            etat = "direct   "
        else:
            etat = "recherche"
        print(f"  [{etat}] {produit['id']:<32} {produit['nom'][:42]}")
        print(f"              {aff.lien_produit(produit)}")
        if produit.get("brouillon"):
            print("              → en attente du titre et des puces descriptives")


def verifier(config: dict, strict: bool = False) -> int:
    """Contrôle qualité : longueur, liens, balises, données structurées.

    Par défaut ce contrôle est un RAPPORT, pas un barrage : il signale les
    points à corriger et rend la main avec un code de succès. Une simple
    remarque de rédaction ne doit jamais empêcher la publication du jour
    ni la mise en ligne du site — sinon un détail de style bloque toute la
    chaîne. Avec --strict, les avertissements redeviennent bloquants (utile
    en local, avant de valider une modification).
    """
    articles = site.rendre_tous(articles_publies(), config)
    if not articles:
        print("Aucun article publié.")
        return 1

    minimum = config["publication"]["minimum_mots"]
    tag = config["affiliation"]["tag"]
    problemes: list[str] = []

    # Garde-fou de conformité : le contrat Amazon Partenaires interdit
    # d'afficher un prix qui ne provient pas de la Product Advertising API.
    motif_prix = re.compile(r"\d[\d  .,]*\s*(?:€|EUR\b|euros?\b)", re.IGNORECASE)

    for a in articles:
        if a["mots"] < minimum:
            problemes.append(f"{a['slug']} : {a['mots']} mots (< {minimum})")
        if len(a["titre_page"]) > 70:
            problemes.append(f"{a['slug']} : title de {len(a['titre_page'])} caractères")
        if len(a["meta"]) > config["seo"]["longueur_max_meta"] + 5:
            problemes.append(f"{a['slug']} : meta de {len(a['meta'])} caractères")
        if not a["meta"]:
            problemes.append(f"{a['slug']} : meta-description vide")
        liens = a["html"].count("amazon.")
        tags = a["html"].count(f"tag={tag}")
        if liens == 0:
            problemes.append(f"{a['slug']} : aucun lien Amazon")
        elif tags < liens:
            problemes.append(f"{a['slug']} : {liens - tags} lien(s) Amazon sans tag d'affiliation")
        elif tags > liens:
            problemes.append(f"{a['slug']} : tag d'affiliation dupliqué ({tags} pour {liens} liens)")
        if "rel=\"sponsored nofollow noopener\"" not in a["html"]:
            problemes.append(f"{a['slug']} : attribut rel manquant sur les liens affiliés")
        if a["mot_cle"].split()[0].lower() not in a["titre_h1"].lower():
            problemes.append(f"{a['slug']} : mot-clé absent du H1")
        prix = motif_prix.findall(a["html"]) + motif_prix.findall(json.dumps(a, ensure_ascii=False))
        if prix:
            problemes.append(
                f"{a['slug']} : montant détecté ({prix[0].strip()}) — interdit par le contrat Amazon"
            )

    total_mots = sum(a["mots"] for a in articles)
    moyenne = total_mots // len(articles)
    print(f"Articles      : {len(articles)}")
    print(f"Mots au total : {total_mots:,}".replace(",", " "))
    print(f"Moyenne       : {moyenne} mots/article (plancher {minimum})")
    print(f"Liens Amazon  : {sum(a['html'].count('amazon.') for a in articles)}")
    print(f"Tag utilisé   : {tag}")

    if problemes:
        print(f"\n⚠ {len(problemes)} point(s) à corriger :")
        for p in problemes[:40]:
            print(f"  - {p}")
        # Remontée dans l'encadré « Annotations » de GitHub Actions : visible
        # d'un coup d'œil depuis un téléphone, sans ouvrir les journaux.
        print(f"::warning title=Contrôle qualité::{len(problemes)} point(s) à corriger — "
              f"{problemes[0]}")
        if strict:
            return 1
        print("  (avertissements non bloquants : le site est publié malgré tout)")
        return 0
    print("\n✓ Tous les contrôles passent.")
    return 0


# ------------------------------------------------------------------------ CLI


def main() -> int:
    ap = argparse.ArgumentParser(description="Publication quotidienne du blog coiffeuse.")
    ap.add_argument("--nombre", type=int, default=1, help="nombre d'articles à rédiger")
    ap.add_argument("--sujet", help="identifiant d'un sujet à forcer")
    ap.add_argument("--mode", choices=["api", "local"], help="mode de rédaction")
    ap.add_argument("--site", action="store_true", help="reconstruire le site uniquement")
    ap.add_argument("--sujets", nargs="?", type=int, const=20, help="afficher la file de sujets")
    ap.add_argument("--produits", action="store_true", help="état du catalogue produits")
    ap.add_argument("--verifier", action="store_true", help="contrôle qualité")
    ap.add_argument(
        "--strict", action="store_true", help="rend les avertissements bloquants"
    )
    ap.add_argument(
        "--regenerer",
        metavar="PRODUIT_ID",
        help="réécrit les articles présentant ce produit (ou « tous »)",
    )
    ap.add_argument("--modeles", action="store_true", help="lister les modèles API disponibles")
    ap.add_argument("--antidater", type=int, default=0, help="publier en remontant N jours")
    args = ap.parse_args()

    config = charger_config()
    if args.mode:
        config["redaction"]["mode"] = args.mode

    if args.modeles:
        import os

        cle = os.environ.get("ANTHROPIC_API_KEY", "")
        if not cle:
            print("ANTHROPIC_API_KEY absente.")
            return 1
        for modele in redacteur.modeles_disponibles(cle):
            print(" ", modele)
        return 0

    if args.produits:
        afficher_produits(config)
        return 0

    calendrier = Calendrier(charger_sujets(), charger_produits())

    if args.sujets is not None:
        afficher_sujets(calendrier, args.sujets)
        return 0

    if args.regenerer:
        return regenerer(config, calendrier, args.regenerer)

    if args.verifier:
        return verifier(config, strict=args.strict)

    if args.site:
        site.construire()
        return 0

    if config["affiliation"]["tag"].startswith("VOTRE-TAG"):
        print("⚠ Tag d'affiliation non configuré : les liens fonctionneront mais ne")
        print("  rapporteront rien. Renseignez config.json → affiliation.tag\n")

    # Un article qui échoue ne doit pas emporter toute la publication : on
    # signale, on continue, et on reconstruit le site avec ce qui existe.
    # Le site déjà en ligne reste ainsi toujours à jour et déployable.
    echecs = 0
    for i in range(args.nombre):
        jour = _date_du_jour(args.antidater - i if args.antidater else 0)
        try:
            publier_un(config, calendrier, args.sujet if i == 0 else None, jour)
        except Exception as erreur:  # noqa: BLE001
            echecs += 1
            print(f"  ! Article non publié : {type(erreur).__name__} — {erreur}")
            print(f"::warning title=Article non publié::{type(erreur).__name__} — {erreur}")
        print()

    site.construire()
    if echecs:
        print(f"⚠ {echecs} article(s) sur {args.nombre} n'ont pas pu être rédigés.")
        print("  Le site a tout de même été reconstruit et sera mis en ligne.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
