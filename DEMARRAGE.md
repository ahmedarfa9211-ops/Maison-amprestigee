# Démarrage en 30 minutes

Suivez les étapes dans l'ordre. À la fin, le site publie un guide par jour, tout seul, gratuitement.

---

## Phase de pré-lancement — sans nom de domaine

Vous pouvez **tout mettre en place avant d'acheter le domaine**. GitHub Pages
fournit une adresse gratuite du type `pseudo.github.io/depot` qui permet de
faire tourner le site en conditions réelles.

Pendant cette phase, `config.json` est réglé sur :

```json
"indexation": false
```

Le site est en ligne et consultable, mais `robots.txt` interdit l'exploration
et chaque page porte une balise `noindex` : **Google n'indexe rien sous la
mauvaise adresse**. C'est exactement ce qu'il faut pour ne pas gâcher le
référencement du futur domaine.

**Ce que vous pouvez faire dès maintenant :** créer le dépôt GitHub, brancher
la clé API, publier 15 articles, tout vérifier.

**Ce qu'il faut attendre :** la candidature Amazon Partenaires et Google Search
Console. Ces deux-là enregistrent l'adresse du site — inutile de les faire deux fois.

**Le jour où le domaine arrive**, trois modifications et une commande :

```json
"url": "https://maisonamprestige.fr",
"indexation": true
```

```bash
python publier.py --site
```

Toutes les balises canoniques, le sitemap et les liens internes basculent sur
le nouveau domaine. Aucun article n'est à réécrire.

---

## Étape 1 — Le tag Amazon Partenaires (10 min)

1. Créez un compte sur **partenaires.amazon.fr** (gratuit).
2. Récupérez votre **identifiant de partenaire**, du type `monsite-21`.
3. Ouvrez `config.json` et remplacez :

```json
"tag": "VOTRE-TAG-21"
```

> ⚠️ Amazon exige **3 ventes en 180 jours** pour valider définitivement le compte. Publier tous les jours dès maintenant est exactement ce qu'il faut pour y arriver.

---

## Étape 2 — Personnaliser le site (5 min)

Toujours dans `config.json` :

```json
"nom": "Coiffeuse Guide",
"url": "https://votre-domaine.fr",
"email_contact": "contact@votre-domaine.fr"
```

L'`url` doit être l'adresse finale du site : elle sert aux balises canoniques et au sitemap.

---

## Étape 3 — Tester en local (2 min)

Aucune dépendance à installer, tout est en Python standard.

```bash
python publier.py --site        # reconstruit le site avec votre tag
python publier.py --verifier    # contrôle qualité
```

Ouvrez ensuite `site/index.html` dans votre navigateur.

> **Les 14 articles livrés sont une démonstration**, rédigés en mode `local`
> (sans API) pour que vous voyiez le site vivant dès l'ouverture. Ils partagent
> des passages communs, ce que Google n'aime pas sur la durée.
>
> **Avant la mise en ligne réelle, supprimez-les** et laissez le mode `api`
> écrire des textes uniques :
>
> ```bash
> rm -rf data/articles data/etat.json
> python publier.py --nombre 10     # 10 vrais articles, uniques
> ```

---

## Étape 4 — Mettre en ligne sur GitHub Pages (10 min, gratuit)

1. Créez un dépôt GitHub (privé ou public) et poussez ce dossier.
2. Dans **Settings → Pages**, choisissez la source **GitHub Actions**.
3. Dans **Settings → Secrets and variables → Actions**, ajoutez :

| Type     | Nom                 | Valeur                                     |
|----------|---------------------|--------------------------------------------|
| Secret   | `ANTHROPIC_API_KEY` | votre clé API (console.anthropic.com)      |
| Secret   | `AMAZON_TAG`        | votre tag, ex. `monsite-21`                |
| Variable | `SITE_URL`          | `https://votre-domaine.fr`                 |

4. Onglet **Actions → Publication quotidienne → Run workflow** pour un premier test.

À partir de là, un article part **chaque matin à 7h00 (Paris)** sans rien faire.

---

## Étape 5 — Google (3 min)

1. **Search Console** → ajoutez la propriété du site.
2. Soumettez `https://votre-domaine.fr/sitemap.xml`.
3. Demandez l'indexation de la page d'accueil.

Comptez 2 à 8 semaines avant les premiers positionnements. C'est normal : un site neuf n'a aucun historique.

---

## Étape 6 — Passer aux liens produits directs (progressif)

Tant qu'un produit n'a pas d'ASIN, le lien pointe vers une **recherche Amazon filtrée** : c'est valide, c'est rémunéré, mais un lien produit direct convertit mieux.

Pour améliorer un produit, ouvrez `data/produits.json` et collez l'ASIN (les 10 caractères après `/dp/` dans l'URL Amazon) :

```json
{
  "id": "coiffeuse-blanche-led",
  "asin": "B08XXXXXXX",
  "specs": {
    "Éclairage": "12 LED, 3 températures de couleur",
    "Rangement": "11 tiroirs"
  }
}
```

Le bloc `specs` est facultatif mais **c'est lui qui fait la différence** :
il affiche un tableau de caractéristiques dans la fiche et sert de matière
première au rédacteur. Copiez-collez simplement les puces de la page Amazon.

Puis :

```bash
python publier.py --produits                          # le lien est-il direct ?
python publier.py --regenerer coiffeuse-blanche-led   # réécrit les articles concernés
```

Faites-en 2 ou 3 par semaine, sans vous presser.

---

## Aide-mémoire des commandes

| Commande | Effet |
|---|---|
| `python publier.py` | article du jour + reconstruction du site |
| `python publier.py --nombre 7` | 7 articles d'un coup |
| `python publier.py --sujet coiffeuse-led` | force un sujet précis |
| `python publier.py --mode local` | rédige sans appeler l'API |
| `python publier.py --site` | reconstruit le site sans rédiger |
| `python publier.py --sujets 30` | affiche les 30 prochains sujets prévus |
| `python publier.py --produits` | état du catalogue et des liens |
| `python publier.py --regenerer <id>` | réécrit les articles d'un produit modifié |
| `python publier.py --verifier` | contrôle qualité complet |
| `python publier.py --modeles` | liste les modèles API disponibles |
