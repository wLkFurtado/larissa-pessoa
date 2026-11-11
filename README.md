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
   O Tag Manager `GTM-59VNHFK6` entra em toda página mesmo sem variável na Vercel: o script fica no
   `<head>` e o iframe `noscript` logo após o `<body>`. O GA4 `G-7K4L9ZHTSR` é tag desse container,
   então o HTML não leva `gtag`. O clique no WhatsApp envia `dataLayer.push({ event: 'whatsapp_click' })`.
   No GTM, o acionador é o evento personalizado `whatsapp_click`.

   O clique abre um formulário HTML (não é iframe) e só então vai ao WhatsApp da unidade.
   O envio é lido pelo External Tracking do GHL, colado no fim de cada página com `async`
   (o formulário já está no DOM antes da tag, e o download não segura o `site.js`).
   O padrão do build já é o script da subconta:

   `https://link.growave.com.br/js/external-tracking.js`
   `data-tracking-id="tk_32d9fa7d4ff44c5a9e02cc2dc4fe8065"`

   Para trocar, edite `GHL_TRACKING_SRC` e `GHL_TRACKING_ID` em `build.py`, ou exporte na
   hora do build `GHL_TRACKING_SRC` e `GHL_TRACKING_ID`. Também vale `GHL_TRACKING_SCRIPT`
   com o `<script>` inteiro de **Settings → External Tracking → Copy Script**. Na Vercel
   essas variáveis precisam existir no build (não basta configurá-las depois que o HTML
   já foi gerado) e em seguida um novo deploy. Sem override, o padrão acima entra sozinho.

   O campo visível do nome é `full_name`. `first_name` e `last_name` são preenchidos no
   submit. O script do GHL descarta `type="hidden"`, então nome, click id e UTM que precisam
   chegar no payload ficam fora da tela, sem `hidden` e sem `opacity: 0`. O `name="name"`
   não vira o nome do contato. O formulário também manda `phone`, `email` (opcional) e `unidade` (`Cabo Frio` ou
   `Copacabana`) e `gclid`, `gbraid`, `wbraid`, `utm_source`, `utm_medium`,
   `utm_campaign`, `utm_term`, `utm_content`, no first-touch de 90 dias. Se esse registro
   tem `gclid`, `gbraid` ou `wbraid` e `utm_source` está vazio, ele é salvo como `google`.
   Se `utm_source` fica `google` e `utm_medium` está vazio, ele é salvo como `cpc`. UTM que
   já veio na URL não muda. Sem click id do Google, nenhuma UTM é inventada. O mesmo
   registro guarda `origem`, um slug fixo para o workflow do GHL aplicar tag. A primeira
   regra que bater ganha, e a visita seguinte não troca esse valor.

   | `origem` | Quando |
   | --- | --- |
   | `google_ads` | `gclid`, `gbraid` ou `wbraid`, ou `utm_source=google` com `utm_medium` `cpc`, `ppc`, `paid` ou `pmax` |
   | `meta_ads` | `fbclid`, ou `utm_source` `facebook`, `fb`, `instagram`, `ig` ou `meta` com `utm_medium` `paid`, `cpc`, `ads` ou `paid_social` |
   | `instagram_bio` | `utm_source=instagram` e `utm_medium=bio` |
   | `instagram_organico` | referrer `instagram.com` ou `l.instagram.com` sem UTM paga, ou `utm_source=instagram` com outro medium, inclusive `stories` |
   | `google_meu_negocio` | `utm_source=google` e `utm_medium` `gmb`, `gbp` ou `maps` |
   | `whatsapp_status` | `utm_source=whatsapp` e `utm_medium=status` |
   | `google_organico` | referrer de busca do Google, sem click id |
   | `outro_site` | outro referrer externo |
   | `utm_outro` | tem UTM que não entrou acima; `utm_source` e `utm_medium` originais ficam como vieram |
   | `direto` | sem click id, sem UTM e sem referrer externo |

   Links prontos para colar:

   - Bio do Instagram: `https://www.hairzenith.com/?utm_source=instagram&utm_medium=bio` → `instagram_bio`
   - Stories: `https://www.hairzenith.com/?utm_source=instagram&utm_medium=stories` → `instagram_organico`
   - Google Meu Negócio: `https://www.hairzenith.com/?utm_source=google&utm_medium=gmb` → `google_meu_negocio`
   - Status do WhatsApp: `https://www.hairzenith.com/?utm_source=whatsapp&utm_medium=status` → `whatsapp_status`

   `pagina_origem`
   e `landing_page` vão junto e o GHL pode ignorá-los. O `fbclid` fica só no cookie.
   Depois do submit válido o site envia `dataLayer.push({ event: 'generate_lead', unidade: 'cabo_frio' | 'copacabana' })`
   e abre o WhatsApp na mesma aba: Cabo Frio `5522999037788`, Copacabana `5521972780789`.
   Se o script do GHL não carregou, o WhatsApp abre na hora.

   `GA_MEASUREMENT_ID` e `META_PIXEL_ID` só entram no HTML se não houver GTM. Com o padrão atual,
   os dois são ignorados para não duplicar a visita nem o pixel.
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
- **Tag Manager:** o HTML publica `GTM-59VNHFK6`. O GA4 `G-7K4L9ZHTSR` fica dentro desse container, sem `gtag` na página.
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
