"""
Vue Historique modernisée avec tableau
"""
from tkinter import Frame, Label, Entry, Button, Text, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from app.database.sqlite import Bdonnee
from app.config import theme, paths, settings


class HistoriqueView(Frame):
    """Vue de l'historique avec tableau moderne"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=theme.Colors.BG_SECONDARY)
        self.main_window = main_window
        self.setup_ui()
        self.afficher_historique()
    
    def setup_ui(self):
        """Configure l'interface"""
        # Titre et barre d'outils
        header_frame = Frame(self, bg=theme.Colors.BG_SECONDARY)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        title = Label(
            header_frame,
            text="Historique des Entrées/Sorties",
            font=("Arial", 24, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY
        )
        title.pack(side="left")
        
        # Bouton actualiser
        refresh_btn = ttk.Button(
            header_frame,
            text="🔄 Actualiser",
            command=self.afficher_historique,
            style="Primary.TButton"
        )
        refresh_btn.pack(side="right", padx=10)

        # Bouton vider l'historique (admin uniquement)
        if settings.is_connected and settings.current_user.is_admin():
            ttk.Button(
                header_frame,
                text="🗑️ Vider l'historique",
                command=self.vider_historique,
                style="Danger.TButton"
            ).pack(side="right", padx=5)
        
        # Frame principal avec tableau et détails
        main_content = Frame(self, bg=theme.Colors.BG_SECONDARY)
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Colonne gauche - Tableau
        left_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Frame pour le tableau avec scrollbar
        tree_frame = Frame(left_frame, bg=theme.Colors.BG_SECONDARY)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("date", "nom", "code", "telephone", "marque", "plaque", "etat", "heure"),
            show="headings",
            height=15,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        # Configuration des colonnes
        self.tree.heading("date", text="Date")
        self.tree.heading("nom", text="Nom & Prénom")
        self.tree.heading("code", text="Code Barre")
        self.tree.heading("telephone", text="Téléphone")
        self.tree.heading("marque", text="Marque")
        self.tree.heading("plaque", text="Plaque")
        self.tree.heading("etat", text="Type")
        self.tree.heading("heure", text="Heure")
        
        self.tree.column("date", width=100)
        self.tree.column("nom", width=150)
        self.tree.column("code", width=80)
        self.tree.column("telephone", width=100)
        self.tree.column("marque", width=80)
        self.tree.column("plaque", width=100)
        self.tree.column("etat", width=80)
        self.tree.column("heure", width=80)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Colonne droite - Détails
        right_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY, width=300)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Image
        img_frame = Frame(right_frame, bg=theme.Colors.BG_SECONDARY, relief="solid", bd=2)
        img_frame.pack(pady=10)
        
        try:
            if paths.PROFIL_PATH.exists():
                img = Image.open(str(paths.PROFIL_PATH))
                img.thumbnail((200, 200))
                photo_tk = ImageTk.PhotoImage(img)
                self.lb_img = Label(img_frame, image=photo_tk, bg=theme.Colors.BG_SECONDARY)
                self.lb_img.image = photo_tk
            else:
                raise FileNotFoundError
        except:
            self.lb_img = Label(
                img_frame,
                text="Aucune image",
                bg=theme.Colors.BG_SECONDARY,
                width=25,
                height=10
            )
        self.lb_img.pack(padx=10, pady=10)
        
        # Zone de texte pour les détails
        details_label = Label(
            right_frame,
            text="Détails",
            font=("Arial", 14, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY
        )
        details_label.pack(pady=(10, 5))
        
        self.zone_text = Text(
            right_frame,
            font=('Arial', 12),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_PRIMARY,
            relief="solid",
            bd=2,
            wrap="word",
            height=10,
            width=30
        )
        self.zone_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.zone_text.insert("end", "Sélectionnez une ligne pour voir les détails")
        self.zone_text.config(state="disabled")
    
    def vider_historique(self):
        """Supprime tout l'historique après confirmation."""
        if not messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer tout l'historique ?\nCette action est irréversible."
        ):
            return
        db = Bdonnee()
        if db.vider_historique():
            messagebox.showinfo("Succès", "Historique vidé avec succès.")
            self.afficher_historique()

    def afficher_historique(self):
        """Affiche l'historique dans le tableau"""
        db = Bdonnee()
        historique = db.recuperer_historique()
        
        # Effacer le contenu existant
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ajouter les données
        for ligne in historique:
            prenom_nom = f"{ligne['prenom']} {ligne['nom']}"
            self.tree.insert("", "end", values=(
                ligne['date'],
                prenom_nom,
                str(ligne['code_barre']).zfill(6),
                ligne['telephone'],
                ligne['marque'],
                ligne['immatriculation'],
                ligne['etat'],
                ligne['heure']
            ))
    
    def on_select(self, event):
        """Gère la sélection d'une ligne"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])["values"]
        
        # Mettre à jour les détails
        self.zone_text.config(state="normal")
        self.zone_text.delete("1.0", "end")
        self.zone_text.insert("end", f"Date: {values[0]}\n")
        self.zone_text.insert("end", f"Nom: {values[1]}\n")
        self.zone_text.insert("end", f"Code Barre: {values[2]}\n")
        self.zone_text.insert("end", f"Téléphone: {values[3]}\n")
        self.zone_text.insert("end", f"Marque: {values[4]}\n")
        self.zone_text.insert("end", f"Plaque: {values[5]}\n")
        self.zone_text.insert("end", f"Type: {values[6]}\n")
        self.zone_text.insert("end", f"Heure: {values[7]}\n")
        self.zone_text.config(state="disabled")
        
        # Charger l'image
        try:
            code = str(values[2]).zfill(6)  # S'assurer que le code a 6 chiffres
            image_path = paths.get_image_path(f"{code}.png")
            if image_path.exists():
                img = Image.open(str(image_path))
                img.thumbnail((200, 200))
                photo_tk = ImageTk.PhotoImage(img)
                self.lb_img.config(image=photo_tk)
                self.lb_img.image = photo_tk
            else:
                # Image par défaut
                if paths.PROFIL_PATH.exists():
                    img = Image.open(str(paths.PROFIL_PATH))
                    img.thumbnail((200, 200))
                    photo_tk = ImageTk.PhotoImage(img)
                    self.lb_img.config(image=photo_tk)
                    self.lb_img.image = photo_tk
        except Exception as e:
            # Si erreur, essayer l'image par défaut
            try:
                if paths.PROFIL_PATH.exists():
                    img = Image.open(str(paths.PROFIL_PATH))
                    img.thumbnail((200, 200))
                    photo_tk = ImageTk.PhotoImage(img)
                    self.lb_img.config(image=photo_tk)
                    self.lb_img.image = photo_tk
            except:
                pass
