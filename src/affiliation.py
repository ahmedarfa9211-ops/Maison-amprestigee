"""Construction et injection automatique des liens d'affiliation Amazon.

Règle de sécurité du projet : le modèle de rédaction n'écrit JAMAIS d'URL.
Toutes les URL sont fabriquées ici, à partir du catalogue et du tag configuré.
Impossible donc d'obtenir un lien inventé, cassé ou sans tag.
"""

from __future__ import annotations

import html
import re
from typing import Any
from urllib.parse import quote_plus

# Un ASIN Amazon = 10 caractères alphanumériques (souvent B0...).
MOTIF_ASIN = re.compile(r"^[A-Z0-9]{10}$")
MOTIF_URL_AMAZON = re.compile(r"https?://(?:www\.)?amazon\.[a-z.]+/[^\s\"'<>]+", re.I)


class Affiliation:
    def __init__(self, config: dict[str, Any]):
        aff = config["affiliation"]
        self.tag = aff["tag"]
        self.domaine = aff.get("domaine", "www.amazon.fr")
        self.cta = aff.get("texte_cta", "Voir le prix sur Amazon")
        self.mention_courte = aff.get("mention_courte", "")
        self.mention_longue = aff.get("mention_longue", "")

    # ------------------------------------------------------------------ URL

    def lien_produit(self, produit: dict[str, Any]) -> str:
        """URL affiliée d'un produit du catalogue.

        - ASIN renseigné  -> lien produit direct /dp/ASIN
        - ASIN absent     -> lien de recherche filtrée (valide et rémunéré)
        """
        asin = (produit.get("asin") or "").strip().upper()
        if asin and MOTIF_ASIN.match(asin):
            return (
                f"https://{self.domaine}/dp/{asin}"
                f"?tag={self.tag}&linkCode=ll1&language=fr_FR"
            )
        requete = produit.get("requete") or produit.get("nom", "coiffeuse")
        return self.lien_recherche(requete)

    def lien_recherche(self, requete: str) -> str:
        return f"https://{self.domaine}/s?k={quote_plus(requete)}&tag={self.tag}"

    def normaliser(self, url: str) -> str:
        """Ajoute ou corrige le tag sur une URL Amazon collée à la main.

        Opération idempotente : une URL déjà correctement taguée ressort
        inchangée, même écrite en HTML avec des `&amp;`.
        """
        if re.search(rf"[?&](?:amp;)?tag={re.escape(self.tag)}(?![\w-])", url):
            return url
        # On retire un éventuel autre tag (y compris sous forme échappée).
        url = re.sub(r"(&amp;|[?&])tag=[^&\s]*", lambda m: "?" if m.group(1) == "?" else "&", url)
        url = re.sub(r"&{2,}", "&", url)
        url = url.replace("?&", "?")
        url = re.sub(r"[?&]+$", "", url)
        separateur = "&amp;" if "&amp;" in url else ("&" if "?" in url else "?")
        return f"{url}{separateur}tag={self.tag}"

    # ----------------------------------------------------------------- HTML

    def _a(self, url: str, texte: str, classe: str) -> str:
        return (
            f'<a class="{classe}" href="{html.escape(url, quote=True)}" '
            f'target="_blank" rel="sponsored nofollow noopener">'
            f"{html.escape(texte)}</a>"
        )

    def bouton(self, produit: dict[str, Any], texte: str | None = None) -> str:
        return self._a(self.lien_produit(produit), texte or self.cta, "btn-amazon")

    def lien_texte(self, produit: dict[str, Any], texte: str | None = None) -> str:
        return self._a(self.lien_produit(produit), texte or produit["nom"], "lien-affilie")

    def bouton_recherche(self, requete: str, texte: str | None = None) -> str:
        return self._a(self.lien_recherche(requete), texte or self.cta, "btn-amazon")

    # ------------------------------------------------- injection automatique

    def injecter_dans_texte(self, texte: str, produits: list[dict[str, Any]]) -> str:
        """Transforme la 1re mention de chaque produit en lien affilié.

        Le modèle écrit le nom du produit en clair ; on le relie ici. Une seule
        occurrence par produit et par bloc, pour rester naturel et éviter le
        sur-maillage sanctionné par Google.
        """
        deja_liees: set[str] = set()
        for produit in produits:
            if produit["id"] in deja_liees:
                continue
            nom = produit["nom"]
            motif = re.compile(re.escape(nom), re.IGNORECASE)
            if motif.search(texte):
                texte = motif.sub(
                    lambda m: self._a(self.lien_produit(produit), m.group(0), "lien-affilie"),
                    texte,
                    count=1,
                )
                deja_liees.add(produit["id"])
        return texte

    def reparer_urls_brutes(self, texte: str) -> str:
        """Sécurité : toute URL Amazon présente dans le texte reçoit le tag."""
        return MOTIF_URL_AMAZON.sub(lambda m: self.normaliser(m.group(0)), texte)

    # -------------------------------------------------------------- mentions

    def encart_mention(self) -> str:
        return (
            '<aside class="mention-affiliation" role="note">'
            f"<strong>Transparence.</strong> {html.escape(self.mention_courte)}"
            "</aside>"
        )

    def pied_mention(self) -> str:
        return f'<p class="mention-pied">{html.escape(self.mention_longue)}</p>'
