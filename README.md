# Projet de Microservices avec Docker : Bibliothèque en Ligne

Ce projet est une application de gestion de bibliothèque construite à l'aide de trois microservices : **Frontend**, **Backend** et **Auth**, chacun géré indépendamment et conteneurisé avec Docker.

## Contenu du projet

### Structure des microservices
1. **Frontend** : Interface utilisateur pour accéder à l'application.
2. **Backend** : Fournit les fonctionnalités principales de gestion des livres, des utilisateurs et des emprunts.
3. **Auth** : Gère l'authentification et l'autorisation via JWT.

### Fonctionnalités principales
- **Gestion des livres** : Permet de rechercher, afficher et lister les livres disponibles dans la base de données.
- **Gestion des utilisateurs** : Recherche et affichage des utilisateurs inscrits dans la bibliothèque.
- **Suivi des emprunts** : Liste les livres actuellement empruntés et les utilisateurs associés.
- **Authentification sécurisée** : Les utilisateurs se connectent avec des identifiants protégés par un système de hachage des mots de passe (bcrypt). Cela garantit une sécurité accrue en cas de compromission des données.

### Technologies utilisées
- **FastAPI** pour le développement des microservices.
- **SQLite** comme base de données locale pour stocker les utilisateurs, les livres et les emprunts.
- **Docker** pour conteneuriser chaque service indépendamment.
- **Docker Compose** pour orchestrer et gérer l'interconnexion entre les services.
- **JWT** pour l´authentification de notre microservice.

## Pré-requis
1. **Docker** et **Docker Compose** doivent être installés.
   - Téléchargez et installez Docker depuis : [https://www.docker.com/](https://www.docker.com/)

## Instructions pour exécuter le projet

### Étape 1 : Construire les conteneurs Docker

Assurez-vous que vous êtes dans le répertoire racine du projet où se trouve le fichier `docker-compose.yml`. Ensuite, exécutez les commandes suivantes :

```bash
# Construire les conteneurs
docker compose build
```

### Étape 2 : Démarrer les services

Une fois les conteneurs construits, lancez les trois microservices avec :

```bash
# Démarrer les services avec Docker Compose
docker compose up
```

Cela lancera les services suivants :
- **Frontend** : Disponible sur `http://localhost:5010`
- **Backend** : Disponible sur `http://localhost:5009`
- **Auth** : Disponible sur `http://localhost:5002`

### Étape 3 : Accéder à l'application

Ouvrez un navigateur et rendez-vous à l'adresse suivante :

```
http://localhost:5010
```

Depuis cette interface, vous pouvez :
- Vous connecter avec vos identifiants (exemple : `alice/password`, `john/secret`).
- Rechercher des livres en fonction de leur titre ou des utilisateurs par nom.
- Visualiser les livres actuellement empruntés.

> **Note sur les mots de passe** : Les mots de passe des utilisateurs (`password` et `secret`) sont hachés dans la base de données à l'aide de bcrypt pour une sécurité optimale.

### Étape 4 : Arrêter les services

Pour arrêter les services, utilisez :

```bash
# Arrêter les services
docker compose down
```

## Structure des fichiers

```plaintext
|-- api/          # Code du Backend
|   |-- api.py    # Points d'entrée de l'API Backend
|   |-- Dockerfile
|-- auth/         # Service Auth pour l'authentification
|   |-- auth.py
|   |-- Dockerfile
|-- front/        # Frontend de l'application
|   |-- app.py
|   |-- templates/
|   |-- Dockerfile
|-- docker-compose.yml
```

## Notes importantes
1. **Authentification JWT** : Le service Auth gère l'authentification avec des tokens JWT. Les utilisateurs doivent fournir un jeton valide pour accéder aux services.
2. **Base de données** : Les fichiers `.db` sont inclus pour simuler une base de données locale.
3. **Dépendances Python** : Les fichiers `requirements.txt` dans chaque dossier définissent les dépendances nécessaires pour chaque microservice.

### Problèmes courants
- **Erreur "No such file or directory"** : Assurez-vous que tous les fichiers `Dockerfile` et `requirements.txt` sont présents dans les répertoires correspondants.
- **Ports déjà utilisés** : Vérifiez que les ports `5002`, `5009`, et `5010` ne sont pas occupés par d'autres applications.

Bon développement !

