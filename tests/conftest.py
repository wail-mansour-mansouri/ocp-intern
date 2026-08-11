"""Fixtures partagées par les tests.

Le scénario réel est résolu **une seule fois** par session : la résolution prend
moins d'une seconde, mais la répéter dans chaque test rendrait la suite inutilement
lente à mesure qu'elle grossit.
"""

from __future__ import annotations

import pytest

from ocp_optim.model import construire_modele
from ocp_optim.preprocessing import calculer_parametres
from ocp_optim.profiles import ProfilsQualite
from ocp_optim.results import extraire
from ocp_optim.scenario import Scenario
from ocp_optim.solver import resoudre


@pytest.fixture(scope="session")
def profils() -> ProfilsQualite:
    return ProfilsQualite.depuis_json()


@pytest.fixture(scope="session")
def scenario() -> Scenario:
    return Scenario.depuis_json()


@pytest.fixture(scope="session")
def params(scenario, profils):
    return calculer_parametres(scenario, profils)


@pytest.fixture(scope="session")
def modele(scenario, params):
    return construire_modele(scenario, params)


@pytest.fixture(scope="session")
def solution(modele):
    return resoudre(modele)


@pytest.fixture(scope="session")
def resultat(modele, solution):
    return extraire(modele, solution)
