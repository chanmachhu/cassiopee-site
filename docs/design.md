# Site de présentation de Cassiopée — design

23/11/2026. Roadmap : `doc/roadmap.md` (!30), partie 3 « campagne de lancement ». Maquette validée : canvas « Maquettes du site Cassiopée », artboard D · Mythologie (version 38).

## Intention

Annoncer Cassiopée comme un vrai outil de déploiement pour les élèves, plus comme un outil en test. Le site est la vitrine de la campagne de lancement :

- il remplace le guide Markdown « Préparer son application » (`doc/preparer-son-app.md`, !30) ;
- il est lui-même déployé sur Cassiopée, comme une app d'élève : la preuve par l'exemple ;
- il montre trois exemples réels qui tournent sur Cassiopée, avec leur code et la recette pour les reproduire ;
- il est la cible des liens de la campagne : l'affiche affichée avant le check de présence et le tutoriel de première visite que SiWeb ajoute à l'intranet (page de retour SiWeb du 22/11), ainsi que l'annonce de 5 minutes avec slides.

## Objectifs, non-objectifs, anti-objectifs

**Objectifs**
- Un accueil fidèle à la maquette D : marbre, lierre et or, colonnes ioniques dessinées, animations.
- Une page « Préparer son app » tirée du guide, mis à jour **avant** le site (Hugo, 23/11) : secrets et espaces d'équipe ajoutés, S3 retiré.
- Une page « Exemples » : pour chacun des trois exemples, ce qu'il montre, un lien vers l'app en ligne, un lien vers le code et la recette (les valeurs exactes à saisir dans le formulaire Cassiopée).
- Trois exemples qui tournent vraiment sur Cassiopée de prod, bot Discord compris (Hugo, 23/11).
- Lisible et utilisable sur téléphone ; accessible (contraste 4,5:1, clavier, focus visible) ; toutes les animations coupées sous `prefers-reduced-motion`.
- Transmissible : un dépôt qu'un successeur reprend et redéploie sans aide.

**Non-objectifs** : un backend pour le site (pas de formulaire, pas de compte, pas de statistiques de visite) ; un CMS ; une autre langue que le français ; un thème sombre (la direction artistique est un marbre clair, choisi) ; présenter le S3 (désactivé, chantier 0) ; les demandes de quota (chantier 3, pas encore cadré avec SiWeb).

**Anti-objectifs**
- un exemple présenté « en ligne » qui ne tourne pas sur Cassiopée ;
- un secret (jeton du bot, clé d'administration, identifiants de base) écrit dans le dépôt, dans une image ou dans un log ;
- un site qui disparaît au nettoyage annuel des apps sans que personne ne l'ait prévu ;
- une page lourde ou lente à cause des animations : le site doit rester rapide sur un téléphone moyen.

## Contraintes

- **Dépôt** : public, sur le GitHub personnel de Hugo, `chanmachhu/cassiopee-site`, sans organisation ; transféré à la passation (Hugo, 20/11). `gh` est connecté en `chanmachhu` avec les droits `repo` et `write:packages`.
- **Images** : publiques sur GHCR, `linux/amd64`, construites par GitHub Actions. Une app Cassiopée doit tourner sans root, écouter sur `0.0.0.0` et sur un seul port, et ne pas écrire sur un disque persistant (guide, sections 1 à 6).
- **Où ça tourne** (Hugo, 23/11, option B) : le site dans l'**espace personnel** de Hugo sur Cassiopée de prod ; les trois exemples dans son **espace d'équipe**. Quota perso : 3 apps, le site en prend 1. Équipe : 18 apps et 18 bases, les exemples prennent 4 apps et 1 base.
- **Déploiement** : à la main, par Hugo, depuis le formulaire Cassiopée de l'intranet de prod, en suivant les recettes du dépôt. Pas de déploiement automatique : Cassiopée n'a pas de jeton machine, et `latest` ne serait pas retéléchargé (`pullPolicy: IfNotPresent`). Une mise à jour = changer le tag de l'image dans le formulaire.
- **Adresses** : choisies par Hugo au déploiement ; `docs` est un nom réservé.
- **Nettoyage annuel** : il est fait à la main (aucun job ne supprime les apps). Le site et les exemples doivent en être explicitement exclus : à écrire dans le README du dépôt et dans le wiki SiOps.
- **Contenu** : le guide de !30 date d'avant les secrets et les équipes. Il est mis à jour en premier, avec les règles réellement en prod (0.8.1) : secrets, références, espaces d'équipe, règle des noms (une lettre minuscule en premier).

## Approches

| | Comment | Pour | Contre |
|---|---|---|---|
| **A · Astro avec des îlots React** (retenue, Hugo, 23/11) | Pages générées en HTML statique ; composants React Bits chargés seulement là où ils animent ; guide en Markdown | Ce qui se fait pour un site vitrine avec de la doc ; peu de JavaScript ; le guide reste un fichier Markdown | Un outil de plus à découvrir pour le successeur |
| B · React et Vite, une seule page | Tout en React, routeur côté navigateur | React Bits utilisé tel quel | Plus de JavaScript ; routeur et plugin Markdown à ajouter ; nginx doit renvoyer `index.html` partout |
| C · HTML, CSS et JavaScript sans build | La maquette reprise presque telle quelle | Aucune dépendance | React Bits seulement imité ; guide converti à la main ; en-tête et pied copiés dans chaque page |

Sécurité : les trois donnent des fichiers statiques servis par nginx sans root, sans serveur applicatif. Le seul risque supplémentaire de A est la chaîne d'approvisionnement npm au build, traité plus bas.

## Décisions prises

**Par Hugo**
- Direction artistique D validée (canvas, version 38) : marbre blanc et gris, lierre vert, or pour les détails ; titres en Cinzel, texte en EB Garamond ; chiffres arabes, tout en français ; pas d'effet sur le curseur.
- Survol des cartes : le lierre d'un temple repousse vite quand on arrive sur la carte, puis se balance ; son ombre n'apparaît qu'ensuite ; quitter la carte ne rejoue rien. Stèles et exemples : la palmette ou le laurier frémit.
- Animations déclenchées section par section, une seule fois, quand la section arrive à l'écran ; pas d'animation liée à la position du défilement.
- Guide mis à jour avant le site.
- Site dans l'espace perso, exemples dans l'espace d'équipe.
- Le bot Discord tourne pour de vrai, sur un serveur Discord SiOps ; Hugo crée l'application Discord plus tard et saisit lui-même le jeton comme secret.
- Astro avec des îlots React.

**Par moi (à corriger si besoin)**
- **Un seul dépôt** pour le site et les exemples : un seul dépôt à transférer, une seule CI. Arborescence :
  ```
  site/                    Astro : pages, composants, dessins, guide
  examples/livre-dor/front fichiers statiques + nginx
  examples/livre-dor/api   API HTTP + PostgreSQL
  examples/stats           tâche planifiée
  examples/bot             bot Discord
  recettes/                une recette par app (valeurs du formulaire)
  .github/workflows/       construction et publication des images
  ```
- **Source unique du guide** : le guide déménage dans le site (`site/src/content/preparer-son-app.md`). Dans !30, on retire `doc/preparer-son-app.md` et le README de Cassiopée pointe vers le site ; la roadmap reste dans !30.
- **Polices auto-hébergées** (paquets Fontsource) plutôt que Google Fonts : aucune requête vers un tiers, une CSP plus stricte, et pas de transfert d'adresse IP à Google.
- **React Bits** : les composants sont copiés dans le dépôt (c'est le mode prévu par React Bits), avec leur licence (MIT + Commons Clause, qui autorise cet usage). Utilisés comme îlots : BlurText (titre), RotatingText (« API » → app, bot, site), ShinyText (accroche), StarBorder et ClickSpark (bouton principal). Tout le reste (lierre, balancement, rayons, poussière d'or, apparitions) reste en CSS et SVG, sans React.
- **Dessins** : le générateur de la maquette (`gen.py` : colonnes ioniques, lierre, fronton, palmettes) entre dans le dépôt, et sa sortie est commitée sous forme de composants Astro sans JavaScript. Il ne tourne pas au build.
- **Exemples en Python** pour l'API, la tâche et le bot (un seul langage, lu par la plupart des élèves) ; front du livre d'or en HTML et JavaScript simples.
- **Images** : taguées par le SHA court du commit ; `latest` n'est pas utilisé dans les recettes.

## Le site

**Pages**
- `/` : l'accueil de la maquette D (fronton, colonnade, chiffres, trois piliers, rituel en trois étapes, trois exemples, ce que le temple accueille, l'oracle (FAQ), fin).
- `/preparer-son-app` : le guide mis à jour, mis en page dans la même direction artistique (titres Cinzel, encadrés de marbre, blocs de code lisibles, sommaire).
- `/exemples` : les trois exemples, une section chacun (`#livre-dor`, `#stats`, `#bot`) avec ce qu'il montre, ses liens et sa recette. Les boutons « Recette » de l'accueil pointent vers ces ancres.
- une page 404 dans le même style.

Les pages « Préparer son app » et « Exemples » n'ont pas encore de maquette : elles sont maquettées sur le canvas et validées par Hugo avant d'être développées, comme l'accueil.

**Animations** : celles de la maquette (version 38), déclenchées par section à l'arrivée à l'écran (IntersectionObserver, une fois). Sans JavaScript ou sous `prefers-reduced-motion`, tout s'affiche directement dans son état final.

**Liens vers les exemples** : les adresses publiques et l'état du bot (en ligne ou pas encore) sont dans un fichier de données du site (`site/src/data/exemples.ts`). Tant que les adresses ne sont pas choisies, les boutons « Voir en ligne » ne s'affichent pas ; on les remplit après le déploiement des exemples, puis on redéploie le site.

**Service** : image `nginxinc/nginx-unprivileged`, port 8080, fichiers statiques seulement (construction en deux étapes : Node pour le build, nginx pour l'image finale). Tous les scripts sont des fichiers servis par le site, aucun script en ligne, pour garder une CSP simple sans empreintes à calculer. En-têtes : CSP stricte (`default-src 'self'`), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` restrictive, `frame-ancestors 'none'`. Cache : HTML revalidé à chaque visite (`no-cache`), fichiers à nom haché (`/_astro/*`) en cache long.

## Les exemples

Tous dans l'espace d'équipe de Hugo. Chaque exemple illustre au moins une fonctionnalité de Cassiopée, et sa recette donne toutes les valeurs du formulaire.

**Livre d'or** (front, API, PostgreSQL) — montre : deux apps qui se parlent par le réseau interne, une base, une référence et un secret.
- Base PostgreSQL créée dans Cassiopée.
- API : lister les messages, en poster un, en supprimer un. La connexion à la base vient d'une **référence** (`DATABASE_URL` → chaîne de connexion de la base). La suppression exige une clé d'administration passée en **secret** (`ADMIN_TOKEN`) : c'est « la clé d'API par un secret » de la maquette. L'API n'a pas d'adresse publique.
- Front : page statique servie par nginx, qui relaie `/api` vers l'API par son nom interne. Chaque app a un Service sur le port 80 qui renvoie vers le port du conteneur : l'URL interne est `http://<nom-de-l-api>` (guide section 11). Cette URL est une **variable** (valeur).
- Le livre d'or est public, ouvert à toute l'école : messages courts (longueur bornée), texte seul (affiché comme texte, jamais comme HTML), suppression par la clé d'administration pour modérer. Limite de débit : globale (un nombre de messages par minute pour tout le livre d'or), et par adresse seulement si l'adresse réelle du visiteur arrive jusqu'à l'app ; c'est à vérifier au déploiement, car le répartiteur de charge devant le cluster peut la masquer.

**Statistiques horaires** (tâche planifiée) — montre : une tâche qui tourne toutes les heures et partage la base d'une autre app.
- Toutes les heures (`0 * * * *`, heure UTC), calcule des statistiques (par exemple le nombre de messages par jour) dans une table de la même base ; le front du livre d'or les affiche.
- Connexion par la même **référence** vers la base : une tâche planifiée accepte variables, secrets et références comme une app, et peut référencer n'importe quelle base de son espace.

**Bot Discord** (app sans port) — montre : une app sans adresse ni port, et un vrai secret.
- Jeton Discord en **secret** (`DISCORD_TOKEN`), saisi par Hugo.
- Une commande, `/livredor`, qui affiche les derniers messages en appelant l'API du livre d'or par son nom interne.
- Tant que l'application Discord n'existe pas, le bot est construit et sa recette écrite, mais il n'est pas déployé ; sa carte n'affiche pas « Voir en ligne ».

**Ressources** : valeurs par défaut de Cassiopée (100 m de CPU, 128 Mo) ; 256 Mo pour l'API et le bot si Python le demande. Le quota d'équipe (6 vCPU, 9 Go) laisse une large marge.

## Ordre de réalisation

1. **Guide** : je mets à jour le guide à partir de `doc/preparer-son-app.md` et de ce qui est en prod (0.8.1) ; Hugo le valide. C'est le contenu de la page « Préparer son app » et la base du tutoriel SiWeb.
2. **Dépôt, CI, accueil et exemples** : création du dépôt, construction des images, accueil d'après la maquette D (fichier de la maquette et générateur copiés dans `docs/maquette/`, textes repris de la maquette), les trois exemples et leurs recettes. En parallèle, maquettes des pages « Préparer son app » et « Exemples » sur le canvas.
3. **Pages « Préparer son app » et « Exemples »**, une fois leurs maquettes validées par Hugo.
4. **Déploiement** par Hugo : exemples dans l'espace d'équipe, puis le site dans l'espace perso ; adresses reportées dans `exemples.ts` ; site redéployé. Le bot suit quand l'application Discord existe.

À la première publication, GHCR crée chaque image en privé : Hugo la passe en public une fois, depuis les réglages du paquet sur GitHub (étape écrite dans le README).

## Sécurité du dépôt et des images

- Aucun secret dans le dépôt : les seules valeurs sensibles (jeton du bot, clé d'administration) sont saisies dans Cassiopée comme secrets ; les identifiants de la base arrivent par une référence. Les recettes nomment ces variables sans valeur.
- Dépendances figées (fichiers de verrouillage, `npm ci`), Dependabot activé pour npm, pip, Docker et GitHub Actions.
- GitHub Actions : actions épinglées par SHA, permissions minimales (`contents: read`, `packages: write` seulement pour la publication), pas de secret de dépôt nécessaire (le jeton GitHub intégré suffit pour GHCR).
- Images finales minimales, sans outils de build, utilisateur non root.

## Laissé au builder

- Le découpage exact en composants Astro et React, et l'organisation des styles.
- Le framework web et le pilote PostgreSQL de l'API, la bibliothèque Discord du bot (en Python).
- Le schéma de la base du livre d'or et des statistiques.
- Les valeurs exactes des limites (longueur des messages, débit), dans des bornes raisonnables pour un livre d'or d'école.
- La mise en page des recettes, tant qu'elles donnent toutes les valeurs du formulaire.
