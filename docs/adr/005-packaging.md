# ADR 005 : distribuer LogiAI comme package Python

- **Statut :** accepté

## Pourquoi `>=` dans `pyproject.toml` et `==` dans `requirements.txt` ?

`pyproject.toml` exprime les versions compatibles pour les installations du
package ; `>=` laisse pip choisir une version plus récente compatible. L'autre
choix (`==`) figerait tous les utilisateurs du package sur les versions de
l'environnement de développement.

`requirements.txt` verrouille les versions utilisées pour reconstruire
l'environnement Docker ; `==` rend ce déploiement reproductible. L'autre choix
(`>=`) pourrait installer des versions différentes d'un build à l'autre et
changer le comportement de l'image.

## Le modèle fait-il partie du package ?

Non. Le package distribue le code et garde le modèle dans `models/`, à côté des
données. L'autre choix, inclure le modèle dans le wheel, augmenterait sa taille,
figerait un artefact local dans la distribution et lierait la mise à jour des
poids à la publication du code. Les données et le modèle ne sont pas inclus
dans le wheel ; `LOGIAI_HOME` indique où les retrouver.
