"""
Vue Gestion des Motos modernisée
"""
from tkinter import Frame, Label, Entry, Button, Text, Toplevel, messagebox, StringVar, OptionMenu
from tkinter import ttk
from PIL import Image, ImageTk
from app.database.sqlite import Bdonnee
from app.config import theme, paths
from app.utils.fonctions import convertir_caracteres_en_chiffres, capture_with_preview
import webbrowser


class OwnersView(Frame):
    """Vue de gestion des motos avec tableau et formulaires modernisés"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=theme.Colors.BG_SECONDARY)
        self.main_window = main_window
        self.setup_ui()
        self.afficher_owners()
    
    def setup_ui(self):
        """Configure l'interface"""
        # Titre et barre d'outils
        header_frame = Frame(self, bg=theme.Colors.BG_SECONDARY)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        title = Label(
            header_frame,
            text="Gestion des Motos",
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
            command=self.add_owner,
            style="Success.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            actions_frame,
            text="✏️ Modifier",
            command=self.update_owner,
            style="Primary.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            actions_frame,
            text="🗑️ Supprimer",
            command=self.supprimer,
            style="Danger.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            actions_frame,
            text="📊 Exporter",
            command=self.exporter,
            style="Primary.TButton"
        ).pack(side="left", padx=5)
        
        # Frame principal
        main_content = Frame(self, bg=theme.Colors.BG_SECONDARY)
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Colonne gauche - Tableau et recherche
        left_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Recherche
        search_frame = Frame(left_frame, bg=theme.Colors.BG_SECONDARY)
        search_frame.pack(fill="x", pady=(0, 10))
        
        self.search_var = StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 12),
            style="Modern.TEntry"
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ttk.Button(
            search_frame,
            text="🔍 Rechercher",
            command=self.rechercher,
            style="Primary.TButton"
        ).pack(side="right")
        
        # Tableau
        tree_frame = Frame(left_frame, bg=theme.Colors.BG_SECONDARY)
        tree_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("nom", "prenom", "telephone", "code", "marque", "plaque", "couleur", "statut"),
            show="headings",
            height=15,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        # Configuration des colonnes
        columns_config = [
            ("nom", "Nom", 100),
            ("prenom", "Prénom", 120),
            ("telephone", "Téléphone", 100),
            ("code", "Code Barre", 100),
            ("marque", "Marque", 100),
            ("plaque", "Plaque", 100),
            ("couleur", "Couleur", 80),
            ("statut", "Statut", 100)
        ]
        
        for col, heading, width in columns_config:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Colonne droite - Détails et image
        right_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY, width=300)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Image
        img_frame = Frame(right_frame, bg=theme.Colors.BG_SECONDARY, relief="solid", bd=2)
        img_frame.pack(pady=10)
        
        try:
            img = Image.open(str(paths.PROFIL_PATH))
            img.thumbnail((200, 200))
            photo_tk = ImageTk.PhotoImage(img)
            self.lb_img = Label(img_frame, image=photo_tk, bg=theme.Colors.BG_SECONDARY)
            self.lb_img.image = photo_tk
        except:
            self.lb_img = Label(
                img_frame,
                text="Aucune image",
                bg=theme.Colors.BG_SECONDARY,
                width=25,
                height=10
            )
        self.lb_img.pack(padx=10, pady=10)
        
        # Bouton changer photo
        ttk.Button(
            right_frame,
            text="📷 Changer Photo",
            command=self.change_photo,
            style="Primary.TButton"
        ).pack(pady=5)
        
        # Zone de texte pour les détails
        self.zone_text = Text(
            right_frame,
            font=('Arial', 12),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_PRIMARY,
            relief="solid",
            bd=2,
            wrap="word",
            height=12,
            width=30
        )
        self.zone_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.zone_text.insert("end", "Sélectionnez une ligne pour voir les détails")
        self.zone_text.config(state="disabled")
    
    def afficher_owners(self):
        """Affiche les propriétaires dans le tableau"""
        db = Bdonnee()
        owners = db.recuperer(2)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, owner in enumerate(owners, 1):
            self.tree.insert("", "end", iid=owner['id'], values=(
                owner['nom'],
                owner['prenom'],
                owner['telephone'],
                str(owner['code_barre']).zfill(6),
                owner['marque'],
                owner['immatriculation'],
                owner['couleur'],
                owner['statut']
            ))
    
    def on_select(self, event):
        """Gère la sélection d'une ligne"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item_id = selected[0]
        values = self.tree.item(item_id)["values"]
        
        # Mettre à jour les détails
        self.zone_text.config(state="normal")
        self.zone_text.delete("1.0", "end")
        self.zone_text.insert("end", f"Nom: {values[0]}\n")
        self.zone_text.insert("end", f"Prénom: {values[1]}\n")
        self.zone_text.insert("end", f"Téléphone: {values[2]}\n")
        self.zone_text.insert("end", f"Code Barre: {values[3]}\n")
        self.zone_text.insert("end", f"Marque: {values[4]}\n")
        self.zone_text.insert("end", f"Plaque: {values[5]}\n")
        self.zone_text.insert("end", f"Couleur: {values[6]}\n")
        self.zone_text.insert("end", f"Statut: {values[7]}\n")
        self.zone_text.config(state="disabled")
        
        # Charger l'image
        try:
            code = values[3]
            path = str(paths.get_image_path(f"{code}.png"))
            img = Image.open(path)
            img.thumbnail((200, 200))
            photo_tk = ImageTk.PhotoImage(img)
            self.lb_img.config(image=photo_tk)
            self.lb_img.image = photo_tk
        except:
            pass
    
    def add_owner(self):
        """Affiche le formulaire d'ajout"""
        self._show_owner_form()
    
    def update_owner(self):
        """Affiche le formulaire de modification"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un propriétaire.")
            return
        item_id = int(selected[0])
        self._show_owner_form(item_id)
    
    def supprimer(self):
        """Supprime un propriétaire"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un propriétaire.")
            return
        
        item_id = int(selected[0])
        values = self.tree.item(selected[0])["values"]
        nom_complet = f"{values[0]} {values[1]}"
        
        if messagebox.askyesno("Confirmation", f"Voulez-vous supprimer {nom_complet} ?"):
            db = Bdonnee()
            if db.supprimer(2, item_id):
                messagebox.showinfo("Succès", "Propriétaire supprimé avec succès.")
                self.afficher_owners()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression.")
    
    def rechercher(self):
        """Recherche un propriétaire"""
        valeur = self.search_var.get().strip()
        if not valeur:
            self.afficher_owners()
            return
        
        db = Bdonnee()
        owners = db.rechercher_owner(valeur)
        
        if not owners:
            messagebox.showinfo("Info", "Aucun propriétaire trouvé.")
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for owner in owners:
            self.tree.insert("", "end", iid=owner['id'], values=(
                owner['nom'],
                owner['prenom'],
                owner['telephone'],
                str(owner['code_barre']).zfill(6),
                owner['marque'],
                owner['immatriculation'],
                owner['couleur'],
                owner['statut']
            ))
    
    def change_photo(self):
        """Change la photo d'un propriétaire"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un propriétaire.")
            return
        
        values = self.tree.item(selected[0])["values"]
        code = values[3]
        capture_with_preview(code)
        self.on_select(None)
    
    def exporter(self):
        """Exporte les données en HTML"""
        db = Bdonnee()
        liste_motards = db.recuperer(2)
        
        html_content = self._generate_html(liste_motards)
        
        with open("motards.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        webbrowser.open("motards.html")
        messagebox.showinfo("Succès", "Données exportées avec succès.")
    
    def _generate_html(self, motards):
        """Génère le contenu HTML"""
        # Code HTML simplifié (vous pouvez l'améliorer)
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Liste des Motos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #1a237e; color: white; }
    </style>
</head>
<body>
    <h1>Liste des Motos</h1>
    <table>
        <tr>
            <th>Nom</th><th>Prénom</th><th>Téléphone</th><th>Code Barre</th>
            <th>Marque</th><th>Plaque</th><th>Couleur</th><th>Statut</th>
        </tr>
"""
        for motard in motards:
            html += f"""
        <tr>
            <td>{motard['nom']}</td>
            <td>{motard['prenom']}</td>
            <td>{motard['telephone']}</td>
            <td>{motard['code_barre']}</td>
            <td>{motard['marque']}</td>
            <td>{motard['immatriculation']}</td>
            <td>{motard['couleur']}</td>
            <td>{motard['statut']}</td>
        </tr>
"""
        html += """
    </table>
</body>
</html>
"""
        return html
    
    def _show_owner_form(self, owner_id=None):
        """Affiche le formulaire d'ajout/modification"""
        dialog = Toplevel(self)
        dialog.title("Ajouter un Propriétaire" if not owner_id else "Modifier un Propriétaire")
        dialog.geometry("800x700")
        dialog.config(bg=theme.Colors.BG_SECONDARY)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"800x700+{x}+{y}")
        
        # Récupérer les données si modification
        owner_data = None
        if owner_id:
            db = Bdonnee()
            owners = db.recuperer(2)
            owner_data = next((o for o in owners if o['id'] == owner_id), None)
        
        # Configuration des champs
        fields_config = {
            "nom": {"label": "Nom *", "type": "entry"},
            "prenom": {"label": "Prénom *", "type": "entry"},
            "matricule": {"label": "Matricule", "type": "entry"},
            "telephone": {"label": "Téléphone *", "type": "entry"},
            "plaque": {"label": "Plaque *", "type": "entry"},
            "code_barre": {"label": "Code Barre *", "type": "entry"},
            "marque": {"label": "Marque", "type": "entry"},
            "couleur": {"label": "Couleur *", "type": "option", "options": ["Rouge", "Noire", "Bleue", "Blanche", "Cendre", "Autres"]},
            "statut": {"label": "Statut *", "type": "option", "options": ["Etudiant", "Enseignant", "Personnel", "Autre"]}
        }
        
        # Valeurs par défaut
        if owner_data:
            for field_name, field_config in fields_config.items():
                if field_name in owner_data:
                    field_config["default"] = str(owner_data[field_name])
        
        # Créer le formulaire
        from app.components.modern_form import ModernForm
        form = ModernForm(
            dialog,
            "Formulaire Propriétaire",
            fields_config,
            "Enregistrer",
            lambda values: self._save_owner(values, owner_id, dialog)
        )
    
    def _save_owner(self, values, owner_id, dialog):
        """Sauvegarde un propriétaire"""
        # Validation
        required_fields = ["nom", "prenom", "telephone", "plaque", "code_barre", "couleur", "statut"]
        for field in required_fields:
            if not values.get(field):
                messagebox.showerror("Erreur", f"Le champ {field} est obligatoire.")
                return
        
        db = Bdonnee()
        code_barre = convertir_caracteres_en_chiffres(values["code_barre"])
        
        if owner_id:
            # Modification
            nouvelles_valeurs = {
                "nom": values["nom"],
                "prenom": values["prenom"],
                "matricule": values.get("matricule", ""),
                "telephone": values["telephone"],
                "immatriculation": values["plaque"],
                "code_barre": code_barre,
                "marque": values.get("marque", "------"),
                "couleur": values["couleur"],
                "statut": values["statut"]
            }
            
            # Vérifier l'existence
            test, sms = db.verifier_existence(code_barre, values["plaque"])
            if test:
                messagebox.showerror("Attention", sms)
                return
            
            if db.modifier(2, owner_id, nouvelles_valeurs):
                messagebox.showinfo("Succès", "Propriétaire modifié avec succès.")
                dialog.destroy()
                self.afficher_owners()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la modification.")
        else:
            # Ajout
            test, sms = db.verifier_existence(code_barre, values["plaque"])
            if test:
                messagebox.showerror("Attention", sms)
                return
            
            if db.ajouter(2, [
                values["nom"],
                values["prenom"],
                values.get("matricule", ""),
                values.get("marque", "------"),
                values["plaque"],
                values["telephone"],
                code_barre,
                values["couleur"],
                values["statut"]
            ]):
                messagebox.showinfo("Succès", "Propriétaire ajouté avec succès.")
                dialog.destroy()
                self.afficher_owners()
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'ajout.")
