# Modèle d'import produits Shopify — Maison AM Prestige

`modele-import-shopify.csv` est un **gabarit** au format d'import natif Shopify
(Boutique en ligne → Produits → Importer). Il contient 3 blocs d'exemple à
dupliquer, avec **toutes les règles légales déjà verrouillées**. Tu n'as qu'à
remplacer les `[MARQUEURS]` par les données réelles du fournisseur, puis importer.

## Règles déjà intégrées (ne pas modifier)

- **`Variant Taxable = FALSE`** sur **toutes** les lignes → franchise en base, art. 293 B du CGI (aucune TVA).
- **`Status = draft`** partout → rien ne part en ligne à l'import (tu publies quand la fiche est complète, GPSR incluse).
- **`Variant Barcode` vide** → aucun GTIN inventé (une colonne vide vaut mieux qu'une fausse).
- **6 variantes de taille `XS → XXL`** pour chaque tenue (bloc « costume »).
- **Bloc GPSR** dans la description : fabricant, responsable UE, référence, avertissements.
- **Bloc Fabrication** (tissage / teinture / confection) → « non communiqué » par défaut, jamais un pays inventé (loi n° 2026-602).
- **Pas de `Compare At Price`** rempli → aucun prix barré sans 30 jours de prix pratiqué.
- Mention « TVA non applicable, art. 293 B du CGI » dans chaque description.

## Les 3 blocs d'exemple

1. **`costume-exemple-sorciere`** — un costume, 6 variantes XS→XXL. `Published = FALSE` et tag `composant-pack` :
   c'est un **composant de pack**, non vendu à l'unité (§6). Duplique ce bloc pour tes 17 costumes.
2. **`accessoire-exemple-chapeau`** — un accessoire, 1 variante « Taille unique », vendable seul (`Published = TRUE`).
3. **`pack-exemple-couple`** — un pack, 1 variante, prix du pack. Duplique pour tes 6 packs.

## Comment remplir

Pour chaque produit, remplace :
- `[TITRE…]`, `[DESCRIPTION…]`, `[SKU…]` ;
- `Variant Price` = ton prix (nombre seul, ex. `39.90`, sans « € ») ;
- `Variant Grams` = poids réel si connu (sinon laisse 0) ;
- dans la description : `[FABRICANT + ADRESSE]`, `[RESPONSABLE UE]`, `[RÉFÉRENCE]`, `[AVERTISSEMENTS]`, et les 3 lieux de fabrication (ou « non communiqué ») ;
- `Image Src` = URL publique d'une image (uniquement des visuels que tu es autorisé à utiliser).

> **Costumes en pack (§6)** : garde `Published = FALSE` sur les 17 costumes-composants ;
> seuls les **packs** et les **accessoires** sont `Published = TRUE`. Un costume-composant
> ne doit pas être achetable seul (à l'unité il coûte plus cher que son prix de marché).

## Rappels de conformité avant publication

- Un **costume enfant** est un **jouet** : pas de mise en vente sans **déclaration 2009/48/CE** et marquage CE (§8).
- **Pas de lentilles** de contact fantaisie.
- Tant qu'un `[MARQUEUR]` GPSR subsiste, la fiche **reste en brouillon**.
- Renseigne l'**ID Refashion** (obtenu du grossiste) dans la page /pages/conformite-securite-produits.

## Ce qu'il me faut pour finir à ta place

Colle-moi les **tarifs + fiches fournisseur** (noms, prix à l'unité, tailles cm,
GPSR, lieux de fabrication, images) et je remplis ce CSV pour les 37 références +
je recalcule les marges, les 6 prix de packs et les 5 paliers de budget.
