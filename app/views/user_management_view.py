"""
Vue Gestion des Utilisateurs modernisée
"""
from tkinter import Frame, Label, Toplevel, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from app.database.sqlite import Bdonnee
from app.config import theme, paths, settings
from app.components.modern_form import ModernForm
import bcrypt


class UserManagementView(Frame):
    """Vue de gestion des utilisateurs avec tableau et formulaires modernisés"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=theme.Colors.BG_SECONDARY)
        self.main_window = main_window
        self.setup_ui()
        self.load_users()
    
    def setup_ui(self):
        """Configure l'interface"""
        # Titre et barre d'outils
        header_frame = Frame(self, bg=theme.Colors.BG_SECONDARY)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        title = Label(
            header_frame,
            text="Gestion des Utilisateurs",
            font=("Arial", 24, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY
        )
        title.pack(side="left")
        
        # Boutons d'action
        actions_frame = Frame(header_frame, bg=theme.Colors.BG_SECONDARY)
        actions_frame.pack(side="right")
        
        ttk.Button(
            actions_frame,
            text="➕ Ajouter",
            command=self.add_user,
            style="Success.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            actions_frame,
            text="✏️ Modifier",
            command=self.edit_user,
            style="Primary.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            actions_frame,
            text="🗑️ Supprimer",
            command=self.delete_user,
            style="Danger.TButton"
        ).pack(side="left", padx=5)
        
        # Frame principal
        main_content = Frame(self, bg=theme.Colors.BG_SECONDARY)
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Colonne gauche - Tableau
        left_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Tableau
        tree_frame = Frame(left_frame, bg=theme.Colors.BG_SECONDARY)
        tree_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("username", "nom", "prenom", "telephone", "email", "role"),
            show="headings",
            height=18,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
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
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Colonne droite - Image
        right_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY, width=250)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Image
        img_frame = Frame(right_frame, bg=theme.Colors.BG_SECONDARY, relief="solid", bd=2)
        img_frame.pack(pady=20)
        
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
    
    def load_users(self):
        """Charge les utilisateurs dans le tableau"""
        db = Bdonnee()
        users = db.recuperer(1)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for user in users:
            role_name = "Administrateur" if user['role'] == 1 else "Utilisateur"
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
    
    def add_user(self):
        """Affiche le formulaire d'ajout"""
        self._show_user_form()
    
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
                messagebox.showinfo("Succès", "Utilisateur supprimé avec succès.")
                self.load_users()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression.")
    
    def _show_user_form(self, user_data=None):
        """Affiche le formulaire utilisateur"""
        dialog = Toplevel(self)
        dialog.title("Ajouter un utilisateur" if not user_data else "Modifier un utilisateur")
        dialog.geometry("600x700")
        dialog.config(bg=theme.Colors.BG_SECONDARY)
        dialog.grab_set()
        dialog.resizable(True, True)
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"600x700+{x}+{y}")
        
        # Configuration des champs
        fields_config = {
            "username": {"label": "Nom d'utilisateur", "type": "entry", "required": True, "placeholder": "Ex: john.doe"},
            "nom": {"label": "Nom", "type": "entry", "required": True, "placeholder": "Ex: Camara"},
            "prenom": {"label": "Prénom", "type": "entry", "required": True, "placeholder": "Ex: Ibrahima"},
            "telephone": {"label": "Téléphone", "type": "entry", "required": True, "placeholder": "Ex: 622000000"},
            "email": {"label": "Email", "type": "entry", "required": True, "placeholder": "Ex: ibrahima@exemple.com"},
            "password": {"label": "Mot de passe", "type": "password", "required": True},
            "role": {"label": "Rôle", "type": "option", "options": ["Utilisateur", "Administrateur"]}
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
                "role": "Administrateur" if user_data.get('role') == 1 else "Utilisateur"
            }
            # Ne pas pré-remplir le mot de passe
            fields_config.pop("password", None)
        
        for field_name, field_config in fields_config.items():
            if field_name in default_values:
                field_config["default"] = default_values[field_name]
        
        # Créer le formulaire
        form = ModernForm(
            dialog,
            "Formulaire Utilisateur",
            fields_config,
            "Enregistrer",
            lambda values: self._save_user(values, user_data['id'] if user_data else None, dialog)
        )
    
    def _save_user(self, values, user_id, dialog):
        """Sauvegarde un utilisateur"""
        db = Bdonnee()
        roles = {"Utilisateur": 0, "Administrateur": 1}
        
        if user_id:
            # Modification
            nouvelles_valeurs = {
                "username": values["username"],
                "nom": values["nom"],
                "prenom": values["prenom"],
                "telephone": values["telephone"],
                "email": values["email"],
                "role": roles[values.get("role", "Utilisateur")]
            }
            
            if db.modifier(1, user_id, nouvelles_valeurs):
                messagebox.showinfo("Succès", "Utilisateur modifié avec succès.")
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la modification.")
        else:
            # Ajout
            if not values.get("password"):
                messagebox.showerror("Erreur", "Le mot de passe est obligatoire.")
                return
            
            password_hash = bcrypt.hashpw(values["password"].encode('utf-8'), bcrypt.gensalt())
            
            if db.ajouter(1, [
                values["username"],
                values["nom"],
                values["prenom"],
                values["telephone"],
                values["email"],
                password_hash,
                roles[values.get("role", "Utilisateur")]
            ]):
                messagebox.showinfo("Succès", "Utilisateur ajouté avec succès.")
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'ajout.")
