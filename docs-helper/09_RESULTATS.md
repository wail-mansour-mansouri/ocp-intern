# 09 — RÉSULTATS ET ANALYSE

> Ce que le modèle répond sur le scénario de référence, et ce que cela nous apprend
> sur l'usine.
>
> Toutes les quantités sont en **tonnes de P₂O₅ par jour**.

---

## 1. Résumé exécutif

| Indicateur | Valeur |
|---|---|
| Statut de résolution | **Optimal** |
| Temps de résolution | 0,06 s (trois passes) |
| Taille du problème | 170 variables (29 binaires), 138 contraintes |
| **Demande satisfaite** | **100 %** — aucun manque |
| Validation indépendante | **86 contrôles réussis sur 86** |
| Niveau 1 (demande non servie) | **0,000** |
| Niveau 2 (violations molles) | 1 268,3 |
| Niveau 3 (coût opératoire) | 3 111,9 |

**Toute la demande est servie**, et la solution respecte l'intégralité des règles de
procédé. Mais le système **ne tient pas dans ses limites de stockage** : deux violations
structurelles subsistent, qu'aucune décision d'exploitation ne peut corriger.

---

## 2. Le plan d'exploitation optimal

### 2.1 Décadmiation
```
13XY : 750 t   (1 filtre)
```
Une seule ligne décadmie, au niveau minimal non nul. C'est le strict nécessaire pour :
- couvrir le besoin de U116BC en acide 29 décadmié (363,6 t) ;
- alimenter la production obligatoire de DEC_CL imposée par la contrainte de qualité
  d'IR11 (476,7 t envoyées en concentration).

Le niveau 3 pénalisant la décadmiation, l'optimiseur ne fait **rien de plus** que ce que
les contraintes exigent. C'est le comportement voulu.

### 2.2 Transferts interzones
```
13F  ->  13ZU    758,8 t
13F  ->  13E     603,3 t
13CD ->  13AB    100,0 t
```

**Trois transferts seulement**, et leur logique est limpide :
- **13F est la source.** C'est la seule ligne sans concentration associée : elle produit
  1 500 t qu'elle n'a presque pas moyen de consommer. Elle est structurellement
  excédentaire.
- **13ZU et 13E sont les puits.** 13ZU ne produit que 800 t mais doit charger 1 481,7 t
  en concentration ; 13E produit 1 500 t mais doit charger 1 505 t **et** livrer 700 t à
  IMACID.
- **Le transfert 13CD → 13AB de 100 t** est exactement au minimum d'expédition : c'est un
  appoint, pas un flux de fond.

> **Lecture industrielle.** Le modèle retrouve tout seul le rôle que 13F joue réellement
> dans l'usine : celui de **réserve souple** du système. C'est un bon signe de validité.

### 2.3 Clarification
```
14XY :  NCL   0,0  |  DEC  476,7  |  total  476,7   (47,7 % des décanteurs)
14ZU :  NCL 722,5  |  DEC    0,0  |  total  722,5   (72,3 % des décanteurs)
```

La séparation est nette et parfaitement rationnelle :
- **14XY** est la seule ligne habilitée à produire du DEC_CL : elle y consacre ses
  décanteurs.
- **14ZU** produit l'acide clarifié destiné à IR12, donc à U53.
- 14AB et 14CD, bien qu'habilitées, ne clarifient pas : **ce n'est pas nécessaire**.
  IR12 contient déjà 3 821,6 t pour une demande de 1 500 t.

---

## 3. Les deux violations structurelles

C'est le résultat le plus important de l'étude.

### 3.1 IR11 déborde de 1 016 t par jour

```
IR11 :  5 514,7  +  2 860,4  -  986,7  =  7 388,3  t
        (initial)   (entrées)  (sorties)              pour une capacité de 6 372,4 t
                                                      soit 115,9 % de remplissage
```

**Origine.** La cocristallisation est **systématique** : les quatre échelons de 14EXT et
quatre des six échelons de 14AB y sont affectés, et traitent donc tout ce qu'ils
produisent, quelle que soit la demande. Résultat : **2 431 t de CoC par jour**, pour un
besoin en acide de qualité décadmiée de **987 t seulement**.

**Pourquoi l'optimiseur ne peut rien y faire.** La production de CoC est un **paramètre**,
pas une variable. Les sorties sont bornées par la demande, qui est fixée. Le solde net
est donc de +1 444 t par jour, dans un bac qui n'offrait que 858 t de marge.

### 3.2 Le stock de 14EXT reste sous sa bande de sécurité

```
14EXT :  stock final 220,8 t  pour une bande de 473,1 – 1 482,4 t
         manque : 252,3 t
```

**Origine.** Les **quatre** échelons de 14EXT sont affectés à la cocristallisation. La
ligne ne produit donc **aucun** acide 54 NCL ordinaire : son stock ne peut que rester à
son niveau initial, qui est déjà trop bas.

### 3.3 Une cause unique

Les deux violations remontent à la même décision de configuration : **le nombre
d'échelons affectés à la cocristallisation**. C'est ce que confirme le balayage suivant.

---

## 4. Analyse de sensibilité

### 4.1 Nombre d'échelons de 14EXT en cocristallisation

| Configuration | CoC produit | Stock IR11 | Dépassement | f₂ | f₃ |
|---|---:|---:|---:|---:|---:|
| **4 sur 4** *(actuel)* | 2 431,3 | 7 388,3 | **1 016,0** | 1 268,3 | 3 111,9 |
| 3 sur 4 | 2 235,3 | 7 157,7 | 785,4 | 792,7 | 3 055,3 |
| 2 sur 4 | 1 899,3 | 6 762,5 | 390,1 | 390,1 | 2 958,1 |
| **1 sur 4** | 1 563,3 | 6 367,2 | **0,0** | **0,0** | 2 901,0 |
| 0 sur 4 | 1 227,3 | 5 971,9 | 0,0 | 0,0 | 2 887,9 |

> ### 🎯 Recommandation principale
> **Ramener de 4 à 1 le nombre d'échelons de 14EXT affectés à la cocristallisation
> résorbe intégralement les deux violations** (f₂ passe de 1 268,3 à 0), tout en
> continuant à servir 100 % de la demande.
>
> Le gain est double : IR11 rentre dans sa capacité, **et** 14EXT se remet à produire de
> l'acide 54 NCL ordinaire, ce qui ramène son stock dans sa bande de sécurité.
>
> C'est un résultat **actionnable** : il ne demande aucun investissement, seulement une
> reconfiguration de la marche des échelons.

### 4.2 Part minimale de DEC_CL dans IR11 (paramètre α, hypothèse H8)

| α | DEC_CL produit | Stock IR11 | Dépassement | f₂ |
|---|---:|---:|---:|---:|
| 0,00 | 0,0 | 6 959,3 | 586,9 | 839,2 |
| 0,05 | 128,0 | 7 087,2 | 714,9 | 967,2 |
| 0,10 | 270,1 | 7 229,4 | 857,1 | 1 109,4 |
| **0,15** *(hypothèse)* | 429,1 | 7 388,3 | 1 016,0 | 1 268,3 |
| 0,20 | 607,8 | 7 567,1 | 1 194,8 | 1 476,7 |
| 0,25 | — | — | — | **INFAISABLE** |
| 0,30 | — | — | — | **INFAISABLE** |

**Deux enseignements.**

**(a) Le domaine admissible de α est borné : α ≲ 0,22.** Au-delà, le modèle n'a plus de
solution. La raison est structurelle : **seule 14XY est habilitée à produire du DEC_CL**,
et sa capacité d'échelons non cocristallisants (820,8 t) plafonne la production possible.

> **À signaler à l'encadrant.** Si la valeur métier de α dépasse 0,22, la configuration
> actuelle ne peut pas la respecter. Il faudrait habiliter une **seconde ligne** à
> produire du DEC_CL.

**(b) Chaque point de α aggrave le débordement d'IR11**, puisque le DEC_CL vient s'ajouter
au CoC dans le même bac. À noter cependant : même avec α = 0, IR11 déborde encore de
586,9 t. **La contrainte de qualité n'est pas la cause du problème**, elle ne fait que
l'accentuer.

### 4.3 Transfert interzone maximal (paramètre τ_max, hypothèse H7)

| τ_max | Nombre de transferts | f₂ | f₃ |
|---|---:|---:|---:|
| 300 | 6 | 1 430,4 | 3 392,3 |
| 500 | 4 | 1 268,3 | 3 161,9 |
| **750** | 3 | **1 268,3** | **3 111,9** |
| 1 000 *(hypothèse)* | 3 | 1 268,3 | 3 111,9 |
| 1 500 | 3 | 1 268,3 | 3 111,9 |

> **La valeur d'attente est validée.** À partir de 750 t, la solution ne bouge plus :
> **le choix de 1 000 t n'a aucune influence sur le résultat.** L'incertitude de
> l'hypothèse H7 est donc sans conséquence, ce qui rétrograde la question Q1 de
> « priorité haute » à « informative ».
>
> En revanche, une borne à 300 t dégraderait la solution : les transferts deviendraient
> plus nombreux (6 au lieu de 3) et le rééquilibrage moins efficace.

---

## 5. Goulots d'étranglement

| Ressource | Utilisé | Capacité | Taux | |
|---|---:|---:|---:|:-:|
| Bac IR11 | 7 388,3 | 6 372,4 | **115,9 %** | 🔴 dépassé |
| Cuves 13F | 965,3 | 965,3 | 100,0 % | 🟠 saturé |
| Cuves 13XY | 965,3 | 965,3 | 100,0 % | 🟠 saturé |
| Cuves 13ZU | 965,3 | 965,3 | 100,0 % | 🟠 saturé |
| Cuves 13CD | 950,7 | 965,3 | 98,5 % | |
| Décanteurs 14ZU | 722,5 | 1 000,0 | 72,3 % | |
| Cuves 13AB | 650,2 | 965,3 | 67,4 % | |
| Cuves 13E | 641,7 | 965,3 | 66,5 % | |

### Lecture

**Le stockage d'acide 29 est saturé sur trois lignes.** C'est ce qui explique pourquoi
13F ne transfère « que » 1 362 t alors qu'elle est excédentaire : **il n'y a plus de place
ailleurs**. Le système est contraint par le stockage, pas par la production.

**Les décanteurs ne sont pas un goulot dans ce scénario** (72 % au plus). C'est
contre-intuitif au regard du document `03` §5.3, qui les présente comme la contrainte
structurante — et c'est un enseignement en soi : la contrainte *conceptuellement* la plus
subtile n'est pas forcément la plus *limitante* un jour donné.

> **⚠️ Ne pas généraliser.** Ce diagnostic vaut pour **ce** scénario. Avec une demande de
> CL plus forte, ou un α plus élevé, les décanteurs redeviendraient contraignants. C'est
> précisément l'intérêt d'avoir un modèle : rejouer le calcul chaque jour plutôt que
> raisonner sur des intuitions figées.

---

## 6. Vérifications de cohérence

### 6.1 La validation indépendante
**86 contrôles, 86 réussis.** Bilans matière fermés sur les 19 nœuds, conservation globale
du P₂O₅, demandes exactement servies, capacités respectées, niveaux de décadmiation
discrets, rendements exacts, stocks positifs.

> Le validateur a d'ailleurs **détecté un vrai bug** lors du premier passage : l'extraction
> des livraisons depuis IR11 écrasait la livraison de CoC par celle de DEC_CL au lieu de
> les cumuler, faussant le bilan de 25,7 t. Un contrôle qui se serait contenté de relire
> les contraintes du modèle n'aurait rien vu. C'est la justification concrète de la
> double vérification.

### 6.2 La tolérance de concentration n'est pas utilisée
L'encadrant a accordé une tolérance sur la charge de concentration, tout en la qualifiant
de « normalement rigide ». **Résultat : l'écart est nul sur les cinq lignes.** La bande
existe en dernier recours, la pénalité du niveau 2 maintient le modèle à l'égalité
stricte. Comportement exactement conforme à la consigne.

### 6.3 La contrainte de qualité d'IR11 est bien nécessaire
Contre-épreuve menée en test automatisé : avec α = 0, **l'optimiseur cesse totalement de
produire du DEC_CL**. La règle métier serait donc violée sans la contrainte C15. La
décision D-09 est empiriquement justifiée.

---

## 7. Synthèse pour l'encadrant

### Ce qui fonctionne
1. Le modèle sert **100 % de la demande** en 0,06 s.
2. La solution est **physiquement valide** — 86 contrôles indépendants.
3. Le plan est **sobre** : une seule décadmiation, trois transferts, deux lignes
   clarifiantes. Rien d'inutile.

### Ce qui ne va pas, et qui ne vient pas de l'optimisation
1. **IR11 déborde de 1 016 t/jour.** Cause : trop d'échelons en cocristallisation.
2. **Le stock de 14EXT reste sous sa bande.** Même cause.
3. **Le stockage d'acide 29 est saturé** sur trois lignes sur six.

### Trois questions à lui poser
1. **Peut-on réduire à 1 ou 2 le nombre d'échelons de 14EXT en cocristallisation ?**
   C'est la seule action qui résorbe les deux violations, et elle ne coûte rien.
2. **Quelle est la vraie valeur de α ?** Si elle dépasse 0,22, il faut habiliter une
   deuxième ligne au DEC_CL.
3. **L'excédent de CoC a-t-il un débouché non modélisé ?** (vente d'acide marchand,
   export, autre bac). Si oui, le débordement d'IR11 est un artefact de modélisation et
   il faut ajouter ce flux ; si non, c'est un vrai problème d'exploitation.

---

## 8. Ce qu'il reste à faire

- [ ] Confronter ces résultats à ce que fait réellement l'usine ce jour-là
- [ ] Obtenir les réponses aux questions ci-dessus
- [ ] Étendre à un horizon multi-périodes (perspective du rapport)
- [ ] Étudier la variante où l'affectation des échelons à la cocristallisation devient une
      **variable de décision** plutôt qu'un paramètre — le §4.1 montre que le gain serait
      substantiel
