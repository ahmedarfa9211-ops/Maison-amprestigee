# Pages légales — Maison AM Prestige (Shopify)

Socle légal complet de la boutique, prêt à coller dans Shopify.
**Chaque page reste en BROUILLON tant qu'un marqueur `[ ]` subsiste** (§7 du prompt maître).

## Comment intégrer dans Shopify

Pour chaque fichier : **Boutique en ligne → Pages → Ajouter une page**, saisir le titre
indiqué, cliquer sur `<>` (Afficher le code HTML) et coller le contenu du fichier.
Vérifier ensuite le *handle* (URL) pour qu'il corresponde aux liens internes.

| Fichier | Titre de page | Handle attendu |
|---|---|---|
| 01-mentions-legales.html | Mentions légales | `mentions-legales` |
| 02-conditions-generales-de-vente.html | Conditions Générales de Vente | `conditions-generales-de-vente` |
| 03-politique-de-confidentialite.html | Politique de confidentialité | `politique-de-confidentialite` |
| 04-politique-de-cookies.html | Politique de cookies | `politique-de-cookies` |
| 05-droit-de-retractation.html | Droit de rétractation | `droit-de-retractation` |
| 06-livraison.html | Livraison | `livraison` |
| 07-paiement-securise.html | Paiement sécurisé | `paiement-securise` |
| 08-mediation-consommation.html | Médiation de la consommation | `mediation-consommation` |
| 09-retours-et-echanges.html | Retours et échanges | `retours-et-echanges` |
| 10-conformite-securite-produits.html | Conformité et sécurité des produits | `conformite-securite-produits` |
| 11-tva-franchise-en-base.html | TVA — Franchise en base | `tva-franchise-en-base` |

À placer dans le pied de page du thème (menu « Informations légales »).

## Marqueurs à compléter avant publication

Tous ces éléments dépendent de vous (§11) — **ne rien inventer**. Une fois remplis, retirer les crochets.

| Marqueur | Où | Source |
|---|---|---|
| `[NOM PRÉNOM]` | toutes les pages | état civil de l'EI |
| `[ADRESSE COMPLÈTE]` | 01, 02, 03, 05 | adresse pro déclarée |
| `[SIREN — 9 chiffres]` | 01, 02 | INSEE / avis de situation |
| `[NUMÉRO RCS]` | 01, 02 | extrait RCS Nîmes |
| `[EMAIL DE CONTACT]` | toutes | e-mail pro |
| `[TÉLÉPHONE — facultatif]` | 01 | facultatif |
| `[DATE DE PUBLICATION]` | toutes | date de mise en ligne réelle |
| `[ADRESSE HÉBERGEUR À VÉRIFIER ...]` | 01 | à vérifier sur le contrat Shopify |
| `[OUTIL DE MESURE ...]` / `[RÉGIE ...]` | 04 | selon apps installées (Google Ads/Analytics) |
| `[... moyens de paiement ...]` | 07 | config Shopify Payments / PayPal |
| `[NOM DU MÉDIATEUR ...]` / `[ADRESSE ...]` / `[URL DE SAISINE ...]` | 08 | **souscription médiateur obligatoire** |
| `[IDENTIFIANT REFASHION ...]` | 10 | à obtenir **par écrit** du grossiste |

## Points de conformité intégrés (vérifiés dans les textes)

- **TVA** : « TVA non applicable, art. 293 B du CGI » sur mentions légales, CGV, paiement, page TVA.
- **Rétractation** : 14 j ; remboursement sous 14 j **frais de livraison standard inclus** ;
  frais de retour à la charge du client ; **exception hygiène L.221-28 5°** (dents, faux ongles,
  perruques descellés).
- **Responsabilité dropshipping** : L.221-15 (responsabilité pleine même via un tiers) + L.216-4
  (risque transport jusqu'à la remise) — assumés explicitement, pas seulement mentionnés.
- **Aucun stock chiffré** affiché ; disponibilité vérifiée avant confirmation.
- **GPSR (UE) 2023/988** + **jouets 2009/48/CE** (costumes enfants) + **origine textile**
  loi n° 2026-602 du 8 juillet 2026 (mention « non communiquée » par défaut, aucune origine inventée).
- **REP / Refashion** : identifiant en marqueur (redevable = metteur sur le marché français).
- **Médiateur** obligatoire ; **aucun lien ODR** (plateforme fermée le 20/07/2025).
- **Prix** : pas de prix barré sans 30 j de prix pratiqué ; économie des packs = écart réel.
- Frais de port 4,90 € (relais) / 6,90 € (domicile), **offerts dès 69 €** ; minimum 39 € ;
  France métropolitaine ; 2–5 j ouvrés (UE).

## HYPOTHÈSES RETENUES

1. Forme = micro-entrepreneur / EI immatriculée au RCS de Nîmes (repris du prompt maître).
2. Hébergeur = Shopify International Limited (Dublin) — adresse **à vérifier** avant publication (marquée).
3. Paiement = Shopify Payments (CB) + éventuellement PayPal — hypothèse standard Shopify Basic, à confirmer.
4. Transporteurs non nommés (non communiqués) → formulations génériques « point relais » / « domicile ».
5. Médiateur non encore souscrit → page prête, laissée en brouillon tant que le nom manque.
6. Aucun SIREN, RCS, adresse, ID Refashion, GTIN, marque ou lieu de fabrication n'a été inventé.
