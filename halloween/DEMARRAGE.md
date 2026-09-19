# Démarrage — site Halloween « Panoplie Halloween »

Suivez les étapes dans l'ordre. Toutes les commandes se lancent **depuis le
dossier `halloween/`** (`cd halloween`).

---

## Étape 1 — Le tag Amazon Partenaires

Le site est déjà configuré avec le tag `maisonamprest-21` (celui de Maison
AMPrestige). Pour utiliser un autre identifiant, ouvrez `config.json` :

```json
"tag": "VOTRE-TAG-21"
```

> ⚠️ Amazon exige **3 ventes en 180 jours** pour valider définitivement le compte.
> Halloween est une saison à fort volume : c'est le bon moment pour les réaliser.

---

## Étape 2 — Personnaliser le site

Toujours dans `config.json` :

```json
"nom": "Panoplie Halloween",
"url": "https://votre-domaine.fr",
"email_contact": "contact@votre-domaine.fr"
```

L'`url` doit être l'adresse finale : elle sert aux balises canoniques, au sitemap
et au fichier CNAME. La palette se règle via `site.couleur_principale`,
`couleur_secondaire` et `couleur_accent`.

---

## Étape 3 — Tester en local

Aucune dépendance à installer, tout est en Python standard.

```bash
cd halloween
python publier.py --site        # reconstruit le site avec votre tag
python publier.py --verifier    # contrôle qualité
```

Ouvrez ensuite `halloween/site/index.html` dans votre navigateur.

> **Les 24 articles livrés sont une démonstration**, rédigés en mode `local`
> (sans API). Ils partagent des passages communs de fond, ce que Google n'aime
> pas sur la durée.
>
> **Avant la mise en ligne réelle, remplacez-les** par des textes uniques :
>
> ```bash
> rm -rf data/articles data/etat.json
> python publier.py --nombre 10     # 10 vrais articles, uniques (mode api)
> ```

---

## Étape 4 — Passer aux liens produits directs (progressif)

Tant qu'un produit n'a pas d'ASIN, son lien pointe vers une **recherche Amazon
filtrée** : c'est valide et rémunéré, mais un lien produit direct convertit mieux.

Ouvrez `data/produits.json` et collez l'ASIN (les 10 caractères après `/dp/` dans
l'URL Amazon), puis ajoutez éventuellement un bloc `specs` :

```json
{
  "id": "costume-sorciere-femme",
  "asin": "B0XXXXXXXX",
  "specs": {
    "Tailles": "du S au XXL",
    "Composition": "polyester, lavable à froid",
    "Contenu": "robe + chapeau"
  }
}
```

Puis :

```bash
python publier.py --produits                       # le lien est-il direct ?
python publier.py --regenerer costume-sorciere-femme   # réécrit les articles concernés
```

Faites-en quelques-uns par semaine, en priorité sur les produits les plus cités.

---

## Étape 5 — Mise en ligne

Le site généré est un dossier statique (`halloween/site/`) hébergeable partout
(GitHub Pages, Netlify, Cloudflare Pages, un simple serveur…).

Un workflow GitHub Actions **manuel** est fourni :
`.github/workflows/halloween.yml`. Il rédige les articles, reconstruit le site et
enregistre le contenu. Lancez-le depuis l'onglet **Actions → Publication Halloween
→ Run workflow**.

Renseignez si besoin, dans **Settings → Secrets and variables → Actions** :

| Type     | Nom                 | Valeur                                |
|----------|---------------------|---------------------------------------|
| Secret   | `ANTHROPIC_API_KEY` | votre clé API (mode api)              |
| Secret   | `AMAZON_TAG`        | votre tag, ex. `maisonamprest-21`     |
| Variable | `SITE_URL_HALLOWEEN`| `https://votre-domaine.fr`            |

> ⚠️ **Un dépôt GitHub Pages n'héberge qu'un seul site.** Le dépôt sert déjà le
> site coiffeuse. Pour publier aussi le site Halloween via GitHub Pages, hébergez-le
> sur **un dépôt distinct** ou un **autre hébergeur** (Netlify/Cloudflare Pages
> pointant sur le dossier `halloween/site`). Le workflow fourni construit et
> enregistre le site sans écraser le déploiement Pages du site coiffeuse.

---

## Aide-mémoire

| Commande | Effet |
|---|---|
| `python publier.py` | article du jour + reconstruction |
| `python publier.py --nombre 7` | 7 articles d'un coup |
| `python publier.py --sujet <id>` | force un sujet |
| `python publier.py --mode local` | sans API |
| `python publier.py --site` | reconstruit sans rédiger |
| `python publier.py --sujets 30` | prochains sujets |
| `python publier.py --produits` | état du catalogue |
| `python publier.py --verifier` | contrôle qualité |
