"""Configuration locale des postes Windows utilisant XAMPP."""
import json
import re
from tkinter import Tk, Toplevel, StringVar, Label, Frame, Entry, Button, messagebox

import bcrypt
import pymysql

from app.config import paths, theme, branding


def prepare_database(config):
    """Vérifie la connexion et crée uniquement la base absente demandée."""
    if not re.fullmatch(r"[A-Za-z0-9_]{1,64}", config["db_name"]):
        raise ValueError("Le nom de la base accepte lettres, chiffres et underscores (64 caractères maximum).")
    with pymysql.connect(host=config["host"], port=config["port"], user=config["user"],
                         password=config["password"], charset="utf8mb4", connect_timeout=5,
                         read_timeout=10, write_timeout=10) as connection:
        try:
            connection.select_db(config["db_name"])
        except pymysql.OperationalError as error:
            if error.args[0] != 1049:
                raise
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE `{config['db_name']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            connection.select_db(config["db_name"])


def configure_database(parent=None, error=None):
    window = Toplevel(parent) if parent else Tk()
    window.title(f"Configuration MySQL — {branding.APP_NAME}")
    window.geometry("570x650")
    window.minsize(570, 650)
    window.configure(bg=theme.Colors.BG_SECONDARY)
    defaults = {"host": "127.0.0.1", "port": 3306, "user": "root", "password": "", "db_name": "parkingapp"}
    try:
        stored = json.loads(paths.CONFIG_FILE.read_text(encoding="utf-8-sig"))
        if isinstance(stored, dict):
            defaults.update({key: stored[key] for key in defaults if key in stored})
    except (OSError, ValueError):
        pass
    body = Frame(window, bg=theme.Colors.BG_SECONDARY, padx=24, pady=18)
    body.pack(fill="both", expand=True)
    Label(body, text=branding.APP_NAME, font=(theme.FONT_FAMILY, 22, "bold"),
          bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.PRIMARY).pack(anchor="w")
    Label(body, text="Démarrez MySQL dans XAMPP, puis renseignez la connexion.\n"
          "La base sera créée si elle n’existe pas. Les bases existantes sont conservées.",
          wraplength=510, justify="left", bg=theme.Colors.BG_SECONDARY,
          fg=theme.Colors.TEXT_SECONDARY).pack(anchor="w", pady=(8, 12))
    if error:
        Label(body, text=str(error), fg=theme.Colors.ERROR, bg=theme.Colors.BG_SECONDARY,
              wraplength=510, justify="left").pack(anchor="w", pady=(0, 10))
    fields = {}
    for key, title in (("host", "Serveur MySQL"), ("port", "Port"), ("db_name", "Base de données"),
                       ("user", "Utilisateur MySQL"), ("password", "Mot de passe MySQL (souvent vide sur XAMPP)")):
        Label(body, text=title, bg=theme.Colors.BG_SECONDARY,
              fg=theme.Colors.TEXT_PRIMARY).pack(anchor="w", pady=(6, 2))
        fields[key] = StringVar(window, value=str(defaults[key]))
        Entry(body, textvariable=fields[key], show="*" if key == "password" else "",
              font=(theme.FONT_FAMILY, 11), relief="solid", bd=1).pack(fill="x", ipady=5)
    saved = False

    def save():
        nonlocal saved
        try:
            config = {key: value.get().strip() if key != "password" else value.get()
                      for key, value in fields.items()}
            config["port"] = int(config["port"])
            if not config["host"] or not config["user"] or not 1 <= config["port"] <= 65535:
                raise ValueError("Renseignez un serveur, un utilisateur et un port valide.")
            prepare_database(config)
            paths.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            temporary = paths.CONFIG_FILE.with_suffix(".tmp")
            temporary.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(paths.CONFIG_FILE)
        except Exception as failure:
            messagebox.showerror("Configuration MySQL", str(failure), parent=window)
            return
        saved = True
        window.destroy()

    Button(body, text="Vérifier et enregistrer", command=save,
           bg=theme.Colors.PRIMARY, fg="white", relief="flat", pady=10).pack(fill="x", pady=(18, 6))
    Label(body, text="Ces paramètres sont propres à ce poste.\nLes comptes UKAG Parking sont distincts des comptes MySQL.",
          bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.TEXT_SECONDARY,
          justify="left").pack(anchor="w", pady=6)
    if parent:
        window.transient(parent)
        window.grab_set()
        parent.wait_window(window)
    else:
        window.mainloop()
    return saved


def create_first_admin(database):
    """Propose un compte au premier lancement d'une base sans utilisateurs."""
    if database.recuperer(1):
        return True
    window = Tk()
    window.title(f"Premier administrateur — {branding.APP_NAME}")
    window.geometry("520x430")
    window.configure(bg=theme.Colors.BG_SECONDARY)
    body = Frame(window, bg=theme.Colors.BG_SECONDARY, padx=24, pady=24)
    body.pack(fill="both", expand=True)
    Label(body, text="Créer le premier administrateur", font=(theme.FONT_FAMILY, 17, "bold"),
          bg=theme.Colors.BG_SECONDARY, fg=theme.Colors.PRIMARY).pack(anchor="w", pady=(0, 10))
    fields = []
    for title, default, hidden in (("Identifiant", "admin", False), ("Mot de passe (8 caractères minimum)", "", True),
                                    ("Confirmer le mot de passe", "", True)):
        Label(body, text=title, bg=theme.Colors.BG_SECONDARY).pack(anchor="w", pady=(10, 3))
        field = Entry(body, show="*" if hidden else "", font=(theme.FONT_FAMILY, 11))
        field.insert(0, default)
        field.pack(fill="x", ipady=6)
        fields.append(field)
    saved = False

    def save():
        nonlocal saved
        username, password, confirmation = (field.get() for field in fields)
        if not username.strip() or len(password) < 8 or len(password.encode("utf-8")) > 72 or password != confirmation:
            messagebox.showerror("Compte administrateur", "Vérifiez l’identifiant et deux mots de passe identiques de 8 caractères minimum (72 octets maximum).", parent=window)
            return
        try:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
            with database._connecter() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM users LIMIT 1 FOR UPDATE")
                    if not cursor.fetchone():
                        cursor.execute("""INSERT INTO users (username, nom, prenom, telephone, email, password, role)
                                          VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                       (username.strip(), "Administrateur", "UKAG", "", "admin@parking.ukag.local", hashed, 1))
                connection.commit()
        except Exception as failure:
            messagebox.showerror("Compte administrateur", str(failure), parent=window)
            return
        saved = True
        window.destroy()

    Button(body, text="Créer mon compte", command=save, bg=theme.Colors.PRIMARY,
           fg="white", relief="flat", pady=10).pack(fill="x", pady=(20, 0))
    window.mainloop()
    return saved
