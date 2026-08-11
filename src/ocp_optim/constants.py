"""Constantes physiques et structurelles du système.

Toutes les grandeurs massiques sont exprimées en **tonnes de P2O5** (voir la décision
D-01 et le document `docs-helper/04_DONNEES_ET_CONVENTIONS.md`, §2).

Règle de conception : aucune valeur *dérivée* n'est écrite en dur. Tout ce qui peut
être calculé à partir des données primaires (sections, hauteurs, densités, titres)
l'est par une fonction, et chaque formule est couverte par un test unitaire.
Cette règle vient du constat que le dossier d'origine contient plusieurs valeurs
dérivées fausses (anomalies A-01, A-02, A-03).
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# 1. Structure du système
# ─────────────────────────────────────────────────────────────────────────────

LIGNES_29: tuple[str, ...] = ("13AB", "13CD", "13XY", "13ZU", "13E", "13F")
LIGNES_54: tuple[str, ...] = ("14AB", "14CD", "14XY", "14ZU", "14EXT")

#: Application sigma : ligne d'acide 29 -> ligne de concentration associée.
#: `None` signifie que la ligne n'alimente aucune concentration (cas de 13F).
SIGMA: dict[str, str | None] = {
    "13AB": "14AB",
    "13CD": "14CD",
    "13XY": "14XY",
    "13ZU": "14ZU",
    "13E": "14EXT",
    "13F": None,
}

#: Application inverse sigma^-1, définie sur LIGNES_54.
SIGMA_INV: dict[str, str] = {v: k for k, v in SIGMA.items() if v is not None}

#: Lignes d'acide 29 disposant d'une ligne de concentration (domaine de sigma restreint).
LIGNES_29_AVEC_54: tuple[str, ...] = tuple(l for l in LIGNES_29 if SIGMA[l] is not None)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Échelons de concentration
# ─────────────────────────────────────────────────────────────────────────────

#: Capacité d'un échelon, en tonnes de P2O5 par jour à plein régime (24 h).
#:
#: Le dossier annote ces valeurs « tonnes/heure », mais la formule de production
#: `C * h / 24` impose des tonnes/jour : à 420 t/h un seul échelon produirait
#: 10 080 t/jour, soit près de vingt fois la production quotidienne du groupe.
#: Voir anomalie A-08.
CAPACITE_ECHELON: dict[str, float] = {
    # 14CD
    "C": 250, "D": 250, "M": 290, "N": 250,
    # 14XY
    "X": 300, "Y": 250, "P": 250, "Q": 250,
    # 14ZU
    "Z": 250, "U": 300, "R": 250, "S": 300, "V": 590, "W": 590,
    # 14EXT — cocristallisation possible
    "E": 420, "F": 420, "G": 420, "H": 420,
    # 14AB — cocristallisation possible
    "A": 300, "B": 300, "K": 300, "L": 300, "I": 590, "J": 590,
}

#: Partition des échelons par ligne de concentration.
GROUPES_ECHELONS: dict[str, tuple[str, ...]] = {
    "14EXT": ("E", "F", "G", "H"),
    "14AB": ("A", "B", "I", "J", "K", "L"),
    "14CD": ("C", "D", "M", "N"),
    "14XY": ("X", "Y", "P", "Q"),
    "14ZU": ("Z", "U", "R", "S", "V", "W"),
}

#: Lignes physiquement équipées d'unités de cocristallisation.
LIGNES_COC_POSSIBLE: tuple[str, ...] = ("14EXT", "14AB")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Réseau de transferts interzones (acide 29 standard uniquement)
# ─────────────────────────────────────────────────────────────────────────────

#: Zone associée à chaque ligne d'acide 29 (la matrice du dossier est indexée par zone).
LIGNE_VERS_ZONE: dict[str, str] = {
    "13AB": "AB", "13CD": "CD", "13XY": "XY",
    "13ZU": "ZU", "13E": "E", "13F": "F",
}
ZONE_VERS_LIGNE: dict[str, str] = {v: k for k, v in LIGNE_VERS_ZONE.items()}

#: Liaisons interzones autorisées, exprimées en zones : {origine: (destinations...)}.
#: La relation est anti-réflexive et **non symétrique** (conduites à sens unique).
INTERZONE_ZONES: dict[str, tuple[str, ...]] = {
    "E": ("AB", "CD"),
    "F": ("E", "AB", "XY", "ZU"),
    "AB": ("E", "CD"),
    "CD": ("E", "AB", "XY"),
    "XY": ("CD", "ZU"),
    "ZU": ("XY",),
}


def arcs_interzone() -> tuple[tuple[str, str], ...]:
    """Renvoie les liaisons interzones autorisées, exprimées en noms de lignes.

    Returns:
        Couples ``(ligne_origine, ligne_destination)``. 14 couples au total.
    """
    return tuple(
        (ZONE_VERS_LIGNE[origine], ZONE_VERS_LIGNE[dest])
        for origine, destinations in INTERZONE_ZONES.items()
        for dest in destinations
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Consommateurs
# ─────────────────────────────────────────────────────────────────────────────

CONSOMMATEURS: tuple[str, ...] = (
    "U16", "U116A", "U116BC",
    "IMACID", "EMAPHOS", "MAPS", "U53", "107DEF", "JFC1-5",
)

#: Ateliers d'engrais : leur besoin se déduit des profils qualité de leurs produits.
ATELIERS_ENGRAIS: tuple[str, ...] = ("U16", "U116A", "U116BC")

#: Raccordements physiques ligne -> consommateur, pour les acides livrés
#: depuis un **stock local**. Les acides centraux (CL, CoC, DEC_CL) transitent
#: par IR11/IR12 et ne sont soumis à aucune contrainte d'interconnexion.
CONNEXIONS_29: dict[str, tuple[str, ...]] = {
    "U16": ("13AB", "13CD", "13XY", "13ZU"),
    "U116A": ("13CD", "13F"),
    "U116BC": ("13F", "13AB", "13XY"),
    "IMACID": ("13E",),
    "EMAPHOS": (),
    "MAPS": ("13E",),
    "U53": (),
    "107DEF": ("13E", "13F"),
    "JFC1-5": ("13F",),
}

CONNEXIONS_54: dict[str, tuple[str, ...]] = {
    "U16": ("14XY", "14CD", "14AB", "14EXT"),
    "U116A": ("14AB", "14CD", "14EXT"),
    "U116BC": ("14XY", "14CD"),
    "IMACID": (),
    "EMAPHOS": ("14ZU", "14XY", "14AB"),
    "MAPS": (),
    "U53": (),
    "107DEF": (),
    "JFC1-5": (),
}


# ─────────────────────────────────────────────────────────────────────────────
# 5. Types d'acide
# ─────────────────────────────────────────────────────────────────────────────

ACIDE_29_STD = "acid_29_std"
ACIDE_29_DEC = "acid_29_dec"
ACIDE_54_NCL = "acid_54_ncl"
ACIDE_54_CL = "acid_54_cl"
ACIDE_54_COC = "acid_54_coc"
ACIDE_54_DEC_CL = "acid_54_dec_cl"

#: Besoin exprimé sur une *propriété* (« acide 54 de qualité décadmiée »),
#: satisfiable indifféremment par du CoC ou du DEC_CL depuis IR11.
BESOIN_54_DEC_TOTAL = "acid_54_dec_total"

#: Acides livrés depuis un stock local -> soumis aux matrices d'interconnexion.
ACIDES_LOCAUX: tuple[str, ...] = (ACIDE_29_STD, ACIDE_29_DEC, ACIDE_54_NCL)

#: Acides livrés depuis un stock central -> accessibles à tous les consommateurs.
ACIDES_CENTRAUX: tuple[str, ...] = (ACIDE_54_CL, ACIDE_54_COC, ACIDE_54_DEC_CL)

#: Types d'acide qu'un consommateur industriel accepte. Les ateliers d'engrais
#: ne figurent pas ici : leurs besoins sont dictés par les profils qualité.
ACIDES_ACCEPTES: dict[str, tuple[str, ...]] = {
    "EMAPHOS": (ACIDE_54_NCL,),
    "U53": (ACIDE_54_CL,),
    "IMACID": (ACIDE_29_STD,),
    "MAPS": (ACIDE_29_STD,),
    "JFC1-5": (ACIDE_29_STD,),
    "107DEF": (ACIDE_29_STD, ACIDE_54_CL, ACIDE_54_COC),
}


# ─────────────────────────────────────────────────────────────────────────────
# 6. Rendements de procédé (fixes, non optimisables)
# ─────────────────────────────────────────────────────────────────────────────

#: Concentration 29 % -> 54 %. Vaut exactement 1 car le P2O5 est conservé :
#: seule l'eau est évaporée. C'est la justification centrale de la décision D-01.
RENDEMENT_CONCENTRATION = 1.00

RENDEMENT_CLARIFICATION = 0.90
RENDEMENT_COCRISTALLISATION = 0.80

BOUE_CLARIFICATION = 1.0 - RENDEMENT_CLARIFICATION      # 0,10 -> stock acide 29 std
BOUE_COCRISTALLISATION = 1.0 - RENDEMENT_COCRISTALLISATION  # 0,20 -> stock acide 29 std

#: Niveaux de décadmiation admissibles : 0, 1 ou 2 filtres de 750 t/jour.
#: C'est ce caractère discret qui impose une formulation en nombres entiers.
NIVEAUX_DECADMIATION: tuple[float, ...] = (0.0, 750.0, 1500.0)

#: Capacité **entrante** des décanteurs, par ligne (2 décanteurs x 500 t/jour).
#: La limite porte sur ce qui est envoyé aux décanteurs, pas sur ce qui en sort
#: (mention « before yield » du guide de procédé). Voir décision D-06.
CAPACITE_DECANTEURS_PAR_LIGNE = 500.0 * 2

#: Retours d'EMAPHOS vers les stocks d'acide 29 standard, en part de la livraison
#: reçue. EMAPHOS consomme au niveau 54 et restitue au niveau 29 : c'est le seul
#: flux du système qui remonte d'un niveau.
RETOURS_EMAPHOS: dict[str, float] = {
    "13AB": 0.125,   # ARP1
    "13CD": 0.125,   # ARP2
    "13XY": 0.150,   # boue
}


# ─────────────────────────────────────────────────────────────────────────────
# 7. Géométrie des cuves
# ─────────────────────────────────────────────────────────────────────────────

# Cuves d'acide 29 %
SECTION_29 = 174.11      # m²
DENSITE_29 = 1.270       # t/m³
TITRE_P2O5_29 = 0.26     # fraction massique de P2O5
H_MIN_29 = 2.00          # m, par cuve
H_MAX_29 = 8.40          # m, par cuve
N_CUVES_29 = 2

# Cuves d'acide 54 %
SECTION_54 = 95.0        # m²
DENSITE_54 = 1.660       # t/m³
TITRE_P2O5_54 = 0.50
H_MIN_54 = 3.00          # m, par cuve
H_MAX_54 = 9.40          # m, par cuve
N_CUVES_54 = 2

#: Coefficients de conversion volume -> P2O5, tels que publiés par le dossier
#: (`get_vol_29 = 174.11 * h * 0.33`, `get_vol_54 = 95 * h * 0.83`).
#:
#: Ce sont les valeurs **opérationnelles** utilisées sur le site ; on les retient
#: telles quelles pour reproduire exactement les stocks initiaux du scénario.
#: Elles valent, au titre et à la densité près :
#:     0.26 x 1.270 = 0.3302  (arrondi a 0.33 -> écart 0,06 %)
#:     0.50 x 1.660 = 0.8300  (exact)
#: Le test `test_units.py::test_coefficients_coherents_avec_la_physique` vérifie
#: en permanence que ces coefficients restent cohérents avec la physique déclarée.
COEF_CONVERSION_29 = 0.33
COEF_CONVERSION_54 = 0.83

# Bacs centraux — leurs formules comportent un volume mort (partie basse non
# soutirable : piquage d'aspiration, boues sédimentées, fond bombé).
IR11_SECTION_EQ = 706.45
IR11_COEF = 0.855
IR11_VOLUME_MORT = 0.25   # m
H_MIN_IR11 = 0.40
H_MAX_IR11 = 10.80

IR12_SECTION_EQ = 706.45
IR12_COEF = 0.84
IR12_VOLUME_MORT = 2.70   # m
#: Attention : cette hauteur minimale est **inférieure** au volume mort de la
#: formule IR12, ce qui donne un volume négatif. La borne est écrêtée à zéro.
#: Voir anomalie A-06.
H_MIN_IR12 = 2.00
H_MAX_IR12 = 10.80


# ─────────────────────────────────────────────────────────────────────────────
# 8. Paramètres de planification (valeurs par défaut, surchargées par scénario)
# ─────────────────────────────────────────────────────────────────────────────

#: Quantité minimale d'un transfert interzone. En dessous, l'opération n'a pas de
#: sens industriel (amorçage de pompe, mobilisation d'opérateur, rinçage).
TRANSFERT_MIN_DEFAUT = 100.0

#: Quantité maximale d'un transfert interzone.
#: HYPOTHÈSE H7 — cette valeur est **absente du dossier** alors que le code
#: d'origine l'utilise. Valeur d'attente cohérente avec l'ordre de grandeur des
#: déséquilibres à corriger. Question Q1 en attente.
TRANSFERT_MAX_DEFAUT = 1000.0

#: Part minimale de DEC_CL dans les entrées d'IR11, traduisant l'obligation
#: métier de mélanger CoC et DEC_CL.
#: HYPOTHÈSE H8 — aucun seuil chiffré n'existe dans le dossier. Question Q2.
#: Mettre 0 désactive proprement la contrainte.
ALPHA_DEC_CL_DEFAUT = 0.15

#: Tolérance relative sur la charge de concentration (contrainte C4).
#: L'encadrant a précisé : « la somme doit être égale, c'est normalement rigide,
#: mais on peut avoir des seuils de tolérance pour respecter la planification des
#: transferts ». La bande est donc autorisée mais tout écart est pénalisé, si
#: bien que le modèle reste à l'égalité stricte sauf lorsque la tolérance lui
#: évite une violation plus grave. Voir décision D-10.
TOLERANCE_CONCENTRATION_DEFAUT = 0.05
