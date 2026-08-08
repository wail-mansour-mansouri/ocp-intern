"""Tests du validateur indépendant.

Deux volets :
  - la solution du scénario réel passe tous les contrôles ;
  - le validateur **détecte** effectivement une solution corrompue. Sans ce
    second volet, un validateur qui dirait toujours « conforme » passerait le
    premier sans rien garantir.
"""

from __future__ import annotations

import copy
import dataclasses

import pytest

from ocp_optim import constants as C
from ocp_optim.validation import valider


# ─────────────────────────────────────────────────────────────────────────────
# La solution de référence est conforme
# ─────────────────────────────────────────────────────────────────────────────

def test_solution_reelle_conforme(resultat, scenario):
    rapport = valider(resultat, scenario)
    assert rapport.conforme, rapport.resume()


def test_nombre_de_controles_significatif(resultat, scenario):
    """Un validateur qui ne contrôlerait presque rien serait sans valeur."""
    rapport = valider(resultat, scenario)
    assert rapport.controles_effectues >= 80


def test_les_19_noeuds_sont_controles(resultat, scenario):
    """6 stocks 29 std + 6 stocks 29 dec + 5 stocks 54 NCL + IR11 + IR12."""
    assert len(resultat.lignes_29) == 6
    assert len(resultat.lignes_54) == 5
    rapport = valider(resultat, scenario)
    assert rapport.conforme


def test_violations_structurelles_signalees_en_observation(resultat, scenario):
    """Les dépassements de bande sont des observations, pas des anomalies.

    Ce sont des contraintes molles assumées : le modèle doit toujours rendre un
    plan exploitable, en quantifiant le problème plutôt qu'en refusant de répondre.
    """
    rapport = valider(resultat, scenario)
    assert rapport.conforme
    assert any("IR11" in o for o in rapport.observations)


# ─────────────────────────────────────────────────────────────────────────────
# Le validateur détecte les corruptions
# ─────────────────────────────────────────────────────────────────────────────

def test_detecte_un_bilan_29_std_faux(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.lignes_29["13AB"].stock_final_std += 500.0
    rapport = valider(corrompu, scenario)
    assert not rapport.conforme
    assert any(a.categorie == "bilan_29_std" for a in rapport.anomalies)


def test_detecte_un_bilan_29_dec_faux(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.lignes_29["13XY"].stock_final_dec -= 100.0
    rapport = valider(corrompu, scenario)
    assert any(a.categorie == "bilan_29_dec" for a in rapport.anomalies)


def test_detecte_un_bilan_54_faux(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.lignes_54["14CD"].stock_final_ncl += 42.0
    rapport = valider(corrompu, scenario)
    assert any(a.categorie == "bilan_54_ncl" for a in rapport.anomalies)


def test_detecte_un_bilan_central_faux(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.ir11.stock_final += 300.0
    rapport = valider(corrompu, scenario)
    assert any(a.categorie == "bilan_central" for a in rapport.anomalies)


def test_detecte_une_demande_non_servie(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.livraisons["IMACID"]["acid_29_std"] -= 50.0
    rapport = valider(corrompu, scenario)
    assert any(a.categorie == "demande" for a in rapport.anomalies)


def test_detecte_un_depassement_de_decanteurs(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.lignes_54["14ZU"].clarification_ncl = 1200.0
    rapport = valider(corrompu, scenario)
    assert any(a.categorie == "capacite_decanteurs" for a in rapport.anomalies)


def test_detecte_un_niveau_de_decadmiation_invalide(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.lignes_29["13XY"].decadmiation = 312.0
    rapport = valider(corrompu, scenario)
    assert any(a.categorie == "decadmiation" for a in rapport.anomalies)


def test_detecte_un_stock_negatif(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.lignes_29["13E"].stock_final_std = -10.0
    rapport = valider(corrompu, scenario)
    assert any(a.categorie == "stock_negatif" for a in rapport.anomalies)


def test_detecte_un_transfert_sous_le_minimum(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    arc = next(iter(corrompu.transferts))
    corrompu.transferts[arc] = 4.0
    rapport = valider(corrompu, scenario)
    assert any(a.categorie == "transfert" for a in rapport.anomalies)


def test_detecte_un_transfert_sur_liaison_inexistante(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.transferts[("13E", "13F")] = 500.0
    rapport = valider(corrompu, scenario)
    assert any("inexistante" in a.message for a in rapport.anomalies)


def test_detecte_un_rendement_de_cocristallisation_faux(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.lignes_54["14EXT"].coc_produit *= 1.5
    rapport = valider(corrompu, scenario)
    assert any(a.categorie == "rendement_coc" for a in rapport.anomalies)


def test_detecte_une_decadmiation_superieure_a_la_production(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.lignes_29["13ZU"].decadmiation = 1500.0   # produit 800 t seulement
    rapport = valider(corrompu, scenario)
    assert any("production" in a.message for a in rapport.anomalies)


def test_detecte_une_clarification_sur_ligne_non_habilitee(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.lignes_54["14EXT"].clarification_ncl = 300.0
    rapport = valider(corrompu, scenario)
    assert any("non habilitée" in a.message for a in rapport.anomalies)


# ─────────────────────────────────────────────────────────────────────────────
# Rapport
# ─────────────────────────────────────────────────────────────────────────────

def test_resume_lisible_quand_conforme(resultat, scenario):
    rapport = valider(resultat, scenario)
    assert "CONFORME" in rapport.resume()


def test_resume_lisible_quand_non_conforme(resultat, scenario):
    corrompu = copy.deepcopy(resultat)
    corrompu.ir12.stock_final += 1000.0
    rapport = valider(corrompu, scenario)
    texte = rapport.resume()
    assert "NON CONFORME" in texte
    assert "IR12" in texte
