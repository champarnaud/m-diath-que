"""
Routes de recherche.
"""

from flask import Blueprint, render_template, request

from app.models.db import get_db
from app.models.support import Support

bp = Blueprint("recherche", __name__)


@bp.route("/recherche")
def rechercher() -> str:
    """Affiche les résultats de recherche pour le terme fourni."""
    terme = request.args.get("q", "").strip()
    db = get_db()
    resultats = Support.rechercher(db, terme) if terme else []
    return render_template(
        "recherche.html",
        resultats=resultats,
        terme=terme,
    )
