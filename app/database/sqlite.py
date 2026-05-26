import sqlite3
from tkinter import messagebox
from datetime import datetime, timedelta
from app.utils.fonctions import today
from app.config import paths

class Bdonnee:
    def __init__(self):
        # Utiliser SQLite au lieu de MySQL
        self.db_file = str(paths.DB_FILE)
        self.tables = ["historique", "users", "owners"]
        self._creer_tables()
        self._creer_admin_par_defaut()
        self._normaliser_codes_barres()

    def _connecter(self):
        """ Crée et retourne une connexion à la base de données SQLite. """
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # Pour obtenir des dictionnaires au lieu de tuples
        return conn
    
    def ajouter(self, indice_table, donnees):
        try:
            table_name = self.tables[indice_table]
            placeholders = ", ".join(["?"] * len(donnees))
            query = f"INSERT INTO {table_name} VALUES (NULL, {placeholders})"

            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute(query, donnees)
                conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout : {e}")
            return False

    def modifier(self, indice_table, row_id, nouvelles_valeurs):
        try:
            table_name = self.tables[indice_table]
            colonnes_str = ", ".join(f"{col} = ?" for col in nouvelles_valeurs.keys())
            valeurs = list(nouvelles_valeurs.values())

            query = f"UPDATE {table_name} SET {colonnes_str} WHERE id = ?"

            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (*valeurs, row_id))
                conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification : {e}")
            return False

    def supprimer(self, indice_table, row_id):
        try:
            table_name = self.tables[indice_table]
            query = f"DELETE FROM {table_name} WHERE id = ?"

            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (row_id,))
                conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")
            return False

    def recuperer(self, indice_table):
        try:
            table_name = self.tables[indice_table]
            query = f"SELECT * FROM {table_name}"

            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                # Convertir les Row en dictionnaires
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération : {e}")
            return []

    def _creer_tables(self):
        """Crée les tables si elles n'existent pas."""
        try:
            with self._connecter() as conn:
                cursor = conn.cursor()
                
                # Activer les clés étrangères pour SQLite
                cursor.execute("PRAGMA foreign_keys = ON")

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        nom TEXT NOT NULL,
                        prenom TEXT NOT NULL,
                        telephone TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        role INTEGER NOT NULL
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS owners (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom TEXT NOT NULL,
                        prenom TEXT NOT NULL,
                        matricule TEXT,
                        marque TEXT DEFAULT '------',
                        immatriculation TEXT NOT NULL UNIQUE,
                        telephone TEXT NOT NULL,
                        code_barre TEXT NOT NULL UNIQUE,
                        couleur TEXT NOT NULL,
                        statut TEXT NOT NULL
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS historique (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        owner_id INTEGER NOT NULL,
                        etat TEXT NOT NULL,
                        heure TEXT NOT NULL,
                        FOREIGN KEY (owner_id) REFERENCES owners(id) ON DELETE CASCADE
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création des tables : {e}")

    def _creer_admin_par_defaut(self):
        """Crée un utilisateur administrateur par défaut si aucun utilisateur n'existe."""
        try:
            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    import bcrypt
                    # Créer un admin par défaut : username="admin", password="admin"
                    password_hash = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt())
                    cursor.execute("""
                        INSERT INTO users (username, nom, prenom, telephone, email, password, role)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, ("admin", "Administrateur", "Système", "000000000", "admin@parking.local", password_hash, 1))
                    conn.commit()
        except sqlite3.Error:
            pass  # Ignorer les erreurs silencieusement

    def _normaliser_codes_barres(self):
        """Normalise tous les codes-barres existants à 6 chiffres (migration unique)."""
        try:
            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, code_barre FROM owners WHERE LENGTH(code_barre) < 6")
                rows = cursor.fetchall()
                for row in rows:
                    padded = str(row['code_barre']).zfill(6)
                    try:
                        cursor.execute("UPDATE owners SET code_barre = ? WHERE id = ?", (padded, row['id']))
                    except sqlite3.IntegrityError:
                        pass  # Conflit UNIQUE : donnée dupliquée, ignorer
                conn.commit()
        except sqlite3.Error:
            pass

    def rechercher_par_code_barre(self, code_barre):
        try:
            code_barre = str(code_barre).zfill(6)
            with self._connecter() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM owners WHERE code_barre = ?"
                cursor.execute(query, (code_barre,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche : {e}")
            return None

    def vider_historique(self):
        """Supprime tous les enregistrements de l'historique."""
        try:
            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM historique")
                conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")
            return False

    def get_dernier_etat(self, owner_id):
        """Retourne le dernier état enregistré AUJOURD'HUI pour cet owner ('Entrée', 'Sortie', ou None)."""
        try:
            query = """
                SELECT etat FROM historique
                WHERE owner_id = ? AND date = ?
                ORDER BY heure DESC
                LIMIT 1
            """
            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (owner_id, today(1)))
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error:
            return None

    def ajouter_historique(self, date, owner_id, etat, heure):
        try:
            query = "INSERT INTO historique (date, owner_id, etat, heure) VALUES (?, ?, ?, ?)"

            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (date, owner_id, etat, heure))
                conn.commit()
            return True
        except sqlite3.Error as e:
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
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération de l'historique : {e}")
            return []

    def mettre_a_jour_sortie(self, heure_sortie, code_barre):
        """Met à jour l'heure de sortie pour la dernière entrée avec ce code-barre."""
        try:
            query = """
                UPDATE historique
                SET sortie = ?
                WHERE id = (
                    SELECT h.id
                    FROM historique h
                    INNER JOIN owners o ON h.owner_id = o.id
                    WHERE o.code_barre = ? AND h.sortie = '------'
                    ORDER BY h.date DESC, h.heure DESC
                    LIMIT 1
                )
            """
            with self._connecter() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (heure_sortie, code_barre))
                if cursor.rowcount == 0:
                    messagebox.showerror("Erreur", "Aucune entrée à mettre à jour.")
                    return False
                conn.commit()
                return True
        except sqlite3.Error as e:
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
            cursor = conn.cursor()
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
            cursor = conn.cursor()
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
            cursor = conn.cursor()
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
            WHERE date = ?
        """
        with self._connecter() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (today(1),))
            result = cursor.fetchone() or (0, 0)

        entrees = result[0] or 0
        sorties = result[1] or 0
        reste = entrees - sorties

        return {
            "Entrée": entrees,
            "Sortie": sorties,
            "A l'intérieur": reste
        }



    def get_entries_last_30_days(self):
        """Récupère le nombre d'entrées par jour pour les 30 derniers jours."""
        today_date = datetime.now().date()

        query = """
            SELECT date(date) as date_str, COUNT(*) 
            FROM historique 
            WHERE date(date) >= date('now', '-30 days')
            GROUP BY date(date)
            ORDER BY date(date) DESC
        """
        with self._connecter() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

        entries_by_day = {}
        for row in results:
            # Convertir la date SQLite en format souhaité
            date_obj = datetime.strptime(row[0], "%Y-%m-%d").date()
            date_str = date_obj.strftime("%d-%m-%Y")
            entries_by_day[date_str] = row[1]

        # Remplir les jours manquants avec 0
        for i in range(30):
            current_date = (today_date - timedelta(days=i)).strftime("%d-%m-%Y")
            if current_date not in entries_by_day:
                entries_by_day[current_date] = 0

        return entries_by_day


    def verifier_existence(self, code_barre, immatriculation, exclude_id=None):
        """Vérifie si le code-barres ou l'immatriculation existent déjà dans la table owners.
        exclude_id : exclure l'owner en cours de modification."""
        code_barre = str(code_barre).zfill(6)
        try:
            with self._connecter() as conn:
                cursor = conn.cursor()
                if exclude_id:
                    query = """
                        SELECT code_barre, immatriculation
                        FROM owners
                        WHERE (code_barre = ? OR immatriculation = ?)
                        AND id != ?
                    """
                    cursor.execute(query, (code_barre, immatriculation, exclude_id))
                else:
                    query = """
                        SELECT code_barre, immatriculation
                        FROM owners
                        WHERE code_barre = ? OR immatriculation = ?
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

        except sqlite3.Error as e:
            return True, f"Erreur lors de la vérification {e}.\n"



    def get_user(self, username):
        """Récupère un utilisateur à partir de son username."""
        try:
            with self._connecter() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM users WHERE username = ? LIMIT 1"
                cursor.execute(query, (username,))
                row = cursor.fetchone()
                
                return dict(row) if row else None
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche : {e}")
            return None


    def rechercher_owner(self, param):
        """Recherche un propriétaire par code-barre ou téléphone"""
        try:
            with self._connecter() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM owners WHERE code_barre = ? OR telephone = ?"
                cursor.execute(query, (param, param))
                results = cursor.fetchall()
                return [dict(row) for row in results] if results else []
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur SQL : {e}")
            return []

