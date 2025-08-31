#!/usr/bin/env python3
"""
Script de migration des mots de passe vers le nouveau système de hachage sécurisé.
Ce script met à jour les anciens mots de passe "activated" vers un système de hachage robuste.
"""

import hashlib
import secrets
import mysql.connector

# Configuration MySQL directe
MYSQL_CONFIG = {
    'host': '192.168.50.101',
    'user': 'gsicloud',
    'password': 'TCOChoosenOne204$',
    'database': 'peupleun',
    'charset': 'utf8mb4'
}

def get_mysql_connection():
    """Obtenir une connexion MySQL directe"""
    return mysql.connector.connect(**MYSQL_CONFIG)

def hash_password(password: str) -> str:
    """Hacher un mot de passe avec sel et pbkdf2"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2:sha256:100000${salt}${password_hash.hex()}"

def migrate_passwords():
    """Migrer les anciens mots de passe vers le nouveau système"""
    print("Démarrage de la migration des mots de passe...")
    
    try:
        db = get_mysql_connection()
        cur = db.cursor(dictionary=True)
        
        # Chercher tous les utilisateurs avec le mot de passe "activated"
        cur.execute('SELECT id, email, username FROM membres WHERE password = %s', ('activated',))
        users_to_migrate = cur.fetchall()
        
        print(f"Trouvé {len(users_to_migrate)} utilisateurs à migrer...")
        
        for user in users_to_migrate:
            # Créer un mot de passe temporaire sécurisé
            temp_password = f"temp_{secrets.token_urlsafe(8)}"
            hashed_password = hash_password(temp_password)
            
            # Mettre à jour le mot de passe dans la base
            cur.execute('UPDATE membres SET password = %s WHERE id = %s', 
                       (hashed_password, user['id']))
            
            print(f"Migré utilisateur {user['email']} (ID: {user['id']})")
            print(f"  Nouveau mot de passe temporaire: {temp_password}")
        
        db.commit()
        print(f"\nMigration terminée avec succès!")
        print(f"IMPORTANT: Les utilisateurs devront réinitialiser leurs mots de passe.")
        print(f"Les mots de passe temporaires sont affichés ci-dessus.")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        if 'db' in locals():
            db.rollback()

def create_test_user():
    """Créer un utilisateur de test avec le nouveau système"""
    print("\nCréation d'un utilisateur de test...")
    
    try:
        db = get_mysql_connection()
        cur = db.cursor(dictionary=True)
        
        # Vérifier si l'utilisateur test existe déjà
        cur.execute('SELECT id FROM membres WHERE email = %s', ('test@biq.com',))
        if cur.fetchone():
            print("L'utilisateur test existe déjà.")
            return
        
        # Créer un utilisateur test
        test_password = "test123"
        hashed_password = hash_password(test_password)
        
        cur.execute('''INSERT INTO membres (username, email, password, nom, created_at)
                       VALUES (%s, %s, %s, %s, NOW())''', 
                   ('testuser', 'test@biq.com', hashed_password, 'Utilisateur Test'))
        
        db.commit()
        
        print(f"Utilisateur de test créé:")
        print(f"  Email: test@biq.com")
        print(f"  Mot de passe: {test_password}")
        
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur test: {e}")

if __name__ == "__main__":
    print("=== Migration des mots de passe BIQ ===")
    print("Ce script va migrer les anciens mots de passe vers un système sécurisé.")
    
    choice = input("Voulez-vous continuer? (oui/non): ")
    if choice.lower() in ['oui', 'o', 'yes', 'y']:
        migrate_passwords()
        create_test_user()
    else:
        print("Migration annulée.")
