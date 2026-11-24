# Recettes de déploiement

Une recette par ressource, avec les valeurs exactes à saisir dans le formulaire de la page Cassiopée de l'intranet (https://intranet.sigl.epita.fr/cassiopee). Ressources : 100 m de CPU et 128 Mo par défaut, sauf mention contraire.

## Avant de commencer

- Les 5 paquets GHCR sont publics (voir « Publication des images » dans le `README.md` racine).
- Une équipe existe dans l'intranet : les exemples vivent dans l'espace d'équipe, le site dans ton espace perso.
- Le tag `<sha>` des recettes est le SHA court (7 caractères) du commit publié par la CI. Tu le trouves dans la page du paquet sur GitHub (Packages) ou dans le run CI de `main`. Les images sont `ghcr.io/chanmachhu/<nom>:<sha>`.

## Ordre de déploiement

1. [`livre-dor-db`](livre-dor-db.md) : la base. Applique ensuite `examples/livre-dor/schema.sql` si la base est vide.
2. [`livre-dor-api`](livre-dor-api.md)
3. [`livre-dor-front`](livre-dor-front.md)
4. [`livre-dor-stats`](livre-dor-stats.md)
5. [`livre-dor-bot`](livre-dor-bot.md) : à ne pas déployer tant que l'application Discord n'existe pas. La carte du bot sur le site affiche « Bientôt en ligne » jusque-là.
6. [`cassiopee-site`](cassiopee-site.md) : en dernier, pour connaître les adresses des exemples.

## Mettre à jour une image

Dans le formulaire de la ressource, change le tag de l'image pour le nouveau `<sha>`, puis enregistre.

## Reporter les adresses sur le site

Après avoir choisi les adresses du front du livre d'or (et de l'API si tu en exposes une), renseigne `enLigne` dans `site/src/data/exemples.ts`, puis redéploie le site (nouveau commit, nouveau tag, mise à jour de `cassiopee-site`).

## Vérifier `TRUST_FORWARDED_FOR`

Cette variable de l'API dit si l'adresse du visiteur se lit dans `X-Forwarded-For`. À `false` (défaut), tous les visiteurs derrière le proxy partagent une seule limite de débit.

1. Déploie l'API avec `TRUST_FORWARDED_FOR=false` (valeur par défaut, rien à saisir).
2. Fais quelques requêtes et regarde les logs de l'API ou une requête de test : l'adresse réelle du visiteur arrive-t-elle dans `X-Forwarded-For` ?
3. Seulement si oui : ajoute la variable `TRUST_FORWARDED_FOR` = `true` (Valeur) et redéploie.

## Nettoyage annuel

Ces apps doivent être exclues du nettoyage annuel de la plateforme.
