"""Verrouillage des valeurs citées dans la documentation et le rapport.

Ce fichier a un rôle particulier : il ne teste pas un comportement du code, il
**garantit que les chiffres publiés restent vrais**.

Le projet cite des valeurs numériques dans une dizaine de documents Markdown et
dans un rapport LaTeX de 79 pages. Sans ce filet, une modification du modèle
rendrait silencieusement fausse une partie de cette documentation — et une
documentation fausse est pire qu'une documentation absente, car on lui fait
confiance.

Chaque assertion porte donc en commentaire l'endroit où la valeur est publiée.
Si l'un de ces tests échoue, deux lectures possibles :
  - le changement est voulu → mettre à jour le test **et** les documents cités ;
  - le changement est involontaire → c'est une régression.
"""

from __future__ import annotations

import dataclasses

import pytest

from ocp_optim import units
from ocp_optim.analysis import resoudre_scenario
from ocp_optim.validation import valider


# ─────────────────────────────────────────────────────────────────────────────
# Taille du modèle — publiée dans README, docs-helper/05, rapport ch. 4 et 7
# ─────────────────────────────────────────────────────────────────────────────

def test_taille_publiee_du_modele(modele):
    """170 variables dont 29 binaires, 141 continues, 138 contraintes.

    Attention : ce décompte porte sur le modèle **avant** résolution. La
    résolution lexicographique ajoute deux contraintes de figeage (une par
    niveau intermédiaire), ce qui porterait le total à 140.
    """
    stats = modele.statistiques()
    assert stats["variables_totales"] == 170
    assert stats["variables_binaires"] == 29
    assert stats["variables_continues"] == 141
    assert stats["contraintes"] == 138


def test_temps_de_resolution_publie(solution):
    """Publié comme « moins de 0,1 s ».

    La marge est large : la médiane mesurée est de l'ordre de 0,07 s, mais le
    temps dépend de la charge de la machine. Le seuil de 1 s laisse de la marge
    tout en détectant une explosion combinatoire.
    """
    assert solution.duree_s < 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Données d'entrée — publiées dans docs-helper/04 et rapport annexe B
# ─────────────────────────────────────────────────────────────────────────────

def test_stocks_initiaux_publies(scenario):
    assert sum(scenario.stock_29_std_initial.values()) == pytest.approx(3553.7, abs=0.05)
    assert sum(scenario.stock_29_dec_initial.values()) == pytest.approx(801.5, abs=0.05)
    assert sum(scenario.stock_54_ncl_initial.values()) == pytest.approx(2707.7, abs=0.05)
    assert scenario.stock_ir11_initial == pytest.approx(5514.7, abs=0.05)
    assert scenario.stock_ir12_initial == pytest.approx(3821.6, abs=0.05)


def test_bornes_de_stock_publiees():
    assert units.bornes_stock_29() == pytest.approx((229.8, 965.3), abs=0.05)
    assert units.bornes_stock_54() == pytest.approx((473.1, 1482.4), abs=0.05)
    assert units.bornes_stock_ir11() == pytest.approx((90.6, 6372.4), abs=0.05)
    assert units.bornes_stock_ir12() == pytest.approx((0.0, 4806.7), abs=0.05)


def test_production_54_publiee(params):
    """Contredit le dossier (6 636) — anomalie A-01."""
    assert params.production_54_totale == pytest.approx(6981.7, abs=0.05)
    attendu = {"14EXT": 1505.0, "14AB": 2134.2, "14CD": 1040.0,
               "14XY": 820.8, "14ZU": 1481.7}
    for ligne, valeur in attendu.items():
        assert params.production_54[ligne] == pytest.approx(valeur, abs=0.05)


def test_cocristallisation_publiee(params):
    """2 431,3 t de CoC pour un besoin de 986,7 t — le facteur 2,5 du rapport."""
    assert params.coc_total == pytest.approx(2431.3, abs=0.05)
    besoin = params.besoins_par_type()["acid_54_dec_total"]
    assert params.coc_total / besoin == pytest.approx(2.46, abs=0.05)


def test_demande_publiee(params):
    assert params.demande_totale == pytest.approx(5811.79, abs=0.005)
    attendu = {
        "acid_29_std": 1088.24, "acid_29_dec": 454.66, "acid_54_ncl": 1782.18,
        "acid_54_cl": 1500.00, "acid_54_dec_total": 986.71,
    }
    for acide, valeur in attendu.items():
        assert params.besoins_par_type()[acide] == pytest.approx(valeur, abs=0.005)


# ─────────────────────────────────────────────────────────────────────────────
# Solution du scénario de référence — publiée partout
# ─────────────────────────────────────────────────────────────────────────────

def test_valeurs_publiees_de_l_objectif(resultat):
    assert resultat.f1 == pytest.approx(0.0, abs=1e-4)
    assert resultat.f2 == pytest.approx(1268.3, abs=0.1)
    assert resultat.f3 == pytest.approx(3111.9, abs=0.1)


def test_plan_publie(resultat):
    """750 t sur 13XY, trois transferts, deux lignes clarifiantes."""
    assert resultat.lignes_29["13XY"].decadmiation == pytest.approx(750.0)
    assert sum(r.decadmiation for r in resultat.lignes_29.values()) == pytest.approx(750.0)

    assert len(resultat.transferts) == 3
    assert resultat.transferts[("13F", "13ZU")] == pytest.approx(758.8, abs=0.1)
    assert resultat.transferts[("13F", "13E")] == pytest.approx(603.3, abs=0.1)
    assert resultat.transferts[("13CD", "13AB")] == pytest.approx(100.0, abs=0.1)

    assert resultat.lignes_54["14XY"].clarification_dec == pytest.approx(476.7, abs=0.1)
    assert resultat.lignes_54["14ZU"].clarification_ncl == pytest.approx(722.5, abs=0.1)


def test_violations_publiees(resultat):
    """IR11 déborde de 1 016 t, 14EXT manque 252,3 t."""
    assert resultat.violations_bandes["IR11"] == pytest.approx(1016.0, abs=0.1)
    assert resultat.violations_bandes["14EXT"] == pytest.approx(252.3, abs=0.1)


def test_bilan_ir11_publie(resultat):
    """5 514,7 + 2 860,4 − 986,7 = 7 388,3 pour une capacité de 6 372,4."""
    assert resultat.ir11.stock_initial == pytest.approx(5514.7, abs=0.05)
    assert resultat.ir11.total_entrees == pytest.approx(2860.4, abs=0.05)
    assert resultat.ir11.total_livraisons == pytest.approx(986.7, abs=0.05)
    assert resultat.ir11.stock_final == pytest.approx(7388.3, abs=0.05)
    assert resultat.ir11.capacite == pytest.approx(6372.4, abs=0.05)


def test_nombre_de_controles_publie(resultat, scenario):
    """86 contrôles de validation, tous réussis."""
    rapport = valider(resultat, scenario)
    assert rapport.controles_effectues == 86
    assert rapport.conforme


# ─────────────────────────────────────────────────────────────────────────────
# Analyses publiées — docs-helper/09 et rapport ch. 7
# ─────────────────────────────────────────────────────────────────────────────

def test_balayage_echelons_publie(scenario, profils):
    """Le tableau du chapitre 7 : 4/4 → 1 016 t de dépassement, 1/4 → zéro."""
    from ocp_optim.analysis import balayer_echelons_cocristallisation

    points = {p.valeur: p for p in
              balayer_echelons_cocristallisation(scenario, "14EXT", profils)}
    assert points["4/4"].depassement_ir11 == pytest.approx(1016.0, abs=0.5)
    assert points["3/4"].depassement_ir11 == pytest.approx(785.4, abs=0.5)
    assert points["2/4"].depassement_ir11 == pytest.approx(390.1, abs=0.5)
    assert points["1/4"].depassement_ir11 == pytest.approx(0.0, abs=1e-3)


def test_domaine_admissible_de_alpha_publie(scenario, profils):
    """Publié comme « alpha ≲ 0,22 » : faisable à 0,20, infaisable à 0,25."""
    from ocp_optim.analysis import balayer_parametre

    points = {p.valeur: p for p in
              balayer_parametre(scenario, "alpha_dec_cl", [0.20, 0.25], profils)}
    assert points[0.20].faisable
    assert not points[0.25].faisable


def test_insensibilite_a_tau_max_publiee(scenario, profils):
    """Publié : au-delà de 750 t, la solution ne change plus."""
    from ocp_optim.analysis import balayer_parametre

    points = balayer_parametre(scenario, "transfert_max", [750.0, 1000.0, 1500.0], profils)
    references = (points[0].f2, points[0].f3, points[0].transferts)
    for point in points[1:]:
        assert (point.f2, point.f3, point.transferts) == pytest.approx(references, abs=0.1)


def test_mode_decidable_publie(scenario, profils):
    """Publié dans D-11 : f2 tombe à 0, CoC à 472 t, f3 à 2 125,2."""
    variante = dataclasses.replace(scenario, cocristallisation_decidable=True)
    resultat = resoudre_scenario(variante, profils)

    assert resultat.f1 == pytest.approx(0.0, abs=1e-4)
    assert resultat.f2 == pytest.approx(0.0, abs=1e-3)
    assert resultat.f3 == pytest.approx(2125.2, abs=0.5)
    coc = sum(r.coc_produit for r in resultat.lignes_54.values())
    assert coc == pytest.approx(472.0, abs=0.5)
