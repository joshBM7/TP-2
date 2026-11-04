# Compte rendu : tester, sécuriser et appeler l'API LogiAI

**Noms :** BAYONNE MANGA joshua phil lilan  **Groupe :** 3

## 1. Casser son API (activité 1)
| Cas | Requête (corps ou URL) | Prévu | Obtenu |
|---|---|---|---|
| champ manquant | POST /v1/predict sans `poids_kg` | 422 | 422 |
| valeur absurde | POST /v1/predict avec `poids_kg: 99999` | 422 | 422 |
| texte au lieu d'un nombre | POST /v1/predict avec `distance_km: "loin"` | 422 | 422 |
| champ en trop | POST /v1/predict avec `couleur: "rouge"` | 422 | 422 |
| route inexistante | POST /v1/prediction | 404 | 404 |

- Une requête acceptée alors qu'elle devait être refusée ? **Oui : `heure_depart: 24` était accepté (bug le=24 au lieu de le=23) ; `nb_arrets: -1` était aussi accepté (bug : ge manquant).**

## 2. Les 2 bugs (activité 2)
| Bug | Test qui l'a révélé | Comportement avant | Correction |
|---|---|---|---|
| 1 | `test_valeurs_limites[heure_depart-24-422]` | `heure_depart=24` accepté (200) alors que 24 h n'existe pas | `Field(ge=0, le=24)` → `Field(ge=0, le=23)` dans `schemas.py` |
| 2 | `test_valeurs_limites[nb_arrets--1-422]` | `nb_arrets=-1` accepté (200) alors qu'un nombre négatif d'arrêts est absurde | Ajout de `ge=0` : `Field(ge=0, le=15)` dans `schemas.py` |

- Sortie de `python -m pytest` à la fin de l'activité 2 : tous les tests passent (vert).

## 3. La clé API (sprint 1)
- Ma fonction `verify_api_key()` :

```python
def verify_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail="Clé API manquante. Ajoutez l'en-tête X-API-Key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    if _egal(x_api_key, config.ADMIN_KEY):
        return "admin"
    if _egal(x_api_key, config.API_KEY):
        return "user"
    raise HTTPException(
        status_code=401,
        detail="Clé API invalide.",
        headers={"WWW-Authenticate": "ApiKey"},
    )
```

| Requête | Code obtenu |
|---|---|
| `/v1/predict` sans clé | 401 |
| `/v1/predict` fausse clé | 401 |
| `/v1/predict` clé utilisateur | 200 |
| `/v1/model-info` clé utilisateur | 403 |
| `/v1/model-info` clé administrateur | 200 |
| `/health` sans clé | 200 |

- Preuve que `.env` n'est pas dans Git (sortie de `git status`) : `.env` apparaît dans `.gitignore`, il n'est pas listé comme fichier suivi.

## 4. Le client web (sprint 2)
- Mon `fetch` :

```javascript
async function appelerApi(livraison, cle) {
  const reponse = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": cle,
    },
    body: JSON.stringify(livraison),
  });
  return { status: reponse.status, corps: await reponse.json() };
}
```

- Ce qui s'affiche :
  - **livraison normale** : « Probabilité de retard : 42.3 %. Livraison probablement à l'heure. » (vert)
  - **pluie de 500 mm** : « Données invalides : pluie_mm : Input should be less than or equal to 100 » (rouge)
  - **fausse clé** : « Clé API absente ou invalide. » (rouge)

- **Expérience CORS (port 5501)** : la page affiche « Impossible de joindre le serveur… » et la console (F12) montre une erreur `CORS policy: No 'Access-Control-Allow-Origin' header`. `curl` marche quand même car curl est un client système qui n'applique pas la politique same-origin : il n'envoie pas de preflight OPTIONS et ne vérifie pas les en-têtes CORS.

- **Où voit-on la clé dans F12 ?** Dans l'onglet **Network** > sélectionner la requête POST > onglet **Headers** > section **Request Headers** : `X-API-Key: <votre-clé>`.

## 5. Questions de compréhension
1. **401 vs 403 vs 422** : 401 = non authentifié (pas de clé ou clé incorrecte) ; 403 = authentifié mais pas autorisé (clé user sur une route admin) ; 422 = requête mal formée (données invalides selon le schéma).
2. **Clé ni dans le code ni dans Git** : si la clé est dans le code, elle est visible par quiconque lit le dépôt (y compris en historique Git). On utilise `.env` (hors Git) pour que la clé reste secrète et puisse changer sans modifier le code.
3. **`compare_digest` plutôt que `==`** : l'opérateur `==` s'arrête dès le premier caractère différent (court-circuit), ce qui crée une fuite temporelle permettant de deviner la clé caractère par caractère. `compare_digest` prend toujours le même temps quelle que soit la position du premier caractère différent.
4. **`curl` fonctionne alors que la page du port 5501 est bloquée** : la politique CORS est appliquée par le navigateur, pas par le serveur. `curl` est un outil en ligne de commande qui n'est pas un navigateur et n'applique pas ces restrictions.
5. **La validation côté navigateur ne remplace pas celle de l'API** : la validation HTML/JS peut être contournée (DevTools, Postman, curl…). L'API est l'unique point d'entrée de confiance ; elle doit valider elle-même toutes les données, indépendamment du client.

## 6. Lien de la pull request
