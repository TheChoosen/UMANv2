#!/usr/bin/env python3
"""
Test pour vérifier le formulaire de médias et la soumission
"""

import requests
import json

def test_media_form_submission():
    """Test de soumission du formulaire de médias"""
    base_url = "http://127.0.0.1:8002"
    
    # Données de test pour un nouveau média
    test_data = {
        "title": "Test Média",
        "description": "Description de test",
        "category": "formation",
        "author": "Testeur",
        "image_url": "/static/RepubliqueduKwebec/Photo/PLAQUE/Plaque Sublimation GN SQ.png",
        "document_url": "https://example.com/test.pdf",
        "is_public": True,
        "is_featured": False
    }
    
    print("🧪 Test de soumission du formulaire de médias")
    print("=" * 50)
    
    try:
        # Test 1: Accès à la page du formulaire
        print("1. Test d'accès à la page du formulaire...")
        form_url = f"{base_url}/rdkq/admin/mediatheque/new"
        response = requests.get(form_url)
        
        if response.status_code == 200:
            print("✅ Page du formulaire accessible")
        else:
            print(f"❌ Erreur d'accès à la page: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return
        
        # Test 2: Soumission du formulaire
        print("\n2. Test de soumission du formulaire...")
        submit_url = f"{base_url}/rdkq/admin/mediatheque/new"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        response = requests.post(submit_url, 
                               headers=headers, 
                               data=json.dumps(test_data))
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"   Response JSON: {response_json}")
            
            if response_json.get('ok'):
                print("✅ Média créé avec succès!")
            else:
                print(f"❌ Erreur lors de la création: {response_json.get('error', 'Erreur inconnue')}")
                
        except json.JSONDecodeError:
            print(f"   Response Text: {response.text[:500]}...")
            print("❌ Réponse non-JSON reçue")
        
        # Test 3: Vérification des routes disponibles
        print("\n3. Test des routes RDKQ disponibles...")
        routes_to_test = [
            "/rdkq/admin",
            "/rdkq/admin/mediatheque",
            "/rdkq/admin/mediatheque/data"
        ]
        
        for route in routes_to_test:
            test_url = f"{base_url}{route}"
            try:
                response = requests.get(test_url, timeout=5)
                print(f"   {route}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   {route}: Erreur - {e}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Flask")
        print("   Assurez-vous que l'application Flask est démarrée sur le port 8002")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    test_media_form_submission()
