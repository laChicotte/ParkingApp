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

def bundled_self_test(output):
    """Diagnostic de distribution sans fenêtre, connexion SQL ni donnée privée."""
    import json
    import struct
    import tkinter
    import bcrypt
    import cv2
    import cryptography
    import pymysql
    from PIL import Image
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from app.config import paths
    from app.core.main_window import MainWindow
    from app.config.installation import configure_database
    with Image.open(paths.LOGO_PATH) as logo:
        logo.verify()
    with Image.open(paths.PROFIL_PATH) as profile:
        profile.verify()
    assert paths.get_icon_path("enter.jpeg").is_file()
    figure = Figure()
    figure.subplots().bar([1, 2], [2, 1])
    FigureCanvasAgg(figure).draw()
    result = {"ok": True, "frozen": paths.IS_FROZEN, "bits": struct.calcsize('P') * 8,
              "app_data": str(paths.DATA_DIR), "config_file": str(paths.CONFIG_FILE),
              "images_dir": str(paths.IMAGES_DIR), "tcl": tkinter.Tcl().eval('info patchlevel'),
              "opencv": cv2.__version__, "cryptography": cryptography.__version__}
    Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--self-test":
        bundled_self_test(sys.argv[2])
    else:
        if getattr(sys, "frozen", False):
            import logging
            from tkinter import messagebox
            from app.config import paths
            paths.LOGS_DIR.mkdir(parents=True, exist_ok=True)
            logging.basicConfig(filename=paths.LOGS_DIR / "application.log", level=logging.ERROR,
                                encoding="utf-8", format="%(asctime)s %(levelname)s %(message)s")
            try:
                from app.main import main
                main()
            except Exception:
                logging.exception("Erreur au lancement")
                messagebox.showerror("UKAG Parking", f"Le lancement a échoué. Consultez le journal :\n{paths.LOGS_DIR / 'application.log'}")
                raise SystemExit(1)
        else:
            from app.main import main
            main()

