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

## Phase 3 — Socle logiciel ⬜

- [ ] Choisir la structure du paquet Python et l'outillage (`pyproject.toml`, `pytest`, `ruff`)
- [ ] Module `constants.py` : lignes, échelons, matrices, rendements, bornes
- [ ] Module `units.py` : conversions hauteur (m) → tonnes P₂O₅, avec tests
- [ ] Reconstruire le fichier `quality_profiles.json` (**absent du dossier fourni**)
- [ ] Module `scenario.py` : chargement + validation d'un scénario (schéma strict)
- [ ] Encoder le scénario réel de `REAL_SCENARIO_REFERENCE.md`
- [ ] Tests unitaires du socle (conversions, profils, validation de scénario)

## Phase 4 — Modèle d'optimisation ⬜

- [ ] Choisir le solveur (proposition : **PuLP + CBC** — libre, suffisant, reproductible)
- [ ] Module `model/sets.py` : construction des ensembles à partir du scénario
- [ ] Module `model/variables.py` : déclaration des variables
- [ ] Module `model/constraints.py` : une fonction par famille de contraintes
- [ ] Module `model/objective.py` : objectif lexicographique (résolution en 3 passes)
- [ ] Module `solver.py` : orchestration, statut, extraction de la solution
- [ ] Vérifier : statut `Optimal` sur le scénario réel
- [ ] Test de non-régression sur la valeur de l'objectif

## Phase 5 — Validation et analyse ⬜

- [ ] Module `validation.py` : vérificateur de bilan matière (tolérance 0,1 %)
- [ ] Vérificateur de satisfaction de la demande (tolérance 0,01 t)
- [ ] Vérificateur de respect des capacités (tolérance 0)
- [ ] Vérificateur des règles de procédé (niveaux de décadmiation, rendements)
- [ ] Analyse de sensibilité sur les paramètres incertains (α, `MAX_TRANSFER`)
- [ ] Analyse des contraintes actives (goulots d'étranglement)
- [ ] Comparaison avec la simulation manuelle de l'encadrant

## Phase 6 — Rapport Excel ⬜

- [ ] Feuille 1 « Demand Delivery »
- [ ] Feuille 2 « Phosphoric Production »
- [ ] Feuille 3 « Acid 29 Stocks »
- [ ] Feuille 4 « Acid 54 Stocks »
- [ ] Feuille 5 « Central Storage Stocks »
- [ ] Mise en forme (retour à la ligne, largeur auto, alignement haut)
- [ ] Export JSON complémentaire (résultats lisibles par machine)

## Phase 7 — Rapport de stage LaTeX ⬜

- [ ] Squelette LaTeX (classe, page de garde INSEA/OCP, table des matières)
- [ ] Chapitre 1 — Présentation de l'organisme d'accueil
- [ ] Chapitre 2 — Contexte et problématique
- [ ] Chapitre 3 — Description du procédé industriel
- [ ] Chapitre 4 — Modélisation mathématique
- [ ] Chapitre 5 — Implémentation logicielle
- [ ] Chapitre 6 — Résultats et validation
- [ ] Chapitre 7 — Conclusion et perspectives
- [ ] Figures (schémas de flux, diagrammes d'architecture)
- [ ] Compilation `latexmk` → PDF, vérification typographique

## Transverse ⬜

- [?] Obtenir la valeur de `MAX_TRANSFER` auprès de l'encadrant
- [?] Obtenir le seuil de production obligatoire de DEC_CL
- [?] Obtenir le fichier `quality_profiles_v2.json` original
- [?] Faire confirmer que l'unité est bien la tonne de P₂O₅
- [?] Faire confirmer la destination des boues de cocristallisation (P29 ou P54 ?)
