import pymysql
import json
from tkinter import messagebox
from datetime import datetime, timedelta
from fonctions import today
from app.config import paths

class Bdonnee:
    def __init__(self):
        try:
            # Essayer d'ouvrir et de charger le fichier JSON
            with open(str(app.config.paths.CONFIG_FILE), "r") as config_file:
                config = json.load(config_file)
            
            self.host = config["host"]
            self.user = config["user"]
            self.password = config["password"]
            self.db_name = config["db_name"]
        
        except FileNotFoundError:
            print(f"Erreur : Le fichier {paths.CONFIG_FILE} est introuvable !")
            exit(1)  # Arrête le programme avec un code d'erreur

        except json.JSONDecodeError:
            print(f"Erreur : Le fichier {paths.CONFIG_FILE} est mal formaté !")
            exit(1)
        self.tables = ["historique", "users", "owners"]
        self._creer_tables()

    def _connecter(self):
        """ Crée et retourne une connexion à la base de données MariaDB. """
        return pymysql.connect(
            host=self.host, 
            user=self.user, 
            password=self.password, 
            database=self.db_name, 
            charset="utf8mb4"
        )
    
    def ajouter(self, indice_table, donnees):
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
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout : {e}")
            return False

    def modifier(self, indice_table, row_id, nouvelles_valeurs):
        try:
            table_name = self.tables[indice_table]
            colonnes_str = ", ".join(f"{col} = %s" for col in nouvelles_valeurs.keys())
            valeurs = list(nouvelles_valeurs.values())

            query = f"UPDATE {table_name} SET {colonnes_str} WHERE id = %s"

            with self._connecter() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (*valeurs, row_id))
                conn.commit()
            return True
        except pymysql.MySQLError as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification : {e}")
            return False

    def supprimer(self, indice_table, row_id):
        try:
            table_name = self.tables[indice_table]
            query = f"DELETE FROM {table_name} WHERE id = %s"

            with self._connecter() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (row_id,))
                conn.commit()
            return True
        except pymysql.MySQLError as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")
            return False

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
            messagebox.showerror("Erreur", f"Erreur lors de la création des tables : {e}")

    def rechercher_par_code_barre(self, code_barre):
        try:
            with self._connecter() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    query = "SELECT * FROM owners WHERE code_barre = %s"
                    cursor.execute(query, (code_barre,))
                    row = cursor.fetchone()
            return row
        except pymysql.MySQLError as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche : {e}")
            return None

    def ajouter_historique(self, date, owner_id, etat, heure):
        try:
            query = "INSERT INTO historique (date, owner_id, etat, heure) VALUES (%s, %s, %s, %s)"

            with self._connecter() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (date, owner_id, etat, heure))
                conn.commit()
            return True
        except pymysql.MySQLError as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout à l'historique : {e}")
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
            "etudiants": result[0] or 0,
            "enseignants": result[1] or 0,
            "Administratif": result[2] or 0,
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
                cursor.execute(query, (today(1),))  # Utilisation de paramètres pour éviter l'injection SQL
                result = cursor.fetchone() or (0, 0)  # Éviter une erreur si aucun résultat

        entrees = result[0] or 0
        sorties = result[1] or 0
        reste = entrees - sorties  # Correctement calculé

        return {
            "Entrée": entrees,
            "Sortie": sorties,
            "A l'intérieur": reste
        }



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


    def verifier_existence(self, code_barre, immatriculation):
        """Vérifie si le code-barres ou l'immatriculation existent déjà dans la table owners."""
        try:
            with self._connecter() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT code_barre, immatriculation 
                        FROM owners 
                        WHERE code_barre = %s OR immatriculation = %s
                    """
                    cursor.execute(query, (code_barre, immatriculation))
                    rows = cursor.fetchall()

            messages = []
            for row in rows:
                if row[0] == code_barre:
                    messages.append("Le code-barre existe déjà.")
                if row[1] == immatriculation:
                    messages.append("L'immatriculation existe déjà.")

            return (True, "\n".join(messages)) if messages else (False, "")

        except pymysql.MySQLError as e:
            return True, f"Erreur lors de la vérification {e}.\n"



    def get_user(self, username):
        """Récupère un utilisateur à partir de son username."""
        try:
            with self._connecter() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    query = "SELECT * FROM users WHERE username = %s LIMIT 1"
                    cursor.execute(query, (username,))
                    row = cursor.fetchone()
                    
                    return row if row else None
        except pymysql.MySQLError as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche : {e}")
            return None


    def rechercher_owner(self, param):
        """Recherche un propriétaire par code-barre ou téléphone"""
        try:
            with self._connecter() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    query = "SELECT * FROM owners WHERE code_barre = %s OR telephone = %s"
                    cursor.execute(query, (param, param))
                    result = cursor.fetchall()
                    return result if result else [] # Retourne résultat
        except pymysql.MySQLError as e:
            messagebox.showerror("Erreur", f"Erreur SQL : {e}")
            return []
