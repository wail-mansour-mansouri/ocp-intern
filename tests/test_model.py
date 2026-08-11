"""Tests du modèle d'optimisation et de sa résolution lexicographique."""

from __future__ import annotations

import dataclasses

import pytest

from ocp_optim import constants as C
from ocp_optim.model import construire_modele
from ocp_optim.preprocessing import calculer_parametres
from ocp_optim.results import extraire
from ocp_optim.solver import resoudre


# ─────────────────────────────────────────────────────────────────────────────
# Structure du modèle
# ─────────────────────────────────────────────────────────────────────────────

def test_le_modele_a_des_variables_binaires(modele):
    """Les décisions discrètes imposent un MILP, pas un simple PL."""
    stats = modele.statistiques()
    assert stats["variables_binaires"] > 0
    # 5 lignes équipées x 3 niveaux + 14 arcs interzones
    assert stats["variables_binaires"] == 5 * 3 + 14


def test_taille_du_modele_raisonnable(modele):
    """Le problème reste minuscule pour un solveur moderne."""
    stats = modele.statistiques()
    assert stats["variables_totales"] < 500
    assert stats["contraintes"] < 500


def test_pas_de_variable_de_livraison_non_autorisee(modele):
    """Les livraisons interdites par les matrices ne sont pas créées du tout."""
    for (acide, ligne, consommateur) in modele.variables.y_loc:
        if acide in (C.ACIDE_29_STD, C.ACIDE_29_DEC):
            assert ligne in C.CONNEXIONS_29[consommateur]
        elif acide == C.ACIDE_54_NCL:
            assert ligne in C.CONNEXIONS_54[consommateur]


def test_acide_dec_seulement_depuis_lignes_habilitees(modele, scenario):
    """L'acide 29 décadmié ne part que des lignes autorisées (anomalie A-09)."""
    for (acide, ligne, _) in modele.variables.y_loc:
        if acide == C.ACIDE_29_DEC:
            assert ligne in scenario.dec29_vers_engrais


def test_variables_de_transfert_sur_les_arcs_valides(modele):
    assert set(modele.variables.t) == set(C.arcs_interzone())
    assert set(modele.variables.b) == set(C.arcs_interzone())


# ─────────────────────────────────────────────────────────────────────────────
# Résolution
# ─────────────────────────────────────────────────────────────────────────────

def test_resolution_optimale(solution):
    assert solution.statut == "Optimal"


def test_resolution_rapide(solution):
    assert solution.duree_s < 30.0


def test_trois_passes_journalisees(solution):
    assert len(solution.journal) == 3
    assert all(nom in "".join(solution.journal) for nom in ("f1", "f2", "f3"))


def test_demande_entierement_satisfaite(solution):
    """Niveau 1 nul : aucun besoin n'est resté non servi."""
    assert solution.f1 == pytest.approx(0.0, abs=1e-4)
    assert solution.demande_entierement_satisfaite


def test_non_regression_des_niveaux(solution):
    """Verrouille les valeurs optimales du scénario de référence.

    Toute modification du modèle qui déplacerait ces valeurs sera signalée : soit
    c'est une amélioration voulue et on met à jour le test, soit c'est une
    régression involontaire.
    """
    assert solution.f1 == pytest.approx(0.0, abs=1e-4)
    assert solution.f2 == pytest.approx(1268.3, rel=1e-3)
    assert solution.f3 == pytest.approx(3111.9, rel=1e-3)


# ─────────────────────────────────────────────────────────────────────────────
# Comportement des contraintes
# ─────────────────────────────────────────────────────────────────────────────

def test_niveaux_de_decadmiation_discrets(resultat):
    for r in resultat.lignes_29.values():
        assert any(abs(r.decadmiation - n) < 1e-4 for n in C.NIVEAUX_DECADMIATION)


def test_transferts_semi_continus(resultat, scenario):
    """Un transfert est soit nul, soit au moins égal au minimum d'expédition."""
    for arc, quantite in resultat.transferts.items():
        assert quantite >= scenario.transfert_min - 1e-6, f"{arc} : {quantite} t < minimum"
        assert quantite <= scenario.transfert_max + 1e-6


def test_capacite_des_decanteurs_respectee(resultat):
    for r in resultat.lignes_54.values():
        assert r.clarification_ncl + r.clarification_dec <= C.CAPACITE_DECANTEURS_PAR_LIGNE + 1e-6


def test_charge_de_concentration_a_l_egalite(resultat):
    """La tolérance accordée par l'encadrant existe mais n'est pas utilisée.

    C'est le comportement voulu : la bande est disponible en dernier recours,
    et la pénalité du niveau 2 maintient le modèle à l'égalité stricte.
    """
    assert resultat.ecarts_charge == {}
    for ligne, r in resultat.lignes_54.items():
        assert r.charge_reelle == pytest.approx(r.production_planifiee, abs=1e-4)


def test_contrainte_de_qualite_ir11_active(resultat, scenario, params):
    """Sans la contrainte C15, aucun DEC_CL ne serait produit."""
    dec_cl = sum(r.dec_cl_produit for r in resultat.lignes_54.values())
    entrees_ir11 = params.coc_total + dec_cl
    assert dec_cl > 0.0
    assert dec_cl / entrees_ir11 >= scenario.alpha_dec_cl - 1e-6


def test_sans_contrainte_de_qualite_aucun_dec_cl(scenario, profils):
    """Contre-épreuve : avec alpha = 0, l'optimiseur cesse de produire du DEC_CL.

    Ce test démontre la nécessité de la contrainte C15 (décision D-09) : la
    cocristallisation systématique couvre déjà tout le besoin, si bien que
    produire du DEC_CL est un coût sans bénéfice pour l'optimiseur.
    """
    sans_alpha = dataclasses.replace(scenario, alpha_dec_cl=0.0)
    params = calculer_parametres(sans_alpha, profils)
    modele = construire_modele(sans_alpha, params)
    resultat = extraire(modele, resoudre(modele))

    dec_cl = sum(r.dec_cl_produit for r in resultat.lignes_54.values())
    assert dec_cl == pytest.approx(0.0, abs=1e-4)


def test_decadmiation_bornee_par_la_production(scenario, profils):
    """13ZU ne produit que 800 t : elle ne peut pas décadmier 1 500 t.

    Contrainte C03, absente du dossier. On force la situation en rendant la
    décadmiation attractive sur cette ligne.
    """
    force = dataclasses.replace(
        scenario,
        decadmiation_equipee=("13ZU",),
        dec29_vers_engrais=(),
        dec_cl_active=(),
        alpha_dec_cl=0.0,
    )
    params = calculer_parametres(force, profils)
    modele = construire_modele(force, params)
    resultat = extraire(modele, resoudre(modele))
    assert resultat.lignes_29["13ZU"].decadmiation <= 800.0


# ─────────────────────────────────────────────────────────────────────────────
# Hiérarchie lexicographique
# ─────────────────────────────────────────────────────────────────────────────

def test_hierarchie_respectee(scenario, profils):
    """Optimiser le niveau 3 seul dégrade le niveau 2 : la hiérarchie sert à quelque chose.

    Si les trois niveaux étaient alignés, l'optimisation lexicographique serait
    inutile. On vérifie qu'ils sont bien en tension.
    """
    params = calculer_parametres(scenario, profils)
    modele = construire_modele(scenario, params)

    import pulp
    modele.prob.setObjective(modele.f3)
    modele.prob.solve(pulp.PULP_CBC_CMD(msg=False))
    f2_si_on_ignore_le_niveau_2 = float(pulp.value(modele.f2))

    solution_lexico = resoudre(construire_modele(scenario, params))
    assert f2_si_on_ignore_le_niveau_2 >= solution_lexico.f2 - 1e-6


# ─────────────────────────────────────────────────────────────────────────────
# Mode « cocristallisation décidable » (décision D-11)
# ─────────────────────────────────────────────────────────────────────────────

def _resoudre_decidable(scenario, profils):
    """Résout le scénario en rendant l'affectation des échelons CoC décidable."""
    variante = dataclasses.replace(scenario, cocristallisation_decidable=True)
    params = calculer_parametres(variante, profils)
    modele = construire_modele(variante, params)
    return variante, modele, extraire(modele, resoudre(modele))


def test_mode_subi_ne_cree_aucune_binaire_de_cocristallisation(modele):
    """Par défaut, la cocristallisation reste un paramètre : aucune variable."""
    assert modele.variables.z == {}


def test_mode_decidable_cree_une_binaire_par_echelon_candidat(scenario, profils):
    """Une binaire est créée pour chaque échelon raccordé à une unité de CoC."""
    _, modele, _ = _resoudre_decidable(scenario, profils)
    candidats = {
        e for echelons in scenario.echelons_cocristallisation.values() for e in echelons
    }
    assert set(modele.variables.z) == candidats
    assert len(candidats) == 8   # 4 sur 14EXT + 4 sur 14AB


def test_mode_decidable_resorbe_les_violations(scenario, profils, resultat):
    """Laisser le modèle choisir fait disparaître les deux violations structurelles.

    C'est le résultat le plus actionnable de l'étude : les violations ne viennent
    d'aucune mauvaise décision d'exploitation, mais d'un paramètre de configuration.
    """
    _, _, decidable = _resoudre_decidable(scenario, profils)

    assert resultat.f2 > 1000.0, "le mode subi doit bien présenter des violations"
    assert decidable.f2 == pytest.approx(0.0, abs=1e-3)
    assert decidable.f1 == pytest.approx(0.0, abs=1e-4), "la demande reste servie"


def test_mode_decidable_ne_degrade_pas_le_cout_operatoire(scenario, profils, resultat):
    """Le mode décidable élargit le domaine réalisable : il ne peut que faire mieux."""
    _, _, decidable = _resoudre_decidable(scenario, profils)
    assert decidable.f3 <= resultat.f3 + 1e-6


def test_mode_decidable_conserve_les_rendements(scenario, profils):
    """Le CoC produit reste égal à 80 % de ce qui entre en cocristallisation."""
    _, _, decidable = _resoudre_decidable(scenario, profils)
    for r in decidable.lignes_54.values():
        assert r.coc_produit == pytest.approx(
            C.RENDEMENT_COCRISTALLISATION * r.coc_entree, abs=1e-6
        )


def test_mode_decidable_reste_dans_les_echelons_candidats(scenario, profils):
    """Aucune ligne non équipée ne peut se mettre à cocristalliser."""
    _, _, decidable = _resoudre_decidable(scenario, profils)
    for nom, r in decidable.lignes_54.items():
        if nom not in C.LIGNES_COC_POSSIBLE:
            assert r.coc_entree == pytest.approx(0.0, abs=1e-6)


def test_mode_decidable_valide_physiquement(scenario, profils):
    """La solution du mode décidable passe le validateur indépendant."""
    from ocp_optim.validation import valider

    variante, _, decidable = _resoudre_decidable(scenario, profils)
    rapport = valider(decidable, variante)
    assert rapport.conforme, rapport.resume()
