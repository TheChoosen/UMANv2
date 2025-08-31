#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration MySQL de la médiathèque RDKQ
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8002"
TEST_CREDENTIALS = {
    "email": "admin@peupleun.live",  # Compte admin vérifié
    "password": "admin123"
}

def test_login():
    """Test de connexion administrateur"""
    print("=== Test de connexion administrateur ===")
    
    session = requests.Session()
    
    # Aller à la page de login pour obtenir les cookies de session
    login_page = session.get(f"{BASE_URL}/rdkq/login")
    if login_page.status_code != 200:
        print(f"❌ Erreur: Impossible d'accéder à la page de login ({login_page.status_code})")
        return None
    
    # Tentative de connexion
    login_data = {
        "email": TEST_CREDENTIALS["email"],
        "password": TEST_CREDENTIALS["password"]
    }
    
    response = session.post(f"{BASE_URL}/rdkq/login", data=login_data, allow_redirects=False)
    
    if response.status_code == 302:  # Redirection = succès
        print("✅ Connexion administrateur réussie")
        return session
    else:
        print(f"❌ Échec de la connexion ({response.status_code})")
        print(f"Réponse: {response.text[:200]}...")
        return None

def test_mediatheque_api(session):
    """Test de l'API médiathèque"""
    print("\n=== Test de l'API médiathèque ===")
    
    response = session.get(f"{BASE_URL}/rdkq/mediatheque")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ API médiathèque accessible - {len(data)} éléments trouvés")
            
            if data:
                print("📋 Exemple d'élément:")
                example = data[0]
                print(f"   - ID: {example.get('id')}")
                print(f"   - Titre: {example.get('title')}")
                print(f"   - Catégorie: {example.get('category')}")
                print(f"   - Vues: {example.get('views')}")
                print(f"   - En vedette: {example.get('is_featured')}")
            
            return True
        except json.JSONDecodeError:
            print("❌ Erreur: Réponse JSON invalide")
            return False
    else:
        print(f"❌ Erreur d'accès à l'API ({response.status_code})")
        return False

def test_admin_interface(session):
    """Test de l'interface d'administration"""
    print("\n=== Test de l'interface d'administration ===")
    
    # Test d'accès à la page d'administration
    response = session.get(f"{BASE_URL}/rdkq/admin/mediatheque")
    
    if response.status_code == 200:
        print("✅ Page d'administration accessible")
        
        # Test de l'API de données admin
        data_response = session.get(f"{BASE_URL}/rdkq/admin/mediatheque/data")
        
        if data_response.status_code == 200:
            try:
                admin_data = data_response.json()
                if admin_data.get('ok'):
                    stats = admin_data.get('stats', {})
                    media_count = len(admin_data.get('media', []))
                    
                    print("✅ API d'administration fonctionnelle")
                    print(f"📊 Statistiques:")
                    print(f"   - Total médias: {stats.get('total', 0)}")
                    print(f"   - Médias publics: {stats.get('public', 0)}")
                    print(f"   - Médias en vedette: {stats.get('featured', 0)}")
                    print(f"   - Vues totales: {stats.get('total_views', 0)}")
                    
                    return True
                else:
                    print(f"❌ Erreur API admin: {admin_data.get('error')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Erreur: Réponse JSON invalide pour l'API admin")
                return False
        else:
            print(f"❌ Erreur d'accès à l'API admin ({data_response.status_code})")
            return False
    else:
        print(f"❌ Erreur d'accès à l'administration ({response.status_code})")
        return False

def test_view_counter(session):
    """Test du compteur de vues"""
    print("\n=== Test du compteur de vues ===")
    
    # D'abord récupérer un média existant
    response = session.get(f"{BASE_URL}/rdkq/mediatheque")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data:
                media_id = data[0]['id']
                initial_views = data[0].get('views', 0)  # Utiliser .get() avec valeur par défaut
                
                # Incrémenter le compteur de vues
                view_response = session.post(f"{BASE_URL}/rdkq/mediatheque/{media_id}/view")
                
                if view_response.status_code == 200:
                    view_data = view_response.json()
                    if view_data.get('ok'):
                        new_views = view_data.get('views')
                        print(f"✅ Compteur de vues fonctionnel")
                        print(f"   - Vues avant: {initial_views}")
                        print(f"   - Vues après: {new_views}")
                        print(f"   - Incrément: +{new_views - initial_views}")
                        return True
                    else:
                        print(f"❌ Erreur incrémentation: {view_data.get('error')}")
                        return False
                else:
                    print(f"❌ Erreur HTTP incrémentation ({view_response.status_code})")
                    return False
            else:
                print("❌ Aucun média disponible pour tester")
                return False
        except json.JSONDecodeError:
            print("❌ Erreur de parsing JSON")
            return False
    else:
        print(f"❌ Impossible de récupérer les médias ({response.status_code})")
        return False

def test_toggle_operations(session):
    """Test des opérations de basculement (visibilité, vedette)"""
    print("\n=== Test des opérations de basculement ===")
    
    # Récupérer les données admin pour avoir un média
    response = session.get(f"{BASE_URL}/rdkq/admin/mediatheque/data")
    
    if response.status_code == 200:
        try:
            admin_data = response.json()
            if admin_data.get('ok') and admin_data.get('media'):
                media = admin_data['media'][0]
                media_id = media['id']
                
                print(f"🎯 Test avec le média ID {media_id}: '{media['title']}'")
                
                # Test basculement visibilité
                current_public = media['is_public']
                visibility_response = session.post(
                    f"{BASE_URL}/rdkq/admin/mediatheque/{media_id}/toggle-visibility",
                    json={"is_public": not current_public}
                )
                
                if visibility_response.status_code == 200:
                    print(f"✅ Basculement visibilité réussi ({current_public} → {not current_public})")
                else:
                    print(f"❌ Erreur basculement visibilité ({visibility_response.status_code})")
                
                # Test basculement vedette
                current_featured = media['is_featured']
                featured_response = session.post(
                    f"{BASE_URL}/rdkq/admin/mediatheque/{media_id}/toggle-featured",
                    json={"is_featured": not current_featured}
                )
                
                if featured_response.status_code == 200:
                    print(f"✅ Basculement vedette réussi ({current_featured} → {not current_featured})")
                    return True
                else:
                    print(f"❌ Erreur basculement vedette ({featured_response.status_code})")
                    return False
                    
            else:
                print("❌ Aucun média disponible pour les tests")
                return False
        except json.JSONDecodeError:
            print("❌ Erreur de parsing JSON admin")
            return False
    else:
        print(f"❌ Impossible de récupérer les données admin ({response.status_code})")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests du système médiathèque RDKQ")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print("-" * 60)
    
    # Test de connexion
    session = test_login()
    if not session:
        print("\n❌ ÉCHEC CRITIQUE: Impossible de se connecter")
        sys.exit(1)
    
    # Tests fonctionnels
    tests = [
        ("API Médiathèque", test_mediatheque_api),
        ("Interface Admin", test_admin_interface),
        ("Compteur de vues", test_view_counter),
        ("Opérations de basculement", test_toggle_operations),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func(session)
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Exception dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status:<12} {test_name}")
    
    print("-" * 60)
    print(f"🎯 Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS ! Le système est opérationnel.")
        sys.exit(0)
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les logs ci-dessus.")
        sys.exit(1)

if __name__ == "__main__":
    main()
