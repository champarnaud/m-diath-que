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


@click.command("migrate")
def migrate_command() -> None:
    """
    Applique les migrations SQL de façon idempotente.

    Vérifie l'existence de chaque colonne via PRAGMA table_info avant
    d'exécuter l'ALTER TABLE correspondant. Aucune donnée n'est effacée.
    """
    db = get_db()
    colonnes_support = [
        row[1]
        for row in db.execute("PRAGMA table_info(support)").fetchall()
    ]

    # --- Migration 001 : champs série ---
    ajouts = 0
    if "est_serie" not in colonnes_support:
        db.execute(
            "ALTER TABLE support ADD COLUMN est_serie INTEGER NOT NULL DEFAULT 0"
        )
        db.commit()
        click.echo("  + Colonne 'est_serie' ajoutée.")
        ajouts += 1
    else:
        click.echo("  ✓ Colonne 'est_serie' déjà présente.")

    if "saisons" not in colonnes_support:
        db.execute("ALTER TABLE support ADD COLUMN saisons TEXT")
        db.commit()
        click.echo("  + Colonne 'saisons' ajoutée.")
        ajouts += 1
    else:
        click.echo("  ✓ Colonne 'saisons' déjà présente.")

    if ajouts:
        click.echo(f"Migration terminée : {ajouts} colonne(s) ajoutée(s).")
    else:
        click.echo("Base de données déjà à jour.")


def init_app(app: Flask) -> None:
    """
    Enregistre les fonctions de gestion de la base dans l'application Flask.

    Args:
        app: L'instance Flask de l'application.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(migrate_command)
