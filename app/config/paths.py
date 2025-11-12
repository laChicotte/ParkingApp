"""
Gestion centralisée des chemins de l'application
"""
import os
from pathlib import Path

# Chemin de base du projet (2 niveaux au-dessus de ce fichier)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Chemins des ressources
RESOURCES_DIR = BASE_DIR / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
IMAGES_DIR = RESOURCES_DIR / "images"
CONFIG_DIR = RESOURCES_DIR / "config"

# Fichiers de configuration
CONFIG_FILE = CONFIG_DIR / "config.json"

# Chemins des images spécifiques
LOGO_PATH = RESOURCES_DIR / "logo.png"
PROFIL_PATH = RESOURCES_DIR / "profil.jpeg"
BG_PATH = RESOURCES_DIR / "ukag_bg.png"

# Base de données SQLite
DB_FILE = BASE_DIR / "parking.db"


def get_icon_path(icon_name):
    """Retourne le chemin complet d'une icône"""
    return ICONS_DIR / icon_name


def get_image_path(image_name):
    """Retourne le chemin complet d'une image"""
    return IMAGES_DIR / image_name


def ensure_directories():
    """Crée les répertoires s'ils n'existent pas"""
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

