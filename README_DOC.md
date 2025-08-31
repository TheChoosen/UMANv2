Documentation rapide des ressources Démocratie Directe

But
----
Fournir une page de documentation interne pour centraliser les fichiers fournis (mandats, glossaire, plan de match, images et vidéos).

Emplacement des assets
----------------------
Les images et vidéos sont stockées dans :
- templates/DemocratieDirecte/DD

Fichiers importants à utiliser
------------------------------
- MandatImperatif.md — description détaillée des 6 mandats
- Glossaire.md — définitions des termes clefs
- Plandematch.md — feuille de route par phases
- De nombreuses images/vidéos dans templates/DemocratieDirecte/DD (logos, backgrounds, photos)

Suggestions d'utilisation
-------------------------
- Créer des pages détaillées pour chaque mandat en convertissant les sections de MandatImperatif.md.
- Utiliser les images pour les bannières, slides et la landing page.
- Générer des PDF pour téléchargement (wkhtmltopdf ou une librairie côté serveur).
- Ajouter métadonnées (titre, description, attribution) aux images et héberger un index côté serveur si la galerie doit être complète.

Comment accéder
---------------
- Page de documentation locale: /democratie/documentation
- Assets: /democratie/assets/<filename> (ex: /democratie/assets/DEMOCRATIEDIRECTE.png)

Notes techniques
----------------
- Une route a été ajoutée dans app.py pour servir les fichiers dans le dossier DD (préfixe /democratie/assets/).
- La page de documentation affiche un aperçu client-side; si vous voulez lister dynamiquement tous les fichiers, je peux ajouter une route/endpoint qui retourne la liste.

Prochaines améliorations possibles
---------------------------------
- Générer automatiquement une page par mandat depuis MandatImperatif.md
- Ajouter un CMS léger (Netlify CMS / Tina / direct editing) pour éditer mandats/glossaire via interface
- Produire mini-visuals (png) pour partager sur les réseaux sociaux
