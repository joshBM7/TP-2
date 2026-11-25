# LogiAI : starter de la séance « Tester, sécuriser et appeler l'API »

Suite du TP précédent : l'API LogiAI existe. Aujourd'hui vous la testez pour la casser, vous la protégez par une clé, puis une page web l'appelle.

## Installation (une fois)

    python -m venv .venv
    .venv\Scripts\activate.bat        # Windows cmd  (PowerShell : .venv\Scripts\Activate.ps1)
    source .venv/bin/activate         # macOS / Linux
    pip install -e ".[api,dev]"
    python -m logiai.dataset
    python -m logiai.train

L'installation éditable rend le package `logiai` importable depuis l'environnement.
`requirements.txt` contient les versions verrouillées utilisées par l'image Docker.

## Vos clés (fichier .env, jamais dans Git)

    copy .env.example .env            # macOS / Linux : cp .env.example .env
    # puis ouvrez .env et choisissez vos deux clés

## Lancer

    python -m uvicorn logiai.api.main:app --reload          # l'API, port 8000
    python -m http.server 5500 --directory web              # la page web, dans un 2e terminal
    # ouvrez http://localhost:5500

## Tester

    python -m pytest

## Utiliser le package et sa commande

Après l'installation éditable, `logiai-predict` prend le chemin d'un fichier JSON :

```powershell
logiai-predict livraison.json
```

La commande affiche une probabilité arrondie et l'état d'alerte. Elle ne
remplace pas la validation Pydantic de l'API. Les données et le modèle sont
recherchés sous `LOGIAI_HOME` (par défaut : le dossier courant) ; définissez
cette variable vers la racine du projet si la commande est lancée depuis un
autre dossier.

## Construire et installer un wheel

Depuis la racine du dépôt :

```powershell
python -m pip wheel --no-deps --wheel-dir dist .
python -m pip install dist\logiai-0.1.0-py3-none-any.whl
```

Le wheel ne contient pas les données ni un modèle entraîné. Le poste destinataire
doit donc disposer d'un environnement Python compatible et installer les
dépendances déclarées par le package. Pour réutiliser un modèle déjà entraîné,
installez aussi les versions exactes de `requirements.txt` afin d'éviter les
incompatibilités de sérialisation scikit-learn.

## Construire et lancer l'image Docker et Nginx

L'image installe LogiAI, fabrique un jeu de données synthétique et entraîne un
modèle au build. Les données d'exemple ne contiennent aucune clé API. Depuis la
racine du dépôt :

```powershell
docker compose up -d --build
docker compose ps
docker compose exec api python -c "import logiai; print(logiai.__file__)"
```

L'API est disponible sur le port 8000 et la page Nginx sur
`http://localhost:8080`. L'API installe le package depuis une zone temporaire,
puis supprime les sources de build. Elle génère un modèle synthétique
démonstratif sous `/app/models`; l'image s'exécute avec un utilisateur non-root.
Pour une image de production, remplacez ce modèle par un modèle métier validé.

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
- Les décisions de packaging sont documentées dans
  `docs/adr/005-packaging.md` et l'étude dans `docs/etude-de-conception.md`.
