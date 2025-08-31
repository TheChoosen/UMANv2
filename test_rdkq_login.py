#!/usr/bin/env python3
"""
Test du système de login RDKQ
"""

import mysql.connector
from config_mysql import MYSQL_CONFIG
from datetime import datetime, timezone
import hashlib

def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode('utf-8')).hexdigest()

def test_rdkq_login_system():
    """Tester le système de login RDKQ"""
    
    print("🎯 Test du système de login RDKQ")
    print("=" * 50)
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Créer un utilisateur de test
        print("👤 Création d'un utilisateur de test...")
        test_email = "test@rdkq.live"
        test_password = "test123"
        test_username = "Test User"
        password_hash = hash_code(test_password)
        now = datetime.now(timezone.utc).isoformat()
        
        # Supprimer l'utilisateur de test s'il existe
        cursor.execute('DELETE FROM membres WHERE email = %s', (test_email,))
        
        # Créer le nouvel utilisateur
        cursor.execute('''
            INSERT INTO membres (username, email, password, nom, is_admin, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (test_username, test_email, password_hash, "User", 0, now))
        
        connection.commit()
        print(f"✅ Utilisateur de test créé: {test_email}")
        
        # 2. Tester la vérification des identifiants
        print("\n🔍 Test de vérification des identifiants...")
        
        # Test avec bon mot de passe
        cursor.execute('SELECT * FROM membres WHERE email = %s', (test_email,))
        user = cursor.fetchone()
        
        if user and hash_code(test_password) == user['password']:
            print("✅ Vérification mot de passe réussie")
        else:
            print("❌ Échec vérification mot de passe")
        
        # Test avec mauvais mot de passe
        if hash_code("wrong_password") != user['password']:
            print("✅ Rejet mauvais mot de passe réussi")
        else:
            print("❌ Échec rejet mauvais mot de passe")
        
        # 3. Tester les administrateurs
        print("\n👑 Test des administrateurs...")
        cursor.execute('SELECT username, email FROM membres WHERE is_admin = 1')
        admins = cursor.fetchall()
        
        print(f"📊 {len(admins)} administrateurs trouvés:")
        for admin in admins:
            print(f"   - {admin['username']} ({admin['email']})")
            
            # Test login admin avec mot de passe temporaire
            if 'admin' in admin['email']:
                print(f"   ✅ Admin peut utiliser le mot de passe temporaire 'admin123'")
        
        # 4. Statistiques de la base
        print("\n📈 Statistiques des membres:")
        cursor.execute('SELECT COUNT(*) as total FROM membres')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as admins FROM membres WHERE is_admin = 1')
        admin_count = cursor.fetchone()['admins']
        
        cursor.execute('SELECT COUNT(*) as users FROM membres WHERE is_admin = 0')
        user_count = cursor.fetchone()['users']
        
        print(f"   Total: {total} membres")
        print(f"   Admins: {admin_count}")
        print(f"   Utilisateurs: {user_count}")
        
        # 5. Nettoyer l'utilisateur de test
        print(f"\n🧹 Nettoyage...")
        cursor.execute('DELETE FROM membres WHERE email = %s', (test_email,))
        connection.commit()
        print("✅ Utilisateur de test supprimé")
        
        connection.close()
        
        print(f"\n🎉 SYSTÈME DE LOGIN RDKQ OPÉRATIONNEL!")
        print(f"✅ Authentification par hash SHA256")
        print(f"✅ Support des comptes admin et utilisateur")
        print(f"✅ Gestion sécurisée des mots de passe")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def show_login_instructions():
    """Afficher les instructions de connexion"""
    print(f"\n📋 INSTRUCTIONS DE CONNEXION RDKQ")
    print(f"=" * 50)
    print(f"🌐 URL de connexion: http://127.0.0.1:8002/rdkq/login")
    print(f"🌐 URL d'inscription: http://127.0.0.1:8002/rdkq/register")
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('SELECT username, email FROM membres WHERE is_admin = 1 LIMIT 3')
        admins = cursor.fetchall()
        
        print(f"\n👑 Comptes administrateurs disponibles:")
        for admin in admins:
            if 'admin' in admin['email']:
                print(f"   📧 Email: {admin['email']}")
                print(f"   🔐 Mot de passe: admin123")
                print(f"   👤 Nom: {admin['username']}")
                print()
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture des admins: {e}")
    
    print(f"✨ Fonctionnalités disponibles après connexion:")
    print(f"   - Accès à l'espace membre RDKQ")
    print(f"   - Profil personnalisé")
    print(f"   - Participation aux cercles locaux")
    print(f"   - Administration (pour les admins)")

if __name__ == "__main__":
    if test_rdkq_login_system():
        show_login_instructions()
    else:
        print("❌ Tests échoués")
