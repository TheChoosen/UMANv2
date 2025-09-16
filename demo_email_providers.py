#!/usr/bin/env python3
"""
Démonstration de l'envoi d'emails avec UMANv2
Montre les différents providers : Resend, SMTP, Console, Staging
"""

import os
import sys
import secrets
from datetime import datetime, timezone

# Ajouter le répertoire parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_email_providers():
    """Démonstration des différents providers d'email"""
    
    print("🚀 Démonstration des providers d'email UMANv2")
    print("=" * 60)
    
    # Importer après avoir ajouté le path
    from app import send_login_code_email, _email_status
    
    test_email = "test@exemple.com"
    test_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    print(f"📧 Email de test: {test_email}")
    print(f"🔢 Code de test: {test_code}")
    print()
    
    # 1. Mode Console (par défaut si aucune config)
    print("1️⃣ Test mode Console (développement)")
    print("-" * 40)
    print("ℹ️  Aucune clé API configurée - utilise la console")
    
    # Sauvegarder l'état des variables d'environnement
    original_resend_key = os.environ.get('RESEND_API_KEY')
    original_smtp_host = os.environ.get('SMTP_HOST')
    
    # Désactiver temporairement toutes les configs
    if 'RESEND_API_KEY' in os.environ:
        del os.environ['RESEND_API_KEY']
    if 'SMTP_HOST' in os.environ:
        del os.environ['SMTP_HOST']
    
    try:
        send_login_code_email(test_email, test_code)
        print(f"✅ Provider utilisé: {_email_status.get('last_provider', 'unknown')}")
        print(f"📊 Résultat: {_email_status.get('last_result', 'unknown')}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print()
    
    # 2. Mode Staging
    print("2️⃣ Test mode Staging (fichiers)")
    print("-" * 40)
    os.environ['UMAN_ENV'] = 'staging'
    test_code_2 = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    try:
        send_login_code_email(test_email, test_code_2)
        print(f"✅ Provider utilisé: {_email_status.get('last_provider', 'unknown')}")
        print(f"📊 Résultat: {_email_status.get('last_result', 'unknown')}")
        print(f"📄 Fichier: {_email_status.get('last_detail', 'unknown')}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Rétablir l'environnement
    if 'UMAN_ENV' in os.environ:
        del os.environ['UMAN_ENV']
    
    print()
    
    # 3. Mode Resend (si clé API fournie)
    print("3️⃣ Test mode Resend (production)")
    print("-" * 40)
    
    if original_resend_key:
        os.environ['RESEND_API_KEY'] = original_resend_key
        test_code_3 = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        print("🔑 Clé API Resend détectée")
        print("⚠️  Pour tester réellement, changez l'email vers une adresse valide")
        
        # Ne pas envoyer réellement en démo, juste montrer la config
        try:
            import resend
            print("✅ SDK Resend disponible")
            print(f"🎯 Serait envoyé via Resend à: {test_email}")
        except ImportError:
            print("❌ SDK Resend non disponible")
    else:
        print("⚠️  Aucune clé RESEND_API_KEY configurée")
        print("💡 Pour tester Resend:")
        print("   export RESEND_API_KEY=re_votre_cle")
    
    print()
    
    # 4. Informations sur la configuration
    print("4️⃣ Configuration actuelle")
    print("-" * 40)
    print(f"🔑 RESEND_API_KEY: {'✅ Définie' if os.environ.get('RESEND_API_KEY') else '❌ Non définie'}")
    print(f"📮 SMTP_HOST: {os.environ.get('SMTP_HOST', '❌ Non défini')}")
    print(f"📧 SMTP_FROM: {os.environ.get('SMTP_FROM', 'info@uman-api.com (défaut)')}")
    print(f"🌍 UMAN_ENV: {os.environ.get('UMAN_ENV', 'development (défaut)')}")
    print(f"📊 LOG_LEVEL: {os.environ.get('LOG_LEVEL', 'INFO (défaut)')}")
    
    print()
    
    # 5. Ordre de priorité
    print("5️⃣ Ordre de priorité des providers")
    print("-" * 40)
    print("1. 🥇 Resend (si RESEND_API_KEY définie)")
    print("2. 🥈 SMTP (si SMTP_HOST/USER/PASS définis)")
    print("3. 🥉 Console (développement)")
    print("4. 📁 Staging (si UMAN_ENV=staging)")
    
    # Restaurer les variables d'environnement
    if original_resend_key:
        os.environ['RESEND_API_KEY'] = original_resend_key
    if original_smtp_host:
        os.environ['SMTP_HOST'] = original_smtp_host

def show_resend_setup():
    """Affiche les instructions de configuration Resend"""
    print()
    print("🎯 Configuration Resend pour la production")
    print("=" * 60)
    print()
    print("1️⃣ Créer un compte sur https://resend.com")
    print("2️⃣ Obtenir votre clé API dans le dashboard")
    print("3️⃣ Configurer votre domaine et DNS")
    print("4️⃣ Définir la variable d'environnement:")
    print("   export RESEND_API_KEY=re_votre_cle_api")
    print()
    print("5️⃣ Tester avec:")
    print("   python3 test_resend_integration.py")
    print()
    print("📚 Documentation complète: docs/resend_configuration.md")

if __name__ == "__main__":
    demo_email_providers()
    show_resend_setup()
    
    print()
    print("=" * 60)
    print("✅ Démonstration terminée!")
    print("🔧 Le système UMANv2 est prêt avec support Resend!")
