# QUESTIONS À POSER À L'ENCADRANT

> Formulées pour être posées telles quelles. Chaque question indique **pourquoi** elle se
> pose, **ce que nous avons fait en attendant**, et **l'impact** de la réponse.
> Aucune de ces questions ne bloque l'avancement : toutes sont traitées comme des
> paramètres explicites du modèle.

---

## Q1 — Quelle est la borne maximale d'un transfert interzone ? ⚠️ *priorité haute*

**La question.**
> « Le document précise qu'un transfert interzone d'acide 29 doit respecter un minimum
> (100 t) et un maximum, mais la valeur du maximum n'apparaît nulle part. Quelle est-elle ?
> Est-elle la même pour tous les couples de lignes, ou dépend-elle de la liaison
> (diamètre de conduite, débit de pompe) ? »

**Pourquoi elle se pose.** Le script `archive/test_transfers.py` importe bien une constante
`MAX_TRANSFER` depuis `core_fixed_elements`, et l'utilise dans son algorithme. Mais
`CORE_FIXED_ELEMENTS.md` ne définit que les trois minima (100 t) et jamais le maximum.
La donnée existe donc dans le code d'origine, mais n'a pas été transcrite dans la
documentation qui nous a été remise.

**Ce que nous faisons en attendant.** Paramètre `TAU_MAX` avec valeur par défaut **1 000 t**,
uniforme sur toutes les liaisons autorisées. Cette valeur est cohérente avec l'ordre de
grandeur des déséquilibres à corriger (quelques centaines de tonnes) et avec la remarque du
`PROCESS_GUIDE` (« on ne peut pas proposer d'envoyer 4 000 t de AB vers CD »).

**Impact de la réponse.** Modéré. Une borne trop lâche autorise des transferts irréalistes ;
une borne trop serrée peut rendre le rééquilibrage impossible et déclencher des violations
de stock. Une analyse de sensibilité est prévue en Phase 5.

---

## Q2 — Comment quantifier l'obligation de produire du DEC_CL ? ⚠️ *priorité haute*

**La question.**
> « Le guide indique que la production de DEC_CL est obligatoire, car IR11 doit contenir un
> mélange de CoC et de DEC_CL — sans quoi la qualité de l'acide baisse. Comment cette
> obligation se traduit-elle en chiffres ? S'agit-il d'un tonnage minimal quotidien, d'une
> proportion minimale de DEC_CL dans IR11, ou d'un ratio cible CoC/DEC_CL ? »

**Pourquoi elle se pose.** C'est le seul endroit du dossier où une règle est qualifiée
d'obligatoire sans être chiffrée. Or elle est décisive : la cocristallisation systématique
produit à elle seule ≈ 2 430 t/j de CoC dans le scénario réel, pour un besoin en
`acid_54_dec_total` de seulement ≈ 987 t/j. Sans contrainte chiffrée, l'optimiseur ne
produira **jamais** de DEC_CL (c'est un coût sans bénéfice pour lui) et violera la règle
métier — exactement le risque que le document anticipe.

**Ce que nous faisons en attendant.** Contrainte de proportion sur les **entrées** d'IR11 :
la part de DEC_CL doit valoir au moins α, avec α = 0,15 par défaut (valeur d'attente
signalée comme telle, sans prétention métier). Voir décision **D-09**.

**Impact de la réponse.** Fort. Cette contrainte pilote directement le niveau de
décadmiation, donc la charge des décanteurs, donc la capacité de clarification restante
pour produire du CL. C'est le couplage le plus fin du modèle.

---

## Q3 — Quelle est la vraie capacité de stockage d'acide 29 par ligne ?

**La question.**
> « Deux valeurs incompatibles figurent dans le dossier pour la capacité des cuves d'acide 29.
> La géométrie (section 174,11 m², hauteur max 8,40 m, 2 cuves, titre 26 %, densité 1,270)
> donne environ 965 t de P₂O₅ par ligne. Mais le document annonce par ailleurs 2 600 t par
> ligne (2 × 1 300 t). Laquelle retenir ? Les 1 300 t par cuve sont-elles exprimées en tonnes
> d'acide marchand plutôt qu'en tonnes de P₂O₅ ? »

**Pourquoi elle se pose.** Écart d'un facteur 2,7 — il ne s'agit pas d'un arrondi. De plus,
`CORE_FIXED_ELEMENTS.md` annonce `Z_MAX_29 ≈ 1 530,7 t`, alors que le recalcul de **sa propre
formule** donne 965,3 t (facteur 1,586 d'écart). Trois valeurs pour une même grandeur.
Note : la même formule appliquée à l'acide 54 reproduit exactement les valeurs du document,
ce qui indique que la méthode est bonne et que l'erreur est localisée sur l'acide 29.

**Ce que nous faisons en attendant.** Recalcul systématique depuis la géométrie
(décision **D-07**), soit `Z_MIN_29 = 229,8` et `Z_MAX_29 = 965,3` t de P₂O₅ par ligne.
Aucune valeur numérique n'est recopiée du document.

**Impact de la réponse.** Fort sur le comportement du modèle. Avec des bornes serrées, les
dépassements sont fréquents et les transferts interzones deviennent indispensables — ce qui
donne d'ailleurs tout leur sens aux contraintes de transfert du dossier.

---

## Q4 — Confirmation de l'unité : tonne de P₂O₅ ou tonne d'acide ?

**La question.**
> « Nous avons conclu que toutes les grandeurs du modèle sont exprimées en tonnes de P₂O₅
> et non en tonnes d'acide marchand, car les fonctions de conversion des cuves intègrent le
> titre (0,26 et 0,50) et parce que le rendement de concentration de 100 % n'est vrai que
> pour le P₂O₅. Pouvez-vous le confirmer ? »

**Pourquoi elle se pose.** C'est l'hypothèse la plus structurante de tout le travail. Si elle
est fausse, tous les bilans matière doivent être réécrits avec un facteur de conversion entre
les niveaux 29 % et 54 %.

**Ce que nous faisons en attendant.** Hypothèse retenue et documentée (décision **D-01**),
avec trois preuves indépendantes convergentes. Confiance élevée.

**Impact de la réponse.** Critique, mais le risque d'erreur est faible.

---

## Q5 — Où retournent les boues de cocristallisation ?

**La question.**
> « Le guide du procédé indique que les 20 % de boues de cocristallisation retournent au
> stock d'acide 29 standard de la ligne amont, mais d'autres documents du dossier indiquent
> un retour au stock d'acide 54 NCL. Laquelle des deux destinations est la bonne ? »

**Pourquoi elle se pose.** Contradiction explicite entre documents (voir anomalie A-05).
La destination change le bilan matière de deux nœuds différents.

**Ce que nous faisons en attendant.** Retour au **stock P29 standard**, conformément au
`PROCESS_GUIDE.md` qui se déclare référence définitive, et à la simulation détaillée de
l'encadrant qui applique ce choix. Le point de retour est un **paramètre** du code
(décision **D-05**), donc basculable instantanément.

**Impact de la réponse.** Modéré et parfaitement circonscrit.

---

## Questions secondaires (à poser si l'occasion se présente)

- **Q6** — Le fichier `config/quality_profiles_v2.json` est référencé partout mais absent du
  dossier. Peut-on l'obtenir ? Nous le reconstruisons pour l'instant à partir des
  coefficients dispersés dans `REAL_SCENARIO_REFERENCE.md`.
- **Q7** — Le format Excel attendu comporte-t-il 5 feuilles (`OUTPUT_FORMAT.md`) ou
  7 feuilles (`archive/TEST_REFERENCE_OUTPUT.md`) ? Nous partons sur **5**, le document
  d'archive étant marqué comme obsolète.
- **Q8** — Quand une ligne d'acide 29 décadmie, l'acide décadmié destiné à la concentration
  passe-t-il par des échelons dédiés ? Nous supposons qu'il n'emprunte pas les échelons
  affectés à la cocristallisation (hypothèse H3).
- **Q9** — Les capacités d'échelon (250, 300, 420, 590) sont annotées « tonnes/heure » mais
  la formule `P54 = C × h / 24` implique des **tonnes/jour**. Confirmation ?
- **Q10** — Existe-t-il un coût ou une préférence entre les lignes (énergie, main-d'œuvre)
  qui permettrait d'affiner le niveau 3 de la fonction objectif ?
