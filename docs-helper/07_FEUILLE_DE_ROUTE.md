# 07 — FEUILLE DE ROUTE DU STAGE

> Le plan complet, de la première lecture au rapport final.
> Chaque phase indique : son objectif, ses livrables, ses critères d'achèvement.

---

## Vue d'ensemble

```
Phase 0  Cadrage et système de continuité              ✅ TERMINÉ
Phase 1  Compréhension du métier                       ✅ TERMINÉ
Phase 2  Formalisation mathématique                    ✅ TERMINÉ
─────────────────────────────────────────────────────────────────
Phase 3  Socle logiciel                                ⬜ SUIVANTE
Phase 4  Modèle d'optimisation
Phase 5  Validation et analyse
Phase 6  Rapport Excel
Phase 7  Rapport de stage LaTeX
```

---

## Phases terminées

### Phase 0 — Cadrage ✅
Structure de travail, système de mémoire (`PILOTAGE/`), feuille de route.

### Phase 1 — Compréhension ✅
Lecture des 9 documents, enrichissement du contexte industriel, identification de l'unité
(tonne de P₂O₅), vérification arithmétique complète, recensement des 11 anomalies.
**Livrables :** `docs-helper/01` à `04` et `06`.

### Phase 2 — Formalisation ✅
Modèle complet : 8 ensembles, 23 familles de paramètres, 9 familles de variables,
19 familles de contraintes, objectif lexicographique à 3 niveaux, 12 hypothèses tracées.
**Livrable :** `docs-helper/05`.

---

## Phase 3 — Socle logiciel ⬜ *(prochaine étape)*

### Objectif
Construire les fondations : constantes, conversions, chargement de scénario, profils
qualité. **Aucune optimisation à ce stade** — uniquement des données propres et testées.

### Architecture proposée

```
src/ocp_optim/
├── __init__.py
├── constants.py       # constantes physiques, matrices, rendements
├── units.py           # conversions hauteur → tonnes P₂O₅
├── scenario.py        # chargement + validation d'un scénario
├── profiles.py        # profils qualité, demande → besoins en acide
├── preprocessing.py   # calcul des paramètres dérivés (Π, G, R…)
├── model/
│   ├── sets.py
│   ├── variables.py
│   ├── constraints.py
│   └── objective.py
├── solver.py          # orchestration, résolution lexicographique
├── validation.py      # vérificateurs (bilan matière, capacités…)
└── reporting/
    ├── excel.py
    └── json_export.py

tests/                 # miroir de src/, un fichier de test par module
data/
├── scenarios/real_scenario.json
└── quality_profiles.json      # RECONSTRUIT (voir A-10)
```

### Justification de cette architecture
- **Modulaire** — un module, une responsabilité. On peut remplacer le solveur sans toucher
  au reste.
- **Testable** — chaque module a des entrées/sorties pures, donc testable isolément.
- **Le pré-traitement est séparé de l'optimisation** — c'est la conséquence directe du fait
  qu'une grande partie du système est déterministe (`03` §7). On calcule d'abord tout ce
  qui est calculable, puis on optimise le reste.

### Livrables
- [ ] `constants.py` — toutes les constantes du document `04` §9
- [ ] `units.py` + tests (les 4 conversions doivent reproduire les stocks initiaux)
- [ ] `data/quality_profiles.json` reconstruit
- [ ] `scenario.py` avec validation stricte (un scénario incomplet doit échouer clairement)
- [ ] `data/scenarios/real_scenario.json`
- [ ] `preprocessing.py` — calcul de $\Pi_m$, $G_m$, $R_{k,a}$
- [ ] Tests unitaires : couverture ≥ 90 % sur le socle

### Critères d'achèvement
- `pytest` passe intégralement
- Le chargement du scénario réel reproduit **exactement** les valeurs du document `04` §7
- La production P54 calculée vaut **6 981,7 t**
- La demande totale calculée vaut **5 811,79 t**

---

## Phase 4 — Modèle d'optimisation ⬜

### Objectif
Traduire le modèle mathématique du document `05` en code, et le résoudre.

### Méthode
Une fonction par famille de contraintes, nommée d'après sa référence :
`add_c07_bilan_acide_29_std(model, ...)`. La correspondance code ↔ documentation est ainsi
immédiate et vérifiable.

### Choix technique : PuLP + CBC

| Critère | Justification |
|---|---|
| **Libre** | aucune licence — indispensable pour un stage et pour la pérennité chez OCP |
| **Suffisant** | ≈ 29 binaires, ≈ 200 contraintes : trivial pour CBC |
| **Lisible** | la syntaxe PuLP est proche de la notation mathématique |
| **Portable** | installation par `pip`, aucun composant externe |

Si les performances devenaient un problème (elles ne le seront pas), PuLP permet de basculer
sur Gurobi ou CPLEX **en changeant une seule ligne**.

### Livrables
- [ ] Modules `model/*.py`
- [ ] `solver.py` avec résolution lexicographique en 3 passes
- [ ] Statut `Optimal` sur le scénario réel
- [ ] Test de non-régression sur la valeur de l'objectif

### Critères d'achèvement
- Résolution en moins de 10 s
- Chaque contrainte du document `05` a sa fonction, nommée d'après elle
- Les niveaux 1, 2 et 3 sont résolus dans l'ordre, avec leurs valeurs journalisées

---

## Phase 5 — Validation et analyse ⬜

### Objectif
Prouver que la solution est **correcte** (elle respecte la physique) et **bonne**
(elle exploite bien le système).

### Deux volets

**Volet 1 — Validation.** Un vérificateur indépendant du solveur, qui recalcule tout à
partir de la solution :
- bilan matière fermé sur les 19 nœuds (tolérance 0,1 %)
- demandes satisfaites (tolérance 0,01 t)
- capacités respectées (tolérance 0)
- règles de procédé respectées (niveaux discrets, rendements)

> **Pourquoi un vérificateur indépendant ?** Si le modèle contient une erreur de
> formulation, le solveur renverra une solution « optimale » **pour un mauvais problème**.
> Seul un contrôle écrit séparément, à partir des équations physiques et non du modèle, peut
> le détecter. C'est le principe de la double vérification.

**Volet 2 — Analyse.**
- identification des **contraintes actives** → les goulots d'étranglement réels
- **analyse de sensibilité** sur les paramètres incertains : $\alpha$, $\tau^{\max}$,
  $Z^{\max}_{29}$ (hypothèses H7, H8, H9)
- comparaison avec la simulation manuelle de l'encadrant, et explication des écarts
- valeurs duales : combien vaudrait une tonne de capacité de décanteur supplémentaire ?

> **L'analyse de sensibilité est la réponse méthodologique correcte à une donnée
> incertaine.** On ne devine pas la valeur : on montre l'influence de son ignorance.
> C'est un excellent chapitre de rapport.

### Livrables
- [ ] `validation.py` + tests
- [ ] Rapport d'analyse de sensibilité (graphiques)
- [ ] Liste commentée des goulots d'étranglement

---

## Phase 6 — Rapport Excel ⬜

### Objectif
Produire le classeur à 5 feuilles conforme à `OUTPUT_FORMAT.md`.

| Feuille | Contenu |
|---|---|
| 1. Demand Delivery | par consommateur : produits, acide requis, acide livré et sa source |
| 2. Phosphoric Production | production P29 et P54, décadmiation, flux |
| 3. Acid 29 Stocks | mouvements et bilan matière de l'acide 29 |
| 4. Acid 54 Stocks | mouvements et bilan matière de l'acide 54 |
| 5. Central Storage Stocks | opérations sur IR11 et IR12 |

Mise en forme : retour à la ligne, alignement en haut, largeur automatique, traçabilité des
sources de chaque livraison.

### Livrables
- [ ] `reporting/excel.py` + tests (vérifier la présence et la structure des 5 feuilles)
- [ ] Export JSON complémentaire

---

## Phase 7 — Rapport de stage LaTeX ⬜

### Objectif
Un document académique et professionnel, compilé en PDF.

### Plan proposé

| Ch. | Titre | Contenu | Source |
|---|---|---|---|
| 1 | Présentation de l'organisme d'accueil | OCP, Jorf Lasfar, le service | `02` |
| 2 | Contexte et problématique | pourquoi ce problème existe, enjeux | `02` |
| 3 | Description du procédé industriel | le procédé, schémas de flux | `03` |
| 4 | Modélisation mathématique | ensembles, variables, contraintes, objectif | `05` |
| 5 | Analyse critique des spécifications | les 11 anomalies, les arbitrages | `06` |
| 6 | Implémentation logicielle | architecture, choix techniques, tests | Phases 3-4 |
| 7 | Résultats et validation | solution, bilans, sensibilité, goulots | Phase 5 |
| 8 | Conclusion et perspectives | bilan, extension multi-période | — |

### Points forts à mettre en avant

Trois éléments distingueront ce rapport d'un rapport de stage ordinaire :

1. **La démonstration de dégénérescence de l'objectif** (`05` §7.1). Trouver qu'une
   spécification est mathématiquement vide, le prouver, et proposer une correction rigoureuse
   — c'est un travail d'ingénieur, pas d'exécutant.
2. **L'identification de l'unité P₂O₅** (`04` §2). Une déduction non triviale, appuyée par
   trois preuves indépendantes, sans laquelle tout le modèle serait faux.
3. **L'audit des spécifications** (`06`). Onze anomalies détectées, chacune prouvée et
   arbitrée avec justification.

### Choix techniques LaTeX
- Classe `report`, `babel` en français, `amsmath` pour les équations
- Schémas de flux en `TikZ` (vectoriel, cohérent avec le reste du document)
- Bibliographie `biblatex`
- Compilation par `latexmk -pdf`
- Page de garde aux couleurs INSEA / OCP

### Livrables
- [ ] Sources LaTeX dans `rapport/`
- [ ] PDF compilé
- [ ] Figures vectorielles

---

## Comment nous travaillons ensemble

### À chaque itération
1. Je te rappelle **où on en est**, ce qui est fait, ce qui reste.
2. Je te dis **ce que tu dois lire ou vérifier**.
3. Je réalise le travail de l'étape.
4. Je mets à jour `PILOTAGE/ETAT_AVANCEMENT.md`, `TODO.md` et `JOURNAL.md`.
5. Je te dis **quelle est la prochaine étape**.

### Règles que je m'impose
- Toute décision est **justifiée** et consignée dans `DECISIONS.md`.
- Toute incertitude est **signalée**, jamais dissimulée sous une valeur inventée.
- Aucun chiffre n'est recopié sans être **recalculé**.
- Tout code est **testé** avant d'être déclaré terminé.
- Toute équation est **expliquée en français** et **rattachée** à un organe industriel.

### Ce que j'attends de toi
- Lire les documents dans l'ordre indiqué.
- Poser les questions de `QUESTIONS_ENCADRANT.md` à ton encadrant.
- Me signaler dès qu'une explication n'est pas claire — un document que tu ne comprends pas
  est un document à réécrire.
- Me transmettre les réponses de l'encadrant dès que tu les as.

---

## Estimation du reste à faire

| Phase | Charge estimée |
|---|---|
| Phase 3 — Socle | 1 itération |
| Phase 4 — Modèle | 1 à 2 itérations |
| Phase 5 — Validation | 1 à 2 itérations |
| Phase 6 — Excel | 1 itération |
| Phase 7 — Rapport | 2 à 3 itérations |

**Total : 6 à 9 itérations.** La Phase 2 étant achevée, l'essentiel de la difficulté
conceptuelle est derrière nous : la suite est du travail d'exécution rigoureux.
