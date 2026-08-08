"""Validateur indépendant de la solution.

Ce module recalcule les bilans matière et vérifie les règles de procédé **à partir
des équations physiques**, et non des contraintes du modèle.

C'est délibéré. Si la formulation du modèle contient une erreur, le solveur
renverra une solution parfaitement « optimale » — pour un mauvais problème.
Rejouer les contraintes du modèle ne détecterait rien. Seul un contrôle écrit
séparément, à partir de la physique, peut mettre l'erreur en évidence. C'est le
principe de la double vérification.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import constants as C
from . import units
from .results import Resultat
from .scenario import Scenario

__all__ = ["Anomalie", "RapportValidation", "valider"]

#: Tolérance relative sur les bilans matière (0,1 %).
TOLERANCE_BILAN_RELATIVE = 1e-3
#: Tolérance absolue sur la satisfaction de la demande (t de P2O5).
TOLERANCE_DEMANDE = 1e-2
#: Tolérance absolue sur les capacités : stricte, au bruit numérique près.
TOLERANCE_CAPACITE = 1e-6


@dataclass
class Anomalie:
    """Un contrôle en échec."""

    categorie: str
    objet: str
    message: str
    ecart: float = 0.0

    def __str__(self) -> str:
        return f"[{self.categorie}] {self.objet} : {self.message}"


@dataclass
class RapportValidation:
    """Synthèse de tous les contrôles.

    Attributes:
        anomalies: contrôles en échec ; vide si tout est conforme.
        controles_effectues: nombre total de contrôles réalisés.
        observations: constats non bloquants mais dignes d'être signalés.
    """

    anomalies: list[Anomalie] = field(default_factory=list)
    controles_effectues: int = 0
    observations: list[str] = field(default_factory=list)

    @property
    def conforme(self) -> bool:
        """Vrai si aucun contrôle n'est en échec."""
        return not self.anomalies

    def resume(self) -> str:
        """Résumé lisible du rapport."""
        if self.conforme:
            texte = f"CONFORME — {self.controles_effectues} contrôles réussis."
        else:
            lignes = "\n".join(f"  - {a}" for a in self.anomalies)
            texte = (
                f"NON CONFORME — {len(self.anomalies)} anomalie(s) "
                f"sur {self.controles_effectues} contrôles :\n{lignes}"
            )
        if self.observations:
            texte += "\n\nObservations :\n" + "\n".join(f"  - {o}" for o in self.observations)
        return texte


def _ecart_relatif(gauche: float, droite: float) -> float:
    """Écart relatif entre deux membres, rapporté à l'ordre de grandeur en jeu."""
    echelle = max(abs(gauche), abs(droite), 1.0)
    return abs(gauche - droite) / echelle


def valider(resultat: Resultat, scenario: Scenario) -> RapportValidation:
    """Contrôle complet d'une solution.

    Args:
        resultat: solution structurée.
        scenario: scénario d'origine.

    Returns:
        Le rapport de validation.
    """
    rapport = RapportValidation()

    _valider_bilans_29_std(resultat, rapport)
    _valider_bilans_29_dec(resultat, rapport)
    _valider_bilans_54_ncl(resultat, rapport)
    _valider_bilans_centraux(resultat, rapport)
    _valider_demande(resultat, rapport)
    _valider_capacites(resultat, scenario, rapport)
    _valider_regles_procede(resultat, scenario, rapport)
    _valider_conservation_globale(resultat, rapport)

    return rapport


# ─────────────────────────────────────────────────────────────────────────────
# Bilans matière — un contrôle par nœud (19 nœuds au total)
# ─────────────────────────────────────────────────────────────────────────────

def _valider_bilans_29_std(resultat: Resultat, rapport: RapportValidation) -> None:
    """Stock d'acide 29 standard : entrées = sorties + variation de stock."""
    for ligne, r in resultat.lignes_29.items():
        entrees = (
            r.stock_initial_std
            + r.production_std
            + r.transferts_entrants
            + r.boue_cocristallisation
            + r.boue_clarification
            + r.retour_emaphos
        )
        sorties = (
            r.transferts_sortants
            + r.vers_concentration_std
            + r.total_livraisons_std
            + r.stock_final_std
        )
        rapport.controles_effectues += 1
        if _ecart_relatif(entrees, sorties) > TOLERANCE_BILAN_RELATIVE:
            rapport.anomalies.append(Anomalie(
                "bilan_29_std", ligne,
                f"entrées {entrees:.3f} != sorties {sorties:.3f}",
                entrees - sorties,
            ))


def _valider_bilans_29_dec(resultat: Resultat, rapport: RapportValidation) -> None:
    """Stock d'acide 29 décadmié : ni transfert, ni boue entrante."""
    for ligne, r in resultat.lignes_29.items():
        entrees = r.stock_initial_dec + r.decadmiation
        sorties = r.vers_concentration_dec + r.total_livraisons_dec + r.stock_final_dec
        rapport.controles_effectues += 1
        if _ecart_relatif(entrees, sorties) > TOLERANCE_BILAN_RELATIVE:
            rapport.anomalies.append(Anomalie(
                "bilan_29_dec", ligne,
                f"entrées {entrees:.3f} != sorties {sorties:.3f}",
                entrees - sorties,
            ))


def _valider_bilans_54_ncl(resultat: Resultat, rapport: RapportValidation) -> None:
    """Stock d'acide 54 NCL : aucune boue n'y revient, le NCL décadmié n'y transite pas."""
    for ligne, r in resultat.lignes_54.items():
        entrees = r.stock_initial_ncl + r.ncl_produit
        sorties = r.clarification_ncl + r.total_livraisons_ncl + r.stock_final_ncl
        rapport.controles_effectues += 1
        if _ecart_relatif(entrees, sorties) > TOLERANCE_BILAN_RELATIVE:
            rapport.anomalies.append(Anomalie(
                "bilan_54_ncl", ligne,
                f"entrées {entrees:.3f} != sorties {sorties:.3f}",
                entrees - sorties,
            ))


def _valider_bilans_centraux(resultat: Resultat, rapport: RapportValidation) -> None:
    """Bacs IR11 et IR12 : stock initial + entrées = livraisons + stock final."""
    for bac in (resultat.ir11, resultat.ir12):
        entrees = bac.stock_initial + bac.total_entrees
        sorties = bac.total_livraisons + bac.stock_final
        rapport.controles_effectues += 1
        if _ecart_relatif(entrees, sorties) > TOLERANCE_BILAN_RELATIVE:
            rapport.anomalies.append(Anomalie(
                "bilan_central", bac.nom,
                f"entrées {entrees:.3f} != sorties {sorties:.3f}",
                entrees - sorties,
            ))


def _valider_conservation_globale(resultat: Resultat, rapport: RapportValidation) -> None:
    """Conservation du P2O5 sur l'ensemble du système.

    Contrôle transverse : il ne rejoue aucun bilan local, mais vérifie que la
    somme de tout ce qui entre dans le périmètre égale la somme de tout ce qui en
    sort. Une erreur de nœud compensée par une autre y échapperait ; une erreur
    isolée y est détectée immédiatement.

    Le retour d'EMAPHOS est une **entrée** du périmètre : c'est de la matière
    déjà livrée qui y revient.
    """
    stock_initial = (
        sum(r.stock_initial_std + r.stock_initial_dec for r in resultat.lignes_29.values())
        + sum(r.stock_initial_ncl for r in resultat.lignes_54.values())
        + resultat.ir11.stock_initial + resultat.ir12.stock_initial
    )
    stock_final = (
        sum(r.stock_final_std + r.stock_final_dec for r in resultat.lignes_29.values())
        + sum(r.stock_final_ncl for r in resultat.lignes_54.values())
        + resultat.ir11.stock_final + resultat.ir12.stock_final
    )
    production = sum(r.production_totale for r in resultat.lignes_29.values())
    retours_emaphos = sum(r.retour_emaphos for r in resultat.lignes_29.values())

    # Pertes en boue : le P2O5 des boues n'est pas perdu, il est recyclé au
    # niveau 29 — il est donc déjà compté dans les entrées. Ce qui sort vraiment
    # du périmètre, ce sont les livraisons.
    livraisons = sum(
        q for besoins in resultat.livraisons.values() for q in besoins.values()
    )

    entrees = stock_initial + production + retours_emaphos
    sorties = stock_final + livraisons

    rapport.controles_effectues += 1
    if _ecart_relatif(entrees, sorties) > TOLERANCE_BILAN_RELATIVE:
        rapport.anomalies.append(Anomalie(
            "conservation_globale", "système",
            f"entrées {entrees:.3f} != sorties {sorties:.3f}",
            entrees - sorties,
        ))


# ─────────────────────────────────────────────────────────────────────────────
# Demande, capacités, règles de procédé
# ─────────────────────────────────────────────────────────────────────────────

def _valider_demande(resultat: Resultat, rapport: RapportValidation) -> None:
    """Chaque besoin doit être exactement couvert."""
    for consommateur, besoins in resultat.besoins.items():
        for acide, requis in besoins.items():
            livre = resultat.livraisons[consommateur][acide]
            rapport.controles_effectues += 1
            if abs(livre - requis) > TOLERANCE_DEMANDE:
                rapport.anomalies.append(Anomalie(
                    "demande", f"{consommateur}/{acide}",
                    f"livré {livre:.3f} pour {requis:.3f} requis",
                    livre - requis,
                ))


def _valider_capacites(
    resultat: Resultat, scenario: Scenario, rapport: RapportValidation
) -> None:
    """Capacités de décantation et bornes de transfert."""
    for ligne, r in resultat.lignes_54.items():
        entree = r.clarification_ncl + r.clarification_dec
        rapport.controles_effectues += 1
        if entree > C.CAPACITE_DECANTEURS_PAR_LIGNE + TOLERANCE_CAPACITE:
            rapport.anomalies.append(Anomalie(
                "capacite_decanteurs", ligne,
                f"{entree:.3f} t envoyées pour une capacité de "
                f"{C.CAPACITE_DECANTEURS_PAR_LIGNE:.0f} t",
                entree - C.CAPACITE_DECANTEURS_PAR_LIGNE,
            ))
        if ligne not in scenario.clarification_active and entree > TOLERANCE_CAPACITE:
            rapport.anomalies.append(Anomalie(
                "capacite_decanteurs", ligne,
                f"clarification de {entree:.3f} t sur une ligne non habilitée",
                entree,
            ))

    for arc, quantite in resultat.transferts.items():
        rapport.controles_effectues += 1
        if not (scenario.transfert_min - TOLERANCE_CAPACITE
                <= quantite
                <= scenario.transfert_max + TOLERANCE_CAPACITE):
            rapport.anomalies.append(Anomalie(
                "transfert", f"{arc[0]}->{arc[1]}",
                f"{quantite:.3f} t hors de l'intervalle "
                f"[{scenario.transfert_min}, {scenario.transfert_max}]",
            ))

    arcs_valides = set(C.arcs_interzone())
    for arc in resultat.transferts:
        rapport.controles_effectues += 1
        if arc not in arcs_valides:
            rapport.anomalies.append(Anomalie(
                "transfert", f"{arc[0]}->{arc[1]}", "liaison interzone inexistante"
            ))


def _valider_regles_procede(
    resultat: Resultat, scenario: Scenario, rapport: RapportValidation
) -> None:
    """Niveaux de décadmiation, rendements, positivité et bandes de stock."""
    for ligne, r in resultat.lignes_29.items():
        rapport.controles_effectues += 1
        if not any(abs(r.decadmiation - n) < 1e-4 for n in C.NIVEAUX_DECADMIATION):
            rapport.anomalies.append(Anomalie(
                "decadmiation", ligne,
                f"niveau {r.decadmiation:.3f} hors de {list(C.NIVEAUX_DECADMIATION)}",
            ))

        rapport.controles_effectues += 1
        if r.decadmiation > r.production_totale + TOLERANCE_CAPACITE:
            rapport.anomalies.append(Anomalie(
                "decadmiation", ligne,
                f"décadmiation {r.decadmiation:.1f} > production {r.production_totale:.1f}",
            ))

        rapport.controles_effectues += 1
        if r.decadmiation > 0 and ligne not in scenario.decadmiation_equipee:
            rapport.anomalies.append(Anomalie(
                "decadmiation", ligne, "ligne non équipée de filtres",
            ))

        for nom, stock in (("std", r.stock_final_std), ("dec", r.stock_final_dec)):
            rapport.controles_effectues += 1
            if stock < -TOLERANCE_CAPACITE:
                rapport.anomalies.append(Anomalie(
                    "stock_negatif", f"{ligne}/{nom}", f"stock final {stock:.3f}",
                ))

    for ligne, r in resultat.lignes_54.items():
        rapport.controles_effectues += 1
        attendu = C.RENDEMENT_COCRISTALLISATION * r.coc_entree
        if abs(r.coc_produit - attendu) > TOLERANCE_DEMANDE:
            rapport.anomalies.append(Anomalie(
                "rendement_coc", ligne,
                f"CoC {r.coc_produit:.3f} au lieu de {attendu:.3f}",
            ))

        rapport.controles_effectues += 1
        if r.stock_final_ncl < -TOLERANCE_CAPACITE:
            rapport.anomalies.append(Anomalie(
                "stock_negatif", ligne, f"stock final NCL {r.stock_final_ncl:.3f}",
            ))

        rapport.controles_effectues += 1
        if r.ncl_produit < -TOLERANCE_CAPACITE:
            rapport.anomalies.append(Anomalie(
                "production_negative", ligne,
                f"NCL produit {r.ncl_produit:.3f} : les échelons cocristallisants "
                "ne sont pas alimentés au plan",
            ))

    # Bandes de sécurité : signalées en observation, non en anomalie, car ce
    # sont des contraintes molles assumées (voir document 04, §8).
    # Le seuil de 0,1 t écarte le bruit numérique du solveur : en dessous de
    # 100 kg sur des cuves de plusieurs centaines de tonnes, il n'y a aucun
    # dépassement au sens de l'exploitation.
    seuil = 0.1
    z_min_29, z_max_29 = units.bornes_stock_29()
    for ligne, r in resultat.lignes_29.items():
        total = r.stock_final_std + r.stock_final_dec
        if total > z_max_29 + seuil:
            rapport.observations.append(
                f"{ligne} : stock final {total:.1f} t au-dessus de la bande "
                f"({z_max_29:.1f} t), dépassement de {total - z_max_29:.1f} t."
            )
        elif total < z_min_29 - seuil:
            rapport.observations.append(
                f"{ligne} : stock final {total:.1f} t sous la bande "
                f"({z_min_29:.1f} t), manque de {z_min_29 - total:.1f} t."
            )

    for bac, bornes in ((resultat.ir11, units.bornes_stock_ir11()),
                        (resultat.ir12, units.bornes_stock_ir12())):
        if bac.stock_final > bornes[1] + seuil:
            rapport.observations.append(
                f"{bac.nom} : stock final {bac.stock_final:.1f} t au-dessus de la "
                f"capacité ({bornes[1]:.1f} t), dépassement de "
                f"{bac.stock_final - bornes[1]:.1f} t."
            )
