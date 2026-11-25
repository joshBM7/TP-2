# Étude de conception : packaging de LogiAI

## Objectif

Rendre LogiAI installable dans un environnement Python propre, fournir une
commande de prédiction scriptable, produire un wheel installable et créer une
image Docker qui démarre l'API sans dépendre des fichiers locaux du développeur.

## État initial observé

- Le code est déjà regroupé dans le package `logiai/`.
- Les dépendances sont listées dans `requirements.txt`, sans métadonnées de
  package ni entry point.
- `Predictor` et l'entraînement utilisent `data/` et `models/` à la racine du
  dépôt. Ces répertoires sont ignorés par Git.
- L'entraînement requiert le CSV généré par `python -m logiai.dataset`.
- Aucun Dockerfile n'existe.

## Conception retenue

### Métadonnées et installation

`pyproject.toml` est l'unique source de vérité pour le nom, la version, les
dépendances d'exécution et les dépendances de développement. `pip install -e
".[api,dev]"` construit une installation éditable : les imports viennent du code
local et les entry points sont créés dans l'environnement courant.

Le backend setuptools découvre les packages `logiai*`. Le layout courant est
maintenu afin de ne pas casser les commandes `python -m logiai.*` ou les tests.

### Commande `logiai-predict`

La commande accepte un chemin JSON positionnel et lit le dictionnaire de
variables transmis au modèle. Elle affiche la probabilité en pourcentage,
l'indication d'alerte et le seuil utilisé. Un chemin absent ou illisible produit
un message sur stderr et un code de sortie non nul. Contrairement à l'API, elle
ne valide pas les bornes métier avec le schéma Pydantic ; les données doivent
être validées par l'appelant.

Exemple :

```powershell
logiai-predict livraison.json
```

### Stockage des données et du modèle

`LOGIAI_HOME` désigne la racine de travail (par défaut le répertoire courant) ;
`LOGIAI_DATA_DIR` peut la remplacer pour le stockage. Le CSV se trouve dans
`data/livraisons.csv`, le modèle dans `models/model.joblib` et ses métadonnées
dans `models/model_info.json`. Depuis un répertoire externe, le collègue définit
`LOGIAI_HOME` vers la racine contenant ces artefacts.

Le wheel ne fournit pas de modèle binaire : un destinataire initialise son
modèle en générant le dataset puis en lançant l'entraînement. L'image Docker
exécute ces étapes au build pour embarquer un modèle de démonstration.

### Image Docker

L'image `python:3.12-slim` installe les dépendances épinglées depuis
`requirements.txt`, puis le package depuis un répertoire temporaire copié avec
`pyproject.toml`. Elle supprime ce répertoire, génère les données synthétiques
et entraîne le modèle sous `/app`. Le conteneur API expose le port 8000 ; un
conteneur Nginx distinct sert la page web sur le port 8080. `.dockerignore`
exclut les clés, les fichiers locaux, les modèles préexistants, les caches et
les tests.

## Vérification

1. Exécuter `python -m pytest`.
2. Installer `pip install -e ".[api,dev]"` et lancer
   `logiai-predict livraison.json`.
3. Construire un wheel avec `python -m pip wheel --no-deps --wheel-dir dist .`.
4. Exécuter `docker compose up -d --build`, vérifier l'état healthy, la page
   Nginx, et l'import du package depuis `site-packages`.

## Limites et suite

- Le modèle Docker est synthétique et ne doit pas être promu en production sans
  validation métier.
- La distribution du wheel n'inclut ni les données ni le modèle ; la procédure
  d'entraînement reste nécessaire pour le poste destinataire.
- La création effective d'une pull request doit se faire dans le dépôt distant
  après revue des fichiers générés et des résultats de validation.
