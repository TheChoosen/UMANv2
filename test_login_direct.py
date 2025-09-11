#!/usr/bin/env python3
"""
Test simple pour vérifier notre route /login
"""

import os
import sys
sys.path.insert(0, '/home/amenard/UMANv2/UMANv2')

# Configurer l'environnement
os.environ['VALID_SECURITY_CODES'] = '12345,54321,11111'
os.environ['SECRET_KEY'] = 'test-secret-key'

from app import app, get_mysql_db
from datetime import datetime, timezone

def test_login_route():
    """Test de la route login directement"""
    with app.test_client() as client:
        # Test avec données valides
        print("Testing valid login...")
        
        response = client.post('/login', data={
            'email': 'test@example.com',
            'security_code': '12345'
        }, headers={
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_data(as_text=True)}")
        
        # Test avec code invalide
        print("\nTesting invalid code...")
        response = client.post('/login', data={
            'email': 'test2@example.com',
            'security_code': '99999'
        }, headers={
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_data(as_text=True)}")

def test_db_connection():
    """Test de la connexion à la base de données"""
    try:
        with app.app_context():  # Utiliser le contexte d'application
            db = get_mysql_db()
            if db:
                print("✅ Connexion MySQL réussie")
                # Test simple query
                cur = db.cursor()
                cur.execute('SELECT VERSION()')
                version = cur.fetchone()
                print(f"Version MySQL: {version[0]}")
                return True
            else:
                print("❌ Connexion MySQL échouée")
                return False
    except Exception as e:
        print(f"❌ Erreur MySQL: {e}")
        return False

if __name__ == "__main__":
    print("=== Test de la fonctionnalité de connexion automatique ===")
    
    # Test de la DB
    print("1. Test de la base de données...")
    if not test_db_connection():
        print("Arrêt des tests - problème avec la DB")
        sys.exit(1)
    
    print("\n2. Test des routes...")
    try:
        test_login_route()
    except Exception as e:
        print(f"Erreur dans les tests: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Tests terminés ===")
