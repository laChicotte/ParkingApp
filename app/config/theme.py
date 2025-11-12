"""
Thème et couleurs de l'application
"""
from tkinter import ttk

# Palette de couleurs harmonisée
class Colors:
    """Couleurs principales de l'application"""
    # Couleurs principales
    PRIMARY = "#1a237e"          # Bleu foncé principal
    PRIMARY_LIGHT = "#3949ab"     # Bleu clair
    PRIMARY_DARK = "#0d47a1"      # Bleu très foncé
    
    # Couleurs secondaires
    SECONDARY = "#1565c0"         # Bleu moyen
    ACCENT = "#00acc1"            # Cyan accent
    
    # Couleurs de fond
    BG_PRIMARY = "#f5f5f5"        # Fond principal (gris clair)
    BG_SECONDARY = "#ffffff"      # Fond secondaire (blanc)
    BG_DARK = "#263238"           # Fond sombre
    BG_DARKER = "#1a1a1a"         # Fond très sombre
    
    # Couleurs de texte
    TEXT_PRIMARY = "#212121"      # Texte principal (gris foncé)
    TEXT_SECONDARY = "#757575"    # Texte secondaire (gris)
    TEXT_LIGHT = "#ffffff"        # Texte clair (blanc)
    
    # Couleurs d'état
    SUCCESS = "#4caf50"           # Vert (succès)
    WARNING = "#ff9800"           # Orange (avertissement)
    ERROR = "#f44336"             # Rouge (erreur)
    INFO = "#2196f3"              # Bleu (information)
    
    # Couleurs de boutons
    BTN_PRIMARY = "#1a237e"       # Bouton principal
    BTN_SECONDARY = "#3949ab"     # Bouton secondaire
    BTN_SUCCESS = "#4caf50"       # Bouton succès
    BTN_DANGER = "#f44336"        # Bouton danger
    BTN_WARNING = "#ff9800"       # Bouton avertissement
    
    # Couleurs de bordure
    BORDER = "#e0e0e0"            # Bordure claire
    BORDER_DARK = "#bdbdbd"       # Bordure foncée


class Theme:
    """Gestion du thème de l'application"""
    
    @staticmethod
    def configure_style():
        """Configure le style ttk de l'application"""
        style = ttk.Style()
        
        # Style pour les boutons
        style.configure(
            "Primary.TButton",
            background=Colors.BTN_PRIMARY,
            foreground=Colors.TEXT_LIGHT,
            padding=10,
            font=("Arial", 11, "bold")
        )
        
        style.map(
            "Primary.TButton",
            background=[("active", Colors.PRIMARY_LIGHT), ("pressed", Colors.PRIMARY_DARK)]
        )
        
        style.configure(
            "Success.TButton",
            background=Colors.BTN_SUCCESS,
            foreground=Colors.TEXT_LIGHT,
            padding=10,
            font=("Arial", 11, "bold")
        )
        
        style.map(
            "Success.TButton",
            background=[("active", "#66bb6a"), ("pressed", "#388e3c")]
        )
        
        style.configure(
            "Danger.TButton",
            background=Colors.BTN_DANGER,
            foreground=Colors.TEXT_LIGHT,
            padding=10,
            font=("Arial", 11, "bold")
        )
        
        style.map(
            "Danger.TButton",
            background=[("active", "#ef5350"), ("pressed", "#d32f2f")]
        )
        
        # Style pour les frames
        style.configure(
            "Card.TFrame",
            background=Colors.BG_SECONDARY,
            relief="flat"
        )
        
        style.configure(
            "Dark.TFrame",
            background=Colors.BG_DARK,
            relief="flat"
        )
        
        # Style pour les labels
        style.configure(
            "Title.TLabel",
            background=Colors.BG_SECONDARY,
            foreground=Colors.TEXT_PRIMARY,
            font=("Arial", 18, "bold")
        )
        
        style.configure(
            "Heading.TLabel",
            background=Colors.BG_SECONDARY,
            foreground=Colors.PRIMARY,
            font=("Arial", 14, "bold")
        )
        
        # Style pour les Entry
        style.configure(
            "Modern.TEntry",
            fieldbackground=Colors.BG_SECONDARY,
            borderwidth=2,
            relief="solid",
            padding=8
        )
        
        return style

