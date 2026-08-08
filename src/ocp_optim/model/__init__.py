"""Construction du modèle d'optimisation.

Assemble ensembles, variables, contraintes et objectif en un problème PuLP prêt à
résoudre. La résolution elle-même est du ressort de `ocp_optim.solver`.
"""

from __future__ import annotations

from dataclasses import dataclass

import pulp

from ..preprocessing import ParametresDerives
from ..scenario import Scenario
from . import constraints as _contraintes
from .objective import PoidsObjectif, niveau_1, niveau_2, niveau_3
from .variables import Variables, creer_variables

__all__ = ["ModeleOptimisation", "construire_modele", "PoidsObjectif"]


@dataclass
class ModeleOptimisation:
    """Modèle assemblé, avec ses trois niveaux d'objectif déjà exprimés.

    Attributes:
        prob: le problème PuLP, contraintes posées mais objectif non encore fixé.
        variables: le conteneur des variables de décision.
        scenario: le scénario d'entrée.
        params: les paramètres dérivés.
        poids: les pondérations de l'objectif.
        f1, f2, f3: les trois niveaux, comme expressions affines.
    """

    prob: pulp.LpProblem
    variables: Variables
    scenario: Scenario
    params: ParametresDerives
    poids: PoidsObjectif
    f1: pulp.LpAffineExpression
    f2: pulp.LpAffineExpression
    f3: pulp.LpAffineExpression

    def statistiques(self) -> dict[str, int]:
        """Compte les variables et contraintes, pour la documentation et les tests.

        PuLP normalise la catégorie « Binary » en « Integer » borné à [0, 1] ;
        on identifie donc les binaires par leurs bornes et non par leur catégorie.
        """
        variables = self.prob.variables()
        binaires = [
            x for x in variables
            if x.cat == pulp.LpInteger and x.lowBound == 0 and x.upBound == 1
        ]
        return {
            "variables_totales": len(variables),
            "variables_binaires": len(binaires),
            "variables_continues": sum(1 for x in variables if x.cat == pulp.LpContinuous),
            "contraintes": len(self.prob.constraints),
        }


def construire_modele(
    scenario: Scenario,
    params: ParametresDerives,
    poids: PoidsObjectif | None = None,
) -> ModeleOptimisation:
    """Assemble le modèle complet.

    Args:
        scenario: scénario validé.
        params: paramètres dérivés issus du pré-traitement.
        poids: pondérations de l'objectif ; valeurs par défaut si omis.

    Returns:
        Le modèle prêt à être résolu.
    """
    poids = poids if poids is not None else PoidsObjectif()

    prob = pulp.LpProblem("ocp_acide_phosphorique", pulp.LpMinimize)
    variables = creer_variables(scenario, params)
    _contraintes.ajouter_toutes_les_contraintes(prob, variables, scenario, params)

    return ModeleOptimisation(
        prob=prob,
        variables=variables,
        scenario=scenario,
        params=params,
        poids=poids,
        f1=niveau_1(variables, poids),
        f2=niveau_2(variables, poids),
        f3=niveau_3(variables, poids),
    )
