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
