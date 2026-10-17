"""Retour sonore asynchrone du lecteur, sans attente dans l'interface."""
try:
    import winsound
except ImportError:
    winsound = None


def play_scan_sound(success, widget):
    if winsound is not None:
        try:
            winsound.PlaySound("SystemAsterisk" if success else "SystemHand",
                              winsound.SND_ALIAS | winsound.SND_ASYNC)
            return
        except RuntimeError:
            pass
    widget.bell()
