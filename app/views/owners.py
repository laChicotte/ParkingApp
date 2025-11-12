from app.utils.fonctions import *
from app.database.sqlite import Bdonnee  # Changer 'mysql' en 'sqlite' pour utiliser SQLite 
from tkinter import Canvas, Label, Button, Entry, Text, Toplevel, filedialog, messagebox, ttk
from PIL import Image, ImageTk
from app.config import settings
import webbrowser
from app.config import paths

class Owner:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Motos")
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-zoomed', True)  # Linux
        self.root.config(bg='#091821')
        self.root.protocol("WM_DELETE_WINDOW", self._quitter)

        self.bg_color = '#091821'
        self.tree = None
        self.entry_photo = None
        self.lb_img = None
        self.zone_text = None

        self.setup_ui()
        self.update_menu_state()

        img_profil = Image.open(str(paths.get_icon_path("profil.png")))  
        img_profil = img_profil.resize((70, 70), Image.Resampling.LANCZOS)
        self.icon_profil = ImageTk.PhotoImage(img_profil)
        # Charger les widgets principaux
        try:
            name = settings.current_user.name()
        except:
            name ="Anonyme"

        self.profil = Button(root, text=f"{name}", image=self.icon_profil, compound="top", 
                             font=("Arial", 10), bg='#091821', fg='white', command=self._login_logout)
        self.profil.place(relx=1.0, y=0, anchor="ne")
        
        self.afficher_owners()

    def setup_ui(self):
        # Titre principal
        Label(self.root, borderwidth=3, relief="sunken", text="Gestion des Motos", font=("Sans Serif", 30),
            bg=self.bg_color, fg="white").pack(ipadx=15)

        self.canvas = Canvas(self.root, width=900, height=680)
        self.canvas.pack(pady=15)
        Button(self.canvas, text="Exporter les données", font=('Arial', 14), bg="gray", command=self.exporter).place(
            x=680, y=50, width=220)

        # exporter les infos des motard vers html, 

        # Boutons Modifier et Supprimer
        Button(self.canvas, text="Modifier", font=('Arial', 14), bg="green", fg="white", command=self.update_owner).place(
            x=680, y=100, width=100)
        Button(self.canvas, text="Supprimer", font=('Arial', 14), bg="red", fg="white", command=self.supprimer).place(
            x=800, y=100, width=100)

        # Champ et bouton pour la recherche
        self.entry_var = StringVar()  # Stocke la valeur entrée
        self.entry = Entry(self.canvas, font=('Arial', 14), textvariable=self.entry_var)
        self.entry.place(x=680, y=160, width=220)
        Button(self.canvas, text="Rechercher", font=('Arial', 14), bg="blue", fg="white", command=self.rechercher).place(
            x=680, y=200, width=220)
        

        self.tree = ttk.Treeview(self.canvas, columns=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), height=10, show="headings")
        self.tree.heading(1, text="N°")
        self.tree.heading(2, text="Noms")
        self.tree.heading(3, text="Prénoms")
        self.tree.heading(4, text="Téléphone")
        self.tree.heading(5, text="C. Barre")
        self.tree.heading(6, text="Marque")
        self.tree.heading(7, text="Plaques")
        self.tree.heading(8, text="Couleur")
        self.tree.heading(9, text="id")
        self.tree.heading(10, text="Matricule")
        self.tree.heading(11, text="Statut")

        self.tree.column(1, width=50, anchor="center")
        self.tree.column(2, width=60)
        self.tree.column(3, width=120)
        self.tree.column(4, width=80, anchor="center")
        self.tree.column(5, width=70, anchor="center")
        self.tree.column(6, width=80, anchor="center")
        self.tree.column(7, width=80, anchor="center")
        self.tree.column(8, width=50, anchor="center")
        self.tree.column(9, width=0, stretch=False)
        self.tree.column(10, width=0, stretch=False)
        self.tree.column(11, width=0, stretch=False)

        self.tree.place(x=20, y=40, height=250, width=650)
        self.tree.bind("<<TreeviewSelect>>", self.tree_select)

        x=-40
        y=15
        # Bouton "home"
        self.home = Button(self.canvas, text="Dashboard", bg="#235F42", font=("Times New Roman", 26, ), command=self.dashboard)
        self.home.place(x=150+x, y=500+y, width=180, height=50)

        # Bouton "Ajouter"
        self.new_save = Button(self.canvas, text="Historique", bg="#235F42", font=("Times New Roman", 26), command=self._historique)
        self.new_save.place(x=340+x, y=500+y, width=170, height=50)

        # Bouton "Afficher Liste"
        self.affiche = Button(self.canvas, text="Accueil", bg="#235F42", font=("Times New Roman", 26), command=self.accueil)
        self.affiche.place(x=520+x, y=500+y, width=170, height=50)


        # Bouton "Afficher Users"
        self.user = Button(self.canvas, text="Utilisateur", bg="#235F42", font=("Times New Roman", 26), command=self._users)
        self.user.place(x=700+x, y=500+y, width=170, height=50)

        # Bouton "Afficher Users"
        self.change_pic = Button(self.canvas, text="Changer la photo", font=('Arial', 14), bg="blue", fg="white", command=self.set_photo)
        self.change_pic.place(x=450, y=480, height=30)
        
        # Zone de texte pour les informations
        self.zone_text = Text(self.canvas, font=('Arial', 16))
        self.zone_text.place(x=20, y=320, width=400, height=180)
        self.zone_text.insert("end", "Nom : \nPrénom : \nTéléphone : \nMarque : \nPlaque : \nCode Barre \nCouleur :")
        self.zone_text.config(state="disabled")

        # Zone pour afficher la photo par défaut
        try:
            img = Image.open(str(paths.PROFIL_PATH))  # Charger l'image par défaut
            img.thumbnail((150, 200))  # Redimensionner l'image
            photo_tk = ImageTk.PhotoImage(img)
            self.lb_img = Label(self.canvas, image=photo_tk)
            self.lb_img.image = photo_tk  # Conserver la référence pour éviter le garbage collector
        except FileNotFoundError:
            # Si profil.jpeg est introuvable, afficher une zone grise
            self.lb_img = Label(self.canvas, bg="gray", text="Aucune image", font=("Arial", 14), fg="white")

        self.lb_img.place(x=450, y=320)

    def _login_logout(self):
        if settings.is_connected:
            if messagebox.askyesno("Confirmation", "Voulez-vous vraiment vous deconnecter ?"):
                settings.is_connected = False
                settings.test = 0
                self.root.destroy()

    def get_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        self.entry_photo.config(state="normal")
        self.entry_photo.delete(0, "end")
        self.entry_photo.insert(0, file_path)
        self.entry_photo.config(state="readonly")

    def set_photo(self):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showwarning("Erreur", "Veuillez sélectionner une ligne.")
                return

            # Sauvegarde de la photo avec le nom correspondant au téléphone
            code = str(self.tree.item(selected_item)["values"][4]).zfill(6)
            capture_with_preview(code)
            messagebox.showinfo("Succès", "Photo ajoutée avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

    def supprimer(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item)["values"]
            id = values[8]
            print(id)
            # Vérification explicite de la réponse de l'utilisateur
            if messagebox.askquestion("Confirmation", "Voulez-vous vraiment supprimer {} ?".format(values[2] + " " + values[1])) == 'yes':
                db = Bdonnee()
                if(db.supprimer(2, id)):
                    del db
                    messagebox.showinfo("Succès", "Ligne supprimée avec succès")
                    self.afficher_owners()
                else:
                    messagebox.showwarning("error", "Echec lors de l'exécution avec la BD")
            else:
                messagebox.showwarning("Annulé", "La suppression a été annulée")
        else:
            messagebox.showinfo("Erreur", "Aucune ligne n'a été sélectionnée")


    def tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item)["values"]
          
            self.zone_text.config(state="normal")
            self.zone_text.delete("1.0", "end")
            self.zone_text.insert(
                "end", "Nom : {}\nPrénom : {}\nTélephone : {}\nMarque : {}\nPlaque : {}\nCode Barre : {}\nCouleur : {}".format(
                values[1], values[2], values[3], values[5], values[6], str(values[4]).zfill(6), values[7]))
            

            self.zone_text.config(state="disabled")
            # Zone pour afficher la photo par défaut
            try:
                path = str(paths.get_image_path("{}.png")).format(str(values[4]).zfill(6))
                img = Image.open(path)  # Charger l'image par défaut
                img.thumbnail((150, 200))  # Redimensionner l'image
                photo_tk = ImageTk.PhotoImage(img)
                self.lb_img = Label(self.canvas, image=photo_tk)
                self.lb_img.image = photo_tk  # Conserver la référence pour éviter le garbage collector
            except FileNotFoundError:
                # Si profil.jpeg est introuvable, afficher une zone grise
                self.lb_img = Label(self.canvas, bg="gray", text="Aucune image", font=("Arial", 14), fg="white")

            self.lb_img.place(x=450, y=320)


    def afficher_owners(self):
        """
        Récupère les données de l'historique à partir de la base de données
        et les affiche dans le Treeview.
        """
        # Initialiser la classe Bdonnee
        db = Bdonnee()

        # Récupérer les données des propriétaires
        owners = db.recuperer(2)
        del db
        # Effacer le contenu existant du Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ajouter les nouvelles données dans le Treeview
        i = 0
        for ligne in owners:
            i=i+1
            self.tree.insert("", "end", values=(
                i, ligne['nom'],
                ligne['prenom'], ligne['telephone'],
                str(ligne['code_barre']).zfill(6), 
                ligne['marque'], ligne['immatriculation'], 
                ligne['couleur'], ligne['id'],
                ligne['matricule'], ligne['statut']
            ))
        
    def afficher_search(self, code):
        """
        Récupère les données de l'historique à partir de la base de données
        et les affiche dans le Treeview.
        """
        # Initialiser la classe Bdonnee
        db = Bdonnee()

        # Récupérer les données des propriétaires
        owners = db.rechercher_par_code_barre(code)
        del db
        # Effacer le contenu existant du Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ajouter les nouvelles données dans le Treeview
        i = 0
        for ligne in owners:
            i=i+1
            self.tree.insert("", "end", values=(
                i, ligne['nom'],
                ligne['prenom'], ligne['telephone'],
                str(ligne['code_barre']).zfill(6), 
                ligne['marque'], ligne['immatriculation'], 
                ligne['couleur'], ligne['id']
            ))


    def _quitter(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment quitter l'application ?"):
            settings.test = -1
            # Fermer la fenêtre principale
            self.root.destroy()

    def accueil(self):
        settings.test = 0
        self.root.destroy()

    def dashboard(self):
        if not settings.current_user.is_admin():
            messagebox.showwarning("Alerte", "Seul l'admin peut acceder à cette page")
            return
        settings.test = 4
        self.root.destroy()

    def _historique(self):
        settings.test = 3
        self.root.destroy()

    def _users(self):
        if not settings.current_user.is_admin():
            messagebox.showwarning("Alerte", "Seul l'admin peut acceder à cette page")
            return
        settings.test = 1
        self.root.destroy()


    def update_owner(self):
        """
        Affiche un formulaire pré-rempli pour modifier les informations d'une personne.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Erreur", "Aucune ligne n'a été sélectionnée.")
            return

        values = self.tree.item(selected_item)["values"]
        row_id = values[8]  # ID de la ligne dans la base de données

        """Affiche une boîte de dialogue pour ajouter un utilisateur avec un design amélioré."""
        dialog = Toplevel(self.root)
        dialog.title("Modifier un Propriétaire")
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
            text="Formulaire de Modification d'informations",
            font=("Sans Serif", 20, "bold"),
            bg="#1e1e2f",
            fg="white"
        ).grid(row=0, column=0, columnspan=4, pady=15)

        # Ligne 1 : Nom d'utilisateur et Nom
        Label(form_frame, text="Nom : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        nom_entry = Entry(form_frame, font=("Arial", 12), width=20)
        nom_entry.insert(0, values[1])
        nom_entry.grid(row=1, column=1, padx=10, pady=10)
        
        Label(form_frame, text="Prénom : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        prenom_entry = Entry(form_frame, font=("Arial", 12), width=20)
        prenom_entry.insert(0, values[2])
        prenom_entry.grid(row=1, column=3, padx=10, pady=10)

        # Ligne 2 : Prénom et Téléphone
        Label(form_frame, text="Matricule :", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        mat_entry = Entry(form_frame, font=("Arial", 12), width=20)
        mat_entry.insert(0, values[9])
        mat_entry.grid(row=2, column=1, padx=10, pady=10)

        Label(form_frame, text="Téléphone : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=2, column=2, padx=10, pady=10, sticky="w")
        tel_entry = Entry(form_frame, font=("Arial", 12), width=20)
        tel_entry.insert(0, values[3])
        tel_entry.grid(row=2, column=3, padx=10, pady=10)

        # Ligne 3 : Plaque et code barre
        Label(form_frame, text="Plaque : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        plaque_entry = Entry(form_frame, font=("Arial", 12), width=20)
        plaque_entry.insert(0, values[6])
        plaque_entry.grid(row=3, column=1, padx=10, pady=10)

        Label(form_frame, text="Code Barre : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=3, column=2, padx=10, pady=10, sticky="w")
        code_entry = Entry(form_frame, font=("Arial", 12), width=20)
        code_entry.insert(0, values[4])
        code_entry.grid(row=3, column=3, padx=10, pady=10)

        # Ligne 4 : Plaque et code barre
        Label(form_frame, text="Marque :", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        marq_entry = Entry(form_frame, font=("Arial", 12), width=20)
        marq_entry.insert(0, values[5])
        marq_entry.grid(row=4, column=1, padx=10, pady=10)

        Label(form_frame, text="Couleur : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=4, column=2, padx=10, pady=10, sticky="w")
        color = StringVar(dialog)
        color.set(values[7])

        colors = ["Rouge", "Noire", "Bleue", "Blanche", "Cendre", "Autres"]
        color_menu = OptionMenu(form_frame, color,  *colors)
        color_menu.config(font=("Arial", 12), bg="white")
        color_menu.grid(row=4, column=3, padx=10, pady=10, sticky="w")

        # Ligne 5 : Statut et couleur
        Label(form_frame, text="Statut : *", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold")).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        statut = StringVar(dialog)
        statut.set(values[-1])
       

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


            if not all([nom or prenom]):
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
            if not all([state or col]) : 
                messagebox.showwarning("Alerte", "Les champs statut et couleur sont obligatoires.")
                return

            code_barre = convertir_caracteres_en_chiffres(code)
            # Ajouter dans la base de données
            values = [nom, prenom, mat, marque, plaque, telephone, code_barre, col, state]

            # Clés correspondant aux colonnes de la table "owners"
            keys = ["nom", "prenom", "matricule", "marque", "immatriculation", "telephone", "code_barre", "couleur", "statut"]

            # Création du dictionnaire (JSON)
            nouvelles_valeurs = dict(zip(keys, values))

            # Appel à la base de données pour mettre à jour
            db = Bdonnee()
            test, sms = db.verifier_existence(code_barre, plaque)
            if(test):
                messagebox.showerror("Attention", sms)
                return
            
            if db.modifier(2, row_id, nouvelles_valeurs):  # Passe un dictionnaire à la méthode 'modifier'
                messagebox.showinfo("Succès", "Modification effectuées avec succès.")
                dialog.destroy()  # Fermer la boîte de dialogue
                self.afficher_owners()  # Recharger la table
            else:
                messagebox.showerror("Erreur", "Une erreur est survenue lors de la modification.")
           
        Button(
            dialog,
            text="Enregistrer",
            command=save_user,
            bg="green",
            fg="white",
            font=("Arial", 14),
            width=15
        ).pack(pady=10)

    def rechercher(self):
        """
        Récupère les données de l'historique à partir de la base de données
        et les affiche dans le Treeview.
        """
        valeur = self.entry_var.get().strip()  # 🔍 Récupère la valeur entrée dans le champ de recherche

        if not valeur:
            messagebox.showwarning("Alerte", "Veuillez entrer un code-barre ou un téléphone à rechercher.")
            self.afficher_owners()
            return

        # Initialiser la classe Bdonnee
        db = Bdonnee()

        # Récupérer les données des propriétaires
        owners = db.rechercher_owner(valeur)

        if not owners:
            messagebox.showinfo("Info", "Aucun propriétaire trouvé pour cette valeur.")
            return

        del db

        # Effacer le contenu existant du Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ajouter les nouvelles données dans le Treeview
        for i, ligne in enumerate(owners, start=1):
            self.tree.insert("", "end", values=(
                i, ligne['nom'], ligne['prenom'], ligne['telephone'],
                str(ligne['code_barre']).zfill(6), ligne['marque'],
                ligne['immatriculation'], ligne['couleur'],
                ligne['id'], ligne['matricule'], ligne['statut']
            ))

    def exporter(self):
        # Création d'une instance de la base de données
        db = Bdonnee()

        # Récupération des données des propriétaires (owners = indice 2)
        liste_motards = db.recuperer(2)

        # Structure de base du fichier HTML
        contenu_html = """<!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Ukag Parking</title>
                <style>
                    /* Styles généraux */
                    body {
                        font-family: Arial, sans-serif;
                        text-align: center;
                        background: linear-gradient(to right, #4CAF50, #2196F3);
                        color: white;
                        padding: 20px;
                    }

                    h1 {
                        font-size: 28px;
                        margin-bottom: 20px;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
                    }

                    /* Table stylisée */
                    table {
                        width: 90%;
                        margin: 20px auto;
                        border-collapse: collapse;
                        background: white;
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
                        color: black;
                    }

                    th, td {
                        border: 1px solid #ddd;
                        padding: 12px;
                        text-align: center;
                    }

                    th {
                        background-color: #2196F3;
                        color: white;
                        text-transform: uppercase;
                        font-size: 14px;
                    }

                    /* Style des lignes */
                    tbody tr:nth-child(odd) {
                        background-color: #f9f9f9;
                    }

                    tbody tr:nth-child(even) {
                        background-color: #e3f2fd;
                    }

                    tbody tr:hover {
                        background-color: #c8e6c9;
                        transform: scale(1.02);
                        transition: all 0.2s ease-in-out;
                    }

                    /* Style des images */
                    td img {
                        width: 80px;
                        height: 60px;
                        object-fit: cover;
                        border-radius: 8px;
                        display: block;
                        border: 2px solid #4CAF50;
                    }

                    td:last-child {
                        padding: 5px;
                    }

                </style>
            </head>
            <body>
                🚀 Liste des Motos UKAG 🏍️
                <table>
                    <tr>
                        <th>C. Barre</th>
                        <th>Nom & Prénom</th>
                        <th>Téléphone</th>
                        <th>Marque</th>
                        <th>Plaques</th>
                        <th>Couleur</th>
                        <th>Matricule</th>
                        <th>Statut</th>
                        <th>Photo</th>
                    </tr>
                """ 

        # Ajout des lignes du tableau
        for motard in liste_motards:
            nom = motard.get("nom", "N/A")
            prenom = motard.get("prenom", "N/A")
            telephone = motard.get("telephone", "N/A")
            marque = motard.get("marque", "------")
            plaques = motard.get("immatriculation", "N/A")
            couleur = motard.get("couleur", "N/A")
            matricule = motard.get("matricule", "Non renseigné")
            statut = motard.get("statut", "N/A")
            code_barre = motard.get("code_barre", "erreur")  # Utilisé pour le nom de l'image

            image_path = fstr(paths.get_image_path("{code_barre}.png"))

            contenu_html += f"""
            <tr>
                <td>{code_barre}</td>
                <td>{nom} {prenom}</td>
                <td>{telephone}</td>
                <td>{marque}</td>
                <td>{plaques}</td>
                <td>{couleur}</td>
                <td>{matricule}</td>
                <td>{statut}</td>
                <td><img src="{image_path}" alt="Photo de {nom}"></td>
            </tr>
            """

        # Fermeture des balises HTML
        contenu_html += """
        </table>
        </body>
        </html>
        """

        # Écriture du fichier HTML
        with open("motards.html", "w", encoding="utf-8") as fichier:
            fichier.write(contenu_html)

        # Ouvrir le fichier HTML dans le navigateur par défaut
        webbrowser.open("motards.html")

    def update_menu_state(self):
        """
        Met à jour l'état des boutons du menu en fonction du rôle de l'utilisateur.
        """
        if settings.is_connected:
            if not settings.current_user.is_admin():
                self.home.config(state="disabled")  # Désactive le bouton Dashboard
                self.user.config(state="disabled")  # Désactive le bouton Utilisateur
        else:
            self.home.config(state="disabled")
            self.user.config(state="disabled")


