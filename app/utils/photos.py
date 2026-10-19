"""Gestion des photos locales, sans toucher aux ressources de l'application."""
from pathlib import Path
import shutil
import tempfile

from app.config import paths


def checked_photo_path(path):
    path = Path(path)
    root = paths.IMAGES_DIR.resolve()
    if path.is_symlink() or path.parent.resolve() != root or not path.resolve().is_relative_to(root):
        raise ValueError("Le chemin de la photo sort du dossier des usagers.")
    return path


def photo_path(table, value):
    if value is None or not str(value).strip():
        return None
    key = str(value).strip()
    if table == 'owners':
        key = key.zfill(6)
    if any(char in key for char in '/\\:<>"|?*') or key in ('.', '..'):
        raise ValueError("Identifiant de photo invalide.")
    return checked_photo_path(paths.IMAGES_DIR / f'{key}.png')


class PhotoChange:
    """Préparer une copie, puis retirer l'ancienne après le commit SQL."""
    def __init__(self, source, destination=None):
        self.source = source
        self.destination = destination
        self.created = False

    def prepare(self):
        if self.source == self.destination:
            return
        if self.destination is not None:
            checked_photo_path(self.destination)
            if self.destination.exists():
                raise ValueError("Une photo existe déjà pour le nouvel identifiant. Elle ne sera pas écrasée.")
        if self.source is None or self.destination is None:
            return
        checked_photo_path(self.source)
        if not self.source.exists():
            return
        try:
            with self.source.open('rb') as original, self.destination.open('xb') as copied:
                self.created = True
                shutil.copyfileobj(original, copied)
        except OSError:
            self.rollback()
            raise

    def rollback(self):
        if self.created:
            checked_photo_path(self.destination).unlink(missing_ok=True)
            self.created = False

    def finish(self, still_referenced=False):
        if self.source is not None and self.source != self.destination and not still_referenced:
            checked_photo_path(self.source).unlink(missing_ok=True)


def save_photo_atomic(path, content):
    """Remplacer une photo uniquement une fois la nouvelle écriture terminée."""
    destination = checked_photo_path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix='.capture-', suffix='.png', delete=False) as output:
            temporary = Path(output.name)
            output.write(content)
        checked_photo_path(destination)
        temporary.replace(destination)
    finally:
        if temporary is not None:
            checked_photo_path(temporary).unlink(missing_ok=True)
