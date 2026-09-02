# Hooks Claude Code — portage Python pour Maison AMPrestige

Adaptation du bundle « claude hooks essentiels » (à l'origine en Node) pour ce
dépôt, qui est **100 % Python, zéro dépendance**. Les hooks sont donc eux aussi
écrits en pur Python 3.9+ (bibliothèque standard uniquement) : pas besoin
d'installer Node pour les faire tourner.

Rien ne sort de la machine. Rien ne s'installe globalement. Tout est
lisible en quelques minutes.

---

## Ce que ça fait

| Fichier | Événement | Rôle |
|---|---|---|
| `protection_config.py` | PreToolUse (Edit/Write) | **Bloque** la modification d'un `ruff.toml`, `.flake8`, `setup.cfg`, `mypy.ini`… existant |
| `accumuler_editions.py` | PostToolUse (Edit/Write) | Note les fichiers touchés dans un temporaire. Ne lance rien. |
| `formater_typer.py` | Stop | Formate (ruff/black) + type (mypy) **une seule fois** en fin de réponse |
| `verifier_traces_debug.py` | Stop | Signale les débogueurs (`breakpoint()`, `pdb`…) oubliés |
| `_fichiers_edites.py` | — | Module partagé (liste des fichiers édités). Pas un hook. |

Le câblage est dans **`.claude/settings.json`** (à la racine de `.claude/`).

### `protection_config` — le seul qui bloque

Le problème qu'il résout : un agent qui bute sur une règle de lint a tendance à
désactiver la règle plutôt qu'à corriger le code. La config se dégrade
silencieusement, réponse après réponse.

- Modifier une config **existante** → bloqué (code 2), message explicatif.
- **Créer** une config absente → autorisé (bootstrap légitime).
- Débloquer ponctuellement : `HOOKS_ALLOW_CONFIG_EDIT=1`

Sont protégés les fichiers de lint/format/type Python (`ruff.toml`,
`.ruff.toml`, `.flake8`, `.pylintrc`, `.isort.cfg`, `mypy.ini`, `setup.cfg`,
`tox.ini`, `pyrightconfig.json`…) plus, par sécurité, les configs JS/TS si le
projet en gagnait un jour.

`pyproject.toml` est **volontairement exclu** : il porte aussi les métadonnées
et les dépendances du projet, le bloquer casserait les ajouts légitimes.
`config.json` (couleurs, tag Amazon, réglages du site) est lui aussi hors liste
par défaut, car l'éditer est un geste courant et voulu — pour le protéger,
ajoutez `"config.json"` à l'ensemble `PROTEGES` dans `protection_config.py`.

### `verifier_traces_debug` — les débogueurs oubliés

Signale `breakpoint()`, `pdb`/`ipdb`/`pudb.set_trace()` et les `import pdb`
dans les fichiers Python édités pendant la réponse.

> **Pourquoi pas `print()` ?** La version Node d'origine traque `console.log`.
> Son équivalent direct serait `print()` — mais ce projet est un **outil en
> ligne de commande** où `print()` EST la sortie légitime (des dizaines
> d'occurrences voulues dans `publier.py` et `src/`). Le flag serait donc du
> bruit permanent. Le vrai résidu à retirer avant un commit, ce sont les
> points d'arrêt de débogage — jamais destinés à être livrés. C'est eux qu'on
> cible.

La détection :

- analyse **ligne par ligne** — une ligne commentée ou une occurrence dans une
  chaîne ne déclenche plus de faux positif ;
- donne le **numéro de ligne** et un extrait ;
- se limite aux fichiers **réellement édités pendant la session** ;
- échappatoire par ligne : commentaire `allow-debug`.

Exclus d'office : `test_*.py`, `*_test.py`, `conftest.py`, `tests/`, `scripts/`.

### `accumuler_editions` + `formater_typer` — la paire

L'approche naïve lance le formateur et le typeur après *chaque* édition. Sur
une réponse qui touche douze fichiers, c'est douze passes complètes — de la
latence pour rien.

Ici : le hook PostToolUse écrit juste un chemin dans un fichier temporaire.
Tout le travail arrive au `Stop`, une fois, groupé par racine de projet. Les
erreurs de type partent sur `stderr`, donc Claude les voit et peut corriger
dans la foulée.

Détails qui comptent :

- chaque hook Stop garde **son propre curseur** de lecture dans l'accumulateur
  (`_fichiers_edites.py`) : les deux voient la même liste, dans n'importe quel
  ordre, et deux `Stop` d'affilée ne retraitent rien ;
- `__pycache__/` et `.claude/plugins/` sont exclus ;
- résolution des outils : binaire sur le PATH, puis `python3 -m <outil>`.
  Jamais d'installation depuis PyPI ;
- **aucun** formateur/typeur configuré dans le projet → le hook ne fait rien,
  en silence. C'est le cas aujourd'hui (le projet n'a ni ruff, ni black, ni
  mypy) : les deux hooks Stop sont donc dormants, prêts à s'activer le jour où
  vous ajoutez `[tool.ruff]`, `[tool.black]` ou `[tool.mypy]` ;
- il **ne bloque jamais** (toujours code 0), même si un outil manque ou plante.

Formatage : `ruff format` (+ `ruff check --fix`) si `ruff.toml`/`[tool.ruff]`
présent, sinon `black` si `[tool.black]` présent. Typage : `mypy` si configuré
(`mypy.ini`, `[tool.mypy]`, ou section `[mypy]` dans `setup.cfg`/`tox.ini`).

---

## Installation

Déjà fait : les hooks vivent dans `.claude/hooks/` et sont câblés par
`.claude/settings.json`, tous deux versionnés dans le dépôt. Redémarrez Claude
Code pour qu'ils soient pris en compte.

### Vérifier que ça marche

```bash
# doit afficher "BLOQUÉ" et sortir en code 2 (dans un dossier ayant un ruff.toml)
echo '{"tool_input":{"file_path":"'$PWD'/ruff.toml"}}' \
  | python3 .claude/hooks/protection_config.py; echo "code=$?"
```

### Désinstaller

Supprimez le dossier `.claude/hooks/` et le bloc `hooks` de
`.claude/settings.json`. Aucun état persistant en dehors d'un fichier
temporaire par session dans le répertoire temp du système.

---

## Origine et licence

`protection_config.py` est adapté de
[affaan-m/ECC](https://github.com/affaan-m/ECC) (licence MIT).
`verifier_traces_debug.py` en reprend l'idée et la liste d'exclusions, mais la
détection vise les débogueurs Python et est réécrite. Les autres fichiers
reprennent le principe du traitement groupé au `Stop` et sont portés de zéro en
Python. Testé sur Python 3.11.
