# Issue: email-server (Medium)

Résumé
- Mettre en place l'envoi d'emails pour confirmations/notifications en production.

Objectifs
- Utiliser Resend si configuré, sinon SMTP relay.
- Fallback en staging -> fichier; dev -> console.

Critères d'acceptation
- Emails envoyés en staging enregistrés dans `tmp/`.
- En prod, emails envoyés via provider configuré.

Tâches
- [ ] Vérifier intégration Resend.
- [ ] Documenter variables d'environnement (`RESEND_API_KEY`, `SMTP_*`).
- [ ] Ajouter tests d'intégration (mock provider).

Labels: backend, medium
