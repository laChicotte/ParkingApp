import os
from tkinter import Label, Entry, Button, Toplevel, messagebox, ttk, StringVar, OptionMenu, Frame
from PIL import Image, ImageTk
import tkinter.font as tkFont
from app.database.sqlite import Bdonnee  # Changer 'mysql' en 'sqlite' pour utiliser SQLite
from app.config import settings
import bcrypt
from app.config import paths


class UserManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Utilisateurs")
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-zoomed', True)  # Linux
        self.root.protocol("WM_DELETE_WINDOW", self._quitter)
        self.root.config(bg='#091821')

        self.bg_color = '#091821'
        self.tree = None
        self.image_label = None  # Pour afficher l'image de l'utilisateur

        # Ajouter le bouton de profil/déconnexion
        try:
            img_profil = Image.open(str(paths.get_icon_path("profil.png")))  
            img_profil = img_profil.resize((70, 70), Image.Resampling.LANCZOS)
            self.icon_profil = ImageTk.PhotoImage(img_profil)
            
            name = settings.current_user.name() if settings.is_connected else "Connexion"
            self.profil = Button(root, text=f"{name}", image=self.icon_profil, compound="top", 
                               font=("Arial", 10), bg=self.bg_color, fg='white', command=self._login_logout)
            self.profil.place(relx=1.0, y=0, anchor="ne")
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône de profil : {e}")

        self.setup_ui()
        self.load_users()


    def setup_ui(self):
        """Configure l'interface utilisateur pour la gestion des utilisateurs."""
        Label(self.root, text="Gestion des Utilisateurs", font=("Sans Serif", 30), bg=self.bg_color, fg="white").pack(pady=15)

        # Conteneur principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Conteneur gauche (Treeview)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        # Treeview pour afficher les utilisateurs
        self.tree = ttk.Treeview(
            left_frame,
            columns=(1, 2, 3, 4, 5, 6, 7),
            show="headings",
            height=15
        )

        bold_font = tkFont.Font(weight="bold")

        self.tree.heading(1, text="ID")
        self.tree.heading(2, text="Nom d'utilisateur")
        self.tree.heading(3, text="Nom")
        self.tree.heading(4, text="Prénom")
        self.tree.heading(5, text="Téléphone")
        self.tree.heading(6, text="Email")
        self.tree.heading(7, text="Rôle")

        self.tree.column(1, width=50, anchor="center")
        self.tree.column(2, width=150)
        self.tree.column(3, width=150)
        self.tree.column(4, width=150)
        self.tree.column(5, width=150, anchor="center")
        self.tree.column(6, width=250)
        self.tree.column(7, width=100, anchor="center")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=bold_font)
        style.configure("Treeview.Heading", font=bold_font)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.display_user_image)

        # Conteneur droit (Image et boutons)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="y", padx=20)

        # Affichage de l'image
        self.image_label = Label(right_frame, bg=self.bg_color)
        self.image_label.pack(pady=10)

        # Charger l'image par défaut au démarrage
        self.update_image(str(paths.PROFIL_PATH))

        # Boutons avec icônes
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(pady=10)

        # Charger et redimensionner les icônes
        icon_add = Image.open(str(paths.get_icon_path("add.png"))).resize((40, 40), Image.Resampling.LANCZOS)
        icon_add = ImageTk.PhotoImage(icon_add)

        icon_edit = Image.open(str(paths.get_icon_path("edit.png"))).resize((40, 40), Image.Resampling.LANCZOS)
        icon_edit = ImageTk.PhotoImage(icon_edit)

        icon_delete = Image.open(str(paths.get_icon_path("delete.png"))).resize((40, 40), Image.Resampling.LANCZOS)
        icon_delete = ImageTk.PhotoImage(icon_delete)

        icon_home = Image.open(str(paths.get_icon_path("home.png"))).resize((40, 40), Image.Resampling.LANCZOS)
        icon_home = ImageTk.PhotoImage(icon_home)

        icon_history = Image.open(str(paths.get_icon_path("history.png"))).resize((40, 40), Image.Resampling.LANCZOS)
        icon_history = ImageTk.PhotoImage(icon_history)

        icon_liste = Image.open(str(paths.get_icon_path("liste.jpeg"))).resize((40, 40), Image.Resampling.LANCZOS)
        icon_liste = ImageTk.PhotoImage(icon_liste)

        # Ajouter les boutons avec les icônes redimensionnées
        Button(button_frame, image=icon_add, command=self.add_user, width=45).grid(row=0, column=0, padx=10)
        Button(button_frame, image=icon_edit, command=self.edit_user, width=45).grid(row=0, column=1, padx=10)
        Button(button_frame, image=icon_delete, command=self.delete_user, width=45).grid(row=0, column=2, padx=10)

        # Ajouter les boutons textuels
        font = ("Times New Roman", 16)
        b_bg = "#235F42"
        Button(button_frame, text="Historique", bg=b_bg, font=font, command=self.navigate_to_history, height=1).grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        Button(button_frame, text="Accueil", bg=b_bg, font=font, command=self.navigate_to_io, height=1).grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        Button(button_frame, text="Motards", bg=b_bg, font=font, command=self.navigate_to_liste, height=1).grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        Button(button_frame, text="Dashboard", bg=b_bg, font=font, command=self.navigate_to_dashboard, height=1).grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        
        self.photo = Button(right_frame, text="Ajouter Photo", bg="green", font=("Times New Roman", 12))
        self.photo.pack(pady=5)

        # IMPORTANT: Conservez une référence aux images pour éviter qu'elles soient collectées par le garbage collector
        self.icons = [icon_add, icon_edit, icon_delete, icon_home, icon_history, icon_liste]

    def _login_logout(self):
        """Gère la déconnexion de l'utilisateur."""
        if settings.is_connected:
            if messagebox.askyesno("Confirmation", "Voulez-vous vraiment vous déconnecter ?"):
                settings.logout()
                self.root.destroy()
        else:
            messagebox.showinfo("Info", "Vous n'êtes pas connecté.")

    
    def load_users(self):
        """Charge les utilisateurs dans le Treeview."""
        db = Bdonnee()
        users = db.recuperer(1)  

        for item in self.tree.get_children():
            self.tree.delete(item)

        for user in users:
            self.tree.insert(
                "",
                "end",
                values=(
                    user["id"],
                    user["username"],
                    user["nom"],
                    user["prenom"],
                    user["telephone"],
                    user["email"],
                    self.get_role_name(user["role"])
                )
            )

    def display_user_image(self, event):
        """Affiche l'image de l'utilisateur sélectionné."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        user_data = self.tree.item(selected_item)["values"]
        telephone = user_data[4]  # Téléphone de l'utilisateur

        # Chemin de l'image
        image_path = os.path.join("images", f"{telephone}.png")
        if not os.path.exists(image_path):
            image_path = str(paths.PROFIL_PATH)  # Image par défaut

        self.update_image(image_path)

    def update_image(self, image_path):
        """Met à jour l'image affichée dans le Label."""
        try:
            img = Image.open(image_path)
            img = img.resize((200, 200), Image.LANCZOS)  # Utilisation directe de LANCZOS
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")


    def get_role_name(self, role):
        """Convertit un rôle (int) en texte."""
        return "Administrateur" if role == 1 else "Utilisateur"


    def navigate_to_home(self):
        settings.test = 4
        self.root.destroy()

    def navigate_to_io(self):
        settings.test = 0
        self.root.destroy()

    def navigate_to_liste(self):
        settings.test = 2
        self.root.destroy()

    def navigate_to_history(self):
        settings.test = 3
        self.root.destroy()

    def navigate_to_dashboard(self):
        """Navigation vers le tableau de bord."""
        if not settings.current_user.is_admin():
            messagebox.showwarning("Alerte", "Seul l'admin peut acceder à cette page")
            return
        settings.test = 4
        self.root.destroy()

    def _quitter(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment quitter l'application ?"):
            settings.test = -1
            # Fermer la fenêtre principale
            self.root.destroy()

    def delete_user(self):
        """Supprime un utilisateur sélectionné."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un utilisateur.")
            return

        user_data = self.tree.item(selected_item)["values"]

        if messagebox.askyesno("Confirmation", f"Voulez-vous supprimer l'utilisateur {user_data[1]} ?"):
            db = Bdonnee()
            if db.supprimer(1, user_data[0]):
                messagebox.showinfo("Succès", "Utilisateur supprimé avec succès.")
                self.load_users()
            else:
                messagebox.showerror("Erreur", "Une erreur est survenue lors de la suppression.")

    def add_user(self):
        """Affiche une boîte de dialogue pour ajouter un utilisateur avec un design amélioré."""
        dialog = Toplevel(self.root)
        dialog.title("Ajouter un utilisateur")
        dialog.geometry("800x400")  # Taille ajustée
        dialog.config(bg=self.bg_color)
        dialog.grab_set()  # Bloque la fenêtre principale
        dialog.resizable(False, False)

        # Conteneur principal avec une bordure
        form_frame = Frame(dialog, bg="#1e1e2f", bd=2, relief="ridge")
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Titre
        Label(
            form_frame,
            text="Formulaire d'ajout d'utilisateur",
            font=("Sans Serif", 20, "bold"),
            bg="#1e1e2f",
            fg="white"
        ).grid(row=0, column=0, columnspan=4, pady=15)

        # Ligne 1 : Nom d'utilisateur et Nom
        Label(form_frame, text="Nom d'utilisateur:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        username_entry = Entry(form_frame, font=("Arial", 12), width=20)
        username_entry.grid(row=1, column=1, padx=10, pady=10)

        Label(form_frame, text="Nom:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        nom_entry = Entry(form_frame, font=("Arial", 12), width=20)
        nom_entry.grid(row=1, column=3, padx=10, pady=10)

        # Ligne 2 : Prénom et Téléphone
        Label(form_frame, text="Prénom:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        prenom_entry = Entry(form_frame, font=("Arial", 12), width=20)
        prenom_entry.grid(row=2, column=1, padx=10, pady=10)

        Label(form_frame, text="Téléphone:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=2, column=2, padx=10, pady=10, sticky="w")
        telephone_entry = Entry(form_frame, font=("Arial", 12), width=20)
        telephone_entry.grid(row=2, column=3, padx=10, pady=10)

        # Ligne 3 : Email et Mot de passe
        Label(form_frame, text="Email:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        email_entry = Entry(form_frame, font=("Arial", 12), width=20)
        email_entry.grid(row=3, column=1, padx=10, pady=10)

        Label(form_frame, text="Mot de passe:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=3, column=2, padx=10, pady=10, sticky="w")
        password_entry = Entry(form_frame, show="*", font=("Arial", 12), width=20)
        password_entry.grid(row=3, column=3, padx=10, pady=10)

        # Ligne 4 : Rôle
        Label(form_frame, text="Rôle:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        role_var = StringVar(dialog)
        role_var.set("Utilisateur")
        roles = {"Utilisateur": 0, "Administrateur": 1}
        role_menu = OptionMenu(form_frame, role_var, *roles.keys())
        role_menu.config(font=("Arial", 12), bg="white")
        role_menu.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # Bouton Enregistrer
        def save_user():
            username = username_entry.get()
            nom = nom_entry.get()
            prenom = prenom_entry.get()
            telephone = telephone_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            role = roles[role_var.get()]

            if not all([username, nom, prenom, telephone, email, password]):
                messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
                return
            # Chiffrement du mot de passe
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            db = Bdonnee()
            if db.ajouter(1, [username, nom, prenom, telephone, email, password_hash, role]):
                messagebox.showinfo("Succès", "Utilisateur ajouté avec succès.")
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Erreur", "Une erreur est survenue lors de l'ajout.")

        Button(
            dialog,
            text="Enregistrer",
            command=save_user,
            bg="green",
            fg="white",
            font=("Arial", 14),
            width=15
        ).pack(pady=10)

    def edit_user(self):
        """Affiche une boîte de dialogue pour modifier un utilisateur existant."""
        # Vérification de la sélection
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un utilisateur.")
            return

        # Récupérer les données de l'utilisateur sélectionné
        user_data = self.tree.item(selected_item)["values"]

        dialog = Toplevel(self.root)
        dialog.title("Modifier un utilisateur")
        dialog.config(bg=self.bg_color)
        dialog.grab_set()  # Bloque la fenêtre principale
        dialog.geometry("800x400")  # Taille ajustée
        
        dialog.resizable(False, False)

        # Conteneur principal avec une bordure
        form_frame = Frame(dialog, bg="#1e1e2f", bd=2, relief="ridge")
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Titre
        Label(
            form_frame,
            text="Formulaire de modification d'utilisateur",
            font=("Sans Serif", 20, "bold"),
            bg="#1e1e2f",
            fg="white"
        ).grid(row=0, column=0, columnspan=4, pady=15)

        # Ligne 1 : Nom d'utilisateur et Nom
        Label(form_frame, text="Nom d'utilisateur:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        username_entry = Entry(form_frame, font=("Arial", 12), width=20)
        username_entry.insert(0, user_data[1])
        username_entry.grid(row=1, column=1, padx=10, pady=10)

        Label(form_frame, text="Nom:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        nom_entry = Entry(form_frame, font=("Arial", 12), width=20)
        nom_entry.insert(0, user_data[2])
        nom_entry.grid(row=1, column=3, padx=10, pady=10)

        # Ligne 2 : Prénom et Téléphone
        Label(form_frame, text="Prénom:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        prenom_entry = Entry(form_frame, font=("Arial", 12), width=20)
        prenom_entry.insert(0, user_data[3])
        prenom_entry.grid(row=2, column=1, padx=10, pady=10)

        Label(form_frame, text="Téléphone:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=2, column=2, padx=10, pady=10, sticky="w")
        telephone_entry = Entry(form_frame, font=("Arial", 12), width=20)
        telephone_entry.insert(0, user_data[4])
        telephone_entry.grid(row=2, column=3, padx=10, pady=10)

        # Ligne 3 : Email et Rôle
        Label(form_frame, text="Email:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        email_entry = Entry(form_frame, font=("Arial", 12), width=20)
        email_entry.insert(0, user_data[5])
        email_entry.grid(row=3, column=1, padx=10, pady=10)

        Label(form_frame, text="Rôle:", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=3, column=2, padx=10, pady=10, sticky="w")
        role_var = StringVar(dialog)
        role_var.set(user_data[6])  # Définir le rôle actuel

        roles = {"Utilisateur": 0, "Administrateur": 1}
        role_menu = OptionMenu(form_frame, role_var, *roles.keys())
        role_menu.config(font=("Arial", 12), bg="white")
        role_menu.grid(row=3, column=3, padx=10, pady=10, sticky="w")

        # Bouton Enregistrer les modif
        def update_user():
            """Enregistre les modifications pour l'utilisateur."""
            # Récupération des champs
            username = username_entry.get().strip()
            nom = nom_entry.get().strip()
            prenom = prenom_entry.get().strip()
            telephone = telephone_entry.get().strip()
            email = email_entry.get().strip()
            role = roles[role_var.get()]  # Récupérer le rôle sélectionné

            # Validation des champs
            if not all([username, nom, prenom, telephone, email]):
                messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
                return

            # Préparer les nouvelles valeurs sous forme de dictionnaire
            nouvelles_valeurs = {
                "username": username,
                "nom": nom,
                "prenom": prenom,
                "telephone": telephone,
                "email": email,
                "role": role
            }

            # Appel à la base de données pour mettre à jour
            db = Bdonnee()
            if db.modifier(1, user_data[0], nouvelles_valeurs):  # Passe un dictionnaire à la méthode 'modifier'
                messagebox.showinfo("Succès", "Utilisateur modifié avec succès.")
                dialog.destroy()  # Fermer la boîte de dialogue
                self.load_users()  # Recharger la table
            else:
                messagebox.showerror("Erreur", "Une erreur est survenue lors de la modification.")

        Button(
            dialog,
            text="Enregistrer les modifications",
            command=update_user,
            bg="orange",
            fg="white",
            font=("Arial", 14),
            width=25
        ).pack(pady=20)




