#!/usr/bin/env python3
"""
Test simple pour vérifier les URLs d'édition
"""

import requests

def test_edit_urls():
    """Test simple des URLs d'édition"""
    base_url = "http://127.0.0.1:8002"
    
    print("🧪 Test simple des URLs RDKQ")
    print("=" * 40)
    
    urls_to_test = [
        "/rdkq",
        "/rdkq/login", 
        "/rdkq/admin/mediatheque",
        "/rdkq/admin/mediatheque/data",
        "/rdkq/admin/mediatheque/new",
        "/rdkq/admin/mediatheque/1/edit"  # Test avec ID 1
    ]
    
    for url in urls_to_test:
        try:
            full_url = base_url + url
            response = requests.get(full_url, allow_redirects=False, timeout=5)
            
            if response.status_code == 200:
                status = "✅ OK"
            elif response.status_code == 302:
                redirect_to = response.headers.get('Location', 'Non spécifié')
                status = f"🔄 Redirect → {redirect_to}"
            elif response.status_code == 404:
                status = "❌ Not Found"
            elif response.status_code == 403:
                status = "🔒 Forbidden (auth required)"
            else:
                status = f"❓ {response.status_code}"
                
            print(f"{url:<35} {status}")
            
        except requests.exceptions.ConnectionError:
            print(f"{url:<35} ❌ Connection Error")
        except requests.exceptions.Timeout:
            print(f"{url:<35} ❌ Timeout")
        except Exception as e:
            print(f"{url:<35} ❌ Error: {e}")

def test_with_manual_steps():
    """Instructions de test manuel"""
    print("\n📋 Instructions de test manuel pour l'édition:")
    print("=" * 50)
    print("1. ✅ S'assurer que Flask fonctionne:")
    print("   → http://127.0.0.1:8002/rdkq")
    print()
    print("2. 🔑 Se connecter en tant qu'admin:")
    print("   → http://127.0.0.1:8002/rdkq/login")
    print("   → Email: admin@peupleun.live")
    print("   → Password: [le bon mot de passe admin]")
    print()
    print("3. 📋 Aller à la liste des médias:")
    print("   → http://127.0.0.1:8002/rdkq/admin/mediatheque")
    print()
    print("4. ✏️ Cliquer sur 'Modifier' d'un média existant")
    print("   → Ouvrir F12 (outils développeur)")
    print("   → Aller dans l'onglet Console")
    print()
    print("5. 🔍 Vérifier dans la console JavaScript:")
    print("   → Taper: console.log('Media ID:', document.getElementById('media-id')?.value);")
    print("   → Doit afficher l'ID du média")
    print()
    print("6. 📝 Modifier le titre et cliquer 'Mettre à Jour'")
    print("   → Observer les logs dans la console:")
    print("   → 🚀 Soumission du formulaire déclenchée")
    print("   → 🔍 Mode édition détecté: true")
    print("   → 🌐 URL de soumission: /rdkq/admin/mediatheque/[ID]/edit")
    print("   → 📡 Réponse du serveur: 200 OK")
    print()
    print("7. ❌ Si ça ne fonctionne pas, noter:")
    print("   → Le message d'erreur exact")
    print("   → Le status code de la réponse")
    print("   → Si l'ID du média est bien détecté")

if __name__ == "__main__":
    test_edit_urls()
    test_with_manual_steps()
