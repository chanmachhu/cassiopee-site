// Short TOC label and anchor per `##` heading of the guide. A heading missing here gets its own text and a slug.
const META: Record<string, [id: string, label: string]> = {
  'À quoi sert Cassiopée': ['a-quoi-sert', 'À quoi sert Cassiopée'],
  'Ce qui change par rapport à ton poste': ['ce-qui-change', 'Ce qui change'],
  'Checklist': ['checklist', 'Checklist'],
  "L'image": ['image', "L'image"],
  'Écouter sur le bon port, et sur 0.0.0.0': ['port', 'Le bon port'],
  'Sans root': ['sans-root', 'Sans root'],
  "La configuration par variables d'environnement": ['variables', 'Les variables'],
  'La base de données': ['base', 'La base de données'],
  'Pas de disque persistant pour une app': ['disque', 'Pas de disque'],
  'Le stockage S3': ['s3', 'Le stockage S3'],
  'Plusieurs instances': ['instances', 'Plusieurs instances'],
  'Ressources et quotas': ['quotas', 'Ressources et quotas'],
  'HTTP derrière le HTTPS de Cassiopée': ['https', 'HTTP derrière HTTPS'],
  'Communication entre tes apps': ['reseau', 'Entre tes apps'],
  'Démarrage, arrêt et logs': ['demarrage', 'Démarrage et logs'],
  'De docker-compose.yml à Cassiopée': ['compose', 'De compose à Cassiopée'],
};

// "5. La base" -> { n: '5', text: 'La base' }; unnumbered headings have no n.
export function sectionMeta(heading: string) {
  const m = heading.match(/^(\d+)\.\s+(.*)$/);
  const text = m ? m[2] : heading;
  const [id, label] = META[text] ?? [text.toLowerCase().normalize('NFD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''), text];
  return { n: m?.[1], id, label };
}
