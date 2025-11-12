from app.database.sqlite import Bdonnee  # Changer 'mysql' en 'sqlite' pour utiliser SQLite 
from tkinter import Canvas, Label, Button, Entry, Text, filedialog, messagebox, ttk
from PIL import Image, ImageTk
from app.config import settings
from app.config import paths


class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Historique")
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-zoomed', True)  # Linux
        self.root.protocol("WM_DELETE_WINDOW", self._quitter)
        self.root.config(bg='#091821')

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

        self.afficher_historique()


    def _login_logout(self):
        if settings.is_connected:
            if messagebox.askyesno("Confirmation", "Voulez-vous vraiment vous deconnecter ?"):
                settings.is_connected = False
                settings.test = 0
                self.root.destroy()


    def _quitter(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment quitter l'application ?"):
            settings.test = -1
            # Fermer la fenêtre principale
            self.root.destroy()

    def setup_ui(self):
        # Titre principal
        Label(self.root, borderwidth=3, relief="sunken", text="Gestion de l'Historique", font=("Sans Serif", 30),
            bg=self.bg_color, fg="white").pack(ipadx=15)

        self.canvas = Canvas(self.root, width=900, height=680)
        self.canvas.pack(pady=15)
        y = 220
        x = -20
        # Bouton Supprimer
        Button(self.canvas, text="Actualiser", font=('Arial', 14), bg="green", fg="white", command=self.afficher_historique).place(
            x=680+x, y=100+y, width=220)

        # Champ et bouton pour la recherche
        Entry(self.canvas, font=('Arial', 14)).place(x=680+x, y=160+y, width=220)
        Button(self.canvas, text="Rechercher", font=('Arial', 14), bg="blue", fg="white", command=self.rechercher).place(
            x=680+x, y=200+y, width=220)
        

        # Boutton de navigation
        x=-60
        y=0
        # Bouton "home"
        self.home = Button(self.canvas, text="Dashboard", bg="#235F42", font=("Times New Roman", 26, ), command=self._dashboard)
        self.home.place(x=150+x, y=500+y, width=180, height=50)

        # Bouton "Ajouter"
        self.new_save = Button(self.canvas, text="Motos", bg="#235F42", font=("Times New Roman", 26), command=self._liste)
        self.new_save.place(x=340+x, y=500+y, width=170, height=50)

        # Bouton "Afficher Liste"
        self.affiche = Button(self.canvas, text="Accueil", bg="#235F42", font=("Times New Roman", 26), command=self._accueil)
        self.affiche.place(x=520+x, y=500+y, width=170, height=50)

        # Bouton "Afficher Users"
        self.user = Button(self.canvas, text="Utilisateur", bg="#235F42", font=("Times New Roman", 26), command=self._user_page)
        self.user.place(x=700+x, y=500+y, width=170, height=50)

        
        self.tree = ttk.Treeview(self.canvas, columns=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), height=10, show="headings")
        self.tree.heading(1, text="ID")
        self.tree.heading(2, text="Dates")
        self.tree.heading(3, text="Prénom et Nom")
        self.tree.heading(4, text="C. Barre")
        self.tree.heading(5, text="Téléphone")
        self.tree.heading(6, text="Marque")
        self.tree.heading(7, text="Plaques")
        self.tree.heading(8, text="Type")
        self.tree.heading(9, text="Heure")
        self.tree.heading(10, text="id")

        self.tree.column(1, width=50, anchor="center")
        self.tree.column(2, width=70, anchor="center")
        self.tree.column(3, width=160)
        self.tree.column(4, width=50, anchor="center")
        # self.tree.column(5, width=0, stretch=False)
        self.tree.column(5, width=80)
        self.tree.column(6, width=80)
        self.tree.column(7, width=70)
        self.tree.column(8, width=80, anchor="center")
        self.tree.column(9, width=50, anchor="center")
        self.tree.column(10, width=0, stretch=False)

        self.tree.place(x=60, y=40, height=250, width=780)
        self.tree.bind("<<TreeviewSelect>>", self.tree_select)

        
        # Zone de texte pour les informations
        self.zone_text = Text(self.canvas, font=('Arial', 12))
        self.zone_text.place(x=20, y=320, width=400, height=150)
        self.zone_text.insert("end", "Nom : \nMatricule : \nMarque : \nTéléphone : \nStatut :")
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

            photo_path = self.entry_photo.get()
            if not photo_path:
                messagebox.showwarning("Erreur", "Aucune photo sélectionnée.")
                return

            # Sauvegarde de la photo avec le nom correspondant au téléphone
            tel = self.tree.item(selected_item)["values"][4]
            img = Image.open(photo_path)
            img.save(fstr(paths.get_image_path("{tel}.png")))
            messagebox.showinfo("Succès", "Photo ajoutée avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")


    def rechercher(self):
        messagebox.showinfo("Rechercher", "Logique pour rechercher ici")

    def tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            statut = "N'est pas à l'interieur"
            values = self.tree.item(selected_item)["values"]
            if values[8] == "------":
                statut = "Est à l'interieur"
            self.zone_text.config(state="normal")
            self.zone_text.delete("1.0", "end")
            self.zone_text.insert("end", "Nom : {}\nTélephone : {}\nMarque : {}\nPlaque : {}\nCode Barre : {}\nStatut : {}".format(
                values[2], values[4], values[5], values[6], str(values[3]).zfill(6), statut))
            

            self.zone_text.config(state="disabled")
            # Zone pour afficher la photo par défaut
            try:
                path = str(paths.get_image_path("{}.png")).format(str(values[3]).zfill(6))
                img = Image.open(path)  # Charger l'image par défaut
                img.thumbnail((150, 150))  # Redimensionner l'image
                photo_tk = ImageTk.PhotoImage(img)
                self.lb_img = Label(self.canvas, image=photo_tk)
                self.lb_img.image = photo_tk  # Conserver la référence pour éviter le garbage collector
            except FileNotFoundError:
                # Si profil.jpeg est introuvable, afficher une zone grise
                self.lb_img = Label(self.canvas, bg="gray", text="Aucune image", font=("Arial", 14), fg="white")

            self.lb_img.place(x=450, y=320)


    def afficher_historique(self):
        """
        Récupère les données de l'historique à partir de la base de données
        et les affiche dans le Treeview.
        """
        # Initialiser la classe Bdonnee
        db = Bdonnee()

        # Récupérer les données de l'historique
        historique = db.recuperer_historique()

        # Effacer le contenu existant du Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ajouter les nouvelles données dans le Treeview
        i = 0
        for ligne in historique:
            prenom_nom = f"{ligne['prenom']} {ligne['nom']}"  # Concaténer prénom et nom
            i=i+1
            self.tree.insert("", "end", values=(
                i, ligne['date'],
                prenom_nom, str(ligne['code_barre']), ligne['telephone'],
                ligne['marque'], ligne['immatriculation'], 
                ligne['etat'], ligne['heure'], ligne['historique_id']
            ))
    
    def _user_page(self):
        if not settings.current_user.is_admin():
            messagebox.showwarning("Alerte", "Seul l'admin peut acceder à cette page")
            return
        settings.test = 1
        self.root.destroy()

    def _accueil(self):
        settings.test = 0
        self.root.destroy()

    def _dashboard(self):
        if not settings.current_user.is_admin():
            messagebox.showwarning("Alerte", "Seul l'admin peut acceder à cette page")
            return
        settings.test = 4
        self.root.destroy()

    def _liste(self):
        settings.test = 2
        self.root.destroy()

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
