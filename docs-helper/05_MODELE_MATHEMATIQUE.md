# 05 — MODÈLE MATHÉMATIQUE

> **Le cœur du stage.** Formalisation complète du problème d'optimisation.
>
> **Discipline de rédaction :** rien n'est utilisé avant d'être défini. On procède dans
> l'ordre : ensembles → paramètres → variables → contraintes → objectif.
> Chaque équation est suivie de sa **traduction en français**, de son **organe industriel**
> et de sa **justification**.

---

## 1. Nature du problème

**Programme linéaire mixte en nombres entiers (MILP), mono-période.**

| Caractéristique | Valeur |
|---|---|
| Horizon | 1 journée |
| Variables continues | **141** *(mesuré)* |
| Variables binaires | **29** *(mesuré)* |
| Contraintes | **138** *(mesuré)* |
| Objectif | lexicographique à 3 niveaux |
| Solveur envisagé | PuLP + CBC (libre) |
| Temps de résolution | **0,06 s** *(mesuré)* |

**Pourquoi « en nombres entiers » ?** Deux familles de décisions sont intrinsèquement
discrètes :
1. les niveaux de décadmiation appartiennent à $\{0, 750, 1500\}$ (on allume 0, 1 ou 2
   filtres) ;
2. un transfert interzone est soit nul, soit d'au moins 100 t (variable semi-continue).

La relaxation continue produirait des solutions physiquement irréalisables.
Voir décision **D-03**.

---

## 2. Ensembles

> *Un ensemble répond à la question : « sur quoi porte l'indice ? »*

| Symbole | Définition | Cardinal | Éléments |
|---|---|---|---|
| $\mathcal{L}_{29}$ | lignes de production d'acide 29 | 6 | 13AB, 13CD, 13XY, 13ZU, 13E, 13F |
| $\mathcal{L}_{54}$ | lignes de concentration | 5 | 14AB, 14CD, 14XY, 14ZU, 14EXT |
| $\mathcal{E}$ | échelons de concentration | 24 | A…W |
| $\mathcal{K}$ | consommateurs | 9 | U16, U116A, U116BC, IMACID, EMAPHOS, MAPS, U53, 107DEF, JFC1-5 |
| $\mathcal{P}$ | produits engrais | var. | DAP_STANDARD, TSP_EURO, … |
| $\mathcal{A}$ | types d'acide | 6 | voir ci-dessous |

### 2.1 Types d'acide

$$\mathcal{A} = \underbrace{\{\text{29std},\ \text{29dec}\}}_{\mathcal{A}_{29}} \;\cup\;
\underbrace{\{\text{54ncl},\ \text{54cl},\ \text{54coc},\ \text{54deccl}\}}_{\mathcal{A}_{54}}$$

**Sous-ensembles utiles :**
- $\mathcal{A}^{\text{loc}} = \{\text{29std},\ \text{29dec},\ \text{54ncl}\}$ — livrés depuis un
  **stock local**, donc soumis aux contraintes d'interconnexion ;
- $\mathcal{A}^{\text{cen}} = \{\text{54cl},\ \text{54coc},\ \text{54deccl}\}$ — livrés depuis
  **IR11 ou IR12**, donc **sans** contrainte d'interconnexion.

> **Justification de cette partition.** Elle traduit la règle industrielle « aucun acide
> traité n'est expédié directement depuis sa ligne ». Elle a un intérêt pratique majeur :
> elle divise par deux le nombre de variables de livraison à créer.

### 2.2 Application ligne 29 → ligne 54

$$\sigma : \mathcal{L}_{29} \longrightarrow \mathcal{L}_{54} \cup \{\varnothing\}$$

$$\sigma(\text{13AB}) = \text{14AB},\quad
\sigma(\text{13CD}) = \text{14CD},\quad
\sigma(\text{13XY}) = \text{14XY},$$
$$\sigma(\text{13ZU}) = \text{14ZU},\quad
\sigma(\text{13E}) = \text{14EXT},\quad
\sigma(\text{13F}) = \varnothing$$

**Propriété.** $\sigma$ restreinte à $\mathcal{L}_{29} \setminus \{\text{13F}\}$ est une
**bijection** sur $\mathcal{L}_{54}$. Son inverse $\sigma^{-1}$ est donc bien défini sur
$\mathcal{L}_{54}$, ce qui autorise à écrire indifféremment une équation « côté 29 » ou
« côté 54 ».

**Notation.** On pose $\mathcal{L}_{29}^{\ast} = \sigma^{-1}(\mathcal{L}_{54})
= \mathcal{L}_{29} \setminus \{\text{13F}\}$ : les lignes 29 disposant d'une concentration.

### 2.3 Partition des échelons

Les échelons sont **partitionnés** par ligne :
$$\mathcal{E} = \bigsqcup_{m \in \mathcal{L}_{54}} \mathcal{E}_m$$

Chaque ligne distingue ses échelons dédiés à la cocristallisation :
$$\mathcal{E}^{coc}_m \subseteq \mathcal{E}_m,
\qquad \mathcal{E}^{ncl}_m = \mathcal{E}_m \setminus \mathcal{E}^{coc}_m$$

avec $\mathcal{E}^{coc}_m = \varnothing$ pour $m \notin \{\text{14EXT}, \text{14AB}\}$.

### 2.4 Ensembles de capacités configurables

- $\mathcal{L}^{dec}_{29} \subseteq \mathcal{L}_{29}$ — lignes équipées de filtres de décadmiation
- $\mathcal{L}^{clar}_{54} \subseteq \mathcal{L}_{54}$ — lignes équipées de décanteurs actifs
- $\mathcal{L}^{deccl}_{54} \subseteq \mathcal{L}_{54}$ — lignes autorisées à produire du DEC_CL

### 2.5 Relations d'incidence

$$\Gamma \subseteq \mathcal{L}_{29} \times \mathcal{L}_{29}
\qquad\text{(liaisons interzones autorisées, }|\Gamma| = 14\text{)}$$

$$\Phi_a \subseteq \mathcal{L} \times \mathcal{K}
\qquad\text{(raccordements ligne → consommateur, pour } a \in \mathcal{A}^{\text{loc}})$$

**Convention.** $\Gamma$ est **anti-réflexive** ($(\ell,\ell) \notin \Gamma$) et
**non symétrique**.

---

## 3. Paramètres

> *Un paramètre est une donnée **connue avant** la résolution. Test : « l'usine peut-elle
> changer ça demain matin ? » Si non, c'est un paramètre.*

### 3.1 Production

| Symbole | Définition | Unité |
|---|---|---|
| $P_\ell$ | production d'acide 29 de la ligne $\ell$ | t P₂O₅/j |
| $C_e$ | capacité de l'échelon $e$ à 24 h | t P₂O₅/j |
| $h_e$ | heures de marche de l'échelon $e$ | h |

**Grandeurs dérivées** (calculées en pré-traitement, pas des variables) :

$$\kappa_e = C_e \cdot \frac{h_e}{24}
\qquad\text{production de l'échelon } e$$

$$\Pi_m = \sum_{e \in \mathcal{E}_m} \kappa_e
\qquad\text{production totale de la ligne } m$$

$$\Pi^{coc}_m = \sum_{e \in \mathcal{E}^{coc}_m} \kappa_e
\qquad
\Pi^{ncl}_m = \Pi_m - \Pi^{coc}_m$$

$$G_m = \eta^{coc} \cdot \Pi^{coc}_m
\qquad\text{CoC produit (systématique)}$$

$$B^{coc}_m = (1 - \eta^{coc}) \cdot \Pi^{coc}_m
\qquad\text{boue de cocristallisation}$$

> **Point de méthode essentiel.** $G_m$ et $B^{coc}_m$ sont des **paramètres**, pas des
> variables, parce que la cocristallisation est **systématique** (voir `03`, §4.3).
> C'est ce qui simplifie le plus le modèle. Une erreur fréquente serait d'en faire une
> décision : le modèle serait alors plus gros, plus lent, et **faux** — il produirait des
> plans que l'usine ne peut pas exécuter.

### 3.2 Rendements et capacités

| Symbole | Valeur | Signification |
|---|---|---|
| $\eta^{conc}$ | 1,00 | rendement de concentration (P₂O₅ conservé) |
| $\eta^{cl}$ | 0,90 | rendement de clarification |
| $\eta^{coc}$ | 0,80 | rendement de cocristallisation |
| $\Lambda$ | 1 000 | capacité **entrante** des décanteurs, par ligne (t/j) |
| $\mathcal{D}$ | $\{0, 750, 1500\}$ | niveaux de décadmiation admissibles |
| $\tau^{\min}$ | 100 | transfert interzone minimal (t) |
| $\tau^{\max}$ | 1 000 | transfert interzone maximal (t) — *valeur d'attente, Q1* |
| $\alpha$ | 0,15 | part minimale de DEC_CL dans les entrées d'IR11 — *valeur d'attente, Q2* |

### 3.3 Stocks

| Symbole | Définition |
|---|---|
| $S^{0,std}_\ell,\ S^{0,dec}_\ell$ | stocks initiaux d'acide 29, par qualité |
| $S^{0,ncl}_m$ | stock initial d'acide 54 NCL |
| $S^{0,11},\ S^{0,12}$ | stocks initiaux des bacs centraux |
| $Z^{\min}_\bullet,\ Z^{\max}_\bullet$ | bornes basse et haute de chaque stock |

### 3.4 Demande

| Symbole | Définition |
|---|---|
| $\delta_{k,a}$ | demande directe du consommateur $k$ en acide $a$ (t) |
| $F_{k,p}$ | tonnage d'engrais $p$ à produire par l'atelier $k$ (t) |
| $q_{p,a}$ | profil qualité : tonnes d'acide $a$ par tonne d'engrais $p$ |

**Demande consolidée** (paramètre calculé en pré-traitement) :

$$\boxed{\;R_{k,a} \;=\; \delta_{k,a} \;+\; \sum_{p \in \mathcal{P}} q_{p,a}\, F_{k,p}\;}$$

> **Traduction.** Le besoin total du consommateur $k$ en acide de type $a$ est la somme de
> ce qu'il commande directement et de ce qu'exigent les recettes des engrais qu'il fabrique.
>
> **Nature mathématique.** C'est une **application linéaire** de l'espace des tonnages
> d'engrais vers l'espace des besoins en acide. Elle se calcule une fois pour toutes, avant
> l'optimisation.

### 3.5 Retours EMAPHOS

$$\beta_{13AB} = 0{,}125,\qquad \beta_{13CD} = 0{,}125,\qquad \beta_{13XY} = 0{,}150,
\qquad \beta_\ell = 0 \text{ sinon}$$

avec $\sum_\ell \beta_\ell = 0{,}40$.

---

## 4. Variables de décision

> *Une variable est ce que le solveur **choisit**. Toutes sont positives ou nulles, sauf
> mention contraire.*

### 4.1 Décadmiation — variables binaires

$$w_{\ell,v} \in \{0,1\},
\qquad \ell \in \mathcal{L}^{dec}_{29},\ v \in \mathcal{D}$$

$w_{\ell,v} = 1$ signifie « la ligne $\ell$ décadmie exactement $v$ tonnes ».

**Quantité décadmiée** (variable dérivée, affine en $w$) :
$$d_\ell = \sum_{v \in \mathcal{D}} v \cdot w_{\ell,v}$$

### 4.2 Concentration

$$x^{std}_\ell \ge 0,\qquad x^{dec}_\ell \ge 0,
\qquad \ell \in \mathcal{L}^{\ast}_{29}$$

Quantités d'acide 29 standard et décadmié envoyées de la ligne $\ell$ vers la concentration.

### 4.3 Transferts interzones

$$t_{\ell\ell'} \ge 0,\qquad b_{\ell\ell'} \in \{0,1\},
\qquad (\ell,\ell') \in \Gamma$$

$t$ est la quantité transférée, $b$ indique si le transfert est activé.

> **Remarque d'implémentation.** On ne crée les variables que pour les couples de $\Gamma$.
> Créer une variable puis la forcer à 0 serait un gaspillage : 14 couples au lieu de 30.

### 4.4 Clarification

$$u^{ncl}_m \ge 0,\qquad m \in \mathcal{L}^{clar}_{54}$$

Quantité de NCL envoyée en clarification.

**Il n'y a pas de variable $u^{dec}_m$.** L'acide décadmié concentré est **obligatoirement**
clarifié (voir `03`, §3.4), d'où la substitution directe :
$$u^{dec}_m \;\equiv\; x^{dec}_{\sigma^{-1}(m)}$$

> **Élégance de cette substitution.** Elle supprime 5 variables *et* 5 contraintes
> d'égalité, tout en rendant automatique le couplage décadmiation ↔ décanteurs. C'est un bon
> exemple de la règle : **une contrainte d'égalité définissant une variable doit être
> éliminée par substitution.**

### 4.5 Livraisons

**Depuis un stock local** ($a \in \mathcal{A}^{\text{loc}}$) :
$$y^{a}_{\ell,k} \ge 0,\qquad (\ell,k) \in \Phi_a$$

**Depuis un stock central** :
$$y^{cl}_{k} \ge 0,\qquad y^{coc}_{k} \ge 0,\qquad y^{deccl}_{k} \ge 0,
\qquad k \in \mathcal{K}$$

### 4.6 Stocks finaux

$$S^{std}_\ell,\ S^{dec}_\ell,\ S^{ncl}_m,\ S^{11},\ S^{12} \;\ge\; 0$$

> Ce sont bien des **variables** : elles résultent des décisions. Mais elles sont entièrement
> **déterminées** par les autres variables via les bilans matière. On les garde explicites
> pour la lisibilité du modèle et la simplicité du rapport de sortie.

### 4.7 Variables d'écart (contraintes molles)

$$\rho_{k,a} \ge 0 \qquad\text{demande non satisfaite}$$
$$\nu^{+}_{\bullet},\ \nu^{-}_{\bullet} \ge 0 \qquad\text{dépassement / sous-passement des bandes de stock}$$

> **Pourquoi des variables d'écart ?** Un modèle qui répond « Infeasible » est inutilisable
> en exploitation : l'ingénieur veut savoir *de combien* et *où* ça coince, pas se voir
> refuser une réponse. Les écarts rendent le modèle **toujours faisable**, et leur valeur
> à l'optimum est en elle-même une information de diagnostic.

---

## 5. Contraintes

> Chaque contrainte est numérotée, traduite, rattachée à son organe industriel et justifiée.

### (C1) Partage de la production d'acide 29

$$P^{std}_\ell \;=\; P_\ell - d_\ell \qquad \forall \ell \in \mathcal{L}_{29}$$

**Français.** Ce qui n'est pas décadmié reste standard.
**Organe.** Sortie de filtration, aiguillage vers les filtres de décadmiation.
**Justification.** La décadmiation ne crée pas de matière, elle **répartit** la production.

### (C2) Choix unique du niveau de décadmiation

$$\sum_{v \in \mathcal{D}} w_{\ell,v} = 1 \qquad \forall \ell \in \mathcal{L}^{dec}_{29}$$
$$d_\ell = 0 \qquad \forall \ell \notin \mathcal{L}^{dec}_{29}$$

**Français.** Chaque ligne équipée choisit exactement un niveau (0, 750 ou 1 500 t). Une
ligne non équipée ne décadmie pas.
**Organe.** Nombre de filtres mis en service.
**Justification.** C'est un encodage « one-hot » d'un choix discret. La somme égale à 1
garantit qu'un niveau et un seul est retenu.

### (C3) Faisabilité de la décadmiation

$$d_\ell \;\le\; P_\ell \qquad \forall \ell \in \mathcal{L}^{dec}_{29}$$

**Français.** On ne peut pas décadmier plus qu'on ne produit.
**Justification.** Sans cette contrainte, 13ZU (qui produit 800 t) pourrait « décadmier »
1 500 t et créer de la matière. **Contrainte indispensable**, absente du dossier.

### (C4) Charge de concentration — *révisée après réponse de l'encadrant*

$$\boxed{\;x^{std}_\ell + x^{dec}_\ell \;=\; \Pi_{\sigma(\ell)} + \varepsilon^{+}_\ell - \varepsilon^{-}_\ell\;}
\qquad \forall \ell \in \mathcal{L}^{\ast}_{29}$$

$$0 \le \varepsilon^{+}_\ell \le \epsilon\, \Pi_{\sigma(\ell)},
\qquad 0 \le \varepsilon^{-}_\ell \le \epsilon\, \Pi_{\sigma(\ell)}$$

**Français.** La ligne 29 fournit à sa concentration ce que celle-ci va produire, à une
tolérance de $\epsilon$ près (5 % par défaut). Tout écart est **pénalisé** au niveau 2 de
l'objectif.

**Origine.** L'encadrant, interrogé sur cette contrainte, a répondu :
> « Oui la somme doit être égale, c'est normalement rigide, mais on peut avoir des seuils
> de tolérance pour respecter la planification des transferts. »

**Justification de la forme.** Une égalité stricte ignorerait la tolérance accordée ; une
inégalité libre la banaliserait, l'optimiseur s'écartant du plan dès que cela l'arrange.
La bande **pénalisée** rend fidèlement les deux moitiés de la réponse : le modèle reste à
l'égalité stricte sauf lorsque s'en écarter évite une violation plus grave.
Voir décision **D-10**.

**Vérification empirique.** Sur le scénario de référence, la solution optimale n'utilise
**aucune** tolérance : les cinq lignes sont exactement au plan. Le comportement est donc
bien celui décrit comme « normalement rigide ».

### (C4b) Alimentation des échelons cocristallisants

$$x^{std}_\ell \;\ge\; \Pi^{coc}_{\sigma(\ell)} \qquad \forall \ell \in \mathcal{L}^{\ast}_{29}$$

**Français.** Les échelons affectés à la cocristallisation tournent au plan : ils doivent
recevoir leur alimentation en acide **standard**.

**Justification.** Conséquence directe de (C4) devenue souple. Si la charge peut s'écarter
du plan, il faut préciser **quels** échelons absorbent l'écart. Les unités de
cocristallisation ne se modulent pas ; ce sont donc les échelons ordinaires qui absorbent
la variation.

### (C5) Limite de l'acide décadmié en concentration

$$x^{dec}_\ell \;\le\; \Pi^{ncl}_{\sigma(\ell)} \qquad \forall \ell \in \mathcal{L}^{\ast}_{29}$$
$$x^{dec}_\ell = 0 \qquad \text{si } \sigma(\ell) \notin \mathcal{L}^{deccl}_{54}$$

**Français.** L'acide décadmié n'emprunte que les échelons non affectés à la
cocristallisation, et seules les lignes habilitées peuvent en traiter.
**Justification.** *(Hypothèse **H3**, à confirmer — question **Q8**.)* Un acide cocristallisé
ne peut pas être clarifié ; envoyer du décadmié sur un échelon de cocristallisation
produirait un acide impossible à traiter ensuite.
**Portée.** Dans le scénario de référence, la seule ligne DEC_CL est 14XY, qui n'a aucun
échelon de cocristallisation. La contrainte est donc **inactive** ici — mais elle protège
le modèle dans toute autre configuration.

### (C6) NCL réellement disponible — *révisée*

$$N_m \;=\; x^{std}_{\sigma^{-1}(m)} \;-\; \Pi^{coc}_m \qquad \forall m \in \mathcal{L}_{54}$$

**Français.** Le NCL ordinaire produit, c'est l'acide standard chargé, moins la part
consommée par les échelons cocristallisants.

**Justification de la révision.** Tant que (C4) était une égalité stricte, on pouvait
écrire $N_m = \Pi^{ncl}_m - x^{dec}$. Dès lors que la charge peut s'écarter du plan, la
production ne peut plus être un paramètre : elle doit suivre la charge réelle.

**Cohérence avec l'ancienne formule.** Quand la charge vaut exactement le plan,
$x^{std} + x^{dec} = \Pi_m = \Pi^{coc}_m + \Pi^{ncl}_m$, donc
$x^{std} - \Pi^{coc}_m = \Pi^{ncl}_m - x^{dec}$. La nouvelle écriture **généralise**
l'ancienne sans la contredire — c'est le test à faire systématiquement quand on relâche
une contrainte.

### (C7) Bilan matière — stock d'acide 29 standard ⭐

$$\begin{aligned}
S^{std}_\ell \;=\;& S^{0,std}_\ell + P^{std}_\ell
&& \text{(initial + production)}\\
&+ \sum_{\ell' : (\ell',\ell) \in \Gamma} t_{\ell'\ell}
 - \sum_{\ell' : (\ell,\ell') \in \Gamma} t_{\ell\ell'}
&& \text{(transferts entrants / sortants)}\\
&+ B^{coc}_{\sigma(\ell)}
&& \text{(boue de cocristallisation)}\\
&+ (1-\eta^{cl})\left(u^{ncl}_{\sigma(\ell)} + x^{dec}_\ell\right)
&& \text{(boue de clarification)}\\
&+ \beta_\ell \sum_{m} y^{54ncl}_{m,\text{EMAPHOS}}
&& \text{(retour EMAPHOS)}\\
&- x^{std}_\ell - \sum_{k} y^{29std}_{\ell,k}
&& \text{(concentration + livraisons)}
\end{aligned}$$

**Français.** Ce qui reste en cuve = ce qu'il y avait + ce qui est produit + ce qui rentre
(transferts, boues, retours) − ce qui sort (concentration, livraisons).

**C'est l'équation la plus riche du modèle.** Elle rassemble **six** flux entrants et deux
sortants. Détaillons chaque terme :

| Terme | Organe industriel | Piège à éviter |
|---|---|---|
| $P^{std}_\ell$ | sortie de filtration | ne pas oublier de retrancher $d_\ell$ |
| $t_{\ell'\ell}$, $t_{\ell\ell'}$ | conduites interzones | attention au sens des indices |
| $B^{coc}$ | eaux mères de cristallisation | va au niveau **29**, pas 54 (décision D-05) |
| boue de clarification | fond des décanteurs | porte sur **les deux** flux, NCL **et** DEC |
| retour EMAPHOS | raffinat de l'extraction | consommé en 54, restitué en **29** |
| $x^{std}_\ell$ | alimentation des échelons | — |
| $y^{29std}$ | expéditions clients | — |

> **⚠️ Les trois pièges classiques**, tous présents dans cette seule équation :
> 1. **Oublier la boue de clarification de l'acide décadmié.** Le terme
>    $(1-\eta^{cl}) x^{dec}_\ell$ est facile à manquer, car cette clarification est
>    « automatique » et n'a pas de variable dédiée.
> 2. **Se tromper de niveau pour le retour EMAPHOS.** Il est prélevé au niveau 54 et
>    restitué au niveau 29 — le seul flux du système qui remonte.
> 3. **Inverser les indices des transferts.** $t_{\ell'\ell}$ entre, $t_{\ell\ell'}$ sort.
>    Un test unitaire dédié est prévu en Phase 3.

### (C8) Bilan matière — stock d'acide 29 décadmié

$$S^{dec}_\ell \;=\; S^{0,dec}_\ell + d_\ell - x^{dec}_\ell - \sum_{k} y^{29dec}_{\ell,k}$$

**Français.** Bien plus simple : ce qui est décadmié part soit en concentration, soit chez un
client, soit reste en stock.
**Justification de sa simplicité.** L'acide décadmié **ne se transfère pas** entre lignes et
**ne reçoit aucune boue** (les boues sont de qualité standard).

### (C9) Capacité partagée des cuves d'acide 29

$$S^{std}_\ell + S^{dec}_\ell \;\le\; Z^{\max}_{29} + \nu^{+}_{29,\ell}$$
$$S^{std}_\ell + S^{dec}_\ell \;\ge\; Z^{\min}_{29} - \nu^{-}_{29,\ell}$$

**Français.** Les deux qualités partagent les mêmes cuves. Leur **somme** est bornée.
**Organe.** Les 2 cuves de la ligne.
**Piège.** Borner chaque qualité séparément autoriserait le double du volume réel.
**Nature molle.** Un dépassement est autorisé mais lourdement pénalisé au niveau 2 de
l'objectif (voir §7.4).

### (C10) Bilan matière — stock d'acide 54 NCL

$$S^{ncl}_m \;=\; S^{0,ncl}_m + N_m - u^{ncl}_m - \sum_{k} y^{54ncl}_{m,k}$$

**Français.** Le NCL produit part en clarification, chez un client, ou reste en stock.
**Remarque.** Aucune boue n'y revient (décision **D-05** : elles vont au niveau 29), et le
54 NCL DEC n'y transite jamais (pas de stockage local pour lui).

### (C11) ⭐ Capacité des décanteurs — la contrainte structurante

$$\boxed{\;u^{ncl}_m \;+\; x^{dec}_{\sigma^{-1}(m)} \;\le\; \Lambda\;}
\qquad \forall m \in \mathcal{L}^{clar}_{54}$$

et $u^{ncl}_m = 0$ pour $m \notin \mathcal{L}^{clar}_{54}$.

**Français.** Les 2 décanteurs d'une ligne traitent au plus 1 000 t/jour en entrée, tous
usages confondus.
**Organe.** Les 2 décanteurs de 500 t/j.
**Justification.** La limite porte sur l'**entrée** (décision **D-06**) : un décanteur est
dimensionné par le débit qu'il reçoit.

> **C'est la contrainte la plus intéressante du modèle.** Elle crée l'arbitrage central :
> ```
> décadmier plus  →  plus de DEC à clarifier (obligatoire)
>                 →  moins de capacité pour le NCL
>                 →  moins de CL vers IR12
>                 →  risque sur la demande de U53 (1 500 t)
> ```
> Elle sera très probablement **saturée** à l'optimum. C'est la première à examiner en
> Phase 5.

### (C12) Bilan matière — IR12

$$S^{12} \;=\; S^{0,12} + \eta^{cl} \sum_{m \in \mathcal{L}^{clar}_{54}} u^{ncl}_m
\;-\; \sum_{k} y^{cl}_{k}$$
$$Z^{\min}_{12} - \nu^{-}_{12} \;\le\; S^{12} \;\le\; Z^{\max}_{12} + \nu^{+}_{12}$$

**Français.** IR12 reçoit 90 % de tout ce qui est clarifié, et alimente les clients en CL.

### (C13) Bilan matière — IR11 (deux sous-inventaires)

$$S^{11,coc} = S^{0,11,coc} + \sum_{m} G_m - \sum_{k} y^{coc}_{k}$$
$$S^{11,deccl} = S^{0,11,deccl} + \eta^{cl}\sum_{m} x^{dec}_{\sigma^{-1}(m)} - \sum_{k} y^{deccl}_{k}$$
$$S^{11} = S^{11,coc} + S^{11,deccl}$$
$$Z^{\min}_{11} - \nu^{-}_{11} \;\le\; S^{11} \;\le\; Z^{\max}_{11} + \nu^{+}_{11}$$

**Français.** IR11 contient deux produits mélangés. On suit chacun séparément (car ils n'ont
pas la même origine), mais **une seule** contrainte de capacité porte sur leur somme — c'est
un bac unique.

> **Note.** Le dossier ne précise pas la répartition initiale entre CoC et DEC_CL dans IR11.
> Hypothèse **H4** : on l'attribue intégralement au CoC, ce qui est le cas le plus
> défavorable pour la contrainte de qualité (C15) et donc le plus prudent.

### (C14) Satisfaction de la demande

Pour tout $k \in \mathcal{K}$ et tout $a \in \mathcal{A}$ tel que $R_{k,a} > 0$ :

**Cas 1 — acide livré depuis un stock local** ($a \in \mathcal{A}^{\text{loc}}$) :
$$\sum_{\ell : (\ell,k) \in \Phi_a} y^{a}_{\ell,k} \;+\; \rho_{k,a} \;=\; R_{k,a}$$

**Cas 2 — acide clarifié** :
$$y^{cl}_{k} + \rho_{k,\text{54cl}} = R_{k,\text{54cl}}$$

**Cas 3 — besoin `acid_54_dec_total`** (substituabilité) :
$$\boxed{\;y^{coc}_{k} + y^{deccl}_{k} + \rho_{k,\text{dectot}} = R_{k,\text{dectot}}\;}$$

**Français.** Chaque besoin est couvert par la somme des livraisons de sources autorisées ;
$\rho$ mesure ce qui manque.

> **Le cas 3 est le plus intéressant mathématiquement.** Le besoin en « acide 54 de qualité
> décadmiée » ne porte **pas** sur un produit, mais sur une **propriété**. Deux produits
> physiquement distincts (CoC et DEC_CL) la possèdent et sont donc **substituables**.
> Formellement, la contrainte porte sur la **somme** de deux variables, pas sur chacune.
> C'est exactement pourquoi ces deux produits partagent le même bac IR11 : ils sont
> interchangeables du point de vue du client.

### (C15) Contrainte de qualité d'IR11 — production obligatoire de DEC_CL

$$\eta^{cl}\sum_{m} x^{dec}_{\sigma^{-1}(m)}
\;\ge\; \alpha \left( \sum_{m} G_m + \eta^{cl}\sum_{m} x^{dec}_{\sigma^{-1}(m)} \right)$$

soit, après réarrangement (forme linéaire à implémenter) :

$$(1-\alpha)\,\eta^{cl}\sum_{m} x^{dec}_{\sigma^{-1}(m)} \;\ge\; \alpha \sum_{m} G_m$$

**Français.** Le DEC_CL doit représenter au moins une fraction $\alpha$ de ce qui entre dans
IR11.
**Justification métier.** Le dossier affirme qu'IR11 doit contenir un mélange de CoC et de
DEC_CL, sous peine de dégradation de la qualité.
**Justification mathématique.** Sans cette contrainte, l'optimiseur ne produirait **jamais**
de DEC_CL : la cocristallisation systématique (2 431 t/j) couvre déjà à elle seule tout le
besoin en `dec_total` (987 t/j). Produire du DEC_CL est pour lui un coût sans bénéfice.
Voir décision **D-09** et question **Q2**.
**Remarque.** $\alpha = 0$ désactive proprement la contrainte.

### (C16) Transferts semi-continus

$$\tau^{\min}\, b_{\ell\ell'} \;\le\; t_{\ell\ell'} \;\le\; \tau^{\max}\, b_{\ell\ell'}
\qquad \forall (\ell,\ell') \in \Gamma$$

**Démonstration de correction.**
- Si $b = 0$ : $0 \le t \le 0$, donc $t = 0$.
- Si $b = 1$ : $\tau^{\min} \le t \le \tau^{\max}$.

Ces deux cas sont exactement ceux souhaités, et aucun autre n'est atteignable. ∎

### (C17) Bornes des stocks d'acide 54

$$Z^{\min}_{54} - \nu^{-}_{54,m} \;\le\; S^{ncl}_m \;\le\; Z^{\max}_{54} + \nu^{+}_{54,m}$$

### (C18) Interconnexions

$$y^{a}_{\ell,k} = 0 \qquad \forall (\ell,k) \notin \Phi_a$$

**Mise en œuvre.** On ne crée simplement pas la variable. C'est plus efficace que de la
créer puis de la contraindre à zéro.

### (C19) Non-négativité

Toutes les variables sont $\ge 0$, sauf les binaires qui sont dans $\{0,1\}$.

---

## 6. Récapitulatif des contraintes

| N° | Nom | Type | Nombre | Organe industriel |
|---|---|---|---:|---|
| C1 | Partage production 29 | égalité | 6 | filtration |
| C2 | Choix du niveau de décadmiation | égalité | 5 | filtres |
| C3 | Faisabilité décadmiation | ≤ | 5 | filtres |
| C4 | Charge de concentration | égalité souple | 5 | échelons |
| C4b | Alimentation des échelons CoC | ≥ | 5 | échelons |
| C5 | Limite acide dec en concentration | ≤ | 5 | échelons |
| C6 | NCL disponible | égalité | 5 | échelons |
| C7 | **Bilan acide 29 std** | égalité | 6 | cuves 29 |
| C8 | Bilan acide 29 dec | égalité | 6 | cuves 29 |
| C9 | Capacité cuves 29 | ≤ / ≥ | 12 | cuves 29 |
| C10 | Bilan acide 54 NCL | égalité | 5 | cuves 54 |
| C11 | **Capacité décanteurs** | ≤ | 4 | décanteurs |
| C12 | Bilan IR12 | égalité | 1 | bac IR12 |
| C13 | Bilan IR11 | égalité | 3 | bac IR11 |
| C14 | Satisfaction demande | égalité | ≈ 15 | expédition |
| C15 | Qualité IR11 | ≥ | 1 | bac IR11 |
| C16 | Transferts semi-continus | ≤ / ≥ | 28 | conduites |
| C17 | Bornes stocks 54 | ≤ / ≥ | 10 | cuves 54 |
| C18 | Interconnexions | structurel | — | tuyauterie |
| C19 | Non-négativité | bornes | toutes | physique |

---

## 7. Fonction objectif

### 7.1 ⭐ Pourquoi l'objectif du dossier est dégénéré

Le dossier demande :
> *« Maximiser le total d'acide livré à tous les consommateurs »*

tout en imposant :
> *« Toutes les demandes doivent être exactement satisfaites »*

**Proposition.** *Sous l'hypothèse que la satisfaction de la demande est une contrainte
d'égalité, l'objectif « maximiser le total livré » est constant sur le domaine réalisable.*

**Démonstration.** Notons $Y$ le total livré. Par la contrainte (C14) avec $\rho \equiv 0$ :
$$Y \;=\; \sum_{k,a} \Big(\text{livraisons vers } k \text{ en acide } a\Big)
\;=\; \sum_{k,a} R_{k,a}$$
Or $R_{k,a}$ est un **paramètre**. Donc $Y = \text{const}$ pour **toute** solution réalisable.
La fonction objectif ne dépend d'aucune variable ; son gradient est nul. ∎

**Conséquences pratiques, et elles sont graves :**
1. Le solveur renvoie un **sommet arbitraire** du polyèdre réalisable.
2. Deux exécutions peuvent donner des plans **très différents** (transferts inutiles,
   décadmiation excessive) avec la **même** valeur d'objectif.
3. Le résultat perd toute crédibilité auprès des exploitants : « pourquoi le logiciel me
   dit-il de transférer 400 t aujourd'hui et rien demain, alors que rien n'a changé ? »

> **C'est l'apport intellectuel principal du stage.** Identifier ce défaut, le démontrer,
> et le corriger proprement est exactement ce qu'on attend d'un ingénieur en optimisation.
> Ce point mérite une section entière du rapport.

### 7.2 La correction : optimisation lexicographique à 3 niveaux

**Principe.** On ordonne les objectifs par priorité **stricte**. On optimise $f_1$ ; on fige
son optimum par une contrainte ; on optimise $f_2$ sous cette contrainte ; puis $f_3$.

Aucun compromis n'est possible entre niveaux : gagner sur $f_2$ ne justifie **jamais** de
perdre sur $f_1$. C'est exactement la logique industrielle — servir le client prime sur
tout le reste.

### 7.3 Niveau 1 — Servir les clients

$$\boxed{\;f_1 \;=\; \sum_{k \in \mathcal{K}} \sum_{a \in \mathcal{A}} \pi_{k,a}\; \rho_{k,a}
\;\longrightarrow\; \min\;}$$

où $\pi_{k,a} \ge 1$ est un **poids de priorité commerciale** (par défaut 1 partout ;
on peut privilégier un client contractuel).

**Équivalence avec l'objectif demandé.** Puisque
$\sum_{k,a}\big(\text{livré}\big) = \sum_{k,a} R_{k,a} - \sum_{k,a}\rho_{k,a}$
et que le premier terme est constant, minimiser $f_1$ (à poids unitaires) revient
**exactement** à maximiser le total livré. **Le niveau 1 est donc une généralisation stricte
de ce que demande le dossier.**

**Ce qu'il apporte en plus.** Si le système ne peut pas tout servir, le modèle ne répond pas
« Infeasible » : il sert au mieux et **indique précisément ce qui manque et pour qui**.
C'est ce qui rend l'outil réellement utilisable en exploitation.

### 7.4 Niveau 2 — Respecter les bandes de stock

$$f_2 \;=\; \sum_{\text{cuves}} \left( \nu^{+} + \nu^{-} \right) \;\longrightarrow\; \min$$

**Français.** Minimiser les débordements et les sous-remplissages.

**Justification industrielle.** Une cuve qui déborde arrête la ligne amont ; une cuve qui se
vide arrête la ligne aval. Ce sont des incidents graves, mais **moins graves que de ne pas
livrer un client** — d'où leur place au niveau 2.

**Justification technique.** Comme montré en `04` §8, la borne d'IR11 est probablement
**intrinsèquement violable** dans le scénario de référence. Une contrainte dure rendrait le
modèle infaisable et donc muet. Le passage en contrainte molle transforme un échec en
**diagnostic chiffré**.

### 7.5 Niveau 3 — Bien exploiter

$$f_3 \;=\; c_t \sum_{(\ell,\ell') \in \Gamma} t_{\ell\ell'}
\;+\; c_b \sum_{(\ell,\ell') \in \Gamma} b_{\ell\ell'}
\;+\; c_d \sum_{\ell} d_\ell
\;+\; c_s \sum_{\text{cuves}} \left| S - S^{\text{cible}} \right|
\;\longrightarrow\; \min$$

| Terme | Ce qu'il pénalise | Justification industrielle |
|---|---|---|
| $c_t \sum t$ | le **volume** transféré | énergie de pompage, usure des conduites |
| $c_b \sum b$ | le **nombre** de transferts | chaque opération mobilise un opérateur |
| $c_d \sum d$ | la décadmiation | réactifs, capacité de filtration consommée |
| $c_s \sum \lvert S - S^{\text{cible}} \rvert$ | l'écart au milieu de bande | robustesse pour le lendemain |

**Cible de stock.** $S^{\text{cible}} = \tfrac{1}{2}(Z^{\min} + Z^{\max})$ : le milieu de la
bande de sécurité, position qui laisse le maximum de marge dans les deux sens.

**Linéarisation de la valeur absolue.** $|S - S^{\text{cible}}|$ n'est pas linéaire. On pose
$g^{+}, g^{-} \ge 0$ avec :
$$S - S^{\text{cible}} = g^{+} - g^{-}, \qquad |S - S^{\text{cible}}| \;\to\; g^{+} + g^{-}$$

*Pourquoi cela fonctionne :* comme on **minimise** $g^{+} + g^{-}$, l'optimum ne rendra
jamais les deux simultanément positifs (on pourrait les diminuer tous deux de la même
quantité sans changer la différence). À l'optimum, l'un des deux est donc nul, et
$g^{+} + g^{-} = |S - S^{\text{cible}}|$. ∎

> **C'est le niveau 3 qui donne la « très grande qualité » de solution demandée.**
> Il transforme un plan simplement réalisable en un plan **sobre et robuste** : pas de
> transfert inutile, pas de décadmiation superflue, et des cuves laissées en bonne position
> pour le lendemain.

### 7.6 Mise en œuvre de la résolution lexicographique

```
ÉTAPE 1 :  minimiser f₁                     →  f₁*
ÉTAPE 2 :  ajouter la contrainte f₁ ≤ f₁* + ε₁
           minimiser f₂                      →  f₂*
ÉTAPE 3 :  ajouter la contrainte f₂ ≤ f₂* + ε₂
           minimiser f₃                      →  solution finale
```

Les $\varepsilon_i$ (de l'ordre de $10^{-6}$) absorbent les erreurs d'arrondi du solveur.
Sans eux, la contrainte $f_1 = f_1^\star$ peut rendre l'étape 2 numériquement infaisable.

**Alternative de secours : la somme pondérée.**
$$f = M_1 f_1 + M_2 f_2 + f_3, \qquad M_1 \gg M_2 \gg 1$$
Plus rapide (une seule résolution), mais **fragile** : si les ordres de grandeur sont mal
choisis, la hiérarchie se brise silencieusement, et les erreurs numériques s'amplifient.
**On retient la résolution en 3 passes** ; la somme pondérée servira de secours si le temps
de calcul devient un problème — ce qui est improbable ici.

---

## 8. Hypothèses du modèle

> **Toute hypothèse est un risque assumé.** Elle doit être écrite, justifiée, et testable.

| N° | Hypothèse | Justification | Risque | Levier |
|---|---|---|---|---|
| **H1** | L'unité est la tonne de P₂O₅ | 3 preuves convergentes (`04` §2) | 🟢 faible | Q4 |
| **H2** | Modèle mono-période (1 jour) | toutes les données sont journalières | 🟢 faible | — |
| **H3** | L'acide dec ne passe pas par les échelons de cocristallisation | un CoC ne peut être clarifié | 🟢 faible | Q8 |
| **H4** | IR11 initial est entièrement du CoC | hypothèse la plus défavorable (prudente) | 🟡 moyen | — |
| **H5** | Les boues de CoC vont au stock 29 std | `PROCESS_GUIDE` (référence définitive) | 🟡 moyen | Q5 |
| **H6** | La limite décanteur porte sur l'entrée | mention « before yield » + physique | 🟢 faible | — |
| **H7** | $\tau^{\max} = 1000$ t | valeur d'attente, cohérente en ordre de grandeur | 🟠 élevé | Q1 |
| **H8** | $\alpha = 0{,}15$ | valeur d'attente, aucun fondement métier | 🔴 très élevé | Q2 |
| **H9** | Bornes de stock recalculées | méthode validée sur l'acide 54 | 🟠 élevé | Q3 |
| **H10** | Les bornes hautes sont molles | sinon le modèle est infaisable (`04` §8) | 🟡 moyen | — |
| **H11** | Rendements déterministes | données de procédé stabilisées | 🟢 faible | — |
| **H12** | Pas de délai de transport | horizon journalier ≫ temps de transfert | 🟢 faible | — |

**Les hypothèses H7, H8 et H9 feront l'objet d'une analyse de sensibilité en Phase 5.**
C'est la réponse méthodologique correcte à une donnée incertaine : ne pas la deviner, mais
**mesurer son influence** sur la solution.

---

## 9. Traçabilité contrainte ↔ réalité industrielle

Tableau à reprendre tel quel dans le rapport de stage.

| Réalité de l'atelier | Traduction mathématique |
|---|---|
| « La production d'acide 29 nous est imposée » | $P_\ell$ paramètre |
| « On allume 1 ou 2 filtres, pas 1,4 » | $d_\ell \in \{0,750,1500\}$, binaires |
| « Concentrer conserve le P₂O₅ » | $\eta^{conc} = 1$ |
| « Les échelons tournent selon le planning » | $\Pi_m$ paramètre, contrainte (C4) en **égalité** |
| « La cocristallisation traite tout, tout le temps » | $G_m$ paramètre, aucune variable |
| « L'acide décadmié est clarifié immédiatement » | substitution $u^{dec}_m \equiv x^{dec}_{\sigma^{-1}(m)}$ |
| « Les 2 décanteurs font 1 000 t/jour » | (C11) |
| « Les boues, on les recycle » | termes de retour dans (C7) |
| « EMAPHOS nous renvoie 40 % » | terme $\beta_\ell$ dans (C7) |
| « Toutes les lignes ne sont pas reliées » | $\Gamma$, $\Phi_a$ ; variables non créées |
| « On ne transfère pas 4 tonnes » | (C16), semi-continue |
| « La cuve ne doit ni déborder ni se vider » | (C9), (C17), molles |
| « IR11 doit contenir un mélange » | (C15) |
| « Le client d'abord » | niveau 1 de l'objectif |
| « Sans gaspiller » | niveau 3 de l'objectif |

---

## 10. Ce qu'il faut vérifier une fois le modèle résolu

Liste de contrôle pour la Phase 5.

- [ ] Statut du solveur = `Optimal`
- [ ] $f_1 = 0$ (toutes les demandes servies) — sinon **expliquer pourquoi**
- [ ] Bilan matière fermé sur les **19 nœuds** (tolérance 0,1 %)
- [ ] Toutes les décadmiations dans $\{0, 750, 1500\}$
- [ ] Tous les transferts nuls ou $\ge 100$ t
- [ ] Aucune capacité de décanteur dépassée
- [ ] Stocks finaux $\ge 0$ partout
- [ ] Contrainte de qualité d'IR11 respectée
- [ ] Identifier les **contraintes actives** (goulots d'étranglement)
- [ ] Analyse de sensibilité sur $\alpha$, $\tau^{\max}$, $Z^{\max}_{29}$


---

## 11. Ce que le modèle a effectivement donné

La résolution du scénario de référence est décrite en détail dans
`09_RESULTATS.md`. En résumé :

| Contrôle du §10 | Résultat |
|---|---|
| Statut du solveur | ✅ **Optimal** (0,06 s) |
| $f_1 = 0$ | ✅ 100 % de la demande servie |
| Bilans matière sur les 19 nœuds | ✅ 86 contrôles indépendants réussis |
| Décadmiations discrètes | ✅ 750 t sur 13XY, rien ailleurs |
| Transferts nuls ou ≥ 100 t | ✅ trois transferts, dont un pile à 100 t |
| Capacités de décanteurs | ✅ 48 % et 72 % au plus |
| Stocks positifs | ✅ partout |
| Qualité d'IR11 | ✅ contrainte active, 429 t de DEC_CL produites |
| Contraintes actives | 🔴 IR11 dépassé de 1 016 t ; cuves d'acide 29 saturées sur 3 lignes |
| Sensibilité | ✅ menée sur $\alpha$, $\tau^{\max}$ et la configuration CoC |

**Le point le plus important :** les deux violations résiduelles ne viennent d'aucune
mauvaise décision d'exploitation — le modèle a fait au mieux. Elles viennent de la
**configuration** de la cocristallisation, qui est un paramètre. Réduire de 4 à 1 le
nombre d'échelons de 14EXT affectés au CoC les résorbe intégralement.

C'est exactement ce qu'un modèle d'optimisation doit produire : non pas seulement un plan,
mais le **diagnostic** de ce qui empêche le plan d'être bon.
