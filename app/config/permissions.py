"""Droits de la session courante, partagés par les vues et leurs actions."""
from functools import wraps

from app.config import settings


def has_permission(permission):
    if not settings.is_connected:
        return permission in {"scan_entries", "scan_exits"}
    return bool(settings.current_user
                and settings.current_user.has_permission(permission))


def requires_permission(permission):
    def decorate(action):
        @wraps(action)
        def guarded(self, *args, **kwargs):
            if not has_permission(permission):
                self.main_window._update_status("Action non autorisée pour ce compte.")
                return False
            return action(self, *args, **kwargs)
        return guarded
    return decorate
