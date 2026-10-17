"""
Point d'entrée principal de l'application ParkingApp
"""
import os

# Supprimer l'avertissement Qt/Wayland d'OpenCV
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''

from app.core.main_window import MainWindow
from app.config import paths
from app.database import Bdonnee
from pymysql import MySQLError


def main():
    """Fonction principale de l'application"""
    # S'assurer que les répertoires existent
    paths.ensure_directories()

    # Préparer MySQL avant d'ouvrir l'accueil, qui n'effectue aucune requête.
    try:
        Bdonnee()
    except (OSError, ValueError, TypeError, MySQLError, RuntimeError) as error:
        print(f"Démarrage impossible : {error}")
        print("Vérifiez MySQL et resources/config/config.json.")
        raise SystemExit(1) from None
    
    # Créer et lancer la fenêtre principale
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
