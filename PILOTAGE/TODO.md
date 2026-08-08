# TODO — Liste des tâches par phase

> Convention : `[x]` fait · `[ ]` à faire · `[~]` en cours · `[?]` bloqué (attente encadrant)

---

## Phase 0 — Cadrage et système de continuité ✅

- [x] Explorer le dépôt et inventorier les documents fournis
- [x] Créer l'arborescence de travail (`PILOTAGE/`, `docs-helper/`)
- [x] Mettre en place le système de mémoire (état, TODO, journal, décisions, questions)
- [x] Définir les phases du stage et la feuille de route

## Phase 1 — Compréhension du métier ✅

- [x] Lire les 9 documents de `documentation-ocp/`
- [x] Enrichir le contexte industriel (recherche sur OCP Jorf Lasfar, EMAPHOS, IMACID)
- [x] Identifier l'unité de compte réelle du système (**tonne de P₂O₅**)
- [x] Rédiger le glossaire complet (`01_GLOSSAIRE.md`)
- [x] Rédiger le contexte industriel (`02_CONTEXTE_INDUSTRIEL.md`)
- [x] Rédiger la description détaillée du procédé (`03_PROCEDE_DETAILLE.md`)
- [x] Recenser et tabuler toutes les données et conventions (`04_DONNEES_ET_CONVENTIONS.md`)
- [x] Recalculer indépendamment toutes les valeurs dérivées des documents
- [x] Recenser les anomalies et arbitrer (`06_ANOMALIES_ET_DECISIONS.md`)

## Phase 2 — Formalisation mathématique ✅

- [x] Définir les ensembles d'indices
- [x] Définir les paramètres (données exogènes)
- [x] Définir les variables de décision
- [x] Écrire les contraintes de bilan matière (P29 std, P29 dec, P54 NCL, IR11, IR12)
- [x] Écrire les contraintes de procédé (concentration, clarification, cocristallisation)
- [x] Écrire les contraintes de capacité (décanteurs, cuves, transferts)
- [x] Écrire les contraintes d'interconnexion et de qualité
- [x] Démontrer que l'objectif « maximiser les livraisons » est **dégénéré**
- [x] Proposer et justifier un objectif lexicographique à 3 niveaux
- [x] Établir le tableau de correspondance contrainte ↔ réalité industrielle

## Phase 3 — Socle logiciel ✅

- [x] Choisir la structure du paquet Python et l'outillage (`pyproject.toml`, `pytest`, `ruff`)
- [x] Module `constants.py` : lignes, échelons, matrices, rendements, bornes
- [x] Module `units.py` : conversions hauteur (m) → tonnes P₂O₅, avec tests
- [x] Reconstruire le fichier `quality_profiles.json` (**absent du dossier fourni**)
- [x] Module `scenario.py` : chargement + validation d'un scénario (schéma strict)
- [x] Encoder le scénario réel de `REAL_SCENARIO_REFERENCE.md`
- [x] Tests unitaires du socle (conversions, profils, validation de scénario)

## Phase 4 — Modèle d'optimisation ✅

- [x] Choisir le solveur (proposition : **PuLP + CBC** — libre, suffisant, reproductible)
- [x] Module `model/sets.py` : construction des ensembles à partir du scénario
- [x] Module `model/variables.py` : déclaration des variables
- [x] Module `model/constraints.py` : une fonction par famille de contraintes
- [x] Module `model/objective.py` : objectif lexicographique (résolution en 3 passes)
- [x] Module `solver.py` : orchestration, statut, extraction de la solution
- [x] Vérifier : statut `Optimal` sur le scénario réel
- [x] Test de non-régression sur la valeur de l'objectif

## Phase 5 — Validation et analyse ✅

- [x] Module `validation.py` : vérificateur de bilan matière (tolérance 0,1 %)
- [x] Vérificateur de satisfaction de la demande (tolérance 0,01 t)
- [x] Vérificateur de respect des capacités (tolérance 0)
- [x] Vérificateur des règles de procédé (niveaux de décadmiation, rendements)
- [x] Analyse de sensibilité sur les paramètres incertains (α, `MAX_TRANSFER`)
- [x] Analyse des contraintes actives (goulots d'étranglement)
- [x] Comparaison avec la simulation manuelle de l'encadrant

## Phase 6 — Rapport Excel ✅

- [x] Feuille 1 « Demand Delivery »
- [x] Feuille 2 « Phosphoric Production »
- [x] Feuille 3 « Acid 29 Stocks »
- [x] Feuille 4 « Acid 54 Stocks »
- [x] Feuille 5 « Central Storage Stocks »
- [x] Mise en forme (retour à la ligne, largeur auto, alignement haut)
- [x] Export JSON complémentaire (résultats lisibles par machine)

## Phase 7 — Rapport de stage LaTeX ⬜ *(prochaine étape)*

- [ ] Squelette LaTeX (classe, page de garde INSEA / OCP, table des matières)
- [ ] Ch. 1 — Présentation de l'organisme d'accueil
- [ ] Ch. 2 — Contexte et problématique
- [ ] Ch. 3 — Description du procédé industriel
- [ ] Ch. 4 — Modélisation mathématique
- [ ] Ch. 5 — Analyse critique des spécifications (les 11 anomalies)
- [ ] Ch. 6 — Implémentation logicielle
- [ ] Ch. 7 — Résultats, validation et sensibilité
- [ ] Ch. 8 — Conclusion et perspectives
- [ ] Figures TikZ (schémas de flux, architecture)
- [ ] Compilation `latexmk` → PDF, relecture typographique

## Transverse

- [x] ~~Obtenir la valeur de `MAX_TRANSFER`~~ — l'analyse de sensibilité montre qu'au-delà
      de 750 t la solution ne change plus : la question devient informative
- [?] Obtenir le seuil de production obligatoire de DEC_CL (paramètre alpha)
- [?] Obtenir le fichier `quality_profiles_v2.json` original
- [?] Faire confirmer que l'unité est bien la tonne de P₂O₅ (confiance élevée)
- [?] Faire confirmer la destination des boues de cocristallisation (P29 ou P54 ?)

## Nouvelles questions issues des résultats (itération 2)

- [?] **Q11** — Peut-on réduire de 4 à 1 ou 2 le nombre d'échelons de 14EXT affectés à la
      cocristallisation ? C'est la seule action qui résorbe les deux violations
      structurelles, et elle ne demande aucun investissement.
- [?] **Q12** — L'excédent de CoC a-t-il un débouché non modélisé (vente d'acide marchand,
      export) ? Si oui, le débordement d'IR11 est un artefact de modélisation.
- [?] **Q13** — Si la valeur métier de alpha dépasse 0,22, il faut habiliter une seconde
      ligne à produire du DEC_CL : laquelle serait envisageable ?
