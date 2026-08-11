"""Résolution lexicographique du modèle.

Méthode : on optimise le niveau 1, on fige sa valeur optimale par une contrainte,
puis on optimise le niveau 2 sous cette contrainte, et ainsi de suite.

Les tolérances ``epsilon`` absorbent les erreurs d'arrondi du solveur. Sans elles,
figer ``f1 = f1*`` à l'exact peut rendre l'étape suivante numériquement infaisable,
le solveur ne retrouvant pas au bit près la valeur qu'il vient d'annoncer.

Les contraintes de figeage sont **retirées en sortie**, y compris en cas d'erreur :
la résolution rend le modèle dans l'état où elle l'a reçu, ce qui la rend
idempotente et permet de résoudre plusieurs fois le même objet.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import pulp

from .model import ModeleOptimisation

__all__ = ["Solution", "resoudre", "SolutionNonOptimale"]

#: Tolérance absolue lors du figeage d'un niveau déjà optimisé.
EPSILON_ABSOLU = 1e-4
#: Tolérance relative, qui prend le relais pour les grandes valeurs d'objectif.
#:
#: Le figeage exact ``f = f*`` est numériquement inutilisable : le solveur ne
#: retrouve pas au bit près la valeur qu'il vient d'annoncer, et la passe suivante
#: est déclarée infaisable. La tolérance reste négligeable devant les grandeurs en
#: jeu (de l'ordre du gramme pour un objectif exprimé en milliers de tonnes).
EPSILON_RELATIF = 1e-6


class SolutionNonOptimale(RuntimeError):
    """Levée quand une passe de la résolution lexicographique n'aboutit pas."""


@dataclass
class Solution:
    """Résultat d'une résolution.

    Attributes:
        statut: statut PuLP de la dernière passe (« Optimal » attendu).
        f1, f2, f3: valeurs optimales des trois niveaux.
        valeurs: valeur numérique de chaque variable, indexée par son nom.
        duree_s: temps de résolution cumulé des trois passes.
        journal: trace des passes, pour la documentation et le débogage.
    """

    statut: str
    f1: float
    f2: float
    f3: float
    valeurs: dict[str, float]
    duree_s: float
    journal: list[str] = field(default_factory=list)

    @property
    def demande_entierement_satisfaite(self) -> bool:
        """Vrai si aucune demande n'est restée non servie (au bruit numérique près)."""
        return self.f1 <= 1e-4


def _tolerance(valeur: float) -> float:
    """Tolérance de figeage adaptée à l'ordre de grandeur de la valeur."""
    return EPSILON_ABSOLU + EPSILON_RELATIF * abs(valeur)


def resoudre(
    modele: ModeleOptimisation,
    solveur: pulp.LpSolver | None = None,
    bavard: bool = False,
) -> Solution:
    """Résout le modèle par optimisation lexicographique en trois passes.

    Args:
        modele: modèle assemblé.
        solveur: solveur PuLP ; CBC silencieux par défaut.
        bavard: si vrai, journalise chaque passe sur la sortie standard.

    Returns:
        La solution, avec les valeurs des trois niveaux et de toutes les variables.

    Raises:
        SolutionNonOptimale: si l'une des passes n'atteint pas le statut « Optimal ».
    """
    solveur = solveur if solveur is not None else pulp.PULP_CBC_CMD(msg=False)
    prob = modele.prob
    journal: list[str] = []
    debut = time.perf_counter()

    niveaux = (("f1", modele.f1), ("f2", modele.f2), ("f3", modele.f3))
    optima: dict[str, float] = {}

    # Noms des contraintes de figeage, à retirer en sortie : la résolution ne
    # doit pas laisser le modèle dans un état différent de celui qu'elle a reçu.
    # Sans ce nettoyage, une seconde résolution du même objet accumulerait les
    # contraintes et le décompte publié dans la documentation deviendrait faux.
    contraintes_temporaires: list[str] = []

    try:
        for rang, (nom, expression) in enumerate(niveaux, start=1):
            prob.setObjective(expression)
            statut_code = prob.solve(solveur)
            statut = pulp.LpStatus[statut_code]

            if statut != "Optimal":
                raise SolutionNonOptimale(
                    f"Passe {rang} ({nom}) : statut « {statut} ». "
                    "Le modèle est infaisable ou non borné à ce niveau."
                )

            optimum = float(pulp.value(expression))
            optima[nom] = optimum

            message = f"Passe {rang} — {nom} = {optimum:.6f} ({statut})"
            journal.append(message)
            if bavard:
                print(message)

            # Fige ce niveau pour les passes suivantes, sauf après la dernière.
            if rang < len(niveaux):
                etiquette = f"LEXICO_fige_{nom}"
                prob += (expression <= optimum + _tolerance(optimum), etiquette)
                contraintes_temporaires.append(etiquette)

        valeurs = {
            v.name: (v.value() if v.value() is not None else 0.0)
            for v in prob.variables()
        }
    finally:
        for etiquette in contraintes_temporaires:
            prob.constraints.pop(etiquette, None)

    return Solution(
        statut="Optimal",
        f1=optima["f1"],
        f2=optima["f2"],
        f3=optima["f3"],
        valeurs=valeurs,
        duree_s=time.perf_counter() - debut,
        journal=journal,
    )
