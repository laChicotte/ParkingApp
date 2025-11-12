"""
Composants de formulaire modernisés et réutilisables
"""
from tkinter import Frame, Label, Entry, Button, StringVar, OptionMenu, Canvas
from tkinter import ttk
from app.config import theme


class ModernFormField:
    """Champ de formulaire modernisé"""
    
    def __init__(self, parent, label_text, field_type="entry", options=None, default_value=""):
        self.frame = Frame(parent, bg=theme.Colors.BG_SECONDARY)
        self.frame.pack(fill="x", pady=8)
        
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
            self.entry = Entry(
                self.frame,
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
            self.widget = self.entry
        elif field_type == "password":
            self.entry = Entry(
                self.frame,
                show="*",
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
            self.widget = self.entry
        elif field_type == "option":
            self.var = StringVar()
            if default_value:
                self.var.set(str(default_value))
            else:
                self.var.set(options[0] if options else "")
            
            option_frame = Frame(self.frame, bg=theme.Colors.BG_SECONDARY)
            option_frame.pack(fill="x")
            
            self.option = OptionMenu(
                option_frame,
                self.var,
                *options
            )
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
            self.option.pack(fill="x", ipady=10, padx=2)
            self.widget = self.var
    
    def get_value(self):
        """Retourne la valeur du champ"""
        if isinstance(self.widget, Entry):
            return self.widget.get()
        elif isinstance(self.widget, StringVar):
            return self.widget.get()
        return ""
    
    def set_value(self, value):
        """Définit la valeur du champ"""
        if isinstance(self.widget, Entry):
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
        
        # Frame principal avec scrollbar
        main_container = Frame(parent, bg=theme.Colors.BG_SECONDARY)
        main_container.pack(fill="both", expand=True)
        
        # Canvas pour le scroll
        canvas = Canvas(main_container, bg=theme.Colors.BG_SECONDARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg=theme.Colors.BG_SECONDARY)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame principal du formulaire
        self.form_frame = Frame(scrollable_frame, bg=theme.Colors.BG_SECONDARY, padx=30, pady=20)
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
        buttons_frame.pack(fill="x", pady=30)
        
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
            width=20
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
            width=20
        )
        cancel_btn.pack(side="right", padx=10)
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg="#ef5350"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=theme.Colors.BTN_DANGER))
        
        # Pack canvas et scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel pour Linux et Windows
        def _on_mousewheel(event):
            try:
                # Windows
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                # Linux
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)
    
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

