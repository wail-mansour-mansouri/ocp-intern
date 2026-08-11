# 04 — DONNÉES, UNITÉS ET CONVENTIONS

> Toutes les données chiffrées du projet, rassemblées, **recalculées et vérifiées**.
> Ce document est la source de vérité numérique. Il sera transcrit tel quel en code
> (module `constants.py`) en Phase 3.
>
> ⚠️ **Chaque valeur signalée « recalculée » diffère de celle du dossier original.**
> Les écarts sont documentés en `06_ANOMALIES_ET_DECISIONS.md`.

---

## 1. Conventions générales

| Convention | Valeur |
|---|---|
| **Unité de masse** | tonne de **P₂O₅** |
| **Unité de temps** | jour |
| **Horizon** | 1 journée (modèle mono-période) |
| **Unité de hauteur de cuve** | mètre |
| **Convention de signe** | toutes les variables de flux sont **positives** ; le sens est porté par la structure des équations |
| **Tolérance bilan matière** | 0,1 % |
| **Tolérance satisfaction demande** | 0,01 t |
| **Tolérance capacité** | 0 (stricte) |

---

## 2. ⭐ L'unité du modèle : la tonne de P₂O₅

**C'est le point le plus important de tout le projet.** Il n'est écrit nulle part dans le
dossier ; il a fallu le déduire. S'y tromper invalide l'intégralité des bilans matière.

### 2.1 L'énigme de départ

Le dossier affirme : *« P29 to P54 concentration : 100 % (1:1 mass ratio) »*.
Autrement dit, 1 tonne d'acide à 29 % donnerait 1 tonne d'acide à 54 %.

**C'est physiquement impossible en masse d'acide.** Concentrer, c'est retirer de l'eau :
la masse ne peut que diminuer, à peu près de moitié.

### 2.2 La résolution

Les quantités ne sont pas des masses d'acide, ce sont des **masses de P₂O₅ contenu**.

**Preuve n° 1 — par les formules de conversion.** Le dossier fournit :
```
get_vol_29(h) = 174,11 × h × 0,33
get_vol_54(h) =  95    × h × 0,83
```
Or il fournit aussi, séparément, les paramètres physiques des cuves :
```
Acide 29 : section 174,11 m² · densité 1,270 t/m³ · titre P₂O₅ 0,26
Acide 54 : section  95    m² · densité 1,660 t/m³ · titre P₂O₅ 0,50
```
Vérifions les coefficients :
$$0{,}26 \times 1{,}270 = 0{,}3302 \approx 0{,}33 \qquad\checkmark$$
$$0{,}50 \times 1{,}660 = 0{,}8300 = 0{,}83 \qquad\checkmark \text{ (exact)}$$

La structure est donc :
$$\text{get\_vol}(h) \;=\; \underbrace{S \times h}_{\text{volume (m³)}} \times \underbrace{\rho}_{\text{densité}} \times \underbrace{\theta}_{\text{titre P₂O₅}}$$

Le facteur $\theta$ est **le titre en P₂O₅**. La fonction ne rend donc pas des tonnes
d'acide : elle rend des **tonnes de P₂O₅**. ∎

**Preuve n° 2 — par la conservation.** Prenons 1 000 t de solution à 26 % :
- P₂O₅ contenu : 260 t
- après concentration à 50 % : ces 260 t sont diluées dans 520 t de solution
- masse d'acide : 1 000 → 520 t (**non conservée**)
- masse de P₂O₅ : 260 → 260 t (**conservée**)

Le rendement vaut 1 **si et seulement si** on compte en P₂O₅. ∎

**Preuve n° 3 — par l'industrie.** EMAPHOS est officiellement dimensionné à
280 000 t **P₂O₅**/an, soit ≈ 770 t P₂O₅/jour. Sa demande dans le scénario est de 700 t/j :
cohérent au pourcentage près avec une unité en P₂O₅.
Toute l'industrie du phosphate compte d'ailleurs en t P₂O₅. ∎

### 2.3 Conséquences pour la lecture

| Quantité du dossier | Interprétation correcte | Équivalent en acide marchand |
|---|---|---|
| Production 13AB = 1 500 t/j | 1 500 t **de P₂O₅** | ≈ 5 770 t/j de solution à 26 % |
| Demande EMAPHOS = 700 t | 700 t **de P₂O₅** | ≈ 1 400 t de solution à 50 % |
| Capacité IR11 = 6 372 t | 6 372 t **de P₂O₅** | ≈ 12 700 t de solution |

### 2.4 Interprétation des rendements

| Procédé | Rendement | Signification en P₂O₅ |
|---|---|---|
| Concentration | 1,00 | tout le P₂O₅ passe (seule l'eau part) |
| Clarification | 0,90 | 90 % du P₂O₅ dans l'acide clair, 10 % piégé dans la boue |
| Cocristallisation | 0,80 | 80 % du P₂O₅ cristallisé, 20 % dans les eaux mères |

**Ces rendements sont des taux de récupération du P₂O₅.** Rien n'est détruit : le
complément est recyclé en amont. C'est physiquement cohérent, et cela **ferme** le bilan
matière global.

---

## 3. Conversion hauteur → tonnes

### 3.1 Les quatre fonctions

```python
get_vol_29(h)      = 174.11 * h * 0.33                # cuves acide 29
get_vol_54(h)      =  95    * h * 0.83                # cuves acide 54 locales
get_vol_54_IR11(h) = (h - 0.25) * 706.45 * 0.855      # bac central IR11
get_vol_54_IR12(h) = (h - 2.70) * 706.45 * 0.84       # bac central IR12
```

### 3.2 Pourquoi les bacs centraux ont un décalage

Les formules IR11 et IR12 comportent une soustraction (`- 0,25` et `- 2,70`). C'est un
**volume mort** : la partie basse du bac, occupée par le piquage d'aspiration, les boues
sédimentées ou le fond bombé, n'est pas exploitable. Le zéro utile est décalé.

- IR11 : 0,25 m de volume mort
- IR12 : 2,70 m de volume mort (nettement plus — bac plus ancien ou plus encrassé)

### 3.3 ⚠️ Les hauteurs fournies sont **cumulées sur 2 cuves**

Le scénario donne pour `13AB` une hauteur de **13,75 m**, alors que la hauteur maximale
d'une cuve est de **8,40 m**. Contradiction apparente.

**Résolution :** la hauteur fournie est la **somme des hauteurs des 2 cuves** de la ligne.
C'est valide car $\text{get\_vol}$ est **linéaire** :
$$\text{get\_vol}(h_1 + h_2) = \text{get\_vol}(h_1) + \text{get\_vol}(h_2)$$
Sommer puis convertir donne donc exactement le même résultat que convertir puis sommer.

*Vérification :* $13{,}75 \le 2 \times 8{,}40 = 16{,}80$ ✓ — et cette lecture reproduit au
dixième près tous les stocks initiaux annoncés. Voir décision **D-08**.

---

## 4. Structure du système

### 4.1 Lignes et correspondance

```python
LIGNES_29 = ['13AB', '13CD', '13XY', '13ZU', '13E', '13F']
LIGNES_54 = ['14AB', '14CD', '14XY', '14ZU', '14EXT']

SIGMA = {'13AB':'14AB', '13CD':'14CD', '13XY':'14XY',
         '13ZU':'14ZU', '13E':'14EXT', '13F': None}
```

### 4.2 Échelons : capacités (t P₂O₅/jour à 24 h)

```python
CAPACITE_ECHELON = {
    # 14CD
    'C': 250, 'D': 250, 'M': 290, 'N': 250,
    # 14XY
    'X': 300, 'Y': 250, 'P': 250, 'Q': 250,
    # 14ZU
    'Z': 250, 'U': 300, 'R': 250, 'S': 300, 'V': 590, 'W': 590,
    # 14EXT  (cocristallisation possible)
    'E': 420, 'F': 420, 'G': 420, 'H': 420,
    # 14AB   (cocristallisation possible)
    'A': 300, 'B': 300, 'K': 300, 'L': 300, 'I': 590, 'J': 590,
}

GROUPES_ECHELONS = {
    '14EXT': ['E','F','G','H'],
    '14AB' : ['A','B','I','J','K','L'],
    '14CD' : ['C','D','M','N'],
    '14XY' : ['X','Y','P','Q'],
    '14ZU' : ['Z','U','R','S','V','W'],
}
```

> **Note d'unité.** Annotées « tonnes/heure » dans le dossier, mais la formule
> $C \times h/24$ impose des **tonnes/jour**. Voir anomalie **A-08**.

### 4.3 Matrice interzone (acide 29 standard uniquement)

```python
INTERZONE = {           # 'x' = transfert autorisé
    'E' : {'AB':'x', 'CD':'x'},
    'F' : {'E':'x', 'AB':'x', 'XY':'x', 'ZU':'x'},
    'AB': {'E':'x', 'CD':'x'},
    'CD': {'E':'x', 'AB':'x', 'XY':'x'},
    'XY': {'CD':'x', 'ZU':'x'},
    'ZU': {'XY':'x'},
}
TAU_MIN = 100.0   # tonnes — quantité minimale d'un transfert
TAU_MAX = 1000.0  # tonnes — VALEUR D'ATTENTE, absente du dossier (question Q1)
```

**14 liaisons autorisées** sur 30 couples possibles, soit 47 % de connectivité.

### 4.4 Matrice d'interconnexion consommateurs

```python
CONNEXIONS = {
    'U16'    : {'29': ['13AB','13CD','13XY','13ZU'], '54': ['14XY','14CD','14AB','14EXT']},
    'U116A'  : {'29': ['13CD','13F'],                '54': ['14AB','14CD','14EXT']},
    'U116BC' : {'29': ['13F','13AB','13XY'],         '54': ['14XY','14CD']},
    'IMACID' : {'29': ['13E'],                       '54': []},
    'EMAPHOS': {'29': [],                            '54': ['14ZU','14XY','14AB']},
    'MAPS'   : {'29': ['13E'],                       '54': []},
    'U53'    : {'29': [],                            '54': []},   # IR12 seulement
    '107DEF' : {'29': ['13E','13F'],                 '54': []},   # + IR11 / IR12
    'JFC1-5' : {'29': ['13F'],                       '54': []},
}
```

> **Rappel :** cette matrice ne s'applique **qu'aux** acides livrés depuis un stock local
> (29 std, 29 dec, 54 NCL). Les acides CL, CoC et DEC_CL viennent d'IR11/IR12 et sont
> accessibles à **tous** les consommateurs sans restriction.

### 4.5 Types d'acide acceptés par consommateur

```python
ACIDES_ACCEPTES = {
    'EMAPHOS': ['acid_54_ncl'],
    'U53'    : ['acid_54_cl'],
    'IMACID' : ['acid_29_std'],
    'MAPS'   : ['acid_29_std'],
    'JFC1-5' : ['acid_29_std'],
    '107DEF' : ['acid_29_std', 'acid_54_cl', 'acid_54_coc'],
    # U16, U116A, U116BC : selon les profils qualité de leurs produits
}
```

---

## 5. Paramètres de procédé

```python
# Rendements (fixes, non optimisables)
RENDEMENT_CONCENTRATION   = 1.00   # P₂O₅ conservé
RENDEMENT_CLARIFICATION   = 0.90   # + 0.10 de boue
RENDEMENT_COCRISTALLISATION = 0.80 # + 0.20 de boue
BOUE_CLARIFICATION        = 0.10
BOUE_COCRISTALLISATION    = 0.20

# Décadmiation
NIVEAUX_DECADMIATION = [0, 750, 1500]   # 0, 1 ou 2 filtres

# Clarification
CAPACITE_DECANTEUR   = 500     # t/j par décanteur
DECANTEURS_PAR_LIGNE = 2
LAMBDA_CLARIFICATION = 1000    # t/j ENTRANTES par ligne (NCL + DEC confondus)

# Retours EMAPHOS (en part de la livraison)
EMAPHOS_ARP1  = 0.125   # → stock 29 std de 13AB
EMAPHOS_ARP2  = 0.125   # → stock 29 std de 13CD
EMAPHOS_BOUE  = 0.150   # → stock 29 std de 13XY
# Total retourné : 0.400
```

---

## 6. Bornes de stockage — ⚠️ recalculées

### 6.1 Méthode

$$Z^{\min} = \text{get\_vol}(n_{\text{cuves}} \times h_{\min}),
\qquad Z^{\max} = \text{get\_vol}(n_{\text{cuves}} \times h_{\max})$$

**Validation de la méthode :** appliquée à l'acide 54, elle donne 473,1 et 1 482,4, à
comparer aux 473,4 et 1 483,6 du dossier — **concordance au dixième près**. La méthode est
donc correcte.

### 6.2 Résultats

| Grandeur | Formule | **Valeur retenue** | Valeur du dossier | Écart |
|---|---|---:|---:|---|
| `Z_MIN_29` | get_vol_29(2 × 2,00) | **229,8** | 364,5 | **+59 %** ❌ |
| `Z_MAX_29` | get_vol_29(2 × 8,40) | **965,3** | 1 530,7 | **+59 %** ❌ |
| `Z_MIN_54` | get_vol_54(2 × 3,00) | **473,1** | 473,4 | ✓ |
| `Z_MAX_54` | get_vol_54(2 × 9,40) | **1 482,4** | 1 483,6 | ✓ |
| `Z_MIN_IR11` | get_vol_IR11(0,40) | **90,6** | 90,8 | ✓ |
| `Z_MAX_IR11` | get_vol_IR11(10,80) | **6 372,4** | 6 378,4 | ✓ |
| `Z_MIN_IR12` | get_vol_IR12(2,00) | **0** (borné) | 0 | ✓ ⚠️ |
| `Z_MAX_IR12` | get_vol_IR12(10,80) | **4 806,7** | 4 804,3 | ✓ |

**Les bornes de l'acide 29 du dossier sont surestimées d'un facteur exactement 1,586**
pour le minimum comme pour le maximum — signature typique d'une erreur de saisie unique.
Décision **D-07** : on retient les valeurs recalculées.

⚠️ **Sur `Z_MIN_IR12` :** la hauteur minimale annoncée (2,00 m) est **inférieure** au volume
mort de la formule (2,70 m). Le calcul brut donne −415 t, ce qui n'a pas de sens. On borne à
0. Le paramètre `H_MIN_54_IR12 = 2,00` est donc incohérent avec `get_vol_54_IR12`.
Voir anomalie **A-06**.

### 6.3 Paramètres physiques des cuves

```python
# Acide 29 %
SECTION_29 = 174.11   # m²
DENSITE_29 = 1.270    # t/m³
TITRE_29   = 0.26
H_MIN_29, H_MAX_29 = 2.00, 8.40   # m par cuve
N_CUVES_29 = 2

# Acide 54 %
SECTION_54 = 95       # m²
DENSITE_54 = 1.660    # t/m³
TITRE_54   = 0.50
H_MIN_54, H_MAX_54 = 3.00, 9.40   # m par cuve
N_CUVES_54 = 2

# Bacs centraux
H_MIN_IR11, H_MAX_IR11 =  0.40, 10.80
H_MIN_IR12, H_MAX_IR12 =  2.00, 10.80   # ⚠️ h_min < volume mort (2,70)
```

---

## 7. Le scénario de référence

### 7.1 Production d'acide 29 (t P₂O₅/j)

| Ligne | 13AB | 13CD | 13XY | 13ZU | 13E | 13F | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Production | 1 500 | 1 500 | 1 500 | **800** | 1 500 | 1 500 | **8 300** |

### 7.2 Stocks initiaux — hauteurs et conversions

| Ligne | h std (m) | **Stock std (t)** | h dec (m) | **Stock dec (t)** |
|---|---:|---:|---:|---:|
| 13AB | 13,75 | 790,0 | 0,00 | 0,0 |
| 13CD | 6,75 | 387,8 | 6,00 | 344,7 |
| 13XY | 5,05 | 290,2 | 7,95 | 456,8 |
| 13ZU | 14,20 | 815,9 | 0,00 | 0,0 |
| 13E | 7,70 | 442,4 | 0,00 | 0,0 |
| 13F | 14,40 | 827,4 | 0,00 | 0,0 |
| **Total** | | **3 553,7** | | **801,5** |

| Ligne P54 | h (m) | **Stock NCL (t)** |
|---|---:|---:|
| 14AB | 11,43 | 901,3 |
| 14CD | 4,68 | 369,0 |
| 14XY | 3,78 | 298,1 |
| 14ZU | 11,65 | 918,6 |
| 14EXT | 2,80 | 220,8 |
| **Total** | | **2 707,7** |

| Bac | h (m) | **Stock (t)** | Capacité | Remplissage |
|---|---:|---:|---:|---:|
| IR11 | 9,38 | **5 514,7** ⚠️ | 6 372,4 | **86,5 %** |
| IR12 | 9,14 | **3 821,6** ⚠️ | 4 806,7 | **79,5 %** |

⚠️ Le dossier annonce IR11 = 5 500,8 (écart mineur, arrondi de hauteur) et
**IR12 = 4 004,1** — mais l'application de sa propre formule à h = 9,14 donne **3 821,6**.
Écart de 4,8 %, non explicable par un arrondi. Voir anomalie **A-03**.

### 7.3 Heures de marche des échelons

| Ligne | Heures par échelon |
|---|---|
| 14EXT | E 24 · F 24 · G 24 · **H 14** |
| 14AB | A 24 · B 24 · I 24 · **J 14** · K 24 · L 24 |
| 14CD | C 24 · D 24 · M 24 · N 24 |
| 14XY | **X 14** · Y 24 · **P 14** · Q 24 |
| 14ZU | **Z 14** · U 24 · **R 14** · S 24 · V 24 · **W 0** |

### 7.4 Production d'acide 54 recalculée

| Ligne | Détail par échelon | **Total** | CoC | NCL libre |
|---|---|---:|---:|---:|
| 14EXT | 420+420+420+245 | **1 505,0** | 1 505,0 | 0,0 |
| 14AB | 300+300+590+344+300+300 | **2 134,2** | 1 534,2 | 600,0 |
| 14CD | 250+250+290+250 | **1 040,0** | 0,0 | 1 040,0 |
| 14XY | 175+250+146+250 | **820,8** | 0,0 | 820,8 |
| 14ZU | 146+300+146+300+590+0 | **1 481,7** | 0,0 | 1 481,7 |
| | | **6 981,7** | **3 039,2** | **3 942,5** |

⚠️ Le dossier annonce **6 636 t**. Écart de 345,7 t (5,2 %). Voir anomalie **A-01**.

**Production de CoC :** $0{,}80 \times 3\,039{,}2 = \mathbf{2\,431{,}4}$ t/jour
**Boue de cocristallisation :** $0{,}20 \times 3\,039{,}2 = 607{,}8$ t
(dont 301,0 t vers le stock de 13E et 306,8 t vers celui de 13AB)

### 7.5 Configuration des capacités par ligne

```python
DEC_29_ACTIVE   = ['13CD', '13XY']          # peuvent produire de l'acide 29 dec
CLARIF_ACTIVE   = ['14AB','14CD','14XY','14ZU']   # peuvent clarifier (pas 14EXT)
DEC_CL_ACTIVE   = ['14XY']                  # peuvent produire du DEC_CL
COC_ECHELONS    = {'14EXT': ['E','F','G','H'],
                   '14AB' : ['I','J','A','K']}
DECAD_ACTIVE    = ['13AB','13CD','13XY','13ZU','13F']   # équipées de filtres
```

> **Attention à une subtilité.** `DEC_29_ACTIVE` (lignes 29 pouvant décadmier pour les
> engrais) et `DECAD_ACTIVE` (lignes équipées de filtres) sont donnés séparément et se
> contredisent partiellement dans le dossier. Voir anomalie **A-09**.

### 7.6 Demande directe des industriels (t P₂O₅)

| Consommateur | Type | Quantité |
|---|---|---:|
| IMACID | acid_29_std | 700 |
| EMAPHOS | acid_54_ncl | 700 |
| U53 | acid_54_cl | 1 500 |
| MAPS, 107DEF, JFC1-5 | — | 0 |
| **Total** | | **2 900** |

### 7.7 Demande engrais et conversion par profils qualité

| Atelier | Produit | Tonnage | Type d'acide | Coefficient | **Besoin (t)** |
|---|---|---:|---|---:|---:|
| U16 | DAP_STANDARD | 3 057 | acid_29_std | 0,127 | 388,24 |
| U16 | DAP_STANDARD | 3 057 | acid_54_ncl | 0,354 | 1 082,18 |
| U16 | TSP_EURO | 1 200 | acid_54_dec_total | 0,379 | 454,80 |
| U116A | MAP_11_52_EU | 3 037 | acid_29_dec | 0,030 | 91,11 |
| U116A | MAP_11_52_EU | 3 037 | acid_54_dec_total | 0,129 | 391,77 |
| U116BC | NPK_12_24_12_EU | 1 540 | acid_54_dec_total | 0,091 | 140,14 |
| U116BC | NPK_15_15_15_… | 2 126 | acid_29_dec | 0,171 | 363,55 |

### 7.8 ⭐ Demande totale consolidée

| Type d'acide | Engrais | Direct | **TOTAL** |
|---|---:|---:|---:|
| `acid_29_std` | 388,24 | 700,00 | **1 088,24** |
| `acid_29_dec` | 454,66 | 0 | **454,66** |
| `acid_54_ncl` | 1 082,18 | 700,00 | **1 782,18** |
| `acid_54_cl` | 0 | 1 500,00 | **1 500,00** |
| `acid_54_dec_total` | 986,71 | 0 | **986,71** |
| | | | **5 811,79** |

✓ Concorde avec la valeur de 5 811 t annoncée par le dossier.

---

## 8. Analyse préliminaire de capacité

| Ressource | Disponible | Requis | Marge |
|---|---:|---:|---|
| Acide 29 (prod. + stock) | 12 655,2 | 8 524,7 ¹ | **confortable** |
| Acide 54 (production) | 6 981,7 | 4 269,0 ² | **confortable** |
| Clarification (4 lignes) | 4 000 entrant | 1 667 ³ | **confortable** |
| **Espace libre dans IR11** | **857,7** | **+1 444,7** ⁴ | 🔴 **SATURATION** |
| Espace libre dans IR12 | 985,1 | ≈ 0 ⁵ | confortable |

¹ concentration (6 981,7) + demande directe en acide 29 (1 543)
² besoins en produits de niveau 54 : NCL 1 782 + CL 1 500 + dec_total 987
³ pour produire 1 500 t de CL : $1\,500/0{,}9 = 1\,667$ t entrantes
⁴ **solde net** d'IR11 : entrées 2 431,3 (CoC systématique) − sorties 986,7 (`dec_total`)
⁵ solde net d'IR12 : entrées 1 500 (CL) − sorties 1 500 (U53) = 0

### Diagnostic

**🔴 IR11 est le goulot d'étranglement principal.** Le bac est rempli à 86,5 % et reçoit
2 431 t/jour de CoC systématique, pour seulement 987 t/jour de sortie. Le solde net est de
**+1 444 t**, alors qu'il ne reste que **858 t** d'espace disponible.

**Le bac déborde.** Le modèle sera donc infaisable si l'on impose simultanément
$S^{IR11} \le Z^{\max}_{IR11}$ en contrainte dure et la satisfaction totale de la demande.

### Trois lectures possibles

1. **La borne d'IR11 est trop basse** — les valeurs recalculées du §6 pourraient encore
   être fausses.
2. **Il existe un débouché non modélisé** pour l'excédent de CoC (export, vente d'acide
   marchand, autre bac) que le dossier ne mentionne pas.
3. **Le scénario de référence est effectivement tendu**, et c'est précisément l'intérêt du
   modèle que de le révéler à l'exploitant.

### Décision de modélisation

Les bornes hautes de stock seront traitées comme des **contraintes molles** : on autorise le
dépassement, mais on le **pénalise fortement au niveau 2 de l'objectif**.

**Justification.** Un modèle qui répond « Infeasible » est inutilisable en exploitation :
l'ingénieur veut savoir *de combien* il va déborder et *où*, pas qu'on lui refuse une
réponse. Un modèle à contraintes molles fournit toujours un plan, **et** quantifie
précisément le problème. C'est aussi ce que fait le dossier lui-même, qui prévoit un
mécanisme de « stock violation tracked but not blocking ».

> **C'est un excellent résultat pour ton rapport de stage :** une analyse de capacité menée
> *avant* toute optimisation a permis d'identifier un goulot d'étranglement structurel. C'est
> exactement la démarche attendue d'un ingénieur — comprendre le système avant de le
> résoudre.

---

## 9. Récapitulatif des constantes pour le code

```python
# ─── Conversions ─────────────────────────────────────────────
get_vol_29      = lambda h: 174.11 * h * 0.33
get_vol_54      = lambda h:  95.00 * h * 0.83
get_vol_54_IR11 = lambda h: (h - 0.25) * 706.45 * 0.855
get_vol_54_IR12 = lambda h: (h - 2.70) * 706.45 * 0.84

# ─── Bornes de stock (RECALCULÉES) ───────────────────────────
Z_MIN_29,   Z_MAX_29   =  229.8,  965.3
Z_MIN_54,   Z_MAX_54   =  473.1, 1482.4
Z_MIN_IR11, Z_MAX_IR11 =   90.6, 6372.4
Z_MIN_IR12, Z_MAX_IR12 =    0.0, 4806.7

# ─── Procédé ─────────────────────────────────────────────────
ETA_CL, ETA_COC        = 0.90, 0.80
BOUE_CL, BOUE_COC      = 0.10, 0.20
NIVEAUX_DECAD          = [0, 750, 1500]
LAMBDA_CLARIF          = 1000.0

# ─── Transferts ──────────────────────────────────────────────
TAU_MIN, TAU_MAX       = 100.0, 1000.0    # TAU_MAX : valeur d'attente (Q1)

# ─── EMAPHOS ─────────────────────────────────────────────────
EMAPHOS_RETOURS = {'13AB': 0.125, '13CD': 0.125, '13XY': 0.150}

# ─── Qualité IR11 ────────────────────────────────────────────
ALPHA_DEC_CL           = 0.15             # valeur d'attente (Q2)
```

> **Règle absolue pour la Phase 3 :** aucune de ces valeurs ne doit être écrite en dur dans
> le code métier. Toutes vivent dans `constants.py` ou dans le fichier de scénario, et
> chacune est couverte par un test unitaire qui vérifie qu'elle est reproduite par sa
> formule d'origine.
