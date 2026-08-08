"""Chargement et validation d'un scénario d'exploitation.

Un scénario rassemble tout ce qui est **connu avant l'optimisation** : production
imposée, stocks initiaux, heures de marche, configuration des capacités de ligne,
demandes, et paramètres de planification.

La validation est volontairement stricte : un scénario incomplet ou incohérent doit
échouer immédiatement avec un message explicite, plutôt que produire silencieusement
un modèle faux.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import constants as C
from . import units

__all__ = ["Scenario", "ScenarioInvalide", "CHEMIN_SCENARIO_REEL"]

CHEMIN_SCENARIO_REEL = (
    Path(__file__).resolve().parents[2] / "data" / "scenarios" / "real_scenario.json"
)


class ScenarioInvalide(ValueError):
    """Levée quand les données d'un scénario sont incomplètes ou incohérentes."""


@dataclass(frozen=True)
class Scenario:
    """Données d'entrée d'une journée d'exploitation.

    Toutes les masses sont en tonnes de P2O5 ; les stocks initiaux sont déjà
    convertis depuis les hauteurs de cuve.
    """

    nom: str

    # ── Production imposée ──────────────────────────────────────────────────
    production_29: dict[str, float]
    heures_marche: dict[str, float]

    # ── Stocks initiaux (tonnes de P2O5) ────────────────────────────────────
    stock_29_std_initial: dict[str, float]
    stock_29_dec_initial: dict[str, float]
    stock_54_ncl_initial: dict[str, float]
    stock_ir11_initial: float
    stock_ir12_initial: float

    # ── Configuration des capacités ─────────────────────────────────────────
    echelons_cocristallisation: dict[str, tuple[str, ...]]
    decadmiation_equipee: tuple[str, ...]
    dec29_vers_engrais: tuple[str, ...]
    clarification_active: tuple[str, ...]
    dec_cl_active: tuple[str, ...]

    # ── Demandes ────────────────────────────────────────────────────────────
    demande_directe: dict[str, dict[str, float]]
    demande_engrais: dict[str, dict[str, float]]

    # ── Paramètres de planification ─────────────────────────────────────────
    transfert_min: float = C.TRANSFERT_MIN_DEFAUT
    transfert_max: float = C.TRANSFERT_MAX_DEFAUT
    alpha_dec_cl: float = C.ALPHA_DEC_CL_DEFAUT
    tolerance_concentration: float = C.TOLERANCE_CONCENTRATION_DEFAUT

    # ── Traçabilité ─────────────────────────────────────────────────────────
    hauteurs_initiales: dict = field(default_factory=dict, repr=False)

    # ── Construction ────────────────────────────────────────────────────────

    @classmethod
    def depuis_json(cls, chemin: Path | str | None = None) -> "Scenario":
        """Charge un scénario depuis un fichier JSON, convertit et valide.

        Args:
            chemin: chemin du fichier ; par défaut le scénario réel de référence.

        Raises:
            ScenarioInvalide: si les données sont incomplètes ou incohérentes.
        """
        chemin = Path(chemin) if chemin is not None else CHEMIN_SCENARIO_REEL
        brut = json.loads(Path(chemin).read_text(encoding="utf-8"))

        for cle in ("production_29", "hauteurs_initiales", "heures_marche",
                    "echelons_cocristallisation", "capacites_lignes",
                    "demande_directe", "demande_engrais"):
            if cle not in brut:
                raise ScenarioInvalide(f"Section « {cle} » absente du scénario {chemin}.")

        h = brut["hauteurs_initiales"]
        caps = brut["capacites_lignes"]
        params = brut.get("parametres_planification", {})

        scenario = cls(
            nom=brut.get("_meta", {}).get("nom", Path(chemin).stem),
            production_29={k: float(v) for k, v in brut["production_29"].items()},
            heures_marche={k: float(v) for k, v in brut["heures_marche"].items()},
            stock_29_std_initial={
                k: units.hauteur_vers_tonnes_29(v) for k, v in h["stock_29_std"].items()
            },
            stock_29_dec_initial={
                k: units.hauteur_vers_tonnes_29(v) for k, v in h["stock_29_dec"].items()
            },
            stock_54_ncl_initial={
                k: units.hauteur_vers_tonnes_54(v) for k, v in h["stock_54_ncl"].items()
            },
            stock_ir11_initial=units.hauteur_vers_tonnes_ir11(h["ir11"]),
            stock_ir12_initial=units.hauteur_vers_tonnes_ir12(h["ir12"]),
            echelons_cocristallisation={
                ligne: tuple(ech) for ligne, ech in brut["echelons_cocristallisation"].items()
            },
            decadmiation_equipee=tuple(caps.get("decadmiation_equipee", ())),
            dec29_vers_engrais=tuple(caps.get("dec29_vers_engrais", ())),
            clarification_active=tuple(caps.get("clarification_active", ())),
            dec_cl_active=tuple(caps.get("dec_cl_active", ())),
            demande_directe={
                k: {a: float(q) for a, q in d.items()}
                for k, d in brut["demande_directe"].items()
            },
            demande_engrais={
                k: {p: float(q) for p, q in d.items()}
                for k, d in brut["demande_engrais"].items()
            },
            transfert_min=float(params.get("transfert_min", C.TRANSFERT_MIN_DEFAUT)),
            transfert_max=float(params.get("transfert_max", C.TRANSFERT_MAX_DEFAUT)),
            alpha_dec_cl=float(params.get("alpha_dec_cl", C.ALPHA_DEC_CL_DEFAUT)),
            tolerance_concentration=float(
                params.get("tolerance_concentration", C.TOLERANCE_CONCENTRATION_DEFAUT)
            ),
            hauteurs_initiales=h,
        )
        scenario.valider()
        return scenario

    # ── Validation ──────────────────────────────────────────────────────────

    def valider(self) -> None:
        """Vérifie la complétude et la cohérence du scénario.

        Raises:
            ScenarioInvalide: au premier problème détecté, avec un message précis.
        """
        erreurs: list[str] = []

        # Complétude des données indexées par ligne.
        for ligne in C.LIGNES_29:
            for champ, table in (
                ("production_29", self.production_29),
                ("stock_29_std_initial", self.stock_29_std_initial),
                ("stock_29_dec_initial", self.stock_29_dec_initial),
            ):
                if ligne not in table:
                    erreurs.append(f"{champ} : ligne {ligne} manquante.")

        for ligne in C.LIGNES_54:
            if ligne not in self.stock_54_ncl_initial:
                erreurs.append(f"stock_54_ncl_initial : ligne {ligne} manquante.")

        # Complétude et validité des heures de marche.
        for echelon in C.CAPACITE_ECHELON:
            if echelon not in self.heures_marche:
                erreurs.append(f"heures_marche : échelon {echelon} manquant.")
            elif not 0.0 <= self.heures_marche[echelon] <= 24.0:
                erreurs.append(
                    f"heures_marche[{echelon}] = {self.heures_marche[echelon]} "
                    "hors de l'intervalle [0, 24]."
                )

        # Les échelons déclarés en cocristallisation doivent appartenir à leur ligne,
        # et cette ligne doit être physiquement équipée.
        for ligne, echelons in self.echelons_cocristallisation.items():
            if ligne not in C.LIGNES_COC_POSSIBLE:
                erreurs.append(
                    f"echelons_cocristallisation : la ligne {ligne} n'est pas équipée "
                    f"de cocristallisation (lignes possibles : {C.LIGNES_COC_POSSIBLE})."
                )
                continue
            for echelon in echelons:
                if echelon not in C.GROUPES_ECHELONS[ligne]:
                    erreurs.append(
                        f"echelons_cocristallisation[{ligne}] : l'échelon {echelon} "
                        f"n'appartient pas à cette ligne."
                    )

        # Cohérence des ensembles de capacités.
        for ligne in self.decadmiation_equipee:
            if ligne not in C.LIGNES_29:
                erreurs.append(f"decadmiation_equipee : {ligne} n'est pas une ligne d'acide 29.")
        for ligne in self.dec29_vers_engrais:
            if ligne not in self.decadmiation_equipee:
                erreurs.append(
                    f"dec29_vers_engrais : {ligne} doit d'abord être équipée de "
                    "décadmiation (decadmiation_equipee)."
                )
        for champ, lignes in (
            ("clarification_active", self.clarification_active),
            ("dec_cl_active", self.dec_cl_active),
        ):
            for ligne in lignes:
                if ligne not in C.LIGNES_54:
                    erreurs.append(f"{champ} : {ligne} n'est pas une ligne d'acide 54.")

        # Une ligne ne peut produire du DEC_CL que si elle peut clarifier.
        for ligne in self.dec_cl_active:
            if ligne not in self.clarification_active:
                erreurs.append(
                    f"dec_cl_active : {ligne} produit du DEC_CL mais n'est pas dans "
                    "clarification_active ; or le DEC_CL passe par les décanteurs."
                )

        # Consommateurs connus.
        for consommateur in list(self.demande_directe) + list(self.demande_engrais):
            if consommateur not in C.CONSOMMATEURS:
                erreurs.append(f"Consommateur inconnu : {consommateur}.")

        # Signes et plages des paramètres.
        if self.transfert_min < 0:
            erreurs.append("transfert_min doit être positif ou nul.")
        if self.transfert_max < self.transfert_min:
            erreurs.append("transfert_max doit être supérieur ou égal à transfert_min.")
        if not 0.0 <= self.alpha_dec_cl < 1.0:
            erreurs.append("alpha_dec_cl doit appartenir à [0, 1[.")
        if not 0.0 <= self.tolerance_concentration <= 0.5:
            erreurs.append("tolerance_concentration doit appartenir à [0, 0.5].")

        for champ, table in (
            ("production_29", self.production_29),
            ("stock_29_std_initial", self.stock_29_std_initial),
            ("stock_29_dec_initial", self.stock_29_dec_initial),
            ("stock_54_ncl_initial", self.stock_54_ncl_initial),
        ):
            for cle, valeur in table.items():
                if valeur < 0:
                    erreurs.append(f"{champ}[{cle}] = {valeur} : valeur négative.")

        if erreurs:
            raise ScenarioInvalide(
                "Scénario invalide :\n  - " + "\n  - ".join(erreurs)
            )
