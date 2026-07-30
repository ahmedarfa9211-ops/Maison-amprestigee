"""Gabarits HTML et feuille de style du site."""

from __future__ import annotations

import html
from typing import Any

e = lambda t: html.escape(str(t))  # noqa: E731


def css(config: dict[str, Any]) -> str:
    s = config["site"]
    return f""":root{{
  --principale:{s['couleur_principale']};--secondaire:{s['couleur_secondaire']};--accent:{s['couleur_accent']};
  --texte:#241f22;--doux:#635a5f;--bord:#e7ddd8;--fond:#fffdfc;--amazon:#f0a13a;--amazon-fonce:#c97e18;
  --rayon:14px;--ombre:0 1px 2px rgba(36,31,34,.06),0 8px 24px rgba(36,31,34,.06);
}}
*,*::before,*::after{{box-sizing:border-box}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--fond);color:var(--texte);
  font:400 17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
  text-rendering:optimizeLegibility}}
img{{max-width:100%;height:auto;display:block}}
a{{color:var(--principale);text-underline-offset:2px}}
.conteneur{{width:min(100% - 2.4rem,1080px);margin-inline:auto}}
.etroit{{width:min(100% - 2.4rem,760px);margin-inline:auto}}

/* en-tête */
.entete{{position:sticky;top:0;z-index:50;background:rgba(255,253,252,.94);
  backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--bord)}}
.entete-in{{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.85rem 0}}
.logo{{font-weight:700;font-size:1.15rem;color:var(--principale);text-decoration:none;letter-spacing:-.02em}}
.logo span{{color:var(--accent)}}
.menu{{display:flex;flex-wrap:wrap;gap:.35rem 1.1rem;list-style:none;margin:0;padding:0;font-size:.93rem}}
.menu a{{color:var(--doux);text-decoration:none;padding:.25rem 0;border-bottom:2px solid transparent;white-space:nowrap}}
.menu a:hover{{color:var(--principale);border-color:var(--accent)}}
@media(max-width:820px){{
  .entete-in{{flex-direction:column;align-items:flex-start;gap:.5rem;padding:.7rem 0 .55rem}}
  .entete nav{{width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}}
  .entete nav::-webkit-scrollbar{{display:none}}
  .menu{{flex-wrap:nowrap;gap:1rem;font-size:.88rem;padding-bottom:.15rem}}
}}

/* héros */
.hero{{background:linear-gradient(180deg,var(--secondaire),transparent);padding:3.2rem 0 2.4rem;
  border-bottom:1px solid var(--bord)}}
.hero h1{{font-size:clamp(1.9rem,4.6vw,2.9rem);line-height:1.15;margin:0 0 .7rem;letter-spacing:-.025em}}
.hero p{{color:var(--doux);font-size:1.06rem;max-width:62ch;margin:0}}

/* fil d'ariane */
.ariane{{font-size:.85rem;color:var(--doux);padding:1rem 0 0}}
.ariane a{{color:var(--doux)}}
.ariane span{{margin:0 .4rem;opacity:.5}}

/* article */
.article{{padding:1.4rem 0 3.5rem}}
.article h1{{font-size:clamp(1.75rem,4.2vw,2.5rem);line-height:1.18;margin:.6rem 0 .8rem;letter-spacing:-.02em}}
.meta-article{{display:flex;flex-wrap:wrap;gap:.4rem 1rem;font-size:.86rem;color:var(--doux);
  padding-bottom:1.2rem;border-bottom:1px solid var(--bord);margin-bottom:1.6rem}}
.etiquette{{background:var(--secondaire);color:var(--principale);border-radius:999px;
  padding:.16rem .7rem;font-weight:600;font-size:.78rem;text-decoration:none}}
.chapeau{{font-size:1.14rem;line-height:1.65;color:#413a3e;border-left:3px solid var(--accent);
  padding-left:1.1rem;margin:1.4rem 0 2rem}}
.article h2{{font-size:clamp(1.35rem,3vw,1.72rem);line-height:1.25;margin:2.6rem 0 .9rem;
  letter-spacing:-.015em;scroll-margin-top:5rem}}
.article h3{{font-size:1.2rem;margin:1.8rem 0 .6rem}}
.article h4{{font-size:1rem;margin:1.2rem 0 .4rem}}
.article p{{margin:0 0 1.15rem}}
.liste-points{{margin:0 0 1.4rem;padding-left:0;list-style:none}}
.liste-points li{{position:relative;padding-left:1.6rem;margin-bottom:.6rem}}
.liste-points li::before{{content:"";position:absolute;left:.35rem;top:.72rem;width:7px;height:7px;
  border-radius:50%;background:var(--accent)}}

/* sommaire */
.sommaire{{background:var(--secondaire);border-radius:var(--rayon);padding:1.3rem 1.5rem;margin:0 0 2.2rem}}
.sommaire h2{{margin:0 0 .6rem;font-size:1.02rem;text-transform:uppercase;letter-spacing:.09em;color:var(--principale)}}
.sommaire ol{{margin:0;padding-left:1.2rem;columns:2;column-gap:2rem;font-size:.95rem}}
.sommaire li{{margin-bottom:.35rem;break-inside:avoid}}
.sommaire a{{color:#4a4145;text-decoration:none}}
.sommaire a:hover{{color:var(--principale);text-decoration:underline}}
@media(max-width:640px){{.sommaire ol{{columns:1}}}}

/* affiliation */
.mention-affiliation{{background:#fdf7f2;border:1px solid var(--bord);border-radius:10px;
  padding:.7rem 1rem;font-size:.85rem;color:var(--doux);margin:0 0 1.6rem}}
.btn-amazon{{display:inline-block;background:linear-gradient(180deg,var(--amazon),var(--amazon-fonce));
  color:#241f22!important;font-weight:700;text-decoration:none;padding:.72rem 1.35rem;border-radius:999px;
  box-shadow:0 2px 8px rgba(201,126,24,.28);white-space:nowrap;font-size:.95rem;transition:transform .12s}}
.btn-amazon:hover{{transform:translateY(-1px)}}
.lien-affilie{{color:var(--principale);font-weight:600;text-decoration:underline;
  text-decoration-color:var(--accent);text-decoration-thickness:2px}}

/* comparatif */
.bloc-comparatif{{margin:2.4rem 0}}
.tableau-defilant{{overflow-x:auto;border:1px solid var(--bord);border-radius:var(--rayon);box-shadow:var(--ombre)}}
table.comparatif{{width:100%;border-collapse:collapse;font-size:.94rem;min-width:640px;background:#fff}}
table.comparatif th{{background:var(--secondaire);text-align:left;padding:.85rem 1rem;
  font-size:.78rem;text-transform:uppercase;letter-spacing:.07em;color:var(--principale)}}
table.comparatif td{{padding:.9rem 1rem;border-top:1px solid var(--bord);vertical-align:middle}}
.rang{{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;
  background:var(--principale);color:#fff;font-weight:700;font-size:.83rem}}
.etoiles{{color:var(--amazon-fonce);letter-spacing:1px}}
.gamme{{color:var(--principale);font-weight:700;letter-spacing:.5px;margin-left:.5rem}}
.gamme-vide{{color:var(--bord);font-weight:700}}
.libelle-gamme{{color:var(--doux);font-size:.85rem;margin-left:.3rem}}
.note-tableau{{font-size:.8rem;color:var(--doux);margin:.6rem 0 0}}
@media(max-width:700px){{
  table.comparatif{{min-width:0}}
  table.comparatif thead{{display:none}}
  table.comparatif tr{{display:block;border-top:1px solid var(--bord);padding:.5rem 0}}
  table.comparatif td{{display:flex;justify-content:space-between;gap:1rem;border:0;padding:.4rem 1rem}}
  table.comparatif td::before{{content:attr(data-libelle);font-weight:600;color:var(--doux);font-size:.82rem}}
}}

/* cartes produit */
.carte-produit{{border:1px solid var(--bord);border-radius:var(--rayon);background:#fff;
  box-shadow:var(--ombre);margin:1.6rem 0;overflow:hidden;scroll-margin-top:5rem}}
.carte-produit header{{padding:1.3rem 1.5rem .8rem;background:linear-gradient(180deg,var(--secondaire),#fff)}}
.carte-produit h3{{margin:.3rem 0 .3rem;font-size:1.25rem}}
.badge-rang{{display:inline-block;background:var(--principale);color:#fff;font-weight:700;
  font-size:.78rem;padding:.15rem .65rem;border-radius:999px}}
.accroche{{color:var(--doux);font-size:.94rem;margin:0}}
.note-globale{{margin:.5rem 0 0;font-size:1rem}}
.corps-produit{{padding:0 1.5rem}}
.colonnes-avis{{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;margin:1rem 0}}
.colonnes-avis ul{{margin:.3rem 0 0;padding-left:1.1rem;font-size:.93rem}}
.colonnes-avis li{{margin-bottom:.35rem}}
.forts h4{{color:#2f7d52;margin:0}}
.faibles h4{{color:#a8452f;margin:0}}
@media(max-width:560px){{.colonnes-avis{{grid-template-columns:1fr}}}}
.specs{{background:#fbf7f5;border:1px solid var(--bord);border-radius:10px;padding:.9rem 1.1rem;margin:1.1rem 0}}
.specs h4{{margin:0 0 .5rem;font-size:.8rem;text-transform:uppercase;letter-spacing:.07em;color:var(--principale)}}
.specs table{{width:100%;border-collapse:collapse;font-size:.9rem}}
.specs th{{text-align:left;font-weight:600;color:var(--doux);padding:.25rem .8rem .25rem 0;
  vertical-align:top;white-space:nowrap;width:1%}}
.specs td{{padding:.25rem 0;vertical-align:top}}
@media(max-width:520px){{
  .specs th,.specs td{{display:block;width:auto;white-space:normal}}
  .specs th{{padding:.5rem 0 0}}
}}
.notes-detail{{list-style:none;margin:1rem 0 1.2rem;padding:0;font-size:.86rem}}
.notes-detail li{{display:grid;grid-template-columns:8.5rem 1fr 3rem;align-items:center;gap:.6rem;margin-bottom:.35rem}}
.barre{{background:var(--secondaire);border-radius:999px;height:7px;overflow:hidden}}
.barre i{{display:block;height:100%;background:var(--accent)}}
.carte-produit footer{{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;
  gap:.9rem;padding:1rem 1.5rem 1.4rem;border-top:1px solid var(--bord);background:#fdfbfa}}
.ideal{{margin:0;font-size:.9rem;color:var(--doux);max-width:60%}}
@media(max-width:560px){{.ideal{{max-width:100%}}}}

/* encadré */
.encadre{{background:var(--secondaire);border-left:4px solid var(--principale);
  border-radius:0 10px 10px 0;padding:1rem 1.25rem;margin:1.6rem 0}}
.encadre h4{{margin:0 0 .35rem;color:var(--principale);font-size:.95rem;
  text-transform:uppercase;letter-spacing:.06em}}
.encadre p{{margin:0;font-size:.96rem}}

/* faq */
.bloc-faq details{{border:1px solid var(--bord);border-radius:10px;margin-bottom:.6rem;background:#fff}}
.bloc-faq summary{{cursor:pointer;padding:.9rem 1.1rem;font-weight:600;list-style:none}}
.bloc-faq summary::-webkit-details-marker{{display:none}}
.bloc-faq summary::after{{content:"+";float:right;color:var(--accent);font-weight:700}}
.bloc-faq details[open] summary::after{{content:"–"}}
.bloc-faq p{{padding:0 1.1rem 1rem;margin:0;color:#413a3e}}

/* listes de liens */
.liste-liens{{list-style:none;margin:0;padding:0;display:grid;gap:.7rem}}
.liste-liens li{{border:1px solid var(--bord);border-radius:10px;padding:.85rem 1.1rem;background:#fff}}
.liste-liens a{{font-weight:600;text-decoration:none;display:block}}
.liste-liens span{{display:block;color:var(--doux);font-size:.88rem;margin-top:.2rem}}

/* grille d'articles */
.grille{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.3rem;margin:2rem 0}}
.vignette{{border:1px solid var(--bord);border-radius:var(--rayon);background:#fff;overflow:hidden;
  box-shadow:var(--ombre);display:flex;flex-direction:column;transition:transform .15s,box-shadow .15s}}
.vignette:hover{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(36,31,34,.1)}}
.vignette-in{{padding:1.15rem 1.25rem 1.35rem;display:flex;flex-direction:column;gap:.45rem;height:100%}}
.vignette h3{{margin:0;font-size:1.06rem;line-height:1.35}}
.vignette h3 a{{text-decoration:none;color:var(--texte)}}
.vignette h3 a:hover{{color:var(--principale)}}
.vignette p{{margin:0;color:var(--doux);font-size:.9rem;flex:1}}
.vignette-pied{{display:flex;justify-content:space-between;font-size:.78rem;color:var(--doux);
  border-top:1px solid var(--bord);padding-top:.6rem;margin-top:.4rem}}

/* pagination */
.pagination{{display:flex;gap:.4rem;flex-wrap:wrap;justify-content:center;margin:2.4rem 0}}
.pagination a,.pagination span{{padding:.5rem .9rem;border:1px solid var(--bord);border-radius:8px;
  text-decoration:none;font-size:.9rem;background:#fff}}
.pagination .actuelle{{background:var(--principale);color:#fff;border-color:var(--principale)}}

/* pied */
.pied{{background:var(--secondaire);border-top:1px solid var(--bord);margin-top:3rem;padding:2.4rem 0 1.8rem}}
.pied-grille{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.8rem}}
.pied h4{{margin:0 0 .55rem;font-size:.82rem;text-transform:uppercase;letter-spacing:.09em;color:var(--principale)}}
.pied ul{{list-style:none;margin:0;padding:0;font-size:.9rem}}
.pied li{{margin-bottom:.35rem}}
.pied a{{color:#4a4145;text-decoration:none}}
.pied a:hover{{text-decoration:underline}}
.mention-pied{{font-size:.8rem;color:var(--doux);border-top:1px solid var(--bord);
  margin-top:1.8rem;padding-top:1.1rem;line-height:1.6}}
.copyright{{font-size:.8rem;color:var(--doux);margin:.6rem 0 0}}
"""


def page(
    config: dict[str, Any],
    titre_html: str,
    tete: str,
    corps: str,
    jsonld: str = "",
    classe_corps: str = "",
) -> str:
    s = config["site"]
    nom = e(s["nom"])
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
{tete}
{jsonld}
<style>{css(config)}</style>
</head>
<body class="{classe_corps}">
<header class="entete"><div class="conteneur entete-in">
  <a class="logo" href="/">{nom.split(' ')[0]}<span>{' ' + ' '.join(nom.split(' ')[1:]) if ' ' in nom else ''}</span></a>
  <nav aria-label="Navigation principale"><ul class="menu">
    <li><a href="/">Accueil</a></li>
    <li><a href="/categorie/comparatifs/">Comparatifs</a></li>
    <li><a href="/categorie/guides-achat/">Guides d'achat</a></li>
    <li><a href="/categorie/guides-complets/">Guides complets</a></li>
    <li><a href="/categorie/amenagement/">Aménagement</a></li>
    <li><a href="/tous-les-guides/">Tous les guides</a></li>
  </ul></nav>
</div></header>
<main>
{corps}
</main>
<footer class="pied"><div class="conteneur">
  <div class="pied-grille">
    <div>
      <h4>{nom}</h4>
      <p style="font-size:.9rem;color:var(--doux);margin:0">{e(s['slogan'])}</p>
    </div>
    <div><h4>Catégories</h4><ul>
      <li><a href="/categorie/comparatifs/">Comparatifs</a></li>
      <li><a href="/categorie/guides-achat/">Guides d'achat</a></li>
      <li><a href="/categorie/guides-complets/">Guides complets</a></li>
      <li><a href="/categorie/amenagement/">Aménagement &amp; déco</a></li>
      <li><a href="/categorie/entretien/">Montage &amp; entretien</a></li>
    </ul></div>
    <div><h4>Le site</h4><ul>
      <li><a href="/tous-les-guides/">Tous les guides</a></li>
      <li><a href="/a-propos/">À propos</a></li>
      <li><a href="/mentions-legales/">Mentions légales</a></li>
      <li><a href="/rss.xml">Flux RSS</a></li>
    </ul></div>
  </div>
  <p class="mention-pied">{e(config['affiliation']['mention_longue'])}</p>
  <p class="copyright">© {nom} — Tous droits réservés.</p>
</div></footer>
</body>
</html>"""


def fil_ariane(elements: list[tuple[str, str | None]]) -> str:
    parties = []
    for libelle, url in elements:
        if url:
            parties.append(f'<a href="{e(url)}">{e(libelle)}</a>')
        else:
            parties.append(f"<strong>{e(libelle)}</strong>")
    return (
        '<nav class="ariane conteneur" aria-label="Fil d\'Ariane">'
        + '<span>›</span>'.join(parties)
        + "</nav>"
    )


def vignette(article: dict[str, Any], nom_categorie: str) -> str:
    return f"""<article class="vignette"><div class="vignette-in">
  <a class="etiquette" href="/categorie/{e(article['categorie'])}/" style="align-self:flex-start">{e(nom_categorie)}</a>
  <h3><a href="/{e(article['slug'])}/">{e(article['titre_h1'])}</a></h3>
  <p>{e(article.get('meta', '')[:130])}</p>
  <div class="vignette-pied"><span>{e(article['date'])}</span><span>{article.get('mots', 0)} mots</span></div>
</div></article>"""
