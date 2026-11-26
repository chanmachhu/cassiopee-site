export type Champ = { nom: string; v: string; fin?: string; genre?: 'texte' | 'aucun' | 'seg' | 'case'; demi?: boolean };
// A Secret variable has no value: the card always shows the mask.
export type Variable = { nom: string; genre: 'Valeur' | 'Secret' | 'Base'; v?: string; fin?: string };
export type Ressource = { nom: string; type: string; code: string; champs: Champ[]; vars?: Variable[] };
export type Noeud = { nk: string; nn: string; ns: string; via?: string };
export type Exemple = {
  slug: 'livre-dor' | 'stats' | 'bot'; titre: string; tags: string; resume: string; code: string; enLigne?: string;
  pitch: string; puces: string[];
  // ext: node outside the team space; via labels the arrow into each node (zone: arrows between nodes).
  archi: { ext?: Noeud & { double?: boolean }; zone: Noeud[] };
  intro: string; recette: Ressource[];
};

const repo = 'https://github.com/chanmachhu/cassiopee-site/tree/main/examples/livre-dor';
const img = (n: string) => ({ nom: 'Image', v: `ghcr.io/chanmachhu/cassiopee-livre-dor-${n}:<sha>` });
const base: Variable = { nom: 'DATABASE_URL', genre: 'Base', v: 'livre-dor-db', fin: 'Chaîne de connexion' };
const apiUrl: Variable = { nom: 'API_URL', genre: 'Valeur', v: 'http://livre-dor-api' };
const db: Noeud = { nk: 'Base', nn: 'livre-dor-db', ns: 'PostgreSQL', via: 'DATABASE_URL' };
const api: Noeud = { nk: 'App · API', nn: 'livre-dor-api', ns: 'port 8000', via: 'http://livre-dor-api' };
const aucunPort: Champ = { nom: 'Port', v: "Mon app n'écoute sur aucun port", genre: 'case' };

// enLigne stays unset until the deployed addresses are chosen: no "Voir en ligne" button without it.
export const exemples: Exemple[] = [
  {
    slug: 'livre-dor', titre: "Livre d'or", tags: 'front · API · PostgreSQL', resume: "La base est branchée par une référence, la clé d'API par un secret.", code: repo,
    pitch: "Un livre d'or ouvert à toute l'école : le front appelle l'API par son nom interne, l'API range les messages dans PostgreSQL.",
    puces: ['Deux apps qui se parlent', 'Base PostgreSQL', 'Référence', 'Secret'],
    archi: { ext: { nk: 'Extérieur', nn: 'Navigateur', ns: 'un élève', via: 'HTTPS' }, zone: [{ nk: 'App · front', nn: 'livre-dor-front', ns: 'port 8080' }, api, db] },
    intro: "Dans l'espace d'équipe, dans cet ordre : la base, puis l'API, puis le front.",
    recette: [
      { nom: 'livre-dor-db', type: 'Base de données', code: `${repo.replace('/tree/', '/blob/')}/schema.sql`, champs: [{ nom: 'Moteur', v: 'PostgreSQL', genre: 'texte' }, { nom: 'Espace', v: 'Équipe', genre: 'seg' }] },
      {
        nom: 'livre-dor-api', type: 'Application', code: `${repo}/api`,
        champs: [img('api'), { nom: 'Port', v: '8000', demi: true }, { nom: 'Mémoire', v: '256 Mo', demi: true }, { nom: 'Adresse', v: "Pas d'adresse : l'API reste interne", genre: 'aucun' }],
        vars: [base, { nom: 'ADMIN_TOKEN', genre: 'Secret' }],
      },
      {
        nom: 'livre-dor-front', type: 'Application', code: `${repo}/front`,
        champs: [img('front'), { nom: 'Port', v: '8080', demi: true }, { nom: 'Adresse', v: '<à choisir>', fin: '.cassiopee.siops.sigl.epita.fr' }],
        vars: [apiUrl],
      },
    ],
  },
  {
    slug: 'stats', titre: 'Statistiques horaires', tags: 'tâche planifiée · toutes les heures', resume: "Calcule des statistiques dans la même base ; le livre d'or les affiche.", code: `${repo}/stats`,
    pitch: "Toutes les heures, une tâche compte les messages du livre d'or dans sa base ; le front affiche le résultat.",
    puces: ['Tâche planifiée', 'Base partagée', 'Référence'],
    archi: { zone: [{ nk: 'Tâche planifiée', nn: 'livre-dor-stats', ns: 'toutes les heures' }, db] },
    intro: "À créer après le livre d'or : la tâche se branche sur sa base, livre-dor-db.",
    recette: [{ nom: 'livre-dor-stats', type: 'Tâche planifiée', code: `${repo}/stats`, champs: [{ nom: 'Horaire', v: '0 * * * *', fin: '(heure UTC)' }, img('stats'), aucunPort], vars: [base] }],
  },
  {
    slug: 'bot', titre: 'Bot Discord', tags: 'app sans port · secret', resume: 'Son jeton est un secret : ni dans Git, ni réaffiché après la saisie.', code: `${repo}/bot`,
    pitch: "La commande `/livredor` affiche les derniers messages, en appelant l'API du livre d'or par son nom interne.",
    puces: ['App sans port', 'Secret', 'Appel interne'],
    archi: { ext: { nk: 'Extérieur', nn: 'Discord', ns: 'serveur SiOps', via: 'sortie Internet', double: true }, zone: [{ nk: 'App · sans port', nn: 'livre-dor-bot', ns: "pas d'adresse" }, api] },
    intro: 'À créer après le livre d\'or : le bot appelle livre-dor-api. Le jeton Discord se saisit comme secret.',
    recette: [{ nom: 'livre-dor-bot', type: 'Application', code: `${repo}/bot`, champs: [img('bot'), aucunPort, { nom: 'Mémoire', v: '256 Mo', demi: true }], vars: [apiUrl, { nom: 'DISCORD_TOKEN', genre: 'Secret' }] }],
  },
];
