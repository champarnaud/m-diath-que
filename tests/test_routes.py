"""
Tests des routes Flask de la Médiathèque.

Couverture : pages principales, soumission de formulaires,
recherche et gestion des prêts via l'interface web.
"""

import pytest

from app import create_app
from app.models.db import init_db, get_db
from app.models.support import Support


@pytest.fixture
def app():
    """Crée une instance de l'application configurée pour les tests."""
    application = create_app({"TESTING": True, "DATABASE": ":memory:"})
    with application.app_context():
        init_db()
        yield application


@pytest.fixture
def client(app):
    """Retourne un client de test Flask."""
    return app.test_client()


@pytest.fixture
def support_audio(app):
    """Insère un support audio en base et retourne son id."""
    db = get_db()
    return Support(
        titre="Nevermind",
        type_support="audio",
        support="CD",
        genre="Grunge",
        date_sortie=1991,
        interprete="Nirvana",
    ).sauvegarder(db)


@pytest.fixture
def support_video(app):
    """Insère un support vidéo en base et retourne son id."""
    db = get_db()
    return Support(
        titre="Jurassic Park",
        type_support="video",
        support="DVD",
        genre="Aventure",
        date_sortie=1993,
        realisateur="Steven Spielberg",
        acteurs="Sam Neill, Laura Dern",
    ).sauvegarder(db)


# ---------------------------------------------------------------------------
# Page d'accueil
# ---------------------------------------------------------------------------


class TestPageAccueil:
    """Tests de la page d'accueil."""

    def test_accueil_retourne_200(self, client):
        """La page d'accueil est accessible."""
        response = client.get("/")
        assert response.status_code == 200

    def test_accueil_affiche_titre(self, client):
        """La page d'accueil affiche le titre de l'application."""
        response = client.get("/")
        assert b"M\xc3\xa9diath\xc3\xa8que" in response.data


# ---------------------------------------------------------------------------
# Liste des supports
# ---------------------------------------------------------------------------


class TestListeSupports:
    """Tests des pages de liste."""

    def test_liste_affiche_supports(self, client, support_audio, support_video):
        """La page de liste affiche tous les supports."""
        response = client.get("/supports/")
        assert response.status_code == 200
        assert b"Nevermind" in response.data
        assert b"Jurassic Park" in response.data

    def test_liste_filtre_audio(self, client, support_audio, support_video):
        """Le filtre 'audio' n'affiche que les supports audio."""
        response = client.get("/supports/?type=audio")
        assert response.status_code == 200
        assert b"Nevermind" in response.data
        assert b"Jurassic Park" not in response.data

    def test_liste_filtre_video(self, client, support_audio, support_video):
        """Le filtre 'video' n'affiche que les supports vidéo."""
        response = client.get("/supports/?type=video")
        assert response.status_code == 200
        assert b"Jurassic Park" in response.data
        assert b"Nevermind" not in response.data


# ---------------------------------------------------------------------------
# Fiche détail
# ---------------------------------------------------------------------------


class TestFicheDetail:
    """Tests de la page de détail d'un support."""

    def test_fiche_retourne_200(self, client, support_audio):
        """La fiche d'un support existant est accessible."""
        response = client.get(f"/supports/{support_audio}")
        assert response.status_code == 200

    def test_fiche_affiche_informations(self, client, support_audio):
        """La fiche affiche les informations du support."""
        response = client.get(f"/supports/{support_audio}")
        assert b"Nevermind" in response.data
        assert b"Nirvana" in response.data

    def test_fiche_inexistante_retourne_404(self, client):
        """Une fiche vers un identifiant inexistant retourne 404."""
        response = client.get("/supports/99999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Ajout d'un support
# ---------------------------------------------------------------------------


class TestAjoutSupport:
    """Tests du formulaire d'ajout."""

    def test_formulaire_ajout_accessible(self, client):
        """La page d'ajout est accessible (GET)."""
        response = client.get("/supports/nouveau")
        assert response.status_code == 200

    def test_ajout_support_audio(self, client):
        """La soumission du formulaire crée un nouveau support audio."""
        response = client.post(
            "/supports/nouveau",
            data={
                "titre": "OK Computer",
                "type_support": "audio",
                "support": "CD",
                "genre": "Rock",
                "date_sortie": "1997",
                "interprete": "Radiohead",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"OK Computer" in response.data

    def test_ajout_sans_titre_rejete(self, client):
        """Un formulaire soumis sans titre est rejeté avec une erreur."""
        response = client.post(
            "/supports/nouveau",
            data={"titre": "", "type_support": "audio", "support": "CD"},
        )
        assert response.status_code == 200  # re-affichage du formulaire
        assert b"titre" in response.data.lower()


# ---------------------------------------------------------------------------
# Recherche
# ---------------------------------------------------------------------------


class TestRecherche:
    """Tests du moteur de recherche."""

    def test_recherche_retourne_resultats(self, client, support_audio):
        """La recherche retourne les supports correspondants."""
        response = client.get("/recherche?q=Nirvana")
        assert response.status_code == 200
        assert b"Nevermind" in response.data

    def test_recherche_vide_retourne_page(self, client):
        """Une recherche avec un terme vide retourne la page sans erreur."""
        response = client.get("/recherche?q=")
        assert response.status_code == 200
