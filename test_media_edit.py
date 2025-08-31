#!/usr/bin/env python3
"""
Test spécifique pour l'édition de médias
"""

import requests
import json

def test_media_edit():
    """Test de l'édition d'un média"""
    base_url = "http://127.0.0.1:8002"
    session = requests.Session()
    
    print("🧪 Test de l'édition de médias")
    print("=" * 50)
    
    # Étape 1: Login en tant qu'admin
    print("1. Connexion en tant qu'admin...")
    login_url = f"{base_url}/rdkq/login"
    login_data = {
        'email': 'admin@peupleun.live',
        'password': 'admin123'  # ou le bon mot de passe
    }
    
    response = session.post(login_url, data=login_data)
    if 'Connexion réussie' in response.text or response.status_code == 302:
        print("✅ Connexion réussie")
    else:
        print("❌ Échec de la connexion")
        print("   Essayez avec le mot de passe admin correct")
        return
    
    # Étape 2: Récupérer la liste des médias
    print("\n2. Récupération de la liste des médias...")
    data_url = f"{base_url}/rdkq/admin/mediatheque/data"
    response = session.get(data_url)
    
    if response.status_code == 200:
        try:
            medias = response.json()
            print(f"✅ {len(medias)} médias trouvés")
            
            if medias:
                # Prendre le premier média pour test
                test_media = medias[0]
                media_id = test_media['id']
                print(f"   Test avec média ID: {media_id} - '{test_media['title']}'")
                
                # Étape 3: Accès à la page d'édition
                print(f"\n3. Accès à la page d'édition du média {media_id}...")
                edit_url = f"{base_url}/rdkq/admin/mediatheque/{media_id}/edit"
                response = session.get(edit_url)
                
                if response.status_code == 200:
                    print("✅ Page d'édition accessible")
                    
                    # Vérifier si le formulaire contient l'ID
                    if f'value="{media_id}"' in response.text:
                        print("✅ ID du média présent dans le formulaire")
                    else:
                        print("❌ ID du média absent du formulaire")
                        print("   Recherche de 'media-id' dans la page...")
                        if 'media-id' in response.text:
                            print("   Champ media-id trouvé")
                        else:
                            print("   Champ media-id non trouvé")
                    
                    # Étape 4: Test de soumission de l'édition
                    print(f"\n4. Test de soumission de l'édition...")
                    
                    updated_data = {
                        "title": test_media['title'] + " (Modifié)",
                        "description": test_media.get('description', '') + " - Test modification",
                        "category": test_media.get('category', 'test'),
                        "author": test_media.get('author', 'Test Author'),
                        "image_url": test_media.get('image_url', ''),
                        "document_url": test_media.get('document_url', ''),
                        "is_public": test_media.get('is_public', True),
                        "is_featured": test_media.get('is_featured', False)
                    }
                    
                    print(f"   Données de mise à jour: {updated_data}")
                    
                    response = session.post(edit_url, 
                                          headers={'Content-Type': 'application/json'},
                                          data=json.dumps(updated_data))
                    
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            print(f"   Résultat: {result}")
                            
                            if result.get('ok'):
                                print("✅ Média modifié avec succès!")
                            else:
                                print(f"❌ Erreur: {result.get('error')}")
                        except json.JSONDecodeError:
                            print(f"   Response non-JSON: {response.text[:200]}...")
                    else:
                        print(f"❌ Erreur HTTP: {response.status_code}")
                        print(f"   Response: {response.text[:200]}...")
                        
                else:
                    print(f"❌ Erreur accès page d'édition: {response.status_code}")
                    
            else:
                print("❌ Aucun média trouvé pour test")
                print("   Créez d'abord un média avec le formulaire de création")
                
        except json.JSONDecodeError:
            print("❌ Erreur de décodage JSON des médias")
            print(f"   Response: {response.text[:200]}...")
    else:
        print(f"❌ Erreur récupération des médias: {response.status_code}")

def test_form_debugging():
    """Test pour vérifier la structure du formulaire"""
    print("\n🔍 Informations de débogage pour le formulaire")
    print("=" * 50)
    
    print("Instructions pour déboguer manuellement:")
    print("1. Allez à http://127.0.0.1:8002/rdkq/admin/mediatheque")
    print("2. Cliquez sur 'Modifier' d'un média existant")
    print("3. Ouvrez F12 (outils développeur)")
    print("4. Dans la console, tapez:")
    print("   console.log('Media ID:', document.getElementById('media-id')?.value);")
    print("5. Modifiez le titre et cliquez sur 'Mettre à Jour'")
    print("6. Observez les messages de débogage dans la console")
    print("\nMessages à rechercher:")
    print("- 🚀 Soumission du formulaire déclenchée")
    print("- 📝 Données du formulaire")
    print("- 🌐 URL de soumission")
    print("- 📡 Réponse du serveur")

if __name__ == "__main__":
    test_media_edit()
    test_form_debugging()
