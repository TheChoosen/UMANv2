#!/usr/bin/env python3
"""
Script pour fusionner la table 'users' dans 'membres'
- Ajoute les colonnes manquantes à la table membres
- Migre les données de users vers membres  
- Supprime la table users après migration
"""

import mysql.connector
from mysql.connector import Error
from config_mysql import MYSQL_CONFIG

def migrate_users_to_membres():
    """Migrer la table users vers membres"""
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("🔄 Début de la migration users → membres")
        print("-" * 50)
        
        # 1. Ajouter les colonnes manquantes à la table membres
        print("📝 Ajout des colonnes manquantes à la table membres...")
        
        # Colonnes de users qui n'existent pas dans membres
        columns_to_add = [
            "ADD COLUMN username VARCHAR(80) UNIQUE AFTER email",
            "ADD COLUMN password VARCHAR(120) AFTER username", 
            "ADD COLUMN is_admin TINYINT(1) DEFAULT 0 AFTER password",
            "ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER is_admin"
        ]
        
        for column_sql in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE membres {column_sql}")
                print(f"✅ Colonne ajoutée: {column_sql.split()[2]}")
            except Error as e:
                if "Duplicate column name" in str(e):
                    print(f"⚠️  Colonne déjà existante: {column_sql.split()[2]}")
                else:
                    print(f"❌ Erreur pour {column_sql}: {e}")
        
        # 2. Vérifier les données existantes
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM membres")
        membres_count = cursor.fetchone()['count']
        
        print(f"\n📊 État initial:")
        print(f"   Users: {users_count} enregistrements")
        print(f"   Membres: {membres_count} enregistrements")
        
        # 3. Migrer les données de users vers membres
        print(f"\n🔄 Migration des données...")
        
        # Récupérer tous les users
        cursor.execute("SELECT * FROM users")
        users_data = cursor.fetchall()
        
        migrated_count = 0
        updated_count = 0
        
        for user in users_data:
            # Vérifier si un membre avec le même email existe déjà
            cursor.execute("SELECT id FROM membres WHERE email = %s", (user['email'],))
            existing_membre = cursor.fetchone()
            
            if existing_membre:
                # Mettre à jour le membre existant avec les données de users
                cursor.execute("""
                    UPDATE membres 
                    SET username = %s, password = %s, is_admin = %s, created_at = %s
                    WHERE email = %s
                """, (user['username'], user['password'], user['is_admin'], 
                     user['created_at'], user['email']))
                updated_count += 1
                print(f"🔄 Mis à jour: {user['username']} ({user['email']})")
            else:
                # Créer un nouveau membre avec les données de users
                cursor.execute("""
                    INSERT INTO membres (email, username, password, is_admin, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user['email'], user['username'], user['password'], 
                     user['is_admin'], user['created_at']))
                migrated_count += 1
                print(f"➕ Créé: {user['username']} ({user['email']})")
        
        connection.commit()
        
        # 4. Vérifier le résultat final
        cursor.execute("SELECT COUNT(*) as count FROM membres")
        final_membres_count = cursor.fetchone()['count']
        
        print(f"\n📈 Résultats de la migration:")
        print(f"   {migrated_count} nouveaux membres créés")
        print(f"   {updated_count} membres existants mis à jour")
        print(f"   Total final dans membres: {final_membres_count}")
        
        # 5. Optionnel: Supprimer la table users (avec confirmation)
        print(f"\n⚠️  Table users prête à être supprimée")
        print(f"   Vous pouvez la supprimer manuellement si tout fonctionne bien")
        
        return True
        
    except Error as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def verify_migration():
    """Vérifier que la migration s'est bien passée"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("\n🔍 Vérification de la migration:")
        print("-" * 40)
        
        # Structure de la table membres
        cursor.execute("DESCRIBE membres")
        columns = cursor.fetchall()
        print("📋 Colonnes dans la table membres:")
        for col in columns:
            print(f"   - {col['Field']} ({col['Type']})")
        
        # Données des administrateurs
        cursor.execute("SELECT username, email, is_admin FROM membres WHERE is_admin = 1")
        admins = cursor.fetchall()
        print(f"\n👑 Administrateurs ({len(admins)}):")
        for admin in admins:
            print(f"   - {admin['username']} ({admin['email']})")
        
        # Total des membres
        cursor.execute("SELECT COUNT(*) as count FROM membres")
        total = cursor.fetchone()['count']
        print(f"\n📊 Total des membres: {total}")
        
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Migration users → membres")
    print(f"📍 Serveur: {MYSQL_CONFIG['host']}")
    print(f"📂 Base: {MYSQL_CONFIG['database']}")
    print("=" * 60)
    
    # Exécuter la migration
    if migrate_users_to_membres():
        verify_migration()
        print("\n🎉 Migration terminée avec succès!")
        print("\n📋 Prochaines étapes:")
        print("   1. Tester l'application avec la table membres")
        print("   2. Modifier le code pour utiliser 'membres' au lieu de 'users'") 
        print("   3. Supprimer la table users si tout fonctionne")
    else:
        print("\n❌ Migration échouée")
