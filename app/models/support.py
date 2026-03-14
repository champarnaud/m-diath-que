"""
Modèle Support : représente un support audiovisuel de la médiathèque.
"""

import sqlite3
from typing import Dict, List, Optional


TYPES_VALIDES = ("audio", "video")
CHAMPS_TRI = ("titre", "date_sortie", "genre")

SAISON_MIN = 1
SAISON_MAX = 20


class Support:
    """
    Représente un support audiovisuel (CD, DVD, Blu-ray, vinyle…).

    Attributes:
        id:           Identifiant en base (None si non encore sauvegardé).
        titre:        Titre de l'œuvre.
        type_support: 'audio' ou 'video'.
        support:      Type physique (CD, DVD, Blu-ray…).
        genre:        Genre musical ou cinématographique.
        date_sortie:  Année de publication.
        duree:        Durée en minutes.
        langue:       Langue principale.
        pochette:     Nom du fichier image de pochette.
        personnes:    Liste de dicts {id, nom, role} chargée via
                      charger_personnes().
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
        pochette: Optional[str] = None,
        est_serie: bool = False,
        saisons: Optional[str] = None,
        id: Optional[int] = None,  # noqa: A002
    ) -> None:
        if not titre or not titre.strip():
            raise ValueError("Le champ 'titre' est obligatoire.")
        if type_support not in TYPES_VALIDES:
            raise ValueError(
                f"Le champ 'type_support' doit être parmi {TYPES_VALIDES}."
            )
        if est_serie and type_support != "video":
            raise ValueError(
                "Seuls les supports vidéo peuvent être marqués comme série."
            )
        if est_serie:
            Support._valider_saisons(saisons)

        self.id = id
        self.titre = titre.strip()
        self.type_support = type_support
        self.support = support
        self.genre = genre
        self.date_sortie = date_sortie
        self.duree = duree
        self.langue = langue
        self.pochette = pochette
        self.est_serie: bool = bool(est_serie)
        self.saisons: Optional[str] = saisons if est_serie else None
        self.personnes: List[Dict] = []

    # ------------------------------------------------------------------
    # Validation des saisons
    # ------------------------------------------------------------------

    @staticmethod
    def _valider_saisons(saisons_str: Optional[str]) -> List[int]:
        """
        Valide la chaîne de saisons et retourne la liste des entiers.

        Les valeurs doivent être des entiers entre SAISON_MIN et SAISON_MAX,
        séparés par des virgules.

        Args:
            saisons_str: Chaîne de saisons (ex : "1,2,3").

        Returns:
            List[int]: Liste des numéros de saison validés.

        Raises:
            ValueError: Si la chaîne est vide, contient des valeurs non
                        entières ou hors de l'intervalle autorisé.
        """
        if not saisons_str or not saisons_str.strip():
            raise ValueError(
                "Le champ 'saisons' est obligatoire pour une série."
            )
        parties = [s.strip() for s in saisons_str.split(",") if s.strip()]
        if not parties:
            raise ValueError(
                "Le champ 'saisons' doit contenir au moins un numéro."
            )
        resultat: List[int] = []
        for partie in parties:
            try:
                n = int(partie)
            except ValueError:
                raise ValueError(
                    f"La valeur '{partie}' n'est pas un entier valide "
                    f"pour un numéro de saison."
                )
            if n < SAISON_MIN or n > SAISON_MAX:
                raise ValueError(
                    f"Le numéro de saison {n} doit être compris entre "
                    f"{SAISON_MIN} et {SAISON_MAX}."
                )
            resultat.append(n)
        return resultat

    def saisons_liste(self) -> List[int]:
        """
        Retourne la liste des numéros de saison sous forme d'entiers.

        Retourne une liste vide si le support n'est pas une série
        ou si aucune saison n'est renseignée.

        Returns:
            List[int]: Numéros de saison.
        """
        if not self.est_serie or not self.saisons:
            return []
        return [int(s.strip()) for s in self.saisons.split(",") if s.strip()]

    # ------------------------------------------------------------------
    # Associations personnes
    # ------------------------------------------------------------------

    def charger_personnes(self, db: sqlite3.Connection) -> None:
        """
        Charge les personnes associées au support dans self.personnes.

        Chaque entrée est un dict {id, nom, role}.

        Args:
            db: Connexion SQLite active.
        """
        rows = db.execute(
            """
            SELECT p.id, p.nom, sp.role
            FROM personne p
            JOIN support_personne sp ON sp.personne_id = p.id
            WHERE sp.support_id = ?
            ORDER BY sp.role, p.nom COLLATE NOCASE
            """,
            (self.id,),
        ).fetchall()
        self.personnes = [
            {"id": r["id"], "nom": r["nom"], "role": r["role"]}
            for r in rows
        ]

    def retirer_toutes_personnes(self, db: sqlite3.Connection) -> None:
        """
        Supprime toutes les associations personne ↔ ce support.

        À utiliser avant de ré-associer les personnes lors d'une édition.

        Args:
            db: Connexion SQLite active.
        """
        db.execute(
            "DELETE FROM support_personne WHERE support_id = ?", (self.id,)
        )
        db.commit()

    def associer_personne(
        self, db: sqlite3.Connection, personne_id: int, role: str
    ) -> None:
        """
        Associe une personne à ce support avec un rôle donné.

        Ignore silencieusement si l'association existe déjà.

        Args:
            db:          Connexion SQLite active.
            personne_id: Identifiant de la personne.
            role:        Rôle de la personne sur ce support
                         (ex : 'realisateur', 'acteur', 'interprete').
        """
        db.execute(
            """
            INSERT OR IGNORE INTO support_personne
                (support_id, personne_id, role)
            VALUES (?, ?, ?)
            """,
            (self.id, personne_id, role),
        )
        db.commit()

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
                     duree, langue, pochette, est_serie, saisons)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.titre, self.type_support, self.support, self.genre,
                    self.date_sortie, self.duree, self.langue, self.pochette,
                    int(self.est_serie), self.saisons,
                ),
            )
            db.commit()
            self.id = cursor.lastrowid
        else:
            db.execute(
                """
                UPDATE support SET
                    titre=?, type_support=?, support=?, genre=?,
                    date_sortie=?, duree=?, langue=?, pochette=?,
                    est_serie=?, saisons=?
                WHERE id=?
                """,
                (
                    self.titre, self.type_support, self.support, self.genre,
                    self.date_sortie, self.duree, self.langue, self.pochette,
                    int(self.est_serie), self.saisons,
                    self.id,
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

        Les personnes associées ne sont pas chargées automatiquement.
        Appeler charger_personnes() si nécessaire.

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
            pochette=row["pochette"],
            est_serie=bool(row["est_serie"]),
            saisons=row["saisons"],
        )

    @classmethod
    def trouver_par_id(
        cls, db: sqlite3.Connection, support_id: int
    ) -> Optional["Support"]:
        """
        Retourne le support correspondant à l'identifiant donné, ou None.

        Charge également les personnes associées.

        Args:
            db:         Connexion SQLite active.
            support_id: Identifiant du support recherché.

        Returns:
            Support ou None.
        """
        row = db.execute(
            "SELECT * FROM support WHERE id = ?", (support_id,)
        ).fetchone()
        if row is None:
            return None
        support = cls._depuis_row(row)
        support.charger_personnes(db)
        return support

    @classmethod
    def compter_tous(cls, db: sqlite3.Connection) -> int:
        """
        Retourne le nombre total de supports en base.

        Args:
            db: Connexion SQLite active.

        Returns:
            int: Nombre total de supports.
        """
        return db.execute(
            "SELECT COUNT(*) FROM support"
        ).fetchone()[0]

    @classmethod
    def compter_par_type(
        cls, db: sqlite3.Connection, type_support: str
    ) -> int:
        """
        Retourne le nombre de supports d'un type donné.

        Args:
            db:           Connexion SQLite active.
            type_support: 'audio' ou 'video'.

        Returns:
            int: Nombre de supports du type demandé.
        """
        return db.execute(
            "SELECT COUNT(*) FROM support WHERE type_support = ?",
            (type_support,),
        ).fetchone()[0]

    @classmethod
    def lister_tous(
        cls,
        db: sqlite3.Connection,
        tri: str = "titre",
        limite: Optional[int] = None,
        offset: int = 0,
    ) -> List["Support"]:
        """
        Retourne tous les supports, triés selon le champ indiqué.

        Args:
            db:     Connexion SQLite active.
            tri:    Nom de la colonne de tri (défaut : 'titre').
            limite: Nombre maximum de résultats (None = tous).
            offset: Décalage pour la pagination (défaut : 0).

        Returns:
            List[Support]: Liste de tous les supports.
        """
        tri = tri if tri in CHAMPS_TRI else "titre"
        if limite is not None:
            rows = db.execute(
                f"""
                SELECT * FROM support
                ORDER BY {tri} COLLATE NOCASE
                LIMIT ? OFFSET ?
                """,
                (limite, offset),
            ).fetchall()
        else:
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
        limite: Optional[int] = None,
        offset: int = 0,
    ) -> List["Support"]:
        """
        Retourne les supports filtrés par type (audio ou video).

        Args:
            db:           Connexion SQLite active.
            type_support: 'audio' ou 'video'.
            tri:          Nom de la colonne de tri (défaut : 'titre').
            limite:       Nombre maximum de résultats (None = tous).
            offset:       Décalage pour la pagination (défaut : 0).

        Returns:
            List[Support]: Liste des supports du type demandé.
        """
        tri = tri if tri in CHAMPS_TRI else "titre"
        if limite is not None:
            rows = db.execute(
                f"""
                SELECT * FROM support
                WHERE type_support = ?
                ORDER BY {tri} COLLATE NOCASE
                LIMIT ? OFFSET ?
                """,
                (type_support, limite, offset),
            ).fetchall()
        else:
            rows = db.execute(
                f"""
                SELECT * FROM support
                WHERE type_support = ?
                ORDER BY {tri} COLLATE NOCASE
                """,
                (type_support,),
            ).fetchall()
        return [cls._depuis_row(r) for r in rows]

    @classmethod
    def rechercher(
        cls, db: sqlite3.Connection, terme: str
    ) -> List["Support"]:
        """
        Recherche des supports dont le titre ou le nom d'une personne
        associée contient le terme donné (insensible à la casse).

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
            SELECT DISTINCT s.*
            FROM support s
            LEFT JOIN support_personne sp ON sp.support_id = s.id
            LEFT JOIN personne p ON p.id = sp.personne_id
            WHERE s.titre LIKE ? COLLATE NOCASE
               OR p.nom   LIKE ? COLLATE NOCASE
            ORDER BY s.titre COLLATE NOCASE
            """,
            (motif, motif),
        ).fetchall()
        return [cls._depuis_row(r) for r in rows]

    @classmethod
    def supprimer(cls, db: sqlite3.Connection, support_id: int) -> None:
        """
        Supprime le support identifié par son id.

        Les associations support_personne et prêts sont supprimés
        en cascade par SQLite.

        Args:
            db:         Connexion SQLite active.
            support_id: Identifiant du support à supprimer.
        """
        db.execute("DELETE FROM support WHERE id = ?", (support_id,))
