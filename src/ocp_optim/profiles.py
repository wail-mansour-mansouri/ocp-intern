"""Profils qualité : conversion d'une demande d'engrais en besoins d'acide.

Un profil qualité est la *recette* d'un engrais, exprimée en tonnes d'acide de
chaque type par tonne d'engrais produite. Formellement, c'est une application

    q : Produit x TypeAcide -> R+

et la conversion demande -> besoins est l'application linéaire

    R[k, a] = somme sur p de  q[p, a] * F[k, p]

où ``F[k, p]`` est le tonnage d'engrais ``p`` à produire par l'atelier ``k``.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

__all__ = ["ProfilsQualite", "CHEMIN_PROFILS_DEFAUT"]

CHEMIN_PROFILS_DEFAUT = Path(__file__).resolve().parents[2] / "data" / "quality_profiles.json"

#: Clés du fichier JSON qui décrivent le profil sans être un type d'acide.
_CLES_NON_ACIDE = frozenset({"source", "remarque"})


class ProfilProduitInconnu(KeyError):
    """Levée quand un scénario réclame un engrais absent du catalogue de profils."""


class ProfilsQualite:
    """Catalogue des recettes d'engrais.

    Attributes:
        profils: dictionnaire ``{nom_produit: {type_acide: coefficient}}``.
    """

    def __init__(self, profils: dict[str, dict[str, float]]) -> None:
        self.profils = profils

    # ── Construction ────────────────────────────────────────────────────────

    @classmethod
    def depuis_json(cls, chemin: Path | str | None = None) -> "ProfilsQualite":
        """Charge le catalogue depuis un fichier JSON.

        Args:
            chemin: chemin du fichier ; par défaut ``data/quality_profiles.json``.

        Returns:
            Le catalogue chargé, nettoyé de ses clés de métadonnées.
        """
        chemin = Path(chemin) if chemin is not None else CHEMIN_PROFILS_DEFAUT
        brut = json.loads(Path(chemin).read_text(encoding="utf-8"))

        profils: dict[str, dict[str, float]] = {}
        for nom, contenu in brut["profils"].items():
            profils[nom] = {
                acide: float(coef)
                for acide, coef in contenu.items()
                if acide not in _CLES_NON_ACIDE
            }
        return cls(profils)

    # ── Utilisation ─────────────────────────────────────────────────────────

    def coefficients(self, produit: str) -> dict[str, float]:
        """Renvoie la recette d'un produit.

        Args:
            produit: nom de l'engrais.

        Raises:
            ProfilProduitInconnu: si le produit n'est pas au catalogue.
        """
        try:
            return self.profils[produit]
        except KeyError as exc:
            connus = ", ".join(sorted(self.profils))
            raise ProfilProduitInconnu(
                f"Profil qualité inconnu pour « {produit} ». Produits au catalogue : {connus}"
            ) from exc

    def besoins_atelier(self, demande_engrais: dict[str, float]) -> dict[str, float]:
        """Convertit la demande d'engrais d'un atelier en besoins d'acide.

        Args:
            demande_engrais: ``{nom_produit: tonnage à produire}``.

        Returns:
            ``{type_acide: tonnage de P2O5 requis}``, agrégé sur tous les produits.
        """
        besoins: dict[str, float] = defaultdict(float)
        for produit, tonnage in demande_engrais.items():
            for acide, coef in self.coefficients(produit).items():
                besoins[acide] += coef * tonnage
        return dict(besoins)
