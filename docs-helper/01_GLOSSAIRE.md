# 01 — GLOSSAIRE COMPLET

> Tous les termes du projet, définis une fois pour toutes.
> Organisation : chimie → procédés → équipements → entités du site → mathématiques.
> **Consulte ce fichier chaque fois qu'un mot te bloque.**

---

## 1. Chimie et produits

### Acide phosphorique — H₃PO₄
Produit chimique obtenu en attaquant du minerai de phosphate par de l'acide sulfurique.
C'est la matière première de presque tous les engrais phosphatés.

### P₂O₅ — pentoxyde de phosphore
La molécule « utile » contenue dans l'acide. Toute l'industrie du phosphate compte en
**tonnes de P₂O₅**, jamais en tonnes de produit brut — exactement comme on achète de l'or
en grammes d'or fin et non en grammes de bijou.

> **Point capital.** Quand un document du dossier écrit « 1 500 tonnes/jour », il faut lire
> **1 500 tonnes de P₂O₅ par jour**. Un atelier produisant 1 500 t P₂O₅/j d'acide à 26 %
> fabrique en réalité 1 500 / 0,26 ≈ 5 770 t/j de solution acide.
> Justification complète en `04`, §2 et décision **D-01**.

### Titre (ou concentration)
Fraction massique de P₂O₅ dans la solution. Le dossier utilise :

| Acide | Appellation commerciale | Titre réel retenu | Densité |
|---|---|---|---|
| Acide 29 | « 29 % » | **0,26** (26 %) | 1,270 t/m³ |
| Acide 54 | « 54 % » | **0,50** (50 %) | 1,660 t/m³ |

L'appellation commerciale et le titre réel diffèrent légèrement : c'est courant dans
l'industrie, où le nom d'un grade est conventionnel.

### Acide 29 (P29)
Acide brut sortant des ateliers d'attaque-filtration. Peu concentré, chargé d'impuretés.
Deux qualités coexistent :
- **acide 29 standard** (`acid_29_std`) — l'acide ordinaire ;
- **acide 29 décadmié** (`acid_29_dec`) — débarrassé de son cadmium.

### Acide 54 (P54)
Acide concentré. Quatre qualités coexistent :

| Code | Nom | Origine | Stockage |
|---|---|---|---|
| `acid_54_ncl` | **NCL** — non clarifié | sortie directe de concentration | local (à l'atelier) |
| `acid_54_cl` | **CL** — clarifié | clarification du NCL | central, **IR12** |
| `acid_54_coc` | **CoC** — cocristallisé | cocristallisation du NCL | central, **IR11** |
| `acid_54_dec_cl` | **DEC_CL** — décadmié clarifié | concentration puis clarification de l'acide 29 décadmié | central, **IR11** |

### `acid_54_dec_total`
**Ce n'est pas un produit**, c'est un **besoin**. Certains engrais réclament un acide 54
« de qualité décadmiée » ; ce besoin peut être couvert **indifféremment** par du DEC_CL ou
du CoC, tous deux stockés dans IR11. Mathématiquement, c'est une contrainte sur la **somme**
de deux livraisons, pas sur chacune.

### Cadmium (Cd)
Métal lourd toxique naturellement présent dans le minerai de phosphate. Les réglementations
européennes plafonnent sa teneur dans les engrais. D'où la nécessité de le retirer :
c'est la **décadmiation**.

### Boue (*sludge*)
Résidu solide ou pâteux séparé lors d'un traitement. Il contient encore du P₂O₅, donc on ne
le jette pas : il est **recyclé vers un stock amont**. Toute boue produite quelque part
réapparaît donc comme une entrée ailleurs — c'est ce qui rend les bilans matière intéressants.

---

## 2. Procédés (les transformations)

### Concentration
**29 % → 54 %.** On évapore de l'eau sous vide.
- Entrée : acide 29 (standard ou décadmié)
- Sortie : acide 54 NCL (ou NCL DEC si l'entrée était décadmiée)
- **Rendement : 100 % en P₂O₅** (rien ne se perd, seule l'eau part)
- Réalisée par les **échelons**

### Décadmiation
**Retrait du cadmium**, appliqué à l'acide 29 juste après sa production.
- Entrée : acide 29 standard
- Sortie : acide 29 décadmié
- **Particularité majeure :** ne fonctionne qu'à des **niveaux discrets**, 750 t ou 1 500 t
  par jour, selon qu'on allume 1 ou 2 filtres. Impossible de décadmier 900 t.
  C'est ce qui impose une formulation **en nombres entiers**.
- L'acide décadmié **ne peut pas être transféré** entre ateliers.

### Clarification
**Retrait des impuretés solides** de l'acide 54 par décantation.
- Entrée : acide 54 NCL (ou NCL DEC)
- Sorties : **90 %** d'acide clarifié + **10 %** de boue recyclée vers le stock d'acide 29
- Réalisée par les **décanteurs**
- Deux usages, en concurrence pour la même capacité :
  - clarifier du NCL ordinaire → **CL** → IR12 *(décision de l'optimiseur)*
  - clarifier du NCL décadmié → **DEC_CL** → IR11 *(obligatoire)*

### Cocristallisation
**Purification poussée par cristallisation.**
- Entrée : acide 54 NCL
- Sorties : **80 %** de CoC + **20 %** de boue recyclée
- Disponible **uniquement** sur les ateliers 14EXT et 14AB
- **Fonctionnement systématique** (voir ci-dessous)
- Un acide cocristallisé **ne peut plus être clarifié** : c'est déjà un produit fini de
  haute pureté, équivalent au DEC_CL.

### Systématique (par opposition à « à la demande »)
Un procédé **systématique** tourne dès que son équipement est en service, sans se soucier
des besoins. Concrètement : si l'échelon *I* est affecté à la cocristallisation, **tout**
l'acide qu'il produit part en cocristallisation, même si personne n'a commandé de CoC.

> C'est contre-intuitif pour un étudiant en optimisation : on s'attend à ce que tout soit
> pilotable. Ici non — c'est une **contrainte imposée**, un fait, pas une décision.
> Industriellement, cela s'explique : ces unités ne se démarrent et ne s'arrêtent pas
> facilement, on les fait tourner en continu.

### Transfert interzone
Déplacement d'acide 29 **standard** d'un atelier vers un autre, par conduite.
- Objectifs : éviter qu'une cuve déborde, éviter qu'une autre se vide, alimenter un atelier
  de concentration plus gourmand que son atelier amont.
- **Toutes les liaisons n'existent pas** : une matrice donne les couples autorisés.
- Quantité **minimale** : 100 t (en dessous, l'opération n'a pas de sens : amorçage de pompe,
  mobilisation d'opérateur).
- Quantité **maximale** : existe, mais sa valeur n'est pas dans le dossier → question **Q1**.
- **L'acide décadmié ne se transfère jamais** : il est traité immédiatement.

---

## 3. Équipements

### Ligne (ou atelier)
Une chaîne de production complète. Le site en compte deux familles :
- **Lignes P29** (6) : `13AB`, `13CD`, `13XY`, `13ZU`, `13E`, `13F`
- **Lignes P54** (5) : `14AB`, `14CD`, `14XY`, `14ZU`, `14EXT`

Chaque ligne P29 alimente **une seule** ligne P54, sauf `13F` qui n'en a aucune :

| Ligne P29 | → Ligne P54 |
|---|---|
| 13AB | 14AB |
| 13CD | 14CD |
| 13XY | 14XY |
| 13ZU | 14ZU |
| 13E | **14EXT** *(attention au nom)* |
| 13F | **aucune** — son acide part directement aux clients ou en transfert |

### Échelon
**Unité élémentaire de concentration.** Une ligne P54 en compte plusieurs (4 à 6), chacun
avec sa capacité propre et ses propres heures de marche. La production d'un échelon vaut :

$$\kappa_e = C_e \times \frac{h_e}{24}$$

où $C_e$ est sa capacité journalière à plein régime et $h_e$ son nombre d'heures de marche.

Les échelons portent des lettres (A à W) et sont répartis ainsi :

| Ligne P54 | Échelons | Dont cocristallisation |
|---|---|---|
| 14EXT | E, F, G, H | tous (par défaut) |
| 14AB | A, B, I, J, K, L | sous-ensemble variable |
| 14CD | C, D, M, N | aucun |
| 14XY | X, Y, P, Q | aucun |
| 14ZU | Z, U, R, S, V, W | aucun |

### Décanteur
Cuve de séparation par gravité qui réalise la clarification.
**2 décanteurs par ligne P54**, soit **1 000 t/jour** de capacité totale par ligne, partagée
entre clarification ordinaire et clarification d'acide décadmié.

### Filtre (de décadmiation)
Équipement de retrait du cadmium. **1 filtre = 750 t/jour.** D'où les niveaux discrets
{0, 750, 1 500}.

### Cuve / bac de stockage
- **Stockage local P29** : 2 cuves par ligne, partagées entre acide standard et décadmié.
- **Stockage local P54** : 2 cuves par ligne, pour le NCL uniquement.
- **Stockage central** : IR11 et IR12.

**Le niveau se mesure en mètres**, puis se convertit en tonnes de P₂O₅ par une formule
géométrique (voir `04`, §3).

### IR11
Bac central recevant **CoC** et **DEC_CL** — les deux acides de haute pureté.
Ils y sont **mélangés** : c'est pourquoi le besoin `acid_54_dec_total` peut être couvert par
l'un ou l'autre.

### IR12
Bac central recevant uniquement l'acide **CL** (clarifié ordinaire).

> **Règle de distribution capitale :** un acide traité (CL, CoC, DEC_CL) n'est **jamais**
> expédié directement depuis sa ligne de production. Il transite obligatoirement par IR11 ou
> IR12. Conséquence mathématique heureuse : ces acides échappent aux contraintes
> d'interconnexion, puisque les bacs centraux desservent tout le monde.

---

## 4. Entités du site (les acteurs)

### Ateliers d'engrais (consommateurs « transformateurs »)
Ils fabriquent des engrais et consomment de l'acide selon des **recettes** :

| Atelier | Rôle |
|---|---|
| **U16** | Production de DAP, TSP |
| **U116A** | Production de MAP |
| **U116BC** | Production de NPK |

### Consommateurs industriels (consommateurs « directs »)
Ils commandent de l'acide en tant que tel, sans recette :

| Consommateur | Nature | Acide consommé |
|---|---|---|
| **EMAPHOS** | *Euro-Maroc Phosphore* — coentreprise OCP / Prayon / Budenheim, produit de l'acide purifié | acide 54 NCL |
| **IMACID** | *Indo-Maroc Phosphore* — coentreprise OCP / groupes indiens | acide 29 standard |
| **MAPS** | Unité partenaire | acide 29 standard |
| **U53** | Unité interne | acide 54 CL (depuis IR12) |
| **107DEF** | Unité interne polyvalente | acide 29 std, CL, ou CoC |
| **JFC1-5** | *Jorf Fertilizer Company*, unités 1 à 5 | acide 29 standard |

### Le cas EMAPHOS — un consommateur qui rend de la matière
EMAPHOS purifie l'acide par **extraction liquide-liquide au solvant**. Ce procédé ne récupère
qu'une partie du P₂O₅ ; le reste, chargé d'impuretés, revient dans le circuit principal.

Sur 100 t reçues, **40 t reviennent** vers les stocks d'acide 29 :

| Flux retour | Part | Destination |
|---|---|---|
| ARP1 | 12,5 % | stock acide 29 std de **13AB** |
| ARP2 | 12,5 % | stock acide 29 std de **13CD** |
| Boue | 15,0 % | stock acide 29 std de **13XY** |

> **Attention au piège de modélisation.** EMAPHOS consomme au **niveau 54** et restitue au
> **niveau 29**. C'est le seul flux du système qui remonte d'un niveau. Il faut donc bien
> soustraire 100 % de la livraison du stock NCL, et ajouter 40 % aux trois stocks P29 cités.

### Engrais fabriqués

| Sigle | Nom | Composition |
|---|---|---|
| **DAP** | Phosphate diammonique | 18-46-0 |
| **MAP** | Phosphate monoammonique | 11-52-0 |
| **TSP** | Superphosphate triple | 0-46-0 |
| **NPK** | Engrais ternaire | azote-phosphore-potassium, dosages variables |

### Profil qualité
La **recette** d'un engrais, exprimée en tonnes d'acide par tonne d'engrais produite.

*Exemple.* Le profil de `DAP_STANDARD` vaut :
```
acid_29_std : 0,127     acid_54_ncl : 0,354
```
Produire 3 057 t de DAP réclame donc :
- 0,127 × 3 057 = **388,2 t** d'acide 29 standard
- 0,354 × 3 057 = **1 082,2 t** d'acide 54 NCL

Mathématiquement, un profil est une **application** $q : \text{Produit} \times \text{Type
d'acide} \to \mathbb{R}_+$, et la conversion demande → besoins est une simple application
linéaire.

---

## 5. Vocabulaire mathématique du projet

### Programme linéaire (PL)
Problème d'optimisation où l'objectif et toutes les contraintes sont des fonctions
**affines** des variables, celles-ci étant réelles. Se résout exactement et rapidement.

### Programme linéaire en nombres entiers mixte (MILP)
Un PL dont **certaines** variables sont contraintes à être entières ou binaires. Ici :
- le choix du niveau de décadmiation (0 / 750 / 1 500) ;
- l'activation ou non d'un transfert interzone.

C'est cette combinatoire qui fait la difficulté — et l'intérêt — du problème.

### Variable binaire
Variable $b \in \{0, 1\}$, servant à représenter un choix « oui/non ».

### Variable semi-continue
Variable qui vaut soit 0, soit une valeur comprise entre une borne basse strictement positive
et une borne haute. Exactement le cas d'un transfert interzone : soit on ne transfère rien,
soit on transfère au moins 100 t.

**Modélisation standard**, avec $b \in \{0,1\}$ :
$$\tau^{\min} \cdot b \;\le\; t \;\le\; \tau^{\max} \cdot b$$

*Vérification.* Si $b = 0$ : $0 \le t \le 0$, donc $t = 0$.
Si $b = 1$ : $\tau^{\min} \le t \le \tau^{\max}$. Les deux cas voulus, et aucun autre. ∎

### Bilan matière
Équation de conservation en un point du système :
$$\text{stock initial} + \text{entrées} \;=\; \text{sorties} + \text{stock final}$$
C'est la traduction mathématique de « la matière ne se crée ni ne se détruit ».
Chaque cuve du système donne exactement une équation de ce type.

### Optimisation lexicographique
Méthode pour traiter plusieurs objectifs de **priorités strictement différentes**.
On optimise d'abord $f_1$ ; on note $f_1^\star$ son optimum ; on ajoute la contrainte
$f_1 = f_1^\star$ ; puis on optimise $f_2$ sous cette contrainte ; et ainsi de suite.

Aucun compromis n'est possible entre niveaux : gagner sur $f_2$ ne justifie **jamais** de
perdre sur $f_1$. C'est exactement la logique industrielle voulue ici — servir le client
prime sur tout le reste.

### Contrainte active (ou saturée)
Contrainte d'inégalité vérifiée avec égalité à l'optimum. Elle identifie les **goulots
d'étranglement** : ce sont ces contraintes qui limitent réellement la performance, et donc
celles sur lesquelles investir.

### Dégénérescence
Situation où plusieurs solutions distinctes atteignent la même valeur optimale. Le solveur
en choisit une arbitrairement, et le résultat devient instable et peu crédible auprès des
exploitants. C'est précisément le défaut de l'objectif proposé dans le dossier
(voir `05`, §7.1).

---

## 6. Table de correspondance des notations

| Notation | Objet | Défini en |
|---|---|---|
| $\mathcal{L}_{29}$, $\mathcal{L}_{54}$ | ensembles des lignes | `05` §2 |
| $\mathcal{E}$, $\mathcal{E}_m$, $\mathcal{E}^{coc}_m$ | échelons | `05` §2 |
| $\mathcal{K}$ | consommateurs | `05` §2 |
| $\mathcal{A}$ | types d'acide | `05` §2 |
| $\sigma$ | application ligne 29 → ligne 54 | `05` §2 |
| $P_\ell$ | production d'acide 29 (paramètre) | `05` §3 |
| $\kappa_e$ | production d'un échelon | `05` §3 |
| $\eta^{cl}, \eta^{coc}$ | rendements (0,90 / 0,80) | `05` §3 |
| $\Lambda$ | capacité décanteur (1 000 t/j) | `05` §3 |
| $d_\ell$ | quantité décadmiée (variable) | `05` §4 |
| $x^{std}_\ell, x^{dec}_\ell$ | envois en concentration | `05` §4 |
| $t_{\ell\ell'}$ | transfert interzone | `05` §4 |
| $u^{ncl}_m, u^{dec}_m$ | entrées en clarification | `05` §4 |
| $y$ | livraisons | `05` §4 |
| $\rho$ | manques (demande non servie) | `05` §4 |
| $S$ | stocks finaux | `05` §4 |
| $f_1, f_2, f_3$ | niveaux de l'objectif | `05` §7 |
