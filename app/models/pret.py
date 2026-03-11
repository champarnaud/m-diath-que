"""
Modèle Pret : représente un prêt d'un support à un tiers.
"""

import sqlite3
from typing import List, Optional


class Pret:
    """
    Représente le prêt d'un support audiovisuel à une personne.

    Attributes:
        id:           Identifiant en base (None si non encore sauvegardé).
        support_id:   Identifiant du support prêté.
        emprunteur:   Nom de la personne ayant emprunté le support.
        date_pret:    Date du prêt (gérée automatiquement par SQLite).
        date_retour:  Date de retour effectif (None si non rendu).
    """

    def __init__(
        self,
        support_id: int,
        emprunteur: str,
        date_pret: Optional[str] = None,
        date_retour: Optional[str] = None,
        id: Optional[int] = None,  # noqa: A002
    ) -> None:
        self.id = id
        self.support_id = support_id
        self.emprunteur = emprunteur
        self.date_pret = date_pret
        self.date_retour = date_retour

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def sauvegarder(self, db: sqlite3.Connection) -> int:
        """
        Insère le prêt en base de données.

        Args:
            db: Connexion SQLite active.

        Returns:
            int: L'identifiant du prêt créé.
        """
        cursor = db.execute(
            "INSERT INTO pret (support_id, emprunteur) VALUES (?, ?)",
            (self.support_id, self.emprunteur),
        )
        db.commit()
        self.id = cursor.lastrowid
        return self.id

    # ------------------------------------------------------------------
    # Requêtes
    # ------------------------------------------------------------------

    @classmethod
    def _depuis_row(cls, row: sqlite3.Row) -> "Pret":
        """
        Construit un objet Pret à partir d'une ligne SQLite.

        Args:
            row: Ligne retournée par sqlite3 avec row_factory=sqlite3.Row.

        Returns:
            Pret: Instance correspondante.
        """
        return cls(
            id=row["id"],
            support_id=row["support_id"],
            emprunteur=row["emprunteur"],
            date_pret=row["date_pret"],
            date_retour=row["date_retour"],
        )

    @classmethod
    def trouver_par_id(
        cls, db: sqlite3.Connection, pret_id: int
    ) -> Optional["Pret"]:
        """
        Retourne le prêt correspondant à l'identifiant donné, ou None.

        Args:
            db:      Connexion SQLite active.
            pret_id: Identifiant du prêt recherché.

        Returns:
            Pret ou None.
        """
        row = db.execute(
            "SELECT * FROM pret WHERE id = ?", (pret_id,)
        ).fetchone()
        return cls._depuis_row(row) if row else None

    @classmethod
    def lister_en_cours(cls, db: sqlite3.Connection) -> List["Pret"]:
        """
        Retourne la liste des prêts non encore rendus.

        Args:
            db: Connexion SQLite active.

        Returns:
            List[Pret]: Prêts dont la date de retour est NULL.
        """
        rows = db.execute(
            "SELECT * FROM pret WHERE date_retour IS NULL ORDER BY date_pret"
        ).fetchall()
        return [cls._depuis_row(r) for r in rows]

    @classmethod
    def retourner(cls, db: sqlite3.Connection, pret_id: int) -> None:
        """
        Enregistre la date de retour du prêt (date du jour).

        Args:
            db:      Connexion SQLite active.
            pret_id: Identifiant du prêt à clôturer.
        """
        db.execute(
            "UPDATE pret SET date_retour = date('now') WHERE id = ?",
            (pret_id,),
        )
        db.commit()
