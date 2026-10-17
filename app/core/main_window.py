"""
Fenêtre principale de l'application avec navigation par onglets
"""
from tkinter import Tk, Frame, Menu, Button, Label
from tkinter import ttk
from app.config import settings, theme, paths, branding
from app.utils.fonctions import today
from app.config.permissions import has_permission
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
        self._notification_frame = None
        self._notification_job = None
        
        # Configuration du style
        self.style = theme.Theme.configure_style(self.root)
        
        # Créer l'interface
        self._create_menu()
        self._create_status_bar()
        self._create_main_container()
        
        # Afficher la vue d'accueil par défaut
        self.show_accueil()
        self.refresh_permissions()
    
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
        self.nav_menu = nav_menu
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
        high_scaling = float(self.root.tk.call("tk", "scaling")) >= 1.8
        self.nav_font_size = 10 if high_scaling else 11
        self.sidebar_logo = branding.load_logo(nav_frame, (84, 84))
        if self.sidebar_logo:
            logo_label = Label(nav_frame, image=self.sidebar_logo,
                               bg=theme.Colors.BG_SECONDARY, padx=5, pady=5)
            logo_label.pack(anchor="center", pady=(20, 0))
        title_label = ttk.Label(
            nav_frame,
            text=branding.APP_NAME,
            style="Title.TLabel",
            background=theme.Colors.BG_DARK,
            foreground=theme.Colors.TEXT_LIGHT,
            font=(theme.FONT_FAMILY, 15 if high_scaling else 17, "bold")
        )
        title_label.pack(anchor="center", pady=(12, 24))
        
        # Boutons de navigation avec style amélioré
        nav_buttons = [
            ("Accueil", self.show_accueil),
            ("Tableau de bord", self.show_dashboard),
            ("Historique", self.show_historique),
            ("Usagers et motos", self.show_owners),
            ("Comptes d'accès", self.show_users),
        ]
        
        self.nav_buttons = []
        self.nav_indicators = {}
        self.active_nav = None
        for text, command in nav_buttons:
            btn_frame = Frame(nav_frame, bg=theme.Colors.BG_DARK)
            btn_frame.pack(pady=4, padx=12, fill="x")
            indicator = Frame(btn_frame, bg=theme.Colors.BG_DARK, width=3)
            indicator.pack(side="left", fill="y")
            
            btn = Button(
                btn_frame,
                text=text,
                command=command,
                font=(theme.FONT_FAMILY, self.nav_font_size),
                bg=theme.Colors.BG_DARK,
                fg=theme.Colors.TEXT_LIGHT,
                activebackground=theme.Colors.NAV_HOVER,
                activeforeground=theme.Colors.TEXT_LIGHT,
                relief="flat",
                bd=0,
                highlightthickness=0,
                highlightbackground=theme.Colors.BG_DARK,
                highlightcolor=theme.Colors.ACCENT,
                cursor="hand2",
                padx=6,
                pady=10,
                anchor="w"
            )
            btn.pack(side="left", fill="x", expand=True)
            self.nav_indicators[btn] = indicator
            btn.bind("<Enter>", lambda e, b=btn: self._paint_navigation(b, hover=True))
            btn.bind("<Leave>", lambda e, b=btn: self._paint_navigation(b))
            btn.bind("<FocusIn>", lambda e, b=btn: self._paint_navigation(b, hover=True))
            btn.bind("<FocusOut>", lambda e, b=btn: self._paint_navigation(b))
            self.nav_buttons.append(btn)
        
        # Bouton de connexion/déconnexion
        login_frame = Frame(nav_frame, bg=theme.Colors.BG_DARK)
        login_frame.pack(side="bottom", pady=20, padx=10, fill="x")
        
        self.login_btn = Button(
            login_frame,
            text="Connexion",
            command=self._toggle_login,
            font=(theme.FONT_FAMILY, 11, "bold"),
            bg=theme.Colors.SUCCESS,
            fg=theme.Colors.TEXT_LIGHT,
            activebackground=theme.Colors.SUCCESS_HOVER,
            activeforeground=theme.Colors.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=10
        )
        self.login_btn.pack(fill="x")
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=theme.Colors.SUCCESS_HOVER))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=theme.Colors.SUCCESS))
        
        # Frame de contenu (zone principale)
        content_shell = Frame(main_frame, bg=theme.Colors.BG_SECONDARY)
        content_shell.pack(side="right", fill="both", expand=True)
        university_header = Frame(content_shell, bg=theme.Colors.BG_SECONDARY)
        self.university_header = university_header
        university_header.pack(fill="x", padx=24, pady=(16, 0))
        self.header_logo = branding.load_logo(university_header, (48, 48))
        self.home_header_logo = branding.load_logo(university_header, (32, 32))
        self.header_logo_label = None
        if self.header_logo:
            self.header_logo_label = Label(university_header, image=self.header_logo,
                                           bg=theme.Colors.BG_SECONDARY)
            self.header_logo_label.grid(row=0, column=0, padx=(0, 12), sticky="w")
        header_text = Frame(university_header, bg=theme.Colors.BG_SECONDARY)
        header_text.grid(row=0, column=1, sticky="w")
        university_header.columnconfigure(2, weight=1)
        self.university_name_label = Label(header_text, text=branding.UNIVERSITY_NAME,
                                           font=(theme.FONT_FAMILY, 13, "bold"), bg=theme.Colors.BG_SECONDARY,
                                           fg=theme.Colors.TEXT_PRIMARY)
        self.university_name_label.pack(anchor="w")
        self.section_label = Label(header_text, text=branding.SERVICE_NAME,
                                   font=(theme.FONT_FAMILY, 10), bg=theme.Colors.BG_SECONDARY,
                                   fg=theme.Colors.TEXT_SECONDARY)
        self.section_label.pack(anchor="w", pady=(2, 0))
        self.home_title_label = Label(university_header, text="Entrées et sorties",
                                      font=(theme.FONT_FAMILY, 16, "bold"),
                                      bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.PRIMARY)
        self.home_date_label = Label(university_header, text=f"Le {today(1)}",
                                     font=(theme.FONT_FAMILY, 12),
                                     bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY)
        self._home_header = False
        self._header_section_title = None
        self.section_title_label = Label(university_header,
                                           font=(theme.FONT_FAMILY, 18, "bold"),
                                           bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.PRIMARY)
        university_header.bind("<Configure>", self._layout_home_header)
        self.header_separator = Frame(content_shell, bg=theme.Colors.BORDER, height=1)
        self.header_separator.pack(fill="x", padx=24, pady=(12, 0))
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
    
    def _clear_content(self, compact_header=False, section_title=None):
        """Efface le contenu actuel"""
        if self.current_view_frame:
            self.current_view_frame.destroy()
        self.root.minsize(1000 if compact_header else 1100, 600 if compact_header else 700)
        self._home_header = compact_header
        self._header_section_title = section_title
        if section_title:
            self.section_title_label.config(text=section_title)
        self._layout_home_header()
        self.university_header.pack_configure(pady=(8 if compact_header else 16, 0))
        self.header_separator.pack_configure(pady=(8 if compact_header else 12, 0))
        self.university_name_label.config(font=(theme.FONT_FAMILY, 12 if compact_header else 13, "bold"))
        if self.header_logo_label:
            self.header_logo_label.config(image=self.home_header_logo if compact_header else self.header_logo)
        if compact_header or section_title:
            self.section_label.pack_forget()
        else:
            self.section_label.pack(anchor="w", pady=(2, 0))
        self.current_view_frame = Frame(self.content_frame, bg=theme.Colors.BG_SECONDARY)
        self.current_view_frame.pack(fill="both", expand=True, padx=16, pady=12 if compact_header else 16)

    def _layout_home_header(self, event=None):
        """Titre et date dans l'en-tête, sur deux lignes si nécessaire."""
        if self._header_section_title:
            self.home_title_label.grid_remove()
            self.home_date_label.grid_remove()
            required = (self.university_name_label.winfo_reqwidth()
                        + self.section_title_label.winfo_reqwidth() + 100)
            self.section_title_label.grid(
                row=0 if self.university_header.winfo_width() >= required else 1,
                column=2, columnspan=2, sticky="e", padx=(16, 0))
            return
        self.section_title_label.grid_remove()
        if not self._home_header:
            self.home_title_label.grid_remove()
            self.home_date_label.grid_remove()
            return
        self.home_date_label.config(text=f"Le {today(1)}")
        required = (self.university_name_label.winfo_reqwidth()
                    + self.home_title_label.winfo_reqwidth()
                    + self.home_date_label.winfo_reqwidth() + 100)
        if self.university_header.winfo_width() >= required:
            self.home_date_label.grid(row=0, column=2, columnspan=1, padx=16, pady=0)
            self.home_title_label.grid(row=0, column=3, columnspan=1, sticky="e", pady=0)
        else:
            self.home_date_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
            self.home_title_label.grid(row=1, column=2, columnspan=2, sticky="e", pady=(8, 0))

    def _select_navigation(self, label):
        """Indique la section ouverte, y compris après navigation par le menu."""
        self.active_nav = label
        self.section_label.config(text=f"{branding.SERVICE_NAME} / {label}")
        self.root.title(f"{branding.APP_NAME} — {label}")
        for button in self.nav_buttons:
            self._paint_navigation(button)

    def _paint_navigation(self, button, hover=False):
        if str(button.cget("state")) == "disabled":
            button.config(bg=theme.Colors.BG_DARK, disabledforeground="#738a98", cursor="arrow")
            self.nav_indicators[button].config(bg=theme.Colors.BG_DARK)
            return
        selected = button.cget("text") == self.active_nav
        background = (theme.Colors.NAV_SELECTED if selected else
                      theme.Colors.NAV_HOVER if hover else theme.Colors.BG_DARK)
        button.config(bg=background, activebackground=theme.Colors.NAV_SELECTED,
                      fg=theme.Colors.TEXT_LIGHT if selected or hover else "#c3d2da",
                      font=(theme.FONT_FAMILY, self.nav_font_size, "bold" if selected else "normal"))
        self.nav_indicators[button].config(bg="#73c5ce" if selected else background)

    def refresh_permissions(self):
        """Griser les actions interdites sans les retirer de la navigation."""
        restrictions = {"Tableau de bord": "view_dashboard", "Comptes d'accès": "manage_users",
                        "Historique": "view_history", "Usagers et motos": "view_owners"}
        for button in self.nav_buttons:
            label = button.cget("text")
            allowed = label not in restrictions or has_permission(restrictions[label])
            button.config(state="normal" if allowed else "disabled", takefocus=allowed,
                          cursor="hand2" if allowed else "arrow")
            self.nav_menu.entryconfigure(label, state="normal" if allowed else "disabled")
            self._paint_navigation(button)
        if self.active_nav in restrictions and not has_permission(restrictions[self.active_nav]):
            self.show_accueil()
        if self.current_view_frame:
            for view in self.current_view_frame.winfo_children():
                if hasattr(view, "update_permissions"):
                    view.update_permissions()
    
    def show_accueil(self):
        """Affiche la vue d'accueil"""
        self._clear_content(compact_header=True)
        view = AccueilView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Accueil")
        self._select_navigation("Accueil")
    
    def show_dashboard(self):
        """Affiche le dashboard"""
        if not self._check_permission("view_dashboard"):
            return
        self._clear_content(section_title="Tableau de bord")
        view = DashboardView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Tableau de bord")
        self._select_navigation("Tableau de bord")
    
    def show_historique(self):
        """Affiche l'historique"""
        if not self._check_permission("view_history"):
            return
        self._clear_content(section_title="Historique des mouvements")
        view = HistoriqueView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Historique")
        self._select_navigation("Historique")
    
    def show_owners(self):
        """Affiche la gestion des motos"""
        if not self._check_permission("view_owners"):
            return
        self._clear_content(section_title="Usagers et motos")
        view = OwnersView(self.current_view_frame, self)
        view.pack(fill="both", expand=True)
        self._update_status("Vue: Usagers et motos")
        self._select_navigation("Usagers et motos")
    
    def show_users(self):
        """Affiche la gestion des utilisateurs"""
        if not self._check_permission("manage_users"):
            return
        self._clear_content(section_title="Comptes d’accès")
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
        self._hide_notification()
        settings.logout()
        self.is_connected = settings.is_connected
        self.current_user = settings.current_user
        self.login_btn.config(text="Connexion", bg=theme.Colors.SUCCESS)
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=theme.Colors.SUCCESS_HOVER))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=theme.Colors.SUCCESS))
        self.user_label.config(text="Non connecté")
        self._update_status("Déconnecté")
        self.show_accueil()
        self.refresh_permissions()
    
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

    def show_notification(self, message, duration=3000):
        """Confirmation non modale qui disparaît automatiquement."""
        self._hide_notification()
        self._notification_frame = Frame(self.root, bg=theme.Colors.SUCCESS, padx=16, pady=12)
        Label(self._notification_frame, text=message, bg=theme.Colors.SUCCESS, fg="white",
              font=(theme.FONT_FAMILY, 11, "bold"), justify="left",
              wraplength=min(420, max(200, self.root.winfo_width() - 80))).pack()
        self._notification_frame.place(relx=1, x=-24, y=70, anchor="ne")
        self._notification_frame.lift()
        self._notification_job = self.root.after(duration, self._hide_notification)

    def _hide_notification(self):
        if self._notification_job is not None:
            self.root.after_cancel(self._notification_job)
            self._notification_job = None
        if self._notification_frame is not None:
            self._notification_frame.destroy()
            self._notification_frame = None
    
    def _on_closing(self):
        """Gère la fermeture de l'application"""
        from tkinter import messagebox
        
        # Demander confirmation
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self._hide_notification()
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

