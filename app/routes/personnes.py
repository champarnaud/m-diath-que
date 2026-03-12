"""
Routes CRUD pour les personnes et les activités.
"""

from typing import Union

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug import Response

from app.models.db import get_db
from app.models.personne import Activite, Personne

bp = Blueprint("personnes", __name__, url_prefix="/personnes")


# ===========================================================================
# Personnes
# ===========================================================================


@bp.route("/")
def liste() -> str:
    """Affiche la liste de toutes les personnes."""
    db = get_db()
    personnes = Personne.lister_toutes(db)
    for p in personnes:
        p.charger_activites(db)
    return render_template("personnes/liste.html", personnes=personnes)


@bp.route("/<int:personne_id>")
def detail(personne_id: int) -> str:
    """Affiche la fiche détaillée d'une personne."""
    db = get_db()
    personne = Personne.trouver_par_id(db, personne_id)
    if personne is None:
        abort(404)

    # Supports liés à cette personne
    rows = db.execute(
        """
        SELECT s.id, s.titre, s.type_support, s.support, sp.role
        FROM support s
        JOIN support_personne sp ON sp.support_id = s.id
        WHERE sp.personne_id = ?
        ORDER BY s.titre COLLATE NOCASE
        """,
        (personne_id,),
    ).fetchall()
    supports_lies = [dict(r) for r in rows]

    return render_template(
        "personnes/detail.html",
        personne=personne,
        supports_lies=supports_lies,
    )


@bp.route("/nouveau", methods=["GET", "POST"])
def nouvelle() -> Union[str, Response]:
    """Affiche et traite le formulaire d'ajout d'une personne."""
    db = get_db()
    activites_dispo = Activite.lister_toutes(db)

    if request.method == "POST":
        erreur = _traiter_formulaire_personne(personne_id=None)
        if erreur:
            flash(erreur, "danger")
            return render_template(
                "personnes/formulaire.html",
                personne=None,
                activites_dispo=activites_dispo,
            )
        flash("Personne ajoutée avec succès.", "success")
        return redirect(url_for("personnes.liste"))

    return render_template(
        "personnes/formulaire.html",
        personne=None,
        activites_dispo=activites_dispo,
    )


@bp.route("/<int:personne_id>/modifier", methods=["GET", "POST"])
def modifier(personne_id: int) -> Union[str, Response]:
    """Affiche et traite le formulaire de modification d'une personne."""
    db = get_db()
    personne = Personne.trouver_par_id(db, personne_id)
    if personne is None:
        abort(404)
    activites_dispo = Activite.lister_toutes(db)

    if request.method == "POST":
        erreur = _traiter_formulaire_personne(personne_id=personne_id)
        if erreur:
            flash(erreur, "danger")
            return render_template(
                "personnes/formulaire.html",
                personne=personne,
                activites_dispo=activites_dispo,
            )
        flash("Personne modifiée avec succès.", "success")
        return redirect(
            url_for("personnes.detail", personne_id=personne_id)
        )

    return render_template(
        "personnes/formulaire.html",
        personne=personne,
        activites_dispo=activites_dispo,
    )


@bp.route("/<int:personne_id>/supprimer", methods=["POST"])
def supprimer(personne_id: int) -> Response:
    """Supprime une personne et redirige vers la liste."""
    db = get_db()
    if Personne.trouver_par_id(db, personne_id) is None:
        abort(404)
    Personne.supprimer(db, personne_id)
    flash("Personne supprimée.", "info")
    return redirect(url_for("personnes.liste"))


# ===========================================================================
# Activités
# ===========================================================================


@bp.route("/activites")
def liste_activites() -> str:
    """Affiche la liste de toutes les activités."""
    db = get_db()
    activites = Activite.lister_toutes(db)
    return render_template("personnes/activites.html", activites=activites)


@bp.route("/activites/nouvelle", methods=["GET", "POST"])
def nouvelle_activite() -> Union[str, Response]:
    """Affiche et traite le formulaire d'ajout d'une activité."""
    if request.method == "POST":
        libelle = request.form.get("libelle", "").strip()
        if not libelle:
            flash("Le libellé est obligatoire.", "danger")
            return render_template("personnes/activite_formulaire.html")
        try:
            db = get_db()
            Activite(libelle=libelle).sauvegarder(db)
            flash(f"Activité « {libelle} » ajoutée.", "success")
            return redirect(url_for("personnes.liste_activites"))
        except Exception as exc:
            flash(str(exc), "danger")
            return render_template("personnes/activite_formulaire.html")

    return render_template("personnes/activite_formulaire.html")


@bp.route("/activites/<int:activite_id>/supprimer", methods=["POST"])
def supprimer_activite(activite_id: int) -> Response:
    """Supprime une activité et redirige vers la liste des activités."""
    db = get_db()
    if Activite.trouver_par_id(db, activite_id) is None:
        abort(404)
    Activite.supprimer(db, activite_id)
    flash("Activité supprimée.", "info")
    return redirect(url_for("personnes.liste_activites"))


# ===========================================================================
# Helpers
# ===========================================================================


def _traiter_formulaire_personne(
    personne_id: Union[int, None],
) -> Union[str, None]:
    """
    Lit les données du formulaire POST, valide et sauvegarde la personne.

    Args:
        personne_id: Identifiant existant pour une modification,
                     None pour un ajout.

    Returns:
        str avec message d'erreur, ou None si succès.
    """
    db = get_db()
    nom = request.form.get("nom", "").strip()
    date_naissance = request.form.get("date_naissance", "").strip() or None
    date_deces = request.form.get("date_deces", "").strip() or None
    activite_ids = request.form.getlist("activite_ids")

    try:
        personne = Personne(
            id=personne_id,
            nom=nom,
            date_naissance=date_naissance,
            date_deces=date_deces,
        )
    except ValueError as exc:
        return str(exc)

    personne.sauvegarder(db)

    # Réinitialise les activités et ré-associe celles cochées
    db.execute(
        "DELETE FROM personne_activite WHERE personne_id = ?",
        (personne.id,),
    )
    db.commit()
    for aid in activite_ids:
        try:
            personne.ajouter_activite(db, int(aid))
        except (ValueError, TypeError):
            pass

    return None
