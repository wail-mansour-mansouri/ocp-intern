"""Tests de la génération des rapports et des analyses post-optimisation."""

from __future__ import annotations

import json

import pytest
from openpyxl import load_workbook

from ocp_optim import constants as C
from ocp_optim.analysis import (
    balayer_echelons_cocristallisation,
    balayer_parametre,
    identifier_goulots,
)
from ocp_optim.cli import main
from ocp_optim.reporting import (
    FEUILLES_ATTENDUES,
    generer_rapport_excel,
    generer_rapport_json,
)
from ocp_optim.validation import valider


# ─────────────────────────────────────────────────────────────────────────────
# Rapport Excel
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def classeur(resultat, scenario, tmp_path_factory):
    chemin = tmp_path_factory.mktemp("rapports") / "resultats.xlsx"
    generer_rapport_excel(resultat, scenario, chemin)
    return load_workbook(chemin)


def test_les_cinq_feuilles_sont_presentes(classeur):
    """Le format imposé compte exactement cinq feuilles (anomalie A-11)."""
    assert tuple(classeur.sheetnames) == FEUILLES_ATTENDUES


def test_chaque_feuille_a_du_contenu(classeur):
    for nom in FEUILLES_ATTENDUES:
        feuille = classeur[nom]
        assert feuille.max_row > 2, f"la feuille {nom} est vide"
        assert feuille.max_column > 1


def test_feuille_demande_couvre_tous_les_consommateurs_servis(classeur, resultat):
    contenu = "\n".join(
        str(cellule.value)
        for ligne in classeur["Demand Delivery"].iter_rows()
        for cellule in ligne
        if cellule.value is not None
    )
    for consommateur in resultat.besoins:
        assert consommateur in contenu


def test_feuille_production_couvre_toutes_les_lignes(classeur):
    contenu = "\n".join(
        str(cellule.value)
        for ligne in classeur["Phosphoric Production"].iter_rows()
        for cellule in ligne
        if cellule.value is not None
    )
    for nom in list(C.LIGNES_29) + list(C.LIGNES_54):
        assert nom in contenu


def test_feuille_stocks_29_a_deux_lignes_par_ligne_de_production(classeur):
    """Une ligne par couple (ligne, qualité d'acide) : 6 lignes x 2 qualités."""
    types = [
        cellule.value
        for ligne in classeur["Acid 29 Stocks"].iter_rows(min_col=2, max_col=2)
        for cellule in ligne
    ]
    assert types.count("acid_29_std") == 6
    assert types.count("acid_29_dec") == 6


def test_feuille_stockage_central_mentionne_les_deux_bacs(classeur):
    contenu = "\n".join(
        str(cellule.value)
        for ligne in classeur["Central Storage Stocks"].iter_rows()
        for cellule in ligne
        if cellule.value is not None
    )
    assert "IR11" in contenu
    assert "IR12" in contenu


def test_le_fichier_est_relisible(resultat, scenario, tmp_path):
    """Un classeur écrit doit pouvoir être rouvert sans erreur."""
    chemin = generer_rapport_excel(resultat, scenario, tmp_path / "sous" / "dossier.xlsx")
    assert chemin.exists()
    assert load_workbook(chemin).sheetnames == list(FEUILLES_ATTENDUES)


# ─────────────────────────────────────────────────────────────────────────────
# Rapport JSON
# ─────────────────────────────────────────────────────────────────────────────

def test_json_serialisable_et_complet(resultat, scenario, tmp_path):
    rapport = valider(resultat, scenario)
    chemin = generer_rapport_json(resultat, scenario, tmp_path / "r.json", rapport)
    donnees = json.loads(chemin.read_text(encoding="utf-8"))

    assert set(donnees["lignes_29"]) == set(C.LIGNES_29)
    assert set(donnees["lignes_54"]) == set(C.LIGNES_54)
    assert donnees["objectif"]["f1_demande_non_satisfaite"] == pytest.approx(0.0, abs=1e-4)
    assert donnees["validation"]["conforme"] is True
    assert donnees["validation"]["controles_effectues"] >= 80


def test_json_aplati_les_cles_de_transfert(resultat, scenario, tmp_path):
    """Les clés JSON doivent être des chaînes, pas des couples."""
    chemin = generer_rapport_json(resultat, scenario, tmp_path / "r.json")
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in donnees["transferts"]:
        assert isinstance(cle, str)
        assert "->" in cle


# ─────────────────────────────────────────────────────────────────────────────
# Goulots d'étranglement
# ─────────────────────────────────────────────────────────────────────────────

def test_ir11_identifie_comme_goulot_principal(resultat, scenario):
    """IR11 est la ressource la plus tendue du scénario de référence."""
    goulots = identifier_goulots(resultat, scenario)
    assert goulots[0].ressource == "Bac IR11"
    assert goulots[0].depasse


def test_goulots_tries_par_tension_decroissante(resultat, scenario):
    goulots = identifier_goulots(resultat, scenario)
    taux = [g.taux for g in goulots]
    assert taux == sorted(taux, reverse=True)


def test_ressource_pile_a_la_limite_non_signalee_comme_depassee(resultat, scenario):
    """Le bruit numérique ne doit pas faire passer une cuve pleine pour débordée."""
    for goulot in identifier_goulots(resultat, scenario):
        if 0.999 <= goulot.taux <= 1.001:
            assert not goulot.depasse


# ─────────────────────────────────────────────────────────────────────────────
# Analyses de sensibilité
# ─────────────────────────────────────────────────────────────────────────────

def test_moins_de_cocristallisation_resorbe_le_depassement(scenario, profils):
    """Réduire le nombre d'échelons CoC de 14EXT fait disparaître le débordement d'IR11.

    C'est le résultat le plus actionnable de l'étude : le débordement ne vient
    d'aucune mauvaise décision d'exploitation, mais de la configuration même de
    la cocristallisation.
    """
    points = balayer_echelons_cocristallisation(scenario, "14EXT", profils)
    assert points[0].valeur == "4/4"
    assert points[0].depassement_ir11 > 900.0
    assert points[-1].depassement_ir11 == pytest.approx(0.0, abs=1e-3)
    # Le dépassement décroît avec le nombre d'échelons affectés.
    depassements = [p.depassement_ir11 for p in points]
    assert depassements == sorted(depassements, reverse=True)


def test_alpha_pilote_la_production_de_dec_cl(scenario, profils):
    """La production de DEC_CL croît avec alpha, et vaut zéro quand alpha est nul."""
    points = balayer_parametre(scenario, "alpha_dec_cl", [0.0, 0.10, 0.20], profils)
    assert points[0].dec_cl_produit == pytest.approx(0.0, abs=1e-4)
    productions = [p.dec_cl_produit for p in points]
    assert productions == sorted(productions)


def test_toutes_les_variantes_servent_la_demande(scenario, profils):
    """Aucune valeur d'attente testée ne rend le système incapable de livrer."""
    for point in balayer_parametre(
        scenario, "transfert_max", [300.0, 1000.0, 1500.0], profils
    ):
        assert point.f1 == pytest.approx(0.0, abs=1e-4)


def test_parametre_inexistant_rejete(scenario, profils):
    with pytest.raises(AttributeError, match="parametre_imaginaire"):
        balayer_parametre(scenario, "parametre_imaginaire", [1.0], profils)


def test_ligne_sans_cocristallisation_rejetee(scenario, profils):
    with pytest.raises(ValueError, match="n'est pas équipée"):
        balayer_echelons_cocristallisation(scenario, "14CD", profils)


# ─────────────────────────────────────────────────────────────────────────────
# Ligne de commande
# ─────────────────────────────────────────────────────────────────────────────

def test_cli_sans_argument(capsys):
    """Le code de retour vaut 0 quand la validation est conforme."""
    assert main([]) == 0
    sortie = capsys.readouterr().out
    assert "VALIDATION INDÉPENDANTE" in sortie
    assert "CONFORME" in sortie


def test_cli_ecrit_les_rapports(tmp_path, capsys):
    assert main(["--sortie", str(tmp_path)]) == 0
    assert (tmp_path / "resultats_optimisation.xlsx").exists()
    assert (tmp_path / "resultats_optimisation.json").exists()
