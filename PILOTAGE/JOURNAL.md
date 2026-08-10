# JOURNAL DES ITÉRATIONS

> Une entrée par séance de travail. Sert à retrouver « pourquoi on a fait ça, ce jour-là ».

---

## Itération 1 — 2026-08-08 — Cadrage, compréhension, formalisation

### Objectif de la séance
Prendre connaissance du dossier remis par l'encadrant, comprendre le sujet, et poser le
modèle mathématique.

### Travail réalisé

**1. Dépouillement du dossier.**
9 documents lus intégralement (≈ 4 200 lignes). Le dossier décrit un système de production
et de distribution d'acide phosphorique : 6 lignes d'acide 29 %, 5 lignes d'acide 54 %,
3 procédés de traitement, 2 stockages centraux, 9 consommateurs.

**2. Enrichissement du contexte.**
Recherche documentaire sur le site de Jorf Lasfar. Résultat déterminant : EMAPHOS est
dimensionné en **tonnes de P₂O₅ par an** (140 000 → 280 000 t P₂O₅/an). Cela a permis de
trancher une question fondamentale que les documents n'explicitent nulle part.

**3. Découverte structurante : l'unité du modèle.**
Toutes les grandeurs du système sont en **tonnes de P₂O₅**, pas en tonnes d'acide.
Preuve : les fonctions de conversion `get_vol_29` et `get_vol_54` contiennent le facteur
de titre P₂O₅ (0,26 et 0,50). Conséquence : le « rendement 100 % » de la concentration
29 % → 54 % devient évident (le P₂O₅ se conserve, l'eau part). Sans cette clé, le modèle
paraît violer la conservation de la masse. Détail dans `docs-helper/04`, §2.

**4. Vérification arithmétique systématique.**
Toutes les valeurs dérivées des documents ont été recalculées par script indépendant.
**11 anomalies** trouvées, dont 4 erreurs de calcul franches :
- production P54 totale du scénario réel : **6 981,7** et non 6 636 (écart 5,2 %) ;
- bornes de stock P29 : `Z_MAX_29` vaut **965,3** et non 1 530,7 (écart 59 %) ;
- stock initial IR12 : **3 821,6** et non 4 004,1 (écart 4,8 %) ;
- capacité de stockage P29 : la géométrie donne 965 t, le document affirme 2 600 t.
Toutes consignées avec arbitrage dans `docs-helper/06`.

**5. Analyse critique de la fonction objectif.**
Les documents demandent de « maximiser le total d'acide livré » tout en imposant que
« toutes les demandes soient exactement satisfaites ». Ces deux exigences sont
**incompatibles au sens de l'optimisation** : si la demande est une égalité, le total livré
est une constante et l'objectif ne discrimine plus aucune solution. Démonstration en
2 lignes dans `docs-helper/05`, §7.1.

**6. Proposition d'un objectif lexicographique à 3 niveaux.**
Il généralise strictement l'objectif demandé (niveau 1 ≡ maximiser les livraisons) tout en
levant la dégénérescence par des critères opératoires réels (niveaux 2 et 3).

**7. Formalisation complète du modèle.**
8 ensembles, 23 familles de paramètres, 9 familles de variables, 19 familles de
contraintes. Chaque contrainte est reliée à son organe industriel.

### Décisions prises
Consignées dans `DECISIONS.md` (D-01 à D-09). Les plus structurantes :
- **D-01** : l'unité de tout le modèle est la tonne de P₂O₅ ;
- **D-04** : objectif lexicographique à 3 niveaux plutôt que maximisation simple ;
- **D-05** : formulation MILP (les niveaux de décadmiation sont discrets) ;
- **D-07** : les bornes de cuve sont recalculées depuis la géométrie, pas reprises du doc.

### Points restés ouverts
5 questions pour l'encadrant (`QUESTIONS_ENCADRANT.md`). Aucune ne bloque la Phase 3 :
elles sont traitées comme des paramètres explicites avec valeur par défaut justifiée.

### Prochaine séance
Phase 3 — construction du socle logiciel (constantes, conversions, scénario, profils
qualité) avec ses tests unitaires.

---

## Itération 2 — 2026-08-08 — Implémentation, résolution, validation

### Objectif de la séance
Passer de la formalisation au logiciel : construire le socle, écrire le modèle MILP, le
résoudre, le valider, produire les rapports.

### Élément déclencheur
L'encadrant a répondu sur la contrainte de charge de concentration (C4) :
> « Oui la somme doit être égale, c'est normalement rigide, mais on peut avoir des seuils
> de tolérance pour respecter la planification des transferts. »

Cette réponse a été intégrée sous la forme d'une **bande de tolérance pénalisée**
(décision **D-10**). Vérification a posteriori : sur le scénario de référence, la solution
optimale **n'utilise pas un gramme de tolérance** — le comportement est donc exactement
celui décrit, « normalement rigide ».

Pour les autres questions restées sans réponse, les hypothèses de l'itération 1 ont été
retenues telles quelles, puis leur influence a été **mesurée** par analyse de sensibilité
plutôt que devinée.

### Travail réalisé

**1. Socle logiciel** — `constants`, `units`, `profiles`, `scenario`, `preprocessing`.
Le fichier `quality_profiles.json`, absent du dossier, a été reconstruit à partir des
coefficients dispersés dans le texte, avec la source de chacun.

**2. Modèle MILP** — 170 variables dont 29 binaires, 138 contraintes. Une fonction par
famille de contraintes, nommée d'après sa référence du document `05`.

**3. Résolution lexicographique** — 3 passes, statut **Optimal** en 0,06 s.
Deux difficultés numériques rencontrées et résolues :
- figer un niveau à l'exact rend la passe suivante infaisable (tolérance relative 1e-6) ;
- PuLP normalise la catégorie « Binary » en « Integer » borné à [0, 1].

**4. Validateur indépendant** — 86 contrôles recalculés à partir des équations physiques,
et non des contraintes du modèle. **Il a immédiatement détecté un vrai bug** : dans
l'extraction des résultats, les livraisons de CoC et de DEC_CL vers un même consommateur
s'écrasaient au lieu de se cumuler, faussant le bilan d'IR11 de 25,7 t. Un contrôle qui
aurait relu les contraintes du modèle n'aurait rien vu.

**5. Tests** — 138 tests en 1,2 s. Trois familles remarquables : ceux qui **verrouillent
une anomalie** du dossier, ceux qui **prouvent par contre-épreuve** qu'une contrainte sert
à quelque chose, et ceux qui **corrompent délibérément** la solution pour vérifier que le
validateur les rejette.

**6. Rapports** — Excel à 5 feuilles conforme à `OUTPUT_FORMAT.md`, plus export JSON.

**7. Analyses** — goulots d'étranglement et sensibilité sur les trois paramètres incertains.

### Résultats

**Le modèle sert 100 % de la demande** en 0,06 s, avec un plan sobre : une seule
décadmiation (750 t sur 13XY), trois transferts, deux lignes clarifiantes.

**Mais deux violations structurelles subsistent**, toutes deux dues à la même cause — le
nombre d'échelons affectés à la cocristallisation :
1. IR11 déborde de 1 016 t/jour ;
2. le stock de 14EXT reste 252 t sous sa bande de sécurité, cette ligne ne produisant
   aucun acide 54 NCL ordinaire.

**Le balayage apporte le remède chiffré** : ramener de 4 à 1 le nombre d'échelons de
14EXT en cocristallisation résorbe **intégralement** les deux violations (f2 : 1 268 → 0),
sans investissement et sans dégrader le service.

**Deux résultats secondaires utiles :**
- le domaine admissible de α est borné à ≈ 0,22, faute d'une seconde ligne habilitée au
  DEC_CL — information à remonter à l'encadrant ;
- la valeur de `MAX_TRANSFER` est **sans effet** au-delà de 750 t, ce qui rétrograde la
  question Q1 de « priorité haute » à « informative ». C'est exactement ce qu'on attend
  d'une analyse de sensibilité : elle transforme une incertitude en non-problème.

### Décisions prises
**D-10** — charge de concentration : bande de tolérance pénalisée. Conséquence
structurante : la ventilation du NCL produit a dû être généralisée en
`N_m = x_std − Π_coc`, forme qui redonne l'ancienne formule quand la charge vaut le plan.

### Prochaine séance
Phase 7 — rapport de stage LaTeX → PDF.

---

## Itération 3 — 2026-08-08 — Rapport de stage

### Objectif
Produire le rapport de stage en LaTeX, compilé en PDF.

### Travail réalisé

**Chaîne de compilation.** Installation de TeX Live (base, recommended, extra, français,
pictures, science, polices) et de `latexmk`.

**Structure.** Classe `book` --- et non `report`, qui ne fournit pas `\frontmatter` et donc
pas la numérotation romaine des pages liminaires. Préambule séparé, un fichier par chapitre,
`Makefile` avec une cible `verif` qui contrôle débordements et références.

**Contenu.** 79 pages : page de garde, remerciements, résumé, notations, huit chapitres,
trois annexes, bibliographie. Deux schémas TikZ (flux du procédé, architecture logicielle).

**Trois difficultés de compilation, et leur cause :**
1. `\frontmatter` indéfini --- la classe `report` ne le fournit pas ;
2. `File ended while scanning use of \@@BOOKMARK` --- des macros `\SI{}` placées dans des
   titres de section cassent les signets PDF générés par hyperref. Remplacées par du texte ;
3. deux schémas TikZ débordant de la largeur du texte --- enveloppés dans un `\resizebox`.

**Résultat : 0 débordement de ligne, 0 référence indéfinie.**

### Choix de rédaction

Le rapport ne se contente pas de décrire ce qui a été fait : il **argumente**. Trois
sections en portent la charge :
- la démonstration de dégénérescence de l'objectif spécifié, posée comme une proposition
  avec sa preuve ;
- le chapitre entier consacré à l'analyse critique des spécifications, avec la hiérarchie
  des sources fixée a priori ;
- la conclusion, qui distingue explicitement un modèle *correct* d'un modèle *utile*.

Deux éléments restent à la charge de l'étudiant, parce qu'ils ne peuvent pas être devinés :
la page de garde (noms, dates) et les remerciements, dont seule une trame est fournie.

### État du projet
Les sept phases sont terminées. La suite dépend des réponses de l'encadrant et de la
confrontation des résultats au réalisé de l'usine.
