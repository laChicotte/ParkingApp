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
from app.config.installation import configure_database, create_first_admin


def main():
    """Fonction principale de l'application"""
    # S'assurer que les répertoires existent
    paths.ensure_directories()

    if paths.IS_FROZEN and not paths.CONFIG_FILE.exists():
        if not configure_database():
            return
    # Préparer MySQL avant d'ouvrir l'accueil, qui n'effectue aucune requête.
    while True:
        try:
            database = Bdonnee()
            break
        except (OSError, ValueError, TypeError, MySQLError, RuntimeError) as error:
            if paths.IS_FROZEN:
                if configure_database(error=error):
                    continue
                return
            print(f"Démarrage impossible : {error}")
            print("Vérifiez MySQL et resources/config/config.json.")
            raise SystemExit(1) from None
    if paths.IS_FROZEN and not create_first_admin(database):
        return
    
    # Créer et lancer la fenêtre principale
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
