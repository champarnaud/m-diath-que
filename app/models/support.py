"""
Modèle Support : représente un support audiovisuel de la médiathèque.
"""

import sqlite3
from typing import List, Optional


TYPES_VALIDES = ("audio", "video")
CHAMPS_TRI = ("titre", "interprete", "realisateur", "date_sortie", "genre")


class Support:
    """
    Représente un support audiovisuel (CD, DVD, Blu-ray, vinyle…).

    Attributes:
        id:           Identifiant en base (None si non encore sauvegardé).
        titre:        Titre de l'œuvre.
        type_support: 'audio' ou 'video'.
        support:      Type physique (CD, DVD, Blu-ray, vinyle…).
        genre:        Genre musical ou cinématographique.
        date_sortie:  Année de publication.
        duree:        Durée en minutes.
        langue:       Langue principale.
        interprete:   Groupe ou interprète (supports audio).
        realisateur:  Réalisateur (supports vidéo).
        acteurs:      Acteurs principaux, séparés par des virgules (supports vidéo).
        pochette:     Nom du fichier image de pochette.
    """

    def __init__(
        self,
        titre: str,
        type_support: str,
        support: str,
        genre: Optional[str] = None,
        date_sortie: Optional[int] = None,
        duree: Optional[int] = None,
        langue: Optional[str] = None,
        interprete: Optional[str] = None,
        realisateur: Optional[str] = None,
        acteurs: Optional[str] = None,
        pochette: Optional[str] = None,
        id: Optional[int] = None,  # noqa: A002
    ) -> None:
        if not titre or not titre.strip():
            raise ValueError("Le champ 'titre' est obligatoire.")
        if type_support not in TYPES_VALIDES:
            raise ValueError(
                f"Le champ 'type_support' doit être parmi {TYPES_VALIDES}."
            )

        self.id = id
        self.titre = titre.strip()
        self.type_support = type_support
        self.support = support
        self.genre = genre
        self.date_sortie = date_sortie
        self.duree = duree
        self.langue = langue
        self.interprete = interprete
        self.realisateur = realisateur
        self.acteurs = acteurs
        self.pochette = pochette

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def sauvegarder(self, db: sqlite3.Connection) -> int:
        """
        Insère ou met à jour le support en base de données.

        Args:
            db: Connexion SQLite active.

        Returns:
            int: L'identifiant du support en base.
        """
        if self.id is None:
            cursor = db.execute(
                """
                INSERT INTO support
                    (titre, type_support, support, genre, date_sortie,
                     duree, langue, interprete, realisateur, acteurs, pochette)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.titre, self.type_support, self.support, self.genre,
                    self.date_sortie, self.duree, self.langue, self.interprete,
                    self.realisateur, self.acteurs, self.pochette,
                ),
            )
            db.commit()
            self.id = cursor.lastrowid
        else:
            db.execute(
                """
                UPDATE support SET
                    titre=?, type_support=?, support=?, genre=?, date_sortie=?,
                    duree=?, langue=?, interprete=?, realisateur=?,
                    acteurs=?, pochette=?
                WHERE id=?
                """,
                (
                    self.titre, self.type_support, self.support, self.genre,
                    self.date_sortie, self.duree, self.langue, self.interprete,
                    self.realisateur, self.acteurs, self.pochette, self.id,
                ),
            )
            db.commit()
        return self.id

    # ------------------------------------------------------------------
    # Requêtes
    # ------------------------------------------------------------------

    @classmethod
    def _depuis_row(cls, row: sqlite3.Row) -> "Support":
        """
        Construit un objet Support à partir d'une ligne SQLite.

        Args:
            row: Ligne retournée par sqlite3 avec row_factory=sqlite3.Row.

        Returns:
            Support: Instance correspondante.
        """
        return cls(
            id=row["id"],
            titre=row["titre"],
            type_support=row["type_support"],
            support=row["support"],
            genre=row["genre"],
            date_sortie=row["date_sortie"],
            duree=row["duree"],
            langue=row["langue"],
            interprete=row["interprete"],
            realisateur=row["realisateur"],
            acteurs=row["acteurs"],
            pochette=row["pochette"],
        )

    @classmethod
    def trouver_par_id(
        cls, db: sqlite3.Connection, support_id: int
    ) -> Optional["Support"]:
        """
        Retourne le support correspondant à l'identifiant donné, ou None.

        Args:
            db:         Connexion SQLite active.
            support_id: Identifiant du support recherché.

        Returns:
            Support ou None.
        """
        row = db.execute(
            "SELECT * FROM support WHERE id = ?", (support_id,)
        ).fetchone()
        return cls._depuis_row(row) if row else None

    @classmethod
    def lister_tous(
        cls,
        db: sqlite3.Connection,
        tri: str = "titre",
    ) -> List["Support"]:
        """
        Retourne tous les supports, triés selon le champ indiqué.

        Args:
            db:  Connexion SQLite active.
            tri: Nom de la colonne de tri (défaut : 'titre').

        Returns:
            List[Support]: Liste de tous les supports.
        """
        tri = tri if tri in CHAMPS_TRI else "titre"
        rows = db.execute(
            f"SELECT * FROM support ORDER BY {tri} COLLATE NOCASE"
        ).fetchall()
        return [cls._depuis_row(r) for r in rows]

    @classmethod
    def lister_par_type(
        cls,
        db: sqlite3.Connection,
        type_support: str,
        tri: str = "titre",
    ) -> List["Support"]:
        """
        Retourne les supports filtrés par type (audio ou video).

        Args:
            db:           Connexion SQLite active.
            type_support: 'audio' ou 'video'.
            tri:          Nom de la colonne de tri (défaut : 'titre').

        Returns:
            List[Support]: Liste des supports du type demandé.
        """
        tri = tri if tri in CHAMPS_TRI else "titre"
        rows = db.execute(
            f"SELECT * FROM support WHERE type_support = ? ORDER BY {tri} COLLATE NOCASE",
            (type_support,),
        ).fetchall()
        return [cls._depuis_row(r) for r in rows]

    @classmethod
    def rechercher(
        cls, db: sqlite3.Connection, terme: str
    ) -> List["Support"]:
        """
        Recherche des supports dont le titre, l'interprète, le réalisateur
        ou les acteurs contiennent le terme donné (insensible à la casse).

        Args:
            db:    Connexion SQLite active.
            terme: Terme de recherche.

        Returns:
            List[Support]: Supports correspondants.
        """
        if not terme or not terme.strip():
            return []
        motif = f"%{terme.strip()}%"
        rows = db.execute(
            """
            SELECT * FROM support
            WHERE titre      LIKE ? COLLATE NOCASE
               OR interprete LIKE ? COLLATE NOCASE
               OR realisateur LIKE ? COLLATE NOCASE
               OR acteurs     LIKE ? COLLATE NOCASE
            ORDER BY titre COLLATE NOCASE
            """,
            (motif, motif, motif, motif),
        ).fetchall()
        return [cls._depuis_row(r) for r in rows]

    @classmethod
    def supprimer(cls, db: sqlite3.Connection, support_id: int) -> None:
        """
        Supprime le support identifié par son id.

        Args:
            db:         Connexion SQLite active.
            support_id: Identifiant du support à supprimer.
        """
        db.execute("DELETE FROM support WHERE id = ?", (support_id,))
        db.commit()
