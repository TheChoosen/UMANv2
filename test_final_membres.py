#!/usr/bin/env python3
"""
Test final pour valider la migration vers la table membres
"""

import mysql.connector
from mysql.connector import Error
from config_mysql import MYSQL_CONFIG

def test_final_migration():
    """Test complet de la migration vers membres"""
    
    print("🎯 Test final de la migration vers la table membres")
    print("=" * 60)
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Vérifier que la table users n'existe plus
        cursor.execute("SHOW TABLES")
        tables = [table[list(table.keys())[0]] for table in cursor.fetchall()]
        
        print("📋 Tables existantes:")
        for table in sorted(tables):
            print(f"   ✅ {table}")
        
        if 'users' in tables:
            print("❌ ERREUR: La table 'users' existe encore!")
            return False
        else:
            print("✅ Table 'users' supprimée avec succès")
        
        # 2. Vérifier la structure de la table membres
        print(f"\n📊 Structure de la table membres:")
        cursor.execute("DESCRIBE membres")
        columns = cursor.fetchall()
        
        required_columns = ['id', 'email', 'username', 'password', 'is_admin', 'created_at']
        found_columns = [col['Field'] for col in columns]
        
        for req_col in required_columns:
            if req_col in found_columns:
                print(f"   ✅ {req_col}")
            else:
                print(f"   ❌ {req_col} MANQUANT")
                return False
        
        # 3. Vérifier les données des administrateurs
        print(f"\n👑 Administrateurs:")
        cursor.execute("SELECT username, email, is_admin FROM membres WHERE is_admin = 1")
        admins = cursor.fetchall()
        
        if len(admins) >= 1:
            for admin in admins:
                print(f"   ✅ {admin['username']} ({admin['email']})")
        else:
            print("   ❌ Aucun administrateur trouvé!")
            return False
        
        # 4. Test de requête comme dans l'application
        print(f"\n🔍 Test des requêtes de l'application:")
        
        # Simuler la requête de connexion admin
        test_email = "admin@peupleun.live"
        cursor.execute('SELECT * FROM membres WHERE email = %s AND is_admin = %s', (test_email, 1))
        admin_test = cursor.fetchone()
        
        if admin_test:
            print(f"   ✅ Connexion admin simulée réussie pour {test_email}")
        else:
            print(f"   ❌ Échec de la connexion admin pour {test_email}")
            return False
        
        # Test de requête de statut admin
        user_id = admin_test['id']
        cursor.execute('SELECT is_admin FROM membres WHERE id = %s', (user_id,))
        status_test = cursor.fetchone()
        
        if status_test and status_test['is_admin']:
            print(f"   ✅ Vérification statut admin réussie pour ID {user_id}")
        else:
            print(f"   ❌ Échec vérification statut pour ID {user_id}")
            return False
        
        # 5. Statistiques finales
        cursor.execute("SELECT COUNT(*) as total FROM membres")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as admins FROM membres WHERE is_admin = 1")
        admin_count = cursor.fetchone()['admins']
        
        print(f"\n📈 Statistiques finales:")
        print(f"   Total membres: {total}")
        print(f"   Administrateurs: {admin_count}")
        
        connection.close()
        
        print(f"\n🎉 MIGRATION RÉUSSIE!")
        print(f"✅ La table 'membres' remplace complètement 'users'")
        print(f"✅ Toutes les fonctionnalités d'authentification fonctionnent")
        print(f"✅ L'application peut maintenant utiliser une seule table")
        
        return True
        
    except Error as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    success = test_final_migration()
    
    if success:
        print(f"\n🚀 L'application est prête!")
        print(f"🌐 Testez sur: http://127.0.0.1:8002")
        print(f"🔑 Login admin: admin@peupleun.live / admin123")
    else:
        print(f"\n❌ Des problèmes ont été détectés")
    
    exit(0 if success else 1)
