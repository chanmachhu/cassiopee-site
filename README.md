# cassiopee-site

Site de présentation de Cassiopée, la plateforme de déploiement du SIGL (les élèves y déploient une image de conteneur depuis l'intranet), et trois exemples d'applications déployables.

## Arborescence

```
site/                       site Astro (accueil, « Préparer son app », exemples)
examples/livre-dor/front    fichiers statiques + nginx
examples/livre-dor/api      API HTTP + PostgreSQL
examples/livre-dor/stats    tâche planifiée
examples/livre-dor/bot      bot Discord
recettes/                   une recette par app (valeurs du formulaire Cassiopée)
docs/                       conception, plan, maquettes
```

## Développement local

```bash
nvm use 22
cd site && npm ci && npm run dev
```

Exemples Python : `pytest` dans chaque dossier (`api`, `stats`, `bot`).

## Publication des images

La CI construit les images à chaque push sur `main` et les publie sur GHCR, taguées par le SHA court du commit (`latest` n'est pas utilisé).

**Première publication : passer chaque paquet en public.** GHCR crée les images en privé, et Cassiopée télécharge sans identifiants. GitHub → Packages → le paquet → Package settings → Change visibility → Public. À faire une fois par paquet.

## Déploiement

À la main, depuis le formulaire Cassiopée de l'intranet : voir [`recettes/README.md`](recettes/README.md). Une mise à jour = changer le tag de l'image dans le formulaire.

## Nettoyage annuel

Cassiopée supprime les apps chaque année. **Le site et les exemples ne doivent pas être supprimés** : ils sont la vitrine de la plateforme.

## Passation

1. Transférer le dépôt (Settings → Transfer ownership) vers le nouvel espace.
2. Redéployer les apps dans le nouvel espace Cassiopée en suivant les recettes, et repasser les paquets GHCR en public s'ils ont changé de propriétaire.
