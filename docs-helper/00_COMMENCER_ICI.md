# 00 — COMMENCER ICI

> **Tu ne connais rien au projet ? C'est le bon fichier.**
> En lisant les 8 documents de ce dossier dans l'ordre, tu comprendras 100 % du sujet :
> le procédé industriel, ce qui est demandé, la modélisation mathématique, les hypothèses,
> les décisions prises et pourquoi.
> Tu n'auras **pas besoin** d'ouvrir les documents originaux de l'encadrant.

---

## 1. Le projet en un paragraphe

L'OCP produit à Jorf Lasfar de l'acide phosphorique. Six ateliers fabriquent un acide
« faible » à 29 %, que cinq ateliers de concentration transforment en acide « fort » à 54 %.
Selon les besoins, cet acide subit ensuite un ou plusieurs traitements de purification
(décadmiation, clarification, cocristallisation), puis il est distribué à neuf clients :
des ateliers d'engrais et des usines chimiques partenaires. Chaque client exige un
**type d'acide précis**, et toutes les lignes ne sont pas reliées à tous les clients.

**Le problème à résoudre :** chaque jour, décider *combien décadmier*, *combien clarifier*,
*quels transferts effectuer entre ateliers* et *qui sert qui*, de manière à satisfaire toutes
les demandes en respectant les contraintes physiques de l'usine — et si possible en laissant
l'usine dans le meilleur état possible pour le lendemain.

**La forme mathématique :** un programme linéaire en nombres entiers (MILP).

---

## 2. Ordre de lecture recommandé

Lis dans cet ordre. Chaque document suppose acquis les précédents.

| # | Document | Durée | Ce que tu y gagnes |
|---|---|---|---|
| **01** | `01_GLOSSAIRE.md` | 20 min | Tous les mots du sujet. Reviens-y sans arrêt. |
| **02** | `02_CONTEXTE_INDUSTRIEL.md` | 20 min | Où tu es, qui sont les acteurs, pourquoi ce problème existe. |
| **03** | `03_PROCEDE_DETAILLE.md` | 60 min | **Le cœur.** Le procédé, organe par organe, avec les schémas. |
| **04** | `04_DONNEES_ET_CONVENTIONS.md` | 45 min | Tous les chiffres, toutes les unités, toutes les matrices. |
| **05** | `05_MODELE_MATHEMATIQUE.md` | 90 min | **Le cœur mathématique.** Ensembles, variables, contraintes, objectif. |
| **06** | `06_ANOMALIES_ET_DECISIONS.md` | 30 min | Les 11 problèmes trouvés dans le dossier et comment on les a tranchés. |
| **07** | `07_FEUILLE_DE_ROUTE.md` | 15 min | Le plan complet du stage, phase par phase. |

**Total : environ 5 heures de lecture attentive.** Ne cherche pas à tout retenir : le
glossaire et les tableaux sont faits pour être consultés, pas appris.

---

## 3. Les 6 idées à retenir absolument

Si tu ne devais retenir que six choses, ce sont celles-ci. Chacune est démontrée dans les
documents indiqués.

### Idée 1 — L'unité de tout le modèle est la tonne de P₂O₅, pas la tonne d'acide

Quand le dossier dit « 1 500 tonnes/jour », il faut lire « 1 500 tonnes de **pentoxyde de
phosphore**, l'élément utile contenu dans l'acide ». C'est ce qui explique le point
suivant, qui sinon paraît absurde.
→ *Démontré en `04`, §2.*

### Idée 2 — Concentrer 1 t d'acide 29 donne 1 t d'acide 54

Ce n'est vrai qu'en P₂O₅ : la concentration ne fait qu'évaporer de l'eau. La masse d'acide,
elle, est presque divisée par deux. Le P₂O₅, lui, est conservé intégralement.
→ *Expliqué en `03`, §3.*

### Idée 3 — Une grande partie du système n'est PAS optimisable

La production d'acide 29 est imposée. La production d'acide 54 est imposée par les heures de
marche. La cocristallisation est **systématique** : quand un échelon y est affecté, il traite
tout ce qu'il produit, sans se soucier de la demande. On ne décide donc que d'une petite
partie du système — mais cette partie a des effets en cascade.
→ *Détaillé en `03`, §7.*

### Idée 4 — L'objectif écrit dans le dossier est mathématiquement vide

Le dossier demande de « maximiser le total d'acide livré » tout en imposant que les demandes
soient « exactement satisfaites ». Si les demandes sont des égalités, le total livré est une
**constante** : l'objectif ne départage plus rien. C'est le principal apport intellectuel du
stage que de le corriger proprement.
→ *Démontré en `05`, §7.1.*

### Idée 5 — Le dossier contient des erreurs de calcul

Onze anomalies ont été identifiées, dont quatre erreurs arithmétiques franches (jusqu'à
59 % d'écart sur les bornes de stock). **Ne recopie jamais un nombre du dossier :
recalcule-le.** Chaque anomalie est documentée avec sa résolution justifiée.
→ *Recensé en `06`.*

### Idée 6 — Tout se joue sur le partage des décanteurs

Chaque ligne d'acide 54 dispose de 2 décanteurs, soit 1 000 t/jour au total. Ces 1 000 t sont
**partagées** entre deux usages concurrents : clarifier de l'acide normal (pour IR12) et
clarifier de l'acide décadmié (obligatoire, pour IR11). C'est le couplage le plus fin du
problème : décadmier davantage, c'est renoncer à clarifier.
→ *Expliqué en `03`, §5.3.*

---

## 4. Comment lire une équation dans ces documents

Toutes les formalisations suivent la même discipline, celle d'un cours de mathématiques :
**rien n'est utilisé avant d'être défini.**

Chaque objet est classé dans exactement une des cinq catégories suivantes :

| Catégorie | Question à laquelle elle répond | Notation typique |
|---|---|---|
| **Ensemble** | Sur quoi porte-t-on l'indice ? | $\mathcal{L}_{29}$, $\mathcal{E}$, $\mathcal{K}$ |
| **Paramètre** | Qu'est-ce qui est connu avant de calculer ? | $P_\ell$, $\eta^{cl}$, $\Lambda$ |
| **Variable** | Qu'est-ce que le solveur choisit ? | $x_\ell$, $u_m$, $t_{\ell\ell'}$ |
| **Contrainte** | Qu'est-ce qui doit être vrai ? | (C4), (C7)… |
| **Objectif** | Qu'est-ce qu'on cherche à rendre optimal ? | $f_1$, $f_2$, $f_3$ |

**Un test simple pour ne pas se tromper :** un paramètre est *donné*, une variable est
*cherchée*. Si tu hésites, demande-toi « est-ce que l'usine peut changer ça demain matin ? ».
Si oui, c'est une variable ; si non, c'est un paramètre.

Chaque équation est systématiquement accompagnée de trois choses :
1. sa **traduction en français courant** ;
2. son **organe industriel** correspondant (quelle cuve, quelle pompe, quel filtre) ;
3. sa **justification** (pourquoi cette forme et pas une autre).

---

## 5. Vocabulaire d'urgence

Le strict minimum pour ne pas être perdu dès la première page. Le reste est en `01`.

| Sigle | Signification |
|---|---|
| **P29** | Acide phosphorique à 29 % de P₂O₅ (acide « faible », brut de production) |
| **P54** | Acide phosphorique à 54 % de P₂O₅ (acide « fort », concentré) |
| **NCL** | *Non-clarifié* — acide 54 brut, sortant de la concentration |
| **CL** | *Clarifié* — acide 54 débarrassé de ses impuretés solides |
| **DEC** | *Décadmié* — acide dont on a retiré le cadmium (métal lourd toxique) |
| **CoC** | *Cocristallisé* — acide ultra-purifié par cristallisation |
| **IR11 / IR12** | Les deux grands bacs de stockage central du site |
| **Échelon** | Une unité élémentaire de concentration (29 % → 54 %) |
| **Interzone** | Transfert d'acide 29 d'un atelier vers un autre |
| **Boue** | *(sludge)* Résidu d'un traitement, recyclé en amont |

---

## 6. Et maintenant ?

1. Lis les documents `01` à `06` dans l'ordre.
2. Ouvre `../PILOTAGE/QUESTIONS_ENCADRANT.md` et pose les **5 questions principales** à ton
   encadrant. Elles sont rédigées pour être posées telles quelles.
3. Reviens me voir et dis-moi : **« on passe à la Phase 3 »**.

L'état d'avancement du projet est toujours à jour dans
`../PILOTAGE/ETAT_AVANCEMENT.md`.
