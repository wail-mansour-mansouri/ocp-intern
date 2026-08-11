"""Tests de cohérence structurelle des constantes du système."""

from __future__ import annotations

from ocp_optim import constants as C


def test_sigma_est_une_bijection_hors_13f():
    """sigma restreinte aux lignes disposant d'une concentration est bijective."""
    images = [v for v in C.SIGMA.values() if v is not None]
    assert len(images) == len(set(images)), "deux lignes 29 partageraient une ligne 54"
    assert set(images) == set(C.LIGNES_54)
    assert C.SIGMA["13F"] is None
    assert "13F" not in C.LIGNES_29_AVEC_54


def test_sigma_inverse_coherente():
    for ligne54, ligne29 in C.SIGMA_INV.items():
        assert C.SIGMA[ligne29] == ligne54


def test_echelons_forment_une_partition():
    """Chaque échelon appartient à exactement une ligne, et toutes sont couvertes."""
    tous = [e for groupe in C.GROUPES_ECHELONS.values() for e in groupe]
    assert len(tous) == len(set(tous)), "un échelon appartiendrait à deux lignes"
    assert set(tous) == set(C.CAPACITE_ECHELON), "échelon sans capacité ou capacité orpheline"
    assert set(C.GROUPES_ECHELONS) == set(C.LIGNES_54)


def test_matrice_interzone_anti_reflexive():
    """Une ligne ne se transfère pas de l'acide à elle-même."""
    for origine, destinations in C.INTERZONE_ZONES.items():
        assert origine not in destinations


def test_matrice_interzone_non_symetrique():
    """La relation est orientée : certaines conduites sont à sens unique.

    Exemple documenté : CD -> E est autorisé alors que E -> ... ne revient pas
    vers F. On vérifie qu'au moins un couple asymétrique existe, sans quoi la
    modélisation orientée serait inutile.
    """
    asymetriques = [
        (o, d)
        for o, dests in C.INTERZONE_ZONES.items()
        for d in dests
        if o not in C.INTERZONE_ZONES.get(d, ())
    ]
    assert asymetriques, "la matrice serait symétrique, contrairement au dossier"


def test_arcs_interzone_bien_formes():
    arcs = C.arcs_interzone()
    assert len(arcs) == 14
    assert len(set(arcs)) == len(arcs)
    for origine, destination in arcs:
        assert origine in C.LIGNES_29
        assert destination in C.LIGNES_29
        assert origine != destination


def test_zones_en_bijection_avec_les_lignes():
    assert set(C.LIGNE_VERS_ZONE) == set(C.LIGNES_29)
    assert len(set(C.LIGNE_VERS_ZONE.values())) == len(C.LIGNES_29)
    assert set(C.INTERZONE_ZONES) == set(C.ZONE_VERS_LIGNE)


def test_partition_des_types_d_acide():
    """Acides locaux et centraux forment une partition des six types."""
    assert not set(C.ACIDES_LOCAUX) & set(C.ACIDES_CENTRAUX)
    assert len(C.ACIDES_LOCAUX) + len(C.ACIDES_CENTRAUX) == 6


def test_rendements_et_boues_se_completent():
    """Rien ne se perd : le complément du rendement part en boue."""
    assert C.RENDEMENT_CLARIFICATION + C.BOUE_CLARIFICATION == 1.0
    assert C.RENDEMENT_COCRISTALLISATION + C.BOUE_COCRISTALLISATION == 1.0
    assert C.RENDEMENT_CONCENTRATION == 1.0, "le P2O5 est conservé par la concentration"


def test_retours_emaphos_somment_a_40_pourcent():
    assert sum(C.RETOURS_EMAPHOS.values()) == 0.40
    for ligne in C.RETOURS_EMAPHOS:
        assert ligne in C.LIGNES_29


def test_niveaux_decadmiation_multiples_du_filtre():
    """Les niveaux correspondent à 0, 1 ou 2 filtres de 750 t."""
    assert C.NIVEAUX_DECADMIATION == (0.0, 750.0, 1500.0)


def test_capacite_decanteurs():
    assert C.CAPACITE_DECANTEURS_PAR_LIGNE == 1000.0


def test_connexions_referencent_des_lignes_existantes():
    for consommateur, lignes in C.CONNEXIONS_29.items():
        assert consommateur in C.CONSOMMATEURS
        assert set(lignes) <= set(C.LIGNES_29)
    for consommateur, lignes in C.CONNEXIONS_54.items():
        assert consommateur in C.CONSOMMATEURS
        assert set(lignes) <= set(C.LIGNES_54)


def test_cocristallisation_limitee_aux_lignes_equipees():
    assert set(C.LIGNES_COC_POSSIBLE) <= set(C.LIGNES_54)
    assert set(C.LIGNES_COC_POSSIBLE) == {"14EXT", "14AB"}
