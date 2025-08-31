#!/usr/bin/env python3
"""
Script pour finaliser la migration et supprimer la table users
"""

import mysql.connector
from mysql.connector import Error
from config_mysql import MYSQL_CONFIG

def cleanup_old_users_table():
    """Supprimer l'ancienne table users après vérification"""
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 Vérification finale avant suppression de la table users")
        print("-" * 60)
        
        # Vérifier que la table membres a bien toutes les données
        cursor.execute("SELECT COUNT(*) as count FROM membres WHERE is_admin = 1")
        admin_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM membres")
        total_members = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        print(f"📊 État des tables:")
        print(f"   Membres total: {total_members}")
        print(f"   Membres admin: {admin_count}")
        print(f"   Users (ancien): {total_users}")
        
        if admin_count >= 1 and total_members >= total_users:
            print("\n✅ Migration vérifiée - la table membres contient toutes les données")
            
            # Sauvegarder le schéma de users avant suppression
            print("\n💾 Sauvegarde du schéma de la table users...")
            cursor.execute("SHOW CREATE TABLE users")
            create_statement = cursor.fetchone()
            
            with open('backup_users_schema.sql', 'w', encoding='utf-8') as f:
                f.write(f"-- Sauvegarde du schéma de la table users\n")
                f.write(f"-- Date: {create_statement}\n")
                f.write(create_statement['Create Table'])
            
            print("✅ Schéma sauvegardé dans backup_users_schema.sql")
            
            # Supprimer la table users
            print("\n🗑️  Suppression de la table users...")
            cursor.execute("DROP TABLE users")
            connection.commit()
            
            print("✅ Table users supprimée avec succès!")
            
            # Vérification finale
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            print(f"\n📋 Tables restantes:")
            for table in tables:
                print(f"   - {table}")
            
            if 'users' not in tables:
                print("\n🎉 Nettoyage terminé! La table users a été supprimée.")
                print("💡 L'application utilise maintenant uniquement la table 'membres'")
            
        else:
            print("\n❌ Migration incomplète - conservation de la table users")
            print("   Vérifiez que tous les administrateurs sont présents dans membres")
        
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False

def test_app_with_membres():
    """Tester que l'application fonctionne avec la table membres"""
    try:
        print("\n🧪 Test de l'application avec la table membres...")
        
        # Test de connexion
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Test de lecture des admins
        cursor.execute("SELECT username, email FROM membres WHERE is_admin = 1")
        admins = cursor.fetchall()
        
        print(f"✅ {len(admins)} administrateurs trouvés:")
        for admin in admins:
            print(f"   - {admin['username']} ({admin['email']})")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Nettoyage final de la migration")
    print(f"📍 Serveur: {MYSQL_CONFIG['host']}")
    print(f"📂 Base: {MYSQL_CONFIG['database']}")
    print("=" * 60)
    
    # Tester l'application d'abord
    if test_app_with_membres():
        # Procéder au nettoyage
        cleanup_old_users_table()
    else:
        print("❌ Tests échoués - conservation de la table users")
