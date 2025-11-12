"""
Vue Dashboard modernisée avec graphiques
"""
from tkinter import Frame, Label
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from app.database.sqlite import Bdonnee
from app.config import theme
from app.utils.fonctions import today


class DashboardView(Frame):
    """Vue du tableau de bord avec statistiques et graphiques"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, bg=theme.Colors.BG_SECONDARY)
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        # Titre
        title = Label(
            self,
            text="Tableau de Bord",
            font=("Arial", 28, "bold"),
            bg=theme.Colors.BG_SECONDARY,
            fg=theme.Colors.PRIMARY,
            pady=20
        )
        title.pack()
        
        # Frame pour les statistiques
        stats_container = Frame(self, bg=theme.Colors.BG_SECONDARY)
        stats_container.pack(fill="x", padx=20, pady=10)
        
        self.create_stats_cards(stats_container)
        
        # Frame pour les graphiques
        charts_container = Frame(self, bg=theme.Colors.BG_SECONDARY)
        charts_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Graphique en barres (gauche)
        left_chart = Frame(charts_container, bg=theme.Colors.BG_SECONDARY)
        left_chart.pack(side="left", fill="both", expand=True, padx=10)
        self.create_bar_chart(left_chart)
        
        # Graphique circulaire (droite)
        right_chart = Frame(charts_container, bg=theme.Colors.BG_SECONDARY)
        right_chart.pack(side="right", fill="both", expand=True, padx=10)
        self.create_pie_chart(right_chart)
    
    def create_stats_cards(self, parent):
        """Crée les cartes de statistiques"""
        db = Bdonnee()
        stats = db.get_tab_values()
        
        # Frame pour les cartes
        cards_frame = Frame(parent, bg=theme.Colors.BG_SECONDARY)
        cards_frame.pack(fill="x", pady=10)
        
        for key, value in stats.items():
            card = Frame(
                cards_frame,
                bg=theme.Colors.BG_SECONDARY,
                relief="solid",
                bd=2,
                padx=20,
                pady=15
            )
            card.pack(side="left", fill="both", expand=True, padx=10)
            
            # Label de la clé
            key_label = Label(
                card,
                text=key,
                font=("Arial", 14, "bold"),
                bg=theme.Colors.BG_SECONDARY,
                fg=theme.Colors.TEXT_SECONDARY
            )
            key_label.pack()
            
            # Valeur
            value_label = Label(
                card,
                text=str(value),
                font=("Arial", 32, "bold"),
                bg=theme.Colors.BG_SECONDARY,
                fg=theme.Colors.PRIMARY
            )
            value_label.pack()
    
    def create_bar_chart(self, parent):
        """Crée un graphique en barres des entrées"""
        db = Bdonnee()
        data = db.get_entries_last_30_days()
        
        # Préparer les données
        dates = list(data.keys())[:15]  # Limiter à 15 jours pour la lisibilité
        values = list(data.values())[:15]
        
        # Créer la figure
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(dates, values, color=theme.Colors.PRIMARY, alpha=0.7)
        ax.set_xlabel("Dates", fontsize=10)
        ax.set_ylabel("Nombre d'entrées", fontsize=10)
        ax.set_title("Évolution des Entrées (15 derniers jours)", fontsize=12, fontweight="bold")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle="--", alpha=0.3)
        
        plt.tight_layout()
        
        # Intégrer dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_pie_chart(self, parent):
        """Crée un graphique circulaire"""
        db = Bdonnee()
        data = db.get_global_stats()
        
        # Filtrer les données non nulles
        labels = []
        values = []
        colors_list = [theme.Colors.PRIMARY, theme.Colors.SUCCESS, theme.Colors.WARNING, theme.Colors.INFO]
        
        for i, (key, value) in enumerate(data.items()):
            if value > 0:
                labels.append(key)
                values.append(value)
        
        if not values or sum(values) == 0:
            no_data_label = Label(
                parent,
                text="Aucune donnée disponible",
                font=("Arial", 14),
                bg=theme.Colors.BG_SECONDARY,
                fg=theme.Colors.TEXT_SECONDARY
            )
            no_data_label.pack(pady=50)
            return
        
        # Créer la figure
        fig, ax = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors_list[:len(values)],
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        ax.set_title("Répartition par Statut", fontsize=14, fontweight="bold")
        
        plt.tight_layout()
        
        # Intégrer dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
