#!/usr/bin/env python3
"""
Test d'intégration Resend pour UMANv2
Test l'envoi d'un code de connexion via Resend
"""

import os
import secrets
from datetime import datetime, timezone
import logging

# Configuration pour le test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_resend_integration():
    """Test l'intégration Resend"""
    try:
        import resend
        print("✓ SDK Resend importé avec succès")
        
        # Vérifier la clé API
        api_key = os.environ.get('RESEND_API_KEY')
        if not api_key:
            print("❌ RESEND_API_KEY non définie dans les variables d'environnement")
            print("Pour définir la clé : export RESEND_API_KEY=re_...")
            return False
        
        print("✓ Clé API Resend trouvée")
        
        # Configuration
        resend.api_key = api_key
        
        # Test email (remplacer par une adresse valide pour tester)
        test_email = "seiadammenard@gmail.com"  # Utiliser l'email de test existant
        test_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        print(f"🧪 Test d'envoi du code {test_code} à {test_email}")
        
        # Créer le contenu HTML
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">Test UMan - Code de connexion</h2>
            <p>Bonjour,</p>
            <p>Voici votre code de test UMan :</p>
            <div style="background-color: #f4f4f4; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                <h1 style="color: #007bff; font-size: 32px; letter-spacing: 3px; margin: 0;">{test_code}</h1>
            </div>
            <p>Ce code est un test d'intégration Resend.</p>
            <p>Timestamp: {datetime.now(timezone.utc).isoformat()}</p>
            <hr style="margin-top: 30px;">
            <p style="color: #666; font-size: 12px;">UMan API - Test Resend</p>
        </div>
        """
        
        text_body = f"Test UMan - Code de connexion: {test_code}\nCe code est un test d'intégration Resend.\nTimestamp: {datetime.now(timezone.utc).isoformat()}"
        
        # Paramètres d'envoi
        params = {
            "from": "UMan API <onboarding@resend.dev>",  # Adresse par défaut pour les tests
            "to": [test_email],
            "subject": "🧪 Test UMan - Code de connexion",
            "html": html_body,
            "text": text_body,
        }
        
        # Envoyer l'email
        result = resend.Emails.send(params)
        
        print(f"✅ Email envoyé avec succès!")
        print(f"📧 Résultat: {result}")
        print(f"🔢 Code envoyé: {test_code}")
        
        return True
        
    except ImportError:
        print("❌ SDK Resend non installé. Installer avec: pip install resend")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test Resend: {e}")
        logger.exception("Détails de l'erreur:")
        return False

if __name__ == "__main__":
    print("🚀 Test d'intégration Resend pour UMANv2")
    print("=" * 50)
    
    success = test_resend_integration()
    
    print("=" * 50)
    if success:
        print("✅ Test d'intégration Resend réussi!")
        print("🎯 Prêt pour la production avec Resend")
    else:
        print("❌ Test d'intégration Resend échoué")
        print("🔧 Vérifiez la configuration et réessayez")
