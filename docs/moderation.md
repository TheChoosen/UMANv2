# Politique de modération — République du Kwébec

Objectif
- Définir les règles de modération et le workflow de publication pour la plateforme RDKQ.

Principes
- Favoriser la liberté d'expression tout en refusant les contenus illégaux et les appels à la violence.
- Transparence: publier les règles et le processus d'appel.
- Proportionnalité: sanctions graduelles, journalisation et droit d'appel.

Règles générales
- Contenu interdit: appels à la violence, instruction pour commettre des délits, pornographie infantile, doxxing.
- Contenu restreint: discours haineux — évaluation au cas par cas; les auteurs seront notifiés et un délai d'édition proposé.

Workflow de modération (MVP)
1. Soumission via `/rdkq/participer` ou formulaire créateur.
2. Filtrage automatique: détections basiques (mots-clés, extensions interdites).
3. Quarantaine: si suspect, contenu mis en quarantaine et signalé aux modérateurs.
4. Validation humaine: décision (approuver / demander modification / rejeter).
5. Publication & horodatage: si approuvé, le contenu est publié et horodaté.
6. Audit: conserver journal d'action (qui, quand, motif).

Recours
- Procédure d'appel: formulaire d'appel public, délai 14 jours.

Notes techniques
- Intégrer champs de métadonnées: submitter_id, provenance, hash du fichier.
- Stocker décisions et raisons dans la table `moderation_actions` pour audit.
