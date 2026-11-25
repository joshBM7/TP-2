# ADR 004 : distribuer LogiAI comme package Python

- **Statut :** accepté
- **Date :** 25 novembre 2026

## Contexte

LogiAI est un package Python importable depuis le dépôt, mais il n'a pas de
métadonnées de build, de commande installable ni de procédure reproductible
d'installation dans Docker. Les données et le modèle sont des artefacts
générés localement et ne sont pas suivis dans Git.

## Décisions

1. Déclarer le package, ses dépendances d'exécution et son extra `dev` dans
   `pyproject.toml`, avec setuptools comme backend PEP 517. Le package existant
   `logiai/` est conservé sans déplacement.
2. Publier `logiai-predict` comme entry point. La commande prend le chemin d'un
   fichier JSON positionnel et affiche une probabilité arrondie et l'état
   d'alerte.
3. Rechercher les données et le modèle sous `LOGIAI_HOME` (par défaut le
   répertoire courant). `LOGIAI_DATA_DIR` peut remplacer explicitement ce
   répertoire racine. Le wheel ne contient pas les données ni le modèle.
4. Construire une image Docker depuis Python 3.12 slim, installer les
   dépendances verrouillées puis le package depuis `/tmp/build`, supprimer les
   sources de build et entraîner un modèle d'exemple à partir des données
   synthétiques. Exécuter l'API sous un utilisateur non-root.
5. Ne pas inclure les clés, les données générées ni le modèle dans le wheel ou
   le contexte Docker.

## Conséquences

- L'installation éditable expose immédiatement les changements de code dans
  l'environnement de développement.
- Le wheel fournit le code et les métadonnées des dépendances, mais pas les
  répertoires `data/` et `models/`. Le destinataire doit fournir les artefacts
  ou indiquer leur emplacement avec `LOGIAI_HOME`.
- L'image Docker est autonome pour la démonstration ; le modèle synthétique
  d'exemple n'est pas un modèle métier validé.
- Le fichier `.env` reste réservé au développement local et n'est pas copié dans
  l'image. Les clés de déploiement doivent être injectées à l'exécution.

## Alternatives écartées

- Ajouter `setup.py` : cela dupliquerait les métadonnées et les dépendances.
- Déplacer tout le code vers un dossier `src/` : aucun bénéfice immédiat ne
  justifie de modifier les imports de l'API et les tests.
- Inclure un modèle binaire dans le wheel : le modèle actuellement utilisé est
  un artefact local non versionné et sa provenance n'est pas un contrat de
  distribution.
