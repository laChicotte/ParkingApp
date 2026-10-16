# ParkingApp - Application de Gestion de Parking

Application de gestion de parking développée en Python avec Tkinter pour l'interface graphique.

## 📁 Structure du Projet

```
ParkingApp/
├── app/                    # Code source de l'application
│   ├── config/            # Configuration et paramètres
│   │   ├── settings.py    # Variables globales et état de l'application
│   │   └── paths.py       # Gestion centralisée des chemins
│   ├── database/          # Modules de base de données
│   │   ├── mysql.py       # Connexion MySQL/MariaDB
│   │   └── sqlite.py      # Ancien module SQLite
│   ├── models/            # Modèles de données
│   │   └── user.py        # Modèle utilisateur
│   ├── views/             # Interfaces utilisateur (GUI)
│   │   ├── accueil.py     # Page d'accueil
│   │   ├── connexion.py   # Fenêtre de connexion
│   │   ├── dashboard.py   # Tableau de bord
│   │   ├── historique.py  # Historique des entrées/sorties
│   │   ├── owners.py      # Gestion des propriétaires
│   │   └── user_management.py  # Gestion des utilisateurs
│   ├── utils/             # Utilitaires et fonctions helper
│   │   └── fonctions.py   # Fonctions utilitaires
│   └── main.py            # Point d'entrée principal
├── resources/             # Ressources de l'application
│   ├── icons/            # Icônes de l'interface
│   ├── images/           # Images des propriétaires
│   └── config/           # Fichiers de configuration
│       └── config.json.template  # Template de configuration MySQL
├── requirements.txt       # Dépendances Python
├── run.py                # Script de lancement
└── README.md             # Ce fichier
```

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**

2. **Créer un environnement virtuel** (recommandé)
   ```bash
   python3 -m venv env
   source env/bin/activate  # Sur Linux/Mac
   # ou
   env\Scripts\activate  # Sur Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Installer python3-tk** (pour l'interface graphique)
   ```bash
   sudo apt install python3-tk  # Sur Ubuntu/Debian
   ```

## 🎯 Utilisation

### Lancement de l'application

```bash
python3 run.py
```

Ou directement :
```bash
python3 -m app.main
```

### Configuration de la base de données

L'application utilise **MySQL/MariaDB** via le point d'accès commun `app.database`. Elle lit les identifiants dans `resources/config/config.json`, ignoré par Git.

Pour préparer la connexion :

1. Copier le template de configuration :
   ```bash
   cp resources/config/config.json.template resources/config/config.json
   ```

2. Modifier `resources/config/config.json` avec vos paramètres :
   ```json
   {
       "host": "127.0.0.1",
       "port": 3306,
       "user": "parkingapp",
       "password": "votre_mot_de_passe",
       "db_name": "parkingapp"
   }
   ```

3. Démarrer MySQL avant l'application. La base configurée doit déjà exister et l'utilisateur doit pouvoir y créer les tables.

4. Depuis PowerShell, à la racine de ParkingApp :
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe run.py
   ```

Au démarrage, les tables `users`, `owners` et `historique` sont créées si elles n'existent pas. Si la configuration ou la connexion échoue, le lancement s'arrête avec une erreur dans le terminal. L'application ne revient pas automatiquement à SQLite.

Les anciennes données de `parking.db` ne sont pas transférées automatiquement. Les identifiants MySQL donnent accès au serveur de base de données ; les comptes de connexion à ParkingApp sont stockés séparément dans `users`.

### Import d'un ancien dump phpMyAdmin

Le script importe les données de `users`, `owners` et `historique` dans les tables existantes. Il exige des tables vides, conserve les identifiants et les mots de passe hachés, et vérifie le contenu avant de valider la transaction. Les instructions de structure du dump ne sont pas exécutées.

Analyser le fichier sans toucher à la base :

```powershell
.\.venv\Scripts\python.exe scripts\import_mysql_dump.py "D:\mybase.sql"
```

Effectuer l'import :

```powershell
.\.venv\Scripts\python.exe scripts\import_mysql_dump.py "D:\mybase.sql" --apply
```

Les dates anciennes à `0000-00-00` sont conservées comme dates inconnues. Elles ne contribuent pas aux statistiques par jour. Après l'import, utilisez les comptes ParkingApp de l'ancienne base et leurs mots de passe habituels.

### Ancien utilisateur par défaut (SQLite)

L'ancien module SQLite créait automatiquement cet administrateur, qui n'est pas créé dans MySQL :
- **Username :** `admin`
- **Password :** `admin`

⚠️ **Important :** Changez le mot de passe après la première connexion !

## 📦 Dépendances

### Version Windows installable

L'installateur est généré dans `dist/installer/UKAGParking-Setup-1.0.1-x64.exe`.
Il inclut Python et les dépendances de l'application. Sur chaque poste Windows
64 bits, démarrer MySQL dans XAMPP puis lancer UKAG Parking. Le premier lancement
propose la configuration MySQL et la création d'un administrateur pour une base vide.

La version installée conserve ses paramètres, photos et exports dans
`%LOCALAPPDATA%\UKAG Parking`, indépendamment du dossier du programme. Les données
MySQL et les photos existantes doivent être transférées séparément. Voir
[`installer/INSTALLATION-WINDOWS.txt`](installer/INSTALLATION-WINDOWS.txt).

Pour reconstruire l'exécutable et l'installateur :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1 -Installer
```

Le compilateur Inno Setup 6 doit être disponible. On peut préciser son chemin avec
`-InnoCompiler "C:\chemin\ISCC.exe"`. La compilation n'embarque ni `config.json`,
ni la base SQLite, ni les photos des usagers.

- `bcrypt` - Hachage de mots de passe
- `Pillow` - Traitement d'images
- `matplotlib` - Graphiques et visualisation
- `opencv-python` - Capture vidéo/webcam
- `pymysql[rsa]` - Connexion MySQL/MariaDB et authentification MySQL 8

## 🔧 Fonctionnalités

- ✅ Gestion des entrées/sorties de véhicules
- ✅ Scan de codes-barres
- ✅ Gestion des propriétaires de véhicules
- ✅ Historique des mouvements
- ✅ Tableau de bord avec statistiques
- ✅ Gestion des utilisateurs et permissions
- ✅ Capture de photos via webcam
- ✅ Export des données en HTML

## 📝 Notes

- L'application crée automatiquement les tables nécessaires dans la base de données
- Les images sont stockées dans `resources/images/`
- Les icônes sont dans `resources/icons/`

## 🐛 Dépannage

### Erreur "No module named tkinter"
Installez python3-tk :
```bash
sudo apt install python3-tk
```

### Erreur de connexion à la base de données
- Vérifiez que MySQL/MariaDB est démarré (si vous utilisez MySQL)
- Vérifiez les paramètres dans `resources/config/config.json`
- Assurez-vous que la base de données existe

## 📄 Licence

Ce projet est sous licence **MIT - Educational and Research Use Only**.

**Utilisation autorisée :**
- ✅ Apprentissage et enseignement
- ✅ Recherche académique
- ✅ Étude personnelle et expérimentation
- ✅ Examen du code à des fins éducatives

**Utilisation interdite :**
- ❌ Vente ou location du logiciel
- ❌ Utilisation dans des produits ou services commerciaux
- ❌ Toute utilisation à but lucratif

Voir le fichier [LICENSE](LICENSE) pour plus de détails.

**Développeur :** Elhadj Ibrahima Barry  
**Institution :** Université Kofi Annan de Guinée

