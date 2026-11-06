// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import site from './src/data/site.json' with { type: 'json' };

// https://astro.build/config
export default defineConfig({
  site: site.url,
  trailingSlash: 'always',
  build: { format: 'directory' },
  integrations: [
    sitemap({
      serialize(item) {
        const caminho = new URL(item.url).pathname;
        item.lastmod = site.atualizado;
        item.priority = caminho === '/' ? 1.0 : caminho.split('/').length === 3 ? 0.8 : 0.6;
        return item;
      },
    }),
  ],
});
