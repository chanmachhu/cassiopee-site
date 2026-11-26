# cassiopee-site

Site de présentation de Cassiopée, la plateforme de déploiement de SIGL (les élèves y déploient une image de conteneur depuis l'intranet), et trois exemples d'applications déployables.

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

Exemples Python, dans chacun des dossiers `api`, `stats`, `bot` de `examples/livre-dor` :

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Les tests PostgreSQL (`api`, `stats`) sont ignorés sans `TEST_DATABASE_URL`. Front : `node --test tests/app.test.mjs` dans `examples/livre-dor/front`.

## Publication des images

La CI construit les images à chaque push sur `main` et les publie sur GHCR, taguées par le SHA court du commit (`latest` n'est pas utilisé).

**Première publication : passer chaque paquet en public.** GHCR crée les images en privé, et Cassiopée télécharge sans identifiants. GitHub → Packages → le paquet → Package settings → Change visibility → Public. À faire une fois par paquet.

## Déploiement

À la main, depuis le formulaire Cassiopée de l'intranet : voir [`recettes/README.md`](recettes/README.md). Une mise à jour = changer le tag de l'image dans le formulaire.

## Nettoyage annuel

Le nettoyage est fait à la main par SiOps (aucun job ne supprime les apps). **Ces six ressources doivent être exclues** : ce sont la vitrine de la plateforme.

- `cassiopee-site` (espace perso)
- `livre-dor-db`, `livre-dor-api`, `livre-dor-front`, `livre-dor-stats`, `livre-dor-bot` (espace équipe)

## Passation

1. Transférer le dépôt (Settings → Transfer ownership) vers le nouvel espace.
2. Les images sont publiées automatiquement sous le nouveau propriétaire (`ghcr.io/<propriétaire>/…`) ; passer chaque nouveau paquet en public, une fois.
3. Mettre à jour le préfixe des images dans Cassiopée lors du redéploiement, en suivant les recettes.
4. Mettre à jour les liens « Code » de `site/src/data/exemples.ts`.
5. Mettre à jour le lien vers le site dans le README du dépôt Cassiopée et dans le wiki SiOps.
