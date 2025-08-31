# RGPD / Protection des données — République du Kwébec

But
- Décrire comment les utilisateurs peuvent demander export et suppression de leurs données.

Procédure de suppression (MVP)
1. Requête utilisateur via formulaire (email + preuve d'identité simple).
2. Vérification manuelle (admin) pour éviter suppression abusive.
3. Suppression logique: marquer `deleted_at` sur enregistrements et supprimer fichiers chiffrés après période de rétention.
4. Export: fournir un package ZIP chiffré contenant les métadonnées et fichiers attachés (si demandé).

Rétention
- Métadonnées opérationnelles: 90 jours par défaut.
- Données légales obligatoires: conservées selon exigences locales (documenter).

Consentement
- Tous les formulaires doivent stocker la valeur RGPD (cbRGPD) et horodater le consentement.

Responsable et contact
- DPO / Contact: dpo@rdkq.example.org (placeholder)

Notes techniques
- Utiliser clé de chiffrement gérée par secret store.
- Logs d'audit séparés et immuables pour actions critiques.
