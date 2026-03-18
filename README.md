# Médiathèque

Application web personnelle de gestion d'une collection de supports audiovisuels — CD, DVD, Blu-ray, vinyles, séries…

---

## Fonctionnalités

### Catalogue de supports
Chaque fiche contient :

| Champ | Description |
|---|---|
| Titre | Titre de l'œuvre |
| Type | Audio ou Vidéo |
| Support | CD, DVD, Blu-ray, vinyle… |
| Genre | Genre musical ou cinématographique |
| Année de sortie | Année de publication |
| Durée | Durée totale (minutes) |
| Langue | Langue principale |
| Interprète / Groupe | Pour les supports audio |
| Réalisateur | Pour les supports vidéo |
| Acteurs principaux | Pour les supports vidéo |
| Pochette | Image de couverture (upload) |
| Série | Pour les vidéos : case à cocher + liste de saisons (1–20) |

### Personnes & activités
- Fiches personnes (artistes, réalisateurs, acteurs…) liées aux supports
- Activités professionnelles associées (interprète, réalisateur, acteur…)

### Recherche & navigation
- Moteur de recherche textuel (titre, artiste, réalisateur, acteurs)
- Filtrage par type (Audio / Vidéo)
- Tri et pagination de la liste

### Prêts *(implémenté en base, interface à venir)*
- Suivi des supports prêtés et rendus

---

## Stack technique

| Composant | Technologie |
|---|---|
| Langage | Python 3.10+ |
| Framework web | Flask 3+ |
| Base de données | SQLite (via `sqlite3` stdlib) |
| Templates | Jinja2 |
| Tests | pytest + pytest-flask (TDD) |

---

## Installation

### 1. Environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Dépendances

```bash
pip install -r requirements.txt
```

### 3. Base de données

**Première installation :**

```bash
export FLASK_APP=run.py
flask init-db
```

**Mise à jour d'une base existante (sans perte de données) :**

```bash
flask migrate
```

> [!WARNING]
> `flask init-db` recrée toutes les tables et efface les données existantes. Utilisez `flask migrate` pour mettre à jour une base en production.

### 4. Lancer l'application

```bash
python run.py
```

Ouvrez [http://127.0.0.1:5000](http://127.0.0.1:5000) dans votre navigateur.

---

## Architecture

```
m-diath-que/
├── app/
│   ├── __init__.py          # Factory Flask (create_app)
│   ├── schema.sql           # Schéma initial de la base
│   ├── models/
│   │   ├── db.py            # Connexion SQLite, CLI init-db / migrate
│   │   ├── support.py       # Modèle Support (avec validation séries)
│   │   ├── personne.py      # Modèles Personne & Activite
│   │   └── pret.py          # Modèle Pret
│   ├── routes/
│   │   ├── supports.py      # CRUD supports
│   │   ├── personnes.py     # CRUD personnes & activités
│   │   └── recherche.py     # Moteur de recherche
│   ├── templates/           # Templates Jinja2
│   └── static/              # CSS + uploads pochettes
├── migrations/              # Scripts ALTER TABLE versionnés
├── tests/
│   ├── test_models.py       # Tests unitaires (53 tests)
│   └── test_routes.py       # Tests d'intégration
├── config.py                # Classes Config / TestingConfig
└── run.py                   # Point d'entrée
```

### Modèle de données

```
support ──< support_personne >── personne ──< personne_activite >── activite
support ──< pret
```

---

## Tests

```bash
pytest
```

Les tests utilisent une base en mémoire (`:memory:`) et ne touchent pas à `instance/mediatheque.db`.

```
53 passed in ~0.8s
```

---

## Méthodologie

Le projet suit le cycle **TDD (Test Driven Design)** :

1. **Red** — Écrire un test décrivant le comportement attendu (il échoue).
2. **Green** — Implémenter le minimum de code pour le faire passer.
3. **Refactor** — Améliorer sans changer le comportement.

Toute nouvelle fonctionnalité commence par ses tests.

---

## Migrations de base de données

Les évolutions du schéma sont gérées via des scripts SQL versionnés dans `migrations/` et appliqués par `flask migrate` (idempotent).

| Fichier | Date | Description |
|---|---|---|
| `migrations/001_series.sql` | 14/03/2026 | Ajout des colonnes `est_serie` et `saisons` sur la table `support` |

---

## Usage

Application à usage personnel, sans authentification requise.
