# LogiAI : starter de la séance « Tester, sécuriser et appeler l'API »

Suite du TP précédent : l'API LogiAI existe. Aujourd'hui vous la testez pour la casser, vous la protégez par une clé, puis une page web l'appelle.

## Installation (une fois)

    python -m venv .venv
    .venv\Scripts\activate.bat        # Windows cmd  (PowerShell : .venv\Scripts\Activate.ps1)
    source .venv/bin/activate         # macOS / Linux
    pip install -r requirements.txt
    python -m logiai.dataset
    python -m logiai.train

## Vos clés (fichier .env, jamais dans Git)

    copy .env.example .env            # macOS / Linux : cp .env.example .env
    # puis ouvrez .env et choisissez vos deux clés

## Lancer

    python -m uvicorn logiai.api.main:app --reload          # l'API, port 8000
    python -m http.server 5500 --directory web              # la page web, dans un 2e terminal
    # ouvrez http://localhost:5500

## Tester

    python -m pytest

## Tester une prédiction avec curl sous PowerShell

Le corps d'exemple est fourni dans `livraison.json`. Dans un terminal PowerShell
ouvert à la racine du projet, chargez la clé utilisateur depuis `.env` puis
envoyez la requête :

```powershell
$apiKey = (Get-Content .env | Where-Object { $_ -match '^LOGIAI_API_KEY=' } | Select-Object -First 1) -replace '^LOGIAI_API_KEY=', ''
curl.exe -X POST "http://localhost:8000/v1/predict" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: $apiKey" `
  --data-binary "@livraison.json"
```

PowerShell utilise l'accent grave (`` ` ``) pour continuer une commande sur la
ligne suivante ; l'antislash `\` ne fonctionne pas comme continuation de ligne
dans PowerShell. Gardez la clé dans `.env` et ne la publiez pas.

## Contenu de l'atelier

- L'API valide les entrées, authentifie les clés utilisateur et réserve les
  informations du modèle à la clé administrateur.
- Les tests couvrent les entrées malformées, les limites du schéma et les
  réponses 401/403. Une route inexistante répond 404.
- La page web envoie la prédiction, affiche les erreurs de validation et
  réactive le bouton après la requête.
- Les décisions de sécurité sont documentées dans `docs/adr/003-securite.md`.
