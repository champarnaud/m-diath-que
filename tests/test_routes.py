"""
Tests des routes Flask de la Médiathèque.

Couverture : pages principales, soumission de formulaires,
recherche et gestion des prêts via l'interface web.
"""

import pytest

from app import create_app
from app.models.db import init_db, get_db
from app.models.personne import Personne
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
    """Insère un support audio en base avec une personne associée."""
    db = get_db()
    support = Support(
        titre="Nevermind",
        type_support="audio",
        support="CD",
        genre="Grunge",
        date_sortie=1991,
    )
    support_id = support.sauvegarder(db)
    artiste_id = Personne(nom="Nirvana").sauvegarder(db)
    support.associer_personne(db, artiste_id, "interprete")
    return support_id


@pytest.fixture
def support_video(app):
    """Insère un support vidéo en base avec des personnes associées."""
    db = get_db()
    support = Support(
        titre="Jurassic Park",
        type_support="video",
        support="DVD",
        genre="Aventure",
        date_sortie=1993,
    )
    support_id = support.sauvegarder(db)
    real_id = Personne(nom="Steven Spielberg").sauvegarder(db)
    acteur_id = Personne(nom="Sam Neill").sauvegarder(db)
    support.associer_personne(db, real_id, "realisateur")
    support.associer_personne(db, acteur_id, "acteur")
    return support_id


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
        assert b"Nirvana" in response.data  # personne associée

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
        """La recherche retourne les supports correspondants (par nom de personne)."""
        response = client.get("/recherche?q=Nirvana")
        assert response.status_code == 200
        assert b"Nevermind" in response.data

    def test_recherche_vide_retourne_page(self, client):
        """Une recherche avec un terme vide retourne la page sans erreur."""
        response = client.get("/recherche?q=")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Série : routes
# ---------------------------------------------------------------------------


class TestSupportSerieRoutes:
    """Tests des routes pour la fonctionnalité Série."""

    def test_ajout_support_serie(self, client):
        """La soumission du formulaire crée un support vidéo de type série."""
        response = client.post(
            "/supports/nouveau",
            data={
                "titre": "Breaking Bad",
                "type_support": "video",
                "support": "DVD",
                "est_serie": "on",
                "saisons": "1,2,3",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Breaking Bad" in response.data

    def test_saisons_invalides_rejetees(self, client):
        """Un formulaire avec un numéro de saison > 20 est rejeté."""
        response = client.post(
            "/supports/nouveau",
            data={
                "titre": "Breaking Bad",
                "type_support": "video",
                "support": "DVD",
                "est_serie": "on",
                "saisons": "1,25",
            },
        )
        assert response.status_code == 200
        assert "saison" in response.data.decode("utf-8").lower()

    def test_fiche_detail_affiche_serie(self, client, app):
        """La fiche d'un support série affiche le badge Série et les saisons."""
        from app.models.db import get_db
        from app.models.support import Support

        db = get_db()
        sid = Support(
            titre="The Wire",
            type_support="video",
            support="DVD",
            est_serie=True,
            saisons="1,2,3,4,5",
        ).sauvegarder(db)

        response = client.get(f"/supports/{sid}")
        assert response.status_code == 200
        contenu = response.data.decode("utf-8")
        assert "Série" in contenu
        assert "1, 2, 3, 4, 5" in contenu

    def test_non_serie_pas_de_saisons(self, client):
        """La fiche d'un support non-série n'affiche pas de saisons."""
        response = client.post(
            "/supports/nouveau",
            data={
                "titre": "Inception",
                "type_support": "video",
                "support": "Blu-Ray",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "Saison" not in response.data.decode("utf-8")
