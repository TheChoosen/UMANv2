PRD — Bureau de l’Indépendance du Québec (BIQ)

Version : 1.0
Date : 2025-08-25

1. Contexte et objectif

Ce document décrit le périmètre fonctionnel, les routes, les modèles de données et les exigences non-fonctionnelles de la plateforme Bureau de l’Indépendance du Québec (BIQ).
L’objectif est de fournir une infrastructure citoyenne, numérique et transparente, permettant :

la défense des droits (notamment face aux abus institutionnels, ex. DPJ),

la mobilisation citoyenne,

l’audit et la reddition de comptes en temps réel,

le développement d’une économie sociale territoriale.

Sources et inspirations :

Écosystème biq.quebec (landing, forums, signalements, alliances).

Documentation citoyenne, manifestes, rapports d’enquête sociale et économique.

2. Valeur produit

Offrir une plateforme souveraine de signalement, transparence et audit.

Donner aux familles et citoyens un espace pour témoigner, se former et se mobiliser.

Permettre une gestion communautaire (alliances, cercles, parrainages, forums).

Créer un cadre de reddition de comptes et de mobilisation citoyenne (alliances WhiteHats, alliances citoyennes).

3. Utilisateurs et rôles

Visiteur public : consulte manifeste, rapports publics, actualités, vidéos.

Membre citoyen : profil, signalements, participation aux forums, adhésion à l’Alliance.

Familles impactées : dépôt de dossiers, suivi des signalements, accès médiation.

WhiteHats : supervision, audit des cas, inspections, formation.

Admin BIQ : gestion des membres, médiathèque, dossiers, décisions, formations.

4. Parcours clés (user stories)

En tant que visiteur, je consulte le manifeste, rapports et actualités.

En tant que citoyen, je m’inscris (/biq/register) et rejoins l’Alliance.

En tant que membre, je me connecte (/biq/login) et accède à mon tableau de bord (/biq/profil).

En tant que famille, je dépose un dossier de signalement via /biq/signalement.

En tant que WhiteHat, je valide/inspecte un dossier et rédige un rapport.

En tant qu’admin, je gère membres, signalements, médiathèque et communications.

5. Routes / Endpoints (prévisionnel)

Site public / BIQ

GET /biq → landing (manifeste, actualités, valeurs).

GET/POST /biq/login → connexion.

GET/POST /biq/register → inscription.

GET /biq/profil → tableau de bord membre.

GET/POST /biq/signalement → signalement citoyen.

GET /biq/mediatheque → médiathèque publique.

Admin (console citoyenne BIQ)

GET /biq/admin → dashboard admin.

GET/POST /biq/admin/users → gestion des membres.

GET/POST /biq/admin/users/<id>/edit → édition membre.

GET /biq/admin/signalements → suivi signalements (liste, état, audit).

GET /biq/admin/mediatheque → gestion médias.

API JSON : /biq/admin/signalements/<id>/validate, /biq/admin/mediatheque/<id>/toggle, /biq/admin/signalements/<id>/audit

6. Principales pages et composants

base.html : layout global, navigation, modals (signalement, manifeste, formation).

index.html : landing (valeurs BIQ, alliances, CTA rejoindre).

login.html / register.html : authentification.

profil.html : dashboard membre (forums, signalements déposés, suivi).

signalement.html : formulaire dépôt de cas (familles).

mediatheque.html : ressources publiques (rapports, vidéos, documents).

admin.html : console citoyenne BIQ (membres, signalements, médias, décisions).

admin/users.html : gestion des membres.

admin/signalements.html : audit des dossiers.

admin/media_form.html : création/édition média.

7. Modèles de données (essentiel)

membres

id, username, prenom, nom, email, password_hash, is_admin, roles, region, created_at

signalements

id, membre_id, type (abus DPJ, falsification, autre), description, preuves (URL/document), statut (en attente, validé, en médiation, clôturé), whitehat_id, created_at, updated_at

mediatheque

id, title, description, file_url, category, is_public, is_featured, views_count, created_at

alliances

id, type (WhiteHats, citoyenne, canadienne), membres, created_at

8. CRUD / comportements

Signalements : dépôt par membre, validation par WhiteHat, suivi du statut.

Membres : inscription, édition profil, admin CRUD complet.

Médiathèque : ajout/édition/suppression de ressources, toggle visibilité.

Alliances : enregistrement et suivi des alliances citoyennes / WhiteHats.

9. Contraintes et exigences non-fonctionnelles

Authentification sécurisée (bcrypt/argon2 + sessions).

CSRF protection pour tous formulaires.

Accessibilité (WCAG) : contrastes, aria, responsive.

Auditabilité : logs complets des actions (citoyens, WhiteHats, admins).

Internationalisation : FR en défaut, prévoir i18n.

10. UX / Validation

Inscription : email unique, mot de passe min 8, confirmation.

Signalement : description obligatoire, preuves optionnelles (PDF/img).

Admin : modification mot de passe optionnelle, rôles attribuables.

11. Tests recommandés

Unitaires : /biq/login, /biq/register, /biq/signalement.

Admin : /biq/admin/users, /biq/admin/signalements.

Intégration : dépôt signalement → validation par WhiteHat → statut mis à jour.

E2E : inscription → dépôt signalement → suivi dossier.

12. Risques et dépendances

Risque légal : contestations institutionnelles → nécessitera appui juridique.

Dépendance forte aux WhiteHats (audit, validation).

Risque de sécurité (cyberattaques) → infrastructure sécurisée obligatoire.

13. Backlog / Prochaines actions

Implémenter dépôt et suivi des signalements.

Développer admin console pour gestion signalements.

Intégrer médiathèque (rapports, vidéos, documents).

Mettre en place module alliances citoyennes / WhiteHats.

Campagne d’inscription citoyenne sur biq.quebec.

14. Mapping exigences → fichiers

Auth : login.html, register.html, routes /biq/login, /biq/register.

Profil : profil.html, route /biq/profil.

Signalement : signalement.html, route /biq/signalement.

Médiathèque : mediatheque.html, routes publiques + admin CRUD.

Admin : admin.html, admin/users.html, admin/signalements.html.

15. Annexes

Les signalements doivent être traçables et audités en temps réel.

Les WhiteHats agissent comme superviseurs indépendants.

La plateforme BIQ devient le pivot numérique de l’autonomie citoyenne au Québec.