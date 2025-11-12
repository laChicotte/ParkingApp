from app.utils.fonctions import *
from PIL import Image, ImageTk
from app.database.sqlite import Bdonnee  # Changer 'mysql' en 'sqlite' pour utiliser SQLite
from app.views.dashboard import Dashboard
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.views.connexion import Connexion
from app.config import settings
from app.config import paths

class Accueil:
    def __init__(self, root):
        self.root = root
        self.root.title("Parking Kofi")
        self.root.config(bg='#091821')
        self.root.protocol("WM_DELETE_WINDOW", self._quitter)
        # Activer le mode plein écran
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-zoomed', True)  # Linux

        self.scanning = False  # État du scannage

        img_entree = Image.open(str(paths.get_icon_path("enter.jpeg")))  
        img_entree = img_entree.resize((150, 70), Image.Resampling.LANCZOS)
        self.icon_entree = ImageTk.PhotoImage(img_entree)

        img_sortie = Image.open(str(paths.get_icon_path("exit.jpeg")))  
        img_sortie = img_sortie.resize((150, 70), Image.Resampling.LANCZOS)
        self.icon_sortie = ImageTk.PhotoImage(img_sortie)

        img_stop = Image.open(str(paths.get_icon_path("stop.png")))  
        img_stop = img_stop.resize((70, 70), Image.Resampling.LANCZOS)
        self.icon_stop = ImageTk.PhotoImage(img_stop)

        # Liste pour stocker les boutons du menu
        self.menu_buttons = []

        # Charger les widgets principaux
        self.setup_ui()

        img_profil = Image.open(str(paths.get_icon_path("profil.png")))  
        img_profil = img_profil.resize((70, 70), Image.Resampling.LANCZOS)
        self.icon_profil = ImageTk.PhotoImage(img_profil)
        
        name = settings.current_user.name() if settings.is_connected else "Connexion"

        self.profil = Button(root, text=f"{name}", image=self.icon_profil, compound="top", 
                             font=("Arial", 10), bg='#091821', fg='white', command=self._login_logout)
        self.profil.place(relx=1.0, y=0, anchor="ne")

        # Ajouter les boutons de navigation à la liste
        self.menu_buttons = [
            self.affiche,  # Bouton Motos
            self.user,     # Bouton Users
            self.home,     # Bouton Dashboard
            self.new_save  # Bouton Ajouter
        ]

        # Mise à jour initiale de l'état du menu
        self.update_menu_state()

    def setup_ui(self):
        # Titre principal
        Label(self.root, borderwidth=3, relief="sunken", text="Gestion Des Entrées/Sorties",
              font=("Sans Serif", 30), bg="#091821", fg="white").pack(ipadx=15)

        # Canvas principal
        self.canvas = Frame(self.root, width=1000, height=680)
        self.canvas.pack(pady=15)

        # Etat du scan
        self.encours = Label(self.canvas, text="Scan arrêté", font=('Arial', 16), fg='black')
        self.encours.place(x=390, y=367, width=300)
        
        # Titre de la date du jour
        lb_jour_j = Label(self.canvas, bg='green', text="Le " + today(1), font=('Algerian', 26), fg='white')
        lb_jour_j.place(x=400, y=6, width=300)

        # Bouton "Entrée"
        self.entree = Button(self.canvas, image=self.icon_entree, command=self.start_scanning)
        self.entree.place(x=220, y=400, width=150, height=70)

        # Bouton "Sortie"
        self.sortie = Button(self.canvas, image=self.icon_sortie, command=self.action_sortie)
        self.sortie.place(x=450, y=400, width=150, height=70)

        # Bouton "Stop"
        self.stop = Button(self.canvas, image=self.icon_stop, command=self.stop_scanning, state="disabled")
        self.stop.place(x=670, y=400, width=70, height=70)

        # Bouton "home"
        self.home = Button(self.canvas, text="Dashboard", bg="#235F42", font=("Times New Roman", 26), command=self._home_page)
        self.home.place(x=150, y=500, width=180, height=50)

        # Bouton "Ajouter"
        self.new_save = Button(self.canvas, text="Ajouter", bg="#235F42", font=("Times New Roman", 26), command=self.add_owner)
        self.new_save.place(x=340, y=500, width=170, height=50)

        # Bouton "Afficher Liste"
        self.affiche = Button(self.canvas, text="Motos", bg="#235F42", font=("Times New Roman", 26), command=self.afficher_liste)
        self.affiche.place(x=520, y=500, width=170, height=50)

        # Bouton "Afficher Users"
        self.user = Button(self.canvas, text="Users", bg="#235F42", font=("Times New Roman", 26), command=self._user_page)
        self.user.place(x=700, y=500, width=170, height=50)

        # Champ caché pour capturer les entrées du scannage
        self.hidden_entry = Entry(self.root, font=("Arial", 12))
        self.hidden_entry.bind("<Return>", self.on_barcode_entry)
        self.hidden_entry.place(x=-100, y=-100)  # Invisible

        # Champ caché pour capturer les entrées du scannage
        self.hidden_entry1 = Entry(self.root, font=("Arial", 12))
        self.hidden_entry1.bind("<Return>", self.on_barcode_exit)
        self.hidden_entry1.place(x=-200, y=-200)  # Invisible

        # Zone pour afficher une photo
        load = Image.open(str(paths.PROFIL_PATH))
        load.thumbnail((400, 300))
        img = ImageTk.PhotoImage(load)
        self.lb_img = Label(self.canvas, image=img)
        self.lb_img.place(x=70, y=60)

        try:
            photo = Image.open(fstr(paths.PROFIL_PATH))
        except FileNotFoundError:
            photo = Image.open(str(paths.PROFIL_PATH))
        photo.thumbnail((400, 300))
        photo_tk = ImageTk.PhotoImage(photo)
        self.lb_img.config(image=photo_tk)
        self.lb_img.image = photo_tk

        # Zone de texte pour les détails
        self.zone_text = Text(self.canvas, font=('Arial', 24))
        self.zone_text.place(x=500, y=60, width=450, height=300)
        self.zone_text.insert("end", "Nom : \nMatricule : \nMarque : \nPlaque : \nCode : \nTél : \nStatut : ")
        self.zone_text.config(state="disabled")
        self.disabled_menu()
    
    def disabled_menu(self):
        if not settings.is_connected:
            self.affiche.config(state="disabled")
            self.user.config(state="disabled")
            self.home.config(state="disabled")
            self.new_save.config(state="disabled")
        else:
            self.affiche.config(state="normal")
            self.user.config(state="normal")
            self.home.config(state="normal")
            self.new_save.config(state="normal")

    def start_scanning(self):
        if not settings.current_user.has_permission("scan_entries"):
            messagebox.showwarning("Alerte", "Vous n'avez pas les permissions nécessaires pour scanner les entrées")
            return
        self.scanning = True
        self.encours.config(text="Entrée en cours...")
        self.entree.config(state="disabled")
        self.sortie.config(state="disabled")
        self.stop.config(state="normal")
        messagebox.showinfo("Info", "Le scannage a démarré. Scannez un code-barres.")
        self.hidden_entry.focus_set()

    def stop_scanning(self):
        self.encours.config(text="Scan arrêté")
        self.scanning = False
        self.entree.config(state="normal")
        self.sortie.config(state="normal")
        self.stop.config(state="disabled")
        self.hidden_entry.delete(0, "end")
        messagebox.showinfo("Info", "Le scannage a été arrêté.")

    def on_barcode_entry(self, event):
        if self.scanning:
            barcode = self.hidden_entry.get()
            if barcode:
                self.scan_display(barcode, True)
                self.hidden_entry.delete(0, "end")

    def on_barcode_exit(self, event):
        if self.scanning:
            barcode = self.hidden_entry1.get()
            if barcode:
                self.scan_display(barcode, False)
                self.hidden_entry1.delete(0, "end")

    def scan_display(self, scanned_code, state):
        converted_code = convertir_caracteres_en_chiffres(scanned_code)
        db = Bdonnee()
        resultat = db.rechercher_par_code_barre(converted_code)

        if resultat:
            # Mettre à jour les informations
            self.zone_text.config(state="normal")
            self.zone_text.delete("1.0", "end")
            self.zone_text.insert("end", f"Nom : {resultat['nom']} \n")
            self.zone_text.insert("end", f"Prénom : {resultat['prenom']} \n")
            self.zone_text.insert("end", f"Matricule : {resultat['matricule']} \n")
            self.zone_text.insert("end", f"Marque : {resultat['marque']} \n")
            self.zone_text.insert("end", f"Plaque : {resultat['immatriculation']} \n")
            self.zone_text.insert("end", f"Tél : {resultat['telephone']} \n")
            self.zone_text.insert("end", f"Couleur : {resultat['couleur']} \n")
            self.zone_text.config(state="disabled")

            # Charger la photo associée
            self.set_photo(f"{converted_code}.png")

            if state:
                # Ajouter à l'historique
                if not db.ajouter_historique(today(1), resultat['id'], "Entrée", today(0)):
                    messagebox.showwarning("Echec", "Entré non enregistré.")
            else:
                # Ajouter à l'historique
                if not db.ajouter_historique(today(1), resultat['id'], "Sortie", today(0)):
                    messagebox.showwarning("Échec", "Sortie non enregistrée.")

        else:
            messagebox.showwarning("Non trouvé", "Aucune donnée trouvée pour ce code-barre.")

    def action_sortie(self):
        if not settings.current_user.has_permission("scan_exits"):
            messagebox.showwarning("Alerte", "Vous n'avez pas les permissions nécessaires pour scanner les sorties")
            return
        self.encours.config(text="Sortie en cours...")
        self.scanning = True
        self.entree.config(state="disabled")
        self.sortie.config(state="disabled")
        self.stop.config(state="normal")
        messagebox.showinfo("Info", "Le scannage a démarré. Scannez un code-barres.")
        self.hidden_entry1.focus_set()

    def set_photo(self, photo_nom):
        try:
            photo = Image.open(fstr(paths.get_image_path("{photo_nom}")))
        except FileNotFoundError:
            photo = Image.open("img.png")
        photo.thumbnail((400, 300))
        photo_tk = ImageTk.PhotoImage(photo)
        self.lb_img.config(image=photo_tk)
        self.lb_img.image = photo_tk

    def _user_page(self):
        if not settings.current_user.has_permission("manage_users"):
            messagebox.showwarning("Alerte", "Vous n'avez pas les permissions nécessaires pour accéder à cette page")
            return
        settings.test = 1
        self.root.destroy()

    def _quitter(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment quitter l'application ?"):
            settings.test = 20
            settings.is_connected = False
            settings.current_user = settings.User()
            # Fermer la fenêtre principale
            self.root.destroy()

    def add_owner(self):
        
        """Affiche une boîte de dialogue pour ajouter un utilisateur avec un design amélioré."""
        
        dialog = Toplevel(self.root)
        dialog.title("Ajouter un Propriétaire")
        dialog.geometry("800x450")  # Taille ajustée
        dialog.config(bg="#091821")
        dialog.grab_set()  # Bloque la fenêtre principale
        dialog.resizable(False, False)

        # Conteneur principal avec une bordure
        form_frame = Frame(dialog, bg="#1e1e2f", bd=2, relief="ridge")
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Titre
        Label(
            form_frame,
            text="Formulaire d'ajout d'un Propriétaire",
            font=("Sans Serif", 20, "bold"),
            bg="#1e1e2f",
            fg="white"
        ).grid(row=0, column=0, columnspan=4, pady=15)

        # Ligne 1 : Nom d'utilisateur et Nom
        Label(form_frame, text="Nom : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        nom_entry = Entry(form_frame, font=("Arial", 12), width=20)
        nom_entry.grid(row=1, column=1, padx=10, pady=10)

        Label(form_frame, text="Prénom : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        prenom_entry = Entry(form_frame, font=("Arial", 12), width=20)
        prenom_entry.grid(row=1, column=3, padx=10, pady=10)

        # Ligne 2 : Prénom et Téléphone
        Label(form_frame, text="Matricule :", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        mat_entry = Entry(form_frame, font=("Arial", 12), width=20)
        mat_entry.grid(row=2, column=1, padx=10, pady=10)

        Label(form_frame, text="Téléphone : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=2, column=2, padx=10, pady=10, sticky="w")
        tel_entry = Entry(form_frame, font=("Arial", 12), width=20)
        tel_entry.grid(row=2, column=3, padx=10, pady=10)

        # Ligne 3 : Plaque et code barre
        Label(form_frame, text="Plaque : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        plaque_entry = Entry(form_frame, font=("Arial", 12), width=20)
        plaque_entry.grid(row=3, column=1, padx=10, pady=10)

        Label(form_frame, text="Code Barre : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=3, column=2, padx=10, pady=10, sticky="w")
        code_entry = Entry(form_frame, font=("Arial", 12), width=20)
        code_entry.grid(row=3, column=3, padx=10, pady=10)

        # Ligne 4 : Plaque et code barre
        Label(form_frame, text="Marque :", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        marq_entry = Entry(form_frame, font=("Arial", 12), width=20)
        marq_entry.grid(row=4, column=1, padx=10, pady=10)

        Label(form_frame, text="Couleur : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=4, column=2, padx=10, pady=10, sticky="w")
        color = StringVar(dialog)
        color.set("")

        colors = ["Rouge", "Noire", "Bleue", "Blanche", "Cendre", "Autres"]
        color_menu = OptionMenu(form_frame, color,  *colors)
        color_menu.config(font=("Arial", 12), bg="white")
        color_menu.grid(row=4, column=3, padx=10, pady=10, sticky="w")

        # Ligne 5 : Statut et couleur
        Label(form_frame, text="Statut : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        statut = StringVar(dialog)
        statut.set("")

        roles = ["Etudiant", "Enseignant", "Personnel", "Autre"]
        statut_menu = OptionMenu(form_frame, statut, *roles)
        statut_menu.config(font=("Arial", 12), bg="white")
        statut_menu.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        # Bouton Enregistrer
        def save_user():
            plaque = plaque_entry.get()
            nom = nom_entry.get()
            prenom = prenom_entry.get()
            telephone = tel_entry.get()
            code = code_entry.get()
            mat = mat_entry.get()
            col = color.get()
            state = statut.get()
            marque = marq_entry.get()

            if not all([nom, prenom]):
                messagebox.showwarning("Alerte", "Les champs nom et prenom sont obligatoires.")
                return
            if not plaque:
                messagebox.showwarning("Alerte", "Le numéro de plaque est obligatoire.")
                return
            if not code:
                messagebox.showwarning("Alerte", "Le numéro de code barre est obligatoire.")
                return
            if not telephone:
                messagebox.showwarning("Alerte", "Le numéro de téléphone est obligatoire.")
                return
            if not all([state, col]) : 
                messagebox.showwarning("Alerte", "Les champs statut et couleur sont obligatoires.")
                return

            code_barre = convertir_caracteres_en_chiffres(code)
            # Ajouter dans la base de données
            db = Bdonnee()
            test, sms = db.verifier_existence(code_barre, plaque)
            if(test):
                messagebox.showerror("Attention", sms)
                return
            
            success = db.ajouter(2, [nom, prenom, mat, marque, plaque, telephone, code_barre, col, state])
            del db

            if success:
                messagebox.showinfo("Succès", "La personne a été ajoutée avec succès.")
                settings.test =2
                self.root.destroy()
            else:
                messagebox.showerror("Erreur", "Échec de l'ajout. Vérifiez les données.")
           
        Button(
            dialog,
            text="Enregistrer",
            command=save_user,
            bg="green",
            fg="white",
            font=("Arial", 14),
            width=15
        ).pack(pady=10)

    def afficher_liste(self):
        if not settings.is_connected:
            messagebox.showwarning("Alerte", "Vous devez être connecté pour accéder à cette page")
            self._login_logout()
            return
        if not settings.current_user.has_permission("view_entries"):
            messagebox.showwarning("Alerte", "Vous n'avez pas les permissions nécessaires pour accéder à cette page")
            return
        settings.test = 2
        self.root.destroy()

    def _login_logout(self):
        if settings.is_connected:
            if messagebox.askyesno("Confirmation", "Voulez-vous vraiment vous déconnecter ?"):
                settings.logout()  # Utilise la fonction centralisée
                self.reset_interface()  # Réinitialise l'interface
                self.root.destroy()  # Ferme la fenêtre actuelle pour forcer le retour à l'accueil
        else:
            # Ouvrir la fenêtre de connexion
            login_window = Connexion(self.root)
            self.root.wait_window(login_window.log)  # Attendre que la fenêtre de connexion soit fermée
            
            # Mettre à jour l'interface après la connexion
            if settings.is_connected:
                self.profil.config(text=settings.current_user.name())
                self.update_menu_state()
                self.root.update_idletasks()  # Forcer la mise à jour de l'interface

    def reset_interface(self):
        """Réinitialise l'interface après la déconnexion."""
        # Réinitialiser le profil
        self.profil.config(text="Connexion")
        
        # Désactiver tous les boutons de navigation
        self.disable_menu()
        
        # Réinitialiser la zone de texte
        self.zone_text.config(state="normal")
        self.zone_text.delete("1.0", "end")
        self.zone_text.insert("end", "Nom : \nMatricule : \nMarque : \nPlaque : \nCode : \nTél : \nStatut : ")
        self.zone_text.config(state="disabled")
        
        # Réinitialiser l'image
        self.set_photo(str(paths.PROFIL_PATH))
        
        # Réinitialiser l'état du scan
        self.scanning = False
        self.encours.config(text="Scan arrêté")
        self.entree.config(state="normal")
        self.sortie.config(state="normal")
        self.stop.config(state="disabled")
        
        # Forcer la mise à jour de l'interface
        self.root.update_idletasks()

    def _home_page(self):
        if not settings.current_user.has_permission("view_dashboard"):
            messagebox.showwarning("Alerte", "Vous n'avez pas les permissions nécessaires pour accéder à cette page")
            return
        settings.test = 4
        self.root.destroy()

    def update_menu_state(self):
        """
        Met à jour l'état des boutons du menu en fonction de l'état de connexion et du rôle.
        """
        if settings.is_connected:
            self.profil.config(text=settings.current_user.name())
            # Activer tous les boutons par défaut
            self.enable_menu()
            # Désactiver les boutons spécifiques si l'utilisateur n'est pas admin
            if not settings.current_user.is_admin():
                self.home.config(state="disabled")  # Désactive le bouton Dashboard
                self.user.config(state="disabled")  # Désactive le bouton Utilisateur
        else:
            self.profil.config(text="Connexion")
            self.disable_menu()
        self.root.update_idletasks()

    def enable_menu(self):
        """
        Active tous les boutons du menu.
        """
        for button in self.menu_buttons:
            button.config(state="normal")

    def disable_menu(self):
        """
        Désactive tous les boutons du menu sauf Connexion.
        """
        for button in self.menu_buttons:
            button.config(state="disabled")