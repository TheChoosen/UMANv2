#!/usr/bin/env python3
"""
Test spécifique pour les nouvelles fonctionnalités de création et édition de médias
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8002"
TEST_CREDENTIALS = {
    "email": "admin@peupleun.live",
    "password": "admin123"
}

def login():
    """Connexion administrateur"""
    session = requests.Session()
    
    # Page de login
    login_page = session.get(f"{BASE_URL}/rdkq/login")
    if login_page.status_code != 200:
        return None
    
    # Connexion
    login_data = {
        "email": TEST_CREDENTIALS["email"],
        "password": TEST_CREDENTIALS["password"]
    }
    
    response = session.post(f"{BASE_URL}/rdkq/login", data=login_data, allow_redirects=False)
    
    if response.status_code == 302:
        return session
    return None

def test_new_media_page(session):
    """Test d'accès à la page de création"""
    print("=== Test page de création ===")
    
    response = session.get(f"{BASE_URL}/rdkq/admin/mediatheque/new")
    
    if response.status_code == 200:
        if "Ajouter un Nouveau Média" in response.text:
            print("✅ Page de création accessible et contenu correct")
            return True
        else:
            print("❌ Page accessible mais contenu incorrect")
            return False
    else:
        print(f"❌ Erreur d'accès à la page de création ({response.status_code})")
        return False

def test_create_media(session):
    """Test de création d'un nouveau média"""
    print("\n=== Test création d'un média ===")
    
    new_media_data = {
        "title": "Test Média Automatisé",
        "description": "Média créé automatiquement par les tests",
        "category": "test",
        "author": "Test Bot",
        "image_url": "https://via.placeholder.com/300x200",
        "document_url": "https://example.com/document.pdf",
        "is_public": True,
        "is_featured": False
    }
    
    response = session.post(
        f"{BASE_URL}/rdkq/admin/mediatheque/new",
        json=new_media_data
    )
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('ok'):
                print("✅ Média créé avec succès")
                return True
            else:
                print(f"❌ Erreur lors de la création: {result.get('error')}")
                return False
        except json.JSONDecodeError:
            print("❌ Réponse JSON invalide")
            return False
    else:
        print(f"❌ Erreur HTTP lors de la création ({response.status_code})")
        return False

def test_edit_media_page(session):
    """Test d'accès à la page d'édition"""
    print("\n=== Test page d'édition ===")
    
    # D'abord récupérer un média existant
    response = session.get(f"{BASE_URL}/rdkq/admin/mediatheque/data")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('ok') and data.get('media'):
                media_id = data['media'][0]['id']
                
                # Tester l'accès à la page d'édition
                edit_response = session.get(f"{BASE_URL}/rdkq/admin/mediatheque/{media_id}/edit")
                
                if edit_response.status_code == 200:
                    if "Modifier le Média" in edit_response.text:
                        print(f"✅ Page d'édition accessible pour média ID {media_id}")
                        return True, media_id
                    else:
                        print("❌ Page accessible mais contenu incorrect")
                        return False, None
                else:
                    print(f"❌ Erreur d'accès à la page d'édition ({edit_response.status_code})")
                    return False, None
            else:
                print("❌ Aucun média disponible pour tester l'édition")
                return False, None
        except json.JSONDecodeError:
            print("❌ Erreur de parsing JSON")
            return False, None
    else:
        print(f"❌ Impossible de récupérer les médias ({response.status_code})")
        return False, None

def test_edit_media(session, media_id):
    """Test de modification d'un média"""
    print(f"\n=== Test modification du média ID {media_id} ===")
    
    updated_data = {
        "title": "Média Modifié par Test",
        "description": "Description mise à jour automatiquement",
        "category": "test-modifie",
        "author": "Test Bot Updater",
        "image_url": "https://via.placeholder.com/400x300",
        "document_url": "https://example.com/updated-document.pdf",
        "is_public": False,  # Changer la visibilité
        "is_featured": True  # Mettre en vedette
    }
    
    response = session.post(
        f"{BASE_URL}/rdkq/admin/mediatheque/{media_id}/edit",
        json=updated_data
    )
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('ok'):
                print("✅ Média modifié avec succès")
                return True
            else:
                print(f"❌ Erreur lors de la modification: {result.get('error')}")
                return False
        except json.JSONDecodeError:
            print("❌ Réponse JSON invalide")
            return False
    else:
        print(f"❌ Erreur HTTP lors de la modification ({response.status_code})")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test des fonctionnalités de création et édition - RDKQ")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Connexion
    session = login()
    if not session:
        print("❌ ÉCHEC: Impossible de se connecter")
        sys.exit(1)
    
    print("✅ Connexion réussie")
    
    # Tests
    tests = []
    
    # Test page de création
    tests.append(("Page de création", test_new_media_page(session)))
    
    # Test création de média
    tests.append(("Création de média", test_create_media(session)))
    
    # Test page d'édition
    edit_page_result, media_id = test_edit_media_page(session)
    tests.append(("Page d'édition", edit_page_result))
    
    # Test modification de média
    if edit_page_result and media_id:
        tests.append(("Modification de média", test_edit_media(session, media_id)))
    else:
        tests.append(("Modification de média", False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status:<12} {test_name}")
    
    print("-" * 60)
    print(f"🎯 Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TOUS LES TESTS DE CRÉATION/ÉDITION SONT PASSÉS !")
        sys.exit(0)
    else:
        print("⚠️  Certains tests ont échoué.")
        sys.exit(1)

if __name__ == "__main__":
    main()
