"""Boutons compacts avec icônes et aide au survol ou au clavier."""
from tkinter import Label, Toplevel, ttk

from PIL import Image, ImageDraw, ImageTk

from app.config import theme


class IconButton(ttk.Button):
    def __init__(self, parent, *, icon, label, command, color=theme.Colors.PRIMARY):
        size = round(24 * float(parent.tk.call("tk", "scaling")) / (96 / 72))
        drawing = Image.new("RGBA", (96, 96))
        pen = ImageDraw.Draw(drawing)

        def line(points):
            pen.line([(x * 4, y * 4) for x, y in points], fill=color, width=8)

        if icon == "add":
            line([(12, 4), (12, 20)])
            line([(4, 12), (20, 12)])
        elif icon == "edit":
            line([(4, 16), (16, 4), (20, 8), (8, 20), (4, 20), (4, 16)])
            line([(13, 7), (17, 11)])
        elif icon == "delete":
            line([(6, 7), (7, 21), (17, 21), (18, 7)])
            line([(3, 6), (21, 6)])
            line([(9, 6), (9, 3), (15, 3), (15, 6)])
            line([(10, 10), (10, 17)])
            line([(14, 10), (14, 17)])
        elif icon == "export":
            line([(4, 14), (4, 21), (20, 21), (20, 14)])
            line([(12, 16), (12, 3)])
            line([(7, 8), (12, 3), (17, 8)])
        elif icon == "search":
            pen.ellipse((12, 12, 60, 60), outline=color, width=8)
            line([(15, 15), (21, 21)])
        else:
            raise ValueError(f"Icône inconnue : {icon}")
        rendered = drawing.resize((size, size), Image.Resampling.LANCZOS)
        self.icon_image = ImageTk.PhotoImage(rendered, master=parent)
        disabled = Image.new("RGBA", (size, size), "#9aa9b3")
        disabled.putalpha(rendered.getchannel("A"))
        self.disabled_icon_image = ImageTk.PhotoImage(disabled, master=parent)
        super().__init__(parent, image=(self.icon_image, "disabled", self.disabled_icon_image), text=label,
                         command=command, style="Secondary.TButton", padding=8, cursor="hand2")
        self._label = label
        self._tip = None
        self._tip_job = None
        self.bind("<Enter>", self._schedule_tip)
        self.bind("<FocusIn>", self._schedule_tip)
        for sequence in ("<Leave>", "<FocusOut>", "<ButtonPress>", "<Escape>"):
            self.bind(sequence, self._hide_tip, add="+")
        self.bind("<Destroy>", self._hide_tip, add="+")

    def _schedule_tip(self, event=None):
        self._hide_tip()
        self._tip_job = self.after(400, self._show_tip)

    def _show_tip(self):
        self._tip_job = None
        self._tip = Toplevel(self)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{self.winfo_rootx()}+{self.winfo_rooty() + self.winfo_height() + 6}")
        text = self._label + " — action non autorisée pour ce compte" if self.instate(["disabled"]) else self._label
        Label(self._tip, text=text, bg=theme.Colors.BG_DARK,
              fg=theme.Colors.TEXT_LIGHT, font=(theme.FONT_FAMILY, 10),
              padx=8, pady=5).pack()

    def _hide_tip(self, event=None):
        if self._tip_job is not None:
            self.after_cancel(self._tip_job)
            self._tip_job = None
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None
