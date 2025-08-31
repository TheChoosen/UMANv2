# PRD — Re-Publique Kwébec (RDKQ)

Version: 1.0
Date: 2025-08-25

## 1. Contexte et objectif
Ce document décrit le périmètre fonctionnel, les routes, les modèles de données et les exigences non-fonctionnelles pour la plateforme Re-Publique Kwébec (RDKQ), telle qu'implémentée aujourd'hui dans les templates et routes du projet.

Sources analysées (templates clés):
- `templates/RepubliqueduKwebec/base.html` (layout, modals, navigation)
- `templates/RepubliqueduKwebec/index.html` (landing, manifeste, thèmes)
- `templates/RepubliqueduKwebec/login.html` (connexion)
- `templates/RepubliqueduKwebec/register.html` (inscription)
- `templates/RepubliqueduKwebec/profil.html` (profil / dashboard)
- `templates/RepubliqueduKwebec/registre.html` (registre foncier modal / page)
- `templates/RepubliqueduKwebec/admin.html` (admin dashboard single page)
- `templates/RepubliqueduKwebec/admin/users.html` (liste utilisateurs)
- `templates/RepubliqueduKwebec/admin/user_form.html` (édition utilisateur)
- `templates/RepubliqueduKwebec/admin/mediatheque.html` (admin médiathèque)
- `templates/RepubliqueduKwebec/admin/media_form.html` (form média)

## 2. Valeur produit
- Offrir une plateforme souveraine de participation (manifeste, médiathèque, registre foncier).
- Permettre la gestion communautaire (membres, cercles, rôles, décisions) via une console admin.
- Fournir des mécanismes transparents de financement et gouvernance (concepts de «Smart Contracts»).

## 3. Utilisateurs et rôles
- Visiteur public: consulte manifeste, médiathèque publique, registres exposés.
- Membre (souverain): profil, publications, participation, accès aux cercles.
- Admin: gestion des membres, médiathèque, décisions, rôles, adhésions, publications.

## 4. Parcours clés (user stories)
- En tant que visiteur, je consulte le manifeste et la médiathèque publique.
- En tant que visiteur, je m'inscris (formulaire `/rdkq/register`) et deviens membre.
- En tant que membre, je me connecte (`/rdkq/login`) et accède à mon profil (`/rdkq/profil`).
- En tant qu'admin, je liste les membres (`/admin/users`) et j'édite un membre (`/admin/users/<id>/edit`).
- En tant qu'admin, j'ajoute/modifie des médias via l'admin médiathèque (`/rdkq/admin/mediatheque` + forms).

## 5. Routes / Endpoints (implémentation actuelle)
- Site public / RDKQ
	- GET `/rdkq` -> `RepubliqueduKwebec/index.html`
	- GET/POST `/rdkq/login` -> `RepubliqueduKwebec/login.html`
	- GET/POST `/rdkq/register` -> `RepubliqueduKwebec/register.html`
	- GET `/rdkq/profil` -> `RepubliqueduKwebec/profil.html`
	- GET `/rdkq/registre` -> `RepubliqueduKwebec/registre.html`

- Admin (compatibility and new routes)
	- GET/POST `/admin/users` -> renders users list (routes in `app.py`)
	- GET/POST `/admin/users/<id>/edit` -> edit user form (added)
	- GET `/rdkq/admin` -> `RepubliqueduKwebec/admin.html`
	- GET `/rdkq/admin/mediatheque` -> `RepubliqueduKwebec/admin/mediatheque.html`
	- API: `/rdkq/admin/mediatheque/data`, `/rdkq/admin/mediatheque/<id>/toggle-visibility`, `/rdkq/admin/mediatheque/<id>/toggle-featured`, `/rdkq/admin/mediatheque/<id>` (DELETE)

## 6. Principales pages et composants (mapping fichiers -> responsabilités)
- `base.html`: navigation, modals partagés (manifeste, médiathèque, registre, smart contract modal), styles globaux.
- `index.html`: landing, manifeste, thèmes, CTA (participer, registres, mediatheque modal).
- `login.html` / `register.html`: UX d'authentification et messages flash.
- `profil.html`: dashboard membre (cercles, publications, décisions, historique, settings/password change form).
- `registre.html`: description et CTA pour Registre Foncier.
- `admin.html`: admin dashboard SPA (JS-driven) avec tabs pour Membres / Cercles / Rôles / Décisions / Adhésions / Publications / Participations.
- `admin/users.html`: table listant membres pour admin (Éditer / Supprimer).
- `admin/user_form.html`: formulaire d'édition utilisateur (nom, email, rôle admin, changement mot de passe).
- `admin/mediatheque.html` + `admin/media_form.html`: CRUD médiathèque (list, stats, edition/creation média).

## 7. Modèles de données (essentiel)
- membres (table `membres`)
	- id, username, prenom, nom, email, password (hash), is_admin, roles, cercle_local, created_at
- mediatheque
	- id, title, description, image_url, document_url, category, author, is_public, is_featured, views_count, created_at, updated_at
- décisions, publications, cercles, adhesions, participations: schémas implicites présents dans l'admin (CRUD expected)

## 8. Comportement CRUD important
- Membres: lister (`admin/users.html`), éditer (`admin/user_form.html`), toggle admin flag, changer mot de passe (nouveau hash via `hash_code`).
- Médiathèque: list + stats, ajouter/éditer média (`admin/media_form.html`), toggle visibility/featured via API, supprimer.
- Admin dashboard (`admin.html`) propose formulaires clients JS pour créer/éditer membres, cercles, rôles, décisions — endpoints serveur doivent exister pour chaque action (à compléter si manquant).

## 9. Contraintes et exigences non-fonctionnelles
- Auth: les routes admin doivent vérifier `session['user_id']` et `session['is_admin']` (déjà présent dans `app.py`).
- Sécurité:
	- Actuel: mot de passe stocké via `hash_code` (SHA-256). Recommander: utiliser bcrypt/argon2 et ajouter salage + iterations.
	- Ajouter CSRF protection (Flask-WTF) pour formulaires POST.
	- Rate-limit login and sensitive endpoints.
- Accessibilité: boutons et labels présents; vérifier contrastes et attributs aria sur modals.
- Internationalisation: templates en français; prévoir structure i18n si nécessaire.
- Template locations: répertoire canonique pour RDKQ est `templates/RepubliqueduKwebec/` (les templates admin ont été déplacés ici).

## 10. UX / Validation
- Inscription: vérifier email unique, password min length 6, confirm match (front + backend).
- Edit user: password change optional — empty = keep existing; validate confirm and length.
- Média form: validate titre obligatoire, image_url either selected plaque ou URL valide.

## 11. Tests recommandés (smoke + unit)
- Tests unitaires pour routes critiques:
	- GET `/rdkq` rendu OK
	- POST `/rdkq/login` with valid/invalid credentials
	- GET `/admin/users` requires admin session
	- POST `/admin/users/<id>/edit` updates fields and password when provided
- Tests d'intégration:
	- Création/édition média via `/rdkq/admin/mediatheque/new` and `/.../<id>/edit` (API JSON)
- Tests E2E (optionnel): parcourir inscription -> login -> profil -> admin actions (using headless browser)

## 12. Risques et dépendances
- Dépendances: MySQL config via `config_mysql.py` ; s'assurer que DB schema (create_mysql_schema.py) est synchronisé.
- Risques: stockage mot de passe faible (SHA-256) ; modals et JS dépendants d'assets statiques (si manquants, UI cassée).

## 13. Backlog / Prochaines actions (priorisées)
1. Sécurité (haute): remplacer `hash_code` par bcrypt/argon2 et migrer les mots de passe existants.
2. CSRF (haute): ajouter protection pour tous les formulaires administratifs.
3. Compléter endpoints admin pour Cercles / Rôles / Décisions / Adhésions / Publications (API serveur) — `admin.html` contient le frontend mais certains endpoints pourraient manquer.
4. Tests automatisés: ajouter tests unitaires pour routes admin et auth.
5. Consolider templates: standardiser l'usage de `RepubliqueduKwebec/admin/...` dans `render_template` pour éviter ambiguïtés.
6. Documentation: ajouter README court expliquant where templates live and how to run locally (venv, port 8002).

## 14. Mapping exigences -> fichiers (bref)
- Auth/Login/Register/Profile: `login.html`, `register.html`, `profil.html`, `app.py` routes `/rdkq/login`, `/rdkq/register`, `/rdkq/profil`.
- Landing/Manifeste/Registre: `index.html`, `base.html` modals, `registre.html`.
- Admin CRUD Membres: `admin.html`, `admin/users.html`, `admin/user_form.html`, routes in `app.py` (`/admin/users`, `/admin/users/<id>/edit`).
- Médiathèque Admin: `admin/mediatheque.html`, `admin/media_form.html`, routes `/rdkq/admin/mediatheque*`.

## 15. Annexes rapides
- Décisions rapides:
	- Tous les templates admin doivent rester sous `templates/RepubliqueduKwebec/admin` (fait).
	- Standardiser `render_template('RepubliqueduKwebec/admin/xxx.html')` ou garder `render_template('admin/xxx.html')` si l'arborescence template loader fonctionne comme aujourd'hui.

---
Si tu veux, j'applique immédiatement (1) migration des mots de passe vers bcrypt (implémentation + migration helper), (2) ajout CSRF minimal, ou (3) mise à jour des appels `render_template` pour utiliser explicitement le préfixe `RepubliqueduKwebec/admin/` — dis ce que tu préfères et j'exécute la suite.

