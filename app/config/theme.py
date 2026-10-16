"""
Thème et couleurs de l'application
"""
from tkinter import ttk

# Palette de couleurs harmonisée
class Colors:
    """Couleurs principales de l'application"""
    # Couleurs principales
    PRIMARY = "#16566b"          # Bleu pétrole
    PRIMARY_LIGHT = "#206c83"
    PRIMARY_DARK = "#103f50"
    
    # Couleurs secondaires
    SECONDARY = "#35687c"
    ACCENT = "#087f8c"
    
    # Couleurs de fond
    BG_PRIMARY = "#eef3f6"        # Fond principal
    BG_SECONDARY = "#ffffff"      # Fond secondaire (blanc)
    BG_DARK = "#172f3d"
    BG_DARKER = "#10232e"
    BG_MUTED = "#e8eff3"
    NAV_HOVER = "#244757"
    NAV_SELECTED = "#16566b"
    
    # Couleurs de texte
    TEXT_PRIMARY = "#182f3d"
    TEXT_SECONDARY = "#526574"
    TEXT_LIGHT = "#ffffff"        # Texte clair (blanc)
    
    # Couleurs d'état
    SUCCESS = "#23734b"
    SUCCESS_HOVER = "#1c603e"
    WARNING = "#945000"
    WARNING_HOVER = "#783f00"
    ERROR = "#b3313d"
    ERROR_HOVER = "#942733"
    INFO = "#216c9b"
    
    # Couleurs de boutons
    BTN_PRIMARY = PRIMARY
    BTN_SECONDARY = SECONDARY
    BTN_SUCCESS = SUCCESS
    BTN_DANGER = ERROR
    BTN_WARNING = WARNING
    
    # Couleurs de bordure
    BORDER = "#cedbe3"
    BORDER_DARK = "#a1b3bf"


FONT_FAMILY = "Segoe UI"


class Theme:
    """Gestion du thème de l'application"""
    
    @staticmethod
    def configure_style(master=None):
        """Configure le style ttk de l'application"""
        style = ttk.Style(master)
        # Le thème natif Windows peut ignorer les fonds personnalisés.
        # Choisir le thème avant de définir les styles et leurs états.
        style.theme_use("clam")
        style.configure(".", font=(FONT_FAMILY, 11),
                        background=Colors.BG_SECONDARY,
                        foreground=Colors.TEXT_PRIMARY)

        for name, base, hover, pressed in (
            ("TButton", Colors.PRIMARY, Colors.PRIMARY_LIGHT, Colors.PRIMARY_DARK),
            ("Primary.TButton", Colors.PRIMARY, Colors.PRIMARY_LIGHT, Colors.PRIMARY_DARK),
            ("Success.TButton", Colors.SUCCESS, Colors.SUCCESS_HOVER, Colors.SUCCESS_HOVER),
            ("Danger.TButton", Colors.ERROR, Colors.ERROR_HOVER, Colors.ERROR_HOVER),
            ("Secondary.TButton", Colors.BG_MUTED, Colors.BORDER, Colors.BORDER_DARK),
        ):
            text_color = Colors.TEXT_PRIMARY if name == "Secondary.TButton" else Colors.TEXT_LIGHT
            style.configure(name, background=base, foreground=text_color,
                            bordercolor=base, lightcolor=base, darkcolor=base,
                            padding=(16, 10), font=(FONT_FAMILY, 10, "bold"),
                            relief="flat", borderwidth=1, anchor="center",
                            focuscolor=text_color, focusthickness=1)
            style.map(name,
                      background=[("disabled", Colors.BG_MUTED), ("pressed", pressed), ("active", hover)],
                      foreground=[("disabled", Colors.TEXT_SECONDARY), ("!disabled", text_color)],
                      bordercolor=[("focus", Colors.ACCENT), ("!focus", base)],
                      lightcolor=[("pressed", pressed), ("active", hover)],
                      darkcolor=[("pressed", pressed), ("active", hover)])
        
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
            font=(FONT_FAMILY, 22, "bold")
        )
        
        style.configure(
            "Heading.TLabel",
            background=Colors.BG_SECONDARY,
            foreground=Colors.PRIMARY,
            font=(FONT_FAMILY, 14, "bold")
        )
        
        # Style pour les Entry
        style.configure(
            "Modern.TEntry",
            fieldbackground=Colors.BG_SECONDARY,
            foreground=Colors.TEXT_PRIMARY,
            insertcolor=Colors.TEXT_PRIMARY,
            bordercolor=Colors.BORDER_DARK,
            lightcolor=Colors.BORDER_DARK,
            darkcolor=Colors.BORDER_DARK,
            borderwidth=1,
            relief="flat",
            padding=10
        )
        style.map("Modern.TEntry",
                  bordercolor=[("focus", Colors.PRIMARY)],
                  lightcolor=[("focus", Colors.PRIMARY)],
                  darkcolor=[("focus", Colors.PRIMARY)])

        style.configure("Treeview", background=Colors.BG_SECONDARY,
                        fieldbackground=Colors.BG_SECONDARY,
                        foreground=Colors.TEXT_PRIMARY, rowheight=36,
                        font=(FONT_FAMILY, 10), bordercolor=Colors.BORDER,
                        lightcolor=Colors.BORDER, darkcolor=Colors.BORDER,
                        borderwidth=1, relief="flat")
        style.map("Treeview", background=[("selected", Colors.PRIMARY)],
                  foreground=[("selected", Colors.TEXT_LIGHT)])
        style.configure("Treeview.Heading", background=Colors.BG_MUTED,
                        foreground=Colors.TEXT_PRIMARY,
                        font=(FONT_FAMILY, 10, "bold"), padding=(10, 12),
                        relief="flat", borderwidth=1,
                        bordercolor=Colors.BORDER, lightcolor=Colors.BG_MUTED,
                        darkcolor=Colors.BG_MUTED)
        style.map("Treeview.Heading", background=[("active", Colors.BORDER)])
        style.configure("Vertical.TScrollbar", background=Colors.BORDER_DARK,
                        troughcolor=Colors.BG_PRIMARY, borderwidth=0, arrowsize=14)
        style.configure("Horizontal.TScrollbar", background=Colors.BORDER_DARK,
                        troughcolor=Colors.BG_PRIMARY, borderwidth=0, arrowsize=14)
        
        return style

