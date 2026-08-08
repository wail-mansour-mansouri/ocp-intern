# 02 — CONTEXTE INDUSTRIEL

> Où tu es, qui sont les acteurs, et **pourquoi ce problème d'optimisation existe**.
> Ce document te donne la culture métier nécessaire pour que les contraintes du modèle
> cessent d'être des lignes abstraites et deviennent des équipements réels.

---

## 1. L'OCP et le site de Jorf Lasfar

L'OCP (Office Chérifien des Phosphates) est le premier exportateur mondial de phosphates et
de leurs dérivés. Le Maroc détient l'essentiel des réserves mondiales de roche phosphatée.

**Jorf Lasfar**, sur la côte atlantique près d'El Jadida, est la plus grande plateforme
chimique du groupe. On y trouve, intégrés sur un même site :

1. des ateliers d'acide **sulfurique** (H₂SO₄) ;
2. des ateliers d'acide **phosphorique** (H₃PO₄) — **c'est notre périmètre** ;
3. des ateliers d'**engrais** (DAP, MAP, TSP, NPK) ;
4. des **coentreprises** avec des partenaires étrangers (EMAPHOS, IMACID, PMP, JFC…) ;
5. une centrale thermique, une station de dessalement, un port minéralier.

Le site produit de l'ordre de plusieurs millions de tonnes de P₂O₅ par an.

### Pourquoi l'intégration crée le problème
Sur un site intégré, les ateliers ne sont pas indépendants : **la sortie de l'un est
l'entrée de l'autre**. Un déséquilibre local se propage immédiatement. Une cuve pleine
arrête la production amont ; une cuve vide arrête la production aval. Coordonner
quotidiennement ces flux, c'est exactement l'objet de ton stage.

---

## 2. La chaîne de valeur en trois étages

```
   Minerai de phosphate  +  Acide sulfurique
                │
                ▼
   ┌──────────────────────────────┐
   │  ÉTAGE 1 — ATTAQUE-FILTRATION│   6 lignes : 13AB 13CD 13XY 13ZU 13E 13F
   │  produit l'acide 29 %        │   ≈ 8 300 t P₂O₅/jour
   └──────────────────────────────┘
                │
                ▼
   ┌──────────────────────────────┐
   │  ÉTAGE 2 — CONCENTRATION     │   5 lignes : 14AB 14CD 14XY 14ZU 14EXT
   │  produit l'acide 54 %        │   ≈ 7 000 t P₂O₅/jour
   └──────────────────────────────┘
                │
                ▼
   ┌──────────────────────────────┐
   │  ÉTAGE 3 — PURIFICATION      │   décadmiation · clarification · cocristallisation
   │  produit les qualités        │
   └──────────────────────────────┘
                │
                ▼
      Engrais  ·  Acide marchand  ·  Acide purifié (export)
```

### Pourquoi concentrer ?
L'acide sortant de l'attaque titre environ 26–29 % de P₂O₅. C'est trop dilué :
- transporter de l'eau coûte cher ;
- la plupart des fabrications d'engrais exigent un acide à 50 % et plus.

On évapore donc l'eau sous vide. **Le P₂O₅ ne bouge pas** — d'où le fameux « rendement de
100 % » qui déroute au premier abord, et qui ne s'explique que si l'on compte en P₂O₅.

### Pourquoi purifier ?
Parce que les clients n'ont pas les mêmes exigences :

| Besoin | Traitement | Raison |
|---|---|---|
| Engrais destinés à l'Europe | **décadmiation** | Le règlement européen plafonne le cadmium dans les engrais. |
| Engrais de qualité, acide marchand | **clarification** | Retirer les solides en suspension (gypse, silice) qui bouchent les installations. |
| Acide de très haute pureté | **cocristallisation** | Éliminer les impuretés jusqu'à des niveaux très bas. |

---

## 3. Les partenaires du site

### EMAPHOS — *Euro-Maroc Phosphore*
Coentreprise entre l'OCP, le belge **Prayon** et l'allemand **Chemische Fabrik Budenheim**.
Elle produit de l'**acide phosphorique purifié** (qualité alimentaire et technique), par
**extraction liquide-liquide au solvant**.

Capacité : **140 000 t P₂O₅/an**, doublée à **280 000 t P₂O₅/an** depuis fin 2022 — soit de
l'ordre de **380 à 770 t P₂O₅/jour**.

> **C'est notre preuve d'unité.** La demande d'EMAPHOS dans le scénario de référence est de
> **700 t/jour**. Ce chiffre ne prend un sens réaliste que si l'unité est la **tonne de
> P₂O₅** — en tonnes d'acide, 700 t/j serait très en deçà de la capacité installée.
> Voir décision **D-01**.

**Le retour de matière expliqué.** L'extraction au solvant sépare l'acide en deux phases :
une phase organique chargée d'acide purifié, et un **raffinat** aqueux qui concentre les
impuretés. Ce raffinat contient encore beaucoup de P₂O₅ : le jeter serait une perte
économique majeure. Il est donc **renvoyé dans le circuit principal**, en amont, où sa
qualité médiocre est diluée dans la masse.

C'est exactement ce que décrit le modèle : sur 100 t livrées, 40 t reviennent
(12,5 % vers 13AB, 12,5 % vers 13CD, 15 % vers 13XY).

### IMACID — *Indo-Maroc Phosphore*
Coentreprise entre l'OCP et des groupes indiens. Elle prélève de l'acide 29 standard pour
alimenter sa propre chaîne. Dans notre modèle, c'est un **consommateur pur** : elle ne rend
rien.

### JFC 1-5 — *Jorf Fertilizer Company*
Unités d'engrais dédiées, consommatrices d'acide 29 standard.

### MAPS, U53, 107DEF, U16, U116A, U116BC
Unités internes ou partenaires du site. Du point de vue du modèle, chacune se caractérise
par **deux informations seulement** :
1. quels **types d'acide** elle accepte ;
2. à quelles **lignes** elle est physiquement raccordée.

---

## 4. Pourquoi les interconnexions ne sont pas complètes

Une question naturelle : pourquoi n'importe quelle ligne ne peut-elle pas servir n'importe
quel client ?

**Parce qu'une conduite d'acide phosphorique coûte cher.** Il faut :
- des matériaux résistants (acier revêtu, polymères spéciaux) — l'acide attaque tout ;
- des pompes, des réchauffeurs (l'acide 54 est visqueux et fige en refroidissant) ;
- des racks de tuyauterie, des vannes, de la maintenance.

On ne construit donc une liaison que si elle est régulièrement utile. Résultat : un réseau
**partiel**, décrit par deux matrices d'incidence :
- la **matrice interzone** (quelles lignes P29 peuvent s'échanger de l'acide) ;
- la **matrice d'interconnexion** (quelle ligne peut servir quel client).

> **Traduction mathématique.** Ces matrices se traduisent le plus simplement du monde :
> pour tout couple non relié, on impose $y = 0$. En pratique, on ne crée même pas la
> variable — ce qui réduit d'autant la taille du problème.

**Exception notable :** les acides traités (CL, CoC, DEC_CL) transitent par IR11 et IR12,
qui sont reliés à **tout le monde**. Il n'y a donc **aucune contrainte d'interconnexion**
pour ces trois qualités. Seuls les acides livrés depuis un stock local (29 std, 29 dec,
54 NCL) sont contraints.

---

## 5. Ce que fait un planificateur, aujourd'hui, sans outil

Chaque matin, un ingénieur d'exploitation doit décider :

1. combien d'acide 29 envoyer en concentration sur chaque ligne ;
2. quelles lignes décadmient, et à quel niveau (1 ou 2 filtres) ;
3. combien clarifier sur chaque ligne, sachant que les décanteurs sont partagés ;
4. quels transferts interzones lancer pour éviter débordements et manques ;
5. quelle ligne sert quel client, pour chaque type d'acide.

Il le fait aujourd'hui **au jugement et au tableur**, avec plusieurs difficultés :
- les décisions sont **couplées** (décadmier davantage réduit la capacité de clarifier) ;
- les retours de boue **rebouclent** sur l'amont ;
- le nombre de combinaisons est **hors de portée** d'un raisonnement manuel ;
- le résultat dépend de la personne présente ce jour-là.

**C'est ce que ton stage automatise et rend optimal.**

---

## 6. La valeur du projet, en termes concrets

| Gain | Mécanisme |
|---|---|
| **Éviter les arrêts de production** | Une cuve qui déborde ou qui se vide arrête une ligne. Le modèle anticipe et corrige par transfert. |
| **Économiser du cadmium retiré inutilement** | La décadmiation consomme des réactifs et de la capacité. Décadmier au plus juste, c'est économiser. |
| **Maximiser la valorisation** | Un acide clarifié se vend mieux qu'un acide brut. Bien allouer les décanteurs augmente la valeur produite. |
| **Réduire les transferts inutiles** | Chaque transfert consomme de l'énergie de pompage et du temps opérateur. |
| **Rendre les décisions traçables** | Une décision issue d'un modèle est justifiable, reproductible et auditable — contrairement à un jugement. |

---

## 7. Ce que le modèle **ne** fait **pas**

Il est aussi important de savoir ce qui est hors périmètre. Le modèle **ne décide pas** :

- ❌ **la production d'acide 29** — elle est imposée par l'amont (attaque, minerai, sulfurique) ;
- ❌ **les heures de marche des échelons** — elles relèvent de la maintenance et du planning,
  et sont une **entrée** du modèle ;
- ❌ **le choix des échelons affectés à la cocristallisation** — configuration du scénario ;
- ❌ **les capacités des équipements** — données physiques ;
- ❌ **les recettes des engrais** — imposées par le service qualité ;
- ❌ **la demande** — imposée par le commerce.

> **Formulation mathématique de cette distinction.** Tout ce qui précède est un
> **paramètre** : une donnée connue avant la résolution. Seules les décisions de la liste du
> §5 sont des **variables**. Cette distinction est la première chose à établir dans toute
> modélisation, et elle est traitée rigoureusement en `05`, §3 et §4.

---

## 8. Ordres de grandeur à avoir en tête

Ces chiffres, tirés du scénario de référence et **recalculés indépendamment**, te permettent
de repérer immédiatement une erreur de calcul (un facteur 10 se voit tout de suite).

| Grandeur | Valeur | Commentaire |
|---|---|---|
| Production d'acide 29 | **8 300 t P₂O₅/j** | imposée |
| Production d'acide 54 | **6 981,7 t P₂O₅/j** | *recalculée — le dossier annonce 6 636* |
| Demande totale | **5 811,8 t P₂O₅/j** | tous clients, tous types |
| Stock initial P29 (std + dec) | ≈ 4 355 t | |
| Stock initial P54 NCL | ≈ 2 708 t | |
| Stock initial IR11 | ≈ 5 515 t | capacité ≈ 6 372 t → **déjà rempli à 87 %** |
| Stock initial IR12 | ≈ 3 822 t | capacité ≈ 4 807 t → **rempli à 79 %** |
| CoC systématique produit | ≈ 2 431 t/j | pour un besoin `dec_total` de **987 t/j** seulement |
| Capacité totale de clarification | 4 000 t/j | 4 lignes autorisées × 1 000 t/j |

### Trois observations qui orientent déjà la modélisation

**1. La production dépasse largement la demande** (6 982 contre 5 812 t/j).
Le problème n'est donc **pas** de produire assez. Il est de bien **répartir** et de bien
**gérer les stocks**. Cela confirme que l'objectif « maximiser les livraisons » est
inopérant : servir tout le monde est facile ici.

**2. La cocristallisation produit 2,5 fois le besoin en acide de qualité décadmiée.**
L'excédent s'accumule dans IR11, qui est déjà rempli à 87 %. **La saturation d'IR11 est un
goulot d'étranglement probable** — à surveiller de près en Phase 5.

**3. La production de CoC étant si abondante, l'optimiseur n'aura spontanément aucune
raison de produire du DEC_CL.** Il violera donc la règle métier « la production de DEC_CL est
obligatoire », exactement comme le dossier le redoute. D'où la nécessité de la contrainte de
mélange de la décision **D-09**, et de la question **Q2**.

---

## Sources

- [EMAPHOS — Jorf Lasfar Purified Phosphoric Acid Plant](https://www.industryabout.com/country-territories-3/1209-morocco/phosphate-mining/16474-emaphos-jorf-lasfar-purified-phosphoric-acid-plant)
- [EMAPHOS launches a new unit to double its production capacity — OCP Group](https://www.ocpgroup.ma/en/press-release/emaphos-launches-new-unit-be-double-its-production-capacity)
- [Creation of Euro Maroc Phosphore (EMAPHOS) — OCP Group](https://www.ocpgroup.ma/en/creation-euro-maroc-phosphore-emaphos)
- [OCP Phosphoric Acid plants complex, Jorf Lasfar — De Smet Engineers & Contractors](https://www.dsengineers.com/en/references/jorf-lasfar-phosphoric-acid-plants-complex-morocco/)
- [Preparation of refined phosphoric acid with recycling of raffinate acid — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0959652623043160)
