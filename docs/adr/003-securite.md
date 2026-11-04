# ADR 003 : sécurité de l'API LogiAI

## Décision 1 : où transmettre la clé (en-tête, URL ou corps) ?
- **Choix : en-tête HTTP (`X-API-Key`).**
- Ce que l'autre option ferait perdre :
  - **URL** : la clé apparaîtrait en clair dans les logs du serveur, l'historique du navigateur et les proxies. Elle serait exposée à quiconque voit la requête HTTP complète.
  - **Corps** : incompatible avec les requêtes GET (qui n'ont pas de corps) ; oblige à lire le corps pour authentifier avant même de valider les données, ce qui complique le middleware.

## Décision 2 : quelles origines autoriser (CORS) ? Une liste précise ou « * » ?
- **Choix : liste précise** (`http://localhost:5500`, `http://127.0.0.1:5500`).
- Ce que `*` ferait perdre :
  - N'importe quelle page web, sur n'importe quel domaine malveillant, pourrait appeler l'API depuis le navigateur d'un utilisateur authentifié. Cela ouvre la porte aux attaques de type CSRF/cross-origin où un site tiers vole les données ou abuse de la clé stockée dans le navigateur.
