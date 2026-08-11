"""Pré-traitement déterministe : calcul de tous les paramètres dérivés.

Une part importante du système n'est **pas** optimisable : la production d'acide 54
découle des heures de marche, et la cocristallisation est systématique. Ces grandeurs
sont donc calculées ici, une fois pour toutes, **avant** la construction du modèle.

Séparer ce calcul de l'optimisation est le choix d'architecture central du projet :
il réduit la taille du modèle, rend chaque grandeur vérifiable isolément, et évite
l'erreur classique consistant à transformer en décision ce qui est en réalité subi.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from . import constants as C
from .profiles import ProfilsQualite
from .scenario import Scenario

__all__ = ["ParametresDerives", "calculer_parametres"]


@dataclass(frozen=True)
class ParametresDerives:
    """Paramètres calculés à partir d'un scénario, avant optimisation.

    Attributes:
        production_echelon: kappa_e — production de chaque échelon (t P2O5/j).
        production_54: Pi_m — production totale de chaque ligne de concentration.
        production_54_coc: Pi_coc_m — part produite par les échelons cocristallisants.
        production_54_ncl: Pi_ncl_m — part produite par les autres échelons.
        coc_produit: G_m — CoC envoyé vers IR11 (systématique).
        boue_coc: B_coc_m — boue de cocristallisation retournant au stock d'acide 29.
        besoins: R[k][a] — besoin consolidé du consommateur k en acide a.
        echelons_coc_candidats: échelons raccordés aux unités de cocristallisation,
            par ligne. En mode subi, ils sont tous en service et les grandeurs
            ci-dessus sont exactes ; en mode décidable, elles constituent la
            borne haute que le modèle peut choisir de ne pas atteindre.
    """

    production_echelon: dict[str, float]
    production_54: dict[str, float]
    production_54_coc: dict[str, float]
    production_54_ncl: dict[str, float]
    coc_produit: dict[str, float]
    boue_coc: dict[str, float]
    besoins: dict[str, dict[str, float]]
    echelons_coc_candidats: dict[str, tuple[str, ...]]

    # ── Agrégats de commodité ───────────────────────────────────────────────

    @property
    def production_54_totale(self) -> float:
        """Production totale d'acide 54, toutes lignes confondues (t P2O5/j)."""
        return sum(self.production_54.values())

    @property
    def coc_total(self) -> float:
        """CoC total produit par cocristallisation systématique (t P2O5/j)."""
        return sum(self.coc_produit.values())

    @property
    def demande_totale(self) -> float:
        """Somme de tous les besoins, tous consommateurs et tous types (t P2O5/j)."""
        return sum(q for besoins in self.besoins.values() for q in besoins.values())

    def besoins_par_type(self) -> dict[str, float]:
        """Agrège les besoins par type d'acide, tous consommateurs confondus."""
        total: dict[str, float] = defaultdict(float)
        for besoins in self.besoins.values():
            for acide, quantite in besoins.items():
                total[acide] += quantite
        return dict(total)


# ─────────────────────────────────────────────────────────────────────────────
# Calculs
# ─────────────────────────────────────────────────────────────────────────────

def _production_echelons(scenario: Scenario) -> dict[str, float]:
    """Calcule kappa_e = C_e * h_e / 24 pour chaque échelon.

    Il s'agit d'un simple prorata horaire : la capacité est exprimée à plein
    régime sur 24 h (anomalie A-08).
    """
    return {
        echelon: capacite * scenario.heures_marche[echelon] / 24.0
        for echelon, capacite in C.CAPACITE_ECHELON.items()
    }


def _productions_par_ligne(
    scenario: Scenario, production_echelon: dict[str, float]
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """Ventile la production d'acide 54 entre échelons cocristallisants et autres.

    Returns:
        Un triplet ``(Pi, Pi_coc, Pi_ncl)`` indexé par ligne d'acide 54.
    """
    total: dict[str, float] = {}
    part_coc: dict[str, float] = {}
    part_ncl: dict[str, float] = {}

    for ligne, echelons in C.GROUPES_ECHELONS.items():
        echelons_coc = set(scenario.echelons_cocristallisation.get(ligne, ()))
        total[ligne] = sum(production_echelon[e] for e in echelons)
        part_coc[ligne] = sum(production_echelon[e] for e in echelons if e in echelons_coc)
        part_ncl[ligne] = total[ligne] - part_coc[ligne]

    return total, part_coc, part_ncl


def _besoins_consommateurs(
    scenario: Scenario, profils: ProfilsQualite
) -> dict[str, dict[str, float]]:
    """Consolide, pour chaque consommateur, ses besoins en acide.

    R[k][a] = demande directe + somme sur les produits des coefficients de recette.

    Les besoins nuls sont écartés : ils alourdiraient le modèle sans rien contraindre.
    """
    besoins: dict[str, dict[str, float]] = {}

    for consommateur in C.CONSOMMATEURS:
        agrege: dict[str, float] = defaultdict(float)

        for acide, quantite in scenario.demande_directe.get(consommateur, {}).items():
            agrege[acide] += quantite

        demande_engrais = scenario.demande_engrais.get(consommateur, {})
        if demande_engrais:
            for acide, quantite in profils.besoins_atelier(demande_engrais).items():
                agrege[acide] += quantite

        filtre = {a: q for a, q in agrege.items() if q > 0.0}
        if filtre:
            besoins[consommateur] = filtre

    return besoins


def calculer_parametres(
    scenario: Scenario, profils: ProfilsQualite | None = None
) -> ParametresDerives:
    """Calcule l'ensemble des paramètres dérivés d'un scénario.

    Args:
        scenario: scénario validé.
        profils: catalogue des recettes ; chargé par défaut depuis le fichier standard.

    Returns:
        Les paramètres dérivés, prêts à alimenter le modèle d'optimisation.
    """
    profils = profils if profils is not None else ProfilsQualite.depuis_json()

    production_echelon = _production_echelons(scenario)
    total, part_coc, part_ncl = _productions_par_ligne(scenario, production_echelon)

    coc_produit = {
        ligne: C.RENDEMENT_COCRISTALLISATION * part_coc[ligne] for ligne in C.LIGNES_54
    }
    boue_coc = {
        ligne: C.BOUE_COCRISTALLISATION * part_coc[ligne] for ligne in C.LIGNES_54
    }

    return ParametresDerives(
        production_echelon=production_echelon,
        production_54=total,
        production_54_coc=part_coc,
        production_54_ncl=part_ncl,
        coc_produit=coc_produit,
        boue_coc=boue_coc,
        besoins=_besoins_consommateurs(scenario, profils),
        echelons_coc_candidats={
            ligne: tuple(scenario.echelons_cocristallisation.get(ligne, ()))
            for ligne in C.LIGNES_54
        },
    )
