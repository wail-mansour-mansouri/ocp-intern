"""Déclaration des variables de décision du modèle.

Toutes les variables sont positives ou nulles, sauf les binaires qui vivent dans
{0, 1}. Les notations suivent celles du document `docs-helper/05_MODELE_MATHEMATIQUE.md`.

Principe d'économie : une variable n'est créée que si elle peut être non nulle.
Les livraisons non autorisées par les matrices d'interconnexion ne sont pas créées
du tout, plutôt que créées puis contraintes à zéro.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pulp

from .. import constants as C
from ..preprocessing import ParametresDerives
from ..scenario import Scenario

__all__ = ["Variables", "creer_variables", "sources_autorisees"]


def sources_autorisees(scenario: Scenario, consommateur: str, acide: str) -> tuple[str, ...]:
    """Lignes autorisées à livrer un acide local donné à un consommateur donné.

    Args:
        scenario: scénario courant (il porte la liste des lignes habilitées).
        consommateur: nom du consommateur.
        acide: l'un des types de `constants.ACIDES_LOCAUX`.

    Returns:
        Les lignes sources autorisées, éventuellement vide.
    """
    if acide == C.ACIDE_29_STD:
        return C.CONNEXIONS_29.get(consommateur, ())
    if acide == C.ACIDE_29_DEC:
        # Doublement filtré : la ligne doit être raccordée **et** habilitée à
        # envoyer de l'acide décadmié vers les engrais (anomalie A-09).
        raccordees = C.CONNEXIONS_29.get(consommateur, ())
        return tuple(l for l in raccordees if l in scenario.dec29_vers_engrais)
    if acide == C.ACIDE_54_NCL:
        return C.CONNEXIONS_54.get(consommateur, ())
    return ()


@dataclass
class Variables:
    """Ensemble des variables de décision du modèle.

    Attributes:
        w: ``w[(ligne, niveau)]`` — binaire, choix du niveau de décadmiation.
        d: ``d[ligne]`` — expression affine donnant la quantité décadmiée.
        x_std: ``x_std[ligne29]`` — acide 29 standard envoyé en concentration.
        x_dec: ``x_dec[ligne29]`` — acide 29 décadmié envoyé en concentration.
        t: ``t[(origine, destination)]`` — transfert interzone.
        b: ``b[(origine, destination)]`` — binaire d'activation du transfert.
        u_ncl: ``u_ncl[ligne54]`` — NCL envoyé en clarification.
        y_loc: ``y_loc[(acide, ligne, consommateur)]`` — livraison depuis un stock local.
        y_cl: ``y_cl[consommateur]`` — livraison de CL depuis IR12.
        y_coc: ``y_coc[(consommateur, motif)]`` — livraison de CoC depuis IR11.
        y_deccl: ``y_deccl[(consommateur, motif)]`` — livraison de DEC_CL depuis IR11.
        s_std, s_dec, s_ncl: stocks finaux locaux.
        s11_coc, s11_deccl, s12: stocks finaux centraux.
        rho: ``rho[(consommateur, acide)]`` — demande non satisfaite.
        nu_plus, nu_minus: dépassement / sous-passement des bandes de stock.
        g_plus, g_minus: écart signé du stock final à sa cible (niveau 3).
        e_plus, e_minus: écart à la charge de concentration planifiée.
    """

    w: dict[tuple[str, float], pulp.LpVariable] = field(default_factory=dict)
    d: dict[str, pulp.LpAffineExpression] = field(default_factory=dict)
    x_std: dict[str, pulp.LpVariable] = field(default_factory=dict)
    x_dec: dict[str, pulp.LpVariable] = field(default_factory=dict)
    t: dict[tuple[str, str], pulp.LpVariable] = field(default_factory=dict)
    b: dict[tuple[str, str], pulp.LpVariable] = field(default_factory=dict)
    u_ncl: dict[str, pulp.LpVariable] = field(default_factory=dict)
    y_loc: dict[tuple[str, str, str], pulp.LpVariable] = field(default_factory=dict)
    y_cl: dict[str, pulp.LpVariable] = field(default_factory=dict)
    y_coc: dict[tuple[str, str], pulp.LpVariable] = field(default_factory=dict)
    y_deccl: dict[tuple[str, str], pulp.LpVariable] = field(default_factory=dict)
    s_std: dict[str, pulp.LpVariable] = field(default_factory=dict)
    s_dec: dict[str, pulp.LpVariable] = field(default_factory=dict)
    s_ncl: dict[str, pulp.LpVariable] = field(default_factory=dict)
    s11_coc: pulp.LpVariable | None = None
    s11_deccl: pulp.LpVariable | None = None
    s12: pulp.LpVariable | None = None
    rho: dict[tuple[str, str], pulp.LpVariable] = field(default_factory=dict)
    nu_plus: dict[str, pulp.LpVariable] = field(default_factory=dict)
    nu_minus: dict[str, pulp.LpVariable] = field(default_factory=dict)
    g_plus: dict[str, pulp.LpVariable] = field(default_factory=dict)
    g_minus: dict[str, pulp.LpVariable] = field(default_factory=dict)
    e_plus: dict[str, pulp.LpVariable] = field(default_factory=dict)
    e_minus: dict[str, pulp.LpVariable] = field(default_factory=dict)


def _positive(nom: str, borne_sup: float | None = None) -> pulp.LpVariable:
    """Crée une variable continue positive ou nulle."""
    return pulp.LpVariable(nom, lowBound=0.0, upBound=borne_sup, cat=pulp.LpContinuous)


def creer_variables(scenario: Scenario, params: ParametresDerives) -> Variables:
    """Instancie toutes les variables de décision du modèle.

    Args:
        scenario: scénario validé.
        params: paramètres dérivés (production d'acide 54, besoins consolidés…).

    Returns:
        Le conteneur `Variables` peuplé.
    """
    v = Variables()

    # ── Décadmiation (C2) : encodage « one-hot » d'un choix discret ──────────
    for ligne in scenario.decadmiation_equipee:
        for niveau in C.NIVEAUX_DECADMIATION:
            v.w[(ligne, niveau)] = pulp.LpVariable(
                f"w_{ligne}_{int(niveau)}", cat=pulp.LpBinary
            )
    for ligne in C.LIGNES_29:
        if ligne in scenario.decadmiation_equipee:
            v.d[ligne] = pulp.lpSum(
                niveau * v.w[(ligne, niveau)] for niveau in C.NIVEAUX_DECADMIATION
            )
        else:
            v.d[ligne] = pulp.LpAffineExpression()  # identiquement nulle

    # ── Concentration ───────────────────────────────────────────────────────
    for ligne in C.LIGNES_29_AVEC_54:
        plafond = params.production_54[C.SIGMA[ligne]] * (1.0 + scenario.tolerance_concentration)
        v.x_std[ligne] = _positive(f"x_std_{ligne}", plafond)
        v.x_dec[ligne] = _positive(f"x_dec_{ligne}", plafond)
        v.e_plus[ligne] = _positive(f"e_plus_{ligne}")
        v.e_minus[ligne] = _positive(f"e_minus_{ligne}")

    # ── Transferts interzones (C16), variables semi-continues ───────────────
    for origine, destination in C.arcs_interzone():
        v.t[(origine, destination)] = _positive(
            f"t_{origine}_{destination}", scenario.transfert_max
        )
        v.b[(origine, destination)] = pulp.LpVariable(
            f"b_{origine}_{destination}", cat=pulp.LpBinary
        )

    # ── Clarification (C11) ─────────────────────────────────────────────────
    for ligne in scenario.clarification_active:
        v.u_ncl[ligne] = _positive(f"u_ncl_{ligne}", C.CAPACITE_DECANTEURS_PAR_LIGNE)

    # ── Livraisons ──────────────────────────────────────────────────────────
    for consommateur, besoins in params.besoins.items():
        for acide in besoins:
            if acide in C.ACIDES_LOCAUX:
                for ligne in sources_autorisees(scenario, consommateur, acide):
                    v.y_loc[(acide, ligne, consommateur)] = _positive(
                        f"y_{acide}_{ligne}_{consommateur}"
                    )
            elif acide == C.ACIDE_54_CL:
                v.y_cl[consommateur] = _positive(f"y_cl_{consommateur}")
            elif acide == C.ACIDE_54_COC:
                v.y_coc[(consommateur, "direct")] = _positive(f"y_coc_direct_{consommateur}")
            elif acide == C.ACIDE_54_DEC_CL:
                v.y_deccl[(consommateur, "direct")] = _positive(
                    f"y_deccl_direct_{consommateur}"
                )
            elif acide == C.BESOIN_54_DEC_TOTAL:
                # Substituabilité : le besoin porte sur une propriété, que deux
                # produits distincts d'IR11 possèdent indifféremment.
                v.y_coc[(consommateur, "dectot")] = _positive(f"y_coc_dectot_{consommateur}")
                v.y_deccl[(consommateur, "dectot")] = _positive(
                    f"y_deccl_dectot_{consommateur}"
                )
            v.rho[(consommateur, acide)] = _positive(f"rho_{consommateur}_{acide}")

    # ── Stocks finaux ───────────────────────────────────────────────────────
    for ligne in C.LIGNES_29:
        v.s_std[ligne] = _positive(f"s_std_{ligne}")
        v.s_dec[ligne] = _positive(f"s_dec_{ligne}")
    for ligne in C.LIGNES_54:
        v.s_ncl[ligne] = _positive(f"s_ncl_{ligne}")
    v.s11_coc = _positive("s11_coc")
    v.s11_deccl = _positive("s11_deccl")
    v.s12 = _positive("s12")

    # ── Écarts aux bandes de stock et aux cibles ────────────────────────────
    for cuve in list(C.LIGNES_29) + list(C.LIGNES_54) + ["IR11", "IR12"]:
        v.nu_plus[cuve] = _positive(f"nu_plus_{cuve}")
        v.nu_minus[cuve] = _positive(f"nu_minus_{cuve}")
        v.g_plus[cuve] = _positive(f"g_plus_{cuve}")
        v.g_minus[cuve] = _positive(f"g_minus_{cuve}")

    return v
