# Médiathèque

Application de gestion d'une collection de supports audiovisuels (CD audio, CD vidéo, DVD, Blu-ray, vinyles, etc.), accessible via un navigateur web.

---

## Description du projet

**Médiathèque** permet de cataloguer, rechercher et organiser une collection personnelle de supports audiovisuels. Chaque support est décrit par une fiche détaillée, et l'ensemble de la collection est consultable et filtrable depuis une interface web.

---

## Fonctionnalités

### Fiches support
Chaque support dispose d'une fiche contenant (liste non exhaustive) :

| Champ | Description |
|---|---|
| Titre | Titre de l'œuvre |
| Type | Audio ou Vidéo |
| Support | CD, DVD, Blu-ray, vinyle… |
| Genre | Genre musical ou cinématographique |
| Date de sortie | Année de publication |
| Durée | Durée totale |
| Langue | Langue principale |
| Groupe / Interprète | Pour les supports audio |
| Réalisateur | Pour les supports vidéo |
| Acteurs principaux | Pour les supports vidéo |
| Pochette | Image de couverture |

### Recherche
- Moteur de recherche textuel sur les principaux champs (titre, artiste, réalisateur, acteurs…)

### Listes et tri
- Affichage de la collection filtrée par type (Audio / Vidéo)
- Tri par : titre, réalisateur, auteur/interprète, acteur

### Gestion des prêts *(à venir)*
- Suivi des supports prêtés à des tiers

---

## Stack technique

| Composant | Technologie |
|---|---|
| Langage | Python |
| Interface web | Flask |
| Base de données | SQLite |
| Tests | pytest (TDD) |

---

## Architecture du projet

```
Médiathèque/
├── README.md
├── app/                  # Code source de l'application Flask
│   ├── __init__.py
│   ├── models/           # Modèles de données (SQLite)
│   ├── routes/           # Routes Flask
│   ├── templates/        # Templates HTML (Jinja2)
│   └── static/           # Fichiers statiques (CSS, JS, images)
├── tests/                # Tests unitaires et d'intégration (pytest)
├── instance/             # Base de données SQLite (non versionnée)
└── requirements.txt      # Dépendances Python
```

---

## Méthodologie de développement

Le projet est développé en suivant le **Test Driven Design (TDD)** :

1. **Red** — Écrire un test qui décrit le comportement attendu (il échoue).
2. **Green** — Implémenter le minimum de code pour faire passer le test.
3. **Refactor** — Améliorer le code sans modifier son comportement.

---

## Usage

Application à usage personnel, sans authentification requise.
