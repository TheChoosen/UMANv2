#!/usr/bin/env python3
"""
Script de test pour vérifier le nouveau système d'authentification BIQ
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8002"
LOGIN_URL = f"{BASE_URL}/biq/login"
PROFILE_URL = f"{BASE_URL}/biq/profile"

def test_login(email, password):
    """Tester la connexion avec email et mot de passe"""
    print(f"\n=== Test de connexion pour {email} ===")
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    
    # D'abord, récupérer la page de login pour obtenir les cookies de session
    print("1. Accès à la page de login...")
    login_page = session.get(LOGIN_URL)
    print(f"   Status: {login_page.status_code}")
    
    # Tenter la connexion
    print("2. Tentative de connexion...")
    login_data = {
        'email': email,
        'password': password
    }
    
    login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code == 302:
        print(f"   Redirection vers: {login_response.headers.get('Location', 'N/A')}")
        print("   ✅ Connexion réussie!")
        
        # Tester l'accès au profil
        print("3. Test d'accès au profil...")
        profile_response = session.get(PROFILE_URL)
        print(f"   Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            print("   ✅ Accès au profil autorisé!")
        else:
            print("   ❌ Accès au profil refusé")
            
    elif login_response.status_code == 200:
        print("   ❌ Connexion échouée (pas de redirection)")
        if "incorrect" in login_response.text.lower():
            print("   Raison: Email ou mot de passe incorrect")
    else:
        print(f"   ❌ Erreur inattendue: {login_response.status_code}")

def test_invalid_login():
    """Tester avec des identifiants invalides"""
    print("\n=== Test avec identifiants invalides ===")
    test_login("invalid@example.com", "wrongpassword")

if __name__ == "__main__":
    print("🔐 Test du système d'authentification BIQ")
    print("=" * 50)
    
    # Test avec l'utilisateur de test créé
    print("Test avec l'utilisateur de test:")
    test_login("test@biq.com", "test123")
    
    # Test avec les utilisateurs migrés (utiliser les mots de passe temporaires)
    print("\nTest avec les utilisateurs migrés:")
    test_login("admin@biq.quebec", "temp_4GVSzRPlpxQ")
    test_login("membre@biq.quebec", "temp_P4OwJjZ97fI")
    
    # Test avec des identifiants invalides
    test_invalid_login()
    
    print("\n" + "=" * 50)
    print("Tests terminés!")
