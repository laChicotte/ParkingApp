"""
Vue Gestion des Utilisateurs modernisée
"""
from tkinter import Frame, Label, Toplevel, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from app.database import Bdonnee
from app.config import theme, paths, settings
from app.config.permissions import has_permission, requires_permission
from app.models.user import User
from app.components.modern_form import ModernForm, configure_dialog, report_form_error, validate_email
from app.components.icon_button import IconButton
import bcrypt


class UserManagementView(Frame):
    """Vue de gestion des utilisateurs avec tableau et formulaires modernisés"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=theme.Colors.BG_SECONDARY)
        self.main_window = main_window
        if not has_permission("manage_users"):
            return
        self.setup_ui()
        self.load_users()
    
    def setup_ui(self):
        """Configure l'interface"""
        # Frame principal
        main_content = Frame(self, bg=theme.Colors.BG_SECONDARY)
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        main_content.columnconfigure(0, weight=1)
        main_content.columnconfigure(1, minsize=250)
        main_content.rowconfigure(0, weight=1)
        
        # Colonne gauche - Tableau
        left_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Tableau
        tree_frame = Frame(left_frame, bg=theme.Colors.BG_SECONDARY)
        tree_frame.pack(fill="both", expand=True)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("username", "nom", "prenom", "telephone", "email", "role"),
            show="headings",
            height=18,
            yscrollcommand=scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        horizontal_scrollbar.config(command=self.tree.xview)
        
        # Configuration des colonnes
        columns_config = [
            ("username", "Nom d'utilisateur", 150),
            ("nom", "Nom", 120),
            ("prenom", "Prénom", 120),
            ("telephone", "Téléphone", 120),
            ("email", "Email", 200),
            ("role", "Rôle", 120)
        ]
        
        for col, heading, width in columns_config:
            self.tree.heading(col, text=heading, anchor="w")
            self.tree.column(col, width=width, minwidth=width, anchor="w")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Colonne droite - Image
        right_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY, width=250)
        right_frame.grid(row=0, column=1, sticky="ns")
        right_frame.pack_propagate(False)
        actions_frame = Frame(right_frame, bg=theme.Colors.BG_SECONDARY)
        actions_frame.pack(anchor="center", pady=(0, 12))
        self.action_buttons = []
        for icon, label, command, color in (
            ("add", "Ajouter un utilisateur", self.add_user, theme.Colors.SUCCESS),
            ("edit", "Modifier", self.edit_user, theme.Colors.PRIMARY),
            ("delete", "Supprimer", self.delete_user, theme.Colors.ERROR),
        ):
            button = IconButton(actions_frame, icon=icon, label=label, command=command, color=color)
            button.pack(side="left", padx=4)
            self.action_buttons.append(button)
        
        # Image
        img_frame = Frame(right_frame, bg=theme.Colors.BG_SECONDARY,
                          highlightbackground=theme.Colors.BORDER, highlightthickness=1)
        img_frame.pack(pady=(0, 12))
        
        try:
            if paths.PROFIL_PATH.exists():
                img = Image.open(str(paths.PROFIL_PATH))
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                photo_tk = ImageTk.PhotoImage(img)
                self.image_label = Label(img_frame, image=photo_tk, bg=theme.Colors.BG_SECONDARY)
                self.image_label.image = photo_tk
            else:
                raise FileNotFoundError
        except:
            self.image_label = Label(
                img_frame,
                text="Aucune image",
                bg=theme.Colors.BG_SECONDARY,
                width=25,
                height=10
            )
        self.image_label.pack(padx=10, pady=10)
        self._default_photo = getattr(self.image_label, "image", None)
        self.update_permissions()

    def update_permissions(self):
        allowed = has_permission("manage_users")
        for button in self.action_buttons:
            button.state(["!disabled"] if allowed else ["disabled"])
            button.config(cursor="hand2" if allowed else "arrow", takefocus=allowed)
    
    @requires_permission("manage_users")
    def load_users(self):
        """Charge les utilisateurs dans le tableau"""
        db = Bdonnee()
        users = db.recuperer(1)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for user in users:
            role_name = User.ROLES.get(user['role'], "Rôle inconnu")
            self.tree.insert("", "end", iid=user['id'], values=(
                user['username'],
                user['nom'],
                user['prenom'],
                user['telephone'],
                user['email'],
                role_name
            ))
    
    def on_select(self, event):
        """Gère la sélection d'un utilisateur"""
        selected = self.tree.selection()
        if not selected:
            self.image_label.config(image=self._default_photo or "", text="" if self._default_photo else "Aucune image")
            self.image_label.image = self._default_photo
            return
        
        user_data = self.tree.item(selected[0])["values"]
        telephone = user_data[3]
        
        # Charger l'image
        try:
            image_path = paths.get_image_path(f"{telephone}.png")
            if image_path.exists():
                img = Image.open(str(image_path))
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo)
                self.image_label.image = photo
            else:
                # Image par défaut
                if paths.PROFIL_PATH.exists():
                    img = Image.open(str(paths.PROFIL_PATH))
                    img = img.resize((200, 200), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.image_label.config(image=photo)
                    self.image_label.image = photo
        except Exception as e:
            # Si erreur, essayer l'image par défaut
            try:
                if paths.PROFIL_PATH.exists():
                    img = Image.open(str(paths.PROFIL_PATH))
                    img = img.resize((200, 200), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.image_label.config(image=photo)
                    self.image_label.image = photo
            except:
                pass
    
    @requires_permission("manage_users")
    def add_user(self):
        """Affiche le formulaire d'ajout"""
        self._show_user_form()
    
    @requires_permission("manage_users")
    def edit_user(self):
        """Affiche le formulaire de modification"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un utilisateur.")
            return
        
        user_id = int(selected[0])
        db = Bdonnee()
        users = db.recuperer(1)
        user_data = next((u for u in users if u['id'] == user_id), None)
        
        if user_data:
            self._show_user_form(user_data)
    
    @requires_permission("manage_users")
    def delete_user(self):
        """Supprime un utilisateur"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un utilisateur.")
            return
        
        user_id = int(selected[0])
        user_data = self.tree.item(selected[0])["values"]
        username = user_data[0]
        
        if messagebox.askyesno("Confirmation", f"Voulez-vous supprimer l'utilisateur {username} ?"):
            db = Bdonnee()
            if db.supprimer(1, user_id):
                warning = getattr(db, "last_warning", "")
                if isinstance(warning, str) and warning:
                    messagebox.showwarning("Photo à vérifier", "Utilisateur supprimé.\n" + warning)
                else:
                    messagebox.showinfo("Succès", "Utilisateur supprimé avec succès.")
                self.load_users()
                self.on_select(None)
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression.")
    
    @requires_permission("manage_users")
    def _show_user_form(self, user_data=None):
        """Affiche le formulaire utilisateur"""
        dialog = Toplevel(self)
        dialog.title("Ajouter un utilisateur" if not user_data else "Modifier un utilisateur")
        configure_dialog(dialog, self)
        
        # Configuration des champs
        fields_config = {
            "username": {"label": "Nom d'utilisateur *", "type": "entry"},
            "nom": {"label": "Nom *", "type": "entry"},
            "prenom": {"label": "Prénom *", "type": "entry"},
            "telephone": {"label": "Téléphone *", "type": "entry"},
            "email": {"label": "Email *", "type": "entry", "validator": validate_email},
            "password": {"label": "Mot de passe *", "type": "password"},
            "role": {"label": "Rôle", "type": "option", "options": ["Agent de parking", "Administrateur"]}
        }
        
        # Valeurs par défaut
        default_values = {}
        if user_data:
            default_values = {
                "username": user_data.get('username', ''),
                "nom": user_data.get('nom', ''),
                "prenom": user_data.get('prenom', ''),
                "telephone": user_data.get('telephone', ''),
                "email": user_data.get('email', ''),
                "role": "Administrateur" if user_data.get('role') == 1 else "Agent de parking"
            }
            # Ne pas pré-remplir le mot de passe
            fields_config.pop("password", None)
        
        for field_name, field_config in fields_config.items():
            if field_name in default_values:
                field_config["default"] = default_values[field_name]
        
        # Créer le formulaire
        form = ModernForm(
            dialog,
            "Modifier un compte" if user_data else "Créer un compte",
            fields_config,
            "Enregistrer",
            lambda values: self._save_user(values, user_data['id'] if user_data else None, dialog)
        )
    
    @requires_permission("manage_users")
    def _save_user(self, values, user_id, dialog):
        """Sauvegarde un utilisateur"""
        # Validation
        required_fields = ["username", "nom", "prenom", "telephone", "email"]
        for field in required_fields:
            if not str(values.get(field, "")).strip():
                report_form_error(dialog, "Vérifiez les champs signalés.", {field: "Ce champ est obligatoire."})
                return
        
        try:
            db = Bdonnee()
        except Exception as error:
            report_form_error(dialog, f"Enregistrement impossible : {error}")
            return
        roles = {"Agent de parking": 0, "Utilisateur": 0, "Administrateur": 1}
        
        if user_id:
            # Modification
            nouvelles_valeurs = {
                "username": values["username"],
                "nom": values["nom"],
                "prenom": values["prenom"],
                "telephone": values["telephone"],
                "email": values["email"],
                "role": roles[values.get("role", "Agent de parking")]
            }
            
            if db.modifier(1, user_id, nouvelles_valeurs, notify=False):
                warning = getattr(db, "last_warning", "")
                if isinstance(warning, str) and warning:
                    messagebox.showwarning("Photo à vérifier", "Utilisateur modifié.\n" + warning)
                else:
                    messagebox.showinfo("Succès", "Utilisateur modifié avec succès.")
                dialog.destroy()
                self.load_users()
            else:
                self._report_user_error(dialog, db.last_error or "Modification impossible. Réessayez.")
        else:
            # Ajout
            if not values.get("password"):
                report_form_error(dialog, "Vérifiez les champs signalés.", {"password": "Ce champ est obligatoire."})
                return
            
            if len(values["password"].encode('utf-8')) > 72:
                report_form_error(dialog, "Vérifiez les champs signalés.", {"password": "Le mot de passe dépasse la taille maximale de 72 octets."})
                return
            password_hash = bcrypt.hashpw(values["password"].encode('utf-8'), bcrypt.gensalt())
            
            if db.ajouter(1, [
                values["username"],
                values["nom"],
                values["prenom"],
                values["telephone"],
                values["email"],
                password_hash,
                roles[values.get("role", "Agent de parking")]
            ], notify=False):
                messagebox.showinfo("Succès", "Utilisateur ajouté avec succès.")
                dialog.destroy()
                self.load_users()
            else:
                self._report_user_error(dialog, db.last_error or "Enregistrement impossible. Réessayez.")

    @staticmethod
    def _report_user_error(dialog, message):
        errors = {"email": "Cette adresse email est déjà utilisée."} if "duplicate" in message.lower() and "email" in message.lower() else {}
        report_form_error(dialog, "Vérifiez les champs signalés." if errors else message, errors)
