# ÉTAT D'AVANCEMENT DU PROJET

> **Fichier de mémoire du projet.** À lire en premier au début de chaque séance de
> travail, et à mettre à jour à la fin de chaque itération.
>
> Dernière mise à jour : **itération 1** — 2026-08-08

---

## 1. Identité du projet

| Champ | Valeur |
|---|---|
| **Sujet** | Optimisation de la production et de la distribution d'acide phosphorique |
| **Site** | OCP Jorf Lasfar (Maroc) |
| **Nature** | Optimisation mathématique (programmation linéaire en nombres entiers) + développement logiciel |
| **Horizon de décision** | 1 journée (modèle mono-période) |
| **Unité de compte** | **tonne de P₂O₅ par jour** (voir `docs-helper/04`, §2 — point capital) |
| **Livrables finaux** | Modèle d'optimisation, code Python testé, rapport LaTeX, documentation |

---

## 2. Où en sommes-nous ?

```
Phase 0 : Cadrage et système de continuité ................. ██████████ 100 %  TERMINÉ
Phase 1 : Compréhension du métier .......................... ██████████ 100 %  TERMINÉ
Phase 2 : Formalisation mathématique ....................... ██████████ 100 %  TERMINÉ
Phase 3 : Implémentation du socle (données, constantes) .... ░░░░░░░░░░   0 %  À FAIRE
Phase 4 : Implémentation du modèle MILP .................... ░░░░░░░░░░   0 %  À FAIRE
Phase 5 : Validation, tests, analyse de résultats .......... ░░░░░░░░░░   0 %  À FAIRE
Phase 6 : Génération du rapport Excel ...................... ░░░░░░░░░░   0 %  À FAIRE
Phase 7 : Rapport de stage LaTeX → PDF ..................... ░░░░░░░░░░   0 %  À FAIRE
```

**Position actuelle : fin de la Phase 2.**
Le problème est entièrement compris et entièrement formalisé. Rien n'a encore été codé.

---

## 3. Ce qui a déjà été fait (itération 1)

### 3.1 Lecture et dépouillement
Les **9 documents** du dossier `documentation-ocp/` ont été lus intégralement :

| Document | Statut | Rôle |
|---|---|---|
| `PROCESS_GUIDE.md` | Lu, exploité | Référence du procédé industriel — **document maître** |
| `CORE_FIXED_ELEMENTS.md` | Lu, exploité | Constantes du système (lignes, capacités, matrices) |
| `REAL_SCENARIO_REFERENCE.md` | Lu, exploité | Jeu de données réel + critères de validation |
| `OUTPUT_FORMAT.md` | Lu, exploité | Format du rapport Excel à produire (5 feuilles) |
| `archive/OBJECTIVE_FUNCTION.md` | Lu, exploité | Objectifs métier (fonction objectif) |
| `archive/TECHNICAL_REFERENCE.md` | Lu, exploité | Architecture logicielle possible |
| `archive/IMPLEMENTATION_GUIDE.md` | Lu, exploité | Options de mise en œuvre |
| `archive/COMPREHENSIVE_SYSTEM_SIMULATION.md` | Lu, exploité | Exemple de calcul de bout en bout |
| `archive/TEST_REFERENCE_OUTPUT.md` | Lu, exploité | Jeu de test alternatif + format Excel 7 feuilles |

### 3.2 Documents d'aide produits
Le dossier `docs-helper/` contient **8 documents** rédigés pour toi. Ils permettent de
comprendre 100 % du projet **sans lire les documents originaux**.

### 3.3 Vérification arithmétique
Toutes les valeurs numériques des documents ont été **recalculées** indépendamment.
**11 anomalies** ont été identifiées (erreurs de calcul, contradictions, données manquantes).
→ Voir `docs-helper/06_ANOMALIES_ET_DECISIONS.md`.

### 3.4 Formalisation mathématique complète
Le modèle est posé : **8 ensembles, 23 familles de paramètres, 9 familles de variables,
19 familles de contraintes, 1 objectif lexicographique à 3 niveaux.**
→ Voir `docs-helper/05_MODELE_MATHEMATIQUE.md`.

---

## 4. Ce qu'il reste à faire

Voir `TODO.md` pour la liste détaillée. En résumé :

1. **Phase 3** — Construire le socle logiciel : constantes, chargement de scénario,
   conversion des hauteurs de cuve, profils qualité.
2. **Phase 4** — Écrire le modèle MILP (PuLP/CBC), le résoudre.
3. **Phase 5** — Valider : bilans matière, satisfaction de la demande, tests unitaires.
4. **Phase 6** — Produire le classeur Excel à 5 feuilles.
5. **Phase 7** — Rédiger le rapport de stage LaTeX.

---

## 5. Points bloquants / à confirmer avec l'encadrant

**5 questions** doivent lui être posées avant la Phase 4. Elles sont listées, formulées et
justifiées dans `QUESTIONS_ENCADRANT.md`. Les deux plus importantes :

- **Q1** — Quelle est la valeur de `MAX_TRANSFER` (borne haute des transferts interzones) ?
  Elle est utilisée dans le code fourni mais **jamais définie** dans la documentation.
- **Q2** — Comment quantifier l'obligation de produire du DEC_CL ? Le document dit qu'elle est
  « obligatoire » pour la qualité, mais ne donne **aucun seuil chiffré**.

En attendant les réponses, le modèle est construit avec des **paramètres explicites** et des
valeurs par défaut justifiées : changer la valeur ne changera pas une ligne de code.

---

## 6. Arborescence du dépôt

```
ocp-intern/
├── README.md                    ← porte d'entrée
├── PILOTAGE/                    ← mémoire et pilotage du projet
│   ├── ETAT_AVANCEMENT.md       ← CE FICHIER : où on en est
│   ├── TODO.md                  ← tâches détaillées par phase
│   ├── JOURNAL.md               ← journal des itérations
│   ├── DECISIONS.md             ← décisions techniques + justifications
│   └── QUESTIONS_ENCADRANT.md   ← questions à poser
├── docs-helper/                 ← documents pédagogiques (à lire)
│   ├── 00_COMMENCER_ICI.md
│   ├── 01_GLOSSAIRE.md
│   ├── 02_CONTEXTE_INDUSTRIEL.md
│   ├── 03_PROCEDE_DETAILLE.md
│   ├── 04_DONNEES_ET_CONVENTIONS.md
│   ├── 05_MODELE_MATHEMATIQUE.md
│   ├── 06_ANOMALIES_ET_DECISIONS.md
│   └── 07_FEUILLE_DE_ROUTE.md
└── documentation-ocp/           ← documents originaux de l'encadrant (NE PAS MODIFIER)
```

---

## 7. Prochaine séance : par où commencer ?

1. Lire `docs-helper/00_COMMENCER_ICI.md` (5 min) — il te donne l'ordre de lecture.
2. Lire les documents `01` à `06` dans l'ordre (≈ 3 h de lecture attentive).
3. Poser les questions de `QUESTIONS_ENCADRANT.md` à ton encadrant.
4. Me dire : **« on passe à la Phase 3 »**.
