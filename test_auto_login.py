#!/usr/bin/env python3
"""
Script de test pour le système de création automatique de compte
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://127.0.0.1:8002"
LOGIN_URL = f"{BASE_URL}/login"

def test_login_new_user():
    """Test de création d'un nouveau compte"""
    print("=== Test: Création d'un nouveau compte ===")
    
    data = {
        'email': 'test.nouveau@example.com',
        'security_code': '12345'
    }
    
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(LOGIN_URL, data=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Nouveau compte créé avec succès!")
        else:
            print("❌ Échec de la création de compte")
    else:
        print("❌ Erreur HTTP")
    
    print()

def test_login_existing_user():
    """Test de connexion avec un utilisateur existant"""
    print("=== Test: Connexion utilisateur existant ===")
    
    data = {
        'email': 'test.nouveau@example.com',
        'security_code': '12345'
    }
    
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(LOGIN_URL, data=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Connexion existante réussie!")
        else:
            print("❌ Échec de la connexion")
    else:
        print("❌ Erreur HTTP")
    
    print()

def test_invalid_code():
    """Test avec code de sécurité invalide"""
    print("=== Test: Code de sécurité invalide ===")
    
    data = {
        'email': 'test@example.com',
        'security_code': '99999'  # Code invalide
    }
    
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(LOGIN_URL, data=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        result = response.json()
        if not result.get('success') and 'invalide' in result.get('message', ''):
            print("✅ Code invalide correctement rejeté!")
        else:
            print("❌ Réponse inattendue")
    else:
        print("❌ Code attendu 401")
    
    print()

def test_invalid_input():
    """Test avec entrées invalides"""
    print("=== Test: Entrées invalides ===")
    
    # Test sans email
    data = {
        'security_code': '12345'
    }
    
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(LOGIN_URL, data=data, headers=headers)
    print(f"Test sans email - Status: {response.status_code}")
    
    # Test avec code de mauvaise longueur
    data = {
        'email': 'test@example.com',
        'security_code': '123'
    }
    
    response = requests.post(LOGIN_URL, data=data, headers=headers)
    print(f"Test code court - Status: {response.status_code}")
    
    # Test avec code non-numérique
    data = {
        'email': 'test@example.com',
        'security_code': 'abcde'
    }
    
    response = requests.post(LOGIN_URL, data=data, headers=headers)
    print(f"Test code non-numérique - Status: {response.status_code}")
    
    print("✅ Tests de validation terminés")
    print()

def main():
    """Exécuter tous les tests"""
    print("🚀 Démarrage des tests du système de connexion automatique")
    print("=" * 60)
    
    try:
        # Vérifier que le serveur est accessible
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Serveur accessible (Status: {response.status_code})")
        print()
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible d'accéder au serveur: {e}")
        print("Assurez-vous que le serveur Flask est démarré sur http://127.0.0.1:8002")
        return
    
    # Exécuter les tests
    test_invalid_input()
    test_invalid_code()
    test_login_new_user()
    test_login_existing_user()
    
    print("=" * 60)
    print("🎯 Tests terminés!")

if __name__ == "__main__":
    main()
