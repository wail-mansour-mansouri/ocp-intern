# 06 — ANOMALIES DU DOSSIER ET ARBITRAGES

> Les documents remis par l'encadrant contiennent **11 anomalies** : erreurs de calcul,
> contradictions internes, données manquantes.
> Ce document les recense toutes, avec pour chacune : le constat, la preuve, l'arbitrage et
> sa justification.
>
> **Ce n'est pas une critique du dossier** — c'est le travail normal de dépouillement d'un
> cahier des charges. Un ingénieur qui reçoit des spécifications les vérifie avant de coder.
> Ce document a d'ailleurs sa place dans le rapport de stage : il démontre une lecture
> critique et rigoureuse.

---

## Tableau de synthèse

| N° | Anomalie | Gravité | Type | Arbitrage |
|---|---|:---:|---|---|
| A-01 | Production P54 mal calculée (6 636 au lieu de 6 981,7) | 🔴 | calcul | recalculer |
| A-02 | Bornes de stock P29 fausses (facteur 1,586) | 🔴 | calcul | recalculer |
| A-03 | Stock initial IR12 incohérent avec sa formule | 🟠 | calcul | recalculer |
| A-04 | Limite décanteur : entrée ou sortie ? | 🟠 | contradiction | entrée (D-06) |
| A-05 | Destination des boues de cocristallisation | 🟠 | contradiction | stock P29 (D-05) |
| A-06 | `H_MIN_IR12` sous le volume mort de sa formule | 🟡 | incohérence | borner à 0 |
| A-07 | Capacité cuve P29 : 965 t ou 2 600 t ? | 🟠 | contradiction | géométrie (D-07) |
| A-08 | Capacités d'échelon : t/h ou t/j ? | 🟡 | unité | t/jour |
| A-09 | Deux listes contradictoires de lignes décadmiantes | 🟡 | contradiction | intersection |
| A-10 | Fichier `quality_profiles_v2.json` absent | 🟠 | donnée manquante | reconstruire |
| A-11 | Format Excel : 5 ou 7 feuilles ? | 🟢 | contradiction | 5 feuilles |
| — | `MAX_TRANSFER` jamais défini | 🔴 | donnée manquante | Q1 |
| — | Seuil de DEC_CL obligatoire jamais chiffré | 🔴 | donnée manquante | Q2 |

**Légende :** 🔴 critique · 🟠 important · 🟡 mineur · 🟢 cosmétique

---

## A-01 — Production d'acide 54 mal calculée 🔴

**Constat.** `COMPREHENSIVE_SYSTEM_SIMULATION.md` annonce une production totale de
**6 636 t/jour** pour le scénario de référence. Le recalcul donne **6 981,7 t/jour**.

**Preuve.** Reprenons ligne par ligne la formule du document lui-même,
$\Pi_m = \sum_e C_e h_e / 24$ :

| Ligne | Calcul détaillé | **Correct** | Document | Écart |
|---|---|---:|---:|---:|
| 14EXT | (420·24 + 420·24 + 420·24 + 420·14)/24 | **1 505,0** | 1 365 | −140,0 |
| 14AB | (300·24 + 300·24 + 590·24 + 590·14 + 300·24 + 300·24)/24 | **2 134,2** | 2 077 | −57,2 |
| 14CD | (250·24 + 250·24 + 290·24 + 250·24)/24 | **1 040,0** | 1 040 | ✓ 0 |
| 14XY | (300·14 + 250·24 + 250·14 + 250·24)/24 | **820,8** | 779 | −41,8 |
| 14ZU | (250·14 + 300·24 + 250·14 + 300·24 + 590·24 + 590·0)/24 | **1 481,7** | 1 375 | −106,7 |
| | | **6 981,7** | 6 636 | **−345,7** |

Détaillons 14EXT : $(10\,080 + 10\,080 + 10\,080 + 5\,880)/24 = 36\,120/24 = 1\,505$.
Le document annonce 1 365 : il manque 140, exactement $420 \times 8/24$.

**Élément remarquable :** 14CD est la **seule** ligne juste — et c'est aussi la seule dont
tous les échelons marchent 24 h. Toutes les erreurs concernent des lignes ayant au moins un
échelon à horaire réduit. **Le document a mal appliqué le prorata horaire.**

**Arbitrage.** Recalculer systématiquement. Ne recopier aucun chiffre du document.

**Impact.** Majeur : 5,2 % d'écart sur le flux principal du système. Toutes les analyses de
capacité en dépendent.

---

## A-02 — Bornes de stock de l'acide 29 surestimées de 59 % 🔴

**Constat.** `CORE_FIXED_ELEMENTS.md` annonce `Z_MIN_29 ≈ 364,5` et `Z_MAX_29 ≈ 1 530,7`.
Le recalcul de **sa propre formule** donne 229,8 et 965,3.

**Preuve.** Le document donne la formule :
```python
Z_MAX_29 = 2 * SECTION_29 * H_MAX_29 * P2O5_29 * DENSITY_29
```
Application numérique :
$$2 \times 174{,}11 \times 8{,}40 \times 0{,}26 \times 1{,}270 = 965{,}85$$

**Validation croisée décisive.** La même formule appliquée à l'acide 54 :
$$2 \times 95 \times 9{,}40 \times 0{,}50 \times 1{,}66 = 1\,482{,}4$$
à comparer aux **1 483,6** annoncés par le document. **Concordance au dixième près.**

*Conclusion :* la méthode est correcte, l'erreur est **localisée** sur l'acide 29.

**Signature de l'erreur.** Les deux valeurs erronées présentent le **même** facteur :
$$\frac{364{,}5}{229{,}8} = 1{,}5860 \qquad \frac{1\,530{,}7}{965{,}3} = 1{,}5858$$
Un facteur constant sur les deux bornes indique une erreur de saisie unique (un coefficient
mal recopié), et non deux erreurs indépendantes.

**Arbitrage.** Valeurs recalculées : $Z^{\min}_{29} = 229{,}8$, $Z^{\max}_{29} = 965{,}3$
(décision **D-07**).

**Justification supplémentaire — la cohérence dimensionnelle.** Les stocks **initiaux** sont
produits par `get_vol_29`. Comparer un stock calculé avec `get_vol_29` à une borne obtenue
par une autre formule serait dimensionnellement incohérent. Les deux **doivent** venir de
la même fonction.

**Impact.** Majeur. Avec la borne correcte (965 au lieu de 1 531), plusieurs lignes
dépassent leur capacité et les transferts interzones deviennent **indispensables** — ce qui
donne rétrospectivement tout son sens à l'existence de la matrice interzone dans le dossier.

---

## A-03 — Stock initial d'IR12 incohérent avec sa propre formule 🟠

**Constat.** Le document annonce `IR12 = 4 004,1 t` pour une hauteur de 9,14 m.

**Preuve.** Application de la formule fournie :
$$\text{get\_vol\_54\_IR12}(9{,}14) = (9{,}14 - 2{,}70) \times 706{,}45 \times 0{,}84$$
$$= 6{,}44 \times 706{,}45 \times 0{,}84 = 3\,821{,}6$$

Écart : 182,5 t, soit 4,8 % — trop important pour un arrondi.

*Vérification à rebours :* pour obtenir 4 004,1, il faudrait $h = 9{,}446$ m.

**Note.** Le même contrôle sur IR11 donne 5 514,7 contre 5 500,8 annoncés — écart de 0,25 %,
compatible avec un arrondi de hauteur. **Seul IR12 pose vraiment problème.**

**Arbitrage.** Retenir 3 821,6 t, valeur cohérente avec la formule et la hauteur fournies.

**Impact.** Modéré. IR12 n'est pas un goulot d'étranglement (son solde net est nul dans le
scénario).

---

## A-04 — Limite des décanteurs : entrée ou sortie ? 🟠

**Constat.** Contradiction interne à `PROCESS_GUIDE.md`.

| Emplacement | Formulation | Interprétation |
|---|---|---|
| §3.1 | « Total Clarification Limit: 1000 t/day per line (**before yield**) » | **entrée** |
| §3.4 | « Send 1000/0.9 = 1111 t to clarification → ~1000 t DEC CL » | **sortie** |
| Règles de validation | « `manual_clarification[line] ≤ 1000` » | **entrée** |

**Arbitrage.** La limite porte sur l'**entrée** (décision **D-06**).

**Justification.**
1. *Physique.* Un décanteur est dimensionné par le débit qu'il **reçoit** — c'est un temps de
   séjour dans une cuve, pas un rendement de sortie.
2. *Textuelle.* La mention « **before yield** » est explicite et sans ambiguïté.
3. *Majorité.* Deux sources sur trois disent « entrée ».

**Impact.** La capacité maximale de production de CL par ligne passe de 1 000 à 900 t/j.

---

## A-05 — Destination des boues de cocristallisation 🟠

**Constat.** Six sources, deux réponses opposées.

| Source | Destination |
|---|---|
| `PROCESS_GUIDE.md` §3.2 | stock **P29** standard |
| `REAL_SCENARIO_REFERENCE.md` | stock **P29** standard |
| `COMPREHENSIVE_SYSTEM_SIMULATION.md` | stock **P29** standard |
| `CORE_FIXED_ELEMENTS.md` | stock **P54** NCL |
| `OUTPUT_FORMAT.md` | stock **P54** NCL |
| `archive/TEST_REFERENCE_OUTPUT.md` | stock **P54** NCL |

**Arbitrage.** Stock **P29 standard**, avec le point de retour rendu **paramétrable** dans
le code (décision **D-05**).

**Justification.**
1. `PROCESS_GUIDE.md` se déclare lui-même « référence définitive du procédé industriel » et
   précise que toute question sur le fonctionnement du procédé doit être tranchée par lui.
2. `REAL_SCENARIO_REFERENCE.md` décrit le scénario que nous devons reproduire.
3. La simulation détaillée applique effectivement ce choix (« Sludge: 273 t → returns to
   13E P29 standard stock »).
4. Deux des trois sources contraires sont marquées comme archivées.

**Justification supplémentaire — la vraisemblance industrielle.** Les eaux mères de
cristallisation sont chargées d'impuretés. Les renvoyer au niveau 54 réintroduirait ces
impuretés dans un acide déjà concentré. Les diluer dans la masse de l'acide 29, en amont de
toute la chaîne de purification, est plus sain. **Le choix physiquement le plus plausible
coïncide avec le choix documentairement le mieux appuyé.**

**Impact.** Modéré, mais parfaitement circonscrit : un seul terme change de nœud.
Le paramétrage rend la bascule instantanée. → Question **Q5**.

---

## A-06 — Hauteur minimale d'IR12 sous le volume mort 🟡

**Constat.** `H_MIN_54_IR12 = 2,00 m`, alors que `get_vol_54_IR12` soustrait 2,70 m.

$$\text{get\_vol\_54\_IR12}(2{,}00) = (2{,}00 - 2{,}70) \times 706{,}45 \times 0{,}84 = -415{,}4$$

Un stock négatif n'a pas de sens.

**Interprétation.** Les 2,70 m sont un volume mort : sous cette hauteur, le bac contient
encore de la matière, mais elle n'est pas soutirable. La hauteur minimale d'exploitation
(2,00 m) est donc **en dessous du zéro utile** — les deux paramètres proviennent
vraisemblablement de sources différentes.

**Arbitrage.** $Z^{\min}_{IR12} = \max(0, \text{get\_vol\_54\_IR12}(2{,}00)) = 0$.
Le document applique d'ailleurs lui-même ce `max(0, ...)`.

**Impact.** Négligeable — IR12 est largement rempli dans tous les scénarios envisagés.

---

## A-07 — Capacité des cuves d'acide 29 : 965 t ou 2 600 t ? 🟠

**Constat.** Trois valeurs pour une même grandeur :

| Source | Valeur |
|---|---|
| Formule géométrique recalculée | **965,3 t** |
| `Z_MAX_29` annoncé | 1 530,7 t |
| `P29_TOTAL_CAPACITY_PER_LINE` | 2 600 t (2 × 1 300) |

**Hypothèse d'explication.** Les 1 300 t par cuve pourraient être exprimées en **tonnes
d'acide marchand** et non en tonnes de P₂O₅. Conversion : $2\,600 \times 0{,}26 = 676$ t de
P₂O₅ — mais cela ne redonne toujours pas 965 t. L'hypothèse ne suffit donc pas.

**Contrôle par la géométrie.** Une cuve de 1 300 t d'acide occuperait
$1\,300 / 1{,}270 = 1\,024$ m³, soit $1\,024 / 174{,}11 = 5{,}88$ m de hauteur — inférieur à
la hauteur maximale de 8,40 m. Les deux données sont incompatibles quelle que soit
l'interprétation.

**Arbitrage.** Retenir la valeur géométrique (965,3 t), méthode validée sur l'acide 54.

**Impact.** Fort sur le comportement du modèle, d'où la question **Q3**.

---

## A-08 — Capacités d'échelon : t/heure ou t/jour ? 🟡

**Constat.** `CORE_FIXED_ELEMENTS.md` annote `ECHELON_CAPACITY` en « tonnes/hour », mais
fournit la formule $P54 = C \times h / 24$.

**Preuve par l'absurde.** Si $C$ était en t/h, un échelon de 420 t/h marchant 24 h
produirait $420 \times 24 = 10\,080$ t/jour. Or la formule le divise par 24, ce qui n'aurait
aucun sens dimensionnel. Et cinq lignes à ce régime produiraient plus de 50 000 t P₂O₅/jour
— soit près de vingt fois la production mondiale quotidienne du groupe OCP.

**Arbitrage.** Les capacités sont en **tonnes par jour à plein régime (24 h)**. La formule
$C \times h/24$ est un simple **prorata horaire**.

**Impact.** Nul sur les calculs (la formule était déjà appliquée correctement), mais
important pour la clarté de la documentation et du code.

---

## A-09 — Deux listes contradictoires de lignes décadmiantes 🟡

**Constat.** `REAL_SCENARIO_REFERENCE.md` donne deux listes différentes :

```python
REAL_LINE_CAPABILITIES['DEC_29_ENABLED']       = ['13CD', '13XY']
REAL_DECADMIATION_CONFIG['enabled_lines'] = ['13AB','13CD','13XY','13ZU','13F']
```

**Interprétation retenue.** Les deux listes ne décrivent pas la même chose :
- `enabled_lines` — les lignes **physiquement équipées** de filtres ;
- `DEC_29_ENABLED` — les lignes **autorisées à produire de l'acide 29 dec destiné aux
  engrais**, un sous-ensemble opérationnel.

Cette lecture est cohérente avec le `PROCESS_GUIDE` §3.4, qui distingue explicitement trois
types de capacité de ligne.

**Arbitrage.** Modéliser les deux ensembles séparément. Une ligne peut décadmier si elle est
dans `enabled_lines` ; son acide décadmié ne peut aller aux engrais que si elle est aussi
dans `DEC_29_ENABLED`.

**Impact.** Faible, mais il faut y penser : ne pas confondre les deux ensembles.

---

## A-10 — Le fichier `quality_profiles_v2.json` est absent 🟠

**Constat.** Ce fichier est référencé comme « essentiel » dans quatre documents, mais ne
figure pas dans le dossier remis.

**Ce dont nous disposons.** Les coefficients sont dispersés dans le texte :

| Produit | Coefficients connus | Source |
|---|---|---|
| DAP_STANDARD | 29_std 0,127 · 54_ncl 0,354 | `REAL_SCENARIO_REFERENCE` |
| TSP_EURO | 54_dec_total 0,379 | idem |
| MAP_11_52_EU | 29_dec 0,030 · 54_dec_total 0,129 | idem |
| NPK_12_24_12_EU | 54_dec_total 0,091 | idem |
| NPK_15_15_15_… | 29_dec 0,171 | idem |
| MAP_11_52_SPECIAL | 29_std 0,625 | `CORE_FIXED_ELEMENTS` |
| DAP_EURO | 29_dec 0,120 · 54_dec_total 0,109 | idem |
| NPK_14_18_18_… | 54_dec_total 0,513 | idem |

**Arbitrage.** Reconstruire le fichier JSON à partir de ces coefficients, en le structurant
proprement et en marquant explicitement chaque source. Le fichier sera clairement identifié
comme **reconstruit**, et remplaçable dès que l'original sera disponible.

**Alerte supplémentaire.** Un même produit apparaît sous **deux noms différents** dans le
même scénario : `MAP_11_54_NE_EU` et `MAP_11_52_EU`. Il s'agit vraisemblablement d'une
coquille. Nous retenons `MAP_11_52_EU`, cohérent avec la nomenclature MAP 11-52-0.

**Impact.** Important — sans profils, aucune conversion demande d'engrais → besoins en
acide. → Question **Q6**.

---

## A-11 — Format Excel : 5 ou 7 feuilles ? 🟢

**Constat.**
- `OUTPUT_FORMAT.md` : **5 feuilles** (Demand Delivery, Phosphoric Production, Acid 29
  Stocks, Acid 54 Stocks, Central Storage Stocks)
- `archive/TEST_REFERENCE_OUTPUT.md` : **7 feuilles** (avec Flow Analysis et KPI Dashboard)

**Arbitrage.** **5 feuilles**, conformément à `OUTPUT_FORMAT.md`.

**Justification.** Le document à 7 feuilles est dans `archive/`, donc explicitement marqué
comme obsolète. `OUTPUT_FORMAT.md` se présente comme reflétant « le système actuel ».

**Note.** Les feuilles « Flow Analysis » et « KPI Dashboard » sont utiles. On pourra les
ajouter **en option** si l'encadrant le souhaite — ce ne sera pas un travail perdu, les
données seront déjà calculées. → Question **Q7**.

---

## Ce que ces anomalies nous apprennent

### 1. Ne jamais recopier un chiffre — le recalculer

Quatre des onze anomalies sont de simples erreurs arithmétiques. Toutes ont été détectées en
**réappliquant les formules du document à ses propres données**. C'est un réflexe à
conserver toute la vie professionnelle.

> **Conséquence pour le code (Phase 3).** Aucune valeur dérivée ne sera écrite en dur.
> Tout ce qui peut être calculé le sera, à partir des données primaires, et un test
> unitaire vérifiera chaque formule.

### 2. Hiérarchiser les sources

Face à une contradiction, il faut une **règle de priorité** décidée à l'avance, et non un
choix au cas par cas. La nôtre :

```
1. PROCESS_GUIDE.md        (se déclare référence définitive du procédé)
2. REAL_SCENARIO_REFERENCE.md  (décrit le scénario à reproduire)
3. CORE_FIXED_ELEMENTS.md  (constantes)
4. OUTPUT_FORMAT.md        (format de sortie uniquement)
5. archive/*               (obsolète, valeur indicative)
```

Et par-dessus tout : **la cohérence physique et dimensionnelle tranche**. Une source qui
viole la conservation de la masse ou l'homogénéité des unités a tort, quel que soit son rang.

### 3. Une donnée manquante n'est pas un blocage

Deux données essentielles sont absentes ($\tau^{\max}$ et $\alpha$). La bonne réponse n'est
ni de deviner en silence, ni de s'arrêter, mais :

1. poser une valeur d'attente **explicitement signalée comme telle** ;
2. la rendre **paramétrable** (jamais écrite en dur) ;
3. **poser la question** à qui détient la réponse ;
4. **mesurer sa sensibilité** par une analyse dédiée.

C'est la démarche professionnelle. Elle permet d'avancer sans jamais dissimuler une
incertitude.
