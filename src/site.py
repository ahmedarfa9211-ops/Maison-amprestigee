"""Construction du site statique complet (pages, sitemap, RSS, robots)."""

from __future__ import annotations

import html
import shutil
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any

from . import gabarits, seo
from .rendu import html_de_larticle
from .reglages import (
    DOSSIER_SITE,
    articles_publies,
    charger_config,
    charger_produits,
    charger_sujets,
)

e = lambda t: html.escape(str(t))  # noqa: E731
PAR_PAGE = 12


def _ecrire(chemin: Path, contenu: str) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")


def _nom_categorie(cle: str, categories: dict[str, str]) -> str:
    return categories.get(cle, cle.replace("-", " ").capitalize())


# ------------------------------------------------------------------ pages


def page_article(article: dict[str, Any], config: dict[str, Any], categories: dict[str, str]) -> str:
    url = f"{config['site']['url']}/{article['slug']}/"
    nom_cat = _nom_categorie(article["categorie"], categories)
    article["categorie_nom"] = nom_cat

    tete = seo.balises_tete(article["titre_page"], article["meta"], url, config, "article")
    jsonld = "".join(
        [
            seo.schema_article(article, config),
            seo.schema_faq(article),
            seo.schema_fil_ariane(article, config),
            article.get("jsonld_selection", ""),
        ]
    )

    corps = f"""{gabarits.fil_ariane([("Accueil", "/"), (nom_cat, f"/categorie/{article['categorie']}/"), (article['titre_h1'], None)])}
<article class="article"><div class="etroit">
  <h1>{e(article['titre_h1'])}</h1>
  <div class="meta-article">
    <a class="etiquette" href="/categorie/{e(article['categorie'])}/">{e(nom_cat)}</a>
    <span>Publié le {e(article['date'])}</span>
    <span>{article.get('mots', 0)} mots</span>
    <span>Lecture ≈ {max(1, article.get('mots', 0) // 220)} min</span>
  </div>
  {article['html']}
</div></article>"""
    return gabarits.page(config, article["titre_page"], tete, corps, jsonld)


def page_liste(
    config: dict[str, Any],
    articles: list[dict[str, Any]],
    categories: dict[str, str],
    titre: str,
    description: str,
    url_relative: str,
    page_num: int = 1,
    total_pages: int = 1,
    accueil: bool = False,
) -> str:
    base = config["site"]["url"]
    suffixe = "" if page_num == 1 else f"page/{page_num}/"
    url = f"{base}{url_relative}{suffixe}"
    tete = seo.balises_tete(
        titre if page_num == 1 else f"{titre} — page {page_num}",
        description,
        url,
        config,
        "website",
    )
    jsonld = seo.schema_site(config) if accueil else ""

    vignettes = "".join(
        gabarits.vignette(a, _nom_categorie(a["categorie"], categories)) for a in articles
    )

    nav = ""
    if total_pages > 1:
        liens = []
        for i in range(1, total_pages + 1):
            cible = url_relative if i == 1 else f"{url_relative}page/{i}/"
            if i == page_num:
                liens.append(f'<span class="actuelle">{i}</span>')
            else:
                liens.append(f'<a href="{e(cible)}">{i}</a>')
        nav = f'<nav class="pagination">{"".join(liens)}</nav>'

    corps = f"""<section class="hero"><div class="conteneur">
  <h1>{e(titre)}</h1><p>{e(description)}</p>
</div></section>
<div class="conteneur"><div class="grille">{vignettes}</div>{nav}</div>"""
    return gabarits.page(config, titre, tete, corps, jsonld)


def page_statique(
    config: dict[str, Any], titre: str, description: str, slug: str, contenu_html: str
) -> str:
    url = f"{config['site']['url']}/{slug}/"
    tete = seo.balises_tete(titre, description, url, config, "website")
    corps = f"""<section class="hero"><div class="conteneur"><h1>{e(titre)}</h1><p>{e(description)}</p></div></section>
<article class="article"><div class="etroit">{contenu_html}</div></article>"""
    return gabarits.page(config, titre, tete, corps)


# ------------------------------------------------------- fichiers techniques


def sitemap(config: dict[str, Any], articles: list[dict[str, Any]], categories: list[str]) -> str:
    base = config["site"]["url"]
    aujourdhui = datetime.now(timezone.utc).date().isoformat()
    urls = [(f"{base}/", aujourdhui, "daily", "1.0")]
    urls += [(f"{base}/tous-les-guides/", aujourdhui, "daily", "0.8")]
    urls += [(f"{base}/categorie/{c}/", aujourdhui, "daily", "0.7") for c in categories]
    urls += [(f"{base}/a-propos/", aujourdhui, "monthly", "0.3")]
    urls += [(f"{base}/mentions-legales/", aujourdhui, "yearly", "0.2")]
    urls += [
        (f"{base}/{a['slug']}/", a.get("date_maj", a["date"]), "monthly", "0.9") for a in articles
    ]

    entrees = "".join(
        f"<url><loc>{e(loc)}</loc><lastmod>{lastmod}</lastmod>"
        f"<changefreq>{freq}</changefreq><priority>{prio}</priority></url>"
        for loc, lastmod, freq, prio in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entrees}</urlset>"
    )


def rss(config: dict[str, Any], articles: list[dict[str, Any]]) -> str:
    s = config["site"]
    maintenant = format_datetime(datetime.now(timezone.utc))
    items = []
    for a in articles[:30]:
        try:
            publie = format_datetime(
                datetime.fromisoformat(a["date"]).replace(tzinfo=timezone.utc)
            )
        except ValueError:
            publie = maintenant
        lien = f"{s['url']}/{a['slug']}/"
        items.append(
            f"<item><title>{e(a['titre_h1'])}</title><link>{e(lien)}</link>"
            f"<guid isPermaLink=\"true\">{e(lien)}</guid>"
            f"<description>{e(a.get('meta', ''))}</description>"
            f"<pubDate>{publie}</pubDate></item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        f"<title>{e(s['nom'])}</title><link>{e(s['url'])}/</link>"
        f"<description>{e(s['description'])}</description>"
        f"<language>fr-fr</language><lastBuildDate>{maintenant}</lastBuildDate>"
        f"{''.join(items)}</channel></rss>"
    )


def robots(config: dict[str, Any]) -> str:
    if not config["seo"].get("indexation", True):
        return "User-agent: *\nDisallow: /\n"
    return (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {config['site']['url']}/sitemap.xml\n"
    )


# --------------------------------------------------------------- contenus fixes


def _html_a_propos(config: dict[str, Any]) -> str:
    s = config["site"]
    return f"""<p>{e(s['nom'])} est un site indépendant entièrement consacré à un seul meuble : la coiffeuse,
aussi appelée table de maquillage. L'objectif est simple : permettre de choisir un modèle adapté à sa pièce
et à son usage réel, sans passer trois soirées à comparer des fiches produit qui se ressemblent toutes.</p>

<h2>Comment nous travaillons</h2>
<p>Chaque guide part des mêmes critères objectifs : les dimensions réelles du meuble et l'espace de dégagement
qu'il exige, la qualité et l'épaisseur des matériaux, la capacité de rangement utile, la position et la
température de l'éclairage, la facilité de montage et la stabilité une fois installé.</p>
<p>Nous ne publions jamais de prix dans nos textes : ils changent en permanence et seule la page du marchand
fait foi. Les liens vous mènent directement à la fiche produit, où le prix et la disponibilité affichés
sont ceux du moment.</p>

<h2>Indépendance</h2>
<p>{e(config['affiliation']['mention_longue'])}</p>
<p>Aucune marque ne paie pour figurer dans nos sélections, et un modèle peut parfaitement être écarté d'un
comparatif si ses limites l'emportent sur ses qualités.</p>

<h2>Contact</h2>
<p>Une question, une erreur à signaler, une suggestion de guide : écrivez à
<a href="mailto:{e(s['email_contact'])}">{e(s['email_contact'])}</a>.</p>"""


def _html_mentions(config: dict[str, Any]) -> str:
    s = config["site"]
    return f"""<h2>Éditeur du site</h2>
<p>{e(s['nom'])} — contact : <a href="mailto:{e(s['email_contact'])}">{e(s['email_contact'])}</a>.</p>

<h2>Affiliation</h2>
<p>{e(config['affiliation']['mention_longue'])}</p>
<p>Les liens présents dans nos articles sont des liens affiliés. Si vous effectuez un achat après avoir
cliqué, nous percevons une commission versée par le marchand. Le prix que vous payez reste strictement
identique. Cette rémunération finance la production des guides et n'influence pas nos classements.</p>

<h2>Prix et disponibilité</h2>
<p>Les prix et la disponibilité des produits sont exacts à la date et à l'heure affichées sur la page du
marchand et peuvent changer à tout moment. Seules les informations présentes sur le site marchand au moment
de l'achat s'appliquent à la transaction.</p>

<h2>Contenu</h2>
<p>Les contenus publiés sont fournis à titre informatif. Malgré le soin apporté à leur rédaction, ils ne
sauraient constituer une garantie sur les caractéristiques exactes d'un produit, qui relèvent de la fiche
du fabricant et du marchand.</p>

<h2>Données personnelles</h2>
<p>Ce site ne collecte aucune donnée personnelle directement. Les liens sortants vers des sites marchands
sont susceptibles de déposer des cookies relevant de la politique de confidentialité de ces sites.</p>

<h2>Propriété intellectuelle</h2>
<p>L'ensemble des textes publiés sur {e(s['nom'])} est protégé. Toute reproduction intégrale sans
autorisation écrite est interdite.</p>"""


# ----------------------------------------------------------------- construction


def rendre_tous(articles: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    """Régénère le HTML de chaque article à partir du contenu stocké."""
    produits_par_id = {p["id"]: p for p in charger_produits()}
    articles_par_slug = {a["slug"]: a for a in articles}
    for article in articles:
        if "contenu" in article:
            article["html"] = html_de_larticle(article, config, produits_par_id, articles_par_slug)
        else:  # article d'une ancienne version : on se contente de retaguer
            from .affiliation import Affiliation

            article["html"] = Affiliation(config).reparer_urls_brutes(article.get("html", ""))
    return articles


def construire(verbeux: bool = True) -> dict[str, int]:
    config = charger_config()

    # Garde-fou de pré-lancement : tant que le site tourne sur l'adresse
    # provisoire github.io, on interdit l'indexation quoi que dise la config.
    # Dès qu'un vrai domaine est en place, l'indexation s'active toute seule.
    if ".github.io" in config["site"]["url"]:
        config["seo"]["indexation"] = False

    categories = charger_sujets()["categories"]
    articles = articles_publies()
    articles = rendre_tous(articles, config)

    if DOSSIER_SITE.exists():
        shutil.rmtree(DOSSIER_SITE)
    DOSSIER_SITE.mkdir(parents=True, exist_ok=True)

    # Articles
    for article in articles:
        article["titre_page"] = article.get("titre_page") or seo.titre_page(
            article, article, config["site"]["nom"], config["seo"]["longueur_max_titre"]
        )
        _ecrire(DOSSIER_SITE / article["slug"] / "index.html", page_article(article, config, categories))

    # Accueil paginé
    total_pages = max(1, (len(articles) + PAR_PAGE - 1) // PAR_PAGE)
    for numero in range(1, total_pages + 1):
        lot = articles[(numero - 1) * PAR_PAGE : numero * PAR_PAGE]
        html_page = page_liste(
            config,
            lot,
            categories,
            config["site"]["nom"],
            config["site"]["description"],
            "/",
            numero,
            total_pages,
            accueil=True,
        )
        cible = DOSSIER_SITE / "index.html" if numero == 1 else DOSSIER_SITE / "page" / str(numero) / "index.html"
        _ecrire(cible, html_page)

    # Toutes les publications
    _ecrire(
        DOSSIER_SITE / "tous-les-guides" / "index.html",
        page_liste(
            config,
            articles,
            categories,
            "Tous les guides",
            "L'intégralité de nos comparatifs, guides d'achat et articles sur la coiffeuse.",
            "/tous-les-guides/",
        ),
    )

    # Catégories
    for cle, nom in categories.items():
        lot = [a for a in articles if a.get("categorie") == cle]
        _ecrire(
            DOSSIER_SITE / "categorie" / cle / "index.html",
            page_liste(
                config,
                lot,
                categories,
                nom,
                f"Tous nos contenus de la rubrique {nom.lower()} consacrés à la coiffeuse.",
                f"/categorie/{cle}/",
            ),
        )

    # Pages fixes
    _ecrire(
        DOSSIER_SITE / "a-propos" / "index.html",
        page_statique(
            config,
            "À propos",
            "Qui nous sommes, comment nous sélectionnons les modèles et comment le site est financé.",
            "a-propos",
            _html_a_propos(config),
        ),
    )
    _ecrire(
        DOSSIER_SITE / "mentions-legales" / "index.html",
        page_statique(
            config,
            "Mentions légales",
            "Éditeur, affiliation, prix et disponibilité, données personnelles.",
            "mentions-legales",
            _html_mentions(config),
        ),
    )

    # 404
    _ecrire(
        DOSSIER_SITE / "404.html",
        page_statique(
            config,
            "Page introuvable",
            "Cette page n'existe pas ou plus.",
            "404",
            '<p>La page demandée est introuvable. <a href="/">Retour à l\'accueil</a> ou '
            '<a href="/tous-les-guides/">voir tous les guides</a>.</p>',
        ),
    )

    # Domaine personnalisé : GitHub Pages a besoin d'un fichier CNAME à la
    # racine du site publié. Comme ce dossier est reconstruit à chaque fois,
    # on le régénère ici à partir de l'adresse configurée.
    hote = config["site"]["url"].split("//", 1)[-1].split("/", 1)[0]
    if hote and not hote.endswith(".github.io"):
        _ecrire(DOSSIER_SITE / "CNAME", hote + "\n")

    # Fichiers techniques
    if config["seo"].get("generer_sitemap", True):
        _ecrire(DOSSIER_SITE / "sitemap.xml", sitemap(config, articles, list(categories)))
    if config["seo"].get("generer_rss", True):
        _ecrire(DOSSIER_SITE / "rss.xml", rss(config, articles))
    _ecrire(DOSSIER_SITE / "robots.txt", robots(config))
    _ecrire(DOSSIER_SITE / ".nojekyll", "")

    if verbeux:
        print(f"  ✓ Site reconstruit : {len(articles)} article(s), {total_pages} page(s) d'accueil.")

    return {"articles": len(articles), "pages": total_pages, "categories": len(categories)}
