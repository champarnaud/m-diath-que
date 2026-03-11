"""
Routes principales : liste, détail, ajout, modification, suppression.
"""

import os
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
from werkzeug.utils import secure_filename
from werkzeug import Response

from app.models.db import get_db
from app.models.support import Support

bp = Blueprint("supports", __name__, url_prefix="/supports")

EXTENSIONS_AUTORISEES = {"png", "jpg", "jpeg", "gif", "webp"}


def _extension_autorisee(nom_fichier: str) -> bool:
    """Vérifie que l'extension du fichier est dans la liste autorisée."""
    return (
        "." in nom_fichier
        and nom_fichier.rsplit(".", 1)[1].lower() in EXTENSIONS_AUTORISEES
    )


@bp.route("/")
def liste() -> str:
    """Affiche la liste de tous les supports, avec filtre et tri optionnels."""
    db = get_db()
    type_filtre = request.args.get("type", "")
    tri = request.args.get("tri", "titre")

    if type_filtre in ("audio", "video"):
        supports = Support.lister_par_type(db, type_filtre, tri=tri)
    else:
        supports = Support.lister_tous(db, tri=tri)

    return render_template(
        "supports/liste.html",
        supports=supports,
        type_filtre=type_filtre,
        tri=tri,
    )


@bp.route("/<int:support_id>")
def detail(support_id: int) -> str:
    """Affiche la fiche détaillée d'un support."""
    db = get_db()
    support = Support.trouver_par_id(db, support_id)
    if support is None:
        abort(404)
    return render_template("supports/detail.html", support=support)


@bp.route("/nouveau", methods=["GET", "POST"])
def nouveau() -> Union[str, Response]:
    """Affiche et traite le formulaire d'ajout d'un support."""
    if request.method == "POST":
        erreur = _traiter_formulaire(support_id=None)
        if erreur:
            flash(erreur, "danger")
            return render_template("supports/formulaire.html", support=None)
        flash("Support ajouté avec succès.", "success")
        return redirect(url_for("supports.liste"))

    return render_template("supports/formulaire.html", support=None)


@bp.route("/<int:support_id>/modifier", methods=["GET", "POST"])
def modifier(support_id: int) -> Union[str, Response]:
    """Affiche et traite le formulaire de modification d'un support."""
    db = get_db()
    support = Support.trouver_par_id(db, support_id)
    if support is None:
        abort(404)

    if request.method == "POST":
        erreur = _traiter_formulaire(support_id=support_id)
        if erreur:
            flash(erreur, "danger")
            return render_template("supports/formulaire.html", support=support)
        flash("Support modifié avec succès.", "success")
        return redirect(url_for("supports.detail", support_id=support_id))

    return render_template("supports/formulaire.html", support=support)


@bp.route("/<int:support_id>/supprimer", methods=["POST"])
def supprimer(support_id: int) -> Response:
    """Supprime un support et redirige vers la liste."""
    db = get_db()
    if Support.trouver_par_id(db, support_id) is None:
        abort(404)
    Support.supprimer(db, support_id)
    flash("Support supprimé.", "info")
    return redirect(url_for("supports.liste"))


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _traiter_formulaire(support_id: Union[int, None]) -> Union[str, None]:
    """
    Lit les données du formulaire POST, valide et sauvegarde le support.

    Args:
        support_id: Identifiant existant pour une modification, None pour un ajout.

    Returns:
        str avec message d'erreur, ou None si succès.
    """
    from flask import current_app

    titre = request.form.get("titre", "").strip()
    type_support = request.form.get("type_support", "").strip()
    support_physique = request.form.get("support", "").strip()

    try:
        support = Support(
            id=support_id,
            titre=titre,
            type_support=type_support,
            support=support_physique,
            genre=request.form.get("genre") or None,
            date_sortie=int(request.form["date_sortie"]) if request.form.get("date_sortie") else None,
            duree=int(request.form["duree"]) if request.form.get("duree") else None,
            langue=request.form.get("langue") or None,
            interprete=request.form.get("interprete") or None,
            realisateur=request.form.get("realisateur") or None,
            acteurs=request.form.get("acteurs") or None,
        )
    except ValueError as exc:
        return str(exc)

    # Gestion de la pochette
    fichier = request.files.get("pochette")
    if fichier and fichier.filename:
        if not _extension_autorisee(fichier.filename):
            return "Format d'image non autorisé (png, jpg, jpeg, gif, webp)."
        nom_securise = secure_filename(fichier.filename)
        chemin = os.path.join(
            current_app.config["UPLOAD_FOLDER"], nom_securise
        )
        fichier.save(chemin)
        support.pochette = nom_securise

    db = get_db()
    support.sauvegarder(db)
    return None
