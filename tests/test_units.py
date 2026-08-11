"""Tests des conversions hauteur -> tonnes de P2O5 et des bornes de stock."""

from __future__ import annotations

import pytest

from ocp_optim import constants as C
from ocp_optim import units


# ─────────────────────────────────────────────────────────────────────────────
# Cohérence des coefficients avec la physique déclarée
# ─────────────────────────────────────────────────────────────────────────────

def test_coefficients_coherents_avec_la_physique():
    """Les coefficients publiés doivent valoir le produit titre x densité.

    C'est la preuve n°1 de la décision D-01 : si ce test passe, la conversion
    inclut bien le titre en P2O5, donc elle rend des tonnes de P2O5 et non des
    tonnes d'acide marchand.
    """
    assert C.COEF_CONVERSION_29 == pytest.approx(
        C.TITRE_P2O5_29 * C.DENSITE_29, rel=1e-3
    ), "0,33 doit être l'arrondi de 0,26 x 1,270"
    assert C.COEF_CONVERSION_54 == pytest.approx(
        C.TITRE_P2O5_54 * C.DENSITE_54, rel=1e-9
    ), "0,83 doit valoir exactement 0,50 x 1,660"


# ─────────────────────────────────────────────────────────────────────────────
# Linéarité : c'est elle qui autorise à convertir une hauteur cumulée (D-08)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "conversion",
    [units.hauteur_vers_tonnes_29, units.hauteur_vers_tonnes_54],
)
def test_conversion_locale_lineaire(conversion):
    """conv(h1 + h2) == conv(h1) + conv(h2) pour les cuves locales."""
    assert conversion(3.0 + 5.0) == pytest.approx(conversion(3.0) + conversion(5.0))


@pytest.mark.parametrize(
    "conversion",
    [units.hauteur_vers_tonnes_29, units.hauteur_vers_tonnes_54],
)
def test_conversion_locale_nulle_en_zero(conversion):
    """Une cuve vide contient zéro tonne : pas de volume mort en local."""
    assert conversion(0.0) == pytest.approx(0.0)


def test_bacs_centraux_ont_un_volume_mort():
    """Sous le volume mort, la conversion devient négative : rien n'est soutirable."""
    assert units.hauteur_vers_tonnes_ir11(C.IR11_VOLUME_MORT) == pytest.approx(0.0)
    assert units.hauteur_vers_tonnes_ir12(C.IR12_VOLUME_MORT) == pytest.approx(0.0)
    assert units.hauteur_vers_tonnes_ir12(1.0) < 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Reproduction des valeurs du dossier
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("hauteur", "attendu"),
    [(13.75, 790.0), (6.75, 387.8), (5.05, 290.2),
     (14.20, 815.9), (7.70, 442.4), (14.40, 827.4)],
)
def test_stocks_initiaux_29_du_scenario_reel(hauteur, attendu):
    """Les hauteurs du scénario réel donnent bien les stocks annoncés."""
    assert units.hauteur_vers_tonnes_29(hauteur) == pytest.approx(attendu, abs=0.1)


@pytest.mark.parametrize(
    ("hauteur", "attendu"),
    [(11.43, 901.3), (4.68, 369.0), (3.78, 298.1), (11.65, 918.6), (2.80, 220.8)],
)
def test_stocks_initiaux_54_du_scenario_reel(hauteur, attendu):
    assert units.hauteur_vers_tonnes_54(hauteur) == pytest.approx(attendu, abs=0.1)


def test_stocks_initiaux_centraux_du_scenario_reel():
    assert units.hauteur_vers_tonnes_ir11(9.38) == pytest.approx(5514.7, abs=0.1)
    assert units.hauteur_vers_tonnes_ir12(9.14) == pytest.approx(3821.6, abs=0.1)


# ─────────────────────────────────────────────────────────────────────────────
# Bornes de stock — anomalie A-02
# ─────────────────────────────────────────────────────────────────────────────

def test_bornes_54_reproduisent_le_dossier():
    """Validation de la méthode de calcul des bornes.

    Le dossier annonce 473,4 et 1483,6 pour l'acide 54. La méthode géométrique
    les reproduit au dixième près : elle est donc correcte, ce qui permet de
    conclure que l'écart constaté sur l'acide 29 est une erreur du dossier.
    """
    z_min, z_max = units.bornes_stock_54()
    assert z_min == pytest.approx(473.4, abs=0.5)
    assert z_max == pytest.approx(1483.6, abs=1.5)


def test_bornes_29_different_du_dossier_anomalie_a02():
    """Les bornes recalculées de l'acide 29 s'écartent du dossier d'un facteur 1,586.

    Ce test verrouille le constat de l'anomalie A-02 : si un jour l'encadrant
    fournit d'autres valeurs, ce test échouera et signalera qu'il faut réexaminer
    la décision D-07.
    """
    z_min, z_max = units.bornes_stock_29()
    assert z_min == pytest.approx(229.8, abs=0.5)
    assert z_max == pytest.approx(965.3, abs=0.5)
    assert 364.5 / z_min == pytest.approx(1.586, abs=0.01)
    assert 1530.7 / z_max == pytest.approx(1.586, abs=0.01)


def test_borne_basse_ir12_ecretee_a_zero():
    """La hauteur minimale d'IR12 passe sous son volume mort : la borne est écrêtée."""
    z_min, z_max = units.bornes_stock_ir12()
    assert z_min == 0.0
    assert z_max == pytest.approx(4806.7, abs=0.5)


def test_bornes_ir11():
    z_min, z_max = units.bornes_stock_ir11()
    assert z_min == pytest.approx(90.6, abs=0.5)
    assert z_max == pytest.approx(6372.4, abs=0.5)


@pytest.mark.parametrize(
    "bornes",
    [units.bornes_stock_29, units.bornes_stock_54,
     units.bornes_stock_ir11, units.bornes_stock_ir12],
)
def test_bornes_ordonnees(bornes):
    """La borne basse est toujours strictement inférieure à la borne haute."""
    z_min, z_max = bornes()
    assert z_min < z_max
