"""
Gestion de la connexion SQLite et initialisation du schéma.
"""

import sqlite3
from typing import Optional

import click
from flask import Flask, current_app, g


def get_db() -> sqlite3.Connection:
    """
    Retourne la connexion SQLite active pour la requête en cours.

    La connexion est stockée dans le contexte applicatif Flask (g)
    afin d'être réutilisée au sein d'une même requête.

    Returns:
        sqlite3.Connection: Connexion à la base de données configurée.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception: Optional[BaseException] = None) -> None:
    """
    Ferme la connexion SQLite à la fin de la requête.

    Args:
        exception: Exception éventuelle survenue pendant la requête.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Initialise la base de données en exécutant le schéma SQL."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


@click.command("init-db")
def init_db_command() -> None:
    """Commande CLI Flask pour (ré)initialiser la base de données."""
    init_db()
    click.echo("Base de données initialisée.")


def init_app(app: Flask) -> None:
    """
    Enregistre les fonctions de gestion de la base dans l'application Flask.

    Args:
        app: L'instance Flask de l'application.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
