export type Exemple = { slug: 'livre-dor' | 'stats' | 'bot'; titre: string; tags: string; resume: string; code: string; enLigne?: string };

const repo = 'https://github.com/chanmachhu/cassiopee-site/tree/main/examples/livre-dor';

// enLigne stays unset until the deployed addresses are chosen: no "Voir en ligne" button without it.
export const exemples: Exemple[] = [
  { slug: 'livre-dor', titre: "Livre d'or", tags: 'front · API · PostgreSQL', resume: "La base est branchée par une référence, la clé d'API par un secret.", code: repo },
  { slug: 'stats', titre: 'Statistiques horaires', tags: 'tâche planifiée · toutes les heures', resume: "Calcule des statistiques dans la même base ; le livre d'or les affiche.", code: `${repo}/stats` },
  { slug: 'bot', titre: 'Bot Discord', tags: 'app sans port · secret', resume: 'Son jeton est un secret : ni dans Git, ni réaffiché après la saisie.', code: `${repo}/bot` },
];
