"""
Factory de l'application Flask Médiathèque.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any

from flask import Flask, render_template

from config import Config


def create_app(config_overrides: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Crée et configure l'instance Flask de l'application.

    Args:
        config_overrides: Dictionnaire de valeurs de configuration à surcharger
                          (utile pour les tests).

    Returns:
        Flask: L'instance de l'application configurée.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Chargement de la configuration depuis config.Config
    app.config.from_object(Config)

    # Chemins absolus qui dépendent de l'instance Flask (non calculables
    # dans config.py sans contexte applicatif)
    app.config["DATABASE"] = os.environ.get(
        "DATABASE", os.path.join(app.instance_path, "mediatheque.db")
    )
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path, "static", "uploads"
    )

    if config_overrides:
        app.config.update(config_overrides)

    # Vérification de la clé secrète en production uniquement
    # (FLASK_ENV=production). En développement ou via CLI, la clé par défaut
    # de config.py est utilisée avec un avertissement.
    if os.environ.get("FLASK_ENV") == "production" and not os.environ.get("SECRET_KEY"):
        raise RuntimeError(
            "La variable d'environnement SECRET_KEY doit être définie "
            "avant de lancer l'application en production."
        )
    if not app.config.get("TESTING") and not os.environ.get("SECRET_KEY"):
        import warnings
        warnings.warn(
            "SECRET_KEY non définie : la clé par défaut est utilisée. "
            "Définissez SECRET_KEY en production.",
            stacklevel=2,
        )

    # Création des dossiers nécessaires
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Variable `now` disponible dans tous les templates
    @app.context_processor
    def inject_now():
        return {"now": datetime.now()}

    # Base de données
    from app.models.db import init_app as init_db_app
    init_db_app(app)

    # Blueprints
    from app.routes.supports import bp as supports_bp
    from app.routes.recherche import bp as recherche_bp
    from app.routes.personnes import bp as personnes_bp
    app.register_blueprint(supports_bp)
    app.register_blueprint(recherche_bp)
    app.register_blueprint(personnes_bp)

    # Page d'accueil
    @app.route("/")
    def index():
        """Page d'accueil : redirige vers la liste des supports."""
        return render_template("index.html")

    # Gestionnaires d'erreurs
    @app.errorhandler(404)
    def page_non_trouvee(e):
        return render_template("404.html"), 404

    return app
