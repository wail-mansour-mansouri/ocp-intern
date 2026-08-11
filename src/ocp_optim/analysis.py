"""Analyses post-optimisation : goulots d'étranglement et sensibilité.

Deux questions auxquelles ce module répond :

1. **Qu'est-ce qui limite réellement le système ?** Les contraintes saturées à
   l'optimum sont les seules qui bornent la performance : ce sont elles, et elles
   seules, qu'il vaut la peine de desserrer.

2. **Que change mon ignorance ?** Plusieurs paramètres du modèle sont des valeurs
   d'attente, faute de donnée fournie (`alpha`, `transfert_max`). La réponse
   méthodologique correcte n'est pas de deviner leur valeur, mais de mesurer
   l'influence de cette incertitude sur la solution.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from . import constants as C
from . import units
from .model import construire_modele
from .preprocessing import calculer_parametres
from .profiles import ProfilsQualite
from .results import Resultat, extraire
from .scenario import Scenario
from .solver import SolutionNonOptimale, resoudre

__all__ = [
    "PointSensibilite",
    "GoulotEtranglement",
    "identifier_goulots",
    "balayer_parametre",
    "balayer_echelons_cocristallisation",
    "comparer_modes_cocristallisation",
    "resoudre_scenario",
]


@dataclass(frozen=True)
class GoulotEtranglement:
    """Une ressource saturée ou dépassée à l'optimum."""

    ressource: str
    utilise: float
    disponible: float
    commentaire: str

    @property
    def taux(self) -> float:
        return self.utilise / self.disponible if self.disponible else 0.0

    @property
    def sature(self) -> bool:
        """Vrai si la ressource est utilisée à 99 % ou davantage."""
        return self.taux >= 0.99

    @property
    def depasse(self) -> bool:
        """Vrai si la capacité est réellement dépassée.

        La marge de 0,1 % écarte le bruit numérique du solveur : une ressource
        pile à sa limite ne doit pas être signalée comme dépassée.
        """
        return self.taux > 1.001


@dataclass(frozen=True)
class PointSensibilite:
    """Un point de balayage : valeur du paramètre et indicateurs obtenus.

    Un point peut être **infaisable** : c'est en soi une information de premier
    ordre, puisqu'elle délimite le domaine des valeurs admissibles du paramètre.
    Les indicateurs valent alors zéro et `faisable` est faux.
    """

    valeur: float | str
    f1: float
    f2: float
    f3: float
    coc_total: float
    dec_cl_produit: float
    stock_ir11: float
    depassement_ir11: float
    transferts: int
    faisable: bool = True


def resoudre_scenario(
    scenario: Scenario, profils: ProfilsQualite | None = None
) -> Resultat:
    """Chaîne complète : pré-traitement, construction, résolution, extraction."""
    params = calculer_parametres(scenario, profils)
    modele = construire_modele(scenario, params)
    return extraire(modele, resoudre(modele))


# ─────────────────────────────────────────────────────────────────────────────
# Goulots d'étranglement
# ─────────────────────────────────────────────────────────────────────────────

def identifier_goulots(resultat: Resultat, scenario: Scenario) -> list[GoulotEtranglement]:
    """Recense les ressources saturées ou dépassées.

    Une contrainte saturée à l'optimum est un goulot : c'est elle qui limite la
    performance. Une contrainte molle dépassée est plus grave encore — le système
    ne tient pas dans ses limites physiques.

    Returns:
        Les goulots, du plus tendu au moins tendu.
    """
    goulots: list[GoulotEtranglement] = []

    # Décanteurs, ligne par ligne.
    for nom, r in resultat.lignes_54.items():
        if nom not in scenario.clarification_active:
            continue
        utilise = r.clarification_ncl + r.clarification_dec
        goulots.append(GoulotEtranglement(
            ressource=f"Décanteurs {nom}",
            utilise=utilise,
            disponible=C.CAPACITE_DECANTEURS_PAR_LIGNE,
            commentaire="capacité partagée entre clarification ordinaire et décadmiée",
        ))

    # Bacs centraux.
    for bac in (resultat.ir11, resultat.ir12):
        goulots.append(GoulotEtranglement(
            ressource=f"Bac {bac.nom}",
            utilise=bac.stock_final,
            disponible=bac.capacite,
            commentaire=(
                "alimenté par la cocristallisation systématique, insensible à la demande"
                if bac.nom == "IR11" else "alimenté par la clarification, pilotable"
            ),
        ))

    # Cuves d'acide 29 et 54.
    _, z_max_29 = units.bornes_stock_29()
    for nom, r in resultat.lignes_29.items():
        goulots.append(GoulotEtranglement(
            ressource=f"Cuves {nom}",
            utilise=r.stock_final_std + r.stock_final_dec,
            disponible=z_max_29,
            commentaire="capacité partagée entre acide standard et décadmié",
        ))

    _, z_max_54 = units.bornes_stock_54()
    for nom, r in resultat.lignes_54.items():
        goulots.append(GoulotEtranglement(
            ressource=f"Cuves {nom}",
            utilise=r.stock_final_ncl,
            disponible=z_max_54,
            commentaire="stock local d'acide 54 NCL",
        ))

    return sorted(goulots, key=lambda g: g.taux, reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# Analyses de sensibilité
# ─────────────────────────────────────────────────────────────────────────────

def _indicateurs(resultat: Resultat, valeur: float | str) -> PointSensibilite:
    """Résume une solution en quelques indicateurs comparables."""
    dec_cl = sum(r.dec_cl_produit for r in resultat.lignes_54.values())
    coc = sum(r.coc_produit for r in resultat.lignes_54.values())
    return PointSensibilite(
        valeur=valeur,
        f1=resultat.f1,
        f2=resultat.f2,
        f3=resultat.f3,
        coc_total=coc,
        dec_cl_produit=dec_cl,
        stock_ir11=resultat.ir11.stock_final,
        depassement_ir11=max(0.0, resultat.ir11.stock_final - resultat.ir11.capacite),
        transferts=len(resultat.transferts),
        faisable=True,
    )


def _point_infaisable(valeur: float | str) -> PointSensibilite:
    """Point de balayage pour lequel aucune solution n'existe."""
    return PointSensibilite(
        valeur=valeur, f1=0.0, f2=0.0, f3=0.0, coc_total=0.0,
        dec_cl_produit=0.0, stock_ir11=0.0, depassement_ir11=0.0,
        transferts=0, faisable=False,
    )


def _evaluer(
    variante: Scenario, valeur: float | str, profils: ProfilsQualite | None
) -> PointSensibilite:
    """Résout une variante, en traitant l'infaisabilité comme un résultat.

    Un balayage qui s'interromprait au premier point infaisable ne servirait à
    rien : c'est justement la frontière du domaine admissible que l'on cherche.
    """
    try:
        return _indicateurs(resoudre_scenario(variante, profils), valeur)
    except SolutionNonOptimale:
        return _point_infaisable(valeur)


def balayer_parametre(
    scenario: Scenario,
    nom_parametre: str,
    valeurs: list[float],
    profils: ProfilsQualite | None = None,
) -> list[PointSensibilite]:
    """Résout le modèle pour plusieurs valeurs d'un paramètre de planification.

    Args:
        scenario: scénario de base.
        nom_parametre: champ à faire varier (`alpha_dec_cl`, `transfert_max`,
            `tolerance_concentration`).
        valeurs: valeurs successives à tester.
        profils: catalogue des recettes.

    Returns:
        Un point par valeur testée.
    """
    if not hasattr(scenario, nom_parametre):
        raise AttributeError(f"Le scénario n'a pas de paramètre « {nom_parametre} ».")

    points: list[PointSensibilite] = []
    for valeur in valeurs:
        variante = dataclasses.replace(scenario, **{nom_parametre: valeur})
        variante.valider()
        points.append(_evaluer(variante, valeur, profils))
    return points


def balayer_echelons_cocristallisation(
    scenario: Scenario,
    ligne: str = "14EXT",
    profils: ProfilsQualite | None = None,
) -> list[PointSensibilite]:
    """Fait varier le nombre d'échelons affectés à la cocristallisation d'une ligne.

    C'est l'analyse la plus utile du scénario de référence : la cocristallisation
    étant systématique, le nombre d'échelons qui lui sont affectés détermine à lui
    seul le remplissage d'IR11, sans qu'aucune décision d'optimisation ne puisse
    le corriger.

    Args:
        scenario: scénario de base.
        ligne: ligne d'acide 54 à examiner ; elle doit être équipée.
        profils: catalogue des recettes.

    Returns:
        Un point par nombre d'échelons, du plus grand au plus petit.
    """
    if ligne not in C.LIGNES_COC_POSSIBLE:
        raise ValueError(f"La ligne {ligne} n'est pas équipée de cocristallisation.")

    echelons_initiaux = tuple(scenario.echelons_cocristallisation.get(ligne, ()))
    points: list[PointSensibilite] = []

    for nombre in range(len(echelons_initiaux), -1, -1):
        configuration = dict(scenario.echelons_cocristallisation)
        configuration[ligne] = echelons_initiaux[:nombre]
        variante = dataclasses.replace(scenario, echelons_cocristallisation=configuration)
        variante.valider()
        points.append(
            _evaluer(variante, f"{nombre}/{len(echelons_initiaux)}", profils)
        )

    return points


def comparer_modes_cocristallisation(
    scenario: Scenario, profils: ProfilsQualite | None = None
) -> list[PointSensibilite]:
    """Compare le mode subi (cahier des charges) au mode décidable (D-11).

    Le mode subi traite l'affectation des échelons à la cocristallisation comme
    un paramètre ; le mode décidable en fait une variable binaire par échelon.

    C'est la comparaison la plus instructive du modèle : elle chiffre ce que
    coûte une contrainte de configuration que personne n'avait identifiée comme
    telle.

    Args:
        scenario: scénario de base.
        profils: catalogue des recettes.

    Returns:
        Deux points, dans l'ordre ``subi`` puis ``décidable``.
    """
    points: list[PointSensibilite] = []
    for decidable, libelle in ((False, "subi"), (True, "décidable")):
        variante = dataclasses.replace(scenario, cocristallisation_decidable=decidable)
        variante.valider()
        points.append(_evaluer(variante, libelle, profils))
    return points
