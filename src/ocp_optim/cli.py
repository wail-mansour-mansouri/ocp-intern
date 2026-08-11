"""Interface en ligne de commande.

Exemples :

    python -m ocp_optim                       # résout le scénario de référence
    python -m ocp_optim --sortie resultats/   # écrit les rapports Excel et JSON
    python -m ocp_optim --sensibilite         # ajoute les analyses de sensibilité
    python -m ocp_optim --coc-decidable       # laisse le modèle choisir les échelons CoC
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

from . import constants as C
from . import units
from .analysis import (
    balayer_echelons_cocristallisation,
    balayer_parametre,
    comparer_modes_cocristallisation,
    identifier_goulots,
)
from .preprocessing import ParametresDerives, calculer_parametres
from .profiles import ProfilsQualite
from .model import construire_modele
from .reporting import generer_rapport_excel, generer_rapport_json
from .results import Resultat, extraire
from .scenario import Scenario
from .solver import resoudre
from .validation import RapportValidation, valider

__all__ = ["main"]

_LARGEUR = 78


def _section(titre: str) -> None:
    print()
    print("═" * _LARGEUR)
    print(f"  {titre}")
    print("═" * _LARGEUR)


def _afficher_contexte(scenario: Scenario, params: ParametresDerives) -> None:
    _section("SCÉNARIO ET PARAMÈTRES DÉRIVÉS")
    mode_coc = "décidable (D-11)" if scenario.cocristallisation_decidable else "subi (cahier des charges)"
    print(f"  Scénario                    : {scenario.nom}")
    print(f"  Cocristallisation           : {mode_coc}")
    print(f"  Unité                       : tonne de P2O5 par jour")
    print()
    print(f"  Production d'acide 29       : {sum(scenario.production_29.values()):9.1f}")
    print(f"  Production d'acide 54       : {params.production_54_totale:9.1f}")
    if scenario.cocristallisation_decidable:
        # En mode décidable, ces valeurs sont des bornes hautes : le modèle
        # choisit combien d'échelons candidats mettre effectivement en service.
        print(f"  Échelons CoC candidats      : {sum(params.production_54_coc.values()):9.1f}  (borne haute)")
        print(f"  CoC maximal possible        : {params.coc_total:9.1f}  (borne haute)")
    else:
        print(f"  dont cocristallisée         : {sum(params.production_54_coc.values()):9.1f}")
        print(f"  CoC produit (systématique)  : {params.coc_total:9.1f}")
    print(f"  Demande totale              : {params.demande_totale:9.1f}")
    print()
    print("  Besoins par type d'acide :")
    for acide, quantite in sorted(params.besoins_par_type().items()):
        print(f"    {acide:22s} {quantite:9.2f}")


def _afficher_decisions(resultat: Resultat) -> None:
    _section("DÉCISIONS D'EXPLOITATION")

    print("  Décadmiation :")
    actives = {n: r.decadmiation for n, r in resultat.lignes_29.items() if r.decadmiation > 0}
    if actives:
        for nom, quantite in actives.items():
            print(f"    {nom:6s} {quantite:7.0f} t")
    else:
        print("    aucune")

    print()
    print("  Transferts interzones :")
    if resultat.transferts:
        for (origine, destination), quantite in sorted(resultat.transferts.items()):
            print(f"    {origine:6s} -> {destination:6s} {quantite:8.1f} t")
    else:
        print("    aucun")

    print()
    print("  Clarification (capacité 1000 t/jour par ligne) :")
    for nom, r in resultat.lignes_54.items():
        total = r.clarification_ncl + r.clarification_dec
        if total > 1e-6:
            print(
                f"    {nom:6s} NCL {r.clarification_ncl:7.1f}  DEC {r.clarification_dec:7.1f}"
                f"  total {total:7.1f}  ({100 * r.taux_occupation_decanteurs:5.1f} %)"
            )


def _afficher_stocks(resultat: Resultat) -> None:
    _section("STOCKS FINAUX")
    z_min_29, z_max_29 = units.bornes_stock_29()
    z_min_54, z_max_54 = units.bornes_stock_54()

    print(f"  Acide 29 (bande {z_min_29:.1f} – {z_max_29:.1f} t)")
    for nom, r in resultat.lignes_29.items():
        total = r.stock_final_std + r.stock_final_dec
        marque = "  <-- hors bande" if total > z_max_29 + 0.1 or total < z_min_29 - 0.1 else ""
        print(f"    {nom:6s} std {r.stock_final_std:7.1f}  dec {r.stock_final_dec:7.1f}"
              f"  total {total:7.1f}{marque}")

    print()
    print(f"  Acide 54 NCL (bande {z_min_54:.1f} – {z_max_54:.1f} t)")
    for nom, r in resultat.lignes_54.items():
        marque = ""
        if r.stock_final_ncl > z_max_54 + 0.1:
            marque = "  <-- au-dessus"
        elif r.stock_final_ncl < z_min_54 - 0.1:
            marque = "  <-- en dessous"
        print(f"    {nom:6s} {r.stock_final_ncl:7.1f}{marque}")

    print()
    print("  Stockage central")
    for bac in (resultat.ir11, resultat.ir12):
        marque = "  <-- DÉPASSEMENT" if bac.stock_final > bac.capacite + 0.1 else ""
        print(
            f"    {bac.nom:6s} {bac.stock_initial:8.1f} + {bac.total_entrees:8.1f}"
            f" - {bac.total_livraisons:8.1f} = {bac.stock_final:8.1f}"
            f"  /{bac.capacite:8.1f}  ({100 * bac.taux_remplissage:5.1f} %){marque}"
        )


def _afficher_objectif(resultat: Resultat) -> None:
    _section("FONCTION OBJECTIF (lexicographique)")
    print(f"  Niveau 1 — demande non satisfaite       : {resultat.f1:10.3f}")
    print(f"  Niveau 2 — violations contraintes molles: {resultat.f2:10.3f}")
    print(f"  Niveau 3 — coût opératoire              : {resultat.f3:10.3f}")
    print(f"  Temps de résolution                     : {resultat.duree_s:10.3f} s")


def _afficher_validation(rapport: RapportValidation) -> None:
    _section("VALIDATION INDÉPENDANTE")
    print("  " + rapport.resume().replace("\n", "\n  "))


def _afficher_goulots(resultat: Resultat, scenario: Scenario) -> None:
    _section("GOULOTS D'ÉTRANGLEMENT")
    goulots = identifier_goulots(resultat, scenario)
    print(f"  {'Ressource':<22}{'Utilisé':>10}{'Capacité':>11}{'Taux':>8}   Commentaire")
    print("  " + "-" * (_LARGEUR - 2))
    for goulot in goulots[:8]:
        marque = " !" if goulot.depasse else (" *" if goulot.sature else "  ")
        print(
            f"  {goulot.ressource:<22}{goulot.utilise:>10.1f}{goulot.disponible:>11.1f}"
            f"{100 * goulot.taux:>7.1f}%{marque} {goulot.commentaire}"
        )
    print()
    print("  ! ressource dépassée      * ressource saturée")


def _afficher_sensibilite(scenario: Scenario, profils: ProfilsQualite) -> None:
    _section("ANALYSE DE SENSIBILITÉ")

    print("  Nombre d'échelons de 14EXT affectés à la cocristallisation")
    print(f"    {'Config':<10}{'CoC':>10}{'DEC_CL':>10}{'IR11':>10}"
          f"{'Dépass.':>10}{'f2':>10}{'f3':>10}")
    for point in balayer_echelons_cocristallisation(scenario, "14EXT", profils):
        print(f"    {str(point.valeur):<10}{point.coc_total:>10.1f}"
              f"{point.dec_cl_produit:>10.1f}{point.stock_ir11:>10.1f}"
              f"{point.depassement_ir11:>10.1f}{point.f2:>10.1f}{point.f3:>10.1f}")

    print()
    print("  Part minimale de DEC_CL dans IR11 (paramètre alpha, hypothèse H8)")
    print(f"    {'alpha':<10}{'DEC_CL':>10}{'IR11':>10}{'Dépass.':>10}{'f2':>10}{'f3':>10}")
    for point in balayer_parametre(
        scenario, "alpha_dec_cl", [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], profils
    ):
        if not point.faisable:
            print(f"    {float(point.valeur):<10.2f}{'INFAISABLE — aucune solution':>50}")
            continue
        print(f"    {float(point.valeur):<10.2f}{point.dec_cl_produit:>10.1f}"
              f"{point.stock_ir11:>10.1f}{point.depassement_ir11:>10.1f}"
              f"{point.f2:>10.1f}{point.f3:>10.1f}")
    print()
    print("    Au-delà d'un certain seuil, seule 14XY pouvant produire du DEC_CL,")
    print("    sa capacité d'échelons non cocristallisants ne suffit plus.")

    print()
    print("  Mode d'affectation de la cocristallisation (décision D-11)")
    print(f"    {'Mode':<12}{'CoC':>10}{'IR11':>10}{'Dépass.':>10}{'f2':>10}{'f3':>10}")
    for point in comparer_modes_cocristallisation(scenario, profils):
        print(f"    {str(point.valeur):<12}{point.coc_total:>10.1f}"
              f"{point.stock_ir11:>10.1f}{point.depassement_ir11:>10.1f}"
              f"{point.f2:>10.1f}{point.f3:>10.1f}")

    print()
    print("  Transfert interzone maximal (paramètre tau_max, hypothèse H7)")
    print(f"    {'tau_max':<10}{'Transferts':>12}{'f2':>10}{'f3':>10}")
    for point in balayer_parametre(
        scenario, "transfert_max", [300.0, 500.0, 750.0, 1000.0, 1500.0], profils
    ):
        if not point.faisable:
            print(f"    {float(point.valeur):<10.0f}{'INFAISABLE — aucune solution':>32}")
            continue
        print(f"    {float(point.valeur):<10.0f}{point.transferts:>12d}"
              f"{point.f2:>10.1f}{point.f3:>10.1f}")


def main(argv: list[str] | None = None) -> int:
    """Point d'entrée de la ligne de commande.

    Returns:
        0 si la validation est conforme, 1 sinon.
    """
    analyseur = argparse.ArgumentParser(
        prog="ocp_optim",
        description="Optimisation de la production et distribution d'acide phosphorique "
                    "— OCP Jorf Lasfar.",
    )
    analyseur.add_argument(
        "--scenario", type=Path, default=None,
        help="fichier de scénario JSON (par défaut : le scénario réel de référence)",
    )
    analyseur.add_argument(
        "--profils", type=Path, default=None,
        help="fichier des profils qualité (par défaut : data/quality_profiles.json)",
    )
    analyseur.add_argument(
        "--sortie", type=Path, default=None,
        help="répertoire où écrire les rapports Excel et JSON",
    )
    analyseur.add_argument(
        "--sensibilite", action="store_true",
        help="exécute les analyses de sensibilité (plus long)",
    )
    analyseur.add_argument(
        "--coc-decidable", action="store_true",
        help="rend l'affectation des échelons à la cocristallisation décidable "
             "par le modèle, au lieu de la subir (mode exploratoire, D-11)",
    )
    arguments = analyseur.parse_args(argv)

    profils = ProfilsQualite.depuis_json(arguments.profils)
    scenario = Scenario.depuis_json(arguments.scenario)
    if arguments.coc_decidable:
        scenario = dataclasses.replace(scenario, cocristallisation_decidable=True)
    params = calculer_parametres(scenario, profils)

    _afficher_contexte(scenario, params)

    modele = construire_modele(scenario, params)
    statistiques = modele.statistiques()
    _section("MODÈLE")
    for cle, valeur in statistiques.items():
        print(f"  {cle:24s} {valeur:6d}")

    solution = resoudre(modele)
    resultat = extraire(modele, solution)
    rapport = valider(resultat, scenario)

    _afficher_objectif(resultat)
    _afficher_decisions(resultat)
    _afficher_stocks(resultat)
    _afficher_validation(rapport)
    _afficher_goulots(resultat, scenario)

    if arguments.sensibilite:
        _afficher_sensibilite(scenario, profils)

    if arguments.sortie:
        _section("RAPPORTS")
        chemin_excel = generer_rapport_excel(
            resultat, scenario, arguments.sortie / "resultats_optimisation.xlsx"
        )
        chemin_json = generer_rapport_json(
            resultat, scenario, arguments.sortie / "resultats_optimisation.json", rapport
        )
        print(f"  Excel : {chemin_excel}")
        print(f"  JSON  : {chemin_json}")

    print()
    return 0 if rapport.conforme else 1


if __name__ == "__main__":
    sys.exit(main())
