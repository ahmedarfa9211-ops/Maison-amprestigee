# Mya Beauty — kit d'acquisition de rendez-vous

Extensions de cheveux weft · Montpellier & Agde · Instagram [@__myabeauty](https://www.instagram.com/__myabeauty/) · TikTok [@MYABEAUTY](https://www.tiktok.com/@myabeauty)

| Fichier | Ce que c'est |
|---|---|
| [`index.html`](index.html) | La page de capture de rendez-vous, à mettre en lien en bio |
| [`calendrier-contenu-30-jours.md`](calendrier-contenu-30-jours.md) | 30 jours de contenu organique, Instagram + TikTok |
| [`creatifs-publicitaires.md`](creatifs-publicitaires.md) | 3 créatifs Meta Ads + TikTok Ads, budget 150–200 € |

---

## À faire avant la mise en ligne (20 minutes)

### 1. Le numéro WhatsApp — indispensable

Le fichier contient un numéro fictif, `33600000000` (3 liens WhatsApp + un rappel en commentaire). Remplacez-le partout par le vôtre au **format international sans le `+` ni le `0`** : `06 12 34 56 78` devient `33612345678`.

```bash
sed -i 's/33600000000/33612345678/g' index.html
```

(ou, dans un éditeur de texte, un simple « Remplacer tout ».)

Le message pré-rempli est déjà écrit — la cliente n'a qu'à compléter :

> Bonjour Mya Beauty ✨
> Je souhaite prendre rendez-vous pour une pose d'extensions weft.
> • Prestation souhaitée :
> • Longueur / volume actuels :
> • Salon Montpellier, Agde ou à domicile (ville) :
> • Disponibilités :

### 2. Les 4 photos avant/après

Cherchez `PHOTO 1` … `PHOTO 4` dans `index.html`. Chaque emplacement contient le bloc à remplacer et, juste au-dessus, la ligne exacte à mettre à la place :

```html
<img src="photos/avant-apres-1.jpg" alt="Avant / après : cheveux fins densifiés par une pose weft">
```

Créez un dossier `photos/` à côté de `index.html`. **Format conseillé : portrait 4:5** (par ex. 1080 × 1350 px), moins de 300 Ko par image, même cadrage et même lumière pour l'avant et l'après.

> ⚠️ Chaque photo de cliente exige une **autorisation écrite**, mentionnant les supports concernés (site, réseaux sociaux, **publicité payante**) et révocable.

### 3. Les tarifs

Cherchez `TARIFS À AJUSTER`. Les montants actuels (150 € / 390 € / 90 € / 50 € / 40 € / 25 €) sont des **ordres de grandeur du marché français**, pas vos prix. Mettez les vôtres : ils doivent être identiques à ceux annoncés dans les publicités.

### 4. Les mentions légales et la confidentialité

Cherchez `À COMPLÉTER` dans le pied de page. Tout ce qui est entre crochets est à remplir : SIRET, adresse, hébergeur, assurance RC professionnelle, médiateur de la consommation, e-mail de contact. Ces deux blocs sont **obligatoires** — légalement, et pour que Meta accepte la page comme destination publicitaire.

### 5. Mettre en ligne

La page est autonome : un seul fichier, aucune dépendance à installer (seules les polices viennent de Google Fonts). Déposez `index.html` et le dossier `photos/` chez n'importe quel hébergeur statique gratuit — GitHub Pages, Netlify, Cloudflare Pages. Puis collez l'adresse dans les deux bios.

**Testez depuis un téléphone** avant de lancer quoi que ce soit : le bouton doit ouvrir WhatsApp avec le message déjà écrit.

---

## Ce que la page fait, et pourquoi

- **Un seul objectif** : ouvrir une conversation WhatsApp. Pas de formulaire, pas de newsletter, pas de second appel à l'action concurrent.
- **Le bouton WhatsApp apparaît trois fois** : en haut, en bas, et dans une barre fixe permanente sur mobile — c'est là que sera 90 % du trafic venu d'Instagram et de TikTok.
- **Le message est pré-rempli** : écrire le premier message est la véritable friction, pas le clic. En le rédigeant à sa place, on lève l'obstacle.
- **Les objections sont traitées avant le bouton** (ça se voit ? ça abîme ? combien ? où ?) — une cliente rassurée écrit, une cliente qui doute ferme l'onglet.
- **Aucun traceur, aucun cookie, aucun formulaire** : rien à déclarer, pas de bandeau de consentement nécessaire tant que vous n'ajoutez pas de pixel publicitaire.

---

## Le principe de conformité, en une ligne

Tout le dispositif repose sur le fait que **c'est la cliente qui écrit en premier**. Aucun bot, aucun message sortant non sollicité, aucun outil d'automatisation de DM : rien qui puisse coûter le compte Instagram, TikTok ou le numéro WhatsApp — c'est-à-dire l'actif qui produit les rendez-vous.

Le détail des règles appliquées se trouve dans [`creatifs-publicitaires.md`](creatifs-publicitaires.md#6-conformité--à-lire-avant-de-lancer) (section 6) et en tête du [calendrier](calendrier-contenu-30-jours.md).
