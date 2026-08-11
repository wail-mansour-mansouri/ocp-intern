"""Tests du pré-traitement déterministe.

Ces tests verrouillent les valeurs recalculées qui **contredisent le dossier**
(anomalie A-01). Si un jour l'encadrant fournit d'autres chiffres, ils échoueront
et signaleront qu'il faut réexaminer le constat.
"""

from __future__ import annotations

import pytest

from ocp_optim import constants as C
from ocp_optim.preprocessing import calculer_parametres


# ─────────────────────────────────────────────────────────────────────────────
# Production des échelons : simple prorata horaire
# ─────────────────────────────────────────────────────────────────────────────

def test_echelon_a_plein_regime(params, scenario):
    """Un échelon marchant 24 h produit exactement sa capacité."""
    for echelon, heures in scenario.heures_marche.items():
        if heures == 24:
            assert params.production_echelon[echelon] == pytest.approx(
                C.CAPACITE_ECHELON[echelon]
            )


def test_echelon_a_l_arret_ne_produit_rien(params, scenario):
    assert scenario.heures_marche["W"] == 0
    assert params.production_echelon["W"] == pytest.approx(0.0)


def test_prorata_horaire(params):
    """Un échelon de 420 t/j marchant 14 h produit 420 x 14/24 = 245 t."""
    assert params.production_echelon["H"] == pytest.approx(420 * 14 / 24)
    assert params.production_echelon["H"] == pytest.approx(245.0)


# ─────────────────────────────────────────────────────────────────────────────
# Production d'acide 54 — anomalie A-01
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("ligne", "attendu"),
    [("14EXT", 1505.0), ("14AB", 2134.2), ("14CD", 1040.0),
     ("14XY", 820.8), ("14ZU", 1481.7)],
)
def test_production_54_par_ligne(params, ligne, attendu):
    assert params.production_54[ligne] == pytest.approx(attendu, abs=0.1)


def test_production_54_totale_contredit_le_dossier(params):
    """Le dossier annonce 6 636 t ; le recalcul donne 6 981,7 t (anomalie A-01)."""
    assert params.production_54_totale == pytest.approx(6981.7, abs=0.1)
    assert abs(params.production_54_totale - 6636.0) > 300.0


def test_ventilation_coc_ncl_est_une_partition(params):
    """La production totale se répartit exactement entre échelons CoC et non-CoC."""
    for ligne in C.LIGNES_54:
        assert params.production_54[ligne] == pytest.approx(
            params.production_54_coc[ligne] + params.production_54_ncl[ligne]
        )


def test_14ext_entierement_dedie_a_la_cocristallisation(params):
    """Les 4 échelons de 14EXT étant affectés au CoC, la ligne ne produit aucun NCL.

    C'est la cause de la deuxième violation structurelle : le stock de 14EXT ne
    peut jamais remonter dans sa bande de sécurité.
    """
    assert params.production_54_ncl["14EXT"] == pytest.approx(0.0)
    assert params.production_54_coc["14EXT"] == pytest.approx(1505.0, abs=0.1)


def test_lignes_sans_cocristallisation(params):
    for ligne in ("14CD", "14XY", "14ZU"):
        assert params.production_54_coc[ligne] == pytest.approx(0.0)
        assert params.coc_produit[ligne] == pytest.approx(0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Cocristallisation systématique
# ─────────────────────────────────────────────────────────────────────────────

def test_rendement_cocristallisation_applique(params):
    for ligne in C.LIGNES_54:
        assert params.coc_produit[ligne] == pytest.approx(
            C.RENDEMENT_COCRISTALLISATION * params.production_54_coc[ligne]
        )
        assert params.boue_coc[ligne] == pytest.approx(
            C.BOUE_COCRISTALLISATION * params.production_54_coc[ligne]
        )


def test_coc_produit_et_boue_somment_a_l_entree(params):
    """Rien ne se perd : CoC + boue = entrée de cocristallisation."""
    for ligne in C.LIGNES_54:
        assert params.coc_produit[ligne] + params.boue_coc[ligne] == pytest.approx(
            params.production_54_coc[ligne]
        )


def test_coc_total_depasse_largement_le_besoin(params):
    """2 431 t de CoC produites pour un besoin de 987 t : facteur 2,5.

    C'est ce déséquilibre qui explique que l'optimiseur n'ait aucune raison
    spontanée de produire du DEC_CL, d'où la nécessité de la contrainte C15.
    """
    assert params.coc_total == pytest.approx(2431.4, abs=0.5)
    besoin_dectot = params.besoins_par_type()[C.BESOIN_54_DEC_TOTAL]
    assert params.coc_total > 2.4 * besoin_dectot


# ─────────────────────────────────────────────────────────────────────────────
# Besoins consolidés
# ─────────────────────────────────────────────────────────────────────────────

def test_demande_totale(params):
    assert params.demande_totale == pytest.approx(5811.79, abs=0.01)


@pytest.mark.parametrize(
    ("acide", "attendu"),
    [("acid_29_std", 1088.24), ("acid_29_dec", 454.66),
     ("acid_54_ncl", 1782.18), ("acid_54_cl", 1500.00),
     ("acid_54_dec_total", 986.71)],
)
def test_besoins_par_type(params, acide, attendu):
    assert params.besoins_par_type()[acide] == pytest.approx(attendu, abs=0.01)


def test_demande_directe_et_engrais_se_cumulent(params):
    """U16 réclame de l'acide 29 std par sa recette DAP uniquement."""
    assert params.besoins["U16"]["acid_29_std"] == pytest.approx(388.24, abs=0.01)
    # IMACID n'a qu'une demande directe.
    assert params.besoins["IMACID"]["acid_29_std"] == pytest.approx(700.0)


def test_besoins_nuls_ecartes(params):
    """Un consommateur sans demande n'apparaît pas : il alourdirait le modèle."""
    assert "MAPS" not in params.besoins
    assert "JFC1-5" not in params.besoins
    assert "107DEF" not in params.besoins
