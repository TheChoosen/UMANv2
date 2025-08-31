#!/usr/bin/env python3
"""
Créer un utilisateur admin directement avec MySQL
"""

import mysql.connector
from config_mysql import MYSQL_CONFIG
import hashlib

def hash_code(content):
    """Fonction de hachage identique à celle dans l'app"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def create_admin_user():
    """Créer un utilisateur admin de test"""
    print("🔧 Création d'un utilisateur admin de test...")
    
    try:
        # Connexion directe à MySQL
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cur = db.cursor()
        
        # Vérifier si l'admin existe déjà
        cur.execute("SELECT id FROM membres WHERE email = %s", ('admin@rdkq.test',))
        if cur.fetchone():
            print("✅ Utilisateur admin existe déjà")
            return
        
        # Créer l'utilisateur admin
        email = 'admin@rdkq.test'
        password = 'admin123'
        password_hash = hash_code(password)
        
        cur.execute('''
            INSERT INTO membres (prenom, nom, email, password, username, is_admin, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ''', (
            'Admin',
            'Test',
            email,
            password_hash,
            'admin_test',
            True
        ))
        
        db.commit()
        print(f"✅ Utilisateur admin créé:")
        print(f"   Email: {email}")
        print(f"   Mot de passe: {password}")
        print(f"   Hash: {password_hash}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
    finally:
        if 'db' in locals():
            db.close()

def test_database():
    """Test de la base de données"""
    print("\n🧪 Test de la base de données...")
    
    try:
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cur = db.cursor()
        
        # Vérifier la table mediatheque
        cur.execute("SHOW TABLES LIKE 'mediatheque'")
        if cur.fetchone():
            print("✅ Table mediatheque existe")
            
            # Vérifier la structure
            cur.execute("DESCRIBE mediatheque")
            columns = cur.fetchall()
            print("   Colonnes disponibles:")
            for col in columns:
                print(f"     - {col[0]} ({col[1]})")
        else:
            print("❌ Table mediatheque n'existe pas")
            
        # Vérifier les utilisateurs admin
        cur.execute("SELECT id, email, username, is_admin FROM membres WHERE is_admin = 1")
        admins = cur.fetchall()
        print(f"\n✅ {len(admins)} administrateur(s) trouvé(s):")
        for admin in admins:
            print(f"   - ID: {admin[0]}, Email: {admin[1]}, Username: {admin[2]}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    create_admin_user()
    test_database()
    
    print("\n📋 Instructions de test:")
    print("1. Ouvrez votre navigateur")
    print("2. Allez à: http://127.0.0.1:8002/rdkq/login")
    print("3. Connectez-vous avec:")
    print("   Email: admin@rdkq.test")
    print("   Mot de passe: admin123")
    print("4. Allez à: http://127.0.0.1:8002/rdkq/admin/mediatheque/new")
    print("5. Ouvrez F12 (outils développeur) pour voir les logs JavaScript")
    print("6. Remplissez le formulaire et cliquez sur 'Créer le Média'")
    print("7. Vérifiez la console pour les messages de débogage")
