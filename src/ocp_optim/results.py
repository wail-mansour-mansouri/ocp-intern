"""Extraction structurée de la solution.

Transforme le dictionnaire brut « nom de variable -> valeur » renvoyé par le
solveur en objets métier lisibles, exploitables aussi bien par le validateur que
par le générateur de rapport.

Cette couche existe pour une raison précise : le validateur doit pouvoir recalculer
les bilans matière **sans relire les contraintes du modèle**. Si la formulation
contient une erreur, le solveur renverra une solution « optimale » pour un mauvais
problème ; seul un contrôle mené à partir des équations physiques peut le détecter.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import constants as C
from .model import ModeleOptimisation
from .solver import Solution

__all__ = ["Resultat", "ResultatLigne29", "ResultatLigne54", "ResultatCentral", "extraire"]


@dataclass
class ResultatLigne29:
    """Flux et stocks d'une ligne d'acide 29, en tonnes de P2O5."""

    ligne: str
    production_totale: float
    decadmiation: float
    stock_initial_std: float
    stock_initial_dec: float
    transferts_entrants: float
    transferts_sortants: float
    boue_cocristallisation: float
    boue_clarification: float
    retour_emaphos: float
    vers_concentration_std: float
    vers_concentration_dec: float
    livraisons_std: dict[str, float] = field(default_factory=dict)
    livraisons_dec: dict[str, float] = field(default_factory=dict)
    stock_final_std: float = 0.0
    stock_final_dec: float = 0.0

    @property
    def production_std(self) -> float:
        """Part de la production restée standard."""
        return self.production_totale - self.decadmiation

    @property
    def total_livraisons_std(self) -> float:
        return sum(self.livraisons_std.values())

    @property
    def total_livraisons_dec(self) -> float:
        return sum(self.livraisons_dec.values())


@dataclass
class ResultatLigne54:
    """Flux et stocks d'une ligne d'acide 54, en tonnes de P2O5."""

    ligne: str
    production_planifiee: float
    charge_reelle: float
    ncl_produit: float
    coc_entree: float
    coc_produit: float
    stock_initial_ncl: float
    clarification_ncl: float
    clarification_dec: float
    livraisons_ncl: dict[str, float] = field(default_factory=dict)
    stock_final_ncl: float = 0.0

    @property
    def total_livraisons_ncl(self) -> float:
        return sum(self.livraisons_ncl.values())

    @property
    def cl_produit(self) -> float:
        """Acide clarifié ordinaire envoyé vers IR12."""
        return C.RENDEMENT_CLARIFICATION * self.clarification_ncl

    @property
    def dec_cl_produit(self) -> float:
        """Acide décadmié clarifié envoyé vers IR11."""
        return C.RENDEMENT_CLARIFICATION * self.clarification_dec

    @property
    def taux_occupation_decanteurs(self) -> float:
        """Part de la capacité de décantation utilisée, entre 0 et 1."""
        return (self.clarification_ncl + self.clarification_dec) / C.CAPACITE_DECANTEURS_PAR_LIGNE


@dataclass
class ResultatCentral:
    """Flux et stocks d'un bac central."""

    nom: str
    stock_initial: float
    entrees: dict[str, float] = field(default_factory=dict)
    livraisons: dict[str, float] = field(default_factory=dict)
    stock_final: float = 0.0
    capacite: float = 0.0

    @property
    def total_entrees(self) -> float:
        return sum(self.entrees.values())

    @property
    def total_livraisons(self) -> float:
        return sum(self.livraisons.values())

    @property
    def taux_remplissage(self) -> float:
        return self.stock_final / self.capacite if self.capacite else 0.0


@dataclass
class Resultat:
    """Solution complète, structurée.

    Attributes:
        lignes_29: résultats indexés par ligne d'acide 29.
        lignes_54: résultats indexés par ligne d'acide 54.
        ir11, ir12: résultats des bacs centraux.
        transferts: ``{(origine, destination): quantité}``, transferts non nuls.
        besoins: besoin de chaque consommateur, par type d'acide.
        livraisons: livraison effective, par consommateur et type d'acide.
        manques: demande non satisfaite, par consommateur et type d'acide.
        violations_bandes: dépassement net de chaque bande de sécurité.
        ecarts_charge: écart à la charge de concentration planifiée, par ligne.
        f1, f2, f3: valeurs des trois niveaux de l'objectif.
        duree_s: temps de résolution.
    """

    lignes_29: dict[str, ResultatLigne29]
    lignes_54: dict[str, ResultatLigne54]
    ir11: ResultatCentral
    ir12: ResultatCentral
    transferts: dict[tuple[str, str], float]
    besoins: dict[str, dict[str, float]]
    livraisons: dict[str, dict[str, float]]
    manques: dict[str, dict[str, float]]
    violations_bandes: dict[str, float]
    ecarts_charge: dict[str, float]
    f1: float
    f2: float
    f3: float
    duree_s: float


def _v(solution: Solution, nom: str) -> float:
    """Valeur d'une variable par son nom, 0 si absente du modèle."""
    return solution.valeurs.get(nom, 0.0)


def extraire(modele: ModeleOptimisation, solution: Solution) -> Resultat:
    """Reconstruit une vue métier de la solution.

    Args:
        modele: le modèle résolu (il porte le scénario et les paramètres dérivés).
        solution: la solution renvoyée par le solveur.

    Returns:
        La solution structurée.
    """
    scenario, params, v = modele.scenario, modele.params, modele.variables

    # ── Transferts ──────────────────────────────────────────────────────────
    transferts = {
        arc: _v(solution, var.name)
        for arc, var in v.t.items()
        if _v(solution, var.name) > 1e-6
    }

    # ── Livraisons depuis les stocks locaux ─────────────────────────────────
    livraisons_locales: dict[tuple[str, str, str], float] = {
        cle: _v(solution, var.name) for cle, var in v.y_loc.items()
    }

    livraison_emaphos_totale = sum(
        q for (acide, _, k), q in livraisons_locales.items()
        if acide == C.ACIDE_54_NCL and k == "EMAPHOS"
    )

    # ── Cocristallisation effectivement mise en service ─────────────────────
    #
    # En mode subi, c'est le paramètre calculé en prétraitement. En mode
    # décidable (D-11), il faut relire les binaires d'activation : le modèle a
    # pu éteindre une partie des échelons candidats.
    if v.z:
        pi_coc = {
            ligne: sum(
                params.production_echelon[e] * _v(solution, v.z[e].name)
                for e in params.echelons_coc_candidats.get(ligne, ())
            )
            for ligne in C.LIGNES_54
        }
    else:
        pi_coc = dict(params.production_54_coc)

    coc_produit = {m: C.RENDEMENT_COCRISTALLISATION * q for m, q in pi_coc.items()}
    boue_coc = {m: C.BOUE_COCRISTALLISATION * q for m, q in pi_coc.items()}
    coc_total = sum(coc_produit.values())

    # ── Lignes d'acide 54 ───────────────────────────────────────────────────
    lignes_54: dict[str, ResultatLigne54] = {}
    for ligne in C.LIGNES_54:
        ligne29 = C.SIGMA_INV[ligne]
        x_std = _v(solution, v.x_std[ligne29].name) if ligne29 in v.x_std else 0.0
        x_dec = _v(solution, v.x_dec[ligne29].name) if ligne29 in v.x_dec else 0.0
        u_ncl = _v(solution, v.u_ncl[ligne].name) if ligne in v.u_ncl else 0.0

        lignes_54[ligne] = ResultatLigne54(
            ligne=ligne,
            production_planifiee=params.production_54[ligne],
            charge_reelle=x_std + x_dec,
            ncl_produit=x_std - pi_coc[ligne],
            coc_entree=pi_coc[ligne],
            coc_produit=coc_produit[ligne],
            stock_initial_ncl=scenario.stock_54_ncl_initial[ligne],
            clarification_ncl=u_ncl,
            clarification_dec=x_dec,
            livraisons_ncl={
                k: q for (acide, source, k), q in livraisons_locales.items()
                if acide == C.ACIDE_54_NCL and source == ligne and q > 1e-6
            },
            stock_final_ncl=_v(solution, v.s_ncl[ligne].name),
        )

    # ── Lignes d'acide 29 ───────────────────────────────────────────────────
    lignes_29: dict[str, ResultatLigne29] = {}
    for ligne in C.LIGNES_29:
        ligne54 = C.SIGMA[ligne]
        decad = sum(
            niveau * _v(solution, v.w[(ligne, niveau)].name)
            for niveau in C.NIVEAUX_DECADMIATION
            if (ligne, niveau) in v.w
        )
        clarif_totale = (
            lignes_54[ligne54].clarification_ncl + lignes_54[ligne54].clarification_dec
            if ligne54 else 0.0
        )

        lignes_29[ligne] = ResultatLigne29(
            ligne=ligne,
            production_totale=scenario.production_29[ligne],
            decadmiation=decad,
            stock_initial_std=scenario.stock_29_std_initial[ligne],
            stock_initial_dec=scenario.stock_29_dec_initial[ligne],
            transferts_entrants=sum(q for (o, d), q in transferts.items() if d == ligne),
            transferts_sortants=sum(q for (o, d), q in transferts.items() if o == ligne),
            boue_cocristallisation=boue_coc[ligne54] if ligne54 else 0.0,
            boue_clarification=C.BOUE_CLARIFICATION * clarif_totale,
            retour_emaphos=C.RETOURS_EMAPHOS.get(ligne, 0.0) * livraison_emaphos_totale,
            vers_concentration_std=_v(solution, v.x_std[ligne].name) if ligne in v.x_std else 0.0,
            vers_concentration_dec=_v(solution, v.x_dec[ligne].name) if ligne in v.x_dec else 0.0,
            livraisons_std={
                k: q for (acide, source, k), q in livraisons_locales.items()
                if acide == C.ACIDE_29_STD and source == ligne and q > 1e-6
            },
            livraisons_dec={
                k: q for (acide, source, k), q in livraisons_locales.items()
                if acide == C.ACIDE_29_DEC and source == ligne and q > 1e-6
            },
            stock_final_std=_v(solution, v.s_std[ligne].name),
            stock_final_dec=_v(solution, v.s_dec[ligne].name),
        )

    # ── Bacs centraux ───────────────────────────────────────────────────────
    from . import units

    dec_cl_total = C.RENDEMENT_CLARIFICATION * sum(
        r.clarification_dec for r in lignes_54.values()
    )
    cl_total = C.RENDEMENT_CLARIFICATION * sum(r.clarification_ncl for r in lignes_54.values())

    # Un même consommateur peut être servi à la fois en CoC et en DEC_CL (cas du
    # besoin `acid_54_dec_total`, satisfiable indifféremment par l'un ou l'autre).
    # Les deux livraisons doivent donc être **cumulées** sur la clé du consommateur.
    livraisons_ir11: dict[str, float] = {}
    for cle, var in list(v.y_coc.items()) + list(v.y_deccl.items()):
        consommateur = cle[0]
        livraisons_ir11[consommateur] = livraisons_ir11.get(consommateur, 0.0) + _v(
            solution, var.name
        )

    ir11 = ResultatCentral(
        nom="IR11",
        stock_initial=scenario.stock_ir11_initial,
        entrees={"CoC": coc_total, "DEC_CL": dec_cl_total},
        livraisons={k: q for k, q in livraisons_ir11.items() if q > 1e-6},
        stock_final=_v(solution, v.s11_coc.name) + _v(solution, v.s11_deccl.name),
        capacite=units.bornes_stock_ir11()[1],
    )
    ir12 = ResultatCentral(
        nom="IR12",
        stock_initial=scenario.stock_ir12_initial,
        entrees={"CL": cl_total},
        livraisons={
            k: _v(solution, var.name)
            for k, var in v.y_cl.items() if _v(solution, var.name) > 1e-6
        },
        stock_final=_v(solution, v.s12.name),
        capacite=units.bornes_stock_ir12()[1],
    )

    # ── Demande : besoins, livraisons effectives, manques ───────────────────
    livraisons: dict[str, dict[str, float]] = {}
    manques: dict[str, dict[str, float]] = {}
    for consommateur, besoins_k in params.besoins.items():
        livraisons[consommateur] = {}
        manques[consommateur] = {}
        for acide, requis in besoins_k.items():
            manque = _v(solution, v.rho[(consommateur, acide)].name)
            livraisons[consommateur][acide] = requis - manque
            manques[consommateur][acide] = manque

    # ── Écarts aux contraintes molles ───────────────────────────────────────
    violations = {
        cuve: _v(solution, v.nu_plus[cuve].name) + _v(solution, v.nu_minus[cuve].name)
        for cuve in v.nu_plus
    }
    ecarts_charge = {
        ligne: _v(solution, v.e_plus[ligne].name) - _v(solution, v.e_minus[ligne].name)
        for ligne in v.e_plus
    }

    return Resultat(
        lignes_29=lignes_29,
        lignes_54=lignes_54,
        ir11=ir11,
        ir12=ir12,
        transferts=transferts,
        besoins=params.besoins,
        livraisons=livraisons,
        manques=manques,
        violations_bandes={c: q for c, q in violations.items() if q > 1e-6},
        ecarts_charge={l: q for l, q in ecarts_charge.items() if abs(q) > 1e-6},
        f1=solution.f1,
        f2=solution.f2,
        f3=solution.f3,
        duree_s=solution.duree_s,
    )
