#!/usr/bin/env python3
"""
Test de l'API JSON pour la connexion automatique
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8003"  # Utilisons un port différent pour tester
LOGIN_URL = f"{BASE_URL}/login"

def start_test_server():
    """Démarre un serveur de test"""
    import os
    import sys
    sys.path.insert(0, '/home/amenard/UMANv2/UMANv2')
    
    # Configuration
    os.environ['VALID_SECURITY_CODES'] = '12345,54321,11111'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    
    from app import app
    
    print("🚀 Démarrage du serveur de test sur le port 8003...")
    app.run(debug=False, port=8003, host='127.0.0.1')

def test_api():
    """Test des appels API"""
    
    # Test 1: Créer un nouveau compte
    print("=== Test 1: Création de nouveau compte ===")
    data = {
        'email': 'nouveau.test@example.com',
        'security_code': '12345'
    }
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(LOGIN_URL, data=data, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text[:200]}...")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"JSON Response: {json.dumps(result, indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête: {e}")
    
    # Test 2: Code invalide
    print("\n=== Test 2: Code invalide ===")
    data = {
        'email': 'test.invalide@example.com',
        'security_code': '99999'
    }
    
    try:
        response = requests.post(LOGIN_URL, data=data, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Content: {response.text[:200]}...")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"JSON Response: {json.dumps(result, indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        start_test_server()
    else:
        print("🧪 Test de l'API de connexion automatique")
        print("Assurez-vous que le serveur tourne sur le port 8003")
        print("Pour démarrer le serveur: python3 test_api.py server")
        print()
        test_api()
