import mysql.connector
from mysql.connector import Error
from config_mysql import MYSQL_CONFIG

def create_mysql_schema():
    """Créer le schéma et les tables dans MySQL"""
    
    # Configuration pour se connecter sans schéma spécifique
    admin_config = MYSQL_CONFIG.copy()
    admin_config.pop('database', None)  # Retirer le schéma pour le créer
    
    try:
        # Connexion administrative
        connection = mysql.connector.connect(**admin_config)
        cursor = connection.cursor()
        
        # 1. Créer le schéma peupleun s'il n'existe pas
        print("Création du schéma 'peupleun'...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS peupleun CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ Schéma 'peupleun' créé ou existe déjà")
        
        # 2. Utiliser le schéma peupleun
        cursor.execute("USE peupleun")
        
        # 3. Créer la table users
        print("Création de la table 'users'...")
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            password VARCHAR(120) NOT NULL,
            email VARCHAR(120) UNIQUE,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_username (username),
            INDEX idx_email (email)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        cursor.execute(create_users_table)
        print("✓ Table 'users' créée")
        
        # 4. Créer la table submissions  
        print("Création de la table 'submissions'...")
        create_submissions_table = """
        CREATE TABLE IF NOT EXISTS submissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL,
            email VARCHAR(120),
            nom VARCHAR(100),
            prenom VARCHAR(100),
            age VARCHAR(10),
            region VARCHAR(100),
            occupation VARCHAR(200),
            salaire VARCHAR(50),
            education VARCHAR(200),
            sante VARCHAR(200),
            transport VARCHAR(200),
            logement VARCHAR(200),
            environnement VARCHAR(200),
            economie VARCHAR(200),
            securite VARCHAR(200),
            culture VARCHAR(200),
            participation VARCHAR(200),
            priorites TEXT,
            ameliorations TEXT,
            commentaires TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_username (username),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        cursor.execute(create_submissions_table)
        print("✓ Table 'submissions' créée")
        
        # 5. Créer la table cercles
        print("Création de la table 'cercles'...")
        create_cercles_table = """
        CREATE TABLE IF NOT EXISTS cercles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(200) NOT NULL,
            description TEXT,
            region VARCHAR(100),
            membres_count INT DEFAULT 0,
            created_by VARCHAR(80),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_region (region),
            INDEX idx_created_by (created_by)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        cursor.execute(create_cercles_table)
        print("✓ Table 'cercles' créée")
        
        # 6. Créer un utilisateur admin par défaut
        print("Création de l'utilisateur admin par défaut...")
        create_admin_user = """
        INSERT IGNORE INTO users (username, password, email, is_admin) 
        VALUES ('admin', 'pbkdf2:sha256:600000$default$hash', 'admin@peupleun.live', TRUE)
        """
        cursor.execute(create_admin_user)
        print("✓ Utilisateur admin créé")
        
        connection.commit()
        print("\n🎉 Migration MySQL terminée avec succès!")
        print("📊 Schéma 'peupleun' créé avec les tables:")
        print("   - users (gestion des utilisateurs)")
        print("   - submissions (données du questionnaire)")  
        print("   - cercles (cercles de démocratie)")
        
    except Error as e:
        print(f"❌ Erreur lors de la création MySQL: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("📝 Connexion MySQL fermée")
    
    return True

def test_mysql_connection():
    """Tester la connexion MySQL"""
    try:
        # Test avec le schéma peupleun
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # Test de lecture
        cursor.execute("SELECT COUNT(*) as user_count FROM users")
        result = cursor.fetchone()
        print(f"✓ Test connexion réussi - {result[0]} utilisateurs dans la base")
        
        # Test des tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✓ Tables disponibles: {[table[0] for table in tables]}")
        
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Erreur de test de connexion: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Début de la migration MySQL...")
    print(f"📍 Serveur: {MYSQL_CONFIG['host']}")
    print(f"📂 Schéma: {MYSQL_CONFIG['database']}")
    print(f"👤 Utilisateur: {MYSQL_CONFIG['user']}")
    print("-" * 50)
    
    # Créer le schéma et les tables
    if create_mysql_schema():
        print("\n🔍 Test de la connexion...")
        test_mysql_connection()
    else:
        print("❌ Échec de la migration")
