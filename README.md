# Coiffeuse Pro — blog d'affiliation Amazon automatisé

Système complet de publication quotidienne pour un site de niche consacré à la
**coiffeuse (meuble de maquillage)**. Chaque jour, il rédige un guide de
**2500 mots minimum optimisé pour le référencement naturel**, y insère
automatiquement vos liens d'affiliation Amazon.fr, reconstruit le site et le
met en ligne.

👉 **Pour démarrer, lisez [DEMARRAGE.md](DEMARRAGE.md)** (30 minutes, étape par étape).

---

## Ce que fait le système

| | |
|---|---|
| **Rédaction** | Un guide de 2500+ mots par jour, rédigé par Claude, unique à chaque fois |
| **Formats** | Comparatifs, guides d'achat, guides complets, aménagement, entretien, questions |
| **Affiliation** | Liens Amazon.fr générés automatiquement, tag toujours présent, `rel="sponsored nofollow"` |
| **SEO technique** | `title`/`meta` calibrés, canoniques, Open Graph, sitemap.xml, RSS, robots.txt |
| **Données structurées** | `Article`, `FAQPage`, `ItemList`, `BreadcrumbList`, `WebSite` |
| **Maillage interne** | Chaque article cite et relie 4 articles voisins, automatiquement |
| **Site** | Statique, sans base de données, sans JavaScript, très rapide |
| **Automatisation** | GitHub Actions, tous les jours à 7h00 Paris, hébergement gratuit |
| **Contrôle qualité** | `--verifier` bloque les articles trop courts ou aux liens incomplets |

Zéro dépendance : Python 3.9+ et rien d'autre.

---

## Architecture

```
coiffeuse-pro/
├── config.json                  ← tag Amazon, nom du site, couleurs, réglages
├── publier.py                   ← ligne de commande (tout passe par ici)
├── DEMARRAGE.md                 ← guide d'installation pas à pas
│
├── data/
│   ├── produits.json            ← catalogue des modèles + ASIN (à enrichir)
│   ├── sujets.json              ← sujets prioritaires + axes de combinaison
│   ├── etat.json                ← journal des publications (généré)
│   └── articles/                ← un JSON par article publié (généré)
│
├── src/
│   ├── reglages.py              ← chargement config et données
│   ├── sujets.py                ← calendrier éditorial, choix du sujet du jour
│   ├── affiliation.py           ← fabrication et injection des liens Amazon
│   ├── redacteur.py             ← rédaction via l'API Claude
│   ├── redaction_locale.py      ← rédaction de secours, sans API
│   ├── seo.py                   ← métadonnées et données structurées
│   ├── rendu.py                 ← contenu → HTML (tableaux, cartes, FAQ)
│   ├── gabarits.py              ← squelette des pages et feuille de style
│   └── site.py                  ← construction du site complet
│
├── site/                        ← le site généré, prêt à héberger
└── .github/workflows/           ← automatisation quotidienne
```

---

## Le calendrier éditorial

Le moteur ne tombe jamais en panne de sujets :

1. **30 sujets prioritaires** écrits à la main, classés par valeur commerciale
   (« meilleure coiffeuse », « coiffeuse LED », « coiffeuse pas cher »…).
2. **Expansion combinatoire** : 24 attributs × 12 contextes × 6 formats, soit
   plus de **200 sujets uniques** supplémentaires générés automatiquement.
3. **20 questions fréquentes** développées en articles complets.
4. Une fois la file épuisée (plus d'un an), les articles les plus anciens
   repassent en **mise à jour annuelle** — ce que Google apprécie.

```bash
python publier.py --sujets 30    # voir les 30 prochains jours
```

---

## Fiches produit : ASIN et caractéristiques

Un produit du catalogue peut porter un bloc `specs`. Quand il est présent :

- un **tableau « Caractéristiques »** s'affiche dans la fiche produit ;
- ces données sont transmises au rédacteur avec la consigne explicite de
  **n'en inventer aucune autre**.

C'est le levier le plus rentable du système : une fiche avec de vraies
caractéristiques convertit nettement mieux qu'un texte générique.

```json
{
  "id": "coiffeuse-blanche-led",
  "asin": "B0FK4ZJCX8",
  "specs": {
    "Éclairage": "12 LED, 3 températures de couleur, luminosité réglable",
    "Rangement": "11 tiroirs"
  }
}
```

### Le garde-fou éditorial : `exclut`

Un produit peut déclarer les angles de sujet sur lesquels il n'a rien à faire.
Une coiffeuse de 105 cm de large et 60 kg est excellente, mais elle n'a aucune
légitimité dans un comparatif « petit espace » — et l'y faire figurer
décrédibilise tout l'article aux yeux du lecteur comme de Google.

```json
"exclut": ["petit-espace", "angle", "murale", "etroite", "enfant", "ado", "budget"]
```

Deux règles de sélection tournent en plus automatiquement :

- un **accessoire** (miroir d'appoint, tabouret, organiseur) ne peut jamais
  ouvrir un comparatif de meubles ; il ne concourt à armes égales que si le
  sujet porte explicitement sur ce type de produit ;
- la sélection est **déterministe** : un même sujet donne toujours la même
  liste, dans le même ordre.

Les avis produits étant figés dans chaque article au moment de sa rédaction,
après avoir corrigé une fiche il faut réécrire les articles concernés :

```bash
python publier.py --regenerer coiffeuse-blanche-led   # articles concernés
python publier.py --regenerer tous                    # tout le site
```

Date de publication, URL et sujet d'origine sont conservés.

---

## Conformité Amazon Partenaires

Le système respecte le contrat d'exploitation du programme :

- **Aucun prix n'est jamais écrit** dans les articles. Le contrat interdit
  d'afficher un prix qui ne provient pas de la Product Advertising API ; le
  système affiche donc toujours « Voir le prix sur Amazon ».
- **Mention d'affiliation** affichée en haut de chaque article et en pied de
  page, comme l'exige l'obligation de divulgation claire et en temps réel.
- **Avertissement** sur la variabilité des prix sous chaque tableau comparatif.
- **Page mentions légales** générée automatiquement.
- Liens en `rel="sponsored nofollow noopener"` et `target="_blank"`.

> Le modèle de rédaction **n'écrit jamais d'URL** : toutes les adresses sont
> fabriquées par `src/affiliation.py` à partir du catalogue et de votre tag.
> Un lien inventé, cassé ou sans tag est donc structurellement impossible.

---

## Les deux modes de rédaction

| | `api` (recommandé) | `local` |
|---|---|---|
| Texte | Unique à chaque article | Assemblé à partir de blocs |
| Coût | Quelques centimes par article | Gratuit |
| Risque SEO | Aucun | Similarité entre articles à la longue |
| Usage | Publication quotidienne réelle | Tests, dépannage, secours |

Le mode `api` bascule automatiquement en `local` si la clé est absente ou si
l'API est indisponible : **aucune journée sans publication**.

---

## Contrôle qualité

```bash
python publier.py --verifier
```

Vérifie sur chaque article : longueur ≥ plancher, `title` ≤ 70 caractères,
méta-description présente et calibrée, présence de liens Amazon, **tag
d'affiliation sur 100 % des liens**, attribut `rel` correct, mot-clé principal
présent dans le H1.

---

## Personnalisation courante

| Envie | Où |
|---|---|
| Changer les couleurs | `config.json` → `site.couleur_*` |
| Viser 3000 mots | `config.json` → `publication.objectif_mots` |
| Publier 2 articles/jour | `config.json` → `publication.articles_par_jour` puis `--nombre 2` |
| Ajouter des produits | `data/produits.json` |
| Corriger une fiche produit | `data/produits.json` puis `--regenerer <id>` |
| Écarter un produit d'un angle | `data/produits.json` → `exclut` |
| Ajouter des sujets | `data/sujets.json` → `prioritaires` ou `axes` |
| Changer l'heure | `.github/workflows/publication-quotidienne.yml` → `cron` |

---

## Ce que ce système ne fait pas

Autant le dire franchement :

- Il ne crée pas de trafic instantané. Un site neuf met **2 à 6 mois** à
  s'installer sur des requêtes concurrentielles.
- Il ne récupère pas les prix ni les images Amazon en temps réel — cela
  demanderait la Product Advertising API, accessible seulement après vos
  premières ventes.
- Il ne remplace pas votre jugement : ajouter progressivement de vrais ASIN et
  de vraies observations produit fera plus pour vos revenus que n'importe quel
  réglage technique.
