# Configuration Resend pour UMANv2

Ce document explique comment configurer et utiliser Resend comme service d'envoi d'emails pour UMANv2.

## 1. Installation

Le SDK Resend est déjà installé dans le projet :
```bash
pip install resend
```

## 2. Configuration

### Variables d'environnement

Configurez votre clé API Resend :
```bash
export RESEND_API_KEY="re_votre_cle_api_resend"
```

### Adresse d'expéditeur

Configurez l'adresse d'expéditeur (optionnel) :
```bash
export SMTP_FROM="noreply@votredomaine.com"
```
Par défaut : `info@uman-api.com`

## 3. Fonctionnement

### Priorité des services d'envoi

1. **Resend** (si `RESEND_API_KEY` est définie)
2. **SMTP** (si configuré avec `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`)
3. **Console** (développement - affiche dans la console)
4. **Staging** (si `UMAN_ENV=staging` - sauvegarde dans des fichiers)

### Fonctions d'envoi

#### send_login_code_email()
- Envoie un code de connexion à 6 chiffres
- Format HTML amélioré avec mise en forme
- Fallback texte pour compatibilité
- Durée de validité : 15 minutes

#### send_code_email()
- Utilise les templates Flask (`emails/confirmation.html` et `.txt`)
- Pour les codes de confirmation généraux
- Durée de validité configurable via `UMAN_CODE_TTL_MINUTES`

## 4. Test de l'intégration

Testez votre configuration Resend :
```bash
python3 test_resend_integration.py
```

## 5. Format des emails envoyés

### Email de connexion (HTML)
- Design moderne avec CSS inline
- Code en gros caractères avec espacement
- Informations de validité claires
- Branding UMan API

### Contenu texte (fallback)
- Version texte brute pour clients email anciens
- Même information essentielle

## 6. Logs et monitoring

Les envois sont loggés avec :
- Provider utilisé (resend/smtp/console/staging)
- Résultat (ok/error)
- Détails de l'erreur le cas échéant
- Timestamp

Variable `_email_status` contient le statut du dernier envoi.

## 7. Domaines autorisés Resend

Pour utiliser Resend en production :
1. Ajoutez votre domaine dans le dashboard Resend
2. Configurez les enregistrements DNS (SPF, DKIM, DMARC)
3. Utilisez une adresse d'expéditeur de votre domaine vérifié

## 8. Limites et quotas

Resend Free tier :
- 3 000 emails/mois
- 100 emails/jour
- Domaine resend.dev pour les tests

Pour plus de volume, passez au plan payant.

## 9. Dépannage

### Erreurs communes

**"API key not found"**
```bash
export RESEND_API_KEY="re_votre_cle"
```

**"Domain not verified"**
- Vérifiez votre domaine dans le dashboard Resend
- Utilisez `onboarding@resend.dev` pour les tests

**"Rate limit exceeded"**
- Attendez avant de renvoyer
- Vérifiez vos quotas Resend

### Debug

Activez les logs détaillés :
```bash
export LOG_LEVEL=DEBUG
```

## 10. Migration depuis SMTP

Pour migrer depuis SMTP vers Resend :
1. Obtenez votre clé API Resend
2. Ajoutez `RESEND_API_KEY` dans vos variables d'environnement
3. L'application utilisera automatiquement Resend en priorité
4. Conservez la configuration SMTP comme fallback
