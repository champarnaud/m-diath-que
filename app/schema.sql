-- Schéma de la base de données Médiathèque

DROP TABLE IF EXISTS support_personne;
DROP TABLE IF EXISTS personne_activite;
DROP TABLE IF EXISTS pret;
DROP TABLE IF EXISTS support;
DROP TABLE IF EXISTS personne;
DROP TABLE IF EXISTS activite;

CREATE TABLE support (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    titre        TEXT    NOT NULL,
    type_support TEXT    NOT NULL CHECK(type_support IN ('audio', 'video')),
    support      TEXT    NOT NULL,
    genre        TEXT,
    date_sortie  INTEGER,
    duree        INTEGER,
    langue       TEXT,
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

-- Activités exercées par une personne (réalisateur, acteur, chanteur…)
CREATE TABLE activite (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle TEXT    NOT NULL UNIQUE
);

-- Personnes physiques (artistes, réalisateurs, acteurs…)
CREATE TABLE personne (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nom            TEXT    NOT NULL,
    date_naissance TEXT,
    date_deces     TEXT
);

-- Association many-to-many personne ↔ activité
CREATE TABLE personne_activite (
    personne_id INTEGER NOT NULL REFERENCES personne(id) ON DELETE CASCADE,
    activite_id INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    PRIMARY KEY (personne_id, activite_id)
);

-- Association personne ↔ support avec le rôle précis sur ce support
CREATE TABLE support_personne (
    support_id  INTEGER NOT NULL REFERENCES support(id) ON DELETE CASCADE,
    personne_id INTEGER NOT NULL REFERENCES personne(id) ON DELETE CASCADE,
    role        TEXT    NOT NULL,
    PRIMARY KEY (support_id, personne_id, role)
);
