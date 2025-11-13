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
│   │   └── sqlite.py      # Connexion SQLite (par défaut)
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

L'application utilise **SQLite par défaut** (aucune configuration requise). La base de données sera créée automatiquement dans `parking.db`.

Pour utiliser **MySQL/MariaDB** :

1. Copier le template de configuration :
   ```bash
   cp resources/config/config.json.template resources/config/config.json
   ```

2. Modifier `resources/config/config.json` avec vos paramètres :
   ```json
   {
       "host": "localhost",
       "user": "root",
       "password": "votre_mot_de_passe",
       "db_name": "parking_db"
   }
   ```

3. Changer les imports dans les fichiers de vues :
   - Remplacer `from app.database.sqlite import Bdonnee` 
   - Par `from app.database.mysql import Bdonnee`

### Utilisateur par défaut (SQLite)

Lors du premier lancement avec SQLite, un utilisateur administrateur est créé automatiquement :
- **Username :** `admin`
- **Password :** `admin`

⚠️ **Important :** Changez le mot de passe après la première connexion !

## 📦 Dépendances

- `bcrypt` - Hachage de mots de passe
- `Pillow` - Traitement d'images
- `matplotlib` - Graphiques et visualisation
- `opencv-python` - Capture vidéo/webcam
- `pymysql` - (Optionnel) Pour MySQL/MariaDB

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

