"""Contraintes du modèle — une fonction par famille.

Chaque fonction porte le numéro de la contrainte du document
`docs-helper/05_MODELE_MATHEMATIQUE.md`, de sorte que la correspondance entre le
code et la formalisation soit immédiate et vérifiable ligne à ligne.
"""

from __future__ import annotations

import pulp

from .. import constants as C
from .. import units
from ..preprocessing import ParametresDerives
from ..scenario import Scenario
from .variables import Variables, sources_autorisees

__all__ = ["ajouter_toutes_les_contraintes"]


# ─────────────────────────────────────────────────────────────────────────────
# Expressions réutilisables
# ─────────────────────────────────────────────────────────────────────────────

def _pi_coc(v: Variables, params: ParametresDerives, ligne54: str):
    """Production dirigée vers la cocristallisation sur la ligne (Pi_coc_m).

    Deux régimes selon le mode retenu :

    - **mode subi** (défaut, conforme au cahier des charges) : c'est un
      paramètre, calculé en prétraitement ;
    - **mode décidable** (D-11) : c'est une expression affine des binaires
      d'activation, ``sum(kappa_e * z_e)``. Toutes les contraintes qui
      l'utilisent restent linéaires.
    """
    if not v.z:
        return params.production_54_coc[ligne54]
    return pulp.lpSum(
        params.production_echelon[e] * v.z[e]
        for e in params.echelons_coc_candidats.get(ligne54, ())
    )


def _coc_produit(v: Variables, params: ParametresDerives, ligne54: str):
    """CoC envoyé vers IR11 par la ligne (G_m)."""
    return C.RENDEMENT_COCRISTALLISATION * _pi_coc(v, params, ligne54)


def _boue_coc(v: Variables, params: ParametresDerives, ligne54: str):
    """Boue de cocristallisation retournant au stock d'acide 29 (B_coc_m)."""
    return C.BOUE_COCRISTALLISATION * _pi_coc(v, params, ligne54)


def _coc_total(v: Variables, params: ParametresDerives):
    """CoC total produit, toutes lignes confondues."""
    if not v.z:
        return params.coc_total
    return pulp.lpSum(_coc_produit(v, params, m) for m in C.LIGNES_54)


def _livraison_emaphos(v: Variables) -> pulp.LpAffineExpression:
    """Total d'acide 54 NCL livré à EMAPHOS, toutes lignes confondues."""
    return pulp.lpSum(
        var for (acide, _, k), var in v.y_loc.items()
        if acide == C.ACIDE_54_NCL and k == "EMAPHOS"
    )


def _ncl_produit(v: Variables, params: ParametresDerives, ligne54: str) -> pulp.LpAffineExpression:
    """NCL ordinaire produit par la ligne (C6).

    La charge totale se répartit en trois flux :
      - ``Pi_coc`` alimente les échelons cocristallisants (acide standard) ;
      - ``x_dec`` alimente des échelons non cocristallisants et devient du DEC ;
      - le reste, soit ``x_std - Pi_coc``, produit du NCL ordinaire.
    """
    ligne29 = C.SIGMA_INV[ligne54]
    return v.x_std[ligne29] - _pi_coc(v, params, ligne54)


def _clarification_dec(v: Variables, ligne54: str) -> pulp.LpAffineExpression:
    """Entrée de clarification décadmiée de la ligne.

    Il n'existe pas de variable dédiée : l'acide décadmié concentré est
    **obligatoirement** clarifié dans la foulée (pas de stockage local pour le
    54 NCL DEC). On substitue donc directement ``x_dec``.
    """
    ligne29 = C.SIGMA_INV[ligne54]
    return v.x_dec.get(ligne29, pulp.LpAffineExpression())


def _entree_clarification_totale(v: Variables, ligne54: str) -> pulp.LpAffineExpression:
    """Total envoyé aux décanteurs de la ligne : NCL ordinaire + décadmié."""
    return v.u_ncl.get(ligne54, pulp.LpAffineExpression()) + _clarification_dec(v, ligne54)


# ─────────────────────────────────────────────────────────────────────────────
# C2, C3 — Décadmiation
# ─────────────────────────────────────────────────────────────────────────────

def c02_choix_niveau_decadmiation(prob, v: Variables, scenario: Scenario) -> None:
    """Chaque ligne équipée retient exactement un niveau de décadmiation."""
    for ligne in scenario.decadmiation_equipee:
        prob += (
            pulp.lpSum(v.w[(ligne, n)] for n in C.NIVEAUX_DECADMIATION) == 1,
            f"C02_niveau_unique_{ligne}",
        )


def c03_faisabilite_decadmiation(prob, v: Variables, scenario: Scenario) -> None:
    """On ne peut pas décadmier plus que la ligne ne produit.

    Contrainte absente du dossier : sans elle, 13ZU (800 t produites) pourrait
    « décadmier » 1 500 t et créer de la matière ex nihilo.
    """
    for ligne in scenario.decadmiation_equipee:
        prob += (
            v.d[ligne] <= scenario.production_29[ligne],
            f"C03_decad_faisable_{ligne}",
        )


# ─────────────────────────────────────────────────────────────────────────────
# C4, C5 — Charge de concentration
# ─────────────────────────────────────────────────────────────────────────────

def c04_charge_concentration(
    prob, v: Variables, scenario: Scenario, params: ParametresDerives
) -> None:
    """La charge envoyée en concentration suit le plan de production d'acide 54.

    L'encadrant a précisé que l'égalité est « normalement rigide », mais qu'un
    seuil de tolérance est admis pour permettre la planification des transferts.
    On borne donc l'écart à la bande autorisée et on le pénalise dans l'objectif :
    le modèle reste à l'égalité stricte sauf lorsque s'en écarter évite une
    violation plus grave. Voir décision D-10.
    """
    tol = scenario.tolerance_concentration
    for ligne in C.LIGNES_29_AVEC_54:
        ligne54 = C.SIGMA[ligne]
        plan = params.production_54[ligne54]

        prob += (
            v.x_std[ligne] + v.x_dec[ligne] == plan + v.e_plus[ligne] - v.e_minus[ligne],
            f"C04_charge_{ligne}",
        )
        prob += (v.e_plus[ligne] <= tol * plan, f"C04_tol_sup_{ligne}")
        prob += (v.e_minus[ligne] <= tol * plan, f"C04_tol_inf_{ligne}")

        # Les échelons cocristallisants tournent au plan : ils doivent être
        # alimentés en acide standard à hauteur de leur production planifiée.
        prob += (
            v.x_std[ligne] >= _pi_coc(v, params, ligne54),
            f"C04b_alim_coc_{ligne}",
        )


def c05_limite_acide_dec_concentration(
    prob, v: Variables, scenario: Scenario, params: ParametresDerives
) -> None:
    """L'acide décadmié n'emprunte que les échelons non cocristallisants.

    Un acide cocristallisé ne peut pas être clarifié ; y envoyer du décadmié
    produirait un acide impossible à traiter ensuite (hypothèse H3).
    Par ailleurs, seules les lignes habilitées produisent du DEC_CL.
    """
    for ligne in C.LIGNES_29_AVEC_54:
        ligne54 = C.SIGMA[ligne]
        if ligne54 in scenario.dec_cl_active:
            # En mode décidable, éteindre un échelon cocristallisant libère de la
            # capacité pour l'acide décadmié : la borne suit donc Pi_coc.
            prob += (
                v.x_dec[ligne] <= params.production_54[ligne54] - _pi_coc(v, params, ligne54),
                f"C05_dec_sur_echelons_ncl_{ligne}",
            )
        else:
            prob += (v.x_dec[ligne] == 0, f"C05_pas_de_deccl_{ligne}")


# ─────────────────────────────────────────────────────────────────────────────
# C7, C8, C9 — Bilans et bornes au niveau de l'acide 29
# ─────────────────────────────────────────────────────────────────────────────

def c07_bilan_acide_29_std(
    prob, v: Variables, scenario: Scenario, params: ParametresDerives
) -> None:
    """Bilan matière du stock d'acide 29 standard de chaque ligne.

    Six flux entrants et deux sortants. Les trois termes faciles à oublier :
    la boue de clarification de l'acide **décadmié**, le retour d'EMAPHOS qui
    remonte du niveau 54 vers le niveau 29, et le sens des indices de transfert.
    """
    livraison_emaphos = _livraison_emaphos(v)

    for ligne in C.LIGNES_29:
        ligne54 = C.SIGMA[ligne]

        production_std = scenario.production_29[ligne] - v.d[ligne]
        entrants = pulp.lpSum(
            v.t[(origine, ligne)] for (origine, dest) in v.t if dest == ligne
        )
        sortants = pulp.lpSum(
            v.t[(ligne, dest)] for (origine, dest) in v.t if origine == ligne
        )

        boue_coc = _boue_coc(v, params, ligne54) if ligne54 else 0.0
        boue_clarif = (
            C.BOUE_CLARIFICATION * _entree_clarification_totale(v, ligne54)
            if ligne54
            else pulp.LpAffineExpression()
        )
        retour_emaphos = C.RETOURS_EMAPHOS.get(ligne, 0.0) * livraison_emaphos

        vers_concentration = v.x_std.get(ligne, pulp.LpAffineExpression())
        vers_clients = pulp.lpSum(
            var for (acide, source, _), var in v.y_loc.items()
            if acide == C.ACIDE_29_STD and source == ligne
        )

        prob += (
            v.s_std[ligne]
            == scenario.stock_29_std_initial[ligne]
            + production_std
            + entrants
            - sortants
            + boue_coc
            + boue_clarif
            + retour_emaphos
            - vers_concentration
            - vers_clients,
            f"C07_bilan_29_std_{ligne}",
        )


def c08_bilan_acide_29_dec(prob, v: Variables, scenario: Scenario) -> None:
    """Bilan matière du stock d'acide 29 décadmié.

    Bien plus simple que le standard : l'acide décadmié ne se transfère pas entre
    lignes et ne reçoit aucune boue (les boues sont de qualité standard).
    """
    for ligne in C.LIGNES_29:
        vers_concentration = v.x_dec.get(ligne, pulp.LpAffineExpression())
        vers_clients = pulp.lpSum(
            var for (acide, source, _), var in v.y_loc.items()
            if acide == C.ACIDE_29_DEC and source == ligne
        )
        prob += (
            v.s_dec[ligne]
            == scenario.stock_29_dec_initial[ligne]
            + v.d[ligne]
            - vers_concentration
            - vers_clients,
            f"C08_bilan_29_dec_{ligne}",
        )


def c09_bornes_stock_29(prob, v: Variables) -> None:
    """Bande de sécurité des cuves d'acide 29.

    La borne porte sur la **somme** des deux qualités : elles sont suivies
    séparément mais partagent physiquement les mêmes cuves. Borner chacune
    séparément autoriserait le double du volume réel.

    Contraintes molles : le dépassement est possible mais pénalisé au niveau 2.
    """
    z_min, z_max = units.bornes_stock_29()
    for ligne in C.LIGNES_29:
        total = v.s_std[ligne] + v.s_dec[ligne]
        prob += (total <= z_max + v.nu_plus[ligne], f"C09_max_{ligne}")
        prob += (total >= z_min - v.nu_minus[ligne], f"C09_min_{ligne}")


# ─────────────────────────────────────────────────────────────────────────────
# C10, C11, C17 — Niveau de l'acide 54
# ─────────────────────────────────────────────────────────────────────────────

def c10_bilan_acide_54_ncl(
    prob, v: Variables, scenario: Scenario, params: ParametresDerives
) -> None:
    """Bilan matière du stock local d'acide 54 NCL.

    Aucune boue n'y revient (elles remontent au niveau 29, décision D-05), et le
    54 NCL décadmié n'y transite jamais : il part directement en clarification.
    """
    for ligne in C.LIGNES_54:
        vers_clients = pulp.lpSum(
            var for (acide, source, _), var in v.y_loc.items()
            if acide == C.ACIDE_54_NCL and source == ligne
        )
        prob += (
            v.s_ncl[ligne]
            == scenario.stock_54_ncl_initial[ligne]
            + _ncl_produit(v, params, ligne)
            - v.u_ncl.get(ligne, pulp.LpAffineExpression())
            - vers_clients,
            f"C10_bilan_54_ncl_{ligne}",
        )


def c11_capacite_decanteurs(prob, v: Variables, scenario: Scenario) -> None:
    """Capacité entrante des décanteurs, partagée entre les deux clarifications.

    C'est la contrainte structurante du modèle : décadmier davantage consomme de
    la capacité de décantation et réduit d'autant la production d'acide clarifié.
    """
    for ligne in C.LIGNES_54:
        entree = _entree_clarification_totale(v, ligne)
        if ligne in scenario.clarification_active:
            prob += (
                entree <= C.CAPACITE_DECANTEURS_PAR_LIGNE,
                f"C11_decanteurs_{ligne}",
            )
        else:
            prob += (entree == 0, f"C11_pas_de_clarification_{ligne}")


def c17_bornes_stock_54(prob, v: Variables) -> None:
    """Bande de sécurité des cuves d'acide 54 NCL (contraintes molles)."""
    z_min, z_max = units.bornes_stock_54()
    for ligne in C.LIGNES_54:
        prob += (v.s_ncl[ligne] <= z_max + v.nu_plus[ligne], f"C17_max_{ligne}")
        prob += (v.s_ncl[ligne] >= z_min - v.nu_minus[ligne], f"C17_min_{ligne}")


# ─────────────────────────────────────────────────────────────────────────────
# C12, C13, C15 — Stockages centraux
# ─────────────────────────────────────────────────────────────────────────────

def c12_bilan_ir12(prob, v: Variables, scenario: Scenario) -> None:
    """Bilan et bande de sécurité d'IR12, qui reçoit l'acide clarifié ordinaire."""
    prob += (
        v.s12
        == scenario.stock_ir12_initial
        + C.RENDEMENT_CLARIFICATION * pulp.lpSum(v.u_ncl.values())
        - pulp.lpSum(v.y_cl.values()),
        "C12_bilan_IR12",
    )
    z_min, z_max = units.bornes_stock_ir12()
    prob += (v.s12 <= z_max + v.nu_plus["IR12"], "C12_max_IR12")
    prob += (v.s12 >= z_min - v.nu_minus["IR12"], "C12_min_IR12")


def c13_bilan_ir11(prob, v: Variables, scenario: Scenario, params: ParametresDerives) -> None:
    """Bilan et bande de sécurité d'IR11, qui mélange CoC et DEC_CL.

    Les deux produits sont suivis séparément — ils n'ont pas la même origine —
    mais une **seule** contrainte de capacité porte sur leur somme : c'est un
    bac unique.
    """
    entree_deccl = C.RENDEMENT_CLARIFICATION * pulp.lpSum(
        _clarification_dec(v, ligne) for ligne in C.LIGNES_54
    )

    prob += (
        v.s11_coc
        == scenario.stock_ir11_initial          # hypothèse H4 : initial = CoC
        + _coc_total(v, params)
        - pulp.lpSum(v.y_coc.values()),
        "C13_bilan_IR11_coc",
    )
    prob += (
        v.s11_deccl == entree_deccl - pulp.lpSum(v.y_deccl.values()),
        "C13_bilan_IR11_deccl",
    )

    z_min, z_max = units.bornes_stock_ir11()
    total = v.s11_coc + v.s11_deccl
    prob += (total <= z_max + v.nu_plus["IR11"], "C13_max_IR11")
    prob += (total >= z_min - v.nu_minus["IR11"], "C13_min_IR11")


def c15_qualite_ir11(prob, v: Variables, scenario: Scenario, params: ParametresDerives) -> None:
    """Le DEC_CL doit représenter au moins une part alpha des entrées d'IR11.

    Sans cette contrainte, l'optimiseur ne produirait jamais de DEC_CL : la
    cocristallisation systématique couvre déjà tout le besoin en acide de qualité
    décadmiée, si bien que produire du DEC_CL est pour lui un coût sans bénéfice.
    Il violerait donc la règle métier. Voir décision D-09.

    Forme linéaire obtenue en réarrangeant  ``deccl >= alpha * (coc + deccl)``.
    """
    alpha = scenario.alpha_dec_cl
    if alpha <= 0.0:
        return

    entree_deccl = C.RENDEMENT_CLARIFICATION * pulp.lpSum(
        _clarification_dec(v, ligne) for ligne in C.LIGNES_54
    )
    prob += (
        (1.0 - alpha) * entree_deccl >= alpha * _coc_total(v, params),
        "C15_qualite_IR11",
    )


# ─────────────────────────────────────────────────────────────────────────────
# C14 — Satisfaction de la demande
# ─────────────────────────────────────────────────────────────────────────────

def c14_satisfaction_demande(
    prob, v: Variables, scenario: Scenario, params: ParametresDerives
) -> None:
    """Chaque besoin est couvert par la somme des livraisons autorisées.

    Le cas de ``acid_54_dec_total`` est le plus intéressant : le besoin porte sur
    une **propriété** (« acide 54 de qualité décadmiée »), que deux produits
    physiquement distincts possèdent. La contrainte porte donc sur la **somme**
    de deux variables, ce qui exprime leur substituabilité.
    """
    for consommateur, besoins in params.besoins.items():
        for acide, requis in besoins.items():
            manque = v.rho[(consommateur, acide)]

            if acide in C.ACIDES_LOCAUX:
                livre = pulp.lpSum(
                    v.y_loc[(acide, ligne, consommateur)]
                    for ligne in sources_autorisees(scenario, consommateur, acide)
                    if (acide, ligne, consommateur) in v.y_loc
                )
            elif acide == C.ACIDE_54_CL:
                livre = v.y_cl[consommateur]
            elif acide == C.ACIDE_54_COC:
                livre = v.y_coc[(consommateur, "direct")]
            elif acide == C.ACIDE_54_DEC_CL:
                livre = v.y_deccl[(consommateur, "direct")]
            elif acide == C.BESOIN_54_DEC_TOTAL:
                livre = (
                    v.y_coc[(consommateur, "dectot")]
                    + v.y_deccl[(consommateur, "dectot")]
                )
            else:
                raise ValueError(f"Type d'acide inconnu dans la demande : {acide}")

            prob += (livre + manque == requis, f"C14_demande_{consommateur}_{acide}")


# ─────────────────────────────────────────────────────────────────────────────
# C16 — Transferts semi-continus
# ─────────────────────────────────────────────────────────────────────────────

def c16_transferts_semi_continus(prob, v: Variables, scenario: Scenario) -> None:
    """Un transfert est soit nul, soit compris entre le minimum et le maximum.

    Si ``b = 0`` alors ``0 <= t <= 0`` donc ``t = 0`` ; si ``b = 1`` alors
    ``tau_min <= t <= tau_max``. Ces deux cas sont exactement ceux voulus, et
    aucun autre n'est atteignable.
    """
    for arc, transfert in v.t.items():
        actif = v.b[arc]
        prob += (transfert >= scenario.transfert_min * actif, f"C16_min_{arc[0]}_{arc[1]}")
        prob += (transfert <= scenario.transfert_max * actif, f"C16_max_{arc[0]}_{arc[1]}")


# ─────────────────────────────────────────────────────────────────────────────
# Écart des stocks finaux à leur cible (support du niveau 3 de l'objectif)
# ─────────────────────────────────────────────────────────────────────────────

def ecarts_aux_cibles(prob, v: Variables) -> None:
    """Décompose l'écart de chaque stock final à sa cible en parts positive et négative.

    La cible est le milieu de la bande de sécurité : c'est la position qui laisse
    le maximum de marge dans les deux sens pour le lendemain.

    Linéarisation de la valeur absolue : on pose ``S - cible = g+ - g-`` avec
    ``g+, g- >= 0``. Comme le niveau 3 **minimise** ``g+ + g-``, l'optimum ne rend
    jamais les deux simultanément positifs, si bien que ``g+ + g-`` vaut
    exactement ``|S - cible|``.
    """
    z_min_29, z_max_29 = units.bornes_stock_29()
    z_min_54, z_max_54 = units.bornes_stock_54()
    z_min_11, z_max_11 = units.bornes_stock_ir11()
    z_min_12, z_max_12 = units.bornes_stock_ir12()

    def _poser(nom: str, expression, borne_min: float, borne_max: float) -> None:
        # `prob.addConstraint` plutôt que `prob += ...` : dans une fonction imbriquée,
        # l'affectation augmentée rebinderait `prob` en variable locale.
        cible = 0.5 * (borne_min + borne_max)
        prob.addConstraint(
            expression - cible == v.g_plus[nom] - v.g_minus[nom], f"CIBLE_{nom}"
        )

    for ligne in C.LIGNES_29:
        _poser(ligne, v.s_std[ligne] + v.s_dec[ligne], z_min_29, z_max_29)
    for ligne in C.LIGNES_54:
        _poser(ligne, v.s_ncl[ligne], z_min_54, z_max_54)
    _poser("IR11", v.s11_coc + v.s11_deccl, z_min_11, z_max_11)
    _poser("IR12", v.s12, z_min_12, z_max_12)


# ─────────────────────────────────────────────────────────────────────────────
# Assemblage
# ─────────────────────────────────────────────────────────────────────────────

def ajouter_toutes_les_contraintes(
    prob, v: Variables, scenario: Scenario, params: ParametresDerives
) -> None:
    """Ajoute au problème l'intégralité des familles de contraintes, dans l'ordre."""
    c02_choix_niveau_decadmiation(prob, v, scenario)
    c03_faisabilite_decadmiation(prob, v, scenario)
    c04_charge_concentration(prob, v, scenario, params)
    c05_limite_acide_dec_concentration(prob, v, scenario, params)
    c07_bilan_acide_29_std(prob, v, scenario, params)
    c08_bilan_acide_29_dec(prob, v, scenario)
    c09_bornes_stock_29(prob, v)
    c10_bilan_acide_54_ncl(prob, v, scenario, params)
    c11_capacite_decanteurs(prob, v, scenario)
    c12_bilan_ir12(prob, v, scenario)
    c13_bilan_ir11(prob, v, scenario, params)
    c14_satisfaction_demande(prob, v, scenario, params)
    c15_qualite_ir11(prob, v, scenario, params)
    c16_transferts_semi_continus(prob, v, scenario)
    c17_bornes_stock_54(prob, v)
    ecarts_aux_cibles(prob, v)
