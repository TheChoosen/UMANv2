#!/usr/bin/env python3
"""
Script de test pour vérifier la migration MySQL
"""

import sys
import traceback
from config_mysql import MYSQL_CONFIG
import mysql.connector
from mysql.connector import Error

def test_mysql_connection():
    """Test 1: Connexion MySQL de base"""
    try:
        print("🔍 Test 1: Connexion MySQL...")
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        print(f"✅ Connexion réussie à {MYSQL_CONFIG['host']}")
        connection.close()
        return True
    except Error as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_tables_exist():
    """Test 2: Vérifier que toutes les tables existent"""
    try:
        print("🔍 Test 2: Vérification des tables...")
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        expected_tables = ['users', 'submissions', 'cercles']
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        for table in expected_tables:
            if table in existing_tables:
                print(f"✅ Table '{table}' trouvée")
            else:
                print(f"❌ Table '{table}' manquante")
                return False
        
        connection.close()
        return True
    except Error as e:
        print(f"❌ Erreur lors de la vérification des tables: {e}")
        return False

def test_admin_user():
    """Test 3: Vérifier que l'admin existe"""
    try:
        print("🔍 Test 3: Vérification de l'admin...")
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE is_admin = 1")
        admin_users = cursor.fetchall()
        
        if admin_users:
            for admin in admin_users:
                print(f"✅ Admin trouvé: {admin['username']} ({admin['email']})")
        else:
            print("❌ Aucun administrateur trouvé")
            return False
        
        connection.close()
        return True
    except Error as e:
        print(f"❌ Erreur lors de la vérification admin: {e}")
        return False

def test_app_import():
    """Test 4: Import de l'application Flask"""
    try:
        print("🔍 Test 4: Import de l'application Flask...")
        from app import app
        print("✅ Application Flask importée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'import de l'app: {e}")
        traceback.print_exc()
        return False

def test_config_mysql_import():
    """Test 5: Import de la configuration MySQL"""
    try:
        print("🔍 Test 5: Import de la configuration MySQL...")
        from config_mysql import get_mysql_db, close_mysql_db
        print("✅ Configuration MySQL importée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'import de config_mysql: {e}")
        return False

def test_user_operations():
    """Test 6: Opérations CRUD sur les utilisateurs"""
    try:
        print("🔍 Test 6: Test des opérations utilisateurs...")
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Compter les utilisateurs
        cursor.execute("SELECT COUNT(*) as count FROM users")
        count = cursor.fetchone()['count']
        print(f"✅ {count} utilisateurs dans la base")
        
        # Tester une requête de sélection
        cursor.execute("SELECT username, email, is_admin FROM users LIMIT 3")
        users = cursor.fetchall()
        
        for user in users:
            status = "Admin" if user['is_admin'] else "Utilisateur"
            print(f"✅ {status}: {user['username']} ({user['email']})")
        
        connection.close()
        return True
    except Error as e:
        print(f"❌ Erreur lors des opérations utilisateurs: {e}")
        return False

def run_all_tests():
    """Exécuter tous les tests"""
    print("🚀 Début des tests de migration MySQL")
    print("=" * 60)
    
    tests = [
        test_mysql_connection,
        test_tables_exist,
        test_admin_user,
        test_config_mysql_import,
        test_app_import,
        test_user_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSÉ\n")
            else:
                print("❌ ÉCHEC\n")
        except Exception as e:
            print(f"❌ ERREUR: {e}\n")
    
    print("=" * 60)
    print(f"📊 Résultats: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Migration MySQL réussie!")
        print("\n📋 Prochaines étapes:")
        print("   1. Tester la connexion admin via http://127.0.0.1:8002/login")
        print("   2. Vérifier le fonctionnement des domaines:")
        print("      - uman-api.com → Page principale")
        print("      - peupleun.live → Page RDKQ")
        print("   3. Tester les fonctionnalités admin")
        return True
    else:
        print("❌ Certains tests ont échoué. Vérifiez la configuration.")
        return False

if __name__ == "__main__":
    print(f"🔧 Configuration MySQL:")
    print(f"   Serveur: {MYSQL_CONFIG['host']}")
    print(f"   Base: {MYSQL_CONFIG['database']}")
    print(f"   Utilisateur: {MYSQL_CONFIG['user']}")
    print()
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
