"""
Vue Gestion des Motos modernisée
"""
from tkinter import Frame, Label, Entry, Button, Text, Toplevel, messagebox, StringVar, OptionMenu
from tkinter import ttk
from PIL import Image, ImageTk
from app.database import Bdonnee
from app.components.icon_button import IconButton
from app.components.modern_form import configure_dialog, report_form_error
from app.config import theme, paths, branding
from app.config.permissions import has_permission, requires_permission
from html import escape
from app.utils.fonctions import convertir_caracteres_en_chiffres, capture_with_preview
import webbrowser
import os
from concurrent.futures import ThreadPoolExecutor


class OwnersView(Frame):
    """Vue de gestion des motos avec tableau et formulaires modernisés"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=theme.Colors.BG_SECONDARY)
        self.main_window = main_window
        self._search_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="owner-search")
        self._search_job = None
        self._search_poll = None
        self._search_future = None
        self._search_generation = 0
        if not has_permission("view_owners"):
            return
        self.setup_ui()
        self.afficher_owners()
        self.search_var.trace_add("write", self._schedule_search)
    
    def setup_ui(self):
        """Configure l'interface"""
        # Frame principal
        main_content = Frame(self, bg=theme.Colors.BG_SECONDARY)
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        main_content.columnconfigure(0, weight=1)
        main_content.columnconfigure(1, minsize=260)
        main_content.rowconfigure(0, weight=1)
        
        # Colonne gauche - Tableau et recherche
        left_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Recherche
        search_frame = Frame(left_frame, bg=theme.Colors.BG_SECONDARY)
        search_frame.pack(fill="x", pady=(0, 10))
        Label(search_frame, text="Rechercher un usager ou une moto", bg=theme.Colors.BG_SECONDARY,
              fg=theme.Colors.TEXT_SECONDARY,
              font=(theme.FONT_FAMILY, 10, "bold")).pack(anchor="w", pady=(0, 6))
        search_help = Label(search_frame,
                            text="Recherche automatique : nom, prénom, matricule, téléphone, plaque ou code-barres",
                            font=(theme.FONT_FAMILY, 9), justify="left", anchor="w",
                            bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY)
        search_help.pack(fill="x", pady=(0, 6))
        search_frame.bind("<Configure>", lambda event: search_help.config(wraplength=max(100, event.width)))
        
        self.search_var = StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=(theme.FONT_FAMILY, 11),
            width=1,
            style="Modern.TEntry"
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        search_entry.bind("<Return>", lambda event: self.rechercher())
        search_entry.bind("<Escape>", lambda event: self.effacer_recherche())

        self.action_buttons = []
        for icon, label, command, color in (
            ("search", "Rechercher", self.rechercher, theme.Colors.PRIMARY),
            ("add", "Ajouter une moto", self.add_owner, theme.Colors.SUCCESS),
            ("edit", "Modifier", self.update_owner, theme.Colors.PRIMARY),
            ("delete", "Supprimer", self.supprimer, theme.Colors.ERROR),
            ("export", "Exporter", self.exporter, theme.Colors.PRIMARY),
        ):
            button = IconButton(search_frame, icon=icon, label=label, command=command, color=color)
            button.pack(side="left", padx=(4, 0))
            self.action_buttons.append(button)
        results_bar = Frame(left_frame, bg=theme.Colors.BG_SECONDARY)
        results_bar.pack(side="bottom", fill="x", pady=(8, 0))
        self.results_var = StringVar(self, value="")
        Label(results_bar, textvariable=self.results_var, font=(theme.FONT_FAMILY, 9),
              bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY).pack(side="left")
        ttk.Button(results_bar, text="Tout afficher", command=self.effacer_recherche,
                   style="Secondary.TButton", cursor="hand2").pack(side="right")
        
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
            columns=("nom", "prenom", "telephone", "code", "marque", "plaque", "couleur", "statut"),
            show="headings",
            height=15,
            yscrollcommand=scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        horizontal_scrollbar.config(command=self.tree.xview)
        
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
            self.tree.heading(col, text=heading, anchor="w")
            self.tree.column(col, width=width, minwidth=width, anchor="w")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Colonne droite - Détails et image
        right_frame = Frame(main_content, bg=theme.Colors.BG_SECONDARY, width=260)
        right_frame.grid(row=0, column=1, sticky="ns")
        right_frame.pack_propagate(False)
        
        # Image
        Label(right_frame, text="Fiche de la moto", font=(theme.FONT_FAMILY, 13, "bold"),
              bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))
        img_frame = Frame(right_frame, bg=theme.Colors.BG_SECONDARY,
                          highlightbackground=theme.Colors.BORDER, highlightthickness=1)
        img_frame.pack(pady=(0, 10))
        
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
        
        # Bouton changer photo
        self.change_photo_btn = ttk.Button(
            right_frame,
            text="Changer la photo",
            command=self.change_photo,
            style="Secondary.TButton"
        )
        self.change_photo_btn.pack(pady=5)
        
        # Zone de texte pour les détails
        self.zone_text = Text(
            right_frame,
            font=(theme.FONT_FAMILY, 11),
            bg=theme.Colors.BG_PRIMARY,
            fg=theme.Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=14,
            pady=14,
            wrap="word",
            height=12,
            width=30
        )
        self.zone_text.pack(fill="both", expand=True, pady=10)
        self.zone_text.insert("end", "Sélectionnez une moto dans le tableau pour consulter sa fiche.")
        self.zone_text.config(state="disabled")
        self.update_permissions()

    def update_permissions(self):
        controls = zip(self.action_buttons[1:] + [self.change_photo_btn],
                       ("edit_owners", "edit_owners", "manage_owners", "manage_owners", "edit_owners"))
        for button, permission in controls:
            allowed = has_permission(permission)
            button.state(["!disabled"] if allowed else ["disabled"])
            button.config(cursor="hand2" if allowed else "arrow", takefocus=allowed)
    
    @requires_permission("view_owners")
    def afficher_owners(self):
        """Affiche les usagers dans le tableau"""
        db = Bdonnee()
        owners = db.recuperer(2)
        self.results_var.set(f"{len(owners)} usager(s)")
        
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
    
    @requires_permission("view_owners")
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
            code = str(values[3]).zfill(6)  # S'assurer que le code a 6 chiffres
            image_path = paths.get_image_path(f"{code}.png")
            # Utiliser le chemin relatif depuis le projet
            path = str(image_path)
            if image_path.exists():
                img = Image.open(path)
                img.thumbnail((200, 200))
                photo_tk = ImageTk.PhotoImage(img)
                self.lb_img.config(image=photo_tk)
                self.lb_img.image = photo_tk
            else:
                # Si l'image n'existe pas, utiliser l'image par défaut
                default_path = paths.PROFIL_PATH
                if default_path.exists():
                    img = Image.open(str(default_path))
                    img.thumbnail((200, 200))
                    photo_tk = ImageTk.PhotoImage(img)
                    self.lb_img.config(image=photo_tk)
                    self.lb_img.image = photo_tk
        except Exception as e:
            # En cas d'erreur, essayer l'image par défaut
            try:
                default_path = paths.PROFIL_PATH
                if default_path.exists():
                    img = Image.open(str(default_path))
                    img.thumbnail((200, 200))
                    photo_tk = ImageTk.PhotoImage(img)
                    self.lb_img.config(image=photo_tk)
                    self.lb_img.image = photo_tk
            except:
                pass
    
    @requires_permission("edit_owners")
    def add_owner(self):
        """Affiche le formulaire d'ajout"""
        self._show_owner_form()
    
    @requires_permission("edit_owners")
    def update_owner(self):
        """Affiche le formulaire de modification"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un usager.")
            return
        item_id = int(selected[0])
        self._show_owner_form(item_id)
    
    @requires_permission("manage_owners")
    def supprimer(self):
        """Supprime un usager"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un usager.")
            return
        
        item_id = int(selected[0])
        values = self.tree.item(selected[0])["values"]
        nom_complet = f"{values[0]} {values[1]}"
        
        if messagebox.askyesno("Confirmation", f"Voulez-vous supprimer {nom_complet} ?"):
            db = Bdonnee()
            if db.supprimer(2, item_id):
                messagebox.showinfo("Succès", "Usager supprimé avec succès.")
                self.afficher_owners()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression.")
    
    @requires_permission("view_owners")
    def rechercher(self):
        """Recherche un usager"""
        self._cancel_search()
        self._search_generation += 1
        generation = self._search_generation
        valeur = self.search_var.get().strip()
        self.results_var.set("Recherche…")
        self._search_future = self._search_executor.submit(self._load_search, valeur)
        self._search_poll = self.after(30, self._poll_search, generation)

    @staticmethod
    def _load_search(value):
        if not has_permission("view_owners"):
            return [], "Accès refusé."
        try:
            db = Bdonnee()
            owners = db.rechercher_owner(value, notify=False)
            return owners, db.last_error
        except Exception as error:
            return [], str(error)

    def _schedule_search(self, *args):
        self._cancel_search()
        self._search_generation += 1
        self._search_job = self.after(350, self.rechercher)

    def _cancel_search(self):
        for name in ("_search_job", "_search_poll"):
            job = getattr(self, name)
            if job is not None:
                self.after_cancel(job)
                setattr(self, name, None)
        if self._search_future is not None:
            self._search_future.cancel()

    def _poll_search(self, generation):
        self._search_poll = None
        if generation != self._search_generation:
            return
        if not self._search_future.done():
            self._search_poll = self.after(30, self._poll_search, generation)
            return
        owners, error = self._search_future.result()
        self._render_search_results(owners, error)

    @requires_permission("view_owners")
    def _render_search_results(self, owners, error=""):
        self.results_var.set(f"{len(owners)} résultat(s)" if owners else "Aucun résultat")
        if error:
            self.results_var.set("Recherche indisponible. Réessayez.")
        
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

    def effacer_recherche(self):
        self.search_var.set("")
        self.rechercher()

    def destroy(self):
        self._cancel_search()
        self._search_executor.shutdown(wait=False, cancel_futures=True)
        super().destroy()
    
    @requires_permission("edit_owners")
    def change_photo(self):
        """Change la photo d'un usager"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un usager.")
            return
        
        values = self.tree.item(selected[0])["values"]
        code = values[3]
        capture_with_preview(code)
        self.on_select(None)
    
    @requires_permission("manage_owners")
    def exporter(self):
        """Exporte les données en HTML"""
        db = Bdonnee()
        liste_motards = db.recuperer(2)
        
        html_content = self._generate_html(liste_motards)
        
        export_path = paths.EXPORTS_DIR / "motards.html"
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        webbrowser.open(export_path.resolve().as_uri())
        messagebox.showinfo("Succès", "Données exportées avec succès.")
    
    def _generate_html(self, motards):
        """Génère le contenu HTML"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{branding.APP_NAME} — Usagers du parking</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 32px; color: #182f3d; }}
        header {{ display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }}
        header img {{ width: 90px; height: 90px; object-fit: contain; }}
        h1 {{ margin: 8px 0; color: #16566b; }}
        p {{ margin: 4px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #cedbe3; padding: 8px; text-align: left; }}
        th {{ background-color: #16566b; color: white; }}
    </style>
</head>
<body>
    <header>
        <img src="{branding.logo_data_uri()}" alt="Logo de l’UKAG">
        <div>
            <p>{branding.UNIVERSITY_NAME}</p>
            <h1>Usagers du parking</h1>
            <p>{branding.APP_NAME} — Liste des motos</p>
        </div>
    </header>
    <table>
        <tr>
            <th>Nom</th><th>Prénom</th><th>Téléphone</th><th>Code Barre</th>
            <th>Marque</th><th>Plaque</th><th>Couleur</th><th>Statut</th>
        </tr>
"""
        for motard in motards:
            html += f"""
        <tr>
            <td>{escape(str(motard['nom']))}</td>
            <td>{escape(str(motard['prenom']))}</td>
            <td>{escape(str(motard['telephone']))}</td>
            <td>{escape(str(motard['code_barre']))}</td>
            <td>{escape(str(motard['marque']))}</td>
            <td>{escape(str(motard['immatriculation']))}</td>
            <td>{escape(str(motard['couleur']))}</td>
            <td>{escape(str(motard['statut']))}</td>
        </tr>
"""
        html += """
    </table>
</body>
</html>
"""
        return html
    
    @requires_permission("edit_owners")
    def _show_owner_form(self, owner_id=None):
        """Affiche le formulaire d'ajout/modification"""
        dialog = Toplevel(self)
        dialog.title("Ajouter un Usager" if not owner_id else "Modifier un Usager")
        configure_dialog(dialog, self)
        
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
                data_key = "immatriculation" if field_name == "plaque" else field_name
                if data_key in owner_data:
                    field_config["default"] = owner_data[data_key]
        
        # Créer le formulaire
        from app.components.modern_form import ModernForm
        form = ModernForm(
            dialog,
            "Modifier un usager" if owner_id else "Ajouter un usager",
            fields_config,
            "Enregistrer",
            lambda values: self._save_owner(values, owner_id, dialog)
        )
    
    @requires_permission("edit_owners")
    def _save_owner(self, values, owner_id, dialog):
        """Sauvegarde un usager"""
        # Validation
        required_fields = ["nom", "prenom", "telephone", "plaque", "code_barre", "couleur", "statut"]
        for field in required_fields:
            if not str(values.get(field, "")).strip():
                report_form_error(dialog, "Vérifiez les champs signalés.", {field: "Ce champ est obligatoire."})
                return
        
        try:
            db = Bdonnee()
        except Exception as error:
            report_form_error(dialog, f"Enregistrement impossible : {error}")
            return
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
            test, sms = db.verifier_existence(code_barre, values["plaque"], exclude_id=owner_id)
            if test:
                self._report_owner_conflict(dialog, sms)
                return
            
            if db.modifier(2, owner_id, nouvelles_valeurs, notify=False):
                messagebox.showinfo("Succès", "Usager modifié avec succès.")
                dialog.destroy()
                self.afficher_owners()
            else:
                self._report_owner_conflict(dialog, db.last_error or "Modification impossible. Réessayez.")
        else:
            # Ajout
            test, sms = db.verifier_existence(code_barre, values["plaque"])
            if test:
                self._report_owner_conflict(dialog, sms)
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
            ], notify=False):
                messagebox.showinfo("Succès", "Usager ajouté avec succès.")
                dialog.destroy()
                self.afficher_owners()
            else:
                self._report_owner_conflict(dialog, db.last_error or "Enregistrement impossible. Réessayez.")

    @staticmethod
    def _report_owner_conflict(dialog, message):
        lower = message.lower()
        errors = {}
        if "code-barre" in lower or "code_barre" in lower:
            errors["code_barre"] = "Ce code-barres appartient déjà à un autre usager."
        if "immatriculation" in lower:
            errors["plaque"] = "Cette plaque appartient déjà à un autre usager."
        report_form_error(dialog, "Vérifiez les champs signalés." if errors else message, errors)
