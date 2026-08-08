# ÉTAT D'AVANCEMENT DU PROJET

> **Fichier de mémoire du projet.** À lire en premier au début de chaque séance de
> travail, et à mettre à jour à la fin de chaque itération.
>
> Dernière mise à jour : **itération 2** — 2026-08-08

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
Phase 3 : Implémentation du socle (données, constantes) .... ██████████ 100 %  TERMINÉ
Phase 4 : Implémentation du modèle MILP .................... ██████████ 100 %  TERMINÉ
Phase 5 : Validation, tests, analyse de résultats .......... ██████████ 100 %  TERMINÉ
Phase 6 : Génération du rapport Excel ...................... ██████████ 100 %  TERMINÉ
Phase 7 : Rapport de stage LaTeX → PDF ..................... ░░░░░░░░░░   0 %  À FAIRE
```

**Position actuelle : fin de la Phase 6.**
Le modèle est implémenté, résolu, validé et documenté. Il ne reste que le rapport LaTeX.

### Résultat en une ligne
Statut **Optimal** en 0,06 s, **100 % de la demande servie**, **86 contrôles de
validation réussis sur 86**, et deux violations structurelles identifiées avec leur
cause et leur remède.

---

## 3. Ce qui a été fait

### Itération 1 — Compréhension et formalisation
- Les **9 documents** du dossier `documentation-ocp/` lus intégralement.
- **8 documents pédagogiques** rédigés (`docs-helper/00` à `07`).
- Toutes les valeurs numériques **recalculées** : **11 anomalies** identifiées.
- Modèle mathématique complet : 8 ensembles, 23 familles de paramètres, 9 familles de
  variables, 19 familles de contraintes, objectif lexicographique à 3 niveaux.

### Itération 2 — Implémentation, résolution, validation
- **Paquet Python complet** : `src/ocp_optim/` (13 modules).
- **Modèle MILP** résolu par PuLP/CBC : 170 variables dont 29 binaires, 138 contraintes.
- **Résolution lexicographique** en 3 passes, statut **Optimal** en 0,06 s.
- **Validateur indépendant** : 86 contrôles, tous réussis.
- **138 tests** automatisés (1,2 s), dont 13 tests de corruption du validateur.
- **Rapports Excel (5 feuilles) et JSON** conformes à `OUTPUT_FORMAT.md`.
- **Analyses de sensibilité** sur les trois paramètres incertains.
- Deux documents pédagogiques supplémentaires : `08_IMPLEMENTATION`, `09_RESULTATS`.

---

## 4. Résultats obtenus

| Indicateur | Valeur |
|---|---|
| Statut | **Optimal**, 0,06 s |
| Demande satisfaite | **100 %** |
| Validation | **86 / 86** contrôles |
| Niveau 1 (demande non servie) | 0,000 |
| Niveau 2 (violations molles) | 1 268,3 |
| Niveau 3 (coût opératoire) | 3 111,9 |

**Plan optimal :** décadmiation de 750 t sur 13XY · 3 transferts interzones
(13F → 13ZU, 13F → 13E, 13CD → 13AB) · clarification sur 14XY (DEC) et 14ZU (NCL).

**Deux violations structurelles**, de cause unique — trop d'échelons affectés à la
cocristallisation :
1. IR11 déborde de **1 016 t/jour** ;
2. le stock de 14EXT reste **252 t sous sa bande** de sécurité.

**Remède chiffré :** ramener de 4 à 1 le nombre d'échelons de 14EXT en cocristallisation
résorbe **intégralement** les deux violations, sans aucun investissement.

Détail complet dans `docs-helper/09_RESULTATS.md`.

---

## 5. Ce qu'il reste à faire

**Phase 7 uniquement** — le rapport de stage LaTeX → PDF. Voir `TODO.md`.

---

## 6. Questions en attente

Aucune ne bloque. Toutes sont traitées comme des paramètres explicites, et l'analyse de
sensibilité mesure l'effet de l'incertitude.

| Question | Statut |
|---|---|
| Q1 — valeur de `MAX_TRANSFER` | **résolue par l'analyse** : sans effet au-delà de 750 t |
| Q2 — seuil de DEC_CL obligatoire (α) | en attente ; domaine admissible établi : α ≲ 0,22 |
| Q4 — unité en tonnes de P₂O₅ | en attente ; confiance élevée (3 preuves) |
| Q5 — destination des boues de CoC | en attente ; paramétrable dans le code |
| **Q11** — réduire les échelons CoC de 14EXT ? | **nouvelle, prioritaire** |
| **Q12** — débouché non modélisé pour l'excédent de CoC ? | **nouvelle** |
| **Q13** — seconde ligne habilitée au DEC_CL ? | **nouvelle** |

---

## 7. Arborescence du dépôt

```
ocp-intern/
├── README.md
├── pyproject.toml
├── PILOTAGE/                 ← mémoire et pilotage
│   ├── ETAT_AVANCEMENT.md    ← CE FICHIER
│   ├── TODO.md · JOURNAL.md · DECISIONS.md · QUESTIONS_ENCADRANT.md
├── docs-helper/              ← 10 documents pédagogiques
│   └── 00_COMMENCER_ICI … 09_RESULTATS
├── src/ocp_optim/            ← le code
│   ├── constants · units · profiles · scenario · preprocessing
│   ├── model/ (variables · constraints · objective)
│   ├── solver · results · validation · analysis · cli
│   └── reporting/ (excel · json_export)
├── tests/                    ← 138 tests
├── data/                     ← profils qualité, scénarios
└── documentation-ocp/        ← documents originaux (NE PAS MODIFIER)
```

---

## 8. Prochaine séance : par où commencer ?

1. Lire `docs-helper/09_RESULTATS.md` — c'est là que sont les conclusions.
2. Poser à l'encadrant les questions **Q11, Q12, Q13**, les plus actionnables.
3. Me dire : **« on passe à la Phase 7 »** (rapport LaTeX).
