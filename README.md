# Site Hair Zenith

Site da Hair Zenith (antiga Larissa Pessoa Tricologia Integrativa), feito com [Astro](https://astro.build).
São 16 páginas estáticas, geradas em `dist/`, prontas para qualquer hospedagem estática.

## Ver no computador

```bash
npm install        # só na primeira vez (Node 22.12 ou mais novo)
npm run dev        # http://localhost:4321, recarrega sozinho a cada alteração
npm run build      # gera o site final em dist/
npm run preview    # serve o dist/ para conferir antes de publicar
```

## Onde mexer

| O quê | Onde |
| --- | --- |
| Contatos, endereços, WhatsApp, domínio, data da inauguração, artigos científicos | `src/data/site.json` |
| As sete páginas de problema (sinais, causas, tratamentos, perguntas) | `src/data/problemas.json` |
| Tricologistas da equipe (nome, unidade, registro no CRBM, texto) | `src/data/equipe.json` |
| Etapas da consulta, resultados, glossário, tecnologias | `src/data/listas.json` |
| Artigos do blog | `src/content/conteudo/*.md` (um arquivo por artigo) |
| Texto das demais páginas | `src/pages/` (um arquivo por página; o diário de obra fica em `nova-clinica.astro`) |
| Blocos reutilizados (abertura, faixa escura, perguntas, índice, fechamento…) | `src/components/` |
| Cabeçalho, rodapé e metatags | `src/components/Header.astro`, `Footer.astro`, `src/layouts/Base.astro` |
| Dados estruturados para o Google | `src/lib/schema.ts` |
| Cores, tipografia, layout | `src/styles/site.css` |
| Mapa do zênite, contagem regressiva, compositor do WhatsApp | `public/assets/js/site.js` |
| Recortes e tamanhos das fotos | `tools/imagens.py` (lê de `fotos-originais/`, grava em `public/assets/img/`) |

**Publicar um artigo novo:** copie o `.md` que já existe em `src/content/conteudo/`, troque o nome do arquivo
(ele vira o endereço: `meu-artigo.md` → `/conteudo/meu-artigo/`), ajuste o cabeçalho (`titulo`, `resumo`,
`data`, `imagem`) e escreva o texto em Markdown, com `##` para os subtítulos. A listagem em `/conteudo/`, o
sitemap e os dados estruturados se atualizam sozinhos no próximo build.

**Fotos:** se mexer nelas, rode `npm run imagens` (precisa de Python 3 com Pillow) antes do build.
Para colocar o retrato da Thaina ou da Júlia: salve a foto em `fotos-originais/`, acrescente uma linha em
`IMAGENS` no `tools/imagens.py` com o nome `thaina` ou `julia` (proporção 4/5) e rode `npm run imagens`.
A página Equipe passa a mostrar o retrato sozinha.

## Páginas

| Endereço | Página |
| --- | --- |
| `/` | Home |
| `/queda-de-cabelo/`, `/calvicie-feminina/`, `/calvicie-masculina/`, `/afinamento-dos-fios/`, `/alteracoes-do-couro-cabeludo/`, `/couro-cabeludo-aparente/`, `/perda-de-densidade-capilar/` | As sete páginas de problema (as mais importantes para o Google) |
| `/tratamentos/` | Índice dos problemas e das tecnologias |
| `/equipe/` e `/equipe/larissa-pessoa/` | Equipe e página própria da fundadora |
| `/consulta/` | As duas modalidades e o compositor de mensagem |
| `/sobre/` | A história da marca |
| `/nova-clinica/` | Contagem regressiva e diário de obra |
| `/conteudo/` e `/conteudo/<artigo>/` | Conteúdo (artigos em Markdown), publicações e glossário |

## Publicar

1. Registrar `hairzenith.com.br` (e `hairzenith.com`). Em 05/11/2026 os dois apareciam livres no WHOIS.
2. Vercel: o `vercel.json` já define o build do Astro (`npm run build`, saída em `dist/`) e os redirecionamentos 301.
   Netlify ou Cloudflare Pages: comando `npm run build`, pasta `dist`; os redirecionamentos vão no `public/_redirects`.
3. Se o domínio final não for `www.hairzenith.com.br`, troque `url` em `src/data/site.json`
   (canonical, sitemap e dados estruturados usam esse endereço).
4. Google Search Console: cadastrar o domínio novo e enviar `sitemap-index.xml`.
5. Quando o site novo estiver no ar, apontar `larissapessoa.com` para ele. As URLs antigas caem nas novas com
   redirecionamento 301 (lista em `vercel.json` e `public/_redirects`), o que transfere a autoridade página a página.
6. Google Business Profile: atualizar o nome para Hair Zenith nas duas unidades, mantendo endereço e telefone
   idênticos aos do site.

## Confirmar antes de publicar

- **Registros no CRBM:** os números da Dra. Thaina e da Dra. Júlia ainda são provisórios (`000`). Enquanto forem só zeros,
  não aparecem no site; basta trocar `registro` em `src/data/equipe.json`.
- **Retratos da Dra. Thaina e da Dra. Júlia:** a seção está montada para recebê-los (veja Fotos, acima).
- **WhatsApp por unidade:** os botões "Agendar no Rio de Janeiro" e "Agendar em Cabo Frio" usam o mesmo número, com
  mensagens diferentes. Se Cabo Frio tiver número próprio, ajuste `src/pages/index.astro` e `src/data/site.json`.
- **Página nova de alterações do couro cabeludo:** texto escrito para esta versão; vale a revisão da equipe clínica.
- **Valores das consultas:** o site diz "informado no agendamento". Se quiser publicar, edite em `src/pages/consulta.astro`.
- **Texto da história** (`/sobre/` e `/equipe/larissa-pessoa/`): foi escrito a partir do que o site antigo
  e o briefing dizem. Vale a Larissa ler e ajustar o tom.
- **Diário de obra:** as três entradas são as únicas datas conhecidas (lançamento da marca, obra em andamento,
  inauguração em março de 2027). Acrescente as etapas e as imagens do projeto arquitetônico em `src/pages/nova-clinica.astro`.
- **Registro profissional:** sites de saúde costumam exibir o número do conselho da responsável técnica no rodapé.
- **E-mail e Instagram:** ainda são os da marca antiga (`lamptricologia@gmail.com`, `@larissapessoatricologia`).
- **Fotos de antes e depois:** vieram do site antigo e trazem a marca d'água Larissa Pessoa. Confirmar a
  autorização das pacientes e as regras do conselho profissional para esse tipo de imagem.
- **Imagens de banco (Adobe Stock):** as fotos de pessoas escovando o cabelo, do homem grisalho e as texturas
  vieram do site antigo. Confirmar se a licença foi comprada em nome da clínica ou da agência anterior.
- **Imagem gerada por IA:** a do site antigo (`Gemini_Generated_Image…`) não foi usada.

## Créditos de imagens de acervo aberto

- Gravura: William Cowper, *The anatomy of humane bodies: skin and hair follicles*, 1698, Wellcome Collection,
  CC BY 4.0, via Wikimedia Commons.
  https://commons.wikimedia.org/wiki/File:The_anatomy_of_humane_bodies;_skin_and_hair_follicles._Wellcome_L0020796.jpg
- *Avenida Nossa Senhora de Copacabana (1)*, foto de Andrevruas, CC BY 3.0, via Wikimedia Commons.
  https://commons.wikimedia.org/wiki/File:Avenida_Nossa_Senhora_de_Copacabana_(1).jpg

Os créditos aparecem no rodapé de todas as páginas.
