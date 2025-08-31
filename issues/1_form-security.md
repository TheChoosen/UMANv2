# Issue: form-security (High)

Résumé
- Renforcer la sécurité du formulaire participatif `/rdkq/participer`.

Objectifs
- Valider et nettoyer tous les champs côté serveur.
- Prévenir injections XSS/SQL/path traversal.
- Limiter upload types et taille, ajouter vérification MIME.

Critères d'acceptation
- Tests unitaires couvrent validation du formulaire.
- Aucun input non-échappé renvoyé au client.
- Document de sécurité mis à jour.

Tâches
- [ ] Ajouter sanitation et whitelisting des champs.
- [ ] Ajouter vérification MIME et signature fichier.
- [ ] Ajouter tests unitaires.

Labels: security, backend, high
