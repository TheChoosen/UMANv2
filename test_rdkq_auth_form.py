#!/usr/bin/env python3
"""
Script pour tester le formulaire avec authentification
"""

import requests
import json
from urllib.parse import urljoin

class RDKQTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8002"
        self.session = requests.Session()
        
    def test_login_and_form(self):
        """Test complet avec login et soumission de formulaire"""
        print("🧪 Test complet RDKQ avec authentification")
        print("=" * 50)
        
        # Étape 1: Test de connexion sans auth
        print("1. Test d'accès au formulaire sans authentification...")
        form_url = urljoin(self.base_url, "/rdkq/admin/mediatheque/new")
        response = self.session.get(form_url, allow_redirects=False)
        
        if response.status_code == 302:
            print("✅ Redirection vers login (normal)")
            print(f"   Redirection vers: {response.headers.get('Location', 'Non spécifié')}")
        else:
            print(f"❌ Status inattendu: {response.status_code}")
        
        # Étape 2: Accès à la page de login
        print("\n2. Test d'accès à la page de login...")
        login_url = urljoin(self.base_url, "/rdkq/login")
        response = self.session.get(login_url)
        
        if response.status_code == 200:
            print("✅ Page de login accessible")
        else:
            print(f"❌ Erreur page login: {response.status_code}")
            return
        
        # Étape 3: Tentative de login (nous n'avons peut-être pas de compte)
        print("\n3. Test des comptes existants...")
        try:
            # Essayer de créer un compte admin temporaire
            self.create_test_admin()
            
            # Tentative de login
            login_data = {
                'email': 'admin@test.rdkq',
                'password': 'testpass123'
            }
            
            response = self.session.post(login_url, data=login_data, allow_redirects=False)
            print(f"   Status login: {response.status_code}")
            
            if response.status_code == 302:
                print("✅ Login réussi (redirection)")
                
                # Étape 4: Test du formulaire après login
                print("\n4. Test du formulaire après authentification...")
                response = self.session.get(form_url)
                
                if response.status_code == 200:
                    print("✅ Formulaire accessible après login")
                    
                    # Étape 5: Test de soumission
                    print("\n5. Test de soumission du formulaire...")
                    self.test_form_submission()
                    
                else:
                    print(f"❌ Erreur formulaire après login: {response.status_code}")
            else:
                print("❌ Échec du login")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
    
    def create_test_admin(self):
        """Créer un compte admin de test"""
        print("   Création d'un compte admin de test...")
        
        # Utiliser l'API directe si disponible
        register_url = urljoin(self.base_url, "/rdkq/register")
        
        register_data = {
            'username': 'admin_test',
            'email': 'admin@test.rdkq',
            'password': 'testpass123'
        }
        
        response = self.session.post(register_url, data=register_data)
        print(f"   Création compte: {response.status_code}")
    
    def test_form_submission(self):
        """Test de soumission du formulaire"""
        submit_url = urljoin(self.base_url, "/rdkq/admin/mediatheque/new")
        
        test_data = {
            "title": "Test Média JS",
            "description": "Test avec JavaScript amélioré",
            "category": "formation",
            "author": "Auto-Test",
            "image_url": "/static/RepubliqueduKwebec/Photo/PLAQUE/Plaque Sublimation GN SQ.png",
            "document_url": "",
            "is_public": True,
            "is_featured": False
        }
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        response = self.session.post(submit_url, 
                                   headers=headers, 
                                   data=json.dumps(test_data))
        
        print(f"   Status soumission: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Résultat: {result}")
                
                if result.get('ok'):
                    print("✅ Média créé avec succès!")
                else:
                    print(f"❌ Erreur: {result.get('error')}")
                    
            except json.JSONDecodeError:
                print(f"   Response text: {response.text[:200]}...")
        else:
            print(f"   Erreur HTTP: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")

if __name__ == "__main__":
    tester = RDKQTester()
    tester.test_login_and_form()
