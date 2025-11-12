"""
Fenêtre principale de l'application avec navigation par onglets
"""
from tkinter import Tk, Frame, Menu, Button
from tkinter import ttk
from app.config import settings, theme, paths
from app.views.accueil_view import AccueilView
from app.views.dashboard_view import DashboardView
from app.views.historique_view import HistoriqueView
from app.views.owners_view import OwnersView
from app.views.user_management_view import UserManagementView
from app.views.connexion_dialog import ConnexionDialog


class MainWindow:
    """Fenêtre principale unique de l'application"""
    
    def __init__(self):
        self.root = Tk()
        self.root.title("ParkingApp - Gestion de Parking")
        self.root.geometry("1400x900")
        
        # Configuration de la fenêtre
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-zoomed', True)  # Linux
        
        self.root.config(bg=theme.Colors.BG_PRIMARY)
        
        # Variables - synchronisées avec settings
        self.current_user = settings.current_user
        self.is_connected = settings.is_connected
        
        # Configuration du style
        self.style = theme.Theme.configure_style()
        
        # Créer l'interface
        self._create_menu()
        self._create_main_container()
        self._create_status_bar()
        
        # Afficher la vue d'accueil par défaut
        self.show_accueil()
        
        # Gérer la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_menu(self):
        """Crée la barre de menu"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Quitter", command=self._on_closing)
        
        # Menu Navigation
        nav_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Navigation", menu=nav_menu)
        nav_menu.add_command(label="Accueil", command=self.show_accueil)
        nav_menu.add_command(label="Dashboard", command=self.show_dashboard)
        nav_menu.add_command(label="Historique", command=self.show_historique)
        nav_menu.add_command(label="Motos", command=self.show_owners)
        nav_menu.add_command(label="Utilisateurs", command=self.show_users)
        
        # Menu Aide
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self._show_about)
    
    def _create_main_container(self):
        """Crée le conteneur principal avec navigation"""
        # Frame principal
        main_frame = Frame(self.root, bg=theme.Colors.BG_PRIMARY)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de navigation latérale
        nav_frame = Frame(main_frame, bg=theme.Colors.BG_DARK, width=200)
        nav_frame.pack(side="left", fill="y", padx=(0, 10))
        nav_frame.pack_propagate(False)
        
        # Titre de navigation
        title_label = ttk.Label(
            nav_frame,
            text="ParkingApp",
            style="Title.TLabel",
            background=theme.Colors.BG_DARK,
            foreground=theme.Colors.TEXT_LIGHT,
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Boutons de navigation avec style amélioré
        nav_buttons = [
            ("🏠 Accueil", self.show_accueil),
            ("📊 Dashboard", self.show_dashboard),
            ("📜 Historique", self.show_historique),
            ("🏍️ Motos", self.show_owners),
            ("👥 Utilisateurs", self.show_users),
        ]
        
        self.nav_buttons = []
        for text, command in nav_buttons:
            btn_frame = Frame(nav_frame, bg=theme.Colors.BG_DARK)
            btn_frame.pack(pady=3, padx=10, fill="x")
            
            btn = Button(
                btn_frame,
                text=text,
                command=command,
                font=("Arial", 12, "bold"),
                bg=theme.Colors.PRIMARY,
                fg=theme.Colors.TEXT_LIGHT,
                activebackground=theme.Colors.PRIMARY_LIGHT,
                activeforeground=theme.Colors.TEXT_LIGHT,
                relief="flat",
                cursor="hand2",
                padx=15,
                pady=12,
                anchor="w"
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=theme.Colors.PRIMARY_LIGHT))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=theme.Colors.PRIMARY))
            self.nav_buttons.append(btn)
        
        # Bouton de connexion/déconnexion
        login_frame = Frame(nav_frame, bg=theme.Colors.BG_DARK)
        login_frame.pack(side="bottom", pady=20, padx=10, fill="x")
        
        self.login_btn = Button(
            login_frame,
            text="🔐 Connexion",
            command=self._toggle_login,
            font=("Arial", 12, "bold"),
            bg=theme.Colors.SUCCESS,
            fg=theme.Colors.TEXT_LIGHT,
            activebackground="#66bb6a",
            activeforeground=theme.Colors.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=12
        )
        self.login_btn.pack(fill="x")
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg="#66bb6a"))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=theme.Colors.SUCCESS))
        
        # Frame de contenu (zone principale)
        self.content_frame = Frame(main_frame, bg=theme.Colors.BG_SECONDARY, relief="flat")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Frame pour le contenu actuel
        self.current_view_frame = None
    
    def _create_status_bar(self):
        """Crée la barre de statut"""
        status_frame = Frame(self.root, bg=theme.Colors.BG_DARK, height=30)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Prêt",
            background=theme.Colors.BG_DARK,
            foreground=theme.Colors.TEXT_LIGHT,
            font=("Arial", 10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.user_label = ttk.Label(
            status_frame,
            text="Non connecté",
            background=theme.Colors.BG_DARK,
            foreground=theme.Colors.TEXT_LIGHT,
            font=("Arial", 10)
        )
        self.user_label.pack(side="right", padx=10, pady=5)
    
    def _clear_content(self):
        """Efface le contenu actuel"""
        if self.current_view_frame:
            self.current_view_frame.destroy()
        self.current_view_frame = Frame(self.content_frame, bg=theme.Colors.BG_SECONDARY)
        self.current_view_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_accueil(self):
        """Affiche la vue d'accueil"""
        self._clear_content()
        view = AccueilView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Accueil")
    
    def show_dashboard(self):
        """Affiche le dashboard"""
        if not self._check_permission("view_dashboard"):
            return
        self._clear_content()
        view = DashboardView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Dashboard")
    
    def show_historique(self):
        """Affiche l'historique"""
        self._clear_content()
        view = HistoriqueView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Historique")
    
    def show_owners(self):
        """Affiche la gestion des motos"""
        self._clear_content()
        view = OwnersView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Gestion des Motos")
    
    def show_users(self):
        """Affiche la gestion des utilisateurs"""
        if not self._check_permission("manage_users"):
            return
        self._clear_content()
        view = UserManagementView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Gestion des Utilisateurs")
    
    def _toggle_login(self):
        """Gère la connexion/déconnexion"""
        if settings.is_connected:
            if self._confirm_logout():
                self._logout()
        else:
            self._login()
    
    def _login(self):
        """Ouvre la fenêtre de connexion"""
        dialog = ConnexionDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
    
    def _logout(self):
        """Déconnecte l'utilisateur"""
        settings.logout()
        self.is_connected = settings.is_connected
        self.current_user = settings.current_user
        self.login_btn.config(text="🔐 Connexion", bg=theme.Colors.SUCCESS)
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg="#66bb6a"))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=theme.Colors.SUCCESS))
        self.user_label.config(text="Non connecté")
        self._update_status("Déconnecté")
        self.show_accueil()
    
    def _check_permission(self, permission):
        """Vérifie si l'utilisateur a la permission"""
        if not settings.is_connected:
            self._show_error("Vous devez être connecté pour accéder à cette fonctionnalité")
            return False
        if not settings.current_user.has_permission(permission):
            self._show_error("Vous n'avez pas les permissions nécessaires")
            return False
        return True
    
    def _confirm_logout(self):
        """Demande confirmation pour la déconnexion"""
        from tkinter import messagebox
        return messagebox.askyesno("Confirmation", "Voulez-vous vraiment vous déconnecter ?")
    
    def _show_error(self, message):
        """Affiche un message d'erreur"""
        from tkinter import messagebox
        messagebox.showerror("Erreur", message)
    
    def _show_about(self):
        """Affiche la fenêtre À propos"""
        from tkinter import messagebox
        messagebox.showinfo(
            "À propos",
            "ParkingApp v1.0.0\n\nApplication de gestion de parking\nDéveloppée avec Python et Tkinter"
        )
    
    def _update_status(self, message):
        """Met à jour le message de statut"""
        self.status_label.config(text=message)
    
    def _on_closing(self):
        """Gère la fermeture de l'application"""
        from tkinter import messagebox
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.root.destroy()
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

