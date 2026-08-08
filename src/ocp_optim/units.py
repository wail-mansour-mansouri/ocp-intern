"""Conversion des hauteurs de cuve (mètres) en tonnes de P2O5.

Principe commun aux quatre cuves du système :

    tonnes de P2O5 = section (m²) x hauteur (m) x densité (t/m³) x titre P2O5

Le facteur de titre est ce qui rend la sortie exprimée en **P2O5** et non en acide
marchand. C'est la preuve n°1 de la décision D-01.

Les bacs centraux IR11 et IR12 ajoutent un **volume mort** : la partie basse du bac
n'est pas soutirable, si bien que le zéro utile est décalé vers le haut.

Convention sur les hauteurs locales
-----------------------------------
Les hauteurs fournies pour les lignes d'acide 29 et 54 sont **cumulées sur les deux
cuves** de la ligne (13AB est donné à 13,75 m alors qu'une cuve plafonne à 8,40 m).
C'est licite car la conversion est linéaire en la hauteur :

    conv(h1 + h2) = conv(h1) + conv(h2)

Sommer les hauteurs puis convertir équivaut donc exactement à convertir puis sommer.
Voir décision D-08.
"""

from __future__ import annotations

from . import constants as C

__all__ = [
    "hauteur_vers_tonnes_29",
    "hauteur_vers_tonnes_54",
    "hauteur_vers_tonnes_ir11",
    "hauteur_vers_tonnes_ir12",
    "bornes_stock_29",
    "bornes_stock_54",
    "bornes_stock_ir11",
    "bornes_stock_ir12",
]


# ─────────────────────────────────────────────────────────────────────────────
# Conversions
# ─────────────────────────────────────────────────────────────────────────────

def hauteur_vers_tonnes_29(hauteur_m: float) -> float:
    """Convertit une hauteur de cuve d'acide 29 % en tonnes de P2O5.

    Args:
        hauteur_m: hauteur, **cumulée sur les deux cuves** de la ligne (m).

    Returns:
        Masse de P2O5 contenue (t).
    """
    return C.SECTION_29 * hauteur_m * C.COEF_CONVERSION_29


def hauteur_vers_tonnes_54(hauteur_m: float) -> float:
    """Convertit une hauteur de cuve d'acide 54 % en tonnes de P2O5.

    Args:
        hauteur_m: hauteur, **cumulée sur les deux cuves** de la ligne (m).

    Returns:
        Masse de P2O5 contenue (t).
    """
    return C.SECTION_54 * hauteur_m * C.COEF_CONVERSION_54


def hauteur_vers_tonnes_ir11(hauteur_m: float) -> float:
    """Convertit une hauteur du bac central IR11 en tonnes de P2O5.

    Args:
        hauteur_m: hauteur mesurée dans le bac (m).

    Returns:
        Masse de P2O5 soutirable (t). Peut être négative si la hauteur passe
        sous le volume mort ; l'écrêtage relève des fonctions de bornes.
    """
    return (hauteur_m - C.IR11_VOLUME_MORT) * C.IR11_SECTION_EQ * C.IR11_COEF


def hauteur_vers_tonnes_ir12(hauteur_m: float) -> float:
    """Convertit une hauteur du bac central IR12 en tonnes de P2O5.

    Args:
        hauteur_m: hauteur mesurée dans le bac (m).

    Returns:
        Masse de P2O5 soutirable (t). Voir la remarque de `hauteur_vers_tonnes_ir11`.
    """
    return (hauteur_m - C.IR12_VOLUME_MORT) * C.IR12_SECTION_EQ * C.IR12_COEF


# ─────────────────────────────────────────────────────────────────────────────
# Bornes de stock
# ─────────────────────────────────────────────────────────────────────────────
#
# Les bornes sont systématiquement **recalculées** à partir de la géométrie et
# jamais recopiées du dossier, qui annonce pour l'acide 29 des valeurs
# surestimées d'un facteur 1,586 (anomalie A-02). La méthode est validée par
# recoupement : appliquée à l'acide 54, elle reproduit les valeurs du dossier.
#
# Cohérence dimensionnelle : les stocks initiaux étant produits par les fonctions
# de conversion ci-dessus, les bornes doivent provenir des mêmes fonctions.

def bornes_stock_29() -> tuple[float, float]:
    """Bornes basse et haute du stock d'acide 29 d'une ligne, en tonnes de P2O5.

    La borne porte sur la **somme** des stocks standard et décadmié : les deux
    qualités sont suivies séparément mais partagent les mêmes cuves.
    """
    return (
        hauteur_vers_tonnes_29(C.N_CUVES_29 * C.H_MIN_29),
        hauteur_vers_tonnes_29(C.N_CUVES_29 * C.H_MAX_29),
    )


def bornes_stock_54() -> tuple[float, float]:
    """Bornes basse et haute du stock d'acide 54 NCL d'une ligne (t de P2O5)."""
    return (
        hauteur_vers_tonnes_54(C.N_CUVES_54 * C.H_MIN_54),
        hauteur_vers_tonnes_54(C.N_CUVES_54 * C.H_MAX_54),
    )


def bornes_stock_ir11() -> tuple[float, float]:
    """Bornes basse et haute du bac central IR11 (t de P2O5)."""
    return (
        max(0.0, hauteur_vers_tonnes_ir11(C.H_MIN_IR11)),
        hauteur_vers_tonnes_ir11(C.H_MAX_IR11),
    )


def bornes_stock_ir12() -> tuple[float, float]:
    """Bornes basse et haute du bac central IR12 (t de P2O5).

    La hauteur minimale annoncée (2,00 m) est inférieure au volume mort de la
    formule (2,70 m), ce qui donnerait un stock négatif. La borne est écrêtée à
    zéro, comme le fait d'ailleurs le dossier lui-même. Voir anomalie A-06.
    """
    return (
        max(0.0, hauteur_vers_tonnes_ir12(C.H_MIN_IR12)),
        hauteur_vers_tonnes_ir12(C.H_MAX_IR12),
    )
