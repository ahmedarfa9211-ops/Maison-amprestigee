# Panoplie Halloween — site d'affiliation Amazon « costumes & déguisements »

Déclinaison Halloween du moteur de publication de Maison AMPrestige, dédiée aux
**costumes et déguisements d'Halloween**. Le système rédige des guides longs
(2000+ mots) optimisés pour le référencement, y insère automatiquement les liens
d'affiliation Amazon.fr, reconstruit le site statique et le met en ligne.

> Ce dossier est **autonome** : il possède sa propre configuration, ses propres
> données et sa propre copie du moteur. Il ne modifie en rien le site coiffeuse
> à la racine du dépôt.

👉 **Pour démarrer, lisez [DEMARRAGE.md](DEMARRAGE.md).**

---

## Ce que fait le système

| | |
|---|---|
| **Rédaction** | Un guide costume par jour, unique, 2000+ mots |
| **Formats** | Comparatifs, guides d'achat, idées, contenus enfants & famille, DIY, FAQ |
| **Affiliation** | Liens Amazon.fr générés automatiquement, tag toujours présent, `rel="sponsored nofollow"` |
| **SEO technique** | `title`/`meta` calibrés, canoniques, Open Graph, sitemap.xml, RSS, robots.txt |
| **Données structurées** | `Article`, `FAQPage`, `ItemList`, `BreadcrumbList`, `WebSite` |
| **Maillage interne** | Chaque article relie 4 articles voisins, automatiquement |
| **Site** | Statique, sans base de données, sans JavaScript, très rapide |
| **Conformité Amazon** | Aucun prix affiché, mention d'affiliation, mentions légales |

Zéro dépendance obligatoire : Python 3.9+ (Pillow est utilisé pour les visuels
d'épingle s'il est disponible, sinon repli automatique).

---

## Architecture

```
halloween/
├── config.json                  ← tag Amazon, nom du site, couleurs, thème
├── publier.py                   ← ligne de commande (tout passe par ici)
├── DEMARRAGE.md                 ← guide d'installation pas à pas
│
├── data/
│   ├── produits.json            ← catalogue des costumes + ASIN (à enrichir)
│   ├── sujets.json              ← sujets prioritaires + axes de combinaison
│   ├── etat.json                ← journal des publications (généré)
│   └── articles/                ← un JSON par article publié (généré)
│
├── src/                         ← moteur (identique au site coiffeuse, adapté)
└── site/                        ← le site généré, prêt à héberger (ignoré par git)
```

Le moteur est le même que celui du site coiffeuse. Les seuls fichiers propres à
Halloween sont : `config.json`, `data/produits.json`, `data/sujets.json`, le fond
éditorial de secours `src/redaction_locale.py`, le prompt de `src/redacteur.py`,
et quelques libellés dans `src/gabarits.py`, `src/site.py` et `src/visuels.py`.

---

## Le calendrier éditorial

Le moteur ne tombe jamais en panne de sujets :

1. **24 sujets prioritaires** écrits à la main (meilleur déguisement, femme,
   homme, enfant, couple, groupe, sorcière, vampire, squelette, zombie, bébé,
   pas cher, dernière minute, effrayant, maquillage, accessoires, chien, ado,
   fantôme, famille, diable, fait maison, original, grande taille).
2. **Expansion combinatoire** : 12 personnages/attributs × 10 contextes × 6
   formats, soit plus de **170 sujets uniques** supplémentaires.
3. **20 questions fréquentes** développées en articles complets.
4. File épuisée : les articles les plus anciens repassent en **mise à jour**.

```bash
python publier.py --sujets 30    # voir les 30 prochains jours
```

---

## Conformité Amazon Partenaires

- **Aucun prix n'est jamais écrit** dans les articles (le contrat l'interdit hors
  Product Advertising API) : le système affiche toujours « Voir le prix sur Amazon ».
- **Mention d'affiliation** en haut de chaque article et en pied de page.
- **Page mentions légales** générée automatiquement.
- Liens en `rel="sponsored nofollow noopener"` et `target="_blank"`.
- Le rédacteur **n'écrit jamais d'URL** : toutes les adresses sont fabriquées par
  `src/affiliation.py` à partir du catalogue et du tag. Aucun lien inventé possible.

---

## Aide-mémoire des commandes

| Commande | Effet |
|---|---|
| `python publier.py` | article du jour + reconstruction du site |
| `python publier.py --nombre 7` | 7 articles d'un coup |
| `python publier.py --sujet costume-sorciere` | force un sujet précis |
| `python publier.py --mode local` | rédige sans appeler l'API |
| `python publier.py --site` | reconstruit le site sans rédiger |
| `python publier.py --sujets 30` | affiche les 30 prochains sujets prévus |
| `python publier.py --produits` | état du catalogue et des liens |
| `python publier.py --regenerer <id>` | réécrit les articles d'un produit modifié |
| `python publier.py --verifier` | contrôle qualité complet |

> Toutes les commandes se lancent **depuis le dossier `halloween/`**.

---

## Les deux modes de rédaction

| | `api` (recommandé) | `local` |
|---|---|---|
| Texte | Unique à chaque article | Assemblé à partir de blocs de fond |
| Coût | Quelques centimes par article | Gratuit |
| Usage | Publication quotidienne réelle | Tests, dépannage, secours |

Le mode `api` bascule automatiquement en `local` si la clé API est absente ou si
l'API est indisponible : aucune journée sans publication. Les 24 articles livrés
en démonstration ont été rédigés en mode `local` ; avant la mise en ligne réelle,
laissez le mode `api` produire des textes uniques (voir DEMARRAGE.md).
