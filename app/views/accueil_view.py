"""
Vue d'accueil modernisée - Gestion des entrées/sorties
"""
from tkinter import Frame, Label, Button, Text, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from app.database.sqlite import Bdonnee
from app.config import settings, theme, paths
from app.utils.fonctions import today, convertir_caracteres_en_chiffres


class AccueilView(Frame):
    """Vue d'accueil pour la gestion des entrées/sorties"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=theme.Colors.BG_SECONDARY)
        self.main_window = main_window
        self.scanning = False
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Titre
        title_frame = Frame(self, bg=theme.Colors.BG_SECONDARY)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = Label(
            title_frame,
            text="Gestion des Entrées/Sorties",
            font=("Arial", 24, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY
        )
        title_label.pack()
        
        # Date du jour
        date_label = Label(
            title_frame,
            text=f"Le {today(1)}",
            font=("Arial", 16),
            bg=theme.Colors.SUCCESS,
            fg=theme.Colors.TEXT_LIGHT,
            padx=20,
            pady=5
        )
        date_label.pack(pady=10)
        
        # Contenu principal
        content_frame = Frame(self, bg=theme.Colors.BG_SECONDARY)
        content_frame.pack(fill="both", expand=True)
        
        # Colonne gauche - Image et informations
        left_frame = Frame(content_frame, bg=theme.Colors.BG_SECONDARY)
        left_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        # Zone d'image
        img_frame = Frame(left_frame, bg=theme.Colors.BG_SECONDARY, relief="solid", bd=2)
        img_frame.pack(pady=20)
        
        try:
            photo = Image.open(str(paths.PROFIL_PATH))
            photo.thumbnail((400, 300))
            photo_tk = ImageTk.PhotoImage(photo)
            self.lb_img = Label(img_frame, image=photo_tk, bg=theme.Colors.BG_SECONDARY)
            self.lb_img.image = photo_tk
        except:
            self.lb_img = Label(
                img_frame,
                text="Aucune image",
                bg=theme.Colors.BG_SECONDARY,
                font=("Arial", 14),
                width=50,
                height=15
            )
        self.lb_img.pack(padx=10, pady=10)
        
        # Zone de texte pour les détails
        details_frame = Frame(left_frame, bg=theme.Colors.BG_SECONDARY)
        details_frame.pack(fill="x", pady=10)
        
        self.zone_text = Text(
            details_frame,
            font=('Arial', 16),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_PRIMARY,
            relief="solid",
            bd=2,
            wrap="word",
            height=8
        )
        self.zone_text.pack(fill="both", expand=True)
        self.zone_text.insert("end", "Nom : \nMatricule : \nMarque : \nPlaque : \nCode : \nTél : \nStatut : ")
        self.zone_text.config(state="disabled")
        
        # Colonne droite - Boutons d'action
        right_frame = Frame(content_frame, bg=theme.Colors.BG_SECONDARY)
        right_frame.pack(side="right", fill="y", padx=20)
        
        # État du scan
        self.encours = Label(
            right_frame,
            text="Scan arrêté",
            font=('Arial', 18, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_SECONDARY,
            pady=20
        )
        self.encours.pack()
        
        # Boutons d'action
        buttons_frame = Frame(right_frame, bg=theme.Colors.BG_SECONDARY)
        buttons_frame.pack(pady=20)
        
        # Charger les icônes
        self._load_icons()
        
        # Bouton Entrée
        self.entree_btn = Button(
            buttons_frame,
            image=self.icon_entree,
            command=self.start_scanning,
            relief="flat",
            bg=theme.Colors.BG_SECONDARY,
            cursor="hand2",
            bd=0
        )
        self.entree_btn.pack(pady=10)
        
        # Bouton Sortie
        self.sortie_btn = Button(
            buttons_frame,
            image=self.icon_sortie,
            command=self.action_sortie,
            relief="flat",
            bg=theme.Colors.BG_SECONDARY,
            cursor="hand2",
            bd=0
        )
        self.sortie_btn.pack(pady=10)
        
        # Bouton Stop
        self.stop_btn = Button(
            buttons_frame,
            image=self.icon_stop,
            command=self.stop_scanning,
            state="disabled",
            relief="flat",
            bg=theme.Colors.BG_SECONDARY,
            cursor="hand2",
            bd=0
        )
        self.stop_btn.pack(pady=10)
        
        # Champ caché pour capturer les entrées du scannage
        self.hidden_entry = ttk.Entry(self, font=("Arial", 12))
        self.hidden_entry.bind("<Return>", self.on_barcode_entry)
        self.hidden_entry.place(x=-100, y=-100)
        
        self.hidden_entry1 = ttk.Entry(self, font=("Arial", 12))
        self.hidden_entry1.bind("<Return>", self.on_barcode_exit)
        self.hidden_entry1.place(x=-200, y=-200)
    
    def _load_icons(self):
        """Charge les icônes des boutons"""
        img_entree = Image.open(str(paths.get_icon_path("enter.jpeg")))
        img_entree = img_entree.resize((180, 80), Image.Resampling.LANCZOS)
        self.icon_entree = ImageTk.PhotoImage(img_entree)
        
        img_sortie = Image.open(str(paths.get_icon_path("exit.jpeg")))
        img_sortie = img_sortie.resize((180, 80), Image.Resampling.LANCZOS)
        self.icon_sortie = ImageTk.PhotoImage(img_sortie)
        
        img_stop = Image.open(str(paths.get_icon_path("stop.png")))
        img_stop = img_stop.resize((80, 80), Image.Resampling.LANCZOS)
        self.icon_stop = ImageTk.PhotoImage(img_stop)
    
    def start_scanning(self):
        """Démarre le scan pour une entrée"""
        if not settings.is_connected or not settings.current_user.has_permission("scan_entries"):
            messagebox.showwarning("Alerte", "Vous n'avez pas les permissions nécessaires")
            return
        
        self.scanning = True
        self.encours.config(text="Entrée en cours...", fg=theme.Colors.SUCCESS)
        self.entree_btn.config(state="disabled")
        self.sortie_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        messagebox.showinfo("Info", "Le scannage a démarré. Scannez un code-barres.")
        self.hidden_entry.focus_set()
    
    def stop_scanning(self):
        """Arrête le scan"""
        self.encours.config(text="Scan arrêté", fg=theme.Colors.TEXT_SECONDARY)
        self.scanning = False
        self.entree_btn.config(state="normal")
        self.sortie_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.hidden_entry.delete(0, "end")
        messagebox.showinfo("Info", "Le scannage a été arrêté.")
    
    def action_sortie(self):
        """Démarre le scan pour une sortie"""
        if not settings.is_connected or not settings.current_user.has_permission("scan_exits"):
            messagebox.showwarning("Alerte", "Vous n'avez pas les permissions nécessaires")
            return
        
        self.encours.config(text="Sortie en cours...", fg=theme.Colors.WARNING)
        self.scanning = True
        self.entree_btn.config(state="disabled")
        self.sortie_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        messagebox.showinfo("Info", "Le scannage a démarré. Scannez un code-barres.")
        self.hidden_entry1.focus_set()
    
    def on_barcode_entry(self, event):
        """Gère la saisie d'un code-barre pour entrée"""
        if self.scanning:
            barcode = self.hidden_entry.get()
            if barcode:
                self.scan_display(barcode, True)
                self.hidden_entry.delete(0, "end")
    
    def on_barcode_exit(self, event):
        """Gère la saisie d'un code-barre pour sortie"""
        if self.scanning:
            barcode = self.hidden_entry1.get()
            if barcode:
                self.scan_display(barcode, False)
                self.hidden_entry1.delete(0, "end")
    
    def scan_display(self, scanned_code, is_entry):
        """Affiche les informations du code-barre scanné"""
        converted_code = convertir_caracteres_en_chiffres(scanned_code)
        db = Bdonnee()
        resultat = db.rechercher_par_code_barre(converted_code)
        
        if resultat:
            # Mettre à jour les informations
            self.zone_text.config(state="normal")
            self.zone_text.delete("1.0", "end")
            self.zone_text.insert("end", f"Nom : {resultat['nom']}\n")
            self.zone_text.insert("end", f"Prénom : {resultat['prenom']}\n")
            self.zone_text.insert("end", f"Matricule : {resultat['matricule']}\n")
            self.zone_text.insert("end", f"Marque : {resultat['marque']}\n")
            self.zone_text.insert("end", f"Plaque : {resultat['immatriculation']}\n")
            self.zone_text.insert("end", f"Tél : {resultat['telephone']}\n")
            self.zone_text.insert("end", f"Couleur : {resultat['couleur']}\n")
            self.zone_text.config(state="disabled")
            
            # Charger la photo
            self.set_photo(f"{converted_code}.png")
            
            # Ajouter à l'historique
            etat = "Entrée" if is_entry else "Sortie"
            if not db.ajouter_historique(today(1), resultat['id'], etat, today(0)):
                messagebox.showwarning("Échec", f"{etat} non enregistrée.")
            else:
                messagebox.showinfo("Succès", f"{etat} enregistrée avec succès.")
        else:
            messagebox.showwarning("Non trouvé", "Aucune donnée trouvée pour ce code-barre.")
    
    def set_photo(self, photo_nom):
        """Met à jour l'image affichée"""
        try:
            photo = Image.open(str(paths.get_image_path(photo_nom)))
            photo.thumbnail((400, 300))
            photo_tk = ImageTk.PhotoImage(photo)
            self.lb_img.config(image=photo_tk)
            self.lb_img.image = photo_tk
        except FileNotFoundError:
            try:
                photo = Image.open(str(paths.PROFIL_PATH))
                photo.thumbnail((400, 300))
                photo_tk = ImageTk.PhotoImage(photo)
                self.lb_img.config(image=photo_tk)
                self.lb_img.image = photo_tk
            except:
                pass

