import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Artigos do blog. Para publicar um novo, crie um .md em src/content/conteudo/ com este cabeçalho.
const conteudo = defineCollection({
  loader: glob({ base: './src/content/conteudo', pattern: '**/*.md' }),
  schema: z.object({
    titulo: z.string(),
    resumo: z.string(),
    data: z.coerce.date(),
    atualizado: z.coerce.date().optional(),
    autoria: z.string().default('Dra. Larissa Pessoa'),
    imagem: z.string(),
    imagemAlt: z.string(),
    // foto do cartão na listagem; sem ela, usa a imagem do artigo
    capa: z.string().optional(),
    capaAlt: z.string().optional(),
  }),
});

export const collections = { conteudo };
