"""
Routes principales : liste, détail, ajout, modification, suppression.
"""

import os
from typing import Union

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename
from werkzeug import Response

from app.models.db import get_db
from app.models.personne import Personne
from app.models.support import Support

bp = Blueprint("supports", __name__, url_prefix="/supports")

EXTENSIONS_AUTORISEES = {"png", "jpg", "jpeg", "gif", "webp"}

_MOTS_CLES_INTERPRETE = ["interpr", "chanteur", "chanteuse", "musicien", "groupe", "artiste", "band"]
_MOTS_CLES_REALISATEUR = ["réalisateur", "realisateur", "metteur", "director"]
_MOTS_CLES_ACTEUR = ["acteur", "actrice", "comédien", "comedien"]


def _listes_personnes_formulaire(db):
    return (
        Personne.lister_pour_role(db, _MOTS_CLES_INTERPRETE),
        Personne.lister_pour_role(db, _MOTS_CLES_REALISATEUR),
        Personne.lister_pour_role(db, _MOTS_CLES_ACTEUR),
    )


def _extension_autorisee(nom_fichier: str) -> bool:
    """Vérifie que l'extension du fichier est dans la liste autorisée."""
    return (
        "." in nom_fichier
        and nom_fichier.rsplit(".", 1)[1].lower() in EXTENSIONS_AUTORISEES
    )


PAR_PAGE_VALIDES = (10, 50, 100)


@bp.route("/")
def liste() -> str:
    """Affiche la liste de tous les supports, avec filtre, tri et pagination."""
    db = get_db()
    type_filtre = request.args.get("type", "")
    tri = request.args.get("tri", "titre")

    try:
        par_page = int(request.args.get("par_page", 10))
    except ValueError:
        par_page = 10
    if par_page not in PAR_PAGE_VALIDES:
        par_page = 10

    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1

    offset = (page - 1) * par_page

    if type_filtre in ("audio", "video"):
        total = Support.compter_par_type(db, type_filtre)
        supports = Support.lister_par_type(
            db, type_filtre, tri=tri, limite=par_page, offset=offset
        )
    else:
        total = Support.compter_tous(db)
        supports = Support.lister_tous(
            db, tri=tri, limite=par_page, offset=offset
        )

    nb_pages = max(1, (total + par_page - 1) // par_page)
    page = min(page, nb_pages)

    for s in supports:
        s.charger_personnes(db)

    return render_template(
        "supports/liste.html",
        supports=supports,
        type_filtre=type_filtre,
        tri=tri,
        par_page=par_page,
        page=page,
        nb_pages=nb_pages,
        total=total,
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
    db = get_db()
    interpretes, realisateurs, acteurs = _listes_personnes_formulaire(db)
    if request.method == "POST":
        erreur = _traiter_formulaire(support_id=None)
        if erreur:
            flash(erreur, "danger")
            return render_template(
                "supports/formulaire.html",
                support=None,
                interpretes=interpretes,
                realisateurs=realisateurs,
                acteurs=acteurs,
                ids_interpretes=[],
                ids_realisateurs=[],
                ids_acteurs=[],
            )
        flash("Support ajouté avec succès.", "success")
        return redirect(url_for("supports.liste"))

    return render_template(
        "supports/formulaire.html",
        support=None,
        interpretes=interpretes,
        realisateurs=realisateurs,
        acteurs=acteurs,
        ids_interpretes=[],
        ids_realisateurs=[],
        ids_acteurs=[],
    )


@bp.route("/<int:support_id>/modifier", methods=["GET", "POST"])
def modifier(support_id: int) -> Union[str, Response]:
    """Affiche et traite le formulaire de modification d'un support."""
    db = get_db()
    support = Support.trouver_par_id(db, support_id)
    if support is None:
        abort(404)
    interpretes, realisateurs, acteurs = _listes_personnes_formulaire(db)
    ids_interpretes = [
        p["id"] for p in support.personnes if p["role"] == "interprete"
    ]
    ids_realisateurs = [
        p["id"] for p in support.personnes if p["role"] == "realisateur"
    ]
    ids_acteurs = [
        p["id"] for p in support.personnes if p["role"] == "acteur"
    ]

    if request.method == "POST":
        erreur = _traiter_formulaire(support_id=support_id)
        if erreur:
            flash(erreur, "danger")
            return render_template(
                "supports/formulaire.html",
                support=support,
                interpretes=interpretes,
                realisateurs=realisateurs,
                acteurs=acteurs,
                ids_interpretes=ids_interpretes,
                ids_realisateurs=ids_realisateurs,
                ids_acteurs=ids_acteurs,
            )
        flash("Support modifié avec succès.", "success")
        return redirect(url_for("supports.detail", support_id=support_id))

    return render_template(
        "supports/formulaire.html",
        support=support,
        interpretes=interpretes,
        realisateurs=realisateurs,
        acteurs=acteurs,
        ids_interpretes=ids_interpretes,
        ids_realisateurs=ids_realisateurs,
        ids_acteurs=ids_acteurs,
    )


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
            date_sortie=(
                int(request.form["date_sortie"])
                if request.form.get("date_sortie")
                else None
            ),
            duree=(
                int(request.form["duree"])
                if request.form.get("duree")
                else None
            ),
            langue=request.form.get("langue") or None,
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

    # Associations personnes : on repart de zéro puis on réinsère
    support.retirer_toutes_personnes(db)
    for role in ("realisateur", "acteur", "interprete"):
        for pid in request.form.getlist(f"{role}_ids"):
            try:
                support.associer_personne(db, int(pid), role)
            except (ValueError, TypeError):
                pass

    return None
