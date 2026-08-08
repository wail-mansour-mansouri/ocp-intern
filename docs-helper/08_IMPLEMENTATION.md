# 08 — L'IMPLÉMENTATION LOGICIELLE

> Ce que le code fait, comment il est organisé, et pourquoi il l'est ainsi.
> À lire après le document `05` (modèle mathématique) : chaque module y renvoie.

---

## 1. Comment lancer le programme

```bash
pip install -e ".[dev]"          # installe le paquet et pytest

python -m ocp_optim                          # résout et affiche la synthèse
python -m ocp_optim --sortie resultats/      # écrit les rapports Excel et JSON
python -m ocp_optim --sensibilite            # ajoute les analyses de sensibilité

pytest                                       # 138 tests, environ 1,2 s
```

Le code de retour vaut **0** si la validation est conforme, **1** sinon : le programme
est donc utilisable dans une chaîne automatisée.

---

## 2. Architecture

```
src/ocp_optim/
├── constants.py       Constantes physiques et structurelles
├── units.py           Conversions hauteur (m) -> tonnes de P2O5
├── profiles.py        Profils qualité : demande d'engrais -> besoins d'acide
├── scenario.py        Chargement et validation stricte d'un scénario
├── preprocessing.py   Calcul des paramètres dérivés (déterministe)
├── model/
│   ├── variables.py   Déclaration des variables de décision
│   ├── constraints.py Une fonction par famille de contraintes (C02…C17)
│   └── objective.py   Les trois niveaux de l'objectif lexicographique
├── solver.py          Résolution lexicographique en trois passes
├── results.py         Extraction structurée de la solution
├── validation.py      Validateur INDÉPENDANT du modèle
├── analysis.py        Goulots d'étranglement et analyses de sensibilité
├── reporting/         Rapports Excel (5 feuilles) et JSON
└── cli.py             Interface en ligne de commande
```

### 2.1 La chaîne de traitement

```
   scénario JSON
        │
        ▼
   ┌────────────────┐  validation stricte : un scénario incohérent
   │  scenario.py   │  échoue tout de suite, avec un message précis
   └────────────────┘
        │
        ▼
   ┌────────────────┐  PRÉ-TRAITEMENT DÉTERMINISTE
   │preprocessing.py│  production d'acide 54, cocristallisation systématique,
   └────────────────┘  besoins consolidés
        │
        ▼
   ┌────────────────┐  MILP : 170 variables dont 29 binaires,
   │    model/      │  138 contraintes
   └────────────────┘
        │
        ▼
   ┌────────────────┐  trois passes lexicographiques (CBC)
   │   solver.py    │
   └────────────────┘
        │
        ▼
   ┌────────────────┐  vue métier de la solution
   │  results.py    │
   └────────────────┘
        │
        ├──────────► validation.py   contrôle indépendant (86 contrôles)
        ├──────────► analysis.py     goulots, sensibilité
        └──────────► reporting/      Excel et JSON
```

### 2.2 Les trois décisions d'architecture

**(a) Le pré-traitement est séparé de l'optimisation.**
Une grande partie du système n'est pas optimisable : la production d'acide 54 découle des
heures de marche, la cocristallisation est systématique. Ces grandeurs sont calculées une
fois pour toutes **avant** de construire le modèle.

*Pourquoi c'est important.* En faire des variables de décision donnerait un modèle plus
gros, plus lent, et surtout **faux** — il produirait des plans que l'usine ne peut pas
exécuter. C'est l'erreur la plus facile à commettre sur ce sujet.

**(b) Une fonction par famille de contraintes, nommée d'après sa référence.**
`c07_bilan_acide_29_std`, `c11_capacite_decanteurs`… La correspondance entre le document
`05` et le code se vérifie ligne à ligne. Une contrainte modifiée dans le modèle
mathématique se retrouve immédiatement dans le code, et réciproquement.

**(c) Le validateur ne relit jamais le modèle.**
`validation.py` recalcule les bilans **à partir des équations physiques**, pas des
contraintes posées dans `model/`.

*Pourquoi c'est indispensable.* Si la formulation contient une erreur, le solveur renverra
une solution parfaitement « optimale » — pour un mauvais problème. Rejouer les contraintes
du modèle ne détecterait rien du tout. C'est le principe de la **double vérification**, et
il a payé : c'est le validateur qui a détecté un bug réel d'agrégation des livraisons
depuis IR11 lors du premier passage.

---

## 3. Les points délicats du code

### 3.1 La substitution qui simplifie tout

L'acide décadmié concentré est **obligatoirement** clarifié (aucun stockage local pour le
54 NCL DEC). Plutôt que créer une variable `u_dec` et une contrainte d'égalité, on
**substitue** directement :

```python
def _clarification_dec(v, ligne54):
    return v.x_dec.get(C.SIGMA_INV[ligne54], pulp.LpAffineExpression())
```

Cela supprime 5 variables et 5 contraintes, et rend **automatique** le couplage entre
décadmiation et capacité des décanteurs. Règle générale de modélisation : *une contrainte
d'égalité qui définit une variable doit être éliminée par substitution.*

### 3.2 Les variables non créées

Une livraison interdite par la matrice d'interconnexion n'est pas créée puis contrainte à
zéro : elle **n'est pas créée du tout**.

```python
for ligne in sources_autorisees(scenario, consommateur, acide):
    v.y_loc[(acide, ligne, consommateur)] = _positive(...)
```

Sur les transferts interzones, cela fait 14 variables au lieu de 30.

### 3.3 Le piège de portée Python

Dans `ecarts_aux_cibles`, une fonction imbriquée doit ajouter des contraintes. Écrire
`prob += ...` à l'intérieur rebinderait `prob` en variable **locale** de la fonction
imbriquée, provoquant un `UnboundLocalError`. D'où l'usage de `prob.addConstraint(...)`.

### 3.4 Les tolérances de la résolution lexicographique

Figer un niveau à l'exact (`f1 == f1*`) rend la passe suivante **infaisable** : le solveur
ne retrouve pas au bit près la valeur qu'il vient d'annoncer. On fige donc avec une
tolérance relative de 1e-6, négligeable devant des grandeurs en milliers de tonnes.

### 3.5 Le coefficient 0,33

Le dossier publie `get_vol_29 = 174,11 × h × 0,33`, alors que la physique déclarée donne
`0,26 × 1,270 = 0,3302`. Écart de 0,06 %. Le code retient le **coefficient publié** (c'est
la formule réellement utilisée sur le site) et un test vérifie en permanence qu'il reste
cohérent avec la physique.

---

## 4. La stratégie de test

**138 tests, 1,2 s.** Six fichiers, chacun avec un rôle distinct.

| Fichier | Ce qu'il garantit |
|---|---|
| `test_constants.py` | cohérence structurelle : σ bijective, échelons partitionnés, rendements complémentaires |
| `test_units.py` | conversions et bornes, y compris le **verrouillage des anomalies** A-02 et A-06 |
| `test_scenario_et_profils.py` | un scénario incohérent est bien **rejeté**, avec le bon message |
| `test_preprocessing.py` | les valeurs recalculées, y compris celles qui contredisent le dossier |
| `test_model.py` | structure du MILP, comportement des contraintes, non-régression |
| `test_validation.py` | le validateur **détecte** les solutions corrompues |
| `test_reporting_et_analyse.py` | rapports, goulots, sensibilité, ligne de commande |

### Trois familles de tests qui méritent d'être signalées

**Les tests qui verrouillent une anomalie.** Exemple :

```python
def test_bornes_29_different_du_dossier_anomalie_a02():
    z_min, z_max = units.bornes_stock_29()
    assert z_max == pytest.approx(965.3, abs=0.5)
    assert 1530.7 / z_max == pytest.approx(1.586, abs=0.01)
```

Si l'encadrant fournit un jour d'autres valeurs, ce test échouera et signalera qu'il faut
réexaminer la décision D-07. Un constat documenté mais non testé finit toujours par être
oublié.

**Les tests de contre-épreuve.** Ils démontrent qu'une contrainte **sert à quelque chose** :

```python
def test_sans_contrainte_de_qualite_aucun_dec_cl(scenario, profils):
    """Avec alpha = 0, l'optimiseur cesse complètement de produire du DEC_CL."""
    sans_alpha = dataclasses.replace(scenario, alpha_dec_cl=0.0)
    ...
    assert dec_cl == pytest.approx(0.0, abs=1e-4)
```

Ce test **prouve** la nécessité de la contrainte C15 (décision D-09) : sans elle, la règle
métier serait effectivement violée.

**Les tests qui corrompent la solution.** Un validateur qui répondrait toujours
« conforme » passerait tous les tests positifs sans rien garantir. On lui soumet donc des
solutions délibérément fausses et on vérifie qu'il les rejette — treize corruptions
différentes sont testées.

---

## 5. Ce que produit le programme

### 5.1 Sortie console
Contexte, statistiques du modèle, valeurs des trois niveaux, décisions d'exploitation,
stocks finaux, rapport de validation, goulots d'étranglement classés.

### 5.2 Rapport Excel — 5 feuilles
Conforme à `OUTPUT_FORMAT.md` : Demand Delivery, Phosphoric Production, Acid 29 Stocks,
Acid 54 Stocks, Central Storage Stocks. Les cellules en dépassement sont surlignées.

### 5.3 Export JSON
Même contenu, lisible par machine — indispensable pour les analyses de sensibilité et les
tests de non-régression.

---

## 6. Comment ajouter quelque chose

| Je veux… | Je modifie… |
|---|---|
| tester un autre scénario | un nouveau JSON dans `data/scenarios/`, puis `--scenario` |
| ajouter un engrais | `data/quality_profiles.json` |
| ajouter une contrainte | une fonction `cXX_...` dans `model/constraints.py`, appelée dans `ajouter_toutes_les_contraintes` |
| changer les priorités | `PoidsObjectif` dans `model/objective.py` |
| ajouter un contrôle | une fonction `_valider_...` dans `validation.py` |
| ajouter une analyse | `analysis.py` |

**Règle absolue :** toute contrainte ajoutée au code doit d'abord être écrite dans
`docs-helper/05_MODELE_MATHEMATIQUE.md`, avec son numéro, sa traduction en français et sa
justification. Le code suit le modèle mathématique, jamais l'inverse.
