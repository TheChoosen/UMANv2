# Script pour créer un premier administrateur dans la base de données

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'uman.db')

def create_admin_user():
    """Créer un utilisateur administrateur par défaut"""
    
    print("Création des administrateurs par défaut...")
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    print(f"Base de données: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Créer les tables si elles n'existent pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prenom TEXT,
            nom TEXT,
            email TEXT UNIQUE,
            organisation TEXT,
            telephone TEXT,
            code_hash TEXT,
            code_expires TIMESTAMP,
            active INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP
        )
    ''')
    
    # Ajouter la colonne is_admin si elle n'existe pas
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
        print("Colonne is_admin ajoutée")
    except Exception as e:
        print("Colonne is_admin existe déjà")
    
    # Créer un admin par défaut
    admin_email = "admin@uman-api.com"
    now = datetime.now(timezone.utc).isoformat()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (prenom, nom, email, organisation, telephone, active, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?, 1, 1, ?)
        ''', ("Admin", "UMan", admin_email, "UMan API", "", now))
        
        # Créer un admin pour peupleun.live aussi
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (prenom, nom, email, organisation, telephone, active, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?, 1, 1, ?)
        ''', ("Admin", "Peuple", "admin@peupleun.live", "République du Kwébec", "", now))
        
        conn.commit()
        print("✅ Administrateurs créés:")
        print(f"   - {admin_email}")
        print(f"   - admin@peupleun.live")
        print("   Ils peuvent se connecter via /login")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user()
