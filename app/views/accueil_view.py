"""
Vue d'accueil modernisée - Gestion des entrées/sorties
"""
from tkinter import Frame, Label, Button, StringVar
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
from app.database import Bdonnee
from app.config import settings, theme, paths
from app.utils.fonctions import today, convertir_caracteres_en_chiffres
from app.utils.sound import play_scan_sound
from app.config.permissions import has_permission


class AccueilView(Frame):
    """Vue d'accueil pour la gestion des entrées/sorties"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=theme.Colors.BG_SECONDARY)
        self.main_window = main_window
        self.scanning = False
        self.scan_mode = None
        self._processing_scan = False
        self.setup_ui()
    
    def setup_ui(self):
        """Accueil sans défilement : actions, photo et informations côte à côte."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._compact = None
        self._photo_source = None
        self._photo_size = None
        self._fitting_details = False
        self.feedback = Label(self, text="Choisissez Entrée ou Sortie pour démarrer.",
                              font=(theme.FONT_FAMILY, 11, "bold"), anchor="w", justify="left",
                              bg=theme.Colors.BG_PRIMARY, fg=theme.Colors.TEXT_PRIMARY, padx=12, pady=10)
        self.feedback.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        body = Frame(self, bg=theme.Colors.BG_SECONDARY)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        actions = Frame(body, bg=theme.Colors.BG_PRIMARY, width=210)
        actions.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        actions.grid_propagate(False)
        actions.columnconfigure(0, weight=1)
        actions.rowconfigure(5, weight=1)
        Label(actions, text="Passages", font=(theme.FONT_FAMILY, 11, "bold"),
              bg=theme.Colors.BG_PRIMARY, fg=theme.Colors.TEXT_PRIMARY).grid(
                  row=0, column=0, sticky="w", padx=14, pady=(14, 4))
        self.encours = Label(actions, text="Scan arrêté", font=(theme.FONT_FAMILY, 11, "bold"),
                             bg=theme.Colors.BG_PRIMARY, fg=theme.Colors.TEXT_SECONDARY,
                             anchor="w", justify="left", wraplength=180)
        self.encours.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))

        def action_button(title, command, background):
            return Button(actions, text=title, command=command,
                          font=(theme.FONT_FAMILY, 11, "bold"), bg=background, fg="white",
                          activebackground=background, activeforeground="white",
                          disabledforeground=theme.Colors.TEXT_SECONDARY, relief="flat", bd=0,
                          highlightthickness=1, highlightbackground=background,
                          highlightcolor=theme.Colors.ACCENT, cursor="hand2", pady=12)

        self.entree_btn = action_button("Entrée", self.start_scanning, theme.Colors.SUCCESS)
        self.sortie_btn = action_button("Sortie", self.action_sortie, theme.Colors.WARNING)
        self.stop_btn = action_button("Arrêter le scan", self.stop_scanning, theme.Colors.BG_MUTED)
        self.stop_btn.config(state="disabled")
        for row, button in enumerate((self.entree_btn, self.sortie_btn, self.stop_btn), 2):
            button.grid(row=row, column=0, sticky="ew", padx=12, pady=(0, 10))
        card = Frame(body, bg=theme.Colors.BG_SECONDARY,
                     highlightbackground=theme.Colors.BORDER, highlightthickness=1)
        card.grid(row=0, column=1, sticky="nsew")
        card.columnconfigure(1, weight=1)
        card.rowconfigure(1, weight=1)
        self.photo_frame = Frame(card, width=180, bg=theme.Colors.BG_PRIMARY)
        self.photo_frame.grid(row=1, column=0, sticky="nsew", padx=(12, 10), pady=(0, 12))
        self.photo_frame.pack_propagate(False)
        self.lb_img = Label(self.photo_frame, text="Aucune photo", bg=theme.Colors.BG_PRIMARY,
                            fg=theme.Colors.TEXT_SECONDARY)
        self.lb_img.pack(fill="both", expand=True, padx=8, pady=8)
        self.photo_frame.bind("<Configure>", self._render_photo)
        self.details_frame = Frame(card, bg=theme.Colors.BG_SECONDARY, width=300)
        self.details_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 14), pady=(0, 12))
        self.details_frame.grid_propagate(False)
        self.details_frame.columnconfigure(1, weight=1)
        # L'espace restant va sous la fiche, sans étirer chaque ligne.
        self.details_frame.rowconfigure(9, weight=1)
        self.detail_values = {}
        self.detail_labels = []
        self.detail_name_labels = []
        for row, (key, title) in enumerate((
            ("nom", "Nom"), ("prenom", "Prénom"), ("matricule", "Matricule"),
            ("telephone", "Téléphone"), ("statut", "Statut"), ("marque", "Marque"),
            ("immatriculation", "Plaque"), ("code_barre", "Code-barres"), ("couleur", "Couleur"),
        )):
            name_label = Label(self.details_frame, text=title, font=(theme.FONT_FAMILY, 10),
                               bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY, anchor="w")
            name_label.grid(row=row, column=0, sticky="w", padx=(0, 12), pady=2)
            self.detail_name_labels.append(name_label)
            variable = StringVar(self, value="—")
            value = Label(self.details_frame, textvariable=variable,
                          font=(theme.FONT_FAMILY, 11, "bold"), anchor="w", justify="left",
                          bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_PRIMARY, wraplength=230)
            value.grid(row=row, column=1, sticky="ew", pady=2)
            self.detail_values[key] = variable
            self.detail_labels.append(value)
        self.details_frame.bind("<Configure>", self._resize_details)
        self.set_photo("")
        self.bind("<Configure>", self._resize_layout)
        self.hidden_entry = ttk.Entry(self)
        self.hidden_entry.bind("<Return>", self.on_barcode_entry)
        self.hidden_entry.place(x=-100, y=-100, width=1, height=1)
        self.hidden_entry1 = ttk.Entry(self)
        self.hidden_entry1.bind("<Return>", self.on_barcode_exit)
        self.hidden_entry1.place(x=-100, y=-100, width=1, height=1)
        self.update_permissions()

    def update_permissions(self):
        if self.scanning and not has_permission("scan_entries" if self.scan_mode else "scan_exits"):
            self.stop_scanning()
        for button, permission in ((self.entree_btn, "scan_entries"), (self.sortie_btn, "scan_exits")):
            allowed = has_permission(permission) and not self.scanning
            color = theme.Colors.SUCCESS if permission == "scan_entries" else theme.Colors.WARNING
            button.config(state="normal" if allowed else "disabled", cursor="hand2" if allowed else "arrow",
                          bg=color if allowed else theme.Colors.BG_MUTED,
                          disabledforeground=theme.Colors.TEXT_SECONDARY)

    def _resize_layout(self, event):
        self.feedback.config(wraplength=max(100, event.width - 28))
        compact = event.height < 550 or event.width < 850
        # Garder de la place pour les neuf champs sur les petits écrans.
        self.photo_frame.config(width=150 if event.width < 850 else min(310, int((event.width - 250) * 0.40)))
        if compact != self._compact:
            self._compact = compact
            high_scaling = float(self.tk.call("tk", "scaling")) >= 1.8
            self.feedback.config(font=(theme.FONT_FAMILY, 9 if compact and high_scaling else 10 if compact else 11, "bold"),
                                 pady=6 if compact else 10)
            compact_font = 11 if high_scaling else 12
            for label in self.detail_labels:
                label.config(font=(theme.FONT_FAMILY, compact_font if compact else 14, "bold"))
                label.grid_configure(pady=0 if compact else 3)
            for label in self.detail_name_labels:
                label.config(font=(theme.FONT_FAMILY, compact_font - 1 if compact else 12))
                label.grid_configure(pady=0 if compact else 3)

    def _resize_details(self, event):
        label_width = self.details_frame.grid_bbox(0, 0, 0, 8)[2]
        available = max(70, event.width - label_width - 8)
        for label in self.detail_labels:
            if int(label.cget("wraplength")) != available:
                label.config(wraplength=available)
        self._fit_details()

    def _fit_details(self):
        """Agrandir les caractères tout en gardant les neuf lignes visibles."""
        if self._fitting_details:
            return
        self._fitting_details = True
        try:
            padding = 0 if self._compact else 3
            for size in range(12 if self._compact else 14, 8, -1):
                for label in self.detail_labels:
                    label.config(font=(theme.FONT_FAMILY, size, "bold"))
                for label in self.detail_name_labels:
                    label.config(font=(theme.FONT_FAMILY, size - 1))
                self.update_idletasks()
                name_width = self.details_frame.grid_bbox(0, 0, 0, 8)[2]
                available = max(70, self.details_frame.winfo_width() - name_width - 8)
                for label in self.detail_labels:
                    label.config(wraplength=available)
                self.update_idletasks()
                required = sum(max(name.winfo_reqheight(), value.winfo_reqheight()) + padding * 2
                               for name, value in zip(self.detail_name_labels, self.detail_labels))
                if required <= self.details_frame.winfo_height():
                    break
        finally:
            self._fitting_details = False

    def _display_owner(self, owner):
        for key, variable in self.detail_values.items():
            value = owner.get(key)
            if key == "code_barre" and value is not None:
                value = str(value).zfill(6)
            variable.set(str(value) if value not in (None, "") else "—")
        self._fit_details()

    def _render_photo(self, event=None):
        if self._photo_source is None:
            return
        width = max(1, min(290, self.photo_frame.winfo_width() - 16))
        height = max(1, min(340, self.photo_frame.winfo_height() - 16))
        if self._photo_size == (width, height):
            return
        self._photo_size = (width, height)
        image = self._photo_source.copy()
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        rendered = ImageTk.PhotoImage(image, master=self)
        self.lb_img.config(image=rendered, text="")
        self.lb_img.image = rendered

    def start_scanning(self):
        """Démarre le scan pour une entrée"""
        self._start_scanning(True)

    def _start_scanning(self, is_entry):
        permission = "scan_entries" if is_entry else "scan_exits"
        if not has_permission(permission):
            self._show_feedback("Accès refusé : connectez-vous avec un compte autorisé.", success=False)
            return
        self.scanning = True
        self.scan_mode = is_entry
        self.encours.config(text="Entrée en cours…" if is_entry else "Sortie en cours…",
                            fg=theme.Colors.SUCCESS if is_entry else theme.Colors.WARNING)
        self.entree_btn.config(state="disabled")
        self.sortie_btn.config(state="disabled")
        self.stop_btn.config(state="normal", bg=theme.Colors.ERROR, fg=theme.Colors.TEXT_LIGHT)
        self.hidden_entry.delete(0, "end")
        self.hidden_entry1.delete(0, "end")
        self._show_feedback("Mode entrée — scannez un code-barres." if is_entry else
                            "Mode sortie — scannez un code-barres.")
        (self.hidden_entry if is_entry else self.hidden_entry1).focus_set()
    
    def stop_scanning(self):
        """Arrête le scan"""
        self.encours.config(text="Scan arrêté", fg=theme.Colors.TEXT_SECONDARY)
        self.scanning = False
        self.scan_mode = None
        self.update_permissions()
        self.stop_btn.config(state="disabled", bg=theme.Colors.BG_MUTED)
        self.hidden_entry1.delete(0, "end")
        self.hidden_entry.delete(0, "end")
        self._show_feedback("Scan arrêté. Choisissez Entrée ou Sortie pour reprendre.")
    
    def action_sortie(self):
        """Démarre le scan pour une sortie"""
        self._start_scanning(False)
    
    def on_barcode_entry(self, event):
        """Gère la saisie d'un code-barre pour entrée"""
        if self.scanning and self.scan_mode is True and not self._processing_scan:
            barcode = self.hidden_entry.get()
            self.hidden_entry.delete(0, "end")
            if barcode:
                self.scan_display(barcode, True)
    
    def on_barcode_exit(self, event):
        """Gère la saisie d'un code-barre pour sortie"""
        if self.scanning and self.scan_mode is False and not self._processing_scan:
            barcode = self.hidden_entry1.get()
            self.hidden_entry1.delete(0, "end")
            if barcode:
                self.scan_display(barcode, False)
    
    def scan_display(self, scanned_code, is_entry):
        """Affiche les informations du code-barre scanné"""
        if self._processing_scan:
            return
        self._processing_scan = True
        try:
            permission = "scan_entries" if is_entry else "scan_exits"
            if not has_permission(permission):
                self._show_feedback("Passage refusé : votre session n’est pas autorisée.", success=False)
                return
            converted_code = convertir_caracteres_en_chiffres(scanned_code.strip())
            if not converted_code.isdigit():
                self._display_owner({})
                self.set_photo("")
                self._show_feedback("Passage refusé : code-barres invalide.", success=False)
                return
            db = Bdonnee()
            resultat = db.rechercher_par_code_barre(converted_code, notify=False)
            if not resultat:
                self._display_owner({})
                self.set_photo("")
                self._show_feedback(db.last_error or f"Code {converted_code} inconnu : passage non enregistré.", success=False)
                return
            self._display_owner(resultat)
            self.set_photo(f"{converted_code}.png")
            etat = "Entrée" if is_entry else "Sortie"
            if db.ajouter_historique(today(1), resultat['id'], etat, today(0)):
                name = f"{resultat.get('prenom', '')} {resultat.get('nom', '')}".strip()
                self._show_feedback(f"{etat} enregistrée — {name}", success=True)
            else:
                self._show_feedback("Passage refusé : " + (db.last_error or f"{etat} non enregistrée."), success=False)
        except Exception as error:
            self._show_feedback(f"Passage non enregistré : {error}", success=False)
        finally:
            self._processing_scan = False
            if self.scanning:
                (self.hidden_entry if self.scan_mode else self.hidden_entry1).focus_set()

    def _show_feedback(self, text, success=None):
        color = theme.Colors.BG_PRIMARY if success is None else theme.Colors.SUCCESS if success else theme.Colors.ERROR
        self.feedback.config(text=text.replace("\n", " "), bg=color,
                             fg=theme.Colors.TEXT_PRIMARY if success is None else "white")
        if success is not None:
            play_scan_sound(success, self)
    
    def set_photo(self, photo_nom):
        """Charge la photo puis la dimensionne à la place réellement disponible."""
        filename = str(photo_nom)
        if filename and not filename.lower().endswith(".png"):
            filename += ".png"
        requested = paths.get_image_path(filename) if filename else paths.PROFIL_PATH
        for candidate in (requested, paths.PROFIL_PATH):
            try:
                with Image.open(candidate) as source:
                    self._photo_source = ImageOps.exif_transpose(source).convert("RGB")
                self._photo_size = None
                self._render_photo()
                return
            except (OSError, ValueError):
                continue
        self._photo_source = None
        self.lb_img.config(image="", text="Aucune photo")
        self.lb_img.image = None
