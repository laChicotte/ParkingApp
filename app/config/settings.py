"""
Configuration et variables globales de l'application
"""
from app.models.user import User

# État de connexion
is_connected = False

# Variable de navigation (test)
test = 0

# Utilisateur actuel
current_user = User()


def logout():
    """Déconnecte l'utilisateur et réinitialise les variables globales."""
    global current_user, is_connected, test
    current_user = User()  # Réinitialise l'utilisateur
    is_connected = False   # Marque comme déconnecté
    test = 0              # Force le retour à l'accueil
