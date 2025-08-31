# Issue: upload-scan (High)

Résumé
- Intégrer scan antivirus/antimalware pour uploads avant persistance.

Objectifs
- Bloquer fichiers malicieux.
- Mettre en quarantaine les fichiers suspects.

Critères d'acceptation
- Uploads passent par un service de scan (mock en staging).
- Suspicious files moved to quarantine and admin alerted.

Tâches
- [ ] Ajouter job d'analyse (sync/async).
- [ ] Implémenter quarantaine et notifications.
- [ ] Documenter le processus.

Labels: security, infra, high
