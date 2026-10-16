"""Identité commune de l'application de gestion du parking de l'UKAG."""
import base64
import mimetypes

from PIL import Image, ImageTk

from app.config import paths

APP_NAME = "UKAG Parking"
APP_VERSION = "1.0.1"
UNIVERSITY_NAME = "Université Kofi Annan de Guinée"
SERVICE_NAME = "Gestion du parking universitaire"


def load_logo(master, size=(80, 80)):
    """Dimensionne le logo sans le déformer ; le widget garde sa référence."""
    try:
        with Image.open(paths.LOGO_PATH) as source:
            image = source.convert("RGBA")
            image.thumbnail(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image, master=master)
    except OSError:
        return None


def logo_data_uri():
    """Embarque le logo dans les exports pour conserver leur autonomie."""
    if not paths.LOGO_PATH.is_file():
        return ""
    mime = mimetypes.guess_type(paths.LOGO_PATH.name)[0] or "image/png"
    encoded = base64.b64encode(paths.LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"
