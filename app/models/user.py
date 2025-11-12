"""
Modèle utilisateur avec gestion des rôles et permissions
"""
import bcrypt


class User:
    """
    Classe pour gérer les utilisateurs et les sessions.
    """
    # Définition des rôles et leurs permissions
    ROLES = {
        0: "Utilisateur",  # Utilisateur normal
        1: "Administrateur",  # Administrateur
        2: "Super Admin"  # Super administrateur
    }

    # Définition des permissions par rôle
    PERMISSIONS = {
        0: ["view_entries", "view_exits", "scan_entries", "scan_exits"],  # Permissions utilisateur
        1: ["view_entries", "view_exits", "scan_entries", "scan_exits", "manage_users", "view_dashboard", "manage_owners"],  # Permissions admin
        2: ["view_entries", "view_exits", "scan_entries", "scan_exits", "manage_users", "view_dashboard", "manage_owners", "manage_admins"]  # Permissions super admin
    }

    def __init__(self, user_id=0, username="Connexion", email="null", password="null", role=0):
        """
        Initialise un utilisateur.
        
        Args:
            user_id (int): L'ID unique de l'utilisateur.
            username (str): Le nom d'utilisateur.
            email (str): L'adresse e-mail de l'utilisateur.
            password (str): Le mot de passe haché de l'utilisateur.
            role (int): Le rôle de l'utilisateur (0: utilisateur normal, 1: admin, 2: super admin).
        """
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.permissions = self.PERMISSIONS.get(role, [])
        
    def name(self):
        return self.username
    
    def verify_password(self, plain_password):
        """
        Vérifie si le mot de passe en clair correspond au mot de passe haché.
        """
        try:
            hashed_password = self.password.encode('utf-8') if isinstance(self.password, str) else self.password
            if bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password):
                return True
        except Exception as e:
            print(f"Erreur de vérification du mot de passe: {e}")
        return False
    
    def has_permission(self, permission):
        """
        Vérifie si l'utilisateur a une permission spécifique.
        
        Args:
            permission (str): La permission à vérifier.
            
        Returns:
            bool: True si l'utilisateur a la permission, False sinon.
        """
        return permission in self.permissions
    
    def get_role_name(self):
        """
        Retourne le nom du rôle de l'utilisateur.
        """
        return self.ROLES.get(self.role, "Rôle inconnu")
    
    def is_admin(self):
        """
        Vérifie si l'utilisateur a un rôle d'administrateur ou supérieur.
        """
        return self.role >= 1
    
    def is_super_admin(self):
        """
        Vérifie si l'utilisateur est un super administrateur.
        """
        return self.role == 2

    def __repr__(self):
        """
        Représentation textuelle de l'utilisateur (utile pour le débogage).
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role={self.get_role_name()})>"

