"""Fonction objectif — optimisation lexicographique à trois niveaux.

Pourquoi trois niveaux
----------------------
Le dossier demande de « maximiser le total d'acide livré » tout en imposant que
toutes les demandes soient « exactement satisfaites ». Ces deux exigences sont
incompatibles au sens de l'optimisation : si la satisfaction est une égalité,
alors le total livré vaut identiquement la somme des demandes, qui est un
paramètre. L'objectif est donc **constant sur tout le domaine réalisable** et ne
départage aucune solution ; le solveur renverrait un sommet arbitraire du
polyèdre, et deux exécutions identiques pourraient produire des plans très
différents.

L'objectif lexicographique corrige ce défaut sans trahir l'intention :

  - **Niveau 1** — minimiser la demande non satisfaite. Strictement équivalent à
    l'objectif demandé quand tout est servi, et il le généralise au cas où le
    système ne peut pas tout servir : le modèle sert alors au mieux et indique ce
    qui manque, au lieu de répondre « Infeasible », réponse inutilisable en
    exploitation.
  - **Niveau 2** — minimiser les écarts aux contraintes molles : violations des
    bandes de stock et écarts à la charge de concentration planifiée.
  - **Niveau 3** — minimiser le coût opératoire : volume et nombre de transferts,
    décadmiation, écart des stocks finaux à leur cible.

Aucun compromis n'est possible entre niveaux : gagner sur le niveau 2 ne justifie
jamais de perdre sur le niveau 1. C'est exactement la hiérarchie industrielle
voulue — servir le client prime sur tout le reste.
"""

from __future__ import annotations

from dataclasses import dataclass

import pulp

from .variables import Variables

__all__ = ["PoidsObjectif", "niveau_1", "niveau_2", "niveau_3"]


@dataclass(frozen=True)
class PoidsObjectif:
    """Pondérations des trois niveaux de l'objectif.

    Attributes:
        priorite_client: poids par consommateur pour la demande non satisfaite ;
            1 pour tous par défaut. Permet de privilégier un client contractuel.
        poids_ecart_charge: pénalité de l'écart à la charge de concentration.
            Supérieure à celle des bandes de stock car l'encadrant qualifie cette
            égalité de « normalement rigide ».
        poids_bande_stock: pénalité du dépassement d'une bande de sécurité.
        cout_transfert_tonne: coût par tonne transférée (énergie de pompage).
        cout_transfert_operation: coût fixe par transfert (mobilisation d'opérateur).
        cout_decadmiation_tonne: coût par tonne décadmiée (réactifs, filtration).
        cout_ecart_cible: coût par tonne d'écart du stock final à sa cible.
    """

    priorite_client: dict[str, float] | None = None
    poids_ecart_charge: float = 10.0
    poids_bande_stock: float = 1.0
    cout_transfert_tonne: float = 1.0
    cout_transfert_operation: float = 50.0
    cout_decadmiation_tonne: float = 1.0
    cout_ecart_cible: float = 0.1

    def priorite(self, consommateur: str) -> float:
        """Poids de priorité commerciale d'un consommateur (1 par défaut)."""
        if not self.priorite_client:
            return 1.0
        return self.priorite_client.get(consommateur, 1.0)


def niveau_1(v: Variables, poids: PoidsObjectif) -> pulp.LpAffineExpression:
    """Niveau 1 — demande non satisfaite, pondérée par priorité commerciale.

    Minimiser cette quantité revient exactement à maximiser le total livré,
    puisque livré + manque = demande, et que la demande est un paramètre.
    """
    return pulp.lpSum(
        poids.priorite(consommateur) * manque
        for (consommateur, _), manque in v.rho.items()
    )


def niveau_2(v: Variables, poids: PoidsObjectif) -> pulp.LpAffineExpression:
    """Niveau 2 — violations des contraintes molles.

    Deux familles : les bandes de sécurité des cuves, et l'écart à la charge de
    concentration planifiée (tolérance accordée par l'encadrant, mais à n'utiliser
    qu'en dernier recours).
    """
    violations_stock = pulp.lpSum(v.nu_plus.values()) + pulp.lpSum(v.nu_minus.values())
    ecarts_charge = pulp.lpSum(v.e_plus.values()) + pulp.lpSum(v.e_minus.values())
    return (
        poids.poids_bande_stock * violations_stock
        + poids.poids_ecart_charge * ecarts_charge
    )


def niveau_3(v: Variables, poids: PoidsObjectif) -> pulp.LpAffineExpression:
    """Niveau 3 — coût opératoire.

    C'est ce niveau qui transforme un plan simplement réalisable en un plan sobre
    et robuste : pas de transfert inutile, pas de décadmiation superflue, et des
    cuves laissées en bonne position pour le lendemain.
    """
    volume_transfere = pulp.lpSum(v.t.values())
    nombre_transferts = pulp.lpSum(v.b.values())
    decadmiation = pulp.lpSum(v.d.values())
    ecart_cible = pulp.lpSum(v.g_plus.values()) + pulp.lpSum(v.g_minus.values())

    return (
        poids.cout_transfert_tonne * volume_transfere
        + poids.cout_transfert_operation * nombre_transferts
        + poids.cout_decadmiation_tonne * decadmiation
        + poids.cout_ecart_cible * ecart_cible
    )
