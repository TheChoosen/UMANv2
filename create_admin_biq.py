#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur BIQ pour tester
"""

import mysql.connector
from mysql.connector import Error
from config_mysql import MYSQL_CONFIG
import hashlib

def create_admin_biq():
    """Créer un administrateur BIQ pour tester"""
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("👤 Création d'un administrateur BIQ...")
        
        # Vérifier si un admin existe déjà
        cursor.execute("SELECT * FROM membres WHERE email = %s", ('admin@biq.quebec',))
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            print("⚠️  Un administrateur BIQ existe déjà avec cet email")
            print(f"   ID: {existing_admin['id']}")
            print(f"   Email: {existing_admin['email']}")
            print(f"   Username: {existing_admin['username']}")
            return True
        
        # Créer l'administrateur
        admin_data = {
            'nom': 'Administrateur BIQ',
            'email': 'admin@biq.quebec',
            'username': 'admin_biq',
            'password': 'activated',  # Compte déjà activé
            'cercle_local': 'Administration',
            'is_admin': 1
        }
        
        cursor.execute("""
            INSERT INTO membres (nom, email, username, password, cercle_local, is_admin, created_at)
            VALUES (%(nom)s, %(email)s, %(username)s, %(password)s, %(cercle_local)s, %(is_admin)s, NOW())
        """, admin_data)
        
        connection.commit()
        admin_id = cursor.lastrowid
        
        print("✅ Administrateur BIQ créé avec succès!")
        print(f"   ID: {admin_id}")
        print(f"   Email: {admin_data['email']}")
        print(f"   Username: {admin_data['username']}")
        print(f"   Nom: {admin_data['nom']}")
        
        # Créer également un membre normal pour tester
        print("\n👤 Création d'un membre test...")
        
        cursor.execute("SELECT * FROM membres WHERE email = %s", ('membre@biq.quebec',))
        existing_member = cursor.fetchone()
        
        if not existing_member:
            member_data = {
                'nom': 'Citoyen Test',
                'email': 'membre@biq.quebec',
                'username': 'membre_test',
                'password': 'activated',
                'cercle_local': 'Montréal',
                'is_admin': 0
            }
            
            cursor.execute("""
                INSERT INTO membres (nom, email, username, password, cercle_local, is_admin, created_at)
                VALUES (%(nom)s, %(email)s, %(username)s, %(password)s, %(cercle_local)s, %(is_admin)s, NOW())
            """, member_data)
            
            connection.commit()
            member_id = cursor.lastrowid
            
            print("✅ Membre test créé avec succès!")
            print(f"   ID: {member_id}")
            print(f"   Email: {member_data['email']}")
            print(f"   Username: {member_data['username']}")
        else:
            print("⚠️  Un membre test existe déjà")
        
        # Afficher les statistiques
        cursor.execute("SELECT COUNT(*) as count FROM membres")
        total_membres = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM membres WHERE is_admin = 1")
        total_admins = cursor.fetchone()['count']
        
        print(f"\n📊 Statistiques:")
        print(f"   Total membres: {total_membres}")
        print(f"   Administrateurs: {total_admins}")
        
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Création d'un administrateur BIQ")
    print(f"📍 Serveur: {MYSQL_CONFIG['host']}")
    print(f"📂 Base: {MYSQL_CONFIG['database']}")
    print("-" * 50)
    
    if create_admin_biq():
        print(f"\n🎉 Utilisateurs créés avec succès!")
        print(f"")
        print(f"🔑 Connexions de test:")
        print(f"   Admin: admin@biq.quebec")
        print(f"   Membre: membre@biq.quebec")
        print(f"   (Mot de passe: les comptes sont déjà activés)")
    else:
        print(f"\n❌ Échec de la création")
