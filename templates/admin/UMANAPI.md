Qu’est-ce que la cyberdémocratie ?

La cyberdémocratie est l’usage structuré du numérique pour proposer, délibérer, décider et exécuter des actions collectives de manière inclusive, traçable et vérifiable. Elle ne se limite pas au vote en ligne : elle couvre tout le cycle décisionnel—de l’idéation à la preuve d’exécution—avec des règles claires, des garanties techniques (sécurité, cryptographie, audit), et une gouvernance éthique.

Transparence & redevabilité : pourquoi c’est central

Transparence : rendre compréhensibles et visibles (aux ayants droit) les informations et justifications à chaque étape.

Redevabilité : rendre attribuables les décisions et leurs suites (qui décide quoi, pourquoi, avec quels effets), et offrir des voies de contestation et de correction.

Dans un système crédible, les deux sont indissociables : on voit le processus (transparence) et on peut agir en cas d’écart (redevabilité).

« Traçabilité complète » : ce que cela veut dire, concrètement

UMan API doit enregistrer un journal de bout en bout pour quatre blocs : Propositions, Débats, Votes, Résultats/Exécution.

1) Propositions

Identité & origine : auteur, mandats/délégations, conflit d’intérêts déclaré.

Versions : chaque modification = nouvelle révision, horodatée, avec diff.

Justificatifs : pièces jointes (PDF, médias), sources, références.

Parcours : états (Brouillon → En revue → Publique → Clôturée), règles de passage.

Empreintes : hash (SHA-256) de chaque version + signature serveur (ou clés orga).

2) Débats / Délibération

Messages liés à la proposition/version, rôle de l’intervenant (membre, expert, élu).

Modération : règles anti-captation (limites par tour, anti-spam), décisions de modération motivée & horodatée.

Synthèses : clôture de phase avec résumé officiel et liens vers contributions.

3) Votes

Type de scrutin : oui/non/abstention, préférentiel (classement), notation, jugements, quorum.

Fenêtre de vote : ouverture/fermeture, fuseau, règles d’éligibilité.

Vérifiabilité : preuve cryptographique (voir plus bas), bulletins anonymisés, registre scellé.

Observabilité : journaux d’événements (ouverture urne, scellé, scellement du décompte).

4) Résultats & Exécution

Tally (dépouillement) : méthode, paramètres (quorum, seuils), fichier de preuves.

Décision formelle : texte de décision + base légale/règlementaire interne.

Plan d’action : responsables, jalons, indicateurs, budget si applicable.

Preuves d’exécution : PV, photos, commits, bons de travail—chaînées à la décision.

Rétro-évaluation : indicateurs atteints / non atteints, raisons, actions correctives.

Architecture de confiance (piliers techniques)

Identité & droits

MFA/SSO, rôles (Membre, Manager, Rapporteur, Auditeur, Observateur), mandats/délégations traçables et révocables.

Journal immuable

Append-only log horodaté (NTP), hash chaînés (Merkle tree) pour versions, débats, bulletins, résultats.

Signatures

Signatures numériques des objets clés (versions, décisions, procès-verbaux).

Scellement temporel

Time-stamping (serveur de temps de confiance), ancre périodique (hash racine) dans un registre externe si souhaité.

Export & audit

Exports CSV/JSON/PDF scellés, API read-only pour auditeurs (journaux + preuves).

Observabilité

Tableaux audit (erreurs, tentatives d’accès, anomalies), alertes, conservation légale.

Transparence vs secret du vote : concilier les deux

Séparation stricte des données d’identité et des bulletins.

Chiffrement de bout en bout des bulletins, avec seuil de déchiffrement (threshold crypto).

Anonymisation via mixnets ou chiffrement homomorphe (selon modèle) ; journal public des preuves (sans PII).

Vérifiabilité individuelle (reçu non-dévoilant) et audits à risque limité (Risk-Limiting Audits) après le décompte.

Publication des paramètres du scrutin (quorum, règles), des hash et preuves du tally.

Gouvernance : rôles, règles, garde-fous

Charte de participation (respect, pertinence, anti-abus), politique de conflits d’intérêts (déclaration/recusation), procédure de contestation (délai, instance, preuve).

Cadre de modération documenté : motifs, délais, possibilité d’appel.

Calendrier et ordre du jour publics (selon droits), avec historique consultable.

Versioning des règles : toute modification de règle elle-même est consignée.

Indicateurs (KPI) « Transparence & Redevabilité »

Taux de complétion de traçabilité (propositions/votes/décisions avec preuves liées)

Délai moyen par phase (débat, vote, exécution)

% de décisions exécutées vs planifiées, écart et actions correctives

Indice de participation (diversité des rôles, rétention, délégations actives)

Taux de contestations et décisions corrigées (qualité & confiance)

NPS/CSAT sur la clarté des décisions et l’accès aux informations

Modèle de données minimal (simplifié, esprit UMan)

proposition(id, auteur_id, titre, état, hash_courant, …)

proposition_version(id, proposition_id, contenu, auteur_id, horodatage, hash, signature)

justificatif(id, proposition_id/version_id, url, type, hash)

debate_message(id, proposition_id/version_id, auteur_id, contenu, horodatage, modération_statut, motif)

scrutin(id, proposition_id/version_id, type, quorum, fenetre_ouverture/fermeture, params)

bulletin(id, scrutin_id, payload_chiffre, preuve, horodatage)

tally(id, scrutin_id, méthode, résultat_json, preuve_hash, signature)

decision(id, proposition_id/version_id, texte, base_regle, signature, horodatage)

action_item(id, decision_id, responsable_id, échéance, statut, preuve_lien)

audit_log(id, entité, entité_id, action, acteur_id, horodatage, ip, hash_chaîne)

delegation(id, délégant_id, délégué_id, domaine, début, fin, révocable, preuve)

Flux de bout en bout (états)

Brouillon → 2. Revue (pairs/experts) → 3. Public (débat) → 4. Vote (fenêtre) →

Dépouillement (preuves) → 6. Décision (publication) → 7. Exécution (plan d’action) → 8. Preuves (rendu) → 9. Rétro-évaluation (KPI & corrections).

Chaque transition est journalisée, horodatée, hashée et, si critique, signée.

Sécurité & conformité (survol)

Protection des données : minimisation, pseudonymisation, cloisonnement (PII vs bulletins).

Conformité : Loi 25 (Québec) / RGPD (UE) — base légale, DPIA, registre des traitements.

Sécurité : durcissement (chiffrement at-rest/in-transit), gestion clés, sauvegardes, PRA/PCA.

Rétention : politiques par type de données (bulletins, logs, pièces), purge certifiée.

Audit externe : accès read-only aux preuves + exports scellés.

UX & pédagogie (rendre la traçabilité visible)

Timeline complète par proposition (versions, débats, votes, décisions, exécution).

Fiche de décision : Contexte → Justifications → Règles du scrutin → Résultat → Plan d’action → Preuves.

Badges de complétude (traçabilité OK/partielle/manquante).

Dossiers exportables (PDF/ZIP) scellés avec sommaire des preuves.

Tooltips pédagogiques (quorum, méthodes de vote, reçus cryptographiques).

Checklist d’implémentation UMan (12 points)

MFA/SSO + rôles & mandats (délégation traçable).

Versioning immutabilisé (hash/signature) pour propositions & règles.

Journal append-only horodaté (chaîné).

Modération motivée & appel.

Scrutins paramétrables (types, quorum, fenêtres).

Bulletins chiffrés/anonymisés + reçus non-dévoilants.

Tally vérifiable + publication des preuves.

Décisions signées + plan d’action lié.

Preuves d’exécution chaînées (hash médias/docs).

Exports scellés + API auditeurs.

Dashboards KPI Transparence & Redevabilité.

Politiques légales (DPIA, rétention, audit externe).