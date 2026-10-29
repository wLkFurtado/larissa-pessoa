# Site Hairzenit

Site estático da Hairzenit (antiga Larissa Pessoa Tricologia Integrativa). São 15 páginas em HTML puro, sem
framework, prontas para qualquer hospedagem estática.

## Ver no computador

```bash
python3 build.py                                   # gera as páginas em site/
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

**Para colocar o retrato da Thaina ou da Júlia:** salve a foto em `fotos-originais/`, acrescente uma linha em
`IMAGENS` no `tools/imagens.py` com o nome `thaina` ou `julia` (proporção 4/5), rode os dois scripts. A página
Equipe passa a mostrar o retrato sozinha.

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

1. Registrar `hairzenit.com.br` (e `hairzenit.com`). Em 28/10/2026 os dois apareciam livres no WHOIS.
2. Subir a pasta `site/` em Netlify, Vercel ou Cloudflare Pages. Os redirecionamentos já estão prontos:
   `_redirects` (Netlify/Cloudflare) e `vercel.json` (Vercel).
3. Se o domínio final não for `www.hairzenit.com.br`, troque `SITE` no `build.py` e gere de novo
   (canonical, sitemap e dados estruturados usam esse endereço).
4. Google Search Console: cadastrar o domínio novo e enviar `sitemap.xml`.
5. Quando o site novo estiver no ar, apontar `larissapessoa.com` para ele. As URLs antigas caem nas novas com
   redirecionamento 301 (mapa em `REDIRECIONAMENTOS`, no `build.py`), o que transfere a autoridade página a página.
6. Google Business Profile: atualizar o nome para Hairzenit nas duas unidades, mantendo endereço e telefone
   idênticos aos do site.

## Confirmar antes de publicar

- **Júlia:** sobrenome, formação e foto. Hoje a página mostra só o primeiro nome.
- **Thaina e Júlia:** retratos (a seção está montada para recebê-los).
- **Quem atende onde:** o site não diz qual profissional atende em qual unidade.
- **Valores das consultas:** o site diz "informado no agendamento". Se quiser publicar, edite em `consulta()`.
- **Texto da história** (`/sobre/` e `/equipe/larissa-pessoa/`): foi escrito a partir do que o site antigo
  e o briefing dizem. Vale a Larissa ler e ajustar o tom.
- **Diário de obra:** as três entradas são as únicas datas conhecidas (lançamento da marca, obra em andamento,
  inauguração em março de 2027). Acrescente as etapas e as imagens do projeto arquitetônico em `nova_clinica()`.
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
