"""
Tests des modèles de données de la Médiathèque.

Couverture : création, lecture, mise à jour, suppression (CRUD)
des supports audiovisuels et des prêts.
"""

import pytest

from app import create_app
from app.models.db import get_db, init_db


@pytest.fixture
def app():
    """Crée une instance de l'application configurée pour les tests."""
    application = create_app({"TESTING": True, "DATABASE": ":memory:"})
    with application.app_context():
        init_db()
        yield application


@pytest.fixture
def db(app):
    """Retourne une connexion à la base de données de test."""
    yield get_db()


# ---------------------------------------------------------------------------
# Support : création
# ---------------------------------------------------------------------------


class TestSupportCreation:
    """Tests de création d'un support audiovisuel."""

    def test_creer_support_audio(self, db):
        """Un support audio peut être inséré et retrouvé par son titre."""
        from app.models.support import Support

        support = Support(
            titre="Dark Side of the Moon",
            type_support="audio",
            support="CD",
            genre="Rock",
            date_sortie=1973,
            duree=43,
            langue="Anglais",
            interprete="Pink Floyd",
        )
        support_id = support.sauvegarder(db)

        assert support_id is not None
        resultat = Support.trouver_par_id(db, support_id)
        assert resultat.titre == "Dark Side of the Moon"
        assert resultat.interprete == "Pink Floyd"
        assert resultat.type_support == "audio"

    def test_creer_support_video(self, db):
        """Un support vidéo peut être inséré et retrouvé par son titre."""
        from app.models.support import Support

        support = Support(
            titre="Blade Runner",
            type_support="video",
            support="DVD",
            genre="Science-Fiction",
            date_sortie=1982,
            duree=117,
            langue="Anglais",
            realisateur="Ridley Scott",
            acteurs="Harrison Ford, Rutger Hauer",
        )
        support_id = support.sauvegarder(db)

        assert support_id is not None
        resultat = Support.trouver_par_id(db, support_id)
        assert resultat.titre == "Blade Runner"
        assert resultat.realisateur == "Ridley Scott"
        assert resultat.type_support == "video"

    def test_titre_obligatoire(self, db):
        """La création d'un support sans titre lève une ValueError."""
        from app.models.support import Support

        with pytest.raises(ValueError, match="titre"):
            Support(titre="", type_support="audio", support="CD")

    def test_type_support_valide(self, db):
        """Le type de support doit être 'audio' ou 'video'."""
        from app.models.support import Support

        with pytest.raises(ValueError, match="type_support"):
            Support(titre="Test", type_support="inconnu", support="CD")


# ---------------------------------------------------------------------------
# Support : lecture et liste
# ---------------------------------------------------------------------------


class TestSupportLecture:
    """Tests de lecture et de listage des supports."""

    def test_lister_tous_les_supports(self, db):
        """La liste retourne tous les supports enregistrés."""
        from app.models.support import Support

        Support(titre="Album A", type_support="audio", support="CD").sauvegarder(db)
        Support(titre="Film B", type_support="video", support="DVD").sauvegarder(db)

        supports = Support.lister_tous(db)
        assert len(supports) == 2

    def test_lister_par_type_audio(self, db):
        """Le filtre par type ne retourne que les supports audio."""
        from app.models.support import Support

        Support(titre="Album A", type_support="audio", support="CD").sauvegarder(db)
        Support(titre="Film B", type_support="video", support="DVD").sauvegarder(db)

        supports = Support.lister_par_type(db, "audio")
        assert len(supports) == 1
        assert supports[0].titre == "Album A"

    def test_lister_par_type_video(self, db):
        """Le filtre par type ne retourne que les supports vidéo."""
        from app.models.support import Support

        Support(titre="Album A", type_support="audio", support="CD").sauvegarder(db)
        Support(titre="Film B", type_support="video", support="DVD").sauvegarder(db)

        supports = Support.lister_par_type(db, "video")
        assert len(supports) == 1
        assert supports[0].titre == "Film B"

    def test_tri_par_titre(self, db):
        """La liste peut être triée par ordre alphabétique du titre."""
        from app.models.support import Support

        Support(titre="Zorro", type_support="video", support="DVD").sauvegarder(db)
        Support(titre="Alien", type_support="video", support="DVD").sauvegarder(db)

        supports = Support.lister_tous(db, tri="titre")
        assert supports[0].titre == "Alien"
        assert supports[1].titre == "Zorro"


# ---------------------------------------------------------------------------
# Support : recherche
# ---------------------------------------------------------------------------


class TestSupportRecherche:
    """Tests du moteur de recherche."""

    def test_recherche_par_titre(self, db):
        """La recherche trouve un support par son titre (insensible à la casse)."""
        from app.models.support import Support

        Support(titre="Thriller", type_support="audio", support="CD", interprete="Michael Jackson").sauvegarder(db)
        Support(titre="Bad", type_support="audio", support="CD", interprete="Michael Jackson").sauvegarder(db)

        resultats = Support.rechercher(db, "thriller")
        assert len(resultats) == 1
        assert resultats[0].titre == "Thriller"

    def test_recherche_par_interprete(self, db):
        """La recherche trouve les supports d'un interprète."""
        from app.models.support import Support

        Support(titre="Thriller", type_support="audio", support="CD", interprete="Michael Jackson").sauvegarder(db)
        Support(titre="Nevermind", type_support="audio", support="CD", interprete="Nirvana").sauvegarder(db)

        resultats = Support.rechercher(db, "michael jackson")
        assert len(resultats) == 1
        assert resultats[0].interprete == "Michael Jackson"

    def test_recherche_sans_resultat(self, db):
        """Une recherche sans correspondance retourne une liste vide."""
        from app.models.support import Support

        Support(titre="Thriller", type_support="audio", support="CD").sauvegarder(db)

        resultats = Support.rechercher(db, "xyzinexistant")
        assert resultats == []


# ---------------------------------------------------------------------------
# Support : mise à jour et suppression
# ---------------------------------------------------------------------------


class TestSupportModification:
    """Tests de mise à jour et de suppression."""

    def test_mettre_a_jour_un_support(self, db):
        """Les champs d'un support peuvent être modifiés."""
        from app.models.support import Support

        support = Support(titre="Ancien titre", type_support="audio", support="CD")
        support_id = support.sauvegarder(db)

        support_lu = Support.trouver_par_id(db, support_id)
        support_lu.titre = "Nouveau titre"
        support_lu.sauvegarder(db)

        support_maj = Support.trouver_par_id(db, support_id)
        assert support_maj.titre == "Nouveau titre"

    def test_supprimer_un_support(self, db):
        """Un support supprimé n'est plus accessible."""
        from app.models.support import Support

        support_id = Support(
            titre="À supprimer", type_support="audio", support="CD"
        ).sauvegarder(db)

        Support.supprimer(db, support_id)

        assert Support.trouver_par_id(db, support_id) is None


# ---------------------------------------------------------------------------
# Prêts
# ---------------------------------------------------------------------------


class TestPrets:
    """Tests de la gestion des prêts."""

    def test_enregistrer_un_pret(self, db):
        """Un support peut être marqué comme prêté à une personne."""
        from app.models.pret import Pret
        from app.models.support import Support

        support_id = Support(
            titre="Titanic", type_support="video", support="DVD"
        ).sauvegarder(db)

        pret_id = Pret(support_id=support_id, emprunteur="Alice").sauvegarder(db)

        pret = Pret.trouver_par_id(db, pret_id)
        assert pret.emprunteur == "Alice"
        assert pret.date_retour is None  # pas encore rendu

    def test_retourner_un_pret(self, db):
        """Un prêt peut être clôturé en enregistrant une date de retour."""
        from app.models.pret import Pret
        from app.models.support import Support

        support_id = Support(
            titre="Titanic", type_support="video", support="DVD"
        ).sauvegarder(db)
        pret_id = Pret(support_id=support_id, emprunteur="Alice").sauvegarder(db)

        Pret.retourner(db, pret_id)

        pret = Pret.trouver_par_id(db, pret_id)
        assert pret.date_retour is not None

    def test_lister_prets_en_cours(self, db):
        """La liste des prêts en cours n'inclut pas les supports rendus."""
        from app.models.pret import Pret
        from app.models.support import Support

        id1 = Support(titre="Film 1", type_support="video", support="DVD").sauvegarder(db)
        id2 = Support(titre="Film 2", type_support="video", support="DVD").sauvegarder(db)

        pret1_id = Pret(support_id=id1, emprunteur="Alice").sauvegarder(db)
        Pret(support_id=id2, emprunteur="Bob").sauvegarder(db)

        Pret.retourner(db, pret1_id)  # Alice a rendu

        en_cours = Pret.lister_en_cours(db)
        assert len(en_cours) == 1
        assert en_cours[0].emprunteur == "Bob"
