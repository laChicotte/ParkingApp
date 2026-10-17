"""Formulaires adaptatifs avec actions fixes et champs partagés."""
from tkinter import Canvas, Frame, Label, StringVar, ttk
from types import SimpleNamespace
import re
from app.config import theme


def validate_email(value):
    return "Adresse email invalide." if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value.strip()) else ""


def report_form_error(dialog, message, errors=None):
    """Afficher un refus dans le formulaire en conservant toutes les valeurs."""
    form = getattr(dialog, "form", None)
    if form is not None:
        form.show_errors(errors, message)


def configure_dialog(dialog, parent, width=760, height=660):
    """Dimensionner et centrer un dialogue dans l'espace de l'écran."""
    dialog.transient(parent.winfo_toplevel())
    dialog.config(bg=theme.Colors.BG_SECONDARY)
    width = min(width, dialog.winfo_screenwidth() - 64)
    height = min(height, dialog.winfo_screenheight() - 100)
    dialog.minsize(min(460, width), min(400, height))
    x = max(0, (dialog.winfo_screenwidth() - width) // 2)
    y = max(0, (dialog.winfo_screenheight() - height) // 2 - 25)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    dialog.resizable(True, True)
    dialog.grab_set()


class ModernFormField:
    def __init__(self, parent, label_text, field_type="entry", options=None, default_value=""):
        self.frame = Frame(parent, bg=theme.Colors.BG_SECONDARY)
        self.label = Label(self.frame, text=label_text,
                           font=(theme.FONT_FAMILY, 10, "bold"), anchor="w",
                           bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_PRIMARY)
        self.label.pack(fill="x", pady=(0, 6))
        default = str(default_value) if default_value is not None else ""
        if field_type == "option" and not default:
            default = options[0] if options else ""
        self.var = StringVar(self.frame, value=default)
        if field_type == "option":
            self.option = ttk.Combobox(self.frame, textvariable=self.var, values=options or (),
                                       state="readonly", font=(theme.FONT_FAMILY, 11),
                                       style="Form.TCombobox", width=1)
            self.widget = self.option
        else:
            self.entry = ttk.Entry(self.frame, textvariable=self.var, width=1,
                                   font=(theme.FONT_FAMILY, 11), style="Form.TEntry",
                                   show="•" if field_type == "password" else "")
            self.widget = self.entry
        self.widget.pack(fill="x")
        self.error_var = StringVar(self.frame, value="")
        self.error_label = Label(self.frame, textvariable=self.error_var, anchor="w", justify="left",
                                 font=(theme.FONT_FAMILY, 9), bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.ERROR)
        self.frame.bind("<Configure>", lambda event: self.error_label.config(wraplength=max(80, event.width)))
        self.var.trace_add("write", lambda *args: self.set_error(""))

    def set_error(self, message):
        self.error_var.set(message)
        self.widget.state(["invalid"] if message else ["!invalid"])
        if message:
            self.error_label.pack(fill="x", pady=(4, 0))
        else:
            self.error_label.pack_forget()

    def get_value(self):
        return self.var.get()

    def set_value(self, value):
        self.var.set(str(value) if value is not None else "")


class ModernForm:
    def __init__(self, parent, title, fields_config, submit_text="Enregistrer", submit_command=None):
        self.parent = parent
        self.fields = {}
        self.fields_config = fields_config
        parent.form = self
        self.submit_command = submit_command
        self._columns = None
        self._wheel_remainder = 0.0
        self._bindings = []
        self.container = Frame(parent, bg=theme.Colors.BG_SECONDARY)
        self.container.pack(fill="both", expand=True)
        header = Frame(self.container, bg=theme.Colors.BG_SECONDARY)
        header.pack(fill="x", padx=24, pady=(20, 16))
        Label(header, text=title, font=(theme.FONT_FAMILY, 18, "bold"), anchor="w",
              bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.PRIMARY).pack(fill="x")
        if any("*" in config.get("label", "") for config in fields_config.values()):
            Label(header, text="* Champ obligatoire", font=(theme.FONT_FAMILY, 10),
                  bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY).pack(anchor="w", pady=(6, 0))
        footer = Frame(self.container, bg=theme.Colors.BG_PRIMARY)
        footer.pack(side="bottom", fill="x")
        Frame(footer, height=1, bg=theme.Colors.BORDER).pack(fill="x")
        actions = Frame(footer, bg=theme.Colors.BG_PRIMARY)
        self.error_var = StringVar(self.container, value="")
        self.error_label = Label(footer, textvariable=self.error_var, justify="left", anchor="w",
                                 bg=theme.Colors.BG_PRIMARY, fg=theme.Colors.ERROR, font=(theme.FONT_FAMILY, 10))
        footer.bind("<Configure>", lambda event: self.error_label.config(wraplength=max(100, event.width - 48)))
        actions.pack(fill="x", padx=24, pady=14)
        self.submit_btn = ttk.Button(actions, text=submit_text, command=self._on_submit,
                                      style="Primary.TButton", cursor="hand2")
        self.submit_btn.pack(side="right")
        self.cancel_btn = ttk.Button(actions, text="Annuler", command=self._on_cancel,
                                      style="Secondary.TButton", cursor="hand2")
        self.cancel_btn.pack(side="right", padx=(0, 10))
        body = Frame(self.container, bg=theme.Colors.BG_SECONDARY)
        body.pack(fill="both", expand=True)
        self.canvas = Canvas(body, bg=theme.Colors.BG_SECONDARY, highlightthickness=0,
                             yscrollincrement=1)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.form_frame = Frame(self.canvas, bg=theme.Colors.BG_SECONDARY, padx=24, pady=4)
        self._window = self.canvas.create_window(0, 0, window=self.form_frame, anchor="nw")
        for name, config in fields_config.items():
            field = ModernFormField(self.form_frame, config.get("label", name),
                                    config.get("type", "entry"), config.get("options"),
                                    config.get("default", ""))
            self.fields[name] = field
            field.widget.bind("<FocusIn>", self._reveal_field, add="+")
        self.canvas.bind("<Configure>", self._layout)
        self.form_frame.bind("<Configure>", self._update_scrollregion)
        self._top = parent.winfo_toplevel()
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self._bindings.append((sequence, self._top.bind(sequence, self._on_mousewheel, add="+")))
        self.container.bind("<Destroy>", self._cleanup, add="+")
        self._bindings.append(("<Escape>", self._top.bind("<Escape>", lambda event: self._on_cancel(), add="+")))
        if self.fields:
            self.container.after_idle(next(iter(self.fields.values())).widget.focus_set)

    def _layout(self, event):
        self.canvas.itemconfigure(self._window, width=event.width)
        columns = 2 if event.width >= 620 else 1
        if columns == self._columns:
            return
        self._columns = columns
        self.form_frame.columnconfigure(0, weight=1, uniform="fields")
        self.form_frame.columnconfigure(1, weight=1 if columns == 2 else 0,
                                        uniform="fields" if columns == 2 else "")
        for index, field in enumerate(self.fields.values()):
            column = index % columns
            field.frame.grid(row=index // columns, column=column, sticky="ew",
                             padx=(0, 12) if columns == 2 and column == 0 else (12, 0) if columns == 2 else 0,
                             pady=(0, 14))

    def _update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _reveal_field(self, event):
        self.canvas.update_idletasks()
        top = event.widget.master.winfo_y()
        bottom = top + event.widget.master.winfo_height()
        offset = self.canvas.canvasy(0)
        height = self.canvas.winfo_height()
        if top < offset:
            self.canvas.yview_scroll(round(top - offset), "units")
        elif bottom > offset + height:
            self.canvas.yview_scroll(round(bottom - offset - height + 12), "units")

    def _on_mousewheel(self, event):
        if not str(event.widget).startswith(str(self.container) + "."):
            return
        bounds = self.canvas.bbox("all")
        if not bounds or bounds[3] <= self.canvas.winfo_height():
            return
        num = getattr(event, "num", None)
        delta = -40 if num == 4 else 40 if num == 5 else -event.delta / 3
        self._wheel_remainder += delta
        pixels = int(self._wheel_remainder)
        self._wheel_remainder -= pixels
        self.canvas.yview_scroll(pixels, "units")
        return "break"

    def _cleanup(self, event):
        if event.widget == self.container:
            for sequence, binding in self._bindings:
                self._top.unbind(sequence, binding)

    def _on_submit(self):
        if self.validate() and self.submit_command:
            self.submit_command(self.get_values())

    def validate(self):
        errors = {}
        for name, field in self.fields.items():
            config = self.fields_config[name]
            value = field.get_value()
            if "*" in config.get("label", "") and not value.strip():
                errors[name] = "Ce champ est obligatoire."
            elif value.strip() and config.get("validator"):
                message = config["validator"](value)
                if message:
                    errors[name] = message
        self.show_errors(errors)
        return not errors

    def show_errors(self, errors=None, message=""):
        errors = errors or {}
        for name, field in self.fields.items():
            field.set_error(errors.get(name, ""))
        self.error_var.set(message or ("Vérifiez les champs signalés." if errors else ""))
        if self.error_var.get():
            self.error_label.pack(fill="x", padx=24, pady=(10, 0), after=self.error_label.master.winfo_children()[0])
        else:
            self.error_label.pack_forget()
        if errors:
            name = next((name for name in self.fields if name in errors), None)
            if name:
                widget = self.fields[name].widget
                widget.focus_set()
                self.container.after_idle(lambda: self._reveal_field(SimpleNamespace(widget=widget)))

    def _on_cancel(self):
        self.parent.winfo_toplevel().destroy()

    def get_values(self):
        return {name: field.get_value() for name, field in self.fields.items()}

    def set_values(self, values):
        for name, value in values.items():
            if name in self.fields:
                self.fields[name].set_value(value)
