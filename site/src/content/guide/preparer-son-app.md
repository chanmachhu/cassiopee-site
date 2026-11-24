---
title: Préparer son application pour Cassiopée
description: Les règles à respecter pour qu'une image de conteneur tourne sur Cassiopée, et comment les vérifier avant de déployer.
---

## À quoi sert Cassiopée

Cassiopée héberge les **projets des élèves** du SIGL : une application web, son API et sa base de données, déployés depuis l'intranet sans toucher à Kubernetes. C'est une plateforme d'école : pas de garantie de disponibilité, pas de sauvegarde automatique, des ressources limitées.

**Toutes les apps sont supprimées chaque année.** Cassiopée est fait pour des projets **éphémères** (projet de cours, hackathon, démo de fin de module), qui ne servent plus à la fin de l'année. Il n'est pas fait pour un PAE ou un service qui doit continuer à tourner d'une année sur l'autre.

**Ce que Cassiopée fait bien** : quelques services (pas des dizaines), sans état, qui communiquent en HTTP ou en WebSocket, chacun avec au plus une base de données. Combien exactement dépend de ton quota (voir « Ressources et quotas »).

| Projet | Sur Cassiopée ? | Pourquoi |
|---|---|---|
| Site ou application web (front + API + PostgreSQL) | **Oui** | C'est le cas prévu : 2 apps, 1 base, 1 ou 2 endpoints |
| Jeu multijoueur dans le navigateur (front + serveur WebSocket + base des scores) | **Oui** | HTTP et WebSocket passent par les endpoints |
| Bot Discord ou Slack | **Oui** | Une app « sans port », qui sort vers Internet |
| Tâche planifiée (rapport quotidien, nettoyage, scraping) | **Oui** | Une app de type tâche planifiée (CronJob) |
| API qui stocke des fichiers (images, PDF) | **À adapter** | Le stockage S3 est indisponible pour l'instant : fichiers en base, ou à l'extérieur |
| Application de 10 à 15 microservices | **Non** | Cassiopée vise quelques services par projet : pas de service mesh, pas de broker de messages géré, quotas limités |
| Kafka, RabbitMQ, Elasticsearch, cluster de bases | **Non** | Ces systèmes ont besoin de disques persistants et de plusieurs nœuds |
| Serveur de jeu natif (Minecraft, serveur UDP) | **Non** | Seuls HTTP et HTTPS sont exposés : pas de port TCP ou UDP brut |
| Entraînement de modèle ML, calcul lourd | **Non** | Pas de GPU, 1 vCPU au total |
| Application qui doit écrire sur son disque (SQLite, uploads locaux) | **À adapter** | Le disque d'une app est effacé à chaque redémarrage : base à la place |
| Image qui doit tourner en root | **À adapter** | Les conteneurs tournent sans root (UID 1000) |
| Service pour de vrais utilisateurs en production | **Non** | Plateforme d'école : pas de garantie de disponibilité ni de sauvegarde |
| PAE, outil de promo ou service qui doit durer plus d'un an | **Non** | Toutes les apps sont supprimées chaque année |

## Ce qui change par rapport à ton poste

Sur Cassiopée, chaque morceau est séparé et isolé : l'application et la base sont des ressources distinctes, reliées par des variables d'environnement. Une image qui marche en local peut donc échouer sur Cassiopée si elle ne respecte pas les règles ci-dessous.

## Checklist

| # | Règle | Si tu l'oublies |
|---|---|---|
| 1 | L'image est **publique**, avec un **tag** (`1.4.2`, pas un digest), construite pour **`linux/amd64`** | `ImagePullBackOff` : image privée, tag inexistant ou image ARM seulement (build sur Mac M1/M2/M3) |
| 2 | L'app écoute sur **`0.0.0.0`**, sur **un seul port** connu (et déclaré par `EXPOSE`) | Le site répond 502 : l'app écoute sur `localhost` ou sur un autre port |
| 3 | L'app tourne **sans root** (UID 1000) | `permission denied` au démarrage, quand l'image écrit dans un dossier réservé à root |
| 4 | **Toute la configuration passe par des variables d'environnement** (base, URLs, clés) | L'app cherche sa base sur `localhost` et plante |
| 5 | L'app **crée elle-même son schéma** de base (migrations au démarrage) et **réessaie** la connexion | Tables manquantes, ou plantage si la base démarre après l'app |
| 6 | **Rien d'important n'est écrit sur le disque** du conteneur | Fichiers perdus à chaque redémarrage ou redéploiement |
| 7 | L'app est **sans état** si elle a plusieurs instances (`replicas` > 1) | Sessions perdues d'une requête à l'autre |
| 8 | L'app tient dans **ses ressources** (128 Mo et 0,1 vCPU par défaut) | `OOMKilled` en boucle (Java, Node, Python avec ML…) |
| 9 | L'app parle **HTTP**, et laisse Cassiopée gérer HTTPS | Boucle de redirection, URLs générées en `http://` |
| 10 | Les logs vont sur **stdout / stderr** | Pas de diagnostic possible |

Les sections suivantes détaillent chaque point, avec la façon de le vérifier **avant** de déployer.

## 1. L'image

- **Publique** : Cassiopée télécharge l'image sans identifiants. Docker Hub, `ghcr.io` (paquet public) ou `registry.cri.epita.fr` (projet public).
- **Taguée** : `image: ghcr.io/moi/mon-app`, `tag: 1.4.2`. Évite `latest` : changer de tag est ce qui déclenche le redéploiement.
- **`linux/amd64`** : les nœuds du cluster sont tous amd64. Sur un Mac Apple Silicon, `docker build` produit de l'arm64 par défaut :

  ```bash
  docker buildx build --platform linux/amd64 -t ghcr.io/moi/mon-app:1.4.2 --push .
  ```

Avant de créer l'app, Cassiopée lit la configuration de ton image : le port déclaré par `EXPOSE` pré-remplit le champ « port », et les pièges connus (image prévue pour root, aucun port déclaré) s'affichent.

## 2. Écouter sur le bon port, et sur 0.0.0.0

Le trafic arrive sur le port que tu indiques dans Cassiopée (`service.target_port`). Ton process doit écouter **sur ce port** et **sur toutes les interfaces**, pas seulement `localhost` :

| Stack | Correct | Piège fréquent |
|---|---|---|
| Node / Express | `app.listen(process.env.PORT \|\| 8080, '0.0.0.0')` | `app.listen(3000, 'localhost')` |
| Python / FastAPI | `uvicorn main:app --host 0.0.0.0 --port 8080` | `--host 127.0.0.1` (défaut) |
| Python / Flask | `gunicorn -b 0.0.0.0:8080 app:app` | `flask run` (dev, `127.0.0.1`) |
| Vite / dev servers | **ne pas** déployer le serveur de dev ; servir le build avec nginx | `vite --host` en prod |
| Spring Boot | `server.port=8080` (écoute sur toutes les interfaces par défaut) | — |

Déclare ce port dans le `Dockerfile` (`EXPOSE 8080`) : Cassiopée le proposera automatiquement.

**Une app qui n'écoute sur aucun port** (bot Discord, worker) : coche « Mon app n'écoute sur aucun port ». Elle n'a alors pas d'adresse et ne peut pas recevoir d'endpoint.

## 3. Sans root

Cassiopée lance tous les conteneurs en **UID 1000**, sans privilèges, quel que soit le `USER` de l'image. Conséquences :

- ton app ne peut écrire que dans `/tmp` ou dans des dossiers qui appartiennent à l'UID 1000 ;
- certaines images officielles prévues pour root échouent : préfère leur variante non-root.

Pour tester en local exactement comme sur Cassiopée :

```bash
docker run --rm --user 1000:0 -p 8080:8080 -e PORT=8080 ghcr.io/moi/mon-app:1.4.2
```

Cassiopée lance le conteneur avec l'UID 1000 et le GID 0, et seuls `/tmp`, `/var/cache/nginx` et `/var/run` sont accessibles en écriture.

## 4. La configuration par variables d'environnement

Rien ne doit être écrit en dur pour ton poste : ni `localhost`, ni mot de passe, ni URL. Lis tout dans l'environnement (`process.env`, `os.environ`, `${…}` dans Spring) et renseigne ces variables dans Cassiopée. Il y a trois sortes de variables :

| Sorte | Pour quoi | Ce qui se passe |
|---|---|---|
| **Valeur** | Une configuration sans risque (`LOG_LEVEL`, `BASE_URL`) | Écrite dans Git : n'y mets rien de sensible |
| **Secret** | Un jeton, une clé d'API | Saisi une fois, rangé dans Vault, jamais réaffiché. Une valeur vide conserve le secret existant |
| **Base** | Une information de connexion d'une base de ton espace | Référence vers la base : chaîne de connexion, hôte, port, utilisateur, mot de passe ou nom de la base |

## 5. La base de données

Ne mets pas ta base dans ton image et ne la déploie pas comme une app : crée-la dans **Bases de données**. Elle a un disque persistant et des identifiants générés pour toi.

| Moteur | Port | Hôte dans ton espace | URL fournie |
|---|---|---|---|
| PostgreSQL (14-17) | 5432 | `<nom>-postgresql` | `postgresql://user:pass@<nom>-postgresql:5432/db` |
| MariaDB (10-11) | 3306 | `<nom>-mariadb` | `mysql://user:pass@<nom>-mariadb:3306/db` |
| MongoDB (6-7) | 27017 | `<nom>-mongodb` | `mongodb://user:pass@<nom>-mongodb:27017/db?authSource=db` |

- **Branche la base par une référence**, sans recopier ses identifiants : une variable de sorte **Base** (`DATABASE_URL` = chaîne de connexion de ta base). Java attend une URL JDBC : prends l'hôte, le port et le nom de la base par trois références, et l'utilisateur et le mot de passe par deux autres.
- **Le mot de passe n'est affiché qu'une fois**, à la création : tu n'as pas besoin de le copier si tu passes par une référence.
- **Ton app doit créer ses tables elle-même**, au démarrage (migrations Prisma, Alembic, Flyway, Liquibase, `sequelize db:migrate`…). La base n'est joignable que depuis ton espace Cassiopée : pas de `psql` depuis ton poste.
- **Réessaie la connexion** pendant quelques dizaines de secondes au démarrage : la base peut être prête après l'app.
- **Pas de sauvegarde automatique** : exporte tes données toi-même si elles comptent.
- **Redis n'existe pas en base gérée** : un Redis lancé comme app perd ses données à chaque redémarrage (acceptable pour un cache, pas pour des données).

## 6. Pas de disque persistant pour une app

Ce qu'une app écrit sur son disque (uploads, fichiers SQLite, logs dans un fichier) **disparaît** à chaque redémarrage ou redéploiement. Selon le besoin :

| En local | Sur Cassiopée |
|---|---|
| Fichier SQLite | Une base PostgreSQL ou MariaDB |
| Dossier `uploads/` | Une base de données (le stockage S3 est indisponible pour l'instant) |
| Sessions en mémoire ou en fichiers | Sessions en base (ou JWT) |

Si l'image déclare un `VOLUME`, c'est qu'elle compte garder des données à cet endroit : elles seront perdues sur Cassiopée.

## 7. Le stockage S3

Le stockage S3 est indisponible pour l'instant.

## 8. Plusieurs instances

Jusqu'à 3 instances (`replicas`) par app. Chaque requête peut tomber sur une instance différente : sessions, fichiers et caches en mémoire ne sont pas partagés. Garde une seule instance si ton app a un état local.

## 9. Ressources et quotas

- **Par défaut**, chaque conteneur a **0,1 vCPU et 128 Mo**. Au-delà de sa mémoire, il est tué (`OOMKilled`) puis relancé.
- **Ton quota personnel** : 1 vCPU et 1,5 Go au total, 3 apps, 3 bases, 30 Go de stockage de base. Une app compte ses limites × ses instances ; **une base compte aussi** (0,25 vCPU et 512 Mo par défaut) : une app Java à 512 Mo plus une base, c'est déjà 1 Go sur 1,5.
- **Espace d'équipe** : ton groupe de l'intranet a son propre espace, avec le même quota pour toutes les équipes : 6 vCPU, 9 Go, 18 apps, 18 bases (180 Go de stockage de base). Il est partagé entre les membres du groupe. La liste des apps a deux onglets, **Personnel** et **Équipe**, et une colonne « Créé par » indique qui a déployé quoi.
- **Noms** : une app, une base ou un endpoint commence par une lettre minuscule, contient des minuscules, des chiffres et des tirets, et finit par une lettre ou un chiffre. Certains noms d'adresses sont réservés à la plateforme (`www`, `api`, `app`, `admin`, `auth`, `docs`, `status`, `staging`, `prod`, `mail`…) : choisis-en un autre.
- Java, Node et Python avec des bibliothèques lourdes dépassent vite 128 Mo : règle `resources.limits` (256 à 512 Mo) et dis-le à ton runtime (`-XX:MaxRAMPercentage=75`, `NODE_OPTIONS=--max-old-space-size=384`).

## 10. HTTP derrière le HTTPS de Cassiopée

Un **endpoint** expose ton app sur `https://<nom>.cassiopee.siops.sigl.epita.fr`, avec un certificat Let's Encrypt émis en une à deux minutes. Cassiopée termine HTTPS et transmet à ton app en **HTTP**.

- Ne redirige pas vers HTTPS dans ton app : Cassiopée le fait déjà (risque de boucle). Si ton framework doit savoir que la requête était en HTTPS, fais-lui confiance pour les en-têtes `X-Forwarded-*` (Express `app.set('trust proxy', 1)`, Spring `server.forward-headers-strategy=framework`, Django `SECURE_PROXY_SSL_HEADER`).
- Si ton app génère des URLs absolues (liens d'e-mail, callbacks OAuth), donne-lui son URL publique par une variable (`BASE_URL`).
- **WebSocket** : supporté.
- **Front et API sur deux endpoints** = deux origines différentes : configure CORS côté API.

## 11. Communication entre tes apps

Tes apps et tes bases vivent dans **ton espace** (namespace `cassiopee-app-<login>`) :

- une app joint une autre app par **`http://<nom-de-l-app>`** : c'est le port 80 du service, pas le port du conteneur (`http://mon-api`, pas `http://mon-api:8080`) ;
- les espaces des autres élèves ne peuvent pas joindre tes apps, et inversement ;
- la sortie vers Internet est ouverte (API externes), **sauf vers les réseaux privés** (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) : une ressource interne à l'école n'est pas joignable.

## 12. Démarrage, arrêt et logs

- **Démarre vite et écoute tôt** : une app n'est déclarée prête qu'une fois son port ouvert, et son statut donne la raison si elle ne l'est pas (image introuvable, crash, rien n'écoute sur le port).
- **Arrête-toi proprement** sur `SIGTERM` : Kubernetes laisse 30 secondes avant de tuer le conteneur. Lance ton process en PID 1 (`CMD ["node", "server.js"]`, pas `CMD npm start` derrière un shell).
- **Logs sur stdout / stderr**, jamais dans un fichier.
- **Tâche planifiée** : l'horaire est une expression cron à **5 champs** (`*/15 * * * *`), en **UTC**. Les conteneurs sont aussi en UTC (`0 6 * * *` = 7 h à Paris l'hiver).

## De `docker-compose.yml` à Cassiopée

| Dans ton compose | Sur Cassiopée |
|---|---|
| un service `web` / `api` (ton image) | une **application** par service |
| un service `db: postgres` | une **base de données** PostgreSQL |
| `ports: "3000:3000"` | le port de l'app (`EXPOSE 3000`) |
| `depends_on: db` | des retries de connexion dans ton app |
| `volumes: ./uploads:/app/uploads` | une base de données (S3 indisponible pour l'instant) |
| `.env` | les variables d'environnement de l'app |
| `http://api:3000` entre services | `http://api` (port 80 du service) |
| un service `cron` | une application de type tâche planifiée (CronJob), qui se termine à chaque exécution |
