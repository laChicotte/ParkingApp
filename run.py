#!/usr/bin/env python3
"""
Script de lancement de l'application ParkingApp
"""
import sys
import os
from pathlib import Path

# Supprimer l'avertissement Qt/Wayland d'OpenCV
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Lancer l'application
from app.main import main

if __name__ == "__main__":
    main()

