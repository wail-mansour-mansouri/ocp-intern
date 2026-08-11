"""Optimisation de la production et de la distribution d'acide phosphorique.

Site OCP de Jorf Lasfar. Modèle linéaire mixte en nombres entiers, mono-période.

Toutes les masses sont exprimées en **tonnes de P2O5** (décision D-01).

Chaîne de traitement :

    Scenario  ->  calculer_parametres  ->  construire_modele  ->  resoudre  ->  valider
     (JSON)         (déterministe)            (MILP)             (CBC)      (indépendant)
"""

from __future__ import annotations

__version__ = "0.1.0"
