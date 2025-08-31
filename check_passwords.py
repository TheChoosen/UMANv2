#!/usr/bin/env python3
"""
Script pour vérifier les mots de passe dans la base de données
"""

import mysql.connector

# Configuration MySQL directe
MYSQL_CONFIG = {
    'host': '192.168.50.101',
    'user': 'gsicloud',
    'password': 'TCOChoosenOne204$',
    'database': 'peupleun',
    'charset': 'utf8mb4'
}

def check_passwords():
    """Vérifier les mots de passe dans la base"""
    try:
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cur = db.cursor(dictionary=True)
        
        # Récupérer tous les utilisateurs
        cur.execute('SELECT id, email, username, password FROM membres ORDER BY id')
        users = cur.fetchall()
        
        print("=== État des mots de passe dans la base ===")
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Email: {user['email']}")
            print(f"Username: {user['username']}")
            print(f"Password: {user['password'][:50]}...")
            print("-" * 40)
        
        db.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_passwords()
