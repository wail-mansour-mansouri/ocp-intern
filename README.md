# Optimisation de la production et distribution d'acide phosphorique — OCP Jorf Lasfar

Projet de stage d'ingénieur — INSEA, filière Data & Software Engineering.

---

## 🚀 Par où commencer ?

| Tu veux… | Va voir |
|---|---|
| **Découvrir le projet** | [`docs-helper/00_COMMENCER_ICI.md`](docs-helper/00_COMMENCER_ICI.md) |
| **Savoir où on en est** | [`PILOTAGE/ETAT_AVANCEMENT.md`](PILOTAGE/ETAT_AVANCEMENT.md) |
| **Voir ce qu'il reste à faire** | [`PILOTAGE/TODO.md`](PILOTAGE/TODO.md) |
| **Comprendre une décision** | [`PILOTAGE/DECISIONS.md`](PILOTAGE/DECISIONS.md) |

---

## Le sujet en trois phrases

L'OCP produit à Jorf Lasfar de l'acide phosphorique sur six lignes à 29 % de P₂O₅, concentré
en acide à 54 % sur cinq lignes, puis purifié par trois procédés (décadmiation,
clarification, cocristallisation) avant d'être distribué à neuf consommateurs.

Chaque jour, il faut décider **combien décadmier, combien clarifier, quels transferts
effectuer entre ateliers et qui sert qui**, en respectant les contraintes physiques de
l'usine.

Ce projet formalise ce problème en **programme linéaire mixte en nombres entiers** et le
résout de façon optimale.

---

## Structure du dépôt

```
├── docs-helper/          📘 Documents pédagogiques — TOUT le projet expliqué
├── PILOTAGE/             🧭 Mémoire du projet : état, TODO, journal, décisions
└── documentation-ocp/    📁 Documents originaux de l'encadrant (ne pas modifier)
```

### `docs-helper/` — la documentation du projet

| Fichier | Contenu |
|---|---|
| `00_COMMENCER_ICI.md` | Point d'entrée, ordre de lecture, les 6 idées clés |
| `01_GLOSSAIRE.md` | Tous les termes du sujet |
| `02_CONTEXTE_INDUSTRIEL.md` | OCP, Jorf Lasfar, les acteurs, les enjeux |
| `03_PROCEDE_DETAILLE.md` | Le procédé, organe par organe, avec schémas |
| `04_DONNEES_ET_CONVENTIONS.md` | Toutes les données, recalculées et vérifiées |
| `05_MODELE_MATHEMATIQUE.md` | Ensembles, variables, contraintes, objectif |
| `06_ANOMALIES_ET_DECISIONS.md` | Les 11 anomalies du dossier et leurs arbitrages |
| `07_FEUILLE_DE_ROUTE.md` | Plan complet du stage, phase par phase |

---

## Avancement

```
Phase 0  Cadrage                        ██████████ 100 %
Phase 1  Compréhension du métier        ██████████ 100 %
Phase 2  Formalisation mathématique     ██████████ 100 %
Phase 3  Socle logiciel                 ░░░░░░░░░░   0 %   ← prochaine étape
Phase 4  Modèle d'optimisation          ░░░░░░░░░░   0 %
Phase 5  Validation et analyse          ░░░░░░░░░░   0 %
Phase 6  Rapport Excel                  ░░░░░░░░░░   0 %
Phase 7  Rapport de stage LaTeX         ░░░░░░░░░░   0 %
```

---

## Trois résultats déjà obtenus

**1. L'unité du modèle est la tonne de P₂O₅, pas la tonne d'acide.**
Cette information n'est écrite nulle part dans le dossier ; elle a été déduite par trois
preuves indépendantes. Sans elle, tous les bilans matière sont faux.
→ `docs-helper/04`, §2

**2. La fonction objectif spécifiée est mathématiquement dégénérée.**
« Maximiser le total livré » sous contrainte de satisfaction exacte de la demande donne un
objectif **constant** sur tout le domaine réalisable. Un objectif lexicographique à trois
niveaux est proposé, qui généralise strictement l'objectif demandé.
→ `docs-helper/05`, §7.1

**3. Onze anomalies ont été identifiées dans les spécifications**, dont quatre erreurs
arithmétiques franches (jusqu'à 59 % d'écart). Chacune est prouvée et arbitrée.
→ `docs-helper/06`

---

## Nature du problème

| Caractéristique | Valeur |
|---|---|
| Type | MILP mono-période |
| Horizon | 1 journée |
| Unité | tonne de P₂O₅ |
| Variables continues | ≈ 175 |
| Variables binaires | ≈ 29 |
| Contraintes | ≈ 200 |
| Objectif | lexicographique, 3 niveaux |
| Solveur envisagé | PuLP + CBC |
