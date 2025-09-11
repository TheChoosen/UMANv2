Parfait — voici un **cahier des charges (fonctionnel + technique) pour UMAN API** afin de livrer, en **SaaS multitenant**, l’équivalent des modules clés de Decidim. J’ai audité la page “Modules” et la documentation officielle pour garantir la parité fonctionnelle et les bons termes (espaces participatifs vs composants) ([decidim.org][1], [docs.decidim.org][2]).

# 1) Périmètre & objectifs

* **But** : offrir une plateforme participative configurable par organisations (tenants), regroupant des **espaces participatifs** (Processus, Assemblées, Consultations, Initiatives, Conférences) et des **composants** (Propositions, Réunions, Budgets, Sondages, Débats, Commentaires, Sortitions, Accountability, Pages/Blog). Les “espaces” structurent le contexte, les “composants” ajoutent des mécanismes de participation ([docs.decidim.org][3]).
* **Référence de parité** (officielle) : Proposals, Page/Blog, Meetings, Budgets, Surveys, Accountability, Debates, Sortitions (+ Comments, Verifications, System) ([decidim.barcelona][4], [decidim.org][1]).
* **API & Open Data** : exposer une **API GraphQL** (lecture) et des **exports Open Data** programmés, comme dans Decidim (lecture publique, docs auto-générées) ([docs.decidim.org][5]).

# 2) Rôles & gestion des accès (SaaS)

* **Visiteur** (lecture publique), **Participant** (inscrit), **Participant vérifié** (actions sensibles), **Modérateur**, **Admin d’espace**, **Admin d’organisation (tenant)**, **Admin système (SaaS)** — modèle aligné sur la doc et le moteur **System** pour le multi-tenant ([decidim.org][1]).
* **Vérifications / autorisations** : preuves via **SMS**, **document d’identité**, **carnet/census organisationnel**, etc., modulaires et extensibles ([docs.decidim.org][6]).

# 3) Exigences par module (MVP + parité)

## Espaces participatifs

* **Processus participatifs** : phases configurables (ex. sondage → propositions → réunions → priorisation/vote) ; calendrier, permissions par phase ([docs.decidim.org][7]).
* **Assemblées** : organes pérennes sans phases (membres, réunions, catégories, composants activables) ([docs.decidim.org][8]).
* **Consultations** : espace dédié à des questions de vote/référendum (proxy d’e-voting), questions/réponses, période de vote, résultats ([decidim.org][1]).
* **Initiatives** : initiatives citoyennes avec collecte de signatures/soutiens selon règles ; suivi du statut ([docs.decidim.org][3]).
* **Conférences** : agrégation d’**événements/réunions** avec programme et inscriptions ([decidim.org][1]).

## Composants

* **Propositions** : créer, commenter, soutenir, voter selon règles ; filtres, catégories, pièces jointes ; modération ([docs.decidim.org][9]).
* **Commentaires** : fil de discussion commun à plusieurs ressources, notifications et préférences utilisateur ([decidim.org][1], [docs.decidim.org][10]).
* **Débats** : discussions sans vote obligatoire ; clôture avec conclusions/synthèse ([docs.decidim.org][11]).
* **Réunions (Meetings)** : création (admin ou participants), agenda, inscriptions/capacité, procès-verbal, sondages de réunion, présentiel ou en ligne ([docs.decidim.org][12]).
* **Budgets participatifs** : projets, règles de vote (quota, panier jusqu’à un montant, etc.), un ou plusieurs budgets par espace, résultats agrégés ([docs.decidim.org][13]).
* **Sondages/Surveys** : questionnaires configurables, collecte et export des réponses ([decidim.org][1]).
* **Sortitions** : tirage aléatoire auditable parmi des propositions/catégories ([decidim.org][1]).
* **Accountability (Suivi d’exécution)** : publier des **Résultats/Projets**, lier aux propositions/budgets/réunions ; états d’avancement et jalons ([docs.decidim.org][14]).
* **Pages/Blog** : pages statiques et actualités par espace ([docs.decidim.org][2]).

**Extensions utiles (optionnel)** :

* **Notifications & Newsletters** (modèles, opt-in, alertes échéances) ([docs.decidim.org][10]).
* **Intégrations** : **Jitsi** pour visioconférences ; **Peertube** pour vidéo ; **cartographie**/GEO ; anti-spam/antivirus communautaires (références disponibles) ([decidim.org][1]).
* **API GraphQL** (lecture) exposée par tenant ; possibilité d’extension “write” via module dédié (ex. **apiext** avec JWT) si besoin B2B/interopération ([docs.decidim.org][5], [GitHub][15]).
* **Open Data** : exports réguliers via tâches planifiées pour transparence et réutilisation des données ([docs.decidim.org][16]).

# 4) Exigences transverses

* **Multitenant (SaaS)** : isolation stricte des données par **Organisation** ; panneau “System” pour gérer organisations, domaines, branding et quotas ([decidim.org][1]).
* **I18n & accessibilité** : FR/EN par défaut ; WCAG 2.2 AA ; formats régionaux (ex. PTP module cite les formats NA) ([decidim.org][1]).
* **Sécurité & conformité** : OAuth2/OIDC, MFA, RGPD + Loi 25 (Québec), **audit log** des actions sensibles, anti-spam, antivirus sur fichiers publics (modules existent) ([decidim.org][1]).
* **Observabilité** : métriques d’engagement, traces, journaux ; **comparative stats** via API GraphQL d’instances publiques si souhaité ([decidim.org][1]).
* **Performance** : pagination/filtrage, indexation recherche, cache CDN public, Web Vitals.
* **Modération & gouvernance** : règles de contenu, workflows de modération, signalements.

# 5) Modèle de données (vue haut niveau)

Entités principales : **Organisation (tenant)**, **Espace** (Processus, Assemblée, Consultation, Initiative, Conférence), **Composant** (Propositions, Meetings, Budgets, Surveys, Debates, Sortitions, Accountability, Pages/Blog, Comments), **Ressources** (Proposal, Meeting, ProjectBudget, Vote, Survey, Response, Debate, Sortition, Result, Page/BlogPost, Comment, Attachment), **Taxonomies/Scopes**, **Utilisateur**, **Groupe**, **Rôle**, **Vérification**, **Notification**, **Newsletter** — aligné avec la séparation espaces/composants et l’API publique ([docs.decidim.org][17]).

# 6) Architecture cible

* **Kernel + modules** : architecture “plugin” où chaque composant est un module activable par espace (contrat de composant), comme dans Decidim ([docs.decidim.org][18]).
* **API Gateway** (GraphQL lecture, REST/GraphQL write optionnel), **Service d’auth**, **Service de notifications**, **Service de fichiers**, **Service Open Data**, **Back-office admin** (System + Organisation + Espace).
* **Intégrations** : SMTP/Email, SMS (vérifications), **Jitsi/Peertube**, webhooks.
* **Tâches planifiées** : exports Open Data quotidiens, rappels/notifications programmés ([docs.decidim.org][16]).

# 7) User stories & critères d’acceptation (extraits)

* **En tant qu’Admin d’organisation**, je crée un **Processus** avec 4 phases (Sondage → Propositions → Réunions → Budgets), chacune avec droits spécifiques ; **DoD** : le front affiche la phase active et masque les composants non autorisés, comme décrit pour les processus par étapes ([docs.decidim.org][7]).
* **En tant que Participant**, je **crée une proposition**, je la **commente** et **je la soutiens** ; **DoD** : états, compteurs de soutiens, signalement/modération actifs ([docs.decidim.org][9]).
* **En tant qu’Admin**, je **paramètre un Budget** avec règle “jusqu’à X \$” ; le système calcule la sélection valide et publie les résultats ([docs.decidim.org][13]).
* **En tant que Modérateur**, je **clôture un Débat** avec conclusions ; celles-ci sont visibles en front et via API ([docs.decidim.org][11]).
* **En tant qu’Admin**, j’active **Accountability** et lie des résultats aux propositions financées ; les statuts sont consultables publiquement ([docs.decidim.org][14]).
* **En tant qu’Admin système**, je **crée un tenant** et attribue un domaine + branding ; les admins org peuvent ensuite gérer leurs espaces (fonction “System”) ([decidim.org][1]).
* **En tant que Participant vérifié**, je **vote** dans une Consultation ; les vérifications (SMS/doc) sont requises avant le vote ([docs.decidim.org][6]).

# 8) API & Données

* **GraphQL publique (lecture)** par organisation, docs auto-générées (`/api/docs`) ; pagination/filtrage par types (proposals, meetings, budgets, etc.) ([docs.decidim.org][5], [decidim.barcelona][4]).
* **Open Data** : export quotidien automatisé (cron) ; formats CSV/JSON ; catalogue par dataset (propositions, votes, budgets, résultats) ([docs.decidim.org][16]).
* **(Optionnel)** API “**write**” sécurisée (mutation) avec **JWT** d’applications partenaires, sur périmètres limités (ex. créer propositions) via un module d’extension type **apiext** ([GitHub][15]).

# 9) Roadmap de réalisation (6 sprints)

* **S1 — Socle SaaS & System** : multi-tenant, rôles, branding, i18n, RGPD/Loi 25, API GraphQL lecture.
* **S2 — Espaces & navigation** : Processus, Assemblées ; Pages/Blog ; Comments ; Notifications de base.
* **S3 — Propositions & Débats** : création/édition, modération, signalements, recherche/filtre, flux d’activité.
* **S4 — Meetings** : agenda, inscriptions, PV ; intégration Jitsi/Peertube optionnelle. ([docs.decidim.org][12])
* **S5 — Budgets & Surveys** : règles de vote, panier, exports ; sondages administrables. ([docs.decidim.org][13])
* **S6 — Sortitions & Accountability & Open Data** : tirages, suivi d’exécution, exports planifiés ; newsletters. ([decidim.org][1], [docs.decidim.org][14])

# 10) NFR (exigences non-fonctionnelles)

* **Accessibilité** WCAG 2.2 AA ; **perf** (TTFB <200 ms cache, LCP <2.5 s public), **SLO** 99.9% (hors maintenances).
* **Sécurité** : OWASP ASVS L2, gestion secrets, durcissement headers, CSRF, rate limiting, chiffrage au repos & en transit.
* **Interopérabilité** : SSO OIDC/SAML, webhooks, taxonomies/scopes, export complet du tenant.

---

Si tu veux, je peux convertir ce cahier de charges en **PRD détaillé** (avec épics/stories et critères d’acceptation exhaustifs) ou en **backlog Jira** prêt à importer.

[1]: https://decidim.org/modules/ "Modules | Decidim"
[2]: https://docs.decidim.org/en/develop/admin/components.html?utm_source=chatgpt.com "Components"
[3]: https://docs.decidim.org/en/develop/features/participatory-spaces.html?utm_source=chatgpt.com "Participatory spaces"
[4]: https://www.decidim.barcelona/api/docs?utm_source=chatgpt.com "decidim.barcelona - API Documentation"
[5]: https://docs.decidim.org/en/develop/develop/api.html?utm_source=chatgpt.com "API"
[6]: https://docs.decidim.org/en/develop/customize/authorizations.html?utm_source=chatgpt.com "Authorizations"
[7]: https://docs.decidim.org/en/develop/admin/spaces/processes.html?utm_source=chatgpt.com "Participatory processes"
[8]: https://docs.decidim.org/en/develop/admin/spaces/assemblies.html?utm_source=chatgpt.com "Assemblies"
[9]: https://docs.decidim.org/en/develop/admin/components/proposals.html?utm_source=chatgpt.com "Proposals"
[10]: https://docs.decidim.org/en/develop/admin/features/participant_actions/notifications.html?utm_source=chatgpt.com "Notifications"
[11]: https://docs.decidim.org/en/develop/admin/components/debates.html?utm_source=chatgpt.com "Debates"
[12]: https://docs.decidim.org/en/develop/admin/components/meetings.html?utm_source=chatgpt.com "Meetings"
[13]: https://docs.decidim.org/en/develop/admin/components/budgets.html?utm_source=chatgpt.com "Budgets"
[14]: https://docs.decidim.org/en/develop/admin/components/accountability.html?utm_source=chatgpt.com "Accountability"
[15]: https://github.com/City-of-Turku/decidim-module-apiext?utm_source=chatgpt.com "City-of-Turku/decidim-module-apiext"
[16]: https://docs.decidim.org/en/develop/develop/open-data.html?utm_source=chatgpt.com "Open Data"
[17]: https://docs.decidim.org/en/develop/features/components.html?utm_source=chatgpt.com "Components"
[18]: https://docs.decidim.org/en/develop/develop/components.html?utm_source=chatgpt.com "Components"
