"""Visuels d'épingle Pinterest, générés à la construction du site.

Pinterest est un moteur de recherche visuel : sans image, pas d'épingle, et
son flux RSS n'accepte un article que s'il porte une illustration. Ce module
fabrique donc une image verticale 1000×1500 par article, aux couleurs du site.

Contrainte du projet : aucune dépendance obligatoire. Pillow est utilisé s'il
est disponible (rendu typographique complet) ; sinon on retombe sur un encodeur
PNG écrit à la main avec la bibliothèque standard, qui produit une image de
fond dégradée — moins belle, mais valide, et le flux ne casse jamais.
"""

from __future__ import annotations

import hashlib
import struct
import zlib
from pathlib import Path
from typing import Any

LARGEUR, HAUTEUR = 1000, 1500

# Déclinaisons chaudes dérivées de la charte du site. L'article choisit la
# sienne d'après son identifiant : deux articles voisins n'ont jamais le même
# visuel, et Pinterest ne les prend pas pour des doublons.
AMBIANCES = [
    {"fond": "#F7F1EA", "encre": "#3D2E33", "accent": "#B48A5E"},
    {"fond": "#EFE4D8", "encre": "#42302B", "accent": "#A87E55"},
    {"fond": "#F4EDE6", "encre": "#33302F", "accent": "#C0996E"},
    {"fond": "#E8DCD0", "encre": "#3A2C2A", "accent": "#96714C"},
    {"fond": "#3D2E33", "encre": "#F7F1EA", "accent": "#C9A57A"},
    {"fond": "#FBF6F1", "encre": "#2F2A2C", "accent": "#B48A5E"},
]

POLICES_SERIF = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
]
POLICES_SANS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]


def accroche(article: dict[str, Any], limite: int = 300) -> str:
    """Texte d'accompagnement de l'épingle, propre à chaque article.

    Pinterest classe ses résultats sur le texte : si toutes les épingles
    portaient la même description, elles se cannibaliseraient. On puise donc
    dans le chapeau de l'article, qui est unique, plutôt que dans la
    méta-description qui suit un gabarit.
    """
    contenu = article.get("contenu") or {}
    source = (contenu.get("chapeau") or "").strip() or article.get("meta", "")
    source = " ".join(source.split())
    if len(source) <= limite:
        return source
    coupe = source[:limite]
    for ponctuation in (". ", " ! ", " ? "):
        position = coupe.rfind(ponctuation)
        if position > limite * 0.5:
            return coupe[: position + 1].strip()
    return coupe.rsplit(" ", 1)[0].rstrip(" ,;:") + "…"


def _rvb(hexa: str) -> tuple[int, int, int]:
    hexa = hexa.lstrip("#")
    return tuple(int(hexa[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def ambiance(identifiant: str) -> dict[str, str]:
    graine = int(hashlib.md5(identifiant.encode("utf-8")).hexdigest()[:8], 16)
    return AMBIANCES[graine % len(AMBIANCES)]


# ------------------------------------------------------- secours sans Pillow


def _png_brut(pixels: list[bytes]) -> bytes:
    """Encode un PNG RVB à partir de lignes de pixels (bibliothèque standard)."""

    def bloc(nom: bytes, donnees: bytes) -> bytes:
        return (
            struct.pack(">I", len(donnees))
            + nom
            + donnees
            + struct.pack(">I", zlib.crc32(nom + donnees) & 0xFFFFFFFF)
        )

    entete = struct.pack(">2I5B", LARGEUR, HAUTEUR, 8, 2, 0, 0, 0)
    corps = zlib.compress(b"".join(b"\x00" + ligne for ligne in pixels), 9)
    return b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", entete) + bloc(b"IDAT", corps) + bloc(b"IEND", b"")


def _degrade(couleur_haut: str, couleur_bas: str) -> bytes:
    haut, bas = _rvb(couleur_haut), _rvb(couleur_bas)
    lignes = []
    for y in range(HAUTEUR):
        t = y / (HAUTEUR - 1)
        teinte = bytes(int(haut[c] + (bas[c] - haut[c]) * t) for c in range(3))
        lignes.append(teinte * LARGEUR)
    return _png_brut(lignes)


# ---------------------------------------------------------- rendu avec Pillow


def _police(chemins: list[str], taille: int):
    from PIL import ImageFont

    for chemin in chemins:
        if Path(chemin).exists():
            try:
                return ImageFont.truetype(chemin, taille)
            except OSError:
                continue
    return ImageFont.load_default()


def _decouper(dessin, texte: str, police, largeur_max: int) -> list[str]:
    mots, lignes, courante = texte.split(), [], ""
    for mot in mots:
        essai = f"{courante} {mot}".strip()
        if dessin.textlength(essai, font=police) <= largeur_max or not courante:
            courante = essai
        else:
            lignes.append(courante)
            courante = mot
    if courante:
        lignes.append(courante)
    return lignes


def _texte_espace(dessin, position, texte: str, police, couleur, ecart: int = 6) -> int:
    """Petites capitales espacées — Pillow ne gère pas l'interlettrage."""
    x, y = position
    for caractere in texte:
        dessin.text((x, y), caractere, font=police, fill=couleur)
        x += dessin.textlength(caractere, font=police) + ecart
    return int(x - ecart)


def _largeur_espace(dessin, texte: str, police, ecart: int = 6) -> int:
    return int(sum(dessin.textlength(c, font=police) + ecart for c in texte) - ecart)


def _rendre_pillow(article: dict[str, Any], config: dict[str, Any]) -> bytes:
    import io

    from PIL import Image, ImageDraw

    couleurs = ambiance(article.get("slug") or article.get("id", "coiffeuse"))
    fond, encre, accent = (_rvb(couleurs[c]) for c in ("fond", "encre", "accent"))

    image = Image.new("RGB", (LARGEUR, HAUTEUR), fond)
    dessin = ImageDraw.Draw(image)

    marge = 90
    # Filet intérieur : donne tout de suite un air de mise en page soignée.
    dessin.rectangle(
        [marge - 26, marge - 26, LARGEUR - marge + 26, HAUTEUR - 214],
        outline=accent,
        width=3,
    )

    surtitre = (article.get("categorie_nom") or article.get("type", "guide")).upper()
    police_surtitre = _police(POLICES_SANS, 30)
    largeur_surtitre = _largeur_espace(dessin, surtitre, police_surtitre)
    _texte_espace(
        dessin,
        ((LARGEUR - largeur_surtitre) // 2, 210),
        surtitre,
        police_surtitre,
        accent,
    )

    # Titre : on garde l'intitulé complet tant qu'il tient élégamment, sinon
    # on se replie sur sa partie principale (avant le deux-points).
    titre_complet = (article.get("titre_h1") or "Coiffeuse").strip()
    largeur_utile = LARGEUR - 2 * marge - 40
    for candidat in (titre_complet, titre_complet.split(" : ")[0].strip()):
        for taille in range(80, 44, -4):
            police_titre = _police(POLICES_SERIF, taille)
            lignes = _decouper(dessin, candidat, police_titre, largeur_utile)
            if len(lignes) <= 5:
                break
        if len(lignes) <= 5:
            break

    hauteur_ligne = int(taille * 1.30)
    police_promesse = _police(POLICES_SANS, 34)
    lignes_p = _decouper(
        dessin, accroche(article, 170), police_promesse, LARGEUR - 2 * marge - 60
    )[:3]

    # On mesure l'ensemble avant de le poser : le bloc est centré dans la zone
    # libre, jamais tassé en haut avec un grand vide en dessous.
    hauteur_titre = len(lignes) * hauteur_ligne
    hauteur_promesse = len(lignes_p) * 50 if lignes_p else 0
    ecart_filet = 62
    total = hauteur_titre + ecart_filet + (hauteur_promesse + 46 if lignes_p else 0)
    haut_zone, bas_zone = 310, HAUTEUR - 250
    y = haut_zone + (bas_zone - haut_zone - total) // 2

    for ligne in lignes:
        largeur = dessin.textlength(ligne, font=police_titre)
        dessin.text(((LARGEUR - largeur) // 2, y), ligne, font=police_titre, fill=encre)
        y += hauteur_ligne

    y += 28
    dessin.line([(LARGEUR // 2 - 70, y), (LARGEUR // 2 + 70, y)], fill=accent, width=4)
    y += 46

    for ligne in lignes_p:
        largeur = dessin.textlength(ligne, font=police_promesse)
        dessin.text(((LARGEUR - largeur) // 2, y), ligne, font=police_promesse, fill=encre)
        y += 50

    # Pied de page : la marque et l'adresse, discrètes mais toujours présentes.
    dessin.rectangle([0, HAUTEUR - 168, LARGEUR, HAUTEUR], fill=encre)
    police_marque = _police(POLICES_SANS, 32)
    marque = config["site"]["nom"].upper()
    largeur_marque = _largeur_espace(dessin, marque, police_marque, 8)
    _texte_espace(
        dessin,
        ((LARGEUR - largeur_marque) // 2, HAUTEUR - 128),
        marque,
        police_marque,
        fond,
        8,
    )
    police_adresse = _police(POLICES_SANS, 26)
    adresse = config["site"]["url"].split("//", 1)[-1]
    largeur_adresse = dessin.textlength(adresse, font=police_adresse)
    dessin.text(
        ((LARGEUR - largeur_adresse) // 2, HAUTEUR - 72),
        adresse,
        font=police_adresse,
        fill=accent,
    )

    tampon = io.BytesIO()
    image.save(tampon, format="PNG", optimize=True)
    return tampon.getvalue()


# ------------------------------------------------------------------- entrée


_pillow_teste = False


def _pillow_disponible() -> bool:
    """Pillow si présent ; sinon une tentative d'installation, une seule fois."""
    global _pillow_teste
    try:
        import PIL  # noqa: F401

        return True
    except ImportError:
        pass
    if _pillow_teste:
        return False
    _pillow_teste = True
    import subprocess
    import sys

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "pillow"],
            check=True,
            timeout=180,
            capture_output=True,
        )
        import PIL  # noqa: F401

        return True
    except Exception:  # noqa: BLE001
        print("  ! Pillow indisponible : visuels d'épingle en dégradé simple.")
        return False


def generer(article: dict[str, Any], config: dict[str, Any], destination: Path) -> Path:
    """Écrit le visuel d'épingle de l'article et renvoie son chemin."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if _pillow_disponible():
        try:
            destination.write_bytes(_rendre_pillow(article, config))
            return destination
        except Exception as erreur:  # noqa: BLE001
            print(f"  ! Visuel Pillow impossible ({erreur}), repli sur le dégradé.")
    couleurs = ambiance(article.get("slug") or article.get("id", "coiffeuse"))
    destination.write_bytes(_degrade(couleurs["fond"], couleurs["accent"]))
    return destination
