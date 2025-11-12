"""
Point d'entrée principal de l'application ParkingApp
"""
import os

# Supprimer l'avertissement Qt/Wayland d'OpenCV
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''

from app.core.main_window import MainWindow
from app.config import paths


def main():
    """Fonction principale de l'application"""
    # S'assurer que les répertoires existent
    paths.ensure_directories()
    
    # Créer et lancer la fenêtre principale
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
