#!/usr/bin/env python3
"""
Test de la médiathèque en modale
"""
import requests
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8002"

def test_mediatheque_modal():
    """Test de la page avec la modale médiathèque"""
    print("=== Test de la page avec modale médiathèque ===")
    
    try:
        # Tester l'accès à une page RDKQ qui contient la modale
        response = requests.get(f"{BASE_URL}/rdkq/")
        
        if response.status_code == 200:
            # Vérifier que la modale est présente dans le HTML
            html_content = response.text
            
            checks = [
                ('Modal médiathèque', 'id="mediathequeModal"' in html_content),
                ('Bouton médiathèque', 'data-bs-target="#mediathequeModal"' in html_content),
                ('Container médias', 'id="mediatheque-list"' in html_content),
                ('Script de chargement', 'loadMediathequeModal' in html_content),
                ('Fonction vues', 'incrementViews' in html_content)
            ]
            
            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}")
                if not passed:
                    all_passed = False
            
            return all_passed
        else:
            print(f"❌ Erreur d'accès à la page RDKQ ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_mediatheque_api():
    """Test de l'API médiathèque publique"""
    print("\n=== Test de l'API médiathèque publique ===")
    
    try:
        response = requests.get(f"{BASE_URL}/rdkq/mediatheque")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ API accessible - {len(data)} médias trouvés")
                
                if data:
                    media = data[0]
                    required_fields = ['id', 'title', 'desc', 'img', 'src', 'category']
                    missing_fields = [field for field in required_fields if field not in media]
                    
                    if not missing_fields:
                        print("✅ Structure des données correcte")
                        return True
                    else:
                        print(f"❌ Champs manquants: {missing_fields}")
                        return False
                else:
                    print("⚠️  Aucun média trouvé (normal si base vide)")
                    return True
                    
            except Exception as e:
                print(f"❌ Erreur de parsing JSON: {e}")
                return False
        else:
            print(f"❌ Erreur API ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test de la médiathèque en modale RDKQ")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    tests = [
        ("Page avec modale", test_mediatheque_modal()),
        ("API médiathèque", test_mediatheque_api())
    ]
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ")
    print("=" * 50)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status:<12} {test_name}")
    
    print("-" * 50)
    print(f"🎯 Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 La médiathèque modale est opérationnelle !")
        sys.exit(0)
    else:
        print("⚠️  Certains tests ont échoué.")
        sys.exit(1)

if __name__ == "__main__":
    main()
