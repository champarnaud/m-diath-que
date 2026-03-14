"""
Modèles Activite et Personne : représentent les contributeurs
artistiques de la médiathèque (réalisateurs, acteurs, interprètes…).
"""

import sqlite3
from typing import List, Optional


# ------------------------------------------------------------------
# Constantes métier : mots-clés de rôles pour le filtrage des personnes
# ------------------------------------------------------------------

# Sous-chaînes cherchées dans le libellé de l'activité (insensible à la casse)
MOTS_CLES_INTERPRETE: List[str] = [
    "interpr", "chanteur", "chanteuse", "musicien",
    "groupe", "artiste", "band",
]
MOTS_CLES_REALISATEUR: List[str] = [
    "réalisateur", "realisateur", "metteur", "director",
]
MOTS_CLES_ACTEUR: List[str] = [
    "acteur", "actrice", "comédien", "comedien",
]


class Activite:
    """
    Représente une activité ou profession artistique.

    Attributes:
        id:      Identifiant en base (None si non encore sauvegardé).
        libelle: Intitulé de l'activité (ex : « Réalisateur », « Acteur »).
    """

    def __init__(self, libelle: str, id: Optional[int] = None) -> None:  # noqa: A002
        if not libelle or not libelle.strip():
            raise ValueError("Le champ 'libelle' est obligatoire.")
        self.id = id
        self.libelle = libelle.strip()

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def sauvegarder(self, db: sqlite3.Connection) -> int:
        """
        Insère ou met à jour l'activité en base de données.

        Args:
            db: Connexion SQLite active.

        Returns:
            int: L'identifiant de l'activité en base.
        """
        if self.id is None:
            cursor = db.execute(
                "INSERT INTO activite (libelle) VALUES (?)",
                (self.libelle,),
            )
            db.commit()
            self.id = cursor.lastrowid
        else:
            db.execute(
                "UPDATE activite SET libelle = ? WHERE id = ?",
                (self.libelle, self.id),
            )
            db.commit()
        return self.id

    # ------------------------------------------------------------------
    # Requêtes
    # ------------------------------------------------------------------

    @classmethod
    def _depuis_row(cls, row: sqlite3.Row) -> "Activite":
        """
        Construit un objet Activite à partir d'une ligne SQLite.

        Args:
            row: Ligne retournée par sqlite3 avec row_factory=sqlite3.Row.

        Returns:
            Activite: Instance correspondante.
        """
        return cls(id=row["id"], libelle=row["libelle"])

    @classmethod
    def trouver_par_id(
        cls, db: sqlite3.Connection, activite_id: int
    ) -> Optional["Activite"]:
        """
        Retourne l'activité correspondant à l'identifiant, ou None.

        Args:
            db:          Connexion SQLite active.
            activite_id: Identifiant de l'activité.

        Returns:
            Activite ou None.
        """
        row = db.execute(
            "SELECT * FROM activite WHERE id = ?", (activite_id,)
        ).fetchone()
        return cls._depuis_row(row) if row else None

    @classmethod
    def lister_toutes(cls, db: sqlite3.Connection) -> List["Activite"]:
        """
        Retourne toutes les activités triées alphabétiquement.

        Args:
            db: Connexion SQLite active.

        Returns:
            List[Activite]: Liste de toutes les activités.
        """
        rows = db.execute(
            "SELECT * FROM activite ORDER BY libelle COLLATE NOCASE"
        ).fetchall()
        return [cls._depuis_row(r) for r in rows]

    @classmethod
    def supprimer(cls, db: sqlite3.Connection, activite_id: int) -> None:
        """
        Supprime l'activité identifiée par son id.

        Args:
            db:          Connexion SQLite active.
            activite_id: Identifiant de l'activité à supprimer.
        """
        db.execute("DELETE FROM activite WHERE id = ?", (activite_id,))
        db.commit()


class Personne:
    """
    Représente une personne physique (artiste, réalisateur, acteur…).

    Attributes:
        id:             Identifiant en base (None si non encore sauvegardé).
        nom:            Nom complet de la personne.
        date_naissance: Date de naissance (format libre, ex : « 1946-09-18 »).
        date_deces:     Date de décès (None si vivant).
        activites:      Liste des activités associées (chargée séparément).
    """

    def __init__(
        self,
        nom: str,
        date_naissance: Optional[str] = None,
        date_deces: Optional[str] = None,
        id: Optional[int] = None,  # noqa: A002
    ) -> None:
        if not nom or not nom.strip():
            raise ValueError("Le champ 'nom' est obligatoire.")
        self.id = id
        self.nom = nom.strip()
        self.date_naissance = date_naissance
        self.date_deces = date_deces
        self.activites: List[Activite] = []

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def sauvegarder(self, db: sqlite3.Connection) -> int:
        """
        Insère ou met à jour la personne en base de données.

        Les activités associées (self.activites) ne sont pas sauvegardées
        ici ; utiliser ajouter_activite / retirer_activite séparément.

        Args:
            db: Connexion SQLite active.

        Returns:
            int: L'identifiant de la personne en base.
        """
        if self.id is None:
            cursor = db.execute(
                """
                INSERT INTO personne (nom, date_naissance, date_deces)
                VALUES (?, ?, ?)
                """,
                (self.nom, self.date_naissance, self.date_deces),
            )
            db.commit()
            self.id = cursor.lastrowid
        else:
            db.execute(
                """
                UPDATE personne
                SET nom = ?, date_naissance = ?, date_deces = ?
                WHERE id = ?
                """,
                (self.nom, self.date_naissance, self.date_deces, self.id),
            )
            db.commit()
        return self.id

    def ajouter_activite(
        self, db: sqlite3.Connection, activite_id: int
    ) -> None:
        """
        Associe une activité à cette personne.

        Ignore silencieusement si l'association existe déjà.

        Args:
            db:          Connexion SQLite active.
            activite_id: Identifiant de l'activité à associer.
        """
        db.execute(
            """
            INSERT OR IGNORE INTO personne_activite (personne_id, activite_id)
            VALUES (?, ?)
            """,
            (self.id, activite_id),
        )
        db.commit()

    def retirer_activite(
        self, db: sqlite3.Connection, activite_id: int
    ) -> None:
        """
        Dissocie une activité de cette personne.

        Args:
            db:          Connexion SQLite active.
            activite_id: Identifiant de l'activité à retirer.
        """
        db.execute(
            """
            DELETE FROM personne_activite
            WHERE personne_id = ? AND activite_id = ?
            """,
            (self.id, activite_id),
        )
        db.commit()

    def charger_activites(self, db: sqlite3.Connection) -> None:
        """
        Charge les activités associées depuis la base et les stocke
        dans self.activites.

        Args:
            db: Connexion SQLite active.
        """
        rows = db.execute(
            """
            SELECT a.* FROM activite a
            JOIN personne_activite pa ON pa.activite_id = a.id
            WHERE pa.personne_id = ?
            ORDER BY a.libelle COLLATE NOCASE
            """,
            (self.id,),
        ).fetchall()
        self.activites = [Activite._depuis_row(r) for r in rows]

    # ------------------------------------------------------------------
    # Requêtes
    # ------------------------------------------------------------------

    @classmethod
    def _depuis_row(cls, row: sqlite3.Row) -> "Personne":
        """
        Construit un objet Personne à partir d'une ligne SQLite.

        Args:
            row: Ligne retournée par sqlite3 avec row_factory=sqlite3.Row.

        Returns:
            Personne: Instance correspondante.
        """
        return cls(
            id=row["id"],
            nom=row["nom"],
            date_naissance=row["date_naissance"],
            date_deces=row["date_deces"],
        )

    @classmethod
    def trouver_par_id(
        cls, db: sqlite3.Connection, personne_id: int
    ) -> Optional["Personne"]:
        """
        Retourne la personne correspondant à l'identifiant, ou None.

        Charge également les activités associées.

        Args:
            db:          Connexion SQLite active.
            personne_id: Identifiant de la personne.

        Returns:
            Personne ou None.
        """
        row = db.execute(
            "SELECT * FROM personne WHERE id = ?", (personne_id,)
        ).fetchone()
        if row is None:
            return None
        personne = cls._depuis_row(row)
        personne.charger_activites(db)
        return personne

    @classmethod
    def lister_toutes(cls, db: sqlite3.Connection) -> List["Personne"]:
        """
        Retourne toutes les personnes triées alphabétiquement par nom.

        N'inclut pas les activités ; appeler charger_activites() si besoin.

        Args:
            db: Connexion SQLite active.

        Returns:
            List[Personne]: Liste de toutes les personnes.
        """
        rows = db.execute(
            "SELECT * FROM personne ORDER BY nom COLLATE NOCASE"
        ).fetchall()
        return [cls._depuis_row(r) for r in rows]

    @classmethod
    def lister_avec_activites(cls, db: sqlite3.Connection) -> List["Personne"]:
        """
        Retourne toutes les personnes avec leurs activités pré-chargées.

        Effectue un chargement grouper des activités pour éviter les
        requêtes N+1.

        Args:
            db: Connexion SQLite active.

        Returns:
            List[Personne]: Personnes avec self.activites renseigné.
        """
        personnes = cls.lister_toutes(db)
        if not personnes:
            return personnes
        ids = [p.id for p in personnes]
        placeholders = ",".join("?" * len(ids))
        act_rows = db.execute(
            f"""
            SELECT pa.personne_id, a.id AS activite_id, a.libelle
            FROM activite a
            JOIN personne_activite pa ON pa.activite_id = a.id
            WHERE pa.personne_id IN ({placeholders})
            ORDER BY a.libelle COLLATE NOCASE
            """,
            ids,
        ).fetchall()
        acts_par_personne: dict = {}
        for row in act_rows:
            pid = row["personne_id"]
            acts_par_personne.setdefault(pid, []).append(
                Activite(id=row["activite_id"], libelle=row["libelle"])
            )
        for p in personnes:
            p.activites = acts_par_personne.get(p.id, [])
        return personnes

    @classmethod
    def lister_pour_role(
        cls,
        db: sqlite3.Connection,
        mots_cles: List[str],
    ) -> List["Personne"]:
        """
        Retourne les personnes dont au moins une activité contient
        l'un des mots-clés donnés (recherche insensible à la casse).

        Utilisé pour pré-filtrer les selects du formulaire support
        selon le rôle (acteur, réalisateur, interprète…).

        Args:
            db:        Connexion SQLite active.
            mots_cles: Sous-chaînes à chercher dans le libellé.

        Returns:
            List[Personne]: Personnes correspondantes avec activités
                            chargées.
        """
        conditions = " OR ".join(
            ["a.libelle LIKE ? COLLATE NOCASE"] * len(mots_cles)
        )
        params = [f"%{mot}%" for mot in mots_cles]
        rows = db.execute(
            f"""
            SELECT DISTINCT p.*
            FROM personne p
            JOIN personne_activite pa ON pa.personne_id = p.id
            JOIN activite a ON a.id = pa.activite_id
            WHERE {conditions}
            ORDER BY p.nom COLLATE NOCASE
            """,
            params,
        ).fetchall()
        personnes = [cls._depuis_row(r) for r in rows]
        if not personnes:
            return personnes
        ids = [p.id for p in personnes]
        placeholders = ",".join("?" * len(ids))
        act_rows = db.execute(
            f"""
            SELECT pa.personne_id, a.id AS activite_id, a.libelle
            FROM activite a
            JOIN personne_activite pa ON pa.activite_id = a.id
            WHERE pa.personne_id IN ({placeholders})
            ORDER BY a.libelle COLLATE NOCASE
            """,
            ids,
        ).fetchall()
        acts_par_personne: dict = {}
        for row in act_rows:
            pid = row["personne_id"]
            acts_par_personne.setdefault(pid, []).append(
                Activite(id=row["activite_id"], libelle=row["libelle"])
            )
        for p in personnes:
            p.activites = acts_par_personne.get(p.id, [])
        return personnes

    @classmethod
    def lister_interpretes(cls, db: sqlite3.Connection) -> List["Personne"]:
        """
        Retourne les personnes dont l'activité correspond à un rôle
        d'interprète (chanteur, musicien, groupe…).

        Args:
            db: Connexion SQLite active.

        Returns:
            List[Personne]: Interprètes triés alphabétiquement.
        """
        return cls.lister_pour_role(db, MOTS_CLES_INTERPRETE)

    @classmethod
    def lister_realisateurs(cls, db: sqlite3.Connection) -> List["Personne"]:
        """
        Retourne les personnes dont l'activité correspond à un rôle
        de réalisateur / metteur en scène.

        Args:
            db: Connexion SQLite active.

        Returns:
            List[Personne]: Réalisateurs triés alphabétiquement.
        """
        return cls.lister_pour_role(db, MOTS_CLES_REALISATEUR)

    @classmethod
    def lister_acteurs(cls, db: sqlite3.Connection) -> List["Personne"]:
        """
        Retourne les personnes dont l'activité correspond à un rôle
        d'acteur / comédien.

        Args:
            db: Connexion SQLite active.

        Returns:
            List[Personne]: Acteurs triés alphabétiquement.
        """
        return cls.lister_pour_role(db, MOTS_CLES_ACTEUR)

    @classmethod
    def supprimer(cls, db: sqlite3.Connection, personne_id: int) -> None:
        """
        Supprime la personne identifiée par son id.

        Les associations personne_activite et support_personne sont
        supprimées en cascade par SQLite.

        Args:
            db:          Connexion SQLite active.
            personne_id: Identifiant de la personne à supprimer.
        """
        db.execute("DELETE FROM personne WHERE id = ?", (personne_id,))
        db.commit()
