-- Schéma de la base de données Médiathèque

DROP TABLE IF EXISTS pret;
DROP TABLE IF EXISTS support;

CREATE TABLE support (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    titre        TEXT    NOT NULL,
    type_support TEXT    NOT NULL CHECK(type_support IN ('audio', 'video')),
    support      TEXT    NOT NULL,
    genre        TEXT,
    date_sortie  INTEGER,
    duree        INTEGER,
    langue       TEXT,
    interprete   TEXT,
    realisateur  TEXT,
    acteurs      TEXT,
    pochette     TEXT,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE pret (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    support_id   INTEGER NOT NULL REFERENCES support(id) ON DELETE CASCADE,
    emprunteur   TEXT    NOT NULL,
    date_pret    TEXT    NOT NULL DEFAULT (date('now')),
    date_retour  TEXT
);
