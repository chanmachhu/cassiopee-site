import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Astro inlines its island loader (<script> without src); the CSP (script-src 'self') needs it as a file.
// A blocking external script runs at the same point, before the islands, so client:visible is unchanged.
const externalIslandScripts = {
  name: 'external-island-scripts',
  hooks: {
    'astro:build:done': ({ dir }) => {
      const root = fileURLToPath(dir);
      for (const page of readdirSync(root, { recursive: true }).filter((f) => f.endsWith('.html'))) {
        const path = join(root, page);
        const html = readFileSync(path, 'utf8').replace(/<script>([\s\S]*?)<\/script>/g, (_, js) => {
          const file = `_astro/island.${createHash('sha256').update(js).digest('hex').slice(0, 10)}.js`;
          writeFileSync(join(root, file), js);
          return `<script src="/${file}"></script>`;
        });
        writeFileSync(path, html);
      }
    },
  },
};

export default defineConfig({
  output: 'static',
  integrations: [react(), externalIslandScripts],
  // Keep CSS and scripts as hashed files: the CSP forbids inline script.
  build: { inlineStylesheets: 'never' },
  vite: { build: { assetsInlineLimit: 0 } },
});
