# Système de Création Automatique de Compte par Email

## Fonctionnalité

Le système permet aux utilisateurs de se créer un compte automatiquement lors de la première connexion en utilisant un processus en 2 étapes sécurisé :

1. **Étape 1** : L'utilisateur entre son adresse email
2. **Étape 2** : Un code à 6 chiffres est envoyé par email
3. **Étape 3** : L'utilisateur entre le code reçu pour se connecter/créer son compte

## Flux de fonctionnement

### Pour un nouvel utilisateur :
1. L'utilisateur clique sur "Connexion" et entre son email
2. Le système génère un code aléatoire à 6 chiffres et l'envoie par email
3. L'utilisateur entre le code reçu par email
4. Le système vérifie le code et crée automatiquement un nouveau compte
5. L'utilisateur est connecté immédiatement et redirigé vers son profil

### Pour un utilisateur existant :
1. L'utilisateur entre son email 
2. Un code à 6 chiffres est envoyé par email
3. L'utilisateur entre le code reçu
4. Le système vérifie le code et connecte l'utilisateur directement

## Configuration

### Sécurité du code
- **Longueur** : 6 chiffres (ex: 123456)
- **Génération** : Aléatoire avec `secrets.randbelow(10)`
- **Validité** : 15 minutes après envoi
- **Stockage** : Code hashé en session (sécurisé)
- **Unicité** : Un seul code actif par session

### Variables d'environnement

**Configuration email (obligatoire pour production) :**
```bash
# Méthode 1: SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=noreply@yoursite.com

# Méthode 2: Resend API (recommandé)
RESEND_API_KEY=your-resend-api-key

# Mode développement/test
UMAN_ENV=staging  # Écrit les emails dans des fichiers
UMAN_STAGING_OUT=/path/to/test/emails
```

## Interface utilisateur

### Modal de connexion - Étape 1
- Champ email avec validation HTML5
- Bouton "Envoyer le code"
- Message explicatif sur la réception du code

### Modal de connexion - Étape 2  
- Champ code à 6 chiffres avec validation en temps réel
- Affichage de l'email de destination
- Boutons "Se connecter", "Renvoyer le code", "Retour"
- Feedback visuel (bordure verte/rouge)

### Messages utilisateur
- **Code envoyé :** "Code envoyé à [email]. Vérifiez votre boîte de réception."
- **Nouveau compte :** "Compte créé et connexion réussie! Bienvenue!"
- **Connexion existante :** "Connexion réussie!"
- **Code invalide :** "Code invalide."
- **Code expiré :** "Code expiré. Veuillez redemander un code."

## API Endpoints

### POST /send-login-code
**Body (JSON):**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Code envoyé à user@example.com. Vérifiez votre boîte de réception."
}
```

**Errors (400/500):**
```json
{
  "success": false,
  "message": "Message d'erreur spécifique"
}
```

### POST /verify-login-code
**Body (JSON):**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Connexion réussie!" | "Compte créé et connexion réussie!",
  "redirect": "/profil"
}
```

**Errors (400):**
```json
{
  "success": false,
  "message": "Code invalide." | "Code expiré." | "Code à 6 chiffres requis."
}
```

## Base de données

### Nouveau membre créé automatiquement :
```sql
INSERT INTO membres (email, username, password, created_at, is_admin)
VALUES (email, username_from_email, 'activated', NOW(), FALSE)
```

### Champs automatiquement remplis :
- `email` : Email fourni par l'utilisateur
- `username` : Partie avant @ de l'email  
- `password` : 'activated' (système simplifié)
- `created_at` : Date/heure actuelle
- `is_admin` : FALSE par défaut

## Sécurité

### Gestion des codes
- **Hachage** : Les codes sont hachés avant stockage (SHA-256)
- **Expiration** : 15 minutes de validité automatique
- **Session** : Code lié à la session utilisateur
- **Nettoyage** : Code supprimé après usage ou expiration

### Protection contre les abus
- Un seul code actif par session
- Validation stricte côté serveur
- Limitation de durée de vie
- Validation du format (6 chiffres exactement)

### Email sécurisé
- Support SMTP avec TLS
- Support Resend API (recommandé)
- Mode staging pour les tests
- Gestion d'erreurs robuste

## Avantages du système

1. **Sécurité renforcée** : Vérification par email obligatoire
2. **Simplicité** : Pas de mot de passe à retenir
3. **Flexibilité** : Fonctionne pour nouveaux et anciens utilisateurs
4. **UX optimale** : Interface intuitive en 2 étapes
5. **Évolutif** : Support de multiples fournisseurs d'email
6. **Testable** : Mode staging pour le développement

## Mode développement

### Test local
```bash
# Mode staging - emails sauvés dans des fichiers
export UMAN_ENV=staging
export UMAN_STAGING_OUT=/tmp/test_emails

# Lancer les tests
python3 test_email_system.py
```

### Test de production
```bash
# Configuration SMTP complète
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASS=your-password
export SMTP_FROM=noreply@yoursite.com

# Démarrer le serveur
python3 app.py
```
