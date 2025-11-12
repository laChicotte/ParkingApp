"""
Composants de formulaire modernisés et réutilisables
"""
from tkinter import Frame, Label, Entry, Button, StringVar, OptionMenu
from tkinter import ttk
from app.config import theme


class ModernFormField:
    """Champ de formulaire modernisé"""
    
    def __init__(self, parent, label_text, field_type="entry", options=None, default_value=""):
        self.frame = Frame(parent, bg=theme.Colors.BG_SECONDARY)
        self.frame.pack(fill="x", pady=10)
        
        # Label
        self.label = Label(
            self.frame,
            text=label_text,
            font=("Arial", 11, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.TEXT_PRIMARY,
            anchor="w"
        )
        self.label.pack(fill="x", pady=(0, 5))
        
        # Champ selon le type
        if field_type == "entry":
            self.entry = ttk.Entry(
                self.frame,
                font=("Arial", 13),
                style="Modern.TEntry"
            )
            self.entry.pack(fill="x", ipady=8)
            if default_value:
                self.entry.insert(0, default_value)
            self.widget = self.entry
        elif field_type == "password":
            self.entry = ttk.Entry(
                self.frame,
                show="*",
                font=("Arial", 13),
                style="Modern.TEntry"
            )
            self.entry.pack(fill="x", ipady=8)
            if default_value:
                self.entry.insert(0, default_value)
            self.widget = self.entry
        elif field_type == "option":
            self.var = StringVar()
            if default_value:
                self.var.set(default_value)
            else:
                self.var.set(options[0] if options else "")
            self.option = OptionMenu(
                self.frame,
                self.var,
                *options
            )
            self.option.config(
                font=("Arial", 12),
                bg=theme.Colors.BG_SECONDARY,
                fg=theme.Colors.TEXT_PRIMARY,
                relief="solid",
                bd=2
            )
            self.option.pack(fill="x", ipady=8)
            self.widget = self.var
    
    def get_value(self):
        """Retourne la valeur du champ"""
        if isinstance(self.widget, ttk.Entry):
            return self.widget.get()
        elif isinstance(self.widget, StringVar):
            return self.widget.get()
        return ""
    
    def set_value(self, value):
        """Définit la valeur du champ"""
        if isinstance(self.widget, ttk.Entry):
            self.widget.delete(0, "end")
            self.widget.insert(0, str(value))
        elif isinstance(self.widget, StringVar):
            self.widget.set(str(value))


class ModernForm:
    """Formulaire modernisé avec validation"""
    
    def __init__(self, parent, title, fields_config, submit_text="Enregistrer", submit_command=None):
        self.parent = parent
        self.fields = {}
        self.submit_command = submit_command
        
        # Frame principal
        self.form_frame = Frame(parent, bg=theme.Colors.BG_SECONDARY, padx=30, pady=20)
        self.form_frame.pack(fill="both", expand=True)
        
        # Titre
        title_label = Label(
            self.form_frame,
            text=title,
            font=("Arial", 22, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY,
            pady=20
        )
        title_label.pack()
        
        # Champs
        fields_container = Frame(self.form_frame, bg=theme.Colors.BG_SECONDARY)
        fields_container.pack(fill="both", expand=True)
        
        for field_name, field_config in fields_config.items():
            field_type = field_config.get("type", "entry")
            label = field_config.get("label", field_name)
            options = field_config.get("options", None)
            default = field_config.get("default", "")
            
            field = ModernFormField(
                fields_container,
                label,
                field_type,
                options,
                default
            )
            self.fields[field_name] = field
        
        # Boutons
        buttons_frame = Frame(self.form_frame, bg=theme.Colors.BG_SECONDARY)
        buttons_frame.pack(fill="x", pady=20)
        
        ttk.Button(
            buttons_frame,
            text=submit_text,
            command=self._on_submit,
            style="Success.TButton",
            width=20
        ).pack(side="left", padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Annuler",
            command=self._on_cancel,
            style="Danger.TButton",
            width=20
        ).pack(side="right", padx=5)
    
    def _on_submit(self):
        """Gère la soumission du formulaire"""
        if self.submit_command:
            values = {name: field.get_value() for name, field in self.fields.items()}
            self.submit_command(values)
    
    def _on_cancel(self):
        """Annule le formulaire"""
        if isinstance(self.parent, Frame):
            self.parent.master.destroy()
        else:
            self.parent.destroy()
    
    def get_values(self):
        """Retourne toutes les valeurs du formulaire"""
        return {name: field.get_value() for name, field in self.fields.items()}
    
    def set_values(self, values):
        """Définit les valeurs du formulaire"""
        for name, value in values.items():
            if name in self.fields:
                self.fields[name].set_value(value)

