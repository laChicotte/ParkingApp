"""
Gestion centralisée des chemins de l'application
"""
import os
import sys
from pathlib import Path

# Chemin de base du projet (2 niveaux au-dessus de ce fichier)
IS_FROZEN = bool(getattr(sys, "frozen", False))
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent.parent))
DATA_DIR = (Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            / "UKAG Parking") if IS_FROZEN else BASE_DIR

# Chemins des ressources
RESOURCES_DIR = BASE_DIR / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
IMAGES_DIR = DATA_DIR / "images" if IS_FROZEN else RESOURCES_DIR / "images"
CONFIG_DIR = DATA_DIR / "config" if IS_FROZEN else RESOURCES_DIR / "config"
EXPORTS_DIR = DATA_DIR / "exports" if IS_FROZEN else BASE_DIR
LOGS_DIR = DATA_DIR / "logs" if IS_FROZEN else BASE_DIR / "build" / "logs"

# Fichiers de configuration
CONFIG_FILE = CONFIG_DIR / "config.json"

# Chemins des images spécifiques
LOGO_PATH = next(
    (path for path in (BASE_DIR / "logo.png", BASE_DIR / "logo.jpg", RESOURCES_DIR / "logo.png")
     if path.is_file()),
    RESOURCES_DIR / "logo.png",
)
PROFIL_PATH = RESOURCES_DIR / "profil.jpeg"
BG_PATH = RESOURCES_DIR / "ukag_bg.png"

# Base de données SQLite
DB_FILE = DATA_DIR / "parking.db"


def get_icon_path(icon_name):
    """Retourne le chemin complet d'une icône"""
    return ICONS_DIR / icon_name


def get_image_path(image_name):
    """Retourne le chemin d'une photo dans le dossier central des images."""
    return IMAGES_DIR / image_name


def get_image_save_path(image_name):
    """Les nouvelles captures sont toujours enregistrées dans resources/images."""
    return IMAGES_DIR / image_name


def ensure_directories():
    """Crée les répertoires s'ils n'existent pas"""
    if not IS_FROZEN:
        ICONS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

