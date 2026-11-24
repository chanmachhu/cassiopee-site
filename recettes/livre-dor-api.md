# livre-dor-api

| Champ | Valeur |
|---|---|
| Espace | équipe |
| Type | Application |
| Image | `ghcr.io/<propriétaire>/cassiopee-livre-dor-api`, tag `<sha>` |
| Port | 8000 |
| Mémoire | 256 Mo (CPU : 100 m par défaut) |
| Adresse publique | aucune |

## Variables d'environnement

| Nom | Type | Valeur |
|---|---|---|
| `DATABASE_URL` | Base | `livre-dor-db`, Chaîne de connexion |
| `ADMIN_TOKEN` | Secret | à générer, jamais affiché ensuite |

`ADMIN_TOKEN` : `openssl rand -hex 32`. Garde-le ailleurs si tu en as besoin ; laissé vide en modification, il est conservé.

Variables optionnelles (Valeur) :

| Nom | Défaut | Rôle |
|---|---|---|
| `RATE_GLOBAL_PER_MIN` | 30 | messages acceptés par minute, tous visiteurs confondus |
| `RATE_PER_CLIENT_PER_MIN` | 5 | messages acceptés par minute et par client |

## Modérer le livre d'or

Lister les derniers messages avec leurs identifiants :

```bash
curl https://<adresse-du-front>/api/messages?limit=50
```

Supprimer un message (réponse 204) :

```bash
curl -X DELETE -H "Authorization: Bearer $ADMIN_TOKEN" https://<adresse-du-front>/api/messages/<id>
```

Vague de spam : un mainteneur supprime en masse depuis la base (`kubectl exec` dans le pod PostgreSQL, puis `psql`) :

```sql
DELETE FROM messages WHERE cree_le > '2026-11-24 10:00';
```

Jeton perdu : saisis une nouvelle valeur du secret `ADMIN_TOKEN` dans Cassiopée (vide, l'ancienne valeur est conservée).

`<sha>` : voir le `README.md` de ce dossier. `TRUST_FORWARDED_FOR` : à passer à `true` après vérification, voir le `README.md`.
