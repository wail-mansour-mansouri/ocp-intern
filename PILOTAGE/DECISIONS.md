# REGISTRE DES DÉCISIONS TECHNIQUES

> Chaque décision suit le même gabarit : **contexte → options → décision → justification →
> conséquences → réversibilité.** Aucune décision n'est prise sans justification.

---

## D-01 — L'unité de compte du modèle est la tonne de P₂O₅

**Contexte.** Les documents parlent de « tonnes » sans jamais préciser tonnes de quoi.
Or le procédé concentre de l'acide à 29 % en acide à 54 %, et les documents affirment un
« rendement massique de 100 % (1 t P29 → 1 t P54) », ce qui est faux pour la masse d'acide.

**Options.**
1. Tonnes d'acide marchand (masse totale de la solution).
2. Tonnes de P₂O₅ (masse de pentoxyde de phosphore contenu).

**Décision.** Option 2 : **tonne de P₂O₅ par jour**.

**Justification.** Trois preuves indépendantes et convergentes :
1. *Preuve par les formules de conversion.* `get_vol_29(h) = 174,11·h·0,33` où
   `0,33 ≈ P2O5_29 × DENSITY_29 = 0,26 × 1,270 = 0,3302`. La conversion inclut donc
   explicitement le titre en P₂O₅. Idem pour l'acide 54 : `0,83 = 0,50 × 1,66` exactement.
   La fonction ne rend pas des tonnes d'acide, elle rend des tonnes de P₂O₅.
2. *Preuve par la conservation.* La concentration élimine de l'eau. La masse d'acide n'est
   pas conservée (facteur ≈ 0,26/0,50 = 0,52), mais la masse de P₂O₅ l'est. Le
   « rendement 100 % » n'est vrai que si l'unité est le P₂O₅.
3. *Preuve par l'industrie.* EMAPHOS, consommateur du système, est officiellement
   dimensionné à 140 000 → 280 000 **t P₂O₅/an**, soit ≈ 380 → 770 t P₂O₅/jour. La demande
   de 700 t/j du scénario tombe exactement dans cette plage.

**Conséquences.** Tous les bilans matière s'écrivent en P₂O₅. Le rendement de concentration
vaut exactement 1. Les rendements de clarification (0,90) et de cocristallisation (0,80)
s'interprètent comme des **taux de récupération du P₂O₅**, le complément partant dans les
boues — ce qui est physiquement cohérent.

**Réversibilité.** Élevée : une constante de conversion globale suffirait à changer d'unité.
→ À faire confirmer par l'encadrant (question Q4).

---

## D-02 — Le modèle est mono-période (une journée)

**Contexte.** Toutes les données sont journalières : production t/j, heures de marche sur
24 h, décadmiation en t/j, capacité décanteur en t/j.

**Décision.** Modèle **statique sur un horizon d'une journée**, avec stock initial donné et
stock final calculé.

**Justification.** Aucune donnée du dossier n'est indexée par le temps. Introduire un
horizon multi-périodes exigerait des prévisions de demande que nous n'avons pas, et
multiplierait la taille du problème sans support de données.

**Conséquences.** Le stock final joue le rôle de variable d'état transmise au jour suivant :
sa qualité (position dans la bande de sécurité) devient un critère du niveau 3 de
l'objectif.

**Réversibilité.** Moyenne. Une extension multi-période est une perspective naturelle du
rapport de stage (chapitre « Perspectives »).

---

## D-03 — Formulation en programmation linéaire mixte (MILP)

**Contexte.** Deux familles de décisions sont intrinsèquement discrètes :
- les niveaux de décadmiation appartiennent à {0, 750, 1500} ;
- un transfert interzone est soit nul, soit ≥ 100 t (quantité minimale d'expédition).

**Options.** (a) relaxation continue ; (b) MILP ; (c) métaheuristique.

**Décision.** **MILP**, avec variables binaires pour le choix de niveau et pour
l'activation des transferts (formulation *semi-continue*).

**Justification.** La relaxation continue produirait des solutions physiquement
irréalisables (décadmier 312 t est impossible : on allume 1 ou 2 filtres, rien d'autre).
La métaheuristique ne garantit pas l'optimalité, or l'énoncé exige explicitement un statut
« Optimal ». Le MILP donne l'optimum global **et** l'exactitude physique. La taille du
problème (≈ 29 binaires) est dérisoire pour un solveur moderne.

**Conséquences.** Solveur CBC (libre) suffisant. Temps de résolution attendu < 1 s.

**Réversibilité.** Élevée.

---

## D-04 — Objectif lexicographique à 3 niveaux

**Contexte.** L'énoncé demande de « maximiser le total d'acide livré » **et** que « toutes
les demandes soient exactement satisfaites ».

**Problème.** Ces deux exigences sont contradictoires au sens de l'optimisation. Si la
satisfaction est une égalité, alors le total livré vaut identiquement la demande totale :
l'objectif est **constant sur tout le domaine réalisable** et ne sélectionne aucune solution.
Le solveur renverrait alors un sommet arbitraire du polyèdre.

**Décision.** Objectif **lexicographique** :
- **Niveau 1** — minimiser la demande non satisfaite (pondérée par priorité) ;
- **Niveau 2** — minimiser les violations des bandes de stock de sécurité ;
- **Niveau 3** — minimiser le coût opératoire (transferts, activations de filtres, écart
  des stocks finaux à leur cible).

**Justification.** Le niveau 1 est **strictement équivalent** à l'objectif demandé : minimiser
le manque revient à maximiser le livré. Il le généralise même au cas infaisable (si le
système ne peut pas tout servir, on sert au mieux au lieu de renvoyer « Infeasible », ce qui
serait inutilisable en exploitation). Les niveaux 2 et 3 lèvent la dégénérescence par des
critères qui ont un sens industriel réel et non par un artifice numérique.

**Conséquences.** Résolution en 3 passes : on optimise le niveau *k*, on fige sa valeur par
une contrainte, on optimise le niveau *k+1*. Alternative implémentable : somme pondérée avec
poids séparés par ordre de grandeur — moins propre, retenue seulement en secours.

**Réversibilité.** Élevée : l'architecture prévoit un module `objective.py` isolé.

---

## D-05 — Les boues de cocristallisation retournent au stock P29 standard

**Contexte.** Les documents se contredisent : `PROCESS_GUIDE` §3.2 et
`REAL_SCENARIO_REFERENCE` disent « retour au stock P29 standard » ; `CORE_FIXED_ELEMENTS`,
`OUTPUT_FORMAT` et `TEST_REFERENCE_OUTPUT` disent « retour au stock P54 NCL ».

**Décision.** Retour au **stock P29 standard** de la ligne amont, avec le point de retour
rendu **paramétrable** dans le code.

**Justification.** `PROCESS_GUIDE.md` se déclare lui-même « référence définitive du procédé
industriel » et précise que toute question sur « comment le procédé doit fonctionner » doit
être tranchée par lui. `REAL_SCENARIO_REFERENCE.md`, qui décrit le scénario que nous devons
reproduire, le confirme. Enfin la simulation détaillée de l'encadrant applique bien ce choix
(« Sludge : 273 t → retourne au stock P29 standard de 13E »). Trois sources concordantes
contre trois sources annexes ou archivées.

**Conséquences.** Le paramétrage coûte 3 lignes de code et rend la question triviale à
retester si l'encadrant tranche autrement. → Question Q5.

---

## D-06 — La limite décanteur de 1 000 t/j porte sur l'**entrée**

**Contexte.** Contradiction interne : `PROCESS_GUIDE` §3.1 dit « 1 000 t/j par ligne
(*before yield*) », donc en entrée ; mais l'exemple §3.4 calcule « envoyer 1 000/0,9 = 1 111 t
en clarification → ≈ 1 000 t de DEC CL », ce qui place la limite en **sortie**.

**Décision.** La limite porte sur le **débit entrant** aux décanteurs :
`u_ncl + u_dec ≤ 1000`.

**Justification.** (i) C'est la lecture physique : un décanteur est dimensionné par le débit
qu'il **reçoit**, pas par ce qu'il restitue. (ii) La mention explicite « *before yield* » est
sans ambiguïté. (iii) Les règles de validation du dossier vérifient
`manual_clarification[line] ≤ 1000`, où `manual_clarification` désigne la quantité **envoyée**
en clarification. Deux sources sur trois, et l'argument physique, convergent.

**Conséquences.** Capacité maximale de production de CL par ligne : 900 t/j de sortie.

---

## D-07 — Les bornes de stock sont recalculées depuis la géométrie des cuves

**Contexte.** `CORE_FIXED_ELEMENTS.md` annonce `Z_MIN_29 ≈ 364,5` et `Z_MAX_29 ≈ 1 530,7`.
Le recalcul de sa propre formule donne 229,8 et 965,3 : les valeurs annoncées sont
**toutes deux surestimées d'un facteur 1,586**. En revanche les bornes de l'acide 54
(473,4 et 1 483,6) sont correctes au dixième près.

**Décision.** Recalculer systématiquement les bornes par
`Z = get_vol(nb_cuves × hauteur) `, et ne jamais recopier une valeur numérique du document.

**Justification.** La méthode de calcul est validée par le cas de l'acide 54, où elle
reproduit exactement les chiffres du document. Elle est donc correcte, et l'écart sur
l'acide 29 est une erreur de saisie. De plus, la cohérence interne l'exige : les stocks
**initiaux** sont produits par `get_vol_29`. Comparer un stock calculé avec `get_vol_29` à
une borne obtenue autrement n'a aucun sens dimensionnel.

**Conséquences.** Les bornes deviennent nettement plus serrées (965 au lieu de 1 531), donc
la contrainte de sur-remplissage devient active plus souvent — c'est précisément ce qui
justifie l'existence des transferts interzones. → Question Q3.

---

## D-08 — Les hauteurs de cuve fournies sont des hauteurs **cumulées** sur 2 cuves

**Contexte.** `REAL_SCENARIO_REFERENCE` donne pour 13AB une hauteur de 13,75 m, alors que
`H_MAX_29` vaut 8,40 m. Une cuve unique ne peut pas contenir 13,75 m.

**Décision.** Interpréter les hauteurs fournies comme la **somme des hauteurs des 2 cuves**
de la ligne, et appliquer `get_vol` directement à cette somme.

**Justification.** `get_vol` est linéaire en *h* : `get_vol(h₁ + h₂) = get_vol(h₁) + get_vol(h₂)`.
Sommer les hauteurs puis convertir équivaut donc exactement à convertir puis sommer.
L'interprétation est cohérente (13,75 ≤ 2 × 8,40 = 16,80) et reproduit au dixième près tous
les stocks initiaux annoncés dans le document.

**Conséquences.** Les bornes s'écrivent avec la hauteur cumulée : `Z_MAX = get_vol(2 × h_max)`.

---

## D-09 — Production obligatoire de DEC_CL modélisée par une contrainte de mélange

**Contexte.** Le document insiste : produire du DEC_CL est **obligatoire** parce que IR11
doit contenir un mélange CoC + DEC_CL, faute de quoi la qualité chute. Mais aucun seuil
chiffré n'est donné. Or, la cocristallisation étant systématique et abondante, l'optimiseur
n'a spontanément aucune raison de produire du DEC_CL : il violerait donc la règle métier.

**Options.**
1. Borne inférieure absolue : `DEC_CL ≥ M` tonnes.
2. Contrainte de proportion : `DEC_CL ≥ α × (entrées totales d'IR11)`.
3. Terme incitatif dans l'objectif (contrainte molle).

**Décision.** Option 2, **contrainte de proportion** avec α paramétrable
(valeur par défaut proposée : α = 0,15).

**Justification.** C'est la seule formulation qui traduit fidèlement l'énoncé : le problème
posé est un problème de **composition du mélange dans IR11**, pas de quantité absolue.
Une borne absolue (option 1) serait arbitraire et deviendrait infaisable les jours de faible
production. Une contrainte molle (option 3) laisserait l'optimiseur l'ignorer dès qu'elle
coûte cher, ce qui contredit le caractère « obligatoire » affirmé par l'énoncé.
La valeur α = 0,15 n'est **pas** une donnée métier : c'est une valeur d'attente explicitement
signalée, à remplacer par le chiffre de l'encadrant. → Question Q2.

**Conséquences.** α = 0 désactive proprement la règle ; le modèle reste utilisable en
attendant la réponse. Une analyse de sensibilité sur α sera menée en Phase 5.

---

## D-10 — Charge de concentration : égalité avec bande de tolérance pénalisée

**Contexte.** L'encadrant, interrogé sur la contrainte (C4), a répondu :
> « Oui la somme doit être égale, c'est normalement rigide, mais on peut avoir des seuils
> de tolérance pour respecter la planification des transferts. »

**Options.**
1. Égalité stricte : `x_std + x_dec = Π`.
2. Inégalité libre dans une bande : `(1−ε)Π ≤ x_std + x_dec ≤ (1+ε)Π`.
3. Bande **et** pénalisation de tout écart.

**Décision.** Option 3 : la bande est autorisée à ±ε (ε = 5 % par défaut, paramétrable),
et tout écart est pénalisé au **niveau 2** de l'objectif, avec un poids supérieur à celui
des violations de bandes de stock.

**Justification.** C'est la seule formulation qui rend fidèlement les deux moitiés de la
réponse. L'option 1 ignore la tolérance accordée. L'option 2 la banalise : l'optimiseur
s'écarterait du plan dès que cela l'arrange, alors que l'encadrant qualifie l'égalité de
« normalement rigide ». En pénalisant, on obtient exactement le comportement voulu — le
modèle **reste à l'égalité stricte** sauf lorsque s'en écarter évite une violation plus
grave. C'est vérifié dans les faits : sur le scénario de référence, la solution optimale
n'utilise pas un gramme de tolérance (test `test_charge_de_concentration_a_l_egalite`).

**Conséquence secondaire, structurante.** Rendre la charge variable a obligé à revoir le
calcul du NCL produit. Si la charge peut s'écarter du plan, la production ne peut plus
être le paramètre `Π_ncl`. La ventilation correcte est :

$$N_m \;=\; \underbrace{x^{std}_\ell}_{\text{acide standard chargé}} \;-\; \underbrace{\Pi^{coc}_m}_{\text{part cocristallisée}}$$

avec la contrainte supplémentaire $x^{std}_\ell \ge \Pi^{coc}_m$ : les échelons
cocristallisants tournent au plan et doivent être alimentés. Quand la charge vaut
exactement le plan, on retrouve bien $N_m = \Pi^{ncl}_m - x^{dec}_\ell$, la formule
initiale. La nouvelle écriture la **généralise** sans la contredire.

**Réversibilité.** Élevée : `tolerance_concentration = 0` restaure l'égalité stricte.

---

## D-11 — Mode optionnel : cocristallisation décidable

**Contexte.** Le cahier des charges présente l'affectation des échelons à la
cocristallisation comme une **configuration subie** : un échelon affecté traite tout ce
qu'il produit, quelle que soit la demande. Le modèle a été construit fidèlement sur cette
base (décision implicite depuis l'itération 1).

L'analyse de sensibilité de l'itération 2 a montré que ce paramètre est **la cause unique**
des deux violations structurelles du scénario de référence : IR11 déborde de 1 016 t/jour et
le stock de 14EXT reste sous sa bande. Aucune décision d'exploitation ne peut les corriger.

**Options.**
1. Ne rien faire : rester fidèle au cahier des charges, signaler le problème.
2. Remplacer le paramètre par une variable de décision.
3. Ajouter un **mode optionnel**, désactivé par défaut.

**Décision.** Option 3 : drapeau `cocristallisation_decidable`, **faux par défaut**.
Quand il est activé, la liste `echelons_cocristallisation` change de sens — elle désigne
alors les échelons *physiquement raccordés* aux unités, et le modèle choisit lesquels
mettre en service, via une binaire $z_e$ par échelon candidat.

**Justification.** Le comportement par défaut doit rester **conforme aux spécifications**
reçues : ce n'est pas au logiciel de décider unilatéralement qu'une règle métier n'en est
pas une. Mais refuser d'explorer la question aurait été tout aussi discutable, puisque
l'analyse désigne ce paramètre comme le seul levier utile. Un mode optionnel réconcilie les
deux : le modèle reste fidèle, et l'étude peut chiffrer ce que coûte la contrainte.

**Linéarité préservée.** Le passage du paramètre à la variable garde le modèle linéaire :

$$\Pi^{coc}_m = \sum_{e} \kappa_e\, z_e, \qquad G_m = \eta^{coc}\,\Pi^{coc}_m$$

Toutes les contraintes qui utilisaient $\Pi^{coc}_m$ (C4b, C6, C7, C13, C15) restent affines.
La contrainte C5 a dû être généralisée : la capacité des échelons non cocristallisants vaut
désormais $\Pi_m - \Pi^{coc}_m$ au lieu du paramètre $\Pi^{ncl}_m$.

**Résultat mesuré.**

| Mode | CoC produit | Dépassement IR11 | Niveau 2 | Niveau 3 |
|---|---:|---:|---:|---:|
| subi (défaut) | 2 431,3 | 1 016,0 | 1 268,3 | 3 111,9 |
| **décidable** | **472,0** | **0,0** | **0,0** | **2 125,2** |

Le mode décidable **résorbe intégralement** les deux violations, tout en servant 100 % de la
demande et en réduisant le coût opératoire. Coût : 8 variables binaires supplémentaires.

**Limite à signaler.** Le modèle étant mono-période, il n'a aucune raison de reconstituer le
stock d'IR11 : celui-ci étant initialement rempli à 86,5 %, l'optimiseur réduit fortement la
cocristallisation pour le ramener vers le milieu de sa bande. Sur un horizon multi-période,
l'arbitrage serait différent. **Ce résultat chiffre un potentiel, il ne constitue pas une
consigne d'exploitation.**

**Réversibilité.** Totale : le drapeau est faux par défaut, et un test vérifie qu'aucune
variable binaire de cocristallisation n'est alors créée.
