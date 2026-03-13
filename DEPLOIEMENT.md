# Procédure de déploiement — Médiathèque

Ce document décrit, étape par étape, comment installer les dépendances, initialiser la base de données et lancer l'application Flask en environnement local.

---

## Prérequis

- **Python 3.10 ou supérieur** installé sur la machine.
- Accès au dossier racine du projet (`Vidéothèque/`).

Vérifiez votre version de Python :

```bash
python3 --version
```

---

## 1. Créer et activer l'environnement virtuel

Un environnement virtuel isole les dépendances du projet du reste du système. Cela évite les conflits de versions entre différents projets Python.

```bash
python3 -m venv .venv
```

- `python3 -m venv` : invoque le module standard Python chargé de créer des environnements virtuels.
- `.venv` : nom du dossier qui contiendra l'environnement. Par convention on le préfixe d'un point pour le masquer dans la plupart des outils.

Activez ensuite l'environnement :

```bash
source .venv/bin/activate
```

- `source` : exécute le script `activate` dans le shell courant (et non dans un sous-shell), ce qui permet de modifier les variables d'environnement de la session active (`PATH`, `VIRTUAL_ENV`, etc.).
- Une fois activé, votre invite de commande affiche `(.venv)` pour confirmer que vous travaillez bien dans l'environnement isolé.

> **Pour désactiver l'environnement** à tout moment : `deactivate`

---

## 2. Installer les dépendances

Le fichier `requirements.txt` liste toutes les bibliothèques Python nécessaires au projet.

```bash
pip install -r requirements.txt
```

- `pip install` : gestionnaire de paquets Python, télécharge et installe les bibliothèques depuis PyPI.
- `-r requirements.txt` : lit le fichier `requirements.txt` ligne par ligne et installe chaque paquet listé.

Les dépendances installées sont :

| Paquet | Rôle |
|---|---|
| `Flask>=3.0` | Framework web utilisé pour les routes, les templates et le serveur HTTP. |
| `pytest>=8.0` | Framework de tests, utilisé pour les tests unitaires et d'intégration. |
| `pytest-flask>=1.3` | Plugin pytest qui facilite les tests des applications Flask (client de test, fixtures, etc.). |

---

## 3. Initialiser la base de données

L'application utilise **SQLite**, une base de données embarquée stockée dans un seul fichier. Le schéma (tables, colonnes, contraintes) est défini dans `app/schema.sql`.

### 3a. Déclarer l'application Flask (variable d'environnement)

Flask a besoin de savoir quel fichier contient l'application pour pouvoir exécuter ses commandes CLI.

```bash
export FLASK_APP=run.py
```

- `export` : rend la variable disponible pour tous les processus enfants lancés depuis ce shell.
- `FLASK_APP` : variable d'environnement lue par Flask pour localiser l'instance de l'application.
- `run.py` : fichier racine qui crée l'application via `create_app()`.

### 3b. Exécuter la commande d'initialisation

```bash
flask init-db
```

- `flask` : CLI (interface en ligne de commande) de Flask, disponible après installation de Flask dans l'environnement.
- `init-db` : commande personnalisée enregistrée dans `app/models/db.py` via `@click.command("init-db")`. Elle exécute le fichier `app/schema.sql` contre la base de données configurée.

Résultat attendu :

```
Base de données initialisée.
```

Le fichier `instance/mediatheque.db` est créé (ou réinitialisé) avec toutes les tables : `support`, `pret`, `personne`, `activite`, `personne_activite`, `support_personne`.

> **Attention :** cette commande supprime et recrée toutes les tables (`DROP TABLE IF EXISTS`). Toute donnée existante sera effacée.

---

## 4. Lancer l'application

```bash
python run.py
```

- `python run.py` : exécute le fichier `run.py` directement, ce qui appelle `app.run(debug=True)`.
- Le mode `debug=True` active le rechargement automatique du serveur lors de modifications de fichiers et affiche les erreurs détaillées dans le navigateur. **Ne jamais utiliser ce mode en production.**

Résultat attendu dans le terminal :

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Ouvrez un navigateur et accédez à :

```
http://127.0.0.1:5000
```

---

## Récapitulatif (copier-coller)

```bash
# 1. Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Initialiser la base de données
export FLASK_APP=run.py
flask init-db

# 4. Lancer l'application
python run.py
```

---

## Lancer les tests

Pour vérifier que l'application fonctionne correctement après installation :

```bash
pytest
```

- `pytest` : découvre automatiquement tous les fichiers `test_*.py` dans le dossier `tests/` et exécute chaque fonction préfixée par `test_`.
- Les tests utilisent une base de données en mémoire (`:memory:`) définie dans `TestingConfig`, sans toucher au fichier `instance/mediatheque.db`.

---

## Structure des répertoires créés automatiquement

| Dossier / Fichier | Créé par | Rôle |
|---|---|---|
| `.venv/` | `python3 -m venv .venv` | Environnement virtuel Python isolé |
| `instance/` | Flask au démarrage (`os.makedirs`) | Contient la base de données SQLite |
| `instance/mediatheque.db` | `flask init-db` | Fichier de base de données SQLite |
| `app/static/uploads/` | Flask au démarrage (`os.makedirs`) | Stockage des pochettes importées |
