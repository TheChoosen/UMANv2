# 🗃️ Documentation des Tables MySQL - UMan API

## 📋 Vue d'ensemble

L'application UMan API utilise une base de données MySQL nommée **`peupleun`** avec plusieurs tables pour gérer les utilisateurs, les soumissions, la médiathèque et les cercles locaux. Cette documentation détaille la structure et l'utilisation de chaque table.

---

## 🏗️ Configuration de la base de données

- **Serveur** : MySQL
- **Schéma** : `peupleun`
- **Encodage** : `utf8mb4` avec collation `utf8mb4_unicode_ci`
- **Moteur** : InnoDB (support des transactions et clés étrangères)

---

## 📊 Tables de la base de données

### 1. 👥 Table `membres`

**Objectif** : Gestion des utilisateurs et membres de la République du Kwébec (RDKQ)

#### Structure des colonnes :

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique du membre |
| `nom` | VARCHAR(100) | | Nom de famille du membre |
| `prenom` | VARCHAR(100) | | Prénom du membre |
| `email` | VARCHAR(120) | UNIQUE | Adresse email (identifiant de connexion) |
| `username` | VARCHAR(80) | UNIQUE | Nom d'utilisateur unique |
| `password` | VARCHAR(120) | | Mot de passe hashé ou code de confirmation temporaire |
| `cercle_local` | VARCHAR(100) | | Cercle local de rattachement |
| `is_admin` | TINYINT(1) | DEFAULT 0 | Statut administrateur (0=membre, 1=admin) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date de création du compte |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Date de dernière modification |

#### Index :
- `idx_email` sur `email`
- `idx_username` sur `username`

#### Utilisation :
- **Authentification** : Login avec email/password
- **Gestion des droits** : Distinction membres/administrateurs
- **Organisation territoriale** : Rattachement aux cercles locaux
- **Activation de compte** : Système de code de confirmation par email

---

### 2. 📝 Table `submissions`

**Objectif** : Stockage des données du questionnaire participatif démocratique

#### Structure des colonnes :

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de la soumission |
| `nom` | VARCHAR(100) | | Nom du participant |
| `email` | VARCHAR(120) | | Email du participant |
| `sujet` | VARCHAR(255) | | Sujet de la participation |
| `message` | TEXT | | Message principal du participant |
| `username` | VARCHAR(80) | NOT NULL | Nom d'utilisateur du participant |
| `prenom` | VARCHAR(100) | | Prénom du participant |
| `age` | VARCHAR(10) | | Tranche d'âge |
| `region` | VARCHAR(100) | | Région de résidence |
| `occupation` | VARCHAR(200) | | Profession/occupation |
| `salaire` | VARCHAR(50) | | Tranche de salaire |
| `education` | VARCHAR(200) | | Niveau d'éducation |
| `sante` | VARCHAR(200) | | Préoccupations santé |
| `transport` | VARCHAR(200) | | Préoccupations transport |
| `logement` | VARCHAR(200) | | Préoccupations logement |
| `environnement` | VARCHAR(200) | | Préoccupations environnementales |
| `economie` | VARCHAR(200) | | Préoccupations économiques |
| `securite` | VARCHAR(200) | | Préoccupations sécurité |
| `culture` | VARCHAR(200) | | Préoccupations culturelles |
| `participation` | VARCHAR(200) | | Modalités de participation souhaitées |
| `priorites` | TEXT | | Priorités politiques |
| `ameliorations` | TEXT | | Suggestions d'amélioration |
| `commentaires` | TEXT | | Commentaires libres |
| `rgpd` | TINYINT(1) | | Acceptation RGPD |
| `attachment` | VARCHAR(500) | | Nom du fichier joint (optionnel) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date de soumission |

#### Index :
- `idx_username` sur `username`
- `idx_created_at` sur `created_at`

#### Utilisation :
- **Démocratie participative** : Collecte des avis citoyens
- **Analyse sociologique** : Données démographiques et socio-économiques
- **Formulaire contact** : Gestion des messages et fichiers joints
- **RGPD** : Traçabilité du consentement

---

### 3. 📚 Table `mediatheque`

**Objectif** : Gestion de la bibliothèque de ressources documentaires de la RDKQ

#### Structure des colonnes :

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique du média |
| `title` | VARCHAR(255) | NOT NULL | Titre du document/média |
| `description` | TEXT | | Description détaillée |
| `image_url` | VARCHAR(500) | | URL de l'image de prévisualisation |
| `document_url` | VARCHAR(500) | | URL du document/vidéo principal |
| `category` | VARCHAR(100) | | Catégorie (documentaire, guide, video, formation, etc.) |
| `author` | VARCHAR(255) | | Auteur ou organisation créatrice |
| `is_public` | BOOLEAN | DEFAULT TRUE | Visibilité publique (1=public, 0=privé) |
| `is_featured` | BOOLEAN | DEFAULT FALSE | Statut vedette pour mise en avant |
| `views_count` | INT | DEFAULT 0 | Compteur de vues |
| `created_by` | INT | FOREIGN KEY → membres(id) | ID du membre créateur |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date de création |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Date de modification |

#### Index :
- `idx_category` sur `category`
- `idx_public` sur `is_public`
- `idx_featured` sur `is_featured`
- `idx_created_at` sur `created_at`

#### Clés étrangères :
- `created_by` REFERENCES `membres(id)` ON DELETE SET NULL

#### Utilisation :
- **Centre de ressources** : Documentaires, guides, formations
- **Gestion des contenus** : Publication/dépublication par les admins
- **Statistiques** : Compteur de vues pour analyser l'engagement
- **Catégorisation** : Organisation thématique des ressources

---

### 4. 🏛️ Table `cercles`

**Objectif** : Gestion des cercles locaux pour l'organisation territoriale démocratique

#### Structure des colonnes :

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique du cercle |
| `nom` | VARCHAR(200) | NOT NULL | Nom du cercle local |
| `description` | TEXT | | Description et objectifs du cercle |
| `region` | VARCHAR(100) | | Région géographique |
| `membres_count` | INT | DEFAULT 0 | Nombre de membres actifs |
| `created_by` | VARCHAR(80) | | Username du créateur |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date de création |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Date de modification |

#### Index :
- `idx_region` sur `region`
- `idx_created_by` sur `created_by`

#### Utilisation :
- **Organisation territoriale** : Structuration géographique des membres
- **Démocratie locale** : Prise de décision au niveau des cercles
- **Statistiques** : Suivi du nombre de membres par cercle
- **Sociocratie** : Application des principes de gouvernance partagée

---

### 5. 📊 Table `users` (EN DÉPRÉCIATION)

**Objectif** : Table historique en cours de migration vers `membres`

#### Structure des colonnes :

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique |
| `username` | VARCHAR(80) | NOT NULL UNIQUE | Nom d'utilisateur |
| `password` | VARCHAR(120) | NOT NULL | Mot de passe hashé |
| `email` | VARCHAR(120) | UNIQUE | Adresse email |
| `is_admin` | BOOLEAN | DEFAULT FALSE | Statut administrateur |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date de création |

#### Index :
- `idx_username` sur `username`
- `idx_email` sur `email`

#### ⚠️ Statut :
Cette table est en cours de dépréciation. Les données sont migrées vers la table `membres` via le script `migrate_users_to_membres.py`.

---

## 🎯 Table `signalements` (BIQ)

**Objectif** : Gestion des signalements BIQ pour la protection des droits

#### Structure des colonnes :

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique du signalement |
| `title` | VARCHAR(255) | NOT NULL | Titre du signalement |
| `type` | VARCHAR(100) | NOT NULL | Type (abus_dpj, falsification, violation_droits, negligence, autre) |
| `description` | TEXT | NOT NULL | Description détaillée du signalement |
| `contact` | VARCHAR(255) | | Contact pour suivi (email/téléphone) |
| `status` | VARCHAR(50) | DEFAULT 'nouveau' | Statut (nouveau, en_cours, resolu) |
| `priority` | VARCHAR(20) | DEFAULT 'normale' | Priorité (normale, haute, critique) |
| `assigned_to` | INT | FOREIGN KEY → membres(id) | WhiteHat assigné au traitement |
| `resolution` | TEXT | | Description de la résolution |
| `created_by` | INT | FOREIGN KEY → membres(id) | ID du membre créateur |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date de création |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Date de modification |

#### Index :
- `idx_type` sur `type`
- `idx_status` sur `status`
- `idx_priority` sur `priority`
- `idx_created_by` sur `created_by`
- `idx_assigned_to` sur `assigned_to`
- `idx_created_at` sur `created_at`

#### Clés étrangères :
- `created_by` REFERENCES `membres(id)` ON DELETE SET NULL
- `assigned_to` REFERENCES `membres(id)` ON DELETE SET NULL

#### Utilisation :
- **Signalements citoyens** : Dépôt et suivi des cas d'abus
- **Workflow WhiteHat** : Assignment et traitement par les administrateurs
- **Traçabilité** : Historique complet des actions et résolutions
- **Priorisation** : Classification par type et urgence

---

## 🔄 Scripts de migration et maintenance

### Scripts disponibles :

1. **`create_mysql_schema.py`** : Création initiale du schéma et des tables
2. **`create_mediatheque_table.py`** : Création de la table médiathèque avec données d'exemple
3. **`create_signalements_table.py`** : Création de la table signalements BIQ
4. **`create_admin_biq.py`** : Création d'utilisateurs test pour BIQ
5. **`migrate_users_to_membres.py`** : Migration de `users` vers `membres`
6. **`cleanup_migration.py`** : Nettoyage post-migration

### Ordre d'exécution recommandé :

```bash
# 1. Création du schéma principal
python create_mysql_schema.py

# 2. Ajout de la médiathèque
python create_mediatheque_table.py

# 3. Ajout des signalements BIQ
python create_signalements_table.py

# 4. Création d'utilisateurs test
python create_admin_biq.py

# 5. Migration des utilisateurs (si nécessaire)
python migrate_users_to_membres.py

# 6. Nettoyage (optionnel)
python cleanup_migration.py
```

---

## 🔐 Sécurité et bonnes pratiques

### Authentification :
- Mots de passe hashés avec `pbkdf2:sha256`
- Codes de confirmation temporaires pour l'activation
- Sessions sécurisées avec contrôle des droits admin

### Protection des données :
- Conformité RGPD avec champ de consentement
- Validation des uploads avec whitelist d'extensions
- Limitation de taille des fichiers joints

### Performance :
- Index optimisés pour les requêtes fréquentes
- Moteur InnoDB pour les transactions ACID
- Gestion des compteurs (vues, membres) en temps réel

---

## 📈 Évolution future

### Améliorations prévues :
- Migration complète vers la table `membres`
- Ajout de tables pour les votes et propositions
- Système de notifications et alertes
- Intégration blockchain pour la traçabilité

### Tables en projet :
- `propositions` : Gestion des propositions citoyennes
- `votes` : Système de vote électronique sécurisé
- `notifications` : Alertes et communications
- `logs` : Audit trail des actions administratives

---

*Documentation générée le {{ date.today() }} - UMan API v2024*
