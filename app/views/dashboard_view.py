"""Tableau de bord du parking : mouvements et motos enregistrées."""
from datetime import datetime
from tkinter import Canvas, Frame, Label, StringVar, messagebox, TclError
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from app.components.dashboard_charts import movement_figure, category_figure
from app.config import theme
from app.config.permissions import has_permission, requires_permission
from app.database import Bdonnee


class DashboardView(Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=theme.Colors.BG_SECONDARY)
        self.main_window = main_window
        self.period = StringVar(value="15 jours")
        self.charts = []
        self._stacked = None
        self._scroll_job = None
        self._scroll_target = None
        self._wheel_bindings = []
        if not has_permission("view_dashboard"):
            return
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.scroll = Canvas(self, bg=theme.Colors.BG_SECONDARY, highlightthickness=0,
                             yscrollincrement=1)
        self.scroll.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.scroll.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.scroll.configure(yscrollcommand=scrollbar.set)
        page = Frame(self.scroll, bg=theme.Colors.BG_SECONDARY)
        window = self.scroll.create_window(0, 0, window=page, anchor="nw")
        page.bind("<Configure>", lambda event: self.scroll.configure(scrollregion=self.scroll.bbox("all")))
        self.scroll.bind("<Configure>", lambda event: self.scroll.itemconfigure(window, width=event.width))

        self.metric_labels = []
        metrics = Frame(page, bg=theme.Colors.BG_SECONDARY)
        metrics.pack(fill="x", padx=16, pady=(0, 20))
        for index, (title, subtitle, color) in enumerate((
            ("Entrées du jour", "Mouvements enregistrés", theme.Colors.PRIMARY),
            ("Sorties du jour", "Mouvements enregistrés", theme.Colors.WARNING),
            ("Motos enregistrées", "Communauté universitaire", theme.Colors.TEXT_PRIMARY),
        )):
            metrics.columnconfigure(index, weight=1, uniform="metrics")
            card = Frame(metrics, bg=theme.Colors.BG_PRIMARY, padx=14, pady=12)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 0 if index == 2 else 6))
            Label(card, text=title, font=(theme.FONT_FAMILY, 10, "bold"),
                  bg=theme.Colors.BG_PRIMARY, fg=theme.Colors.TEXT_SECONDARY).pack(anchor="w")
            value = Label(card, text="—", font=(theme.FONT_FAMILY, 28, "bold"),
                          bg=theme.Colors.BG_PRIMARY, fg=color)
            value.pack(anchor="w", pady=(4, 0))
            self.metric_labels.append(value)
            Label(card, text=subtitle, font=(theme.FONT_FAMILY, 9),
                  bg=theme.Colors.BG_PRIMARY, fg=theme.Colors.TEXT_SECONDARY).pack(anchor="w")

        controls = Frame(page, bg=theme.Colors.BG_SECONDARY)
        controls.pack(fill="x", padx=16, pady=(0, 12))
        Label(controls, text="Période des mouvements", font=(theme.FONT_FAMILY, 10),
              bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 10))
        selector = ttk.Combobox(controls, textvariable=self.period, state="readonly",
                                values=("7 jours", "15 jours", "30 jours"), width=10)
        selector.pack(side="left")
        selector.bind("<<ComboboxSelected>>", lambda event: self.refresh())
        ttk.Button(controls, text="Actualiser", style="Secondary.TButton",
                   command=self.refresh).pack(side="right")

        self.panels = Frame(page, bg=theme.Colors.BG_SECONDARY)
        self.panels.pack(fill="x", padx=16)
        self.movement_panel, self.movement_plot = self._panel("Activité du parking")
        self.category_panel, self.category_plot = self._panel("Répartition des motos")
        self.movement_caption = Label(self.movement_panel, font=(theme.FONT_FAMILY, 9),
                                      bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY)
        self.movement_caption.pack(before=self.movement_plot, anchor="w", padx=14, pady=(0, 4))
        self.category_caption = Label(self.category_panel, font=(theme.FONT_FAMILY, 9),
                                      bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY)
        self.category_caption.pack(before=self.category_plot, anchor="w", padx=14, pady=(0, 4))
        self.panels.bind("<Configure>", self._layout_charts)
        self._layout_charts()
        Label(page, text="Les compteurs du jour et la répartition couvrent des périodes différentes.",
              font=(theme.FONT_FAMILY, 9), bg=theme.Colors.BG_SECONDARY,
              fg=theme.Colors.TEXT_SECONDARY, wraplength=650, justify="left").pack(anchor="w", padx=16, pady=(12, 16))
        self.updated = Label(page, font=(theme.FONT_FAMILY, 9), bg=theme.Colors.BG_SECONDARY,
                             fg=theme.Colors.TEXT_SECONDARY)
        self.updated.pack(anchor="w", padx=16, pady=(0, 14))
        # Le tag de la fenêtre reçoit aussi les événements des enfants,
        # notamment ceux des canevas Matplotlib recréés à chaque actualisation.
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            binding = self.winfo_toplevel().bind(sequence, self._on_mousewheel, add="+")
            self._wheel_bindings.append((sequence, binding))

    def _on_mousewheel(self, event):
        widget_path = str(event.widget)
        if widget_path != str(self) and not widget_path.startswith(str(self) + "."):
            return
        if event.state & 0x0001:  # Laisser les gestes horizontaux à leur contrôle.
            return
        if isinstance(event.widget, ttk.Combobox):
            return
        number = getattr(event, "num", None)
        pixels = -48 if number == 4 else 48 if number == 5 else -event.delta * 48 / 120
        bounds = self.scroll.bbox("all")
        if not bounds or bounds[3] <= self.scroll.winfo_height():
            return
        current = self.scroll.canvasy(0)
        # Repartir de la position réelle après une manipulation de la barre.
        origin = current if self._scroll_job is None else self._scroll_target
        maximum = max(0, bounds[3] - self.scroll.winfo_height())
        self._scroll_target = max(0, min(maximum, origin + pixels))
        if self._scroll_job is None:
            self._animate_scroll()
        return "break"

    def _animate_scroll(self):
        bounds = self.scroll.bbox("all")
        maximum = max(0, bounds[3] - self.scroll.winfo_height()) if bounds else 0
        self._scroll_target = max(0, min(maximum, self._scroll_target))
        current = self.scroll.canvasy(0)
        distance = self._scroll_target - current
        if abs(distance) < 1:
            self._scroll_job = None
            return
        step = round(distance * 0.35)
        self.scroll.yview_scroll(step or (1 if distance > 0 else -1), "units")
        self._scroll_job = self.after(16, self._animate_scroll)

    def _panel(self, title):
        panel = Frame(self.panels, bg=theme.Colors.BG_SECONDARY,
                      highlightbackground=theme.Colors.BORDER, highlightthickness=1)
        Label(panel, text=title, font=(theme.FONT_FAMILY, 13, "bold"),
              bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(14, 4))
        plot = Frame(panel, bg=theme.Colors.BG_SECONDARY, height=280)
        plot.pack(fill="both", expand=True)
        return panel, plot

    def _layout_charts(self, event=None):
        width = event.width if event else self.panels.winfo_width()
        stacked = width < 850
        if stacked == self._stacked:
            return
        self._stacked = stacked
        self.movement_panel.grid_forget()
        self.category_panel.grid_forget()
        self.panels.columnconfigure(0, weight=3, uniform="charts")
        self.panels.columnconfigure(1, weight=0 if stacked else 2, uniform="" if stacked else "charts")
        self.panels.rowconfigure(0, minsize=350)
        self.panels.rowconfigure(1, minsize=350 if stacked else 0)
        self.movement_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 0 if stacked else 8))
        self.category_panel.grid(row=1 if stacked else 0, column=0 if stacked else 1,
                                 sticky="nsew", padx=(0 if stacked else 8, 0), pady=(12 if stacked else 0, 0))

    @requires_permission("view_dashboard")
    def refresh(self):
        try:
            database = Bdonnee()
            daily = database.get_tab_values()
            counts = database.count_owners_by_statut()
            movements = database.get_daily_movements(int(self.period.get().split()[0]))
        except Exception as error:
            messagebox.showerror("Tableau de bord", f"Impossible de charger les statistiques : {error}")
            return
        total = sum(int(count) for count in counts.values())
        for label, value in zip(self.metric_labels, (daily["Entrée"], daily["Sortie"], total)):
            label.config(text=f"{value:,}".replace(",", " "))
        entries = sum(row["entries"] for row in movements)
        exits = sum(row["exits"] for row in movements)
        start, end = movements[0]["date"], movements[-1]["date"]
        self.movement_caption.config(text=f"Du {start:%d/%m} au {end:%d/%m}   |   {entries} entrées, {exits} sorties")
        self.category_caption.config(text=f"{total} motos au total, toutes dates confondues")
        self._clear_charts()
        for parent, figure in ((self.movement_plot, movement_figure(movements)),
                               (self.category_plot, category_figure(counts))):
            canvas = FigureCanvasTkAgg(figure, master=parent)
            widget = canvas.get_tk_widget()
            widget.configure(width=1, height=1, highlightthickness=0)
            widget.pack(fill="both", expand=True)
            canvas.draw_idle()
            self.charts.append(canvas)
        self.updated.config(text=f"Actualisé le {datetime.now():%d/%m/%Y à %H:%M}")

    def _clear_charts(self):
        for canvas in self.charts:
            try:
                if canvas._idle_draw_id:
                    self.after_cancel(canvas._idle_draw_id)
            except TclError:
                pass
            canvas.get_tk_widget().destroy()
            canvas.figure.clear()
        self.charts.clear()

    def destroy(self):
        if self._scroll_job is not None:
            self.after_cancel(self._scroll_job)
        for sequence, binding in self._wheel_bindings:
            self.winfo_toplevel().unbind(sequence, binding)
        self._clear_charts()
        super().destroy()
