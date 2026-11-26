CREATE TABLE IF NOT EXISTS messages (
    id serial PRIMARY KEY,
    auteur text NOT NULL,
    texte text NOT NULL,
    cree_le timestamptz NOT NULL DEFAULT now()
);

-- Filled hourly by the stats job.
CREATE TABLE IF NOT EXISTS stats (
    jour date PRIMARY KEY,
    messages int NOT NULL
);
