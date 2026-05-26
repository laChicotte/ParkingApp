"""
Composants de formulaire modernisés et réutilisables
"""
from tkinter import Frame, Label, Entry, Button, StringVar, OptionMenu, Canvas
from tkinter import ttk
from app.config import theme


class ModernFormField:
    """Champ de formulaire avec validation inline et placeholder"""

    _PLACEHOLDER_COLOR = "#aaaaaa"

    def __init__(self, parent, label_text, field_type="entry", options=None,
                 default_value="", required=False, placeholder=""):
        self.required = required
        self.field_type = field_type
        self._placeholder = placeholder
        self._showing_placeholder = False

        self.frame = Frame(parent, bg=theme.Colors.BG_SECONDARY)
        self.frame.pack(fill="x", pady=6)

        # Ligne label (texte + astérisque rouge si requis)
        label_row = Frame(self.frame, bg=theme.Colors.BG_SECONDARY)
        label_row.pack(fill="x", pady=(0, 3))

        Label(
            label_row,
            text=label_text,
            font=("Arial", 11, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_PRIMARY,
            anchor="w"
        ).pack(side="left")

        if required:
            Label(
                label_row,
                text=" *",
                font=("Arial", 11, "bold"),
                bg=theme.Colors.BG_SECONDARY,
                fg=theme.Colors.ERROR,
            ).pack(side="left")

        # Widget selon le type
        if field_type in ("entry", "password"):
            show = "*" if field_type == "password" else ""
            self.entry = Entry(
                self.frame,
                show=show,
                font=("Arial", 13),
                bg="#ffffff",
                fg=theme.Colors.TEXT_PRIMARY,
                relief="solid",
                bd=2,
                highlightthickness=1,
                highlightbackground=theme.Colors.BORDER,
                highlightcolor=theme.Colors.PRIMARY,
                insertbackground=theme.Colors.TEXT_PRIMARY
            )
            self.entry.pack(fill="x", ipady=10, padx=2)

            if default_value:
                self.entry.insert(0, str(default_value))
            elif placeholder and field_type == "entry":
                self._set_placeholder()

            if field_type == "entry":
                self.entry.bind("<FocusIn>", self._on_focus_in)
                self.entry.bind("<FocusOut>", self._on_focus_out)

            self.widget = self.entry

        elif field_type == "option":
            self.var = StringVar()
            if default_value:
                self.var.set(str(default_value))
            else:
                self.var.set(options[0] if options else "")

            self.option = OptionMenu(self.frame, self.var, *options)
            self.option.config(
                font=("Arial", 12),
                bg="#ffffff",
                fg=theme.Colors.TEXT_PRIMARY,
                relief="solid",
                bd=2,
                activebackground=theme.Colors.PRIMARY_LIGHT,
                activeforeground=theme.Colors.TEXT_LIGHT,
                highlightthickness=1,
                highlightbackground=theme.Colors.BORDER,
                highlightcolor=theme.Colors.PRIMARY
            )
            self.option.pack(fill="x", ipady=8, padx=2)
            self.widget = self.var

        # Label d'erreur inline (vide par défaut)
        self.error_label = Label(
            self.frame,
            text="",
            font=("Arial", 9),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.ERROR,
            anchor="w"
        )
        self.error_label.pack(fill="x", padx=4)

    # --- Placeholder ---

    def _set_placeholder(self):
        self._showing_placeholder = True
        self.entry.config(fg=self._PLACEHOLDER_COLOR)
        self.entry.insert(0, self._placeholder)

    def _on_focus_in(self, event):
        if self._showing_placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg=theme.Colors.TEXT_PRIMARY)
            self._showing_placeholder = False

    def _on_focus_out(self, event):
        if not self.entry.get() and self._placeholder:
            self._set_placeholder()

    # --- Validation ---

    def show_error(self, message):
        self.error_label.config(text=message)
        if hasattr(self, "entry"):
            self.entry.config(
                highlightbackground=theme.Colors.ERROR,
                highlightcolor=theme.Colors.ERROR
            )

    def clear_error(self):
        self.error_label.config(text="")
        if hasattr(self, "entry"):
            self.entry.config(
                highlightbackground=theme.Colors.BORDER,
                highlightcolor=theme.Colors.PRIMARY
            )

    # --- Accesseurs ---

    def get_value(self):
        if isinstance(self.widget, Entry):
            return "" if self._showing_placeholder else self.widget.get()
        elif isinstance(self.widget, StringVar):
            return self.widget.get()
        return ""

    def set_value(self, value):
        if isinstance(self.widget, Entry):
            if self._showing_placeholder:
                self.widget.config(fg=theme.Colors.TEXT_PRIMARY)
                self._showing_placeholder = False
            self.widget.delete(0, "end")
            self.widget.insert(0, str(value))
        elif isinstance(self.widget, StringVar):
            self.widget.set(str(value))


class ModernForm:
    """Formulaire modernisé avec validation inline des champs obligatoires"""

    def __init__(self, parent, title, fields_config,
                 submit_text="Enregistrer", submit_command=None):
        self.parent = parent
        self.fields = {}
        self.submit_command = submit_command

        # Conteneur principal avec scrollbar
        main_container = Frame(parent, bg=theme.Colors.BG_SECONDARY)
        main_container.pack(fill="both", expand=True)

        canvas = Canvas(main_container, bg=theme.Colors.BG_SECONDARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg=theme.Colors.BG_SECONDARY)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.form_frame = Frame(scrollable_frame, bg=theme.Colors.BG_SECONDARY, padx=30, pady=20)
        self.form_frame.pack(fill="both", expand=True)

        # Titre
        Label(
            self.form_frame,
            text=title,
            font=("Arial", 20, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY,
            pady=12
        ).pack()

        # Séparateur
        Frame(self.form_frame, bg=theme.Colors.PRIMARY, height=2).pack(fill="x", pady=(0, 15))

        # Champs
        fields_container = Frame(self.form_frame, bg=theme.Colors.BG_SECONDARY)
        fields_container.pack(fill="both", expand=True)

        first_entry = None
        for field_name, cfg in fields_config.items():
            field = ModernFormField(
                fields_container,
                label_text=cfg.get("label", field_name),
                field_type=cfg.get("type", "entry"),
                options=cfg.get("options"),
                default_value=cfg.get("default", ""),
                required=cfg.get("required", False),
                placeholder=cfg.get("placeholder", "")
            )
            self.fields[field_name] = field
            if first_entry is None and hasattr(field, "entry"):
                first_entry = field.entry

        # Boutons
        buttons_frame = Frame(self.form_frame, bg=theme.Colors.BG_SECONDARY)
        buttons_frame.pack(fill="x", pady=25)

        submit_btn = Button(
            buttons_frame,
            text=submit_text,
            command=self._on_submit,
            font=("Arial", 13, "bold"),
            bg=theme.Colors.SUCCESS,
            fg=theme.Colors.TEXT_LIGHT,
            activebackground="#66bb6a",
            activeforeground=theme.Colors.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=12,
            width=18
        )
        submit_btn.pack(side="left", padx=10)
        submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg="#66bb6a"))
        submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg=theme.Colors.SUCCESS))

        cancel_btn = Button(
            buttons_frame,
            text="Annuler",
            command=self._on_cancel,
            font=("Arial", 13, "bold"),
            bg=theme.Colors.BTN_DANGER,
            fg=theme.Colors.TEXT_LIGHT,
            activebackground="#ef5350",
            activeforeground=theme.Colors.TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=12,
            width=18
        )
        cancel_btn.pack(side="right", padx=10)
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg="#ef5350"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=theme.Colors.BTN_DANGER))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            if not canvas.winfo_exists():
                return
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            elif event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)
        canvas.bind("<Destroy>", _unbind_mousewheel)

        # Focus automatique sur le premier champ texte
        if first_entry:
            parent.after(100, first_entry.focus_set)

    def _validate(self):
        """Valide les champs requis et affiche les erreurs inline."""
        valid = True
        for field in self.fields.values():
            field.clear_error()
            if field.required and not field.get_value().strip():
                field.show_error("Ce champ est obligatoire")
                valid = False
        return valid

    def _on_submit(self):
        if not self._validate():
            return
        if self.submit_command:
            self.submit_command({name: f.get_value() for name, f in self.fields.items()})

    def _on_cancel(self):
        self.parent.destroy()

    def get_values(self):
        return {name: f.get_value() for name, f in self.fields.items()}

    def set_values(self, values):
        for name, value in values.items():
            if name in self.fields:
                self.fields[name].set_value(value)
