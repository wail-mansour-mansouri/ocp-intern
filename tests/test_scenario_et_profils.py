"""Tests du chargement des profils qualité et de la validation des scénarios."""

from __future__ import annotations

import dataclasses
import json

import pytest

from ocp_optim import constants as C
from ocp_optim.profiles import ProfilProduitInconnu, ProfilsQualite
from ocp_optim.scenario import Scenario, ScenarioInvalide


# ─────────────────────────────────────────────────────────────────────────────
# Profils qualité
# ─────────────────────────────────────────────────────────────────────────────

def test_profils_ne_contiennent_que_des_types_d_acide_valides(profils):
    """Les clés de métadonnées ne doivent pas être prises pour des types d'acide."""
    valides = set(C.ACIDES_LOCAUX) | set(C.ACIDES_CENTRAUX) | {C.BESOIN_54_DEC_TOTAL}
    for produit, coefficients in profils.profils.items():
        assert set(coefficients) <= valides, f"clé inattendue dans le profil {produit}"
        assert all(isinstance(v, float) for v in coefficients.values())


def test_profils_a_coefficients_positifs(profils):
    for coefficients in profils.profils.values():
        assert all(c > 0 for c in coefficients.values())


def test_conversion_demande_engrais_en_besoins(profils):
    """3057 t de DAP demandent 0,127 x 3057 t d'acide 29 std et 0,354 x 3057 de NCL."""
    besoins = profils.besoins_atelier({"DAP_STANDARD": 3057})
    assert besoins["acid_29_std"] == pytest.approx(388.24, abs=0.01)
    assert besoins["acid_54_ncl"] == pytest.approx(1082.18, abs=0.01)


def test_besoins_s_agregent_sur_plusieurs_produits(profils):
    """Deux produits réclamant le même acide voient leurs besoins s'additionner."""
    besoins = profils.besoins_atelier({
        "NPK_12_24_12_EU": 1540,           # 0,091 de dec_total
        "MAP_11_52_EU": 3037,              # 0,129 de dec_total
    })
    attendu = 0.091 * 1540 + 0.129 * 3037
    assert besoins[C.BESOIN_54_DEC_TOTAL] == pytest.approx(attendu, abs=0.01)


def test_produit_inconnu_leve_une_erreur_explicite(profils):
    with pytest.raises(ProfilProduitInconnu, match="ENGRAIS_IMAGINAIRE"):
        profils.besoins_atelier({"ENGRAIS_IMAGINAIRE": 100})


# ─────────────────────────────────────────────────────────────────────────────
# Chargement du scénario réel
# ─────────────────────────────────────────────────────────────────────────────

def test_scenario_reel_se_charge(scenario):
    assert set(scenario.production_29) == set(C.LIGNES_29)
    assert set(scenario.stock_54_ncl_initial) == set(C.LIGNES_54)
    assert set(scenario.heures_marche) == set(C.CAPACITE_ECHELON)


def test_production_29_totale(scenario):
    assert sum(scenario.production_29.values()) == pytest.approx(8300.0)


def test_stocks_initiaux_convertis(scenario):
    assert sum(scenario.stock_29_std_initial.values()) == pytest.approx(3553.7, abs=0.5)
    assert sum(scenario.stock_29_dec_initial.values()) == pytest.approx(801.5, abs=0.5)
    assert sum(scenario.stock_54_ncl_initial.values()) == pytest.approx(2707.7, abs=0.5)
    assert scenario.stock_ir11_initial == pytest.approx(5514.7, abs=0.5)
    assert scenario.stock_ir12_initial == pytest.approx(3821.6, abs=0.5)


# ─────────────────────────────────────────────────────────────────────────────
# Validation : un scénario incohérent doit échouer clairement
# ─────────────────────────────────────────────────────────────────────────────

def _scenario_modifie(scenario: Scenario, **champs) -> None:
    """Applique une modification et déclenche la validation."""
    dataclasses.replace(scenario, **champs).valider()


def test_heures_de_marche_hors_bornes_rejetees(scenario):
    heures = dict(scenario.heures_marche)
    heures["E"] = 30.0
    with pytest.raises(ScenarioInvalide, match="hors de l'intervalle"):
        _scenario_modifie(scenario, heures_marche=heures)


def test_ligne_manquante_rejetee(scenario):
    production = dict(scenario.production_29)
    del production["13AB"]
    with pytest.raises(ScenarioInvalide, match="13AB manquante"):
        _scenario_modifie(scenario, production_29=production)


def test_cocristallisation_sur_ligne_non_equipee_rejetee(scenario):
    with pytest.raises(ScenarioInvalide, match="n'est pas équipée"):
        _scenario_modifie(scenario, echelons_cocristallisation={"14CD": ("C",)})


def test_echelon_etranger_a_sa_ligne_rejete(scenario):
    with pytest.raises(ScenarioInvalide, match="n'appartient pas à cette ligne"):
        _scenario_modifie(scenario, echelons_cocristallisation={"14EXT": ("C",)})


def test_dec_cl_sans_clarification_rejete(scenario):
    """Le DEC_CL passe par les décanteurs : la ligne doit pouvoir clarifier."""
    with pytest.raises(ScenarioInvalide, match="clarification_active"):
        _scenario_modifie(scenario, dec_cl_active=("14EXT",))


def test_dec29_vers_engrais_sans_filtre_rejete(scenario):
    with pytest.raises(ScenarioInvalide, match="decadmiation_equipee"):
        _scenario_modifie(scenario, dec29_vers_engrais=("13E",))


def test_alpha_hors_bornes_rejete(scenario):
    with pytest.raises(ScenarioInvalide, match="alpha_dec_cl"):
        _scenario_modifie(scenario, alpha_dec_cl=1.5)


def test_transfert_max_inferieur_au_min_rejete(scenario):
    with pytest.raises(ScenarioInvalide, match="transfert_max"):
        _scenario_modifie(scenario, transfert_min=500.0, transfert_max=100.0)


def test_production_negative_rejetee(scenario):
    production = dict(scenario.production_29)
    production["13AB"] = -10.0
    with pytest.raises(ScenarioInvalide, match="valeur négative"):
        _scenario_modifie(scenario, production_29=production)


def test_consommateur_inconnu_rejete(scenario):
    with pytest.raises(ScenarioInvalide, match="Consommateur inconnu"):
        _scenario_modifie(scenario, demande_directe={"USINE_FANTOME": {"acid_29_std": 1}})


def test_section_absente_rejetee(tmp_path):
    fichier = tmp_path / "incomplet.json"
    fichier.write_text(json.dumps({"production_29": {}}), encoding="utf-8")
    with pytest.raises(ScenarioInvalide, match="absente"):
        Scenario.depuis_json(fichier)
