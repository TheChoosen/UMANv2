#!/usr/bin/env python3
"""
Test simple pour vérifier les fonctions de hachage
"""

import hashlib
import secrets

def hash_password(password: str) -> str:
    """Hacher un mot de passe avec sel et pbkdf2"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2:sha256:100000${salt}${password_hash.hex()}"

def verify_password(password: str, password_hash: str) -> bool:
    """Vérifier un mot de passe contre son hash"""
    if password_hash == 'activated':
        # Ancien système - accepter n'importe quel mot de passe pour les comptes "activated"
        return True
    
    if not password_hash.startswith('pbkdf2:sha256:'):
        # Hash non reconnu
        return False
    
    try:
        # Format: pbkdf2:sha256:100000$salt$hash
        parts = password_hash.split('$')
        if len(parts) != 3:
            return False
            
        algorithm_info, salt, stored_hash = parts
        iterations = int(algorithm_info.split(':')[-1])
        
        password_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        return password_check.hex() == stored_hash
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test des fonctions de hachage")
    
    # Test 1: Hacher et vérifier un mot de passe
    test_password = "test123"
    print(f"\n1. Test avec le mot de passe: {test_password}")
    
    hashed = hash_password(test_password)
    print(f"   Hash généré: {hashed}")
    
    # Vérifier le mot de passe
    is_valid = verify_password(test_password, hashed)
    print(f"   Vérification: {'✅ Valide' if is_valid else '❌ Invalide'}")
    
    # Test 2: Vérification avec mauvais mot de passe
    print(f"\n2. Test avec mauvais mot de passe")
    wrong_check = verify_password("wrongpassword", hashed)
    print(f"   Vérification: {'✅ Valide' if wrong_check else '❌ Invalide (attendu)'}")
    
    # Test 3: Ancien système "activated"
    print(f"\n3. Test avec ancien système 'activated'")
    old_check = verify_password("anypassword", "activated")
    print(f"   Vérification: {'✅ Valide (compatibilité)' if old_check else '❌ Invalide'}")
    
    print("\n" + "=" * 50)
    print("Tests terminés!")
