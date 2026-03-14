-- Migration 001 : ajout des champs "série" sur la table support
--
-- Cette migration est idempotente : la commande `flask migrate` vérifie
-- l'existence des colonnes (PRAGMA table_info) avant d'exécuter les ALTER.
-- Ne jamais utiliser ce fichier directement avec sqlite3 sans passer
-- par `flask migrate`, sauf sur une base vierge.

ALTER TABLE support ADD COLUMN est_serie INTEGER NOT NULL DEFAULT 0;
ALTER TABLE support ADD COLUMN saisons    TEXT;
