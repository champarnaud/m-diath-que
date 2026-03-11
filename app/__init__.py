"""
Factory de l'application Flask Médiathèque.
"""

import os
from typing import Optional, Dict, Any

from flask import Flask, render_template


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

    # Configuration par défaut
    app.config.from_mapping(
        SECRET_KEY="dev-secret-key",
        DATABASE=os.path.join(app.instance_path, "mediatheque.db"),
        UPLOAD_FOLDER=os.path.join(app.root_path, "static", "uploads"),
    )

    if config_overrides:
        app.config.update(config_overrides)

    # Création des dossiers nécessaires
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Base de données
    from app.models.db import init_app as init_db_app
    init_db_app(app)

    # Blueprints
    from app.routes.supports import bp as supports_bp
    from app.routes.recherche import bp as recherche_bp
    app.register_blueprint(supports_bp)
    app.register_blueprint(recherche_bp)

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
