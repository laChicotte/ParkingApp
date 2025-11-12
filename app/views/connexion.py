from tkinter import Toplevel, Label, Entry, Button, messagebox, SUNKEN
from app.database.sqlite import Bdonnee  # Changer 'mysql' en 'sqlite' pour utiliser SQLite
from app.config import settings
import bcrypt


class Connexion:
    def __init__(self, log):
        """Initialisation de la fenêtre de connexion."""
        self.bg = '#091821'
        self.test = False  # Pour stocker l'état de la connexion
        self.log = Toplevel(log)
        self.log.title("Connexion")
        self.log.geometry("600x400+400+100")
        self.log.resizable(False, False)
        self.log.config(bg=self.bg)
        self.log.grab_set()  # Empêche l'interaction avec la fenêtre principale
        self.log.focus_set()  # Donne le focus à la fenêtre de connexion

        self.create_widgets()  # Création des widgets

    def create_widgets(self):
        """Crée les widgets de l'interface de connexion."""
        # Titre
        mon_titre = Label(self.log, borderwidth=3, relief=SUNKEN,
                          text="Formulaire de connexion", font=("Sans Serif", 25),
                          bg="#13274F", fg="white")
        mon_titre.place(x=84, y=8, width=430)

        # Champ utilisateur
        user_tex = Label(self.log, text="Nom d'utilisateur :", font=('Arial', 15), bg="#13274F", fg='white')
        user_tex.place(x=30, y=120, width=180)
        self.user_entry = Entry(self.log, bd=4, font=('Arial', 13))
        self.user_entry.place(x=220, y=120, width=200, height=33)
        self.user_entry.focus_set()  # Donne le focus au champ utilisateur

        # Champ mot de passe
        password_tex = Label(self.log, text="Mot de passe :", font=('Arial', 15), bg="#13274F", fg='white')
        password_tex.place(x=30, y=170, width=150)
        self.password_entry = Entry(self.log, show='*', bd=4, font=('Arial', 13))
        self.password_entry.place(x=220, y=170, width=200, height=33)

        # Bouton de connexion
        login_button = Button(self.log, text='Connexion', font=('Arial', 17), fg='white', bg='#ff4500',
                              command=self.me_connecter)
        login_button.place(x=220, y=230, width=200)

        # Lier la touche Entrée au bouton de connexion
        self.log.bind('<Return>', lambda event: self.me_connecter())
        self.password_entry.bind('<Return>', lambda event: self.me_connecter())

    def me_connecter(self):
        """Gère la logique de connexion."""
        adress = self.user_entry.get().strip()  # Supprimer les espaces inutiles
        mdp = self.password_entry.get().strip()

        # Vérification des champs vides
        if not adress or not mdp:
            messagebox.showerror("Erreur", "Tous les champs doivent être renseignés.")
            self.clear_fields()
            return

        try:
            # Recherche de l'utilisateur dans la base de données
            user = Bdonnee().get_user(adress)
            if user:
                settings.current_user = settings.User(
                    user['id'], 
                    user['username'], 
                    user['email'], 
                    user['password'],
                    user['role']
                )

                # Vérification des données saisies
                if settings.current_user.verify_password(mdp):
                    messagebox.showinfo("Succès", "Connexion réussie. Bienvenue !")
                    self.test = True
                    settings.is_connected = True
                    self.log.destroy()  # Fermer la fenêtre après succès
                else:
                    messagebox.showwarning("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")
                    self.clear_fields()
            else:
                messagebox.showwarning("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")
                self.clear_fields()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
            self.clear_fields()

    def clear_fields(self):
        """Réinitialise tous les champs."""
        self.user_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.user_entry.focus_set()  # Remet le focus sur le champ utilisateur

