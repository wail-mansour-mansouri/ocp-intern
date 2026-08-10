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
├── rapport/              📄 Rapport de stage LaTeX → PDF (79 pages)
├── src/ocp_optim/        ⚙️  Le code (13 modules)
├── tests/                ✅ 138 tests
├── data/                 📊 Profils qualité et scénarios
└── documentation-ocp/    📁 Documents originaux de l'encadrant (ne pas modifier)
```

## Lancer le programme

```bash
pip install -e ".[dev]"

python -m ocp_optim                        # résout et affiche la synthèse
python -m ocp_optim --sortie resultats/    # rapports Excel (5 feuilles) et JSON
python -m ocp_optim --sensibilite          # analyses de sensibilité

pytest                                     # 138 tests, ~1,2 s

cd rapport && make                         # compile le rapport en PDF
```

### `docs-helper/` — la documentation du projet

| Fichier | Contenu |
|---|---|
| `00_COMMENCER_ICI.md` | Point d'entrée, ordre de lecture, les 7 idées clés |
| `01_GLOSSAIRE.md` | Tous les termes du sujet |
| `02_CONTEXTE_INDUSTRIEL.md` | OCP, Jorf Lasfar, les acteurs, les enjeux |
| `03_PROCEDE_DETAILLE.md` | Le procédé, organe par organe, avec schémas |
| `04_DONNEES_ET_CONVENTIONS.md` | Toutes les données, recalculées et vérifiées |
| `05_MODELE_MATHEMATIQUE.md` | Ensembles, variables, contraintes, objectif |
| `06_ANOMALIES_ET_DECISIONS.md` | Les 11 anomalies du dossier et leurs arbitrages |
| `07_FEUILLE_DE_ROUTE.md` | Plan complet du stage, phase par phase |
| `08_IMPLEMENTATION.md` | Le code : architecture, points délicats, stratégie de test |
| `09_RESULTATS.md` | **Résultats, analyses de sensibilité, recommandations** |

---

## Avancement

```
Phase 0  Cadrage                        ██████████ 100 %
Phase 1  Compréhension du métier        ██████████ 100 %
Phase 2  Formalisation mathématique     ██████████ 100 %
Phase 3  Socle logiciel                 ██████████ 100 %
Phase 4  Modèle d'optimisation          ██████████ 100 %
Phase 5  Validation et analyse          ██████████ 100 %
Phase 6  Rapport Excel                  ██████████ 100 %
Phase 7  Rapport de stage LaTeX         ██████████ 100 %
```

---

## Résultat de l'optimisation

| Indicateur | Valeur |
|---|---|
| Statut | **Optimal** en 0,06 s |
| Demande satisfaite | **100 %** |
| Validation indépendante | **86 / 86** contrôles |
| Taille du problème | 170 variables (29 binaires), 138 contraintes |

**Plan optimal :** 750 t de décadmiation sur 13XY · 3 transferts interzones ·
clarification sur 14XY (décadmiée) et 14ZU (ordinaire).

**Deux violations structurelles identifiées**, de cause unique — trop d'échelons affectés
à la cocristallisation : IR11 déborde de 1 016 t/jour, et le stock de 14EXT reste 252 t
sous sa bande de sécurité.

> **🎯 Recommandation chiffrée.** Ramener de 4 à 1 le nombre d'échelons de 14EXT en
> cocristallisation résorbe **intégralement** les deux violations, sans investissement et
> sans dégrader le service. → `docs-helper/09_RESULTATS.md`

## Quatre apports du travail

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

**4. Le validateur indépendant a détecté un vrai bug.** Écrit à partir des équations
physiques et non des contraintes du modèle, il a relevé une erreur d'agrégation des
livraisons depuis IR11 qu'un contrôle interne n'aurait jamais vue. C'est la justification
concrète du principe de double vérification.
→ `docs-helper/08`, §2

---

## Nature du problème

| Caractéristique | Valeur |
|---|---|
| Type | MILP mono-période |
| Horizon | 1 journée |
| Unité | tonne de P₂O₅ |
| Variables continues | 141 |
| Variables binaires | 29 |
| Contraintes | 138 |
| Objectif | lexicographique, 3 niveaux |
| Solveur | PuLP + CBC |
