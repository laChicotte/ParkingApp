import pymysql
import json
from tkinter import messagebox
from datetime import datetime, timedelta
from app.config import paths
from app.utils.photos import PhotoChange, photo_path

class Bdonnee:
    def __init__(self):
        try:
            # Essayer d'ouvrir et de charger le fichier JSON
            with open(paths.CONFIG_FILE, "r", encoding="utf-8-sig") as config_file:
                config = json.load(config_file)

            if not isinstance(config, dict):
                raise ValueError("La configuration MySQL doit être un objet JSON.")
            required = ("host", "user", "password", "db_name")
            missing = [key for key in required if key not in config]
            if missing:
                raise ValueError("Configuration MySQL incomplète : " + ", ".join(missing))
            for key in required:
                if not isinstance(config[key], str) or (key != "password" and not config[key].strip()):
                    raise ValueError(f"Le paramètre MySQL {key} doit être une chaîne valide.")
            
            self.host = config["host"]
            self.user = config["user"]
            self.password = config["password"]
            self.db_name = config["db_name"]
            self.port = int(config.get("port", 3306))
            if not 1 <= self.port <= 65535:
                raise ValueError("Le port MySQL doit être compris entre 1 et 65535.")
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration MySQL introuvable : {paths.CONFIG_FILE}") from None

        except json.JSONDecodeError:
            raise ValueError(f"Configuration JSON invalide : {paths.CONFIG_FILE}") from None
        self.tables = ["historique", "users", "owners"]
        self.last_warning = ""
        self._creer_tables()

    def _connecter(self):
        """Crée une connexion MySQL/MariaDB à partir de la configuration locale."""
        return pymysql.connect(
            host=self.host, 
            user=self.user, 
            password=self.password, 
            database=self.db_name, 
            port=self.port,
            charset="utf8mb4",
            connect_timeout=5,
            read_timeout=10,
            write_timeout=10
        )
    
    def ajouter(self, indice_table, donnees, notify=True):
        self.last_error = ""
        try:
            table_name = self.tables[indice_table]
            placeholders = ", ".join(["%s"] * len(donnees))
            query = f"INSERT INTO {table_name} VALUES (NULL, {placeholders})"

            with self._connecter() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, donnees)
                conn.commit()
            return True
        except pymysql.MySQLError as e:
            self.last_error = f"Erreur lors de l'ajout : {e}"
            if notify:
                messagebox.showerror("Erreur", self.last_error)
            return False

    def modifier(self, indice_table, row_id, nouvelles_valeurs, notify=True):
        self.last_error = ""
        self.last_warning = ""
        photo = None
        connection = None
        committed = False
        try:
            table_name = self.tables[indice_table]
            colonnes_str = ", ".join(f"{col} = %s" for col in nouvelles_valeurs.keys())
            valeurs = list(nouvelles_valeurs.values())

            query = f"UPDATE {table_name} SET {colonnes_str} WHERE id = %s"

            with self._connecter() as conn:
                connection = conn
                conn.begin()
                with conn.cursor() as cursor:
                    key = "code_barre" if table_name == "owners" else "telephone" if table_name == "users" else None
                    if key and key in nouvelles_valeurs:
                        cursor.execute(f"SELECT {key} FROM {table_name} WHERE id = %s FOR UPDATE", (row_id,))
                        row = cursor.fetchone()
                        if row is None:
                            raise ValueError("Cette fiche n'existe plus. Actualisez la liste.")
                        photo = PhotoChange(photo_path(table_name, row[0]), photo_path(table_name, nouvelles_valeurs[key]))
                        photo.prepare()
                    cursor.execute(query, (*valeurs, row_id))
                    referenced = self._photo_referenced(cursor, photo.source) if photo and photo.source != photo.destination else False
                conn.commit()
                committed = True
            self._finish_photo(photo, referenced)
            return True
        except (pymysql.MySQLError, OSError, ValueError) as e:
            if committed:
                self._finish_photo(photo, referenced)
                self.last_warning = self.last_warning or f"La modification est enregistrée, mais la connexion s'est fermée avec une erreur : {e}"
                return True
            if connection is not None:
                try:
                    connection.rollback()
                except pymysql.MySQLError:
                    pass
            if photo is not None:
                try:
                    photo.rollback()
                except (OSError, ValueError):
                    self.last_warning = "Une copie temporaire de photo n'a pas pu être supprimée."
            self.last_error = f"Erreur lors de la modification : {e}"
            if notify:
                messagebox.showerror("Erreur", self.last_error)
            return False

    def supprimer(self, indice_table, row_id):
        self.last_error = ""
        self.last_warning = ""
        committed = False
        try:
            table_name = self.tables[indice_table]
            query = f"DELETE FROM {table_name} WHERE id = %s"

            with self._connecter() as conn:
                conn.begin()
                with conn.cursor() as cursor:
                    key = "code_barre" if table_name == "owners" else "telephone" if table_name == "users" else None
                    photo = None
                    if key:
                        cursor.execute(f"SELECT {key} FROM {table_name} WHERE id = %s FOR UPDATE", (row_id,))
                        row = cursor.fetchone()
                        if row is None:
                            raise ValueError("Cette fiche n'existe plus. Actualisez la liste.")
                        photo = PhotoChange(photo_path(table_name, row[0]))
                    cursor.execute(query, (row_id,))
                    referenced = self._photo_referenced(cursor, photo.source) if photo else False
                conn.commit()
                committed = True
            self._finish_photo(photo, referenced)
            return True
        except (pymysql.MySQLError, OSError, ValueError) as e:
            if committed:
                self._finish_photo(photo, referenced)
                self.last_warning = self.last_warning or f"La suppression est enregistrée, mais la connexion s'est fermée avec une erreur : {e}"
                return True
            self.last_error = f"Erreur lors de la suppression : {e}"
            messagebox.showerror("Erreur", self.last_error)
            return False

    @staticmethod
    def _photo_referenced(cursor, path):
        if path is None:
            return False
        # Les comptes et les propriétaires peuvent partager le même nom de fichier.
        cursor.execute("""SELECT 1 FROM owners
                          WHERE (CASE WHEN CHAR_LENGTH(TRIM(code_barre)) < 6
                                 THEN LPAD(TRIM(code_barre), 6, '0') ELSE TRIM(code_barre) END) = %s
                          UNION ALL SELECT 1 FROM users WHERE TRIM(telephone) = %s LIMIT 1""",
                       (path.stem, path.stem))
        return cursor.fetchone() is not None

    def _finish_photo(self, photo, referenced):
        if photo is None:
            return
        try:
            photo.finish(still_referenced=referenced)
        except (OSError, ValueError) as error:
            self.last_warning = f"La base est mise à jour, mais l'ancienne photo n'a pas pu être supprimée : {error}"

    def recuperer(self, indice_table):
        try:
            table_name = self.tables[indice_table]
            query = f"SELECT * FROM {table_name}"

            with self._connecter() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
            return rows
        except pymysql.MySQLError as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération : {e}")
            return []

    def _creer_tables(self):
        """Crée les tables si elles n'existent pas."""
        try:
            with self._connecter() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(255) NOT NULL,
                            nom VARCHAR(255) NOT NULL,
                            prenom VARCHAR(255) NOT NULL,
                            telephone VARCHAR(20) NOT NULL,
                            email VARCHAR(255) NOT NULL UNIQUE,
                            password VARCHAR(255) NOT NULL,
                            role INT NOT NULL
                        )
                    """)

                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS owners (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            nom VARCHAR(255) NOT NULL,
                            prenom VARCHAR(255) NOT NULL,
                            matricule VARCHAR(50),
                            marque VARCHAR(100) DEFAULT '------',
                            immatriculation VARCHAR(100) NOT NULL UNIQUE,
                            telephone VARCHAR(20) NOT NULL,
                            code_barre VARCHAR(100) NOT NULL UNIQUE,
                            couleur VARCHAR(50) NOT NULL,
                            statut VARCHAR(50) NOT NULL
                        )
                    """)

                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS historique (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            date DATE NOT NULL,
                            owner_id INT NOT NULL,
                            etat VARCHAR(255) NOT NULL,
                            heure TIME NOT NULL,
                            FOREIGN KEY (owner_id) REFERENCES owners(id) ON DELETE CASCADE
                        )
                    """)
                conn.commit()
        except pymysql.MySQLError as e:
            # Une initialisation échouée doit interrompre le démarrage.
            raise pymysql.OperationalError(
                f"Impossible de préparer les tables MySQL dans {self.db_name} "
                f"sur {self.host}:{self.port} : {e}"
            ) from e

    def rechercher_par_code_barre(self, code_barre, notify=True):
        self.last_error = ""
        try:
            with self._connecter() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    query = "SELECT * FROM owners WHERE code_barre = %s"
                    cursor.execute(query, (code_barre,))
                    row = cursor.fetchone()
            return row
        except pymysql.MySQLError as e:
            self.last_error = f"Erreur lors de la recherche : {e}"
            if notify:
                messagebox.showerror("Erreur", self.last_error)
            return None

    def ajouter_historique(self, date, owner_id, etat, heure):
        """Enregistre un passage en alternant entrée et sortie pour chaque moto."""
        self.last_error = ""
        try:
            if etat not in ("Entrée", "Sortie"):
                raise ValueError("Le mouvement doit être une entrée ou une sortie.")
            # Les vues affichent des dates françaises et des heures comme 14h20min.
            # MySQL attend des valeurs DATE et TIME, contrairement à SQLite.
            if isinstance(date, str):
                try:
                    date = datetime.strptime(date, "%d-%m-%Y").date()
                except ValueError:
                    date = datetime.strptime(date, "%Y-%m-%d").date()
            if isinstance(heure, str):
                heure = datetime.strptime(heure, "%Hh%Mmin").time() if "h" in heure else datetime.strptime(heure, "%H:%M:%S").time()
            query = "INSERT INTO historique (date, owner_id, etat, heure) VALUES (%s, %s, %s, %s)"

            with self._connecter() as conn:
                conn.begin()
                with conn.cursor() as cursor:
                    # Verrouiller la moto avant de lire son état : deux scans
                    # simultanés doivent effectuer le contrôle l'un après l'autre.
                    cursor.execute("SELECT id FROM owners WHERE id = %s FOR UPDATE", (owner_id,))
                    if not cursor.fetchone():
                        self.last_error = "Cette moto n’existe plus dans les usagers du parking."
                        conn.rollback()
                        return False
                    cursor.execute(
                        "SELECT etat FROM historique WHERE owner_id = %s ORDER BY id DESC LIMIT 1 FOR UPDATE",
                        (owner_id,),
                    )
                    previous = cursor.fetchone()
                    if not previous and etat == "Sortie":
                        self.last_error = "Sortie refusée : aucune entrée n’a encore été enregistrée pour cette moto."
                    elif previous and previous[0] not in ("Entrée", "Sortie"):
                        self.last_error = "Le dernier mouvement de cette moto est inconnu. Vérifiez son historique."
                    elif previous and previous[0] == etat:
                        self.last_error = (
                            "Entrée refusée : cette moto est déjà à l’intérieur. Enregistrez sa sortie avant une nouvelle entrée."
                            if etat == "Entrée" else
                            "Sortie refusée : cette moto est déjà à l’extérieur. Enregistrez son entrée avant une nouvelle sortie."
                        )
                    if self.last_error:
                        conn.rollback()
                        return False
                    cursor.execute(query, (date, owner_id, etat, heure))
                conn.commit()
            return True
        except (pymysql.MySQLError, ValueError) as e:
            self.last_error = f"Impossible d’enregistrer le mouvement : {e}"
            return False

    def recuperer_historique(self):
        try:
            query = """
                SELECT 
                    h.id AS historique_id, 
                    h.date, 
                    h.etat, 
                    h.heure, 
                    o.nom, 
                    o.prenom, 
                    o.matricule, 
                    o.marque, 
                    o.immatriculation, 
                    o.telephone, 
                    o.code_barre, 
                    o.couleur
                FROM 
                    historique h
                INNER JOIN 
                    owners o ON h.owner_id = o.id
                ORDER BY 
                    h.date DESC
            """

            with self._connecter() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
            return rows
        except pymysql.MySQLError as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération de l'historique : {e}")
            return []

    def mettre_a_jour_sortie(self, heure_sortie, code_barre):
        """Met à jour l'heure de sortie pour la dernière entrée avec ce code-barre."""
        try:
            query = """
                UPDATE historique
                SET sortie = %s
                WHERE id = (
                    SELECT h.id
                    FROM historique h
                    INNER JOIN owners o ON h.owner_id = o.id
                    WHERE o.code_barre = %s AND h.sortie = '------'
                    ORDER BY h.date DESC, h.heure DESC
                    LIMIT 1
                )
            """
            with self._connecter() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (heure_sortie, code_barre))
                    if cursor.rowcount == 0:
                        messagebox.showerror("Erreur", "Aucune entrée à mettre à jour.")
                        return False
                    conn.commit()
                    return True
        except pymysql.MySQLError as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour de l'heure de sortie : {e}")
            return False


    def count_owners_by_statut(self):
        """Compte le nombre de propriétaires par statut."""
        query = """
            SELECT statut, COUNT(*) 
            FROM owners
            GROUP BY statut
        """
        with self._connecter() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        return {row[0]: row[1] for row in results}


    def count_history_by_type(self):
        """Compte le nombre d'entrées dans l'historique par type d'état."""
        query = """
            SELECT etat, COUNT(*) 
            FROM historique
            GROUP BY etat
        """
        with self._connecter() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        return {row[0]: row[1] for row in results}


    def get_global_stats(self):
        """Retourne les statistiques globales sur les propriétaires."""
        query = """
            SELECT 
                SUM(CASE WHEN statut = 'Etudiant' THEN 1 ELSE 0 END) AS etudiants,
                SUM(CASE WHEN statut = 'Enseignant' THEN 1 ELSE 0 END) AS enseignants,
                SUM(CASE WHEN statut = 'Personnel' THEN 1 ELSE 0 END) AS administratif,
                COUNT(*) AS motards
            FROM owners
        """
        with self._connecter() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
        return {
            "etudiants": int(result[0] or 0),
            "enseignants": int(result[1] or 0),
            "Administratif": int(result[2] or 0),
            # "motards": result[3] or 0
        }
    
    def get_tab_values(self):
        """Retourne les statistiques globales sur les propriétaires."""
        query = """
            SELECT 
                SUM(CASE WHEN etat = 'Entrée' THEN 1 ELSE 0 END) AS etudiants,
                SUM(CASE WHEN etat = 'Sortie' THEN 1 ELSE 0 END) AS enseignants
            FROM historique 
            WHERE date = %s
        """
        with self._connecter() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (datetime.now().date(),))
                result = cursor.fetchone() or (0, 0)  # Éviter une erreur si aucun résultat

        entrees = int(result[0] or 0)
        sorties = int(result[1] or 0)
        reste = entrees - sorties  # Correctement calculé

        return {
            "Entrée": entrees,
            "Sortie": sorties,
            "A l'intérieur": reste
        }



    def get_daily_movements(self, days=15):
        """Entrées et sorties par jour, dans l'ordre et avec les jours vides."""
        if not isinstance(days, int) or not 1 <= days <= 366:
            raise ValueError("La période doit contenir entre 1 et 366 jours.")
        end = datetime.now().date()
        start = end - timedelta(days=days - 1)
        query = """
            SELECT date,
                   SUM(CASE WHEN etat = 'Entrée' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN etat = 'Sortie' THEN 1 ELSE 0 END)
            FROM historique
            WHERE date BETWEEN %s AND %s
            GROUP BY date
            ORDER BY date
        """
        with self._connecter() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (start, end))
                counts = {row[0]: (int(row[1] or 0), int(row[2] or 0))
                          for row in cursor.fetchall()}
        return [
            {"date": start + timedelta(days=offset),
             "entries": counts.get(start + timedelta(days=offset), (0, 0))[0],
             "exits": counts.get(start + timedelta(days=offset), (0, 0))[1]}
            for offset in range(days)
        ]

    def get_entries_last_30_days(self):
        """Récupère le nombre d'entrées par jour pour les 30 derniers jours."""
        today = datetime.now().date()

        query = """
            SELECT DATE(date), COUNT(*) 
            FROM historique 
            WHERE DATE(date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY DATE(date)
            ORDER BY DATE(date) DESC;
        """
        with self._connecter() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

        entries_by_day = {row[0].strftime("%d-%m-%Y"): row[1] for row in results}

        # Remplir les jours manquants avec 0
        for i in range(30):
            current_date = (today - timedelta(days=i)).strftime("%d-%m-%Y")
            if current_date not in entries_by_day:
                entries_by_day[current_date] = 0

        return entries_by_day


    def verifier_existence(self, code_barre, immatriculation, exclude_id=None):
        """Cherche les doublons, hors de l'usager modifié si son ID est fourni."""
        try:
            with self._connecter() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT code_barre = %s, immatriculation = %s
                        FROM owners 
                        WHERE (code_barre = %s OR immatriculation = %s)
                    """
                    params = (code_barre, immatriculation, code_barre, immatriculation)
                    if exclude_id is not None:
                        query += " AND id <> %s"
                        params += (exclude_id,)
                    cursor.execute(query, params)
                    rows = cursor.fetchall()

            messages = []
            for row in rows:
                if row[0] and "Le code-barre existe déjà." not in messages:
                    messages.append("Le code-barre existe déjà.")
                if row[1] and "L'immatriculation existe déjà." not in messages:
                    messages.append("L'immatriculation existe déjà.")

            return (True, "\n".join(messages)) if messages else (False, "")

        except pymysql.MySQLError as e:
            return True, f"Erreur lors de la vérification {e}.\n"



    def get_user(self, username, notify=True):
        """Récupère un utilisateur à partir de son username."""
        self.last_error = ""
        try:
            with self._connecter() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    query = "SELECT * FROM users WHERE username = %s LIMIT 1"
                    cursor.execute(query, (username,))
                    row = cursor.fetchone()
                    
                    return row if row else None
        except pymysql.MySQLError as e:
            self.last_error = f"Erreur lors de la recherche : {e}"
            if notify:
                messagebox.showerror("Erreur", self.last_error)
            return None


    def rechercher_owner(self, param, notify=True):
        """Recherche partielle par identité, matricule, téléphone, plaque ou code."""
        self.last_error = ""
        columns = ("nom", "prenom", "matricule", "telephone", "immatriculation", "code_barre")
        conditions = []
        params = []
        for word in str(param).split():
            # Les caractères saisis restent littéraux, même % et _.
            pattern = "%" + word.replace("=", "==").replace("%", "=%").replace("_", "=_") + "%"
            conditions.append("(" + " OR ".join(
                f"LOWER({column}) LIKE LOWER(%s) ESCAPE '='" for column in columns) + ")")
            params.extend([pattern] * len(columns))
        try:
            with self._connecter() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    query = "SELECT * FROM owners"
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
                    query += " ORDER BY nom, prenom, id"
                    cursor.execute(query, tuple(params))
                    result = cursor.fetchall()
                    return result if result else [] # Retourne résultat
        except pymysql.MySQLError as e:
            self.last_error = f"Erreur SQL : {e}"
            if notify:
                messagebox.showerror("Erreur", self.last_error)
            return []
