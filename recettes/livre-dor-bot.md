# livre-dor-bot

Ne le déploie pas avant que l'application Discord existe. Jusque-là, la carte du bot sur le site affiche « Bientôt en ligne ».

| Champ | Valeur |
|---|---|
| Espace | équipe |
| Type | Application |
| Image | `ghcr.io/<propriétaire>/cassiopee-livre-dor-bot`, tag `<sha>` |
| Port | pas de port |
| Mémoire | 256 Mo (CPU : 100 m par défaut) |
| Adresse publique | aucune |

## Variables d'environnement

| Nom | Type | Valeur |
|---|---|---|
| `API_URL` | Valeur | `http://livre-dor-api` |
| `DISCORD_TOKEN` | Secret | le token du bot, depuis le portail développeur Discord (Bot, Reset Token) |

`<sha>` : voir le `README.md` de ce dossier.
