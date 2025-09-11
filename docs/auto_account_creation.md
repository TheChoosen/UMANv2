# Système de Création Automatique de Compte

## Fonctionnalité

Le système permet aux utilisateurs de se créer un compte automatiquement lors de la première connexion en utilisant :
1. **Email** : L'adresse email de l'utilisateur
2. **Code de sécurité** : Un code à 5 chiffres fourni par l'administration

## Flux de fonctionnement

### Pour un nouvel utilisateur :
1. L'utilisateur entre son email et un code de sécurité à 5 chiffres
2. Le système vérifie si le code est valide
3. Si le code est valide et que l'utilisateur n'existe pas :
   - Un nouveau compte est créé automatiquement
   - L'utilisateur est connecté immédiatement
   - Il est redirigé vers sa page de profil

### Pour un utilisateur existant :
1. L'utilisateur entre son email et le code de sécurité
2. Le système vérifie le code de sécurité
3. Si le code est valide, l'utilisateur est connecté directement

## Configuration

### Codes de sécurité valides
Les codes de sécurité valides sont configurables via la variable d'environnement `VALID_SECURITY_CODES`.

**Défaut :** `12345,54321,11111,22222,33333`

**Exemple de configuration :**
```bash
export VALID_SECURITY_CODES="98765,13579,24680,55555,99999"
```

### Sécurité

- Les codes sont vérifiés côté serveur
- La validation JavaScript empêche la saisie de caractères non numériques
- Le champ est limité à exactement 5 chiffres
- Les requêtes AJAX sont sécurisées avec des headers appropriés

## Interface utilisateur

### Modal de connexion
- Champ email : Validation HTML5 standard
- Champ code de sécurité : 
  - Validation en temps réel (chiffres uniquement)
  - Feedback visuel (bordure verte/rouge)
  - Limitation automatique à 5 caractères
- Messages d'erreur/succès en temps réel via AJAX

### Messages utilisateur
- **Nouveau compte :** "Compte créé et connexion réussie! Bienvenue!"
- **Connexion existante :** "Connexion réussie!"
- **Code invalide :** "Code de sécurité invalide."
- **Erreurs de validation :** Messages spécifiques selon le problème

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

## API Endpoints

### POST /login
**Body (form-data):**
- `email` (string, required) : Email de l'utilisateur
- `security_code` (string, required) : Code à 5 chiffres

**Responses:**

**Succès (200):**
```json
{
  "success": true,
  "message": "Connexion réussie!" | "Compte créé et connexion réussie!",
  "redirect": "/profil"
}
```

**Erreur (400/401/500):**
```json
{
  "success": false,
  "message": "Message d'erreur spécifique"
}
```

## Avantages du système

1. **Simplicité** : Pas besoin de processus d'inscription complexe
2. **Contrôle** : L'administration contrôle qui peut créer des comptes via les codes
3. **Sécurité** : Les codes peuvent être révoqués/changés facilement
4. **UX** : Interface simple et directe pour l'utilisateur
5. **Flexibilité** : Support des utilisateurs existants et nouveaux

## Gestion des codes

### Renouvellement des codes
Pour changer les codes de sécurité, il suffit de mettre à jour la variable d'environnement et redémarrer l'application.

### Révocation
Pour révoquer l'accès, il suffit de retirer le code de la liste des codes valides.

### Codes temporaires
Il est possible d'ajouter des codes temporaires pour des événements spécifiques, puis les retirer après l'événement.
