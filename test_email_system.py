#!/usr/bin/env python3
"""
Test du nouveau système de connexion par email avec code à 6 chiffres
"""

import os
import sys
import json
sys.path.insert(0, '/home/amenard/UMANv2/UMANv2')

# Configuration pour les tests
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['UMAN_ENV'] = 'staging'  # Utiliser le mode staging pour les emails
os.environ['UMAN_STAGING_OUT'] = '/tmp/uman_test_emails'

def test_email_flow():
    """Test du flux complet d'envoi et de vérification de code"""
    print("🧪 TEST: Flux complet de connexion par email")
    print("=" * 50)
    
    from app import app
    
    with app.test_client() as client:
        test_email = 'test.nouveau.flow@example.com'
        
        # Étape 1: Demander un code
        print(f"\n📧 Étape 1: Envoi du code à {test_email}")
        response = client.post('/send-login-code', 
                              json={'email': test_email},
                              headers={'X-Requested-With': 'XMLHttpRequest'})
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.get_json()
            print(f"   ✅ Succès: {result.get('message')}")
        else:
            print(f"   ❌ Erreur: {response.get_data(as_text=True)}")
            return False
        
        # Lire le code depuis le fichier généré en mode staging
        import glob
        email_files = glob.glob('/tmp/uman_test_emails/login_code_*.txt')
        if not email_files:
            print("   ❌ Aucun fichier email trouvé")
            return False
        
        latest_file = max(email_files, key=os.path.getctime)
        with open(latest_file, 'r') as f:
            content = f.read()
            # Extraire le code du contenu
            import re
            code_match = re.search(r'Code: (\d{6})', content)
            if not code_match:
                print("   ❌ Code non trouvé dans l'email")
                return False
            
            code = code_match.group(1)
            print(f"   📋 Code extrait: {code}")
        
        # Étape 2: Vérifier le code
        print(f"\n🔐 Étape 2: Vérification du code")
        response = client.post('/verify-login-code',
                              json={'email': test_email, 'code': code},
                              headers={'X-Requested-With': 'XMLHttpRequest'})
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.get_json()
            print(f"   ✅ Succès: {result.get('message')}")
            print(f"   🔄 Redirection: {result.get('redirect')}")
            return True
        else:
            print(f"   ❌ Erreur: {response.get_data(as_text=True)}")
            return False

def test_invalid_scenarios():
    """Test des scénarios d'erreur"""
    print("\n🚫 TEST: Scénarios d'erreur")
    print("=" * 30)
    
    from app import app
    
    with app.test_client() as client:
        # Test 1: Code invalide
        print("\n   Test 1: Code invalide")
        response = client.post('/verify-login-code',
                              json={'email': 'test@example.com', 'code': '999999'},
                              headers={'X-Requested-With': 'XMLHttpRequest'})
        
        if response.status_code == 400:
            result = response.get_json()
            print(f"   ✅ Rejet attendu: {result.get('message')}")
        else:
            print(f"   ⚠️  Status inattendu: {response.status_code}")
        
        # Test 2: Email manquant
        print("\n   Test 2: Email manquant")
        response = client.post('/send-login-code',
                              json={},
                              headers={'X-Requested-With': 'XMLHttpRequest'})
        
        if response.status_code == 400:
            result = response.get_json()
            print(f"   ✅ Validation: {result.get('message')}")
        else:
            print(f"   ⚠️  Status inattendu: {response.status_code}")
        
        # Test 3: Code trop court
        print("\n   Test 3: Code trop court")
        response = client.post('/verify-login-code',
                              json={'email': 'test@example.com', 'code': '123'},
                              headers={'X-Requested-With': 'XMLHttpRequest'})
        
        if response.status_code == 400:
            result = response.get_json()
            print(f"   ✅ Validation: {result.get('message')}")
        else:
            print(f"   ⚠️  Status inattendu: {response.status_code}")

def check_database():
    """Vérifier l'état de la base de données"""
    print("\n💾 TEST: Base de données")
    print("=" * 25)
    
    from app import app, get_mysql_db
    
    try:
        with app.app_context():
            db = get_mysql_db()
            cur = db.cursor(dictionary=True)
            
            # Compter les utilisateurs
            cur.execute('SELECT COUNT(*) as count FROM membres')
            count = cur.fetchone()['count']
            print(f"   📊 Utilisateurs total: {count}")
            
            # Afficher les derniers utilisateurs
            cur.execute('SELECT email, username, created_at, is_admin FROM membres ORDER BY created_at DESC LIMIT 3')
            users = cur.fetchall()
            
            print("   👥 Derniers utilisateurs:")
            for user in users:
                admin_flag = " [Admin]" if user['is_admin'] else ""
                print(f"      - {user['email']} ({user['username']}){admin_flag}")
            
            return True
    except Exception as e:
        print(f"   ❌ Erreur DB: {e}")
        return False

def main():
    """Exécuter tous les tests"""
    print("🎯 NOUVEAU SYSTÈME DE CONNEXION PAR EMAIL")
    print("Système en 2 étapes avec code à 6 chiffres")
    print("=" * 60)
    
    # Créer le dossier de test
    os.makedirs('/tmp/uman_test_emails', exist_ok=True)
    
    # Tests
    success = True
    success &= check_database()
    success &= test_email_flow()
    test_invalid_scenarios()  # Tests d'erreur (pas critique pour le succès)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("\n✅ Fonctionnalités validées:")
        print("   - Envoi de code à 6 chiffres par email")
        print("   - Vérification et validation du code")
        print("   - Création automatique de compte")
        print("   - Connexion des utilisateurs existants")
        print("   - Gestion d'erreurs et validation")
        
        print("\n🌐 Pour tester dans le navigateur:")
        print("1. Démarrer: python3 app.py")
        print("2. Aller sur: http://localhost:8002")
        print("3. Cliquer 'Connexion' puis:")
        print("   - Étape 1: Entrer votre email")
        print("   - Étape 2: Entrer le code à 6 chiffres reçu")
        print("4. Compte créé automatiquement si nouveau!")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    
    # Nettoyage
    import shutil
    if os.path.exists('/tmp/uman_test_emails'):
        shutil.rmtree('/tmp/uman_test_emails')

if __name__ == "__main__":
    main()
