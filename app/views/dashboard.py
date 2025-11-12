from tkinter import *
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from app.database.sqlite import Bdonnee  # Changer 'mysql' en 'sqlite' pour utiliser SQLite
from app.config import settings
from PIL import Image, ImageTk
from app.config import paths


class Dashboard:
    def __init__(self, root):
        """Initialisation du tableau de bord."""
        self.root = root
        self.root.title("Dashboard")
        self.root.protocol("WM_DELETE_WINDOW", self._quitter)
        self.bg_color = "#091821"
        self.root.config(bg=self.bg_color)
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-zoomed', True)  # Linux
        self.stats = Bdonnee().get_global_stats()

        # Ajouter le bouton de profil/déconnexion
        img_profil = Image.open(str(paths.get_icon_path("profil.png")))  
        img_profil = img_profil.resize((70, 70), Image.Resampling.LANCZOS)
        self.icon_profil = ImageTk.PhotoImage(img_profil)
        
        name = settings.current_user.name() if settings.is_connected else "Connexion"
        self.profil = Button(root, text=f"{name}", image=self.icon_profil, compound="top", 
                           font=("Arial", 10), bg=self.bg_color, fg='white', command=self._login_logout)
        self.profil.place(relx=1.0, y=0, anchor="ne")

        # Ajouter une frame pour les boutons de navigation
        self.button_frame = Frame(root, height=80, bg=self.bg_color)
        self.button_frame.pack(side="bottom", fill="x", padx=30)

        # Ajouter une sous-frame pour centrer les boutons
        self.button_container = Frame(self.button_frame, bg=self.bg_color)
        self.button_container.pack(expand=True)

        # Ajouter les boutons de navigation
        self.add_navigation_buttons()
        
        self.setup_ui()

    def _login_logout(self):
        """Gère la déconnexion de l'utilisateur."""
        if settings.is_connected:
            if messagebox.askyesno("Confirmation", "Voulez-vous vraiment vous déconnecter ?"):
                settings.logout()
                self.root.destroy()
        else:
            messagebox.showinfo("Info", "Vous n'êtes pas connecté.")

    def _quitter(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment quitter l'application ?"):
            settings.test = -1
            self.root.destroy()
    
    def setup_ui(self):
        """Configure l'interface utilisateur du tableau de bord."""
        # Titre principal
        Label(self.root, borderwidth=3, relief="sunken", text="Tableau de Bord", font=("Sans Serif", 35),
              bg=self.bg_color, fg="white").pack(ipadx=15, pady=5)

        # Création du Canvas
        canvas = Canvas(self.root, width=1400, height=880, bg=self.bg_color, highlightthickness=0)  
        canvas.pack(pady=15)

        # Conteneur pour tout le contenu
        main_frame = ttk.Frame(canvas)
        canvas.create_window(0, 0, anchor="nw", window=main_frame)

        # Partie centrale : Conteneur des statistiques et diagramme circulaire
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(fill="both", expand=True, pady=20, padx=40)

        # Grille pour les statistiques (à gauche)
        stats_frame = ttk.Frame(center_frame)
        stats_frame.pack(side="left", padx=40, fill="y", expand=True)
        self.create_stats(stats_frame)

        # Diagramme circulaire (à droite)
        pie_frame = ttk.Frame(center_frame)
        pie_frame.pack(side="right", padx=40, fill="y", expand=True)
        self.create_pie_chart(pie_frame)

        # Partie supérieure : Diagramme en barres
        graph_frame = self.generer_graphique_entrees(main_frame)
        graph_frame.pack(pady=20, padx=40)

    def create_pie_chart(self, parent):
        """Crée un diagramme circulaire et l'intègre directement dans l'interface Tkinter."""

        # Récupérer les données depuis la base
        data = Bdonnee().get_global_stats()

        # Extraire les labels et valeurs
        labels = list(data.keys())
        valeurs = list(data.values())

        # Vérifier si toutes les valeurs sont nulles
        if sum(valeurs) == 0:
            messagebox.showinfo("Info", "Il n'y a pas suffisamment de données pour générer un graphique.")
            settings.test = 0
            return 

        # Fonction d'affichage des valeurs
        def afficher_valeur(pct, valeurs):
            total = float(sum(valeurs))  # Convertir en float
            if total == 0:
                return "0"
            return f"{int(round(pct * total / 100.0))}"


        # Création de la figure pour le camembert 
        fig, ax = plt.subplots(figsize=(6, 3)) 

        wedges, texts, autotexts = ax.pie(
            valeurs, 
            labels=labels, 
            autopct=lambda pct: afficher_valeur(pct, valeurs),
            colors=['#4A90E2', '#F5A623', '#7ED321', '#D0021B', '#8B572A'],  
            startangle=90, 
            textprops={'fontsize': 14}  
        )

        # Ajuster la taille de police des valeurs affichées
        for autotext in autotexts:
            autotext.set_fontsize(14)  

        ax.set_title("Répartition des données", fontsize=18)  

        # Intégrer le graphique dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    def create_stats(self, parent):
        """Affiche les statistiques globales sous forme de grands cadres en grille."""
        
        data = Bdonnee().get_tab_values()
        row, col = 0, 0
        for key, value in data.items():
            frame = ttk.Frame(parent, padding=10, relief="solid")
            frame.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")

            ttk.Label(
                frame,
                text=key.replace("_", " ").capitalize(),
                font=("Arial", 26, "bold"), 
                foreground="white",
                background="#13254F",
                anchor="center",
                padding=10,
            ).pack(fill="x")

            ttk.Label(
                frame,
                text=str(value),
                font=("Arial", 28, "bold"), 
                foreground="#1f77b4",
                background="#FFFFFF",
                anchor="center",
                padding=5,
            ).pack(fill="x")

            col += 1
            if col > 1:
                col = 0
                row += 1

    def generer_graphique_entrees(self, parent):
        """Génère un graphique des entrées et l'intègre à Tkinter avec une hauteur fixe."""
        
        val = Bdonnee().get_entries_last_30_days()
        val = dict(reversed(val.items()))  

        dates = list(val.keys())
        dates = [date_str[:5] for date_str in dates]  
        entrees = list(val.values())  

        fig, ax = plt.subplots(figsize=(10, 4))  
        ax.plot(dates, entrees, marker='o', linestyle='-', color='b', label="Entrées")
        ax.set_xlabel("Dates", fontsize=12)
        ax.set_ylabel("Nombre d'Entrées", fontsize=12)
        ax.set_ylim(0)
        ax.set_title("Évolution des Entrées des 30 Derniers Jours", fontsize=14)
        ax.tick_params(axis='x', rotation=45)  
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()

        for i in range(len(dates)):
            ax.text(dates[i], entrees[i], str(entrees[i]), ha='left', va='top', bbox=dict(facecolor='white', alpha=0.7))

        frame = ttk.Frame(parent, height=420)  
        frame.pack_propagate(False)  
        frame.pack(pady=20, fill="x", padx=20)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

        return frame


    def add_navigation_buttons(self):
        """ Ajoute les boutons de navigation dans la frame en bas. """
        # Bouton "Dashboard"
        self.accueil = Button(
            self.button_container,
            text="Accueil",
            bg="#235F42",
            fg="white",
            font=("Times New Roman", 16, "bold"),
            bd=2,
            relief="raised",
            command=self.navigate_accueil
        )
        self.accueil.pack(side="left", padx=10, pady=10)

        # Bouton "Ajouter"
        self.historique = Button(
            self.button_container,
            text="Historique",
            bg="#235F42",
            fg="white",
            font=("Times New Roman", 16, "bold"),
            bd=2,
            relief="raised",
            command=self.navigate_history
        )
        self.historique.pack(side="left", padx=10, pady=10)

        # Bouton "Motards"
        self.affiche = Button(
            self.button_container,
            text="Motos",
            bg="#235F42",
            fg="white",
            font=("Times New Roman", 16, "bold"),
            bd=2,
            relief="raised",
            command=self.navigate_owners
        )
        self.affiche.pack(side="left", padx=10, pady=10)

        # Bouton "Users"
        self.user = Button(
            self.button_container,
            text="Utilisateurs",
            bg="#235F42",
            fg="white",
            font=("Times New Roman", 16, "bold"),
            bd=2,
            relief="raised",
            command=self.navigate_users
        )
        self.user.pack(side="left", padx=10, pady=10)
    
    def navigate_accueil(self):
        settings.test = 0
        self.root.destroy()

    def navigate_users(self):
        settings.test = 1
        # Fermer la fenêtre principale
        self.root.destroy()

    def navigate_history(self):
        settings.test = 3
        # Fermer la fenêtre principale
        self.root.destroy()

    def navigate_owners(self):
        settings.test = 2
        # Fermer la fenêtre principale
        self.root.destroy()
