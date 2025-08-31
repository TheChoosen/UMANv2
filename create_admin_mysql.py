import mysql.connector
from mysql.connector import Error
from config_mysql import MYSQL_CONFIG
import hashlib

def create_admin_user(username='admin', email='admin@peupleun.live', password='admin123'):
    """Créer un utilisateur administrateur dans MySQL"""
    
    try:
        # Connexion à MySQL
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # Hash du mot de passe (méthode simple pour cet exemple)
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        # Vérifier si l'admin existe déjà
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            # Mettre à jour l'admin existant
            cursor.execute("""
                UPDATE users 
                SET username = %s, password = %s, is_admin = %s 
                WHERE email = %s
            """, (username, password_hash, 1, email))
            print(f"✓ Administrateur '{username}' mis à jour")
        else:
            # Créer un nouvel admin
            cursor.execute("""
                INSERT INTO users (username, password, email, is_admin, created_at) 
                VALUES (%s, %s, %s, %s, NOW())
            """, (username, password_hash, email, 1))
            print(f"✓ Administrateur '{username}' créé")
        
        connection.commit()
        
        print(f"📧 Email: {email}")
        print(f"🔐 Mot de passe: {password}")
        print("⚠️  Changez ce mot de passe après la première connexion!")
        
        return True
        
    except Error as e:
        print(f"❌ Erreur lors de la création de l'admin: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def list_users():
    """Lister tous les utilisateurs"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        print("\n📋 Liste des utilisateurs:")
        print("-" * 60)
        for user in users:
            admin_status = "👑 ADMIN" if user['is_admin'] else "👤 USER"
            print(f"{user['id']:3d} | {admin_status:8s} | {user['username']:20s} | {user['email']}")
        
        return users
        
    except Error as e:
        print(f"❌ Erreur lors de la lecture des utilisateurs: {e}")
        return []
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🔧 Gestion des utilisateurs MySQL")
    print(f"📍 Serveur: {MYSQL_CONFIG['host']}")
    print(f"📂 Base: {MYSQL_CONFIG['database']}")
    print("-" * 50)
    
    # Créer l'admin par défaut
    create_admin_user()
    
    # Lister les utilisateurs
    list_users()
