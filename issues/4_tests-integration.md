# Issue: tests-integration (Medium)

Résumé
- Ajouter tests d'intégration CI pour le flux formulaire -> upload -> email.

Objectifs
- Garantir que les workflows critiques fonctionnent en CI.

Critères d'acceptation
- CI exécute tests d'intégration et renvoie vert pour PR.

Tâches
- [ ] Ajouter pytest et fixtures pour test client.
- [ ] Ecrire tests pour POST `/rdkq/participer` (avec et sans fichier).
- [ ] Intégrer tests dans pipeline CI.

Labels: testing, ci, medium
