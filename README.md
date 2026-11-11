# Site Hairzenith

Site estático da Hairzenith (antiga Larissa Pessoa Tricologia Integrativa). São 15 páginas em HTML puro, sem
framework, prontas para qualquer hospedagem estática.

## Ver no computador

```bash
python3 build.py                                   # ou: npm run build
python3 tools/verificar.py                         # ou: npm run lint
python3 -m http.server 8080 --directory site       # abre em http://localhost:8080
```

Abra pelo servidor local, e não clicando direto no `index.html`: os links usam endereços limpos
(`/queda-de-cabelo/`), que só funcionam servidos.

## Onde mexer

| O quê | Onde |
| --- | --- |
| Todo o texto, contatos, endereços, data da inauguração, domínio | `build.py` (constantes no topo, conteúdo de cada página logo abaixo) |
| Cores, tipografia, layout | `site/assets/css/site.css` |
| Mapa do zênite, contagem regressiva, compositor do WhatsApp | `site/assets/js/site.js` |
| Recortes e tamanhos das fotos | `tools/imagens.py` (lê de `fotos-originais/`, grava em `site/assets/img/`) |

Depois de editar, rode `python3 build.py` de novo. Se mexer nas fotos, rode antes `python3 tools/imagens.py`
(precisa do Pillow).

Os retratos da Thaina e da Júlia estão em `fotos-originais/thaina.png` e `fotos-originais/julia.png`.
Para trocar só essas fotos, substitua o arquivo e rode:

```bash
python3 -c "import importlib.util; s=importlib.util.spec_from_file_location('imagens','tools/imagens.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.somente_retratos()"
python3 build.py
```

`python3 tools/imagens.py` recria o acervo inteiro.

## Páginas

| Endereço | Página |
| --- | --- |
| `/` | Home |
| `/queda-de-cabelo/`, `/calvicie-feminina/`, `/calvicie-masculina/`, `/couro-cabeludo-aparente/`, `/afinamento-dos-fios/`, `/perda-de-densidade-capilar/` | As seis páginas de problema (as mais importantes para o Google) |
| `/tratamentos/` | Índice dos problemas e das tecnologias |
| `/equipe/` e `/equipe/larissa-pessoa/` | Equipe e página própria da fundadora |
| `/consulta/` | As duas modalidades e o compositor de mensagem |
| `/sobre/` | A história da marca |
| `/nova-clinica/` | Contagem regressiva e diário de obra |
| `/conteudo/` e `/conteudo/quando-a-queda-de-cabelo-nao-e-normal/` | Conteúdo (artigo migrado do site antigo) e glossário |

## Publicar

1. O domínio final é `www.hairzenith.com` (com www, sem .br). Na Vercel ele é o domínio primário.
   Os redirects do `vercel.json` e do `_redirects` são só de caminho (`/sobre/`, etc.) e não trocam o host,
   então não forçam o apex nem entram em loop com o www.
2. Subir a pasta `site/` em Netlify, Vercel ou Cloudflare Pages. Os redirecionamentos já estão prontos:
   `_redirects` (Netlify/Cloudflare) e `vercel.json` (Vercel).
3. O padrão de `SITE_URL` é `https://www.hairzenith.com`. Canonical, sitemap, Open Graph e JSON-LD
   saem todos dessa origem. Para outro endereço:
   `SITE_URL=https://outro.exemplo python3 build.py`
   Pixel da Meta, GA4 e Tag Manager só entram com ID real, pelas variáveis abaixo. Há dois caminhos,
   e eles não se misturam:

   - **Recomendado:** só `GTM_ID`. Dentro do Tag Manager, crie a tag do GA4 e a do Pixel.
     O clique no WhatsApp já envia `dataLayer.push({ event: 'whatsapp_click' })`.
     No GTM, use um acionador de evento personalizado com o nome `whatsapp_click` e marque essa conversão no GA4.
   - **Direto, sem Tag Manager:** `GA_MEASUREMENT_ID` (formato `G-…`) e/ou `META_PIXEL_ID` (só números).
     O gerador coloca as tags no HTML.

   Se `GTM_ID` estiver definido, `GA_MEASUREMENT_ID` e `META_PIXEL_ID` são ignorados, para não contar
   a visita nem o pixel duas vezes. Nunca publique o GTM e, ao mesmo tempo, as tags diretas.
4. Google Search Console: cadastrar o domínio novo e enviar `sitemap.xml`.
5. Quando o site novo estiver no ar, apontar `larissapessoa.com` para ele. As URLs antigas caem nas novas com
   redirecionamento 301 (mapa em `REDIRECIONAMENTOS`, no `build.py`), o que transfere a autoridade página a página.
6. Google Business Profile: atualizar o nome para Hairzenith nas duas unidades, mantendo endereço e telefone
   idênticos aos do site.

## Confirmar antes de publicar

- **Júlia:** sobrenome e formação. A foto já está na página Equipe; o texto continua só com o primeiro nome.
- **Thaina:** a foto já está na página Equipe.
- **Quem atende onde:** o site não diz qual profissional atende em qual unidade.
- **Valores das consultas:** o site diz "informado no agendamento". Se quiser publicar, edite em `consulta()`.
- **Texto da história** (`/sobre/` e `/equipe/larissa-pessoa/`): foi escrito a partir do que o site antigo
  e o briefing dizem. Vale a Larissa ler e ajustar o tom.
- **Diário de obra:** as três entradas são as únicas datas conhecidas (lançamento da marca, obra em andamento,
  inauguração em março de 2027). Acrescente as etapas e as imagens do projeto arquitetônico em `nova_clinica()`.
- **Registro profissional:** o site não publica CRM nem outro conselho, e o schema da Larissa é `Person`, não `Physician`. O nome antigo "Dra. Larissa Pessoa Tricologia" segue só como alternateName. Confirmar o número antes de usar "Dra." no ar.
- **Domínio:** o final é `https://www.hairzenith.com`. Canonical, sitemap, Open Graph e JSON-LD já usam esse endereço.
- **CEP, horário e pin:** os dois endereços e o WhatsApp (21) 97278-0789 estão no código. CEP, horário de funcionamento e a coordenada medida no prédio não estão. O mapa usa grau e minuto aproximado.
- **Endereço da nova clínica:** não está no projeto. A página só marca a inauguração em março de 2027.
- **Pixel, Analytics e Tag Manager:** não há ID no repositório. Sem a variável, a tag não é publicada. Com `GTM_ID`, o GA4 e o Pixel ficam de fora do HTML de propósito.
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
