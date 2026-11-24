# Site de présentation de Cassiopée — plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construire le site de présentation de Cassiopée (Astro, direction D) et ses trois exemples, dans le dépôt public `chanmachhu/cassiopee-site`, avec des images publiées sur GHCR prêtes à être déployées sur Cassiopée.

**Architecture:** Un dépôt unique : `site/` (Astro, pages statiques, îlots React pour les composants React Bits, dessins SVG générés et commités), `examples/` (livre d'or : front nginx + API FastAPI + tâche de statistiques + bot Discord, en Python), `recettes/` (valeurs du formulaire Cassiopée), une CI GitHub Actions qui teste et publie cinq images. Le déploiement reste manuel, par Hugo, depuis l'intranet.

**Tech Stack:** Astro 7 (Node ≥ 22.23), React 19 via `@astrojs/react`, `motion` (requis par BlurText et RotatingText), Fontsource ; Python 3.12, FastAPI, psycopg 3, discord.py, httpx, pytest ; nginx-unprivileged ; GitHub Actions, GHCR.

**Spec:** `doc/2026-11-23-site-presentation-design.md` (même dépôt Cassiopée, branche `docs/site-presentation`).

## Global Constraints

- Dépôt : `chanmachhu/cassiopee-site`, public, compte personnel ; dossier local `/home/hugo/epita/SIGL/SIOPS/cassiopee-site`. Travail sur la branche `feat/site`, jamais directement sur `main` ; Hugo pousse et merge.
- Images : `ghcr.io/chanmachhu/cassiopee-site`, `…/cassiopee-livre-dor-front`, `…/cassiopee-livre-dor-api`, `…/cassiopee-livre-dor-stats`, `…/cassiopee-livre-dor-bot` ; `linux/amd64` ; tag = 7 premiers caractères du SHA du commit ; jamais `latest` dans les recettes.
- Toute image : utilisateur non root, écoute sur `0.0.0.0`, un seul port (8080 pour nginx, 8000 pour l'API), aucune écriture sur disque persistant.
- Aucun secret dans le dépôt, les images ou les logs : `ADMIN_TOKEN` et `DISCORD_TOKEN` sont saisis dans Cassiopée comme secrets ; la base arrive par la référence `DATABASE_URL` (chaîne de connexion `postgresql://user:pass@host:5432/db`).
- Noms d'apps Cassiopée : une lettre minuscule en premier, puis minuscules, chiffres, tirets, fin par une lettre ou un chiffre. Noms d'adresses interdits : `www`, `api`, `app`, `admin`, `docs`, `status`, `auth`, `login`, `vault`, `registry`, `staging`, `prod` (liste complète dans `endpoint_service.py`).
- Appel interne entre apps : `http://<nom-de-l-app>` (Service sur le port 80 vers le port du conteneur).
- Copie du site en français ; chiffres arabes ; direction D (maquette `docs/maquette/Mythologie.dc.html`, version 38 du canvas) : Cinzel (titres), EB Garamond (texte), JetBrains Mono (code), polices auto-hébergées.
- Aucun script en ligne dans le HTML produit (`<script>` sans `src` interdit) ; aucune requête vers un domaine tiers.
- Animations : déclenchées une fois par section à l'arrivée à l'écran ; sans JavaScript ou sous `prefers-reduced-motion`, tout le contenu est visible dans son état final.
- Commentaires de code et messages de commit en anglais, courts ; aucune référence de ticket dans le code.
- Actions GitHub épinglées par SHA ; permissions minimales.

## Review Focus

- Un message du livre d'or contenant du HTML, du Markdown Discord ou `@everyone` doit s'afficher comme du texte brut dans le front et dans le bot, sans mention ni balise interprétée (tests dans les tâches 6, 7 et 9).
- Auteur ou texte vide, fait d'espaces, trop long, ou plein d'emojis : refusé avec 422 si vide ou trop long après suppression des espaces, accepté sinon (tâche 6).
- API injoignable : le front affiche « Le livre d'or ne répond pas pour l'instant », le bot répond un message d'erreur visible seulement par l'utilisateur (tâches 7 et 9).
- `ADMIN_TOKEN` absent ou vide : la suppression est refusée (403), jamais ouverte à tous (tâche 6).
- JavaScript désactivé ou `prefers-reduced-motion` : aucune section ne reste invisible (tâche 5).

---

### Task 0 (contrôleur) : environnement

- [ ] **Step 1:** Installer Node 22 avec nvm (`nvm install 22 && nvm use 22`) ; vérifier `node --version` ≥ `v22.23.4` (Astro 7 l'exige ; seule la 20 est installée).
- [ ] **Step 2:** Créer le dépôt : `gh repo create chanmachhu/cassiopee-site --public --add-readme --description "Site de présentation et exemples de Cassiopée"`, le cloner dans `/home/hugo/epita/SIGL/SIOPS/cassiopee-site`, créer la branche `feat/site`.
- [ ] **Step 3:** Copier la maquette et le générateur : `.superpowers/site-mockups/project/Mythologie.dc.html` → `docs/maquette/Mythologie.dc.html`, `.superpowers/site-mockups/generator/{gen.py,template.html}` → `site/tools/`. Copier le design et ce plan dans `docs/`. Commit `chore: import mockup, generator and design docs`.

### Task 1 : squelette du dépôt et guide mis à jour

**Files:**
- Create: `README.md` (remplace celui de GitHub), `.gitignore`, `.github/dependabot.yml`, `site/src/content/guide/preparer-son-app.md`

**Interfaces:**
- Produces: le guide en Markdown avec un frontmatter `title: Préparer son application pour Cassiopée` et `description` (une phrase), lu par la tâche 12.

- [ ] **Step 1: README** — sections : à quoi sert le dépôt ; arborescence ; développement local (`nvm use 22`, `cd site && npm ci && npm run dev`, `pytest` dans chaque exemple) ; publication des images (CI sur `main`, tag = SHA court) ; **première publication : passer chaque paquet GHCR en public** (GitHub → Packages → Package settings → Change visibility) ; déploiement (renvoi vers `recettes/README.md`) ; **nettoyage annuel : le site et les exemples ne doivent pas être supprimés** ; passation (transfert du dépôt, redéploiement dans le nouvel espace).
- [ ] **Step 2: Dependabot** — écosystèmes `npm` (`/site`), `pip` (`/examples/livre-dor/api`, `/examples/livre-dor/stats`, `/examples/livre-dor/bot`), `docker` (chaque dossier avec un Dockerfile), `github-actions` (`/`) ; fréquence hebdomadaire.
- [ ] **Step 3: Guide** — partir de `doc/preparer-son-app.md` (branche `docs/app-prerequisites` du dépôt Cassiopée) et le mettre à jour avec ce qui est en prod 0.8.1 :
  - section 4 : trois sortes de variables — **Valeur** (écrite dans Git, rien de sensible), **Secret** (saisi une fois, rangé dans Vault, jamais réaffiché ; une valeur vide le conserve), **Base** (référence vers une information de connexion d'une base de l'espace : chaîne de connexion, hôte, port, utilisateur, mot de passe, nom de la base) ; supprimer l'avertissement « stockées en clair, pas de secret » ;
  - section 5 : brancher la base par une référence plutôt que recopier ses identifiants ;
  - section 7 (S3) : remplacer par une phrase « Le stockage S3 est indisponible pour l'instant » ;
  - section 9 : quota perso 1 vCPU, 1,5 Go, 3 apps, 3 bases ; espace d'équipe = groupe de l'intranet, même quota pour toutes les équipes : 6 vCPU, 9 Go, 18 apps, 18 bases, partagé entre les membres, onglets Personnel et Équipe, colonne « Créé par » ;
  - noms : une lettre minuscule en premier, minuscules, chiffres et tirets, fin par une lettre ou un chiffre ; noms d'adresses réservés ;
  - section 11 : `http://<nom-de-l-app>` (port 80 du Service) ;
  - tâches planifiées : expression cron à 5 champs, heure UTC.
- [ ] **Step 4: Vérifier** que chaque chiffre du guide correspond à `backend/src/config/settings.py` (quotas) et à `backend/src/models/schemas.py` (noms, cron) du dépôt Cassiopée.
- [ ] **Step 5: Commit** `docs: repository skeleton and updated student guide`. **Porte : Hugo valide le guide** (les tâches 2 à 11 n'attendent pas).

### Task 2 : socle du site Astro

**Files:**
- Create: `site/package.json`, `site/package-lock.json`, `site/astro.config.mjs`, `site/tsconfig.json`, `site/src/styles/tokens.css`, `site/src/styles/global.css`, `site/src/layouts/Base.astro`, `site/src/components/Header.astro`, `site/src/components/Footer.astro`, `site/src/pages/404.astro`, `site/tests/dist.test.mjs`, `site/Dockerfile`, `site/nginx/default.conf`

**Interfaces:**
- Produces: `Base.astro` (props `title: string`, `description: string`, slot) ; `tokens.css` (variables `--marble`, `--stone-*`, `--ivy-*`, `--gold`, `--ink`, `--font-heading`, `--font-body`, `--font-mono`, valeurs reprises de la maquette) ; script `npm test` = `node --test tests/` après `npm run build`.

- [ ] **Step 1: Initialiser** Astro (dernière 7.x), `@astrojs/react`, `react`, `react-dom`, `motion`, `@fontsource/cinzel`, `@fontsource/eb-garamond`, `@fontsource/jetbrains-mono` ; `astro.config.mjs` : `output: 'static'`, `build.inlineStylesheets: 'never'`, intégration React. Scripts : `dev`, `build`, `test` (`npm run build && node --test tests/`).
- [ ] **Step 2: Écrire `tests/dist.test.mjs`** (échoue tant que `dist/` n'existe pas) :

```js
test('every page exists', () => { for (const p of ['index.html', '404.html']) assert.ok(existsSync(`dist/${p}`)); });
test('no inline script in any page', () => { for (const f of htmlFiles('dist')) assert.doesNotMatch(read(f), /<script(?![^>]*\bsrc=)[^>]*>/); });
test('no third-party request', () => { for (const f of htmlFiles('dist')) assert.doesNotMatch(read(f), /(src|href)="https?:\/\/(?!cassiopee)/); });
```
- [ ] **Step 3: Layout, en-tête, pied, 404** d'après la maquette (logo constellation, navigation « Préparer son app », « Exemples », « L'oracle », bouton « Ouvrir l'intranet » vers `https://intranet.sigl.epita.fr`) ; 404 : « Cette page n'existe pas » et un lien vers l'accueil.
- [ ] **Step 4: `npm test`** → PASS.
- [ ] **Step 5: Image** — `Dockerfile` en deux étapes (`node:22-alpine` pour `npm ci && npm run build`, `nginxinc/nginx-unprivileged:stable-alpine` pour servir `dist/`), port 8080. `nginx/default.conf` : `listen 8080;` ; en-têtes sur toutes les réponses : `Content-Security-Policy "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'none'"`, `X-Content-Type-Options nosniff`, `Referrer-Policy strict-origin-when-cross-origin`, `Permissions-Policy "camera=(), microphone=(), geolocation=()"` ; `Cache-Control: no-cache` sur le HTML, `public, max-age=31536000, immutable` sur `/_astro/` ; `error_page 404 /404.html`.
- [ ] **Step 6: Commit** `feat(site): Astro base layout, tests and nginx image`.

### Task 3 : dessins générés

**Files:**
- Modify: `site/tools/gen.py` (sortie TypeScript au lieu de la page de maquette)
- Create: `site/src/drawings/generated.ts` (produit, commité), `site/tools/README.md`

**Interfaces:**
- Produces: `export const drawings: Record<DrawingName, string>` dans `generated.ts`, clés = celles de `DRAW` dans `gen.py` (`DEFS`, `PEDIMENT`, `ARCH_HERO`, `STEPS_HERO`, `COL_OL`, `COL_IL`, `COL_IR`, `COL_OR`, `HERO_BACK`, `HERO_FRONT`, `PLAQUE_BACK`, `PLAQUE_FRONT`, `ROOF1`, `ROOF2`, `ROOF3`, `ARCH_CARD`, `STEPS_CARD1`, `STEPS_CARD2`, `STEPS_CARD3`, `CARD1_L`, `CARD1_R`, `CARD2_L`, `CARD2_R`, `CARD3_L`, `CARD3_R`, `CARD3_BACK`, `CARD3_FRONT`, `CROWN`, `DUST`) ; utilisées avec `set:html` dans les composants Astro.

- [ ] **Step 1:** Ajouter à `gen.py` un mode `python3 gen.py --ts site/src/drawings/generated.ts` qui écrit le dictionnaire `DRAW` en TypeScript (chaînes JSON-échappées) ; garder le mode maquette.
- [ ] **Step 2: Test** — `site/tests/drawings.test.mjs` : relancer le générateur dans un fichier temporaire et vérifier qu'il est identique à `generated.ts` (sortie déterministe, fichier commité à jour). Exécuter → FAIL puis PASS.
- [ ] **Step 3:** `tools/README.md` : quand et comment régénérer (une commande).
- [ ] **Step 4: Commit** `feat(site): generated SVG drawings`.

### Task 4 : page d'accueil (statique)

**Files:**
- Create: `site/src/pages/index.astro`, `site/src/components/home/{Hero,Plaque,Piliers,TempleCard,Rituel,Stele,ExemplesApercu,ExempleCard,Accueil,Oracle,Fin}.astro`, `site/src/data/exemples.ts`, `site/src/styles/home.css`
- Test: `site/tests/home.test.mjs`

**Interfaces:**
- Consumes: `drawings` (tâche 3), `Base.astro` (tâche 2).
- Produces: `export type Exemple = { slug: 'livre-dor' | 'stats' | 'bot'; titre: string; tags: string; resume: string; code: string; enLigne?: string }` et `export const exemples: Exemple[]` dans `data/exemples.ts` (sans `enLigne` tant que les adresses ne sont pas choisies) ; ancres de section `#oracle` et classes de section `sec` + attribut `data-reveal="<nom>"` sur chaque section (utilisés par la tâche 5).

- [ ] **Step 1: Test** `home.test.mjs` (sur `dist/index.html`) :

```js
test('home keeps the mockup copy', () => { for (const s of ['Mets ton', 'parmi les étoiles', 'Les trois piliers', 'Le rituel, en trois étapes', 'Trois exemples, en ligne', "Consulte l'oracle", "Ton temple t'attend"]) assert.match(html, new RegExp(s)); });
test('no "Voir en ligne" without an address', () => { assert.equal(count(html, 'Voir en ligne'), exemples.filter(e => e.enLigne).length); });
test('recipe buttons point to the examples page', () => { for (const s of ['livre-dor', 'stats', 'bot']) assert.match(html, new RegExp(`href="/exemples#${s}"`)); });
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Reproduire la maquette section par section (textes, chiffres 3/2/0/1, cartes temples, stèles, cartes d'exemples, accueil et FAQ) avec les dessins de `drawings` ; liens « Code » vers `https://github.com/chanmachhu/cassiopee-site/tree/main/examples/livre-dor/<dossier>` ; boutons « Recette » vers `/exemples#<slug>`.
- [ ] **Step 4:** `npm test` → PASS ; capture de la page (Chromium headless, 1440 px et 390 px) comparée à la maquette.
- [ ] **Step 5: Commit** `feat(site): home page from mockup D`.

### Task 5 : animations

**Files:**
- Create: `site/src/components/reactbits/{BlurText,RotatingText,ShinyText,StarBorder,ClickSpark}.tsx` (+ leurs `.css`, variante TS-CSS de reactbits.dev, en-tête de licence conservé), `site/src/scripts/reveal.ts`, `site/src/scripts/regrow.ts`, `site/src/styles/motion.css`
- Modify: composants de la tâche 4
- Test: `site/tests/motion.test.mjs`

**Interfaces:**
- Consumes: `data-reveal` et `.sec` (tâche 4).
- Produces: `reveal.ts` ajoute `armed` sur `<html>` puis `in` sur chaque section quand 20 % est visible (`IntersectionObserver`, une fois, `rootMargin: '0px 0px -10% 0px'`) ; rien si `prefers-reduced-motion`.

- [ ] **Step 1: Test** `motion.test.mjs` (sur les CSS et HTML produits) :

```js
test('paused animations only once the page is armed', () => { assert.match(css, /\.armed \.sec:not\(\.in\)/); assert.doesNotMatch(css, /^\s*\.sec:not\(\.in\)/m); });
test('reduced motion turns every animation off', () => { assert.match(css, /@media \(prefers-reduced-motion: ?reduce\)[^}]*animation:\s*none/); });
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Porter les effets de la maquette : croissance du lierre (tiges `pathLength="1"`, feuilles qui se déplient), balancement des brins, rayons, poussière d'or, apparition des blocs, ombre du lierre après la croissance ; îlots `client:visible` : BlurText (titre, mot par mot), RotatingText (« API » → app, bot, site, deux tours puis retour à « API »), ShinyText (accroche), StarBorder et ClickSpark (bouton principal). Survol : `regrow.ts` rejoue vite la croissance du lierre d'un temple à l'entrée (classe `rg`, rien à la sortie), palmette et laurier qui frémissent.
- [ ] **Step 4:** `npm test` → PASS ; vérification visuelle (état final identique à la tâche 4 ; JavaScript désactivé → tout visible).
- [ ] **Step 5: Commit** `feat(site): React Bits islands and section animations`.

### Task 6 : API du livre d'or

**Files:**
- Create: `examples/livre-dor/schema.sql`, `examples/livre-dor/api/{app.py,store.py,limits.py,requirements.txt,Dockerfile}`, `examples/livre-dor/api/tests/{conftest.py,test_api.py,test_pgstore.py}`

**Interfaces:**
- Produces (HTTP, consommé par les tâches 7 et 9) :
  - `GET /api/messages?limit=n` → 200 `[{ "id": int, "auteur": str, "texte": str, "cree_le": iso8601 }]`, plus récents d'abord, `limit` par défaut 20, max 50 ;
  - `POST /api/messages` `{ "auteur", "texte" }` → 201 message créé ; 422 si `auteur` vide ou > 40 caractères, ou `texte` vide ou > 280 caractères, après suppression des espaces ; 429 au-delà de la limite ;
  - `DELETE /api/messages/{id}` avec `Authorization: Bearer <ADMIN_TOKEN>` → 204 ; 401 jeton absent ou faux ; 403 si `ADMIN_TOKEN` n'est pas configuré ; 404 inconnu ;
  - `GET /api/stats` → 200 `[{ "jour": "YYYY-MM-DD", "messages": int }]`, 30 derniers jours ;
  - `GET /health` → 200.
- Produces (Python) : `create_app(store: Store, admin_token: str | None, limiter: Limiter) -> FastAPI` ; `class Store(Protocol)` avec `list_messages(limit) -> list[Message]`, `add_message(auteur, texte) -> Message`, `delete_message(id) -> bool`, `list_stats(days) -> list[DayStat]` ; `MemoryStore`, `PgStore(dsn)`.
- Environnement : `DATABASE_URL`, `ADMIN_TOKEN`, `RATE_GLOBAL_PER_MIN` (défaut 30), `RATE_PER_CLIENT_PER_MIN` (défaut 5), `TRUST_FORWARDED_FOR` (défaut `false` : la limite par visiteur ne s'applique que si l'adresse réelle est vérifiée au déploiement).

- [ ] **Step 1: Tests** `test_api.py` (avec `MemoryStore`) :

```python
def test_post_then_list_newest_first(client): ...  # two posts, GET returns the second first
def test_rejects_blank_or_too_long(client): ...      # "   ", 41-char auteur, 281-char texte -> 422; "🏛️🌿" alone -> 201
def test_keeps_markup_as_text(client): ...           # texte "<img src=x onerror=alert(1)> @everyone" returned unchanged
def test_delete_requires_token(client): ...          # no header -> 401, wrong -> 401, right -> 204, again -> 404
def test_delete_disabled_without_token(): ...         # create_app(..., admin_token=None) -> DELETE gives 403
def test_global_rate_limit(client): ...              # 31st POST within a minute -> 429
def test_per_client_limit_only_when_trusted(): ...    # X-Forwarded-For honoured only with TRUST_FORWARDED_FOR=true
```
`test_pgstore.py` : mêmes opérations sur `PgStore`, ignoré si `TEST_DATABASE_URL` est absent (exécuté en CI avec PostgreSQL).
- [ ] **Step 2:** `pytest` → FAIL.
- [ ] **Step 3:** Implémenter. Le schéma (`schema.sql` : tables `messages(id serial, auteur text, texte text, cree_le timestamptz default now())` et `stats(jour date primary key, messages int)`) est appliqué au démarrage, avec trois tentatives espacées de 5 s si la base n'est pas encore prête. Jeton comparé avec `hmac.compare_digest`. Limiteur en mémoire par fenêtre glissante d'une minute.
- [ ] **Step 4:** `pytest` → PASS.
- [ ] **Step 5: Image** — `python:3.12-slim`, utilisateur non root, `uvicorn app:app --host 0.0.0.0 --port 8000` ; build depuis `examples/livre-dor` pour inclure `schema.sql`.
- [ ] **Step 6: Commit** `feat(livre-dor): guestbook API`.

### Task 7 : front du livre d'or

**Files:**
- Create: `examples/livre-dor/front/{index.html,app.js,style.css,Dockerfile}`, `examples/livre-dor/front/nginx/default.conf.template`, `examples/livre-dor/front/tests/app.test.mjs`

**Interfaces:**
- Consumes: l'API de la tâche 6 sous `/api/`.
- Produces: `app.js` exporte `renderMessages(list, container)`, `renderStats(list, container)` (texte uniquement, `textContent`) et `async loadMessages(fetchImpl, container)` (appelle `/api/messages`, affiche le message d'indisponibilité en cas d'échec).

- [ ] **Step 1: Tests** `app.test.mjs` (`node --test`, DOM minimal fourni par un objet factice) :

```js
test('messages are rendered as text', () => { renderMessages([{ auteur: '<b>x</b>', texte: '<img src=x onerror=alert(1)>', cree_le: '2026-11-23T10:00:00Z' }], c); assert.equal(c.textContent.includes('<img src=x onerror=alert(1)>'), true); });
test('the source never uses innerHTML', () => { assert.doesNotMatch(readFileSync('app.js', 'utf8'), /innerHTML|insertAdjacentHTML|outerHTML/); });
test('an unreachable API shows a clear message', async () => { await loadMessages(() => Promise.reject(new TypeError('Failed to fetch')), c); assert.equal(c.textContent, "Le livre d'or ne répond pas pour l'instant."); });
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Page : formulaire (auteur, message, compteurs de caractères 40/280), liste des derniers messages, statistiques des 30 derniers jours (venant de la tâche de statistiques), même direction artistique en plus simple (marbre, Cinzel, or discret) ; si l'API ne répond pas : « Le livre d'or ne répond pas pour l'instant. » ; 429 : « Trop de messages en ce moment, réessaie dans une minute. »
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5: Image** — `nginxinc/nginx-unprivileged:stable-alpine`, port 8080 ; `default.conf.template` : `location /api/ { proxy_pass ${API_URL}; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; }`, mêmes en-têtes de sécurité que le site ; `API_URL` (défaut `http://livre-dor-api`) substituée au démarrage par l'image nginx.
- [ ] **Step 6: Commit** `feat(livre-dor): guestbook front`.

### Task 8 : tâche de statistiques

**Files:**
- Create: `examples/livre-dor/stats/{stats.py,requirements.txt,Dockerfile}`, `examples/livre-dor/stats/tests/test_stats.py`

**Interfaces:**
- Consumes: `schema.sql` (tâche 6).
- Produces: `refresh(conn) -> int` : recalcule le nombre de messages par jour des 30 derniers jours dans `stats` (une requête `INSERT … SELECT … ON CONFLICT (jour) DO UPDATE`), renvoie le nombre de jours écrits ; `main()` lit `DATABASE_URL`, applique le schéma, appelle `refresh`, sort avec le code 0.

- [ ] **Step 1: Test** (ignoré sans `TEST_DATABASE_URL`) : trois messages sur deux jours → `refresh` renvoie 2 et `stats` contient `(jour1, 2)`, `(jour2, 1)` ; un second appel donne le même résultat.
- [ ] **Step 2:** Run en CI ou avec une base locale → FAIL, implémenter, PASS.
- [ ] **Step 3: Image** — `python:3.12-slim`, non root, `CMD ["python", "stats.py"]`, build depuis `examples/livre-dor`.
- [ ] **Step 4: Commit** `feat(livre-dor): hourly stats job`.

### Task 9 : bot Discord

**Files:**
- Create: `examples/livre-dor/bot/{bot.py,livredor.py,requirements.txt,Dockerfile}`, `examples/livre-dor/bot/tests/test_livredor.py`

**Interfaces:**
- Consumes: `GET /api/messages?limit=5` (tâche 6) à `API_URL` (défaut `http://livre-dor-api`).
- Produces: `async fetch_last(client: httpx.AsyncClient, api_url: str, n: int = 5) -> list[dict]` et `format_messages(messages: list[dict]) -> str` dans `livredor.py` ; `bot.py` enregistre la commande `/livredor` et démarre avec `DISCORD_TOKEN`.

- [ ] **Step 1: Tests** :

```python
def test_format_escapes_discord_markup(): ...   # "**x** @everyone <@1>" comes out escaped, no live mention
def test_format_fits_discord_limit(): ...       # 50 long messages -> result <= 2000 chars
async def test_fetch_last_handles_api_down(): ...  # httpx.MockTransport raising ConnectError -> raises LivreDorIndisponible
```
- [ ] **Step 2:** `pytest` → FAIL.
- [ ] **Step 3:** Implémenter ; réponse de `/livredor` avec `allowed_mentions=discord.AllowedMentions.none()` ; si l'API ne répond pas, réponse éphémère « Le livre d'or ne répond pas pour l'instant. » ; aucun port, aucune intention privilégiée.
- [ ] **Step 4:** `pytest` → PASS.
- [ ] **Step 5: Image** — `python:3.12-slim`, non root, `CMD ["python", "bot.py"]`.
- [ ] **Step 6: Commit** `feat(livre-dor): Discord bot`.

### Task 10 : CI et publication des images

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1:** Jobs : `site` (Node 22 : `npm ci`, `npm test`) ; `python` (Python 3.12, service PostgreSQL 16, `TEST_DATABASE_URL` défini, `pytest` dans `api`, `stats`, `bot`) ; `front` (`node --test` dans `front`) ; `images` (après les trois autres, matrice des cinq images, `docker/build-push-action`, `platforms: linux/amd64`, contexte `site/` ou `examples/livre-dor/`, tag `ghcr.io/chanmachhu/<image>:<sha7>`, push seulement sur `main`) ; pour `cassiopee-site`, lancer le conteneur et vérifier par `curl -sI` la présence de `Content-Security-Policy` et `X-Content-Type-Options`, et que le conteneur tourne sous un UID ≠ 0.
- [ ] **Step 2:** Permissions : `contents: read` par défaut, `packages: write` sur le job `images` seulement ; toutes les actions épinglées par SHA (commentaire avec la version).
- [ ] **Step 3:** Valider la syntaxe (`actionlint` si disponible, sinon relecture) ; le premier passage réel a lieu quand Hugo pousse `feat/site`.
- [ ] **Step 4: Commit** `ci: test and publish the five images`.

### Task 11 : recettes

**Files:**
- Create: `recettes/README.md`, `recettes/{cassiopee-site,livre-dor-db,livre-dor-api,livre-dor-front,livre-dor-stats,livre-dor-bot}.md`

- [ ] **Step 1:** Une recette par ressource, avec les valeurs exactes du formulaire :

| Ressource | Espace | Type | Image (tag = SHA) | Port | Variables | Secrets | Références | Adresse |
|---|---|---|---|---|---|---|---|---|
| `cassiopee-site` | perso | App | `cassiopee-site` | 8080 | – | – | – | choisie au déploiement |
| `livre-dor-db` | équipe | Base PostgreSQL | – | – | – | – | – | – |
| `livre-dor-api` | équipe | App | `cassiopee-livre-dor-api` | 8000 | – | `ADMIN_TOKEN` | `DATABASE_URL` → `livre-dor-db` / chaîne de connexion | aucune |
| `livre-dor-front` | équipe | App | `cassiopee-livre-dor-front` | 8080 | `API_URL=http://livre-dor-api` | – | – | choisie au déploiement |
| `livre-dor-stats` | équipe | Tâche planifiée `0 * * * *` | `cassiopee-livre-dor-stats` | aucun | – | – | `DATABASE_URL` → `livre-dor-db` / chaîne de connexion | aucune |
| `livre-dor-bot` | équipe | App sans port | `cassiopee-livre-dor-bot` | aucun | `API_URL=http://livre-dor-api` | `DISCORD_TOKEN` | – | aucune |
Ressources : valeurs par défaut (100 m de CPU, 128 Mo) ; 256 Mo de mémoire pour `livre-dor-api` et `livre-dor-bot`.
- [ ] **Step 2:** `README.md` : ordre de déploiement (base, API, front, stats, bot, site), comment changer le tag d'une image pour une mise à jour, report des adresses dans `site/src/data/exemples.ts` puis redéploiement du site, vérification de `TRUST_FORWARDED_FOR`.
- [ ] **Step 3: Commit** `docs: deployment recipes`.

### Task 12 : page « Préparer son app » (après validation de sa maquette)

**Porte :** maquette de la page sur le canvas (contrôleur), validée par Hugo ; guide de la tâche 1 validé.

**Files:**
- Create: `site/src/content.config.ts`, `site/src/pages/preparer-son-app.astro`, `site/src/styles/guide.css`
- Test: ajouter à `site/tests/dist.test.mjs`

- [ ] **Step 1: Test** : `dist/preparer-son-app/index.html` existe, contient le titre du guide et un sommaire avec un lien par section `##`.
- [ ] **Step 2:** Run → FAIL ; collection de contenu `guide`, page rendue dans la mise en page validée ; Run → PASS.
- [ ] **Step 3: Commit** `feat(site): student guide page`.

### Task 13 : page « Exemples » (après validation de sa maquette)

**Porte :** maquette validée par Hugo ; recettes de la tâche 11.

**Files:**
- Create: `site/src/pages/exemples.astro`, `site/src/components/exemples/Recette.astro`
- Modify: `site/src/data/exemples.ts` (ajout de `recette: { ressource: string; champs: [string, string][] }[]`, repris des recettes)

- [ ] **Step 1: Test** : `dist/exemples/index.html` contient les ancres `id="livre-dor"`, `id="stats"`, `id="bot"`, et pour chaque exemple le nom de chaque variable de sa recette (`DATABASE_URL`, `ADMIN_TOKEN`, `API_URL`, `DISCORD_TOKEN`) sans aucune valeur de secret.
- [ ] **Step 2:** Run → FAIL ; implémenter ; Run → PASS.
- [ ] **Step 3: Commit** `feat(site): examples page`.

### Task 14 (Hugo, avec le contrôleur) : déploiement

- [ ] Hugo pousse `feat/site`, ouvre et merge la PR ; la CI publie les images ; Hugo les passe en public.
- [ ] Déploiement des exemples puis du site selon `recettes/README.md` ; vérification de l'adresse réelle des visiteurs (`TRUST_FORWARDED_FOR`).
- [ ] Adresses reportées dans `site/src/data/exemples.ts`, site redéployé.
- [ ] Dépôt Cassiopée : dans !30, retirer `doc/preparer-son-app.md` et faire pointer le README vers le site.
- [ ] Wiki SiOps : site et exemples exclus du nettoyage annuel.
