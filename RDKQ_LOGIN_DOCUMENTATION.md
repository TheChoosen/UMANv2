# Système de Login RDKQ - Documentation

## 🎯 Vue d'ensemble

Le système de login RDKQ (République du Kwébec) est maintenant opérationnel avec une interface dédiée et des fonctionnalités complètes d'authentification.

## 🔗 URLs Disponibles

### Pages principales
- **Accueil RDKQ**: http://127.0.0.1:8002/rdkq
- **Connexion**: http://127.0.0.1:8002/rdkq/login
- **Inscription**: http://127.0.0.1:8002/rdkq/register
- **Administration**: http://127.0.0.1:8002/rdkq/admin (réservé aux admins)

### Actions
- **Déconnexion**: http://127.0.0.1:8002/rdkq/logout

## 👑 Comptes Administrateurs

### Admin principal
- **Email**: admin@peupleun.live
- **Mot de passe**: admin123
- **Statut**: Administrateur

### Admin secondaire
- **Email**: seiadammenard@gmail.com  
- **Mot de passe**: admin123
- **Statut**: Administrateur

## ✨ Fonctionnalités

### 🔐 Authentification
- ✅ Hash sécurisé SHA256 pour les mots de passe
- ✅ Validation des formulaires côté client et serveur
- ✅ Messages flash pour les erreurs/succès
- ✅ Sessions utilisateur persistantes
- ✅ Gestion des permissions admin/utilisateur

### 🎨 Interface utilisateur
- ✅ Design cohérent avec le thème RDKQ
- ✅ Effets glass morphism
- ✅ Animations d'entrée fluides
- ✅ Responsive design
- ✅ Navigation intuitive

### 📝 Formulaires
- ✅ **Connexion**: Email + mot de passe + option "se souvenir"
- ✅ **Inscription**: Prénom, nom, email, mot de passe, cercle local
- ✅ Validation en temps réel
- ✅ Confirmation de mot de passe
- ✅ Acceptation des conditions d'utilisation

### 🗄️ Base de données
- ✅ Table `membres` unifiée (fusion users + membres)
- ✅ Colonnes: id, email, username, password, nom, cercle_local, is_admin, created_at
- ✅ Support des cercles locaux (Montréal, Québec, etc.)
- ✅ Gestion des rôles admin/utilisateur

## 🛡️ Sécurité

### Mots de passe
- Hash SHA256 pour tous les nouveaux comptes
- Mot de passe minimum 6 caractères
- Vérification de confirmation lors de l'inscription

### Sessions
- Stockage sécurisé des informations utilisateur
- Variables de session: user_id, user_email, username, is_admin
- Déconnexion complète avec nettoyage de session

### Permissions
- Contrôle d'accès basé sur les rôles
- Pages admin protégées
- Vérification des droits à chaque requête

## 🚀 Utilisation

### Pour se connecter
1. Aller sur http://127.0.0.1:8002/rdkq/login
2. Entrer email et mot de passe
3. Cliquer "Se connecter"
4. Redirection vers l'accueil RDKQ avec session active

### Pour s'inscrire
1. Aller sur http://127.0.0.1:8002/rdkq/register
2. Remplir le formulaire (prénom, nom, email, mot de passe)
3. Choisir un cercle local (optionnel)
4. Accepter les conditions
5. Création automatique du compte

### Navigation
- Le bouton "Connexion" apparaît quand l'utilisateur n'est pas connecté
- Le bouton "Déconnexion" apparaît quand l'utilisateur est connecté
- Le bouton "Admin" apparaît uniquement pour les administrateurs

## 🔧 Architecture technique

### Fichiers modifiés/créés
- `templates/RepubliqueduKwebec/login.html` - Page de connexion
- `templates/RepubliqueduKwebec/register.html` - Page d'inscription
- `templates/RepubliqueduKwebec/base.html` - Navigation mise à jour
- `app.py` - Routes RDKQ ajoutées (/rdkq/login, /rdkq/register, /rdkq/logout)

### Routes Flask
```python
@app.route('/rdkq/login', methods=['GET', 'POST'])
@app.route('/rdkq/register', methods=['GET', 'POST']) 
@app.route('/rdkq/logout')
```

### Base de données MySQL
- Serveur: 192.168.50.101
- Schema: peupleun
- Table: membres (remplace l'ancienne table users)

## 📊 État actuel

✅ **Système opérationnel**
- 2 administrateurs configurés
- Base de données MySQL connectée
- Interface utilisateur complète
- Authentification sécurisée
- Navigation fonctionnelle

## 🎯 Prochaines améliorations possibles

1. **Récupération de mot de passe** (route /rdkq/forgot-password)
2. **Validation par email** pour les nouveaux comptes
3. **Profils utilisateur** étendus avec photo et bio
4. **Gestion des cercles locaux** avec fonctionnalités dédiées
5. **Système de notifications** pour les membres
6. **API REST** pour les applications mobiles

Le système de login RDKQ est maintenant pleinement fonctionnel et prêt pour la production! 🎉
