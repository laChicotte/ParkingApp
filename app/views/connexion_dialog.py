"""Connexion au parking universitaire."""
from tkinter import BooleanVar, Frame, Label, Toplevel, ttk

from app.components.modern_form import ModernFormField, configure_dialog
from app.database import Bdonnee
from app.config import settings, theme, branding
from app.models.user import User


class ConnexionDialog:
    def __init__(self, parent, main_window):
        self.main_window = main_window
        self.dialog = Toplevel(parent)
        self.dialog.title(f"Connexion — {branding.APP_NAME}")
        configure_dialog(self.dialog, parent, width=540, height=600)
        self.create_widgets()

    def create_widgets(self):
        main = Frame(self.dialog, bg=theme.Colors.BG_SECONDARY)
        main.pack(fill="both", expand=True, padx=28, pady=20)
        self.logo = branding.load_logo(main, (56, 56))
        if self.logo:
            Label(main, image=self.logo, bg=theme.Colors.BG_SECONDARY).pack(pady=(0, 10))
        Label(main, text="Connexion", font=(theme.FONT_FAMILY, 20, "bold"),
              bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.PRIMARY).pack()
        university = Label(main, text=branding.UNIVERSITY_NAME,
                           font=(theme.FONT_FAMILY, 10), wraplength=440,
                           bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY)
        university.pack(pady=(4, 20))
        main.bind("<Configure>", lambda event: university.config(wraplength=max(100, event.width)))

        footer = Frame(main, bg=theme.Colors.BG_SECONDARY)
        footer.pack(side="bottom", fill="x", pady=(12, 0))
        self.error_label = Label(footer, text="", font=(theme.FONT_FAMILY, 10),
                                  wraplength=420, anchor="w", justify="left",
                                  bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.ERROR)
        self.login_btn = ttk.Button(footer, text="Se connecter", command=self.me_connecter,
                                     style="Primary.TButton", cursor="hand2")
        self.login_btn.pack(fill="x")
        Label(footer, text="Accès réservé aux personnes habilitées de l’UKAG.",
              wraplength=420, font=(theme.FONT_FAMILY, 9), bg=theme.Colors.BG_SECONDARY,
              fg=theme.Colors.TEXT_SECONDARY).pack(pady=(12, 0))

        user = ModernFormField(main, "Nom d’utilisateur")
        self.user_field = user
        user.frame.pack(fill="x", pady=(0, 14))
        self.user_entry = user.entry
        password = ModernFormField(main, "Mot de passe", field_type="password")
        self.password_field = password
        password.frame.pack(fill="x", pady=(0, 10))
        self.password_entry = password.entry
        self.show_password = BooleanVar(self.dialog, value=False)
        ttk.Checkbutton(main, text="Afficher le mot de passe", variable=self.show_password,
                        command=lambda: self.password_entry.config(
                            show="" if self.show_password.get() else "•")).pack(anchor="w")
        self.dialog.bind("<Return>", lambda event: self.me_connecter())
        self.dialog.bind("<Escape>", lambda event: self.dialog.destroy())
        self.user_entry.focus_set()

    def me_connecter(self):
        username = self.user_entry.get().strip()
        password = self.password_entry.get().strip()
        self.user_field.set_error("")
        self.password_field.set_error("")
        self.error_label.pack_forget()
        if not username or not password:
            self.user_field.set_error("Indiquez votre nom d’utilisateur." if not username else "")
            self.password_field.set_error("Indiquez votre mot de passe." if not password else "")
            (self.user_entry if not username else self.password_entry).focus_set()
            return
        try:
            db = Bdonnee()
            user_data = db.get_user(username, notify=False)
            if db.last_error:
                self._show_error("Connexion impossible. Vérifiez la disponibilité de la base de données.")
                return
            if user_data:
                current_user = User(user_data['id'], user_data['username'], user_data['email'],
                                    user_data['password'], user_data['role'])
                if current_user.verify_password(password):
                    settings.current_user = current_user
                    settings.is_connected = True
                    self.main_window.is_connected = settings.is_connected
                    self.main_window.current_user = settings.current_user
                    self.main_window.login_btn.config(text="Déconnexion", bg=theme.Colors.WARNING)
                    self.main_window.login_btn.bind("<Enter>", lambda e: self.main_window.login_btn.config(bg=theme.Colors.WARNING_HOVER))
                    self.main_window.login_btn.bind("<Leave>", lambda e: self.main_window.login_btn.config(bg=theme.Colors.WARNING))
                    self.main_window.user_label.config(text=f"Connecté: {current_user.name()}")
                    self.main_window.refresh_permissions()
                    self.main_window._update_status("Connexion réussie")
                    self.dialog.destroy()
                    self.main_window.show_notification(f"Connexion réussie. Bienvenue {current_user.name()} !")
                    return
            self.password_field.set_error("Nom d’utilisateur ou mot de passe incorrect.")
            self.password_entry.focus_set()
        except Exception as error:
            self._show_error(f"Connexion impossible : {error}")

    def _show_error(self, message):
        self.error_label.config(text=message)
        self.error_label.pack(fill="x", pady=(0, 10), before=self.login_btn)

    def clear_fields(self):
        self.user_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.user_entry.focus_set()
