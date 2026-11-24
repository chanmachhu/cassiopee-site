# livre-dor-api

| Champ | Valeur |
|---|---|
| Espace | équipe |
| Type | Application |
| Image | `ghcr.io/chanmachhu/cassiopee-livre-dor-api`, tag `<sha>` |
| Port | 8000 |
| Mémoire | 256 Mo (CPU : 100 m par défaut) |
| Adresse publique | aucune |

## Variables d'environnement

| Nom | Type | Valeur |
|---|---|---|
| `DATABASE_URL` | Base | `livre-dor-db`, Chaîne de connexion |
| `ADMIN_TOKEN` | Secret | à générer, jamais affiché ensuite |

`ADMIN_TOKEN` : `openssl rand -hex 32`. Garde-le ailleurs si tu en as besoin ; laissé vide en modification, il est conservé.

`<sha>` : voir le `README.md` de ce dossier. `TRUST_FORWARDED_FOR` : à ajouter plus tard, voir le `README.md`.
