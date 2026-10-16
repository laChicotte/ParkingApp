"""
Fenêtre de connexion modernisée
"""
from tkinter import Toplevel, Label, Entry, Button, Frame, messagebox
from app.database import Bdonnee
from app.config import settings, theme, branding
from app.models.user import User


class ConnexionDialog:
    """Fenêtre de dialogue de connexion modernisée"""
    
    def __init__(self, parent, main_window):
        self.main_window = main_window
        self.dialog = Toplevel(parent)
        self.dialog.title(f"Connexion — {branding.APP_NAME}")
        self.dialog.geometry("520x700")
        self.dialog.resizable(False, True)
        self.dialog.minsize(520, 620)
        self.dialog.config(bg=theme.Colors.BG_SECONDARY)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        height = min(700, self.dialog.winfo_screenheight() - 80)
        x = max(0, (self.dialog.winfo_screenwidth() - 520) // 2)
        y = max(0, (self.dialog.winfo_screenheight() - height) // 2)
        self.dialog.geometry(f"520x{height}+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crée les widgets de l'interface"""
        # Frame principal avec ombre
        main_frame = Frame(
            self.dialog,
            bg=theme.Colors.BG_SECONDARY,
            relief="flat"
        )
        main_frame.pack(fill="both", expand=True, padx=24, pady=20)
        self.logo = branding.load_logo(main_frame, (76, 76))
        if self.logo:
            Label(main_frame, image=self.logo, bg=theme.Colors.BG_SECONDARY).pack(pady=(0, 4))
        
        # Titre
        title_label = Label(
            main_frame,
            text=f"Connexion à {branding.APP_NAME}",
            font=(theme.FONT_FAMILY, 21, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY,
            pady=8
        )
        title_label.pack()
        Label(main_frame, text=branding.UNIVERSITY_NAME, wraplength=450,
              font=(theme.FONT_FAMILY, 11), bg=theme.Colors.BG_SECONDARY,
              fg=theme.Colors.TEXT_SECONDARY).pack()
        
        # Sous-titre
        subtitle_label = Label(
            main_frame,
            text="Accédez à la gestion du parking universitaire",
            font=(theme.FONT_FAMILY, 10),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_SECONDARY,
            pady=10
        )
        subtitle_label.pack()
        
        # Formulaire
        form_frame = Frame(main_frame, bg=theme.Colors.BG_SECONDARY)
        form_frame.pack(fill="x", pady=(14, 0))
        
        # Champ utilisateur
        user_container = Frame(form_frame, bg=theme.Colors.BG_SECONDARY)
        user_container.pack(fill="x", pady=(0, 20))
        
        user_label = Label(
            user_container,
            text="Nom d'utilisateur",
            font=(theme.FONT_FAMILY, 11, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_PRIMARY,
            anchor="w"
        )
        user_label.pack(fill="x", pady=(0, 5))
        
        self.user_entry = Entry(
            user_container,
            font=(theme.FONT_FAMILY, 13),
            bg="#ffffff",
            fg=theme.Colors.TEXT_PRIMARY,
            relief="solid",
            bd=2,
            highlightthickness=1,
            highlightbackground=theme.Colors.BORDER,
            highlightcolor=theme.Colors.PRIMARY,
            insertbackground=theme.Colors.TEXT_PRIMARY
        )
        self.user_entry.pack(fill="x", ipady=10, padx=2)
        self.user_entry.focus_set()
        
        # Champ mot de passe
        password_container = Frame(form_frame, bg=theme.Colors.BG_SECONDARY)
        password_container.pack(fill="x", pady=(0, 20))
        
        password_label = Label(
            password_container,
            text="Mot de passe",
            font=(theme.FONT_FAMILY, 11, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_PRIMARY,
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 5))
        
        self.password_entry = Entry(
            password_container,
            show='*',
            font=(theme.FONT_FAMILY, 13),
            bg="#ffffff",
            fg=theme.Colors.TEXT_PRIMARY,
            relief="solid",
            bd=2,
            highlightthickness=1,
            highlightbackground=theme.Colors.BORDER,
            highlightcolor=theme.Colors.PRIMARY,
            insertbackground=theme.Colors.TEXT_PRIMARY
        )
        self.password_entry.pack(fill="x", ipady=10, padx=2)
        
        # Bouton de connexion
        login_btn = Button(
            form_frame,
            text="Se connecter",
            command=self.me_connecter,
            font=(theme.FONT_FAMILY, 14, "bold"),
            bg=theme.Colors.PRIMARY,
            fg=theme.Colors.TEXT_LIGHT,
            activebackground=theme.Colors.PRIMARY_LIGHT,
            activeforeground=theme.Colors.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=15
        )
        login_btn.pack(fill="x", pady=20)
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg=theme.Colors.PRIMARY_LIGHT))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg=theme.Colors.PRIMARY))
        
        # Lier la touche Entrée
        self.dialog.bind('<Return>', lambda event: self.me_connecter())
        self.password_entry.bind('<Return>', lambda event: self.me_connecter())
        
        # Info par défaut (pour SQLite)
        info_label = Label(
            main_frame,
            text="Accès réservé aux personnes habilitées de l’UKAG.",
            font=(theme.FONT_FAMILY, 9),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_SECONDARY,
            pady=10
        )
        info_label.pack()
    
    def me_connecter(self):
        """Gère la logique de connexion"""
        username = self.user_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Tous les champs doivent être renseignés.")
            return
        
        try:
            db = Bdonnee()
            user_data = db.get_user(username)
            
            if user_data:
                # Créer l'objet User
                current_user = User(
                    user_data['id'],
                    user_data['username'],
                    user_data['email'],
                    user_data['password'],
                    user_data['role']
                )
                
                # Vérifier le mot de passe
                if current_user.verify_password(password):
                    # Mettre à jour les variables globales
                    settings.current_user = current_user
                    settings.is_connected = True
                    
                    # Mettre à jour la fenêtre principale
                    from app.config import theme
                    self.main_window.is_connected = settings.is_connected
                    self.main_window.current_user = settings.current_user
                    self.main_window.login_btn.config(text="🔓 Déconnexion", bg=theme.Colors.WARNING)
                    self.main_window.login_btn.bind("<Enter>", lambda e: self.main_window.login_btn.config(bg=theme.Colors.WARNING_HOVER))
                    self.main_window.login_btn.bind("<Leave>", lambda e: self.main_window.login_btn.config(bg=theme.Colors.WARNING))
                    self.main_window.user_label.config(
                        text=f"Connecté: {current_user.name()}"
                    )
                    self.main_window._update_status("Connexion réussie")
                    
                    messagebox.showinfo("Succès", "Connexion réussie. Bienvenue !")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")
                    self.clear_fields()
            else:
                messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")
                self.clear_fields()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
            self.clear_fields()
    
    def clear_fields(self):
        """Réinitialise les champs"""
        self.user_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.user_entry.focus_set()

