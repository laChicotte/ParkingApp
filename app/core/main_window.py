"""
Fenêtre principale de l'application avec navigation par onglets
"""
from tkinter import Tk, Frame, Menu, Button, Label
from tkinter import ttk
from app.config import settings, theme, paths, branding
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
        self.root.title(f"{branding.APP_NAME} — {branding.UNIVERSITY_NAME}")
        self.window_icon = branding.load_logo(self.root, (48, 48))
        if self.window_icon:
            self.root.iconphoto(True, self.window_icon)
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)
        self.root.option_add("*Font", (theme.FONT_FAMILY, 11))
        
        # Configuration de la fenêtre
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-zoomed', True)  # Linux
        
        self.root.config(bg=theme.Colors.BG_PRIMARY)
        
        # Gérer la fermeture de l'application
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Variables - synchronisées avec settings
        self.current_user = settings.current_user
        self.is_connected = settings.is_connected
        
        # Configuration du style
        self.style = theme.Theme.configure_style(self.root)
        
        # Créer l'interface
        self._create_menu()
        self._create_status_bar()
        self._create_main_container()
        
        # Afficher la vue d'accueil par défaut
        self.show_accueil()
    
    def _create_menu(self):
        """Crée la barre de menu"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Configurer MySQL / XAMPP", command=self._configure_database)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self._on_closing)
        
        # Menu Navigation
        nav_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Navigation", menu=nav_menu)
        nav_menu.add_command(label="Accueil", command=self.show_accueil)
        nav_menu.add_command(label="Tableau de bord", command=self.show_dashboard)
        nav_menu.add_command(label="Historique", command=self.show_historique)
        nav_menu.add_command(label="Usagers et motos", command=self.show_owners)
        nav_menu.add_command(label="Comptes d'accès", command=self.show_users)
        
        # Menu Aide
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Guide utilisateur", command=self._show_guide)
        help_menu.add_separator()
        help_menu.add_command(label="À propos", command=self._show_about)
    
    def _configure_database(self):
        from app.config.installation import configure_database
        from tkinter import messagebox
        if configure_database(self.root):
            messagebox.showinfo("Configuration enregistrée", "Relancez UKAG Parking pour utiliser cette connexion.", parent=self.root)
            self.root.destroy()

    def _create_main_container(self):
        """Crée le conteneur principal avec navigation"""
        # Frame principal
        main_frame = Frame(self.root, bg=theme.Colors.BG_PRIMARY)
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Frame de navigation latérale
        nav_frame = Frame(main_frame, bg=theme.Colors.BG_DARK, width=215)
        nav_frame.pack(side="left", fill="y", padx=(0, 16))
        nav_frame.pack_propagate(False)
        
        # Titre de navigation
        self.sidebar_logo = branding.load_logo(nav_frame, (84, 84))
        if self.sidebar_logo:
            logo_label = Label(nav_frame, image=self.sidebar_logo,
                               bg=theme.Colors.BG_SECONDARY, padx=5, pady=5)
            logo_label.pack(anchor="w", padx=20, pady=(20, 0))
        title_label = ttk.Label(
            nav_frame,
            text=branding.APP_NAME,
            style="Title.TLabel",
            background=theme.Colors.BG_DARK,
            foreground=theme.Colors.TEXT_LIGHT,
            font=(theme.FONT_FAMILY, 18, "bold")
        )
        title_label.pack(anchor="w", padx=20, pady=(12, 4))
        Label(nav_frame, text="Gestion du parking",
              font=(theme.FONT_FAMILY, 10), bg=theme.Colors.BG_DARK,
              fg="#bdcfd9").pack(anchor="w", padx=20, pady=(0, 28))
        
        # Boutons de navigation avec style amélioré
        nav_buttons = [
            ("Accueil", self.show_accueil),
            ("Tableau de bord", self.show_dashboard),
            ("Historique", self.show_historique),
            ("Usagers et motos", self.show_owners),
            ("Comptes d'accès", self.show_users),
        ]
        
        self.nav_buttons = []
        self.active_nav = None
        for text, command in nav_buttons:
            btn_frame = Frame(nav_frame, bg=theme.Colors.BG_DARK)
            btn_frame.pack(pady=3, padx=10, fill="x")
            
            btn = Button(
                btn_frame,
                text=text,
                command=command,
                font=(theme.FONT_FAMILY, 11, "bold"),
                bg=theme.Colors.BG_DARK,
                fg=theme.Colors.TEXT_LIGHT,
                activebackground=theme.Colors.NAV_HOVER,
                activeforeground=theme.Colors.TEXT_LIGHT,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=theme.Colors.BG_DARK,
                highlightcolor=theme.Colors.ACCENT,
                cursor="hand2",
                padx=15,
                pady=12,
                anchor="w"
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=theme.Colors.NAV_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.config(
                bg=theme.Colors.NAV_SELECTED if b.cget("text") == self.active_nav else theme.Colors.BG_DARK))
            self.nav_buttons.append(btn)
        
        # Bouton de connexion/déconnexion
        login_frame = Frame(nav_frame, bg=theme.Colors.BG_DARK)
        login_frame.pack(side="bottom", pady=20, padx=10, fill="x")
        
        self.login_btn = Button(
            login_frame,
            text="Connexion",
            command=self._toggle_login,
            font=(theme.FONT_FAMILY, 12, "bold"),
            bg=theme.Colors.SUCCESS,
            fg=theme.Colors.TEXT_LIGHT,
            activebackground=theme.Colors.SUCCESS_HOVER,
            activeforeground=theme.Colors.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=12
        )
        self.login_btn.pack(fill="x")
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=theme.Colors.SUCCESS_HOVER))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=theme.Colors.SUCCESS))
        
        # Frame de contenu (zone principale)
        content_shell = Frame(main_frame, bg=theme.Colors.BG_SECONDARY)
        content_shell.pack(side="right", fill="both", expand=True)
        university_header = Frame(content_shell, bg=theme.Colors.BG_SECONDARY)
        university_header.pack(fill="x", padx=24, pady=(16, 0))
        self.header_logo = branding.load_logo(university_header, (48, 48))
        if self.header_logo:
            Label(university_header, image=self.header_logo,
                  bg=theme.Colors.BG_SECONDARY).pack(side="left", padx=(0, 12))
        header_text = Frame(university_header, bg=theme.Colors.BG_SECONDARY)
        header_text.pack(side="left", fill="x", expand=True)
        Label(header_text, text=branding.UNIVERSITY_NAME,
              font=(theme.FONT_FAMILY, 13, "bold"), bg=theme.Colors.BG_SECONDARY,
              fg=theme.Colors.TEXT_PRIMARY).pack(anchor="w")
        self.section_label = Label(header_text, text=branding.SERVICE_NAME,
                                   font=(theme.FONT_FAMILY, 10), bg=theme.Colors.BG_SECONDARY,
                                   fg=theme.Colors.TEXT_SECONDARY)
        self.section_label.pack(anchor="w", pady=(2, 0))
        Frame(content_shell, bg=theme.Colors.BORDER, height=1).pack(fill="x", padx=24, pady=(12, 0))
        self.content_frame = Frame(content_shell, bg=theme.Colors.BG_SECONDARY, relief="flat")
        self.content_frame.pack(fill="both", expand=True)
        
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
            font=(theme.FONT_FAMILY, 10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.user_label = ttk.Label(
            status_frame,
            text="Non connecté",
            background=theme.Colors.BG_DARK,
            foreground=theme.Colors.TEXT_LIGHT,
            font=(theme.FONT_FAMILY, 10)
        )
        self.user_label.pack(side="right", padx=10, pady=5)
    
    def _clear_content(self):
        """Efface le contenu actuel"""
        if self.current_view_frame:
            self.current_view_frame.destroy()
        self.current_view_frame = Frame(self.content_frame, bg=theme.Colors.BG_SECONDARY)
        self.current_view_frame.pack(fill="both", expand=True, padx=16, pady=16)

    def _select_navigation(self, label):
        """Indique la section ouverte, y compris après navigation par le menu."""
        self.active_nav = label
        self.section_label.config(text=f"{branding.SERVICE_NAME} / {label}")
        self.root.title(f"{branding.APP_NAME} — {label}")
        for button in self.nav_buttons:
            selected = button.cget("text") == label
            button.config(bg=theme.Colors.NAV_SELECTED if selected else theme.Colors.BG_DARK)
    
    def show_accueil(self):
        """Affiche la vue d'accueil"""
        self._clear_content()
        view = AccueilView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Accueil")
        self._select_navigation("Accueil")
    
    def show_dashboard(self):
        """Affiche le dashboard"""
        if not self._check_permission("view_dashboard"):
            return
        self._clear_content()
        view = DashboardView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Tableau de bord")
        self._select_navigation("Tableau de bord")
    
    def show_historique(self):
        """Affiche l'historique"""
        self._clear_content()
        view = HistoriqueView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Historique")
        self._select_navigation("Historique")
    
    def show_owners(self):
        """Affiche la gestion des motos"""
        self._clear_content()
        view = OwnersView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Usagers et motos")
        self._select_navigation("Usagers et motos")
    
    def show_users(self):
        """Affiche la gestion des utilisateurs"""
        if not self._check_permission("manage_users"):
            return
        self._clear_content()
        view = UserManagementView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Comptes d'accès")
        self._select_navigation("Comptes d'accès")
    
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
        self.login_btn.config(text="Connexion", bg=theme.Colors.SUCCESS)
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=theme.Colors.SUCCESS_HOVER))
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
        from tkinter import messagebox, Toplevel, Label, Frame
        from app.config import theme
        
        about_window = Toplevel(self.root)
        about_window.title("À propos")
        about_window.geometry("500x400")
        about_window.config(bg=theme.Colors.BG_SECONDARY)
        about_window.resizable(False, False)
        about_window.grab_set()
        
        # Centrer la fenêtre
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (about_window.winfo_screenheight() // 2) - (400 // 2)
        about_window.geometry(f"500x400+{x}+{y}")
        
        # Contenu
        main_frame = Frame(about_window, bg=theme.Colors.BG_SECONDARY, padx=30, pady=30)
        main_frame.pack(fill="both", expand=True)
        
        # Titre
        title = Label(
            main_frame,
            text=f"À propos de {branding.APP_NAME}",
            font=(theme.FONT_FAMILY, 22, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY,
            pady=20
        )
        title.pack()
        
        # Version
        version = Label(
            main_frame,
            text=f"Version {branding.APP_VERSION}",
            font=(theme.FONT_FAMILY, 12),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_SECONDARY,
            pady=10
        )
        version.pack()
        
        # Description
        description = Label(
            main_frame,
            text="Application de gestion de parking\npour l'Université Kofi Annan de Guinée",
            font=(theme.FONT_FAMILY, 12),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_PRIMARY,
            justify="center",
            pady=20
        )
        description.pack()
        
        # Développeur
        developer = Label(
            main_frame,
            text="Développé par :\nElhadj Ibrahima Barry",
            font=(theme.FONT_FAMILY, 11, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY,
            justify="center",
            pady=10
        )
        developer.pack()
        
        # Technologies
        tech = Label(
            main_frame,
            text="Technologies :\nPython • Tkinter • MySQL",
            font=(theme.FONT_FAMILY, 10),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_SECONDARY,
            justify="center",
            pady=20
        )
        tech.pack()
        
        # Bouton fermer
        close_btn = Button(
            main_frame,
            text="Fermer",
            command=about_window.destroy,
            font=(theme.FONT_FAMILY, 11, "bold"),
            bg=theme.Colors.PRIMARY,
            fg=theme.Colors.TEXT_LIGHT,
            activebackground=theme.Colors.PRIMARY_LIGHT,
            activeforeground=theme.Colors.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=10
        )
        close_btn.pack(pady=10)
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=theme.Colors.PRIMARY_LIGHT))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=theme.Colors.PRIMARY))
    
    def _update_status(self, message):
        """Met à jour le message de statut"""
        self.status_label.config(text=message)
    
    def _on_closing(self):
        """Gère la fermeture de l'application"""
        from tkinter import messagebox
        
        # Demander confirmation
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            # Nettoyage si nécessaire
            self._cleanup()
            # Fermer l'application
            self.root.destroy()
            self.root.quit()
    
    def _cleanup(self):
        """Nettoie les ressources avant la fermeture"""
        # Fermer les connexions à la base de données si nécessaire
        try:
            # Les connexions SQLite se ferment automatiquement
            # Mais on peut ajouter du nettoyage ici si nécessaire
            pass
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
    
    def _show_guide(self):
        """Affiche le guide utilisateur"""
        from tkinter import Toplevel, Label, Frame, Text, Scrollbar
        from app.config import theme
        
        guide_window = Toplevel(self.root)
        guide_window.title("Guide utilisateur")
        guide_window.geometry("700x600")
        guide_window.config(bg=theme.Colors.BG_SECONDARY)
        guide_window.resizable(True, True)
        guide_window.grab_set()
        
        # Centrer la fenêtre
        guide_window.update_idletasks()
        x = (guide_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (guide_window.winfo_screenheight() // 2) - (600 // 2)
        guide_window.geometry(f"700x600+{x}+{y}")
        
        # Contenu
        main_frame = Frame(guide_window, bg=theme.Colors.BG_SECONDARY, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Titre
        title = Label(
            main_frame,
            text="Guide utilisateur - UKAG Parking",
            font=(theme.FONT_FAMILY, 20, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY,
            pady=15
        )
        title.pack()
        
        # Zone de texte avec scrollbar
        text_frame = Frame(main_frame, bg=theme.Colors.BG_SECONDARY)
        text_frame.pack(fill="both", expand=True, pady=10)
        
        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        guide_text = Text(
            text_frame,
            font=(theme.FONT_FAMILY, 11),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_PRIMARY,
            wrap="word",
            yscrollcommand=scrollbar.set,
            padx=15,
            pady=15,
            relief="flat",
            bd=0
        )
        guide_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=guide_text.yview)
        
        # Contenu du guide
        guide_content = """
═══════════════════════════════════════════════════════════════
                    GUIDE UTILISATEUR - PARKINGAPP
═══════════════════════════════════════════════════════════════

1. CONNEXION
───────────────────────────────────────────────────────────────
• Cliquez sur le bouton "🔐 Connexion" dans le menu latéral
• Entrez votre nom d'utilisateur et mot de passe
• Par défaut : vos identifiants UKAG Parking

2. ACCUEIL - Gestion des entrées/sorties
───────────────────────────────────────────────────────────────
• Cliquez sur "🏠 Accueil" dans le menu
• Bouton "Entrée" : Enregistrer l'entrée d'une moto
• Bouton "Sortie" : Enregistrer la sortie d'une moto
• Scannez le code-barres ou entrez-le manuellement
• Les informations du propriétaire s'affichent automatiquement

3. DASHBOARD - Statistiques
───────────────────────────────────────────────────────────────
• Cliquez sur "📊 Dashboard" dans le menu
• Visualisez les statistiques globales :
  - Nombre total de motos
  - Motos présentes dans le parking
  - Motos absentes
  - Graphiques d'évolution

4. HISTORIQUE
───────────────────────────────────────────────────────────────
• Cliquez sur "📜 Historique" dans le menu
• Consultez l'historique de toutes les entrées/sorties
• Recherchez par date, nom, plaque, etc.
• Exportez les données si nécessaire

5. USAGERS ET MOTOS
───────────────────────────────────────────────────────────────
• Cliquez sur "Usagers et motos" dans le menu
• Ajouter : Enregistrer un nouveau propriétaire de moto
• Modifier : Modifier les informations d'un propriétaire
• Supprimer : Supprimer un propriétaire
• Rechercher : Rechercher par nom, plaque, code-barres
• Exporter : Exporter la liste en HTML
• Changer photo : Prendre une photo avec la webcam

6. COMPTES D’ACCÈS (Admin uniquement)
───────────────────────────────────────────────────────────────
• Cliquez sur "Comptes d’accès" dans le menu
• Réservé aux administrateurs
• Ajouter : Créer un nouvel utilisateur
• Modifier : Modifier les informations d'un utilisateur
• Supprimer : Supprimer un utilisateur
• Définir les rôles : Administrateur ou Utilisateur

7. NAVIGATION
───────────────────────────────────────────────────────────────
• Utilisez le menu latéral pour naviguer entre les sections
• Le menu supérieur offre des raccourcis supplémentaires
• La barre de statut en bas affiche les informations actuelles

8. CONSEILS
───────────────────────────────────────────────────────────────
• Sauvegardez régulièrement vos données
• Utilisez des codes-barres uniques pour chaque moto
• Vérifiez les informations avant de valider une entrée/sortie
• Déconnectez-vous après utilisation pour la sécurité

9. SUPPORT
───────────────────────────────────────────────────────────────
• Pour toute question ou problème, contactez :
  Développeur : Elhadj Ibrahima Barry
  Université : Kofi Annan de Guinée

═══════════════════════════════════════════════════════════════
                        Bonne utilisation !
═══════════════════════════════════════════════════════════════
"""
        
        guide_text.insert("1.0", guide_content)
        guide_text.config(state="disabled")  # Lecture seule
        
        # Bouton fermer
        close_btn = Button(
            main_frame,
            text="Fermer",
            command=guide_window.destroy,
            font=(theme.FONT_FAMILY, 11, "bold"),
            bg=theme.Colors.PRIMARY,
            fg=theme.Colors.TEXT_LIGHT,
            activebackground=theme.Colors.PRIMARY_LIGHT,
            activeforeground=theme.Colors.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=10
        )
        close_btn.pack(pady=15)
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=theme.Colors.PRIMARY_LIGHT))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=theme.Colors.PRIMARY))
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

