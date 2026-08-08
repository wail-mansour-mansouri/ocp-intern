"""Export JSON des résultats, lisible par machine.

Complément du rapport Excel : ce format permet de rejouer, comparer ou archiver
les résultats sans passer par un tableur, ce qui est indispensable pour les
analyses de sensibilité et les tests de non-régression.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ..results import Resultat
from ..scenario import Scenario
from ..validation import RapportValidation

__all__ = ["generer_rapport_json", "resultat_en_dictionnaire"]


def resultat_en_dictionnaire(
    resultat: Resultat, scenario: Scenario, rapport: RapportValidation | None = None
) -> dict:
    """Sérialise la solution en structures Python élémentaires.

    Args:
        resultat: solution structurée.
        scenario: scénario d'origine.
        rapport: rapport de validation, s'il a été produit.

    Returns:
        Un dictionnaire prêt à être écrit en JSON.
    """
    donnees: dict = {
        "scenario": {
            "nom": scenario.nom,
            "alpha_dec_cl": scenario.alpha_dec_cl,
            "tolerance_concentration": scenario.tolerance_concentration,
            "transfert_min": scenario.transfert_min,
            "transfert_max": scenario.transfert_max,
        },
        "objectif": {
            "f1_demande_non_satisfaite": resultat.f1,
            "f2_violations_contraintes_molles": resultat.f2,
            "f3_cout_operatoire": resultat.f3,
            "duree_resolution_s": resultat.duree_s,
        },
        "lignes_29": {nom: asdict(r) for nom, r in resultat.lignes_29.items()},
        "lignes_54": {nom: asdict(r) for nom, r in resultat.lignes_54.items()},
        "stockage_central": {
            "IR11": asdict(resultat.ir11),
            "IR12": asdict(resultat.ir12),
        },
        # Les clés JSON doivent être des chaînes : on aplatit les couples.
        "transferts": {
            f"{origine}->{destination}": quantite
            for (origine, destination), quantite in resultat.transferts.items()
        },
        "besoins": resultat.besoins,
        "livraisons": resultat.livraisons,
        "manques": {
            k: {a: q for a, q in v.items() if q > 1e-6}
            for k, v in resultat.manques.items()
        },
        "violations_bandes": resultat.violations_bandes,
        "ecarts_charge_concentration": resultat.ecarts_charge,
    }

    if rapport is not None:
        donnees["validation"] = {
            "conforme": rapport.conforme,
            "controles_effectues": rapport.controles_effectues,
            "anomalies": [
                {
                    "categorie": a.categorie,
                    "objet": a.objet,
                    "message": a.message,
                    "ecart": a.ecart,
                }
                for a in rapport.anomalies
            ],
            "observations": rapport.observations,
        }

    return donnees


def generer_rapport_json(
    resultat: Resultat,
    scenario: Scenario,
    chemin: Path | str,
    rapport: RapportValidation | None = None,
) -> Path:
    """Écrit les résultats au format JSON.

    Args:
        resultat: solution structurée.
        scenario: scénario d'origine.
        chemin: fichier de sortie (`.json`).
        rapport: rapport de validation à inclure, facultatif.

    Returns:
        Le chemin du fichier écrit.
    """
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(
        json.dumps(
            resultat_en_dictionnaire(resultat, scenario, rapport),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return chemin
