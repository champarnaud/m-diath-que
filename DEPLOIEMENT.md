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

## 3bis. Appliquer les migrations (base existante)

Si la base de données existe déjà et contient des données, **ne pas utiliser `flask init-db`** (elle efface tout). Utilisez à la place la commande de migration, qui ajoute les colonnes manquantes de façon **idempotente** — elle vérifie ce qui est déjà présent et ne modifie que ce qui manque.

```bash
flask migrate
```

- `migrate` : commande personnalisée enregistrée dans `app/models/db.py`. Elle interroge `PRAGMA table_info(support)` pour connaître les colonnes existantes, puis exécute uniquement les `ALTER TABLE` nécessaires.
- **Aucune donnée n'est effacée ou modifiée.**
- La commande est idempotente : l'exécuter plusieurs fois ne produit aucun effet secondaire.

Résultat attendu sur une base non encore migrée :

```
  + Colonne 'est_serie' ajoutée.
  + Colonne 'saisons' ajoutée.
Migration terminée : 2 colonne(s) ajoutée(s).
```

Résultat attendu si la migration a déjà été appliquée :

```
  ✓ Colonne 'est_serie' déjà présente.
  ✓ Colonne 'saisons' déjà présente.
Base de données déjà à jour.
```

### Quand appliquer `flask migrate` ?

| Situation | Commande à utiliser |
|---|---|
| Première installation (base vierge) | `flask init-db` |
| Mise à jour d'une base avec données | `flask migrate` |
| Reset complet (développement) | `flask init-db` |

### Fichiers de migration

Les scripts SQL de migration sont versionnés dans le dossier `migrations/` :

| Fichier | Date | Description |
|---|---|---|
| `migrations/001_series.sql` | 14/03/2026 | Ajout des colonnes `est_serie` et `saisons` sur la table `support` |

---

## 4. Lancer l'application

### En développement

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

### Avec gunicorn (serveur de production)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
```

- `gunicorn` : serveur WSGI de production, plus robuste que le serveur intégré de Flask.
- `-w 4` : lance 4 *workers* (processus) en parallèle pour traiter les requêtes simultanées.
- `-b 0.0.0.0:5000` : écoute sur toutes les interfaces réseau sur le port 5000 (accessible depuis d'autres machines, contrairement à `127.0.0.1`).
- `"run:app"` : indique à gunicorn de charger l'objet `app` depuis le module `run` (fichier `run.py`).
- Ajoutez `&` en fin de commande pour lancer le serveur en arrière-plan et libérer le terminal.

> Installez gunicorn si nécessaire : `pip install gunicorn`

Ouvrez un navigateur et accédez à :

```
http://127.0.0.1:5000
```

---

## 5. Arrêter l'application

### Serveur de développement Flask (premier plan)

Dans le terminal où le serveur tourne, appuyez sur :

```
Ctrl + C
```

- `Ctrl + C` : envoie le signal `SIGINT` (interruption) au processus Python en cours. Flask intercepte ce signal et arrête proprement le serveur de développement.

### Gunicorn (arrière-plan)

Si gunicorn a été lancé en arrière-plan avec `&`, le `Ctrl + C` n'est pas disponible. Utilisez l'une des commandes suivantes :

```bash
# Arrêt propre de tous les processus gunicorn (recommandé)
pkill gunicorn

# Arrêt en ciblant le port (utile si plusieurs serveurs tournent)
kill $(lsof -ti :5000)

# Si le PID a été noté au lancement (ex : [1] 12345)
kill 12345

# En dernier recours, forcer l'arrêt immédiat (SIGKILL)
pkill -9 gunicorn
```

- `pkill gunicorn` : envoie `SIGTERM` à tous les processus dont le nom contient "gunicorn", leur laissant le temps de finir les requêtes en cours.
- `lsof -ti :5000` : retourne le PID du processus qui écoute sur le port 5000.
- `kill` sans option envoie `SIGTERM` (arrêt propre) ; `kill -9` envoie `SIGKILL` (arrêt immédiat, sans nettoyage).

> Si vous avez activé un environnement virtuel, n'oubliez pas de le désactiver ensuite :
>
> ```bash
> deactivate
> ```

---

## Récapitulatif (copier-coller)

```bash
# 1. Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Initialiser la base de données (première installation)
export FLASK_APP=run.py
flask init-db

# 3bis. OU, si la base existe déjà avec des données : migrer sans perte
# flask migrate

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
| `migrations/` | Versionné dans le dépôt | Scripts SQL de migration incrémentale |
