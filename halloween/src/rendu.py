"""Transformation du contenu rédigé en HTML d'article, liens affiliés inclus."""

from __future__ import annotations

import html
import re
from typing import Any

from .affiliation import Affiliation
from .sujets import slugifier

e = lambda t: html.escape(str(t))  # noqa: E731


def lier_articles_internes(texte: str, articles: list[dict[str, Any]]) -> str:
    """Transforme la mention d'un titre d'article existant en lien interne."""
    for article in articles:
        titre = e(article.get("titre_h1", ""))
        if not titre or titre not in texte:
            continue
        lien = f'<a href="/{e(article["slug"])}/">{titre}</a>'
        texte = re.sub(re.escape(titre), lambda _m: lien, texte, count=1)
    return texte


def _ancre(titre: str) -> str:
    return slugifier(titre) or "section"


def _etoiles(note: float) -> str:
    pleines = int(round(note))
    return "★" * pleines + "☆" * (5 - pleines)


def _note_globale(produit: dict[str, Any]) -> float:
    notes = produit.get("notes", {})
    if not notes:
        return 4.0
    return round(sum(notes.values()) / len(notes), 1)


# Positionnement tarifaire indicatif — SANS aucun montant, ce que le contrat
# Amazon interdit hors Product Advertising API. Trois symboles, zéro chiffre.
SYMBOLES_GAMME = {"budget": "€", "milieu": "€€", "premium": "€€€"}
LIBELLES_GAMME = {"budget": "entrée de gamme", "milieu": "milieu de gamme", "premium": "haut de gamme"}


def _gamme(produit: dict[str, Any]) -> tuple[str, str]:
    cle = produit.get("gamme", "milieu")
    symbole = SYMBOLES_GAMME.get(cle, "€€")
    libelle = LIBELLES_GAMME.get(cle, "milieu de gamme")
    plein = f'<b>{symbole}</b><span class="gamme-vide">{"€" * (3 - len(symbole))}</span>'
    return plein, libelle


# ------------------------------------------------------------------ blocs


def sommaire(sections: list[dict[str, Any]], avec_produits: bool, avec_faq: bool) -> str:
    liens = []
    if avec_produits:
        liens.append('<li><a href="#comparatif">Le comparatif en un coup d\'œil</a></li>')
        liens.append('<li><a href="#selection">Notre sélection détaillée</a></li>')
    for section in sections:
        titre = section.get("titre", "")
        if titre:
            liens.append(f'<li><a href="#{_ancre(titre)}">{e(titre)}</a></li>')
    if avec_faq:
        liens.append('<li><a href="#faq">Questions fréquentes</a></li>')
    return (
        '<nav class="sommaire" aria-label="Sommaire">'
        "<h2>Sommaire</h2><ol>" + "".join(liens) + "</ol></nav>"
    )


def tableau_comparatif(produits: list[dict[str, Any]], aff: Affiliation) -> str:
    if not produits:
        return ""
    lignes = []
    for i, produit in enumerate(produits, 1):
        note = _note_globale(produit)
        symboles, libelle = _gamme(produit)
        lignes.append(
            "<tr>"
            f'<td data-libelle="Rang"><span class="rang">#{i}</span></td>'
            f'<td data-libelle="Modèle"><strong>{e(produit["nom"])}</strong></td>'
            f'<td data-libelle="Idéal pour">{e(produit.get("pour_qui", ""))}</td>'
            f'<td data-libelle="Positionnement"><span class="gamme" title="{e(libelle)}">{symboles}</span></td>'
            f'<td data-libelle="Note"><span class="etoiles" title="{note}/5">{_etoiles(note)}</span></td>'
            f'<td data-libelle="Lien">{aff.bouton(produit, "Voir sur Amazon")}</td>'
            "</tr>"
        )
    return (
        '<section id="comparatif" class="bloc-comparatif">'
        "<h2>Le comparatif en un coup d'œil</h2>"
        '<div class="tableau-defilant"><table class="comparatif">'
        "<thead><tr><th>Rang</th><th>Modèle</th><th>Idéal pour</th>"
        "<th>Gamme</th><th>Note</th><th></th></tr></thead>"
        f"<tbody>{''.join(lignes)}</tbody></table></div>"
        '<p class="note-tableau">'
        "<strong>€</strong> entrée de gamme · <strong>€€</strong> milieu de gamme · "
        "<strong>€€€</strong> haut de gamme. Il s'agit d'un positionnement indicatif : "
        "les prix et la disponibilité sont consultables directement sur Amazon et "
        "peuvent changer à tout moment."
        "</p>"
        "</section>"
    )


def carte_produit(
    index: int, produit: dict[str, Any], avis: dict[str, Any] | None, aff: Affiliation
) -> str:
    avis = avis or {}
    forts = avis.get("points_forts") or produit.get("points_forts", [])
    faibles = avis.get("points_faibles") or produit.get("points_faibles", [])
    verdict = avis.get("verdict", "")
    accroche = avis.get("accroche") or produit.get("pour_qui", "")
    note = _note_globale(produit)
    symboles, libelle_gamme = _gamme(produit)

    # Évite de répéter mot pour mot l'accroche dans le pied de carte.
    ideal = avis.get("ideal_pour") or produit.get("pour_qui", "")
    if ideal and ideal.strip().lower() in accroche.strip().lower():
        ideal = "Un choix cohérent si ces limites correspondent à votre usage."

    detail_notes = "".join(
        f'<li><span>{e(critere.replace("_", " ").capitalize())}</span>'
        f'<span class="barre"><i style="width:{valeur / 5 * 100:.0f}%"></i></span>'
        f"<b>{valeur}/5</b></li>"
        for critere, valeur in produit.get("notes", {}).items()
    )

    # Caractéristiques vérifiées (affichées seulement si elles existent).
    specs = produit.get("specs") or {}
    bloc_specs = ""
    if specs:
        lignes = "".join(
            f"<tr><th>{e(cle)}</th><td>{e(valeur)}</td></tr>" for cle, valeur in specs.items()
        )
        bloc_specs = (
            '<div class="specs"><h4>Caractéristiques</h4>'
            f"<table>{lignes}</table></div>"
        )

    return f"""<article class="carte-produit" id="produit-{e(produit['id'])}">
  <header>
    <span class="badge-rang">#{index}</span>
    <h3>{e(produit['nom'])}</h3>
    <p class="accroche">{e(accroche)}</p>
    <p class="note-globale"><span class="etoiles">{_etoiles(note)}</span> <b>{note}/5</b>
       <span class="gamme" title="{e(libelle_gamme)}">{symboles}</span>
       <span class="libelle-gamme">{e(libelle_gamme)}</span></p>
  </header>
  <div class="corps-produit">
    <p>{e(verdict)}</p>
    {bloc_specs}
    <div class="colonnes-avis">
      <div class="forts"><h4>Points forts</h4><ul>{''.join(f'<li>{e(p)}</li>' for p in forts)}</ul></div>
      <div class="faibles"><h4>Limites</h4><ul>{''.join(f'<li>{e(p)}</li>' for p in faibles)}</ul></div>
    </div>
    <ul class="notes-detail">{detail_notes}</ul>
  </div>
  <footer>
    <p class="ideal">{e(ideal)}</p>
    {aff.bouton(produit)}
  </footer>
</article>"""


def selection(
    produits: list[dict[str, Any]], avis_par_id: dict[str, Any], aff: Affiliation
) -> str:
    if not produits:
        return ""
    cartes = [
        carte_produit(i, produit, avis_par_id.get(produit["id"]), aff)
        for i, produit in enumerate(produits, 1)
    ]
    return (
        '<section id="selection" class="bloc-selection">'
        "<h2>Notre sélection détaillée</h2>" + "".join(cartes) + "</section>"
    )


def rendre_section(
    section: dict[str, Any],
    produits: list[dict[str, Any]],
    aff: Affiliation,
    articles_lies: list[dict[str, Any]] | None = None,
) -> str:
    articles_lies = articles_lies or []
    titre = section.get("titre", "")
    morceaux = [f'<h2 id="{_ancre(titre)}">{e(titre)}</h2>'] if titre else []

    for paragraphe in section.get("paragraphes", []):
        texte = aff.injecter_dans_texte(e(paragraphe), produits)
        texte = lier_articles_internes(texte, articles_lies)
        morceaux.append(f"<p>{texte}</p>")

    liste = section.get("liste")
    if liste:
        items = "".join(
            f"<li>{lier_articles_internes(aff.injecter_dans_texte(e(item), produits), articles_lies)}</li>"
            for item in liste
        )
        morceaux.append(f"<ul class='liste-points'>{items}</ul>")

    encadre = section.get("encadre")
    if encadre and encadre.get("texte"):
        morceaux.append(
            '<aside class="encadre">'
            f"<h4>{e(encadre.get('titre', 'À retenir'))}</h4>"
            f"<p>{e(encadre['texte'])}</p></aside>"
        )
    return f'<section class="bloc-texte">{"".join(morceaux)}</section>'


def bloc_faq(faq: list[dict[str, str]]) -> str:
    if not faq:
        return ""
    items = "".join(
        f"<details><summary>{e(item['q'])}</summary><p>{e(item['r'])}</p></details>"
        for item in faq
    )
    return f'<section id="faq" class="bloc-faq"><h2>Questions fréquentes</h2>{items}</section>'


def bloc_maillage(articles: list[dict[str, Any]]) -> str:
    if not articles:
        return ""
    items = "".join(
        f'<li><a href="/{e(a["slug"])}/">{e(a["titre_h1"])}</a>'
        f'<span>{e(a.get("meta", "")[:110])}</span></li>'
        for a in articles
    )
    return (
        '<section class="bloc-maillage"><h2>À lire aussi</h2>'
        f'<ul class="liste-liens">{items}</ul></section>'
    )


# ---------------------------------------------------------------- assemblage


def rendre_article(
    contenu: dict[str, Any],
    produits: list[dict[str, Any]],
    articles_lies: list[dict[str, Any]],
    aff: Affiliation,
) -> str:
    sections = contenu.get("sections", [])
    avis_par_id = {a.get("produit_id"): a for a in contenu.get("avis_produits", [])}
    avec_produits = bool(produits)

    parties: list[str] = [aff.encart_mention()]
    parties.append(f'<p class="chapeau">{e(contenu.get("chapeau", ""))}</p>')
    parties.append(sommaire(sections, avec_produits, bool(contenu.get("faq"))))

    if avec_produits:
        parties.append(tableau_comparatif(produits, aff))

    # Deux sections de contexte, puis la sélection, puis le reste.
    tete, reste = sections[:2], sections[2:]
    parties.extend(rendre_section(s, produits, aff, articles_lies) for s in tete)

    if avec_produits:
        parties.append(selection(produits, avis_par_id, aff))

    parties.extend(rendre_section(s, produits, aff, articles_lies) for s in reste)
    parties.append(bloc_faq(contenu.get("faq", [])))

    if contenu.get("conclusion"):
        conclusion = lier_articles_internes(
            aff.injecter_dans_texte(e(contenu["conclusion"]), produits), articles_lies
        )
        parties.append(
            '<section class="bloc-conclusion"><h2 id="verdict">Notre verdict</h2>'
            f"<p>{conclusion}</p></section>"
        )

    parties.append(bloc_maillage(articles_lies))

    corps = "".join(parties)
    return aff.reparer_urls_brutes(corps)


def html_de_larticle(
    article: dict[str, Any],
    config: dict[str, Any],
    produits_par_id: dict[str, Any],
    articles_par_slug: dict[str, Any],
) -> str:
    """Reconstruit le HTML d'un article à partir de son contenu stocké.

    Le HTML n'est jamais figé sur le disque : il est régénéré à chaque build.
    Changer le tag d'affiliation, le texte des boutons ou le nombre de liens
    internes se répercute donc sur TOUS les articles déjà publiés.
    """
    aff = Affiliation(config)
    produits = [produits_par_id[i] for i in article.get("produits", []) if i in produits_par_id]
    lies = [articles_par_slug[s] for s in article.get("lies", []) if s in articles_par_slug]
    return rendre_article(article["contenu"], produits, lies, aff)
