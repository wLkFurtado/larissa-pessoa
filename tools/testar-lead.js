#!/usr/bin/env node
// Testa o first-touch, a validação e o fluxo do formulário com o GHL só no HTML.
const { execFileSync, spawn } = require('child_process');
const fs = require('fs');
const http = require('http');
const path = require('path');
const vm = require('vm');

const RAIZ = path.resolve(__dirname, '..');
const SITE = path.join(RAIZ, 'site');
let falhas = 0;

function ok(cond, msg) {
  if (cond) {
    console.log('ok', msg);
    return;
  }
  falhas += 1;
  console.error('falhou', msg);
}

function carregarLead() {
  const sandbox = {
    URLSearchParams,
    URL,
    console,
    setTimeout,
    clearTimeout,
  };
  sandbox.globalThis = sandbox;
  vm.runInNewContext(fs.readFileSync(path.join(SITE, 'assets/js/lead.js'), 'utf8'), sandbox);
  return sandbox.HairzenithLead;
}

function testarFuncoes() {
  const lead = carregarLead();
  ok(lead.ESPERA_MS >= 800 && lead.ESPERA_MS <= 1200, 'espera do script entre 800 e 1200 ms');
  ok(lead.mascararTelefone('22999037788') === '(22) 99903-7788', 'máscara de celular');
  ok(lead.mascararTelefone('5522999037788') === '(22) 99903-7788', 'máscara tira o 55');
  ok(lead.normalizarTelefone('(21) 97278-0789') === '21972780789', 'celular do Rio');
  ok(lead.normalizarTelefone('+55 22 99903-7788') === '22999037788', 'celular de Cabo Frio');
  ok(lead.normalizarTelefone('2133334444') === '', 'rejeita fixo');
  ok(lead.normalizarTelefone('(00) 99999-9999') === '', 'rejeita DDD inválido');
  ok(lead.normalizarTelefone('(21) 99999-9999') === '', 'rejeita número repetido');
  ok(lead.validarNome('Ana Souza'), 'nome válido');
  ok(!lead.validarNome('A'), 'nome curto demais');
  ok(!lead.validarNome('http://spam.test'), 'nome com url');
  ok(lead.validarEmail(''), 'e-mail vazio passa');
  ok(lead.validarEmail('ana@hairzenith.com'), 'e-mail válido');
  ok(!lead.validarEmail('ana@'), 'e-mail inválido');
  ok(lead.FONES['Cabo Frio'] === '5522999037788', 'WhatsApp de Cabo Frio');
  ok(lead.FONES.Copacabana === '5521972780789', 'WhatsApp de Copacabana');
  ok(lead.SLUGS['Cabo Frio'] === 'cabo_frio' && lead.SLUGS.Copacabana === 'copacabana', 'slugs do dataLayer');
  const partes = lead.partirNome('Ana Maria Souza');
  ok(partes.full === 'Ana Maria Souza' && partes.first === 'Ana' && partes.last === 'Maria Souza', 'nome completo vira first e last');
  ok(lead.partirNome('Ana').last === '', 'nome único não inventa sobrenome');
  const msg = lead.mensagemWhatsapp('Ana Souza', 'Cabo Frio', 'Olá! Vim pelo site da Hairzenith e gostaria de agendar a Consulta Signature, com a Dra. Larissa Pessoa.');
  ok(msg.includes('Ana Souza') && msg.includes('Cabo Frio') && msg.includes('Consulta Signature, com a Dra. Larissa Pessoa'), 'mensagem curta com nome e unidade');
  const expert = lead.mensagemWhatsapp('Ana Souza', 'Copacabana', 'Olá! Vim pelo site da Hairzenith e gostaria de agendar a Consulta Expert.');
  ok(expert.includes('agendar a Consulta Expert na unidade Copacabana'), 'mensagem da Consulta Expert');

  const agora = 1_700_000_000_000;
  const primeira = lead.resolverAtribuicao(
    { cookie: null, storage: null },
    { href: 'https://www.hairzenith.com/?gclid=AAA&utm_source=google&fbclid=FB', search: '?gclid=AAA&utm_source=google&fbclid=FB' },
    agora
  );
  ok(primeira.novo && primeira.dados.gclid === 'AAA' && primeira.dados.utm_source === 'google' && primeira.dados.fbclid === 'FB', 'primeira visita guarda o clique');
  const segunda = lead.resolverAtribuicao(
    { cookie: primeira.dados, storage: null },
    { href: 'https://www.hairzenith.com/consulta/?gclid=BBB&utm_source=facebook', search: '?gclid=BBB&utm_source=facebook' },
    agora + 1000
  );
  ok(!segunda.novo && segunda.dados.gclid === 'AAA' && segunda.dados.utm_source === 'google', 'first-touch não troca o gclid');
  const vencida = lead.resolverAtribuicao(
    { cookie: primeira.dados, storage: primeira.dados },
    { href: 'https://www.hairzenith.com/?gclid=CCC', search: '?gclid=CCC' },
    agora + lead.JANELA_MS + 1
  );
  ok(vencida.novo && vencida.dados.gclid === 'CCC', 'depois de 90 dias grava de novo');
  const organica = lead.resolverAtribuicao(
    { cookie: null, storage: null },
    { href: 'https://www.hairzenith.com/', search: '' },
    agora
  );
  const depois = lead.resolverAtribuicao(
    { cookie: organica.dados, storage: organica.dados },
    { href: 'https://www.hairzenith.com/?gclid=DDD', search: '?gclid=DDD' },
    agora + 5000
  );
  ok(!depois.novo && !depois.dados.gclid, 'primeira visita sem anúncio continua first-touch');

  const soGclid = lead.resolverAtribuicao(
    { cookie: null, storage: null },
    { href: 'https://www.hairzenith.com/?gclid=SOGCLID', search: '?gclid=SOGCLID' },
    agora
  );
  ok(soGclid.dados.gclid === 'SOGCLID' && soGclid.dados.utm_source === 'google' && soGclid.dados.utm_medium === 'cpc', 'só gclid preenche utm_source=google e utm_medium=cpc');

  const comMeta = lead.resolverAtribuicao(
    { cookie: null, storage: null },
    { href: 'https://www.hairzenith.com/?gclid=AAA&utm_source=meta', search: '?gclid=AAA&utm_source=meta' },
    agora
  );
  ok(comMeta.dados.utm_source === 'meta' && !comMeta.dados.utm_medium, 'gclid com utm_source=meta não troca a UTM nem inventa medium');

  const semClique = lead.resolverAtribuicao(
    { cookie: null, storage: null },
    { href: 'https://www.hairzenith.com/consulta/', search: '' },
    agora
  );
  ok(!semClique.dados.gclid && !semClique.dados.utm_source && !semClique.dados.utm_medium, 'sem click id não preenche UTM');
  ok(semClique.dados.origem === 'direto', 'sem click id e sem referrer é direto');

  const classificar = (search, referrer) => lead.resolverAtribuicao(
    { cookie: null, storage: null },
    { href: 'https://www.hairzenith.com/' + (search || ''), search: search || '', referrer: referrer || '' },
    agora
  ).dados;
  ok(classificar('?gclid=G').origem === 'google_ads', 'origem google_ads com gclid');
  ok(classificar('?gbraid=B').origem === 'google_ads', 'origem google_ads com gbraid');
  ok(classificar('?wbraid=W').origem === 'google_ads', 'origem google_ads com wbraid');
  ok(classificar('?utm_source=google&utm_medium=cpc').origem === 'google_ads', 'origem google_ads com utm cpc');
  ok(classificar('?utm_source=google&utm_medium=ppc').origem === 'google_ads', 'origem google_ads com ppc');
  ok(classificar('?utm_source=google&utm_medium=paid').origem === 'google_ads', 'origem google_ads com paid');
  ok(classificar('?utm_source=google&utm_medium=pmax').origem === 'google_ads', 'origem google_ads com pmax');
  ok(classificar('?fbclid=FB').origem === 'meta_ads', 'origem meta_ads com fbclid');
  ok(classificar('?utm_source=facebook&utm_medium=paid').origem === 'meta_ads', 'origem meta_ads facebook/paid');
  ok(classificar('?utm_source=fb&utm_medium=cpc').origem === 'meta_ads', 'origem meta_ads fb/cpc');
  ok(classificar('?utm_source=instagram&utm_medium=ads').origem === 'meta_ads', 'origem meta_ads instagram/ads');
  ok(classificar('?utm_source=ig&utm_medium=paid_social').origem === 'meta_ads', 'origem meta_ads ig/paid_social');
  ok(classificar('?utm_source=meta&utm_medium=paid').origem === 'meta_ads', 'origem meta_ads meta/paid');
  ok(classificar('?utm_source=instagram&utm_medium=bio').origem === 'instagram_bio', 'origem instagram_bio');
  ok(classificar('?utm_source=instagram&utm_medium=stories').origem === 'instagram_organico', 'stories vira instagram_organico');
  ok(classificar('', 'https://l.instagram.com/').origem === 'instagram_organico', 'referrer l.instagram.com é instagram_organico');
  ok(classificar('', 'https://www.instagram.com/hair').origem === 'instagram_organico', 'referrer instagram.com é instagram_organico');
  ok(classificar('?utm_source=google&utm_medium=gmb').origem === 'google_meu_negocio', 'origem google_meu_negocio gmb');
  ok(classificar('?utm_source=google&utm_medium=gbp').origem === 'google_meu_negocio', 'origem google_meu_negocio gbp');
  ok(classificar('?utm_source=google&utm_medium=maps').origem === 'google_meu_negocio', 'origem google_meu_negocio maps');
  ok(classificar('?utm_source=whatsapp&utm_medium=status').origem === 'whatsapp_status', 'status do WhatsApp vira whatsapp_status');
  const zap = classificar('?utm_source=whatsapp&utm_medium=status');
  ok(zap.utm_source === 'whatsapp' && zap.utm_medium === 'status', 'whatsapp_status não troca a UTM original');
  ok(classificar('', 'https://www.google.com/search?q=tricologia').origem === 'google_organico', 'busca Google sem click id é google_organico');
  ok(classificar('', 'https://www.google.com.br/').origem === 'google_organico', 'google.com.br sem click id é google_organico');
  ok(classificar('', 'https://blog.exemplo.com/post').origem === 'outro_site', 'outro referrer é outro_site');
  const outro = classificar('?utm_source=newsletter&utm_medium=email');
  ok(outro.origem === 'utm_outro' && outro.utm_source === 'newsletter' && outro.utm_medium === 'email', 'UTM fora da tabela vira utm_outro e preserva os originais');
  ok(classificar('?gclid=G&utm_source=meta').origem === 'google_ads', 'gclid ganha de utm_source=meta');
  ok(classificar('?gclid=G&fbclid=F').origem === 'google_ads', 'click id do Google ganha do fbclid');
  const gravado = classificar('?utm_source=instagram&utm_medium=bio');
  const deNovo = lead.resolverAtribuicao(
    { cookie: gravado, storage: gravado },
    { href: 'https://www.hairzenith.com/?utm_source=google&utm_medium=cpc', search: '?utm_source=google&utm_medium=cpc', referrer: '' },
    agora + 1000
  );
  ok(deNovo.dados.origem === 'instagram_bio', 'origem do first-touch não muda numa visita seguinte');

  const soGbraid = lead.resolverAtribuicao(
    { cookie: null, storage: null },
    { href: 'https://www.hairzenith.com/?wbraid=WB', search: '?wbraid=WB' },
    agora
  );
  ok(soGbraid.dados.utm_source === 'google' && soGbraid.dados.utm_medium === 'cpc', 'wbraid sem UTM também vira google/cpc');

  const mediumPronto = lead.resolverAtribuicao(
    { cookie: null, storage: null },
    { href: 'https://www.hairzenith.com/?gclid=AAA&utm_medium=display', search: '?gclid=AAA&utm_medium=display' },
    agora
  );
  ok(mediumPronto.dados.utm_source === 'google' && mediumPronto.dados.utm_medium === 'display', 'utm_medium existente não é sobrescrito');

  const antigo = { v: 1, ts: agora, landing: 'https://www.hairzenith.com/?gclid=ANTIGO', gclid: 'ANTIGO' };
  const relido = lead.resolverAtribuicao(
    { cookie: antigo, storage: { ...antigo } },
    { href: 'https://www.hairzenith.com/consulta/', search: '' },
    agora + 1000
  );
  ok(!relido.novo && relido.sincronizar && relido.dados.utm_source === 'google' && relido.dados.utm_medium === 'cpc' && relido.dados.ts === agora, 'registro antigo só com gclid é completado sem mudar a data');
}

function testarBuild() {
  const py = (env) => execFileSync('python3', ['-c', 'import build; print(build.script_ghl())'], {
    cwd: RAIZ,
    encoding: 'utf8',
    env: { ...process.env, ...env },
  });
  const padrao = py({});
  ok(padrao.includes('https://link.growave.com.br/js/external-tracking.js'), 'padrão usa o src do GHL');
  ok(padrao.includes('data-tracking-id="tk_32d9fa7d4ff44c5a9e02cc2dc4fe8065"'), 'padrão usa o tracking id público');
  ok(padrao.includes(' async '), 'script é async');
  const trocado = py({ GHL_TRACKING_ID: 'tk_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' });
  ok(trocado.includes('tk_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), 'GHL_TRACKING_ID sobrescreve');
  ok(!trocado.includes('tk_32d9fa7d4ff44c5a9e02cc2dc4fe8065'), 'override não deixa o id antigo');
  const script = '<script src="https://link.outro.example/js/external-tracking.js" data-tracking-id="tk_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"></script>';
  const colado = py({ GHL_TRACKING_SCRIPT: script });
  ok(colado.includes('link.outro.example') && colado.includes('tk_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'), 'GHL_TRACKING_SCRIPT aceita a tag inteira');
  const invalido = py({ GHL_TRACKING_SRC: 'http://inseguro.example/js/external-tracking.js' });
  ok(invalido.includes('tk_32d9fa7d4ff44c5a9e02cc2dc4fe8065'), 'src inválido volta para o padrão');
}

function servir() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let nome = decodeURIComponent(req.url.split('?')[0]);
      if (nome.endsWith('/')) nome += 'index.html';
      const arquivo = path.resolve(SITE, '.' + nome);
      if (!arquivo.startsWith(SITE + path.sep) && arquivo !== SITE) {
        res.writeHead(403);
        res.end();
        return;
      }
      fs.readFile(arquivo, (erro, dados) => {
        if (erro) {
          res.writeHead(404);
          res.end('nao');
          return;
        }
        const tipo = arquivo.endsWith('.js') ? 'text/javascript; charset=utf-8'
          : arquivo.endsWith('.css') ? 'text/css; charset=utf-8'
            : 'text/html; charset=utf-8';
        res.writeHead(200, { 'content-type': tipo, 'cache-control': 'no-store' });
        res.end(dados);
      });
    });
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

function esperar(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function comChrome(porta, fn, opcoes) {
  const extra = (opcoes && opcoes.args) || [];
  const aoPausar = opcoes && opcoes.aoPausar;
  const debugPort = (opcoes && opcoes.debugPort) || 9333;
  const userDir = fs.mkdtempSync('/tmp/hz-chrome-');
  const proc = spawn('google-chrome', [
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
    `--remote-debugging-port=${debugPort}`,
    `--user-data-dir=${userDir}`,
    ...extra,
    'about:blank',
  ], { stdio: 'ignore' });
  let versao = null;
  for (let i = 0; i < 40; i += 1) {
    try {
      versao = await fetch(`http://127.0.0.1:${debugPort}/json/version`).then((r) => r.json());
      break;
    } catch (erro) {
      await esperar(150);
    }
  }
  if (!versao) throw new Error('Chrome não abriu o depurador');
  const ws = new WebSocket(versao.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve);
    ws.addEventListener('error', reject);
  });
  let seq = 0;
  const pendentes = new Map();
  const eventos = [];
  const bloqueio = { capturas: [] };
  let enviarDepois = () => {};
  const ehLocal = (url) => {
    if (!/^https?:/i.test(url || '')) return true;
    try {
      const host = new URL(url).hostname;
      return host === '127.0.0.1' || host === 'localhost';
    } catch (erro) {
      return false;
    }
  };
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pendentes.has(msg.id)) {
      pendentes.get(msg.id)(msg);
      pendentes.delete(msg.id);
      return;
    }
    if (msg.method === 'Fetch.requestPaused') {
      if (aoPausar) {
        Promise.resolve(aoPausar(msg, enviarDepois, bloqueio)).catch((erro) => {
          console.error('interceptação', erro);
          try {
            enviarDepois('Fetch.failRequest', {
              requestId: msg.params.requestId,
              errorReason: 'Aborted',
            }, msg.sessionId);
          } catch (falha) { /* a pausa já foi respondida */ }
        });
        return;
      }
      const pedido = msg.params.request || {};
      const url = pedido.url || '';
      const sess = msg.sessionId;
      if (!ehLocal(url)) {
        bloqueio.capturas.push({ url: url, method: pedido.method || '', body: pedido.postData || '' });
        enviarDepois('Fetch.fulfillRequest', {
          requestId: msg.params.requestId,
          responseCode: 204,
          responseHeaders: [
            { name: 'access-control-allow-origin', value: '*' },
            { name: 'access-control-allow-methods', value: 'POST, OPTIONS' },
            { name: 'access-control-allow-headers', value: 'content-type' },
            { name: 'content-type', value: 'text/plain' },
          ],
        }, sess);
        return;
      }
      enviarDepois('Fetch.continueRequest', { requestId: msg.params.requestId }, sess);
      return;
    }
    if (msg.method) eventos.push(msg);
  });
  const enviar = (method, params, sessionId) => {
    const id = ++seq;
    const pacote = { id, method, params: params || {} };
    if (sessionId) pacote.sessionId = sessionId;
    ws.send(JSON.stringify(pacote));
    return new Promise((resolve) => pendentes.set(id, resolve));
  };
  enviarDepois = enviar;
  try {
    await fn({ enviar, eventos, porta, bloqueio });
  } finally {
    ws.close();
    proc.kill('SIGKILL');
  }
}

async function testarNavegador(porta) {
  await comChrome(porta, async ({ enviar, eventos, bloqueio }) => {
    const criado = await enviar('Target.createTarget', { url: 'about:blank' });
    const targetId = criado.result.targetId;
    const anexo = await enviar('Target.attachToTarget', { targetId, flatten: true });
    const sessao = anexo.result.sessionId;
    const cmd = (method, params) => enviar(method, params, sessao);
    await cmd('Page.enable');
    await cmd('Runtime.enable');
    await cmd('Fetch.enable', { patterns: [{ urlPattern: '*', requestStage: 'Request' }] });
    await cmd('Emulation.setDeviceMetricsOverride', {
      width: 390, height: 844, deviceScaleFactor: 2, mobile: true,
    });

    const avaliar = async (expr) => {
      const res = await cmd('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
      if (res.result.exceptionDetails) {
        throw new Error(JSON.stringify(res.result.exceptionDetails.exception ? res.result.exceptionDetails.exception.description : res.result.exceptionDetails.text));
      }
      return res.result.result.value;
    };
    const ir = async (caminho) => {
      eventos.length = 0;
      await cmd('Page.navigate', { url: `http://127.0.0.1:${porta}${caminho}` });
      for (let i = 0; i < 80; i += 1) {
        const pronto = await avaliar(`document.readyState !== 'loading' && !!document.getElementById('lead-form') && location.pathname === ${JSON.stringify(caminho === '/' ? '/' : caminho.split('?')[0])}`);
        if (pronto) return;
        await esperar(100);
      }
      throw new Error('página não carregou: ' + caminho);
    };
    const foto = async (nome) => {
      const shot = await cmd('Page.captureScreenshot', { format: 'png' });
      const destino = '/opt/cursor/artifacts/' + nome;
      fs.mkdirSync('/opt/cursor/artifacts', { recursive: true });
      fs.writeFileSync(destino, Buffer.from(shot.result.data, 'base64'));
    };

    await ir('/?gclid=GCLIDFIRST&utm_source=google&utm_medium=cpc&utm_campaign=queda&fbclid=FB1');
    const tag = await avaliar(`(() => {
      const s = document.querySelector('script[data-tracking-id]');
      return s ? s.getAttribute('src') + ' ' + s.getAttribute('data-tracking-id') + ' ' + (s.async ? 'async' : '') : '';
    })()`);
    ok(String(tag).includes('tk_32d9fa7d4ff44c5a9e02cc2dc4fe8065') && String(tag).includes('async'), 'HTML servido traz o script async');

    await avaliar(`document.querySelector('a[href*="wa.me"]').click()`);
    const aberto = await avaliar(`(() => ({
      hidden: document.getElementById('lead-modal').hidden,
      foco: document.activeElement && document.activeElement.id,
      gclid: document.querySelector('#lead-form input[name="gclid"]').value,
      fb: document.querySelector('#lead-form input[name="fbclid"]') ? 'tem' : '',
      titulo: document.getElementById('lead-titulo').textContent
    }))()`);
    ok(aberto.hidden === false, 'modal abre no clique do WhatsApp');
    ok(aberto.foco === 'lead-nome', 'foco vai para o nome');
    ok(aberto.gclid === 'GCLIDFIRST', 'gclid da primeira visita entra no hidden');
    ok(aberto.fb === '', 'fbclid não vira campo do formulário');
    await foto('lead-modal-mobile.png');

    await avaliar(`document.getElementById('lead-form').requestSubmit()`);
    const erro = await avaliar(`document.getElementById('lead-alerta').textContent`);
    ok(String(erro).includes('Informe seu nome'), 'submit vazio avisa e fica na página');
    const ainda = await avaliar(`location.hostname`);
    ok(ainda === '127.0.0.1', 'submit inválido não abre o WhatsApp');

    await avaliar(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))`);
    const fechou = await avaliar(`document.getElementById('lead-modal').hidden`);
    ok(fechou === true, 'ESC fecha o modal');

    await ir('/consulta/?gclid=GCLIDSECOND&utm_source=facebook');
    await avaliar(`document.querySelector('#cabo-frio a[href*="wa.me"]').click()`);
    const unidade = await avaliar(`(() => {
      const form = document.getElementById('lead-form');
      const marcada = form.querySelector('input[name="unidade"]:checked');
      return {
        gclid: form.querySelector('input[name="gclid"]').value,
        utm: form.querySelector('input[name="utm_source"]').value,
        marcada: marcada ? marcada.value : '',
        landing: form.querySelector('input[name="landing_page"]').value
      };
    })()`);
    ok(unidade.gclid === 'GCLIDFIRST' && unidade.utm === 'google', 'segunda página mantém o first-touch');
    ok(unidade.marcada === 'Cabo Frio', 'link do rodapé pré-seleciona Cabo Frio');
    ok(String(unidade.landing).includes('gclid=GCLIDFIRST'), 'landing page é a da primeira visita');

    await cmd('Emulation.setDeviceMetricsOverride', {
      width: 1280, height: 800, deviceScaleFactor: 1, mobile: false,
    });
    await foto('lead-modal-desktop.png');

    const antes = Date.now();
    const eventosDl = await avaliar(`(() => {
      document.getElementById('lead-nome').value = 'Ana Souza';
      document.getElementById('lead-phone').value = '(11) 98870-1234';
      const tag = document.querySelector('script[data-tracking-id]');
      tag.dataset.hzEstado = 'erro';
      window.__hzErros = [];
      window.addEventListener('unhandledrejection', (e) => window.__hzErros.push(String(e.reason && e.reason.stack || e.reason)));
      document.getElementById('lead-form').requestSubmit();
      return (window.dataLayer || []).filter((e) => e && e.event).map((e) => e.event + (e.unidade ? ':' + e.unidade : ''));
    })()`);
    ok(eventosDl.includes('whatsapp_click'), 'mantém whatsapp_click');
    ok(eventosDl.includes('generate_lead:cabo_frio'), 'generate_lead com a unidade');
    const ehWhatsapp = (url) => /wa\.me\/5522999037788|phone=5522999037788/.test(String(url || ''));
    const urlDoEvento = (e) => (e.params && (e.params.url || (e.params.frame && e.params.frame.url))) || '';
    let destino = '';
    for (let i = 0; i < 25; i += 1) {
      const pedido = eventos.filter((e) => e.method === 'Page.frameRequestedNavigation' && ehWhatsapp(urlDoEvento(e))).pop();
      if (pedido) {
        destino = urlDoEvento(pedido);
        break;
      }
      await esperar(40);
    }
    const levou = Date.now() - antes;
    if (!destino) {
      const paginas = eventos.filter((e) => String(e.method || '').startsWith('Page.')).map((e) => e.method);
      console.error('eventos de página:', paginas.join(', ') || 'nenhum');
      try {
        console.error('ainda na página:', await avaliar(`location.href + ' :: ' + JSON.stringify(window.__hzErros || [])`));
      } catch (erro) {
        console.error('leitura depois do submit:', erro.message);
      }
    }
    ok(ehWhatsapp(destino), 'script ausente abre o WhatsApp de Cabo Frio na mesma aba: ' + destino);
    ok(decodeURIComponent(destino).includes('Ana Souza') && decodeURIComponent(destino).includes('Cabo Frio'), 'mensagem leva o nome e a unidade');
    ok(levou < 800, 'sem o script carregado, não espera o segundo do GHL (' + levou + ' ms)');
    const postsGhl = bloqueio.capturas.filter((c) => c.method === 'POST' && /leadconnectorhq|growave/i.test(c.url));
    ok(postsGhl.length === 0, 'o fluxo da página não montou POST para o GHL');
  });
}

function servirFixture(script) {
  const html = `<!doctype html><html><body>
<form id="f">
  <label for="n">Nome</label>
  <input id="n" name="full_name" type="text" value="Ana Maria Souza">
  <input name="first_name" type="text" value="" style="position:absolute;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden">
  <input name="last_name" type="text" value="" style="position:absolute;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden">
  <input name="phone" type="tel" value="11988701234">
  <input name="email" type="email" value="">
  <input name="unidade" type="text" value="Cabo Frio">
  <input name="utm_source" type="text" value="google" tabindex="-1" aria-hidden="true" style="position:absolute;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden">
  <input name="origem" type="text" value="google_ads" tabindex="-1" aria-hidden="true" style="position:absolute;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden">
  <input name="gclid" type="hidden" value="NAO-DEVE-SAIR">
  <button type="submit">Enviar</button>
</form>
<script>
window.__erros = [];
window.addEventListener('error', function (e) { window.__erros.push(String(e.message)); });
document.getElementById('f').addEventListener('submit', function () {
  var nome = document.querySelector('[name=full_name]').value.trim();
  var pedacos = nome.split(/\\s+/);
  document.querySelector('[name=first_name]').value = pedacos.shift() || '';
  document.querySelector('[name=last_name]').value = pedacos.join(' ');
}, true);
</script>
<script src="/external-tracking.js" data-tracking-id="tk_teste_local_apenas"></script>
</body></html>`;
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const caminho = req.url.split('?')[0];
      if (caminho === '/external-tracking.js') {
        res.writeHead(200, { 'content-type': 'text/javascript; charset=utf-8' });
        res.end(script);
        return;
      }
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(html);
    });
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

async function testarPayloadDoScript() {
  const resposta = await fetch('https://link.growave.com.br/js/external-tracking.js');
  if (!resposta.ok) throw new Error('não baixou o external-tracking.js');
  const script = Buffer.from(await resposta.arrayBuffer());
  const server = await servirFixture(script);
  const porta = server.address().port;
  try {
    await comChrome(porta, async ({ enviar, bloqueio }) => {
      const criado = await enviar('Target.createTarget', { url: 'about:blank' });
      const anexo = await enviar('Target.attachToTarget', { targetId: criado.result.targetId, flatten: true });
      const sessao = anexo.result.sessionId;
      const cmd = (method, params) => enviar(method, params, sessao);
      await cmd('Page.enable');
      await cmd('Fetch.enable', { patterns: [{ urlPattern: '*', requestStage: 'Request' }] });
      await cmd('Page.navigate', { url: `http://127.0.0.1:${porta}/fixture.html` });
      for (let i = 0; i < 40; i += 1) {
        const pronto = await cmd('Runtime.evaluate', {
          expression: 'document.readyState !== "loading" && !!document.getElementById("f")',
          returnByValue: true,
        });
        if (pronto.result && pronto.result.result && pronto.result.result.value) break;
        await esperar(100);
      }
      await cmd('Runtime.evaluate', { expression: 'document.getElementById("f").requestSubmit()', returnByValue: true });
      let corpo = null;
      for (let i = 0; i < 40; i += 1) {
        const achado = bloqueio.capturas.find((c) => c.method === 'POST' && c.body.includes('external_form_submission'));
        if (achado) {
          corpo = achado;
          break;
        }
        await esperar(100);
      }
      if (!corpo) {
        console.error('capturas', bloqueio.capturas.map((c) => c.method + ' ' + c.url + ' ' + (c.body || '').slice(0, 180)));
        try {
          const diag = await cmd('Runtime.evaluate', {
            expression: 'JSON.stringify({erros: window.__erros || [], forms: document.forms.length, script: !!document.querySelector("script[data-tracking-id]")})',
            returnByValue: true,
          });
          console.error('diag', diag.result && diag.result.result && diag.result.result.value);
        } catch (erro) {
          console.error('diag falhou', erro.message);
        }
      }
      ok(!!corpo, 'o script tentou enviar o formulário e a requisição foi interceptada');
      if (!corpo) return;
      ok(corpo.url.includes('leadconnectorhq.com'), 'payload ia para ' + corpo.url);
      const json = JSON.parse(corpo.body);
      const dados = json.formData || {};
      ok(dados.full_name === 'Ana Maria Souza', 'payload traz full_name');
      ok(dados.first_name === 'Ana' && dados.last_name === 'Maria Souza', 'payload traz first_name e last_name');
      ok(dados.phone === '11988701234' && dados.unidade === 'Cabo Frio', 'phone e unidade continuam no payload');
      ok(dados.utm_source === 'google', 'utm fora da tela, sem type=hidden, entra no payload');
      ok(dados.origem === 'google_ads', 'origem entra no payload interceptado');
      ok(!('gclid' in dados) || dados.gclid == null, 'input type=hidden não entra no payload: ' + JSON.stringify(dados.gclid));
      ok(!('name' in dados), 'a chave name não é enviada');
      console.log('payload.formData', JSON.stringify(dados));
    });
  } finally {
    server.close();
  }
}

function tipoDoArquivo(arquivo) {
  if (arquivo.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (arquivo.endsWith('.css')) return 'text/css; charset=utf-8';
  if (arquivo.endsWith('.html')) return 'text/html; charset=utf-8';
  if (arquivo.endsWith('.svg')) return 'image/svg+xml';
  if (arquivo.endsWith('.png')) return 'image/png';
  if (arquivo.endsWith('.jpg') || arquivo.endsWith('.jpeg')) return 'image/jpeg';
  if (arquivo.endsWith('.webp')) return 'image/webp';
  if (arquivo.endsWith('.avif')) return 'image/avif';
  if (arquivo.endsWith('.json')) return 'application/json; charset=utf-8';
  if (arquivo.endsWith('.webmanifest')) return 'application/manifest+json';
  if (arquivo.endsWith('.xml')) return 'application/xml';
  if (arquivo.endsWith('.txt')) return 'text/plain; charset=utf-8';
  if (arquivo.endsWith('.ico')) return 'image/x-icon';
  return 'application/octet-stream';
}

function arquivoDoSite(url) {
  let caminho = '';
  try { caminho = decodeURIComponent(new URL(url).pathname); } catch (erro) { return null; }
  if (caminho.endsWith('/')) caminho += 'index.html';
  const arquivo = path.resolve(SITE, '.' + caminho);
  const raiz = SITE.endsWith(path.sep) ? SITE : SITE + path.sep;
  if (arquivo !== SITE && !arquivo.startsWith(raiz)) return null;
  return arquivo;
}

function origemDoPedido(pedido) {
  const headers = pedido.headers || {};
  if (Array.isArray(headers)) {
    const achado = headers.find((h) => String(h.name || '').toLowerCase() === 'origin');
    return (achado && achado.value) || 'https://www.hairzenith.com';
  }
  return headers.Origin || headers.origin || 'https://www.hairzenith.com';
}

function enviosDeFormulario(capturas) {
  return capturas.filter((c) => c.method === 'POST' && String(c.body || '').includes('external_form_submission'));
}

// A home é servida como https://www.hairzenith.com/ com os arquivos locais.
// O script do GHL baixa de verdade. O POST ao leadconnectorhq é pausado no
// estágio Request e abortado (Fetch.failRequest Aborted): o Chrome não envia
// o corpo ao CRM. O preflight OPTIONS é respondido localmente só para o
// navegador chegar a emitir o POST, que então é abortado.
async function aoPausarHome(msg, enviar, bloqueio) {
  const pedido = msg.params.request || {};
  const url = pedido.url || '';
  const metodo = String(pedido.method || 'GET').toUpperCase();
  const sess = msg.sessionId;
  const id = msg.params.requestId;
  const falhar = () => enviar('Fetch.failRequest', { requestId: id, errorReason: 'Aborted' }, sess);
  let host = '';
  let pathname = '';
  try {
    const parsed = new URL(url);
    host = parsed.hostname;
    pathname = parsed.pathname;
  } catch (erro) {
    falhar();
    return;
  }
  if (host === 'backend.leadconnectorhq.com' || host === 'staging.backend.leadconnectorhq.com') {
    let body = pedido.postData || '';
    if (!body && pedido.hasPostData) {
      const extra = await enviar('Fetch.getRequestPostData', { requestId: id }, sess);
      body = (extra.result && extra.result.postData) || '';
    }
    bloqueio.capturas.push({ url, method: metodo, body, abortado: true, em: Date.now() });
    if (metodo === 'OPTIONS') {
      const origem = origemDoPedido(pedido);
      enviar('Fetch.fulfillRequest', {
        requestId: id,
        responseCode: 204,
        responseHeaders: [
          { name: 'access-control-allow-origin', value: origem },
          { name: 'access-control-allow-methods', value: 'POST, OPTIONS' },
          { name: 'access-control-allow-headers', value: 'content-type' },
          { name: 'access-control-max-age', value: '600' },
        ],
      }, sess);
      return;
    }
    falhar();
    return;
  }
  if (host === 'link.growave.com.br' && pathname === '/js/external-tracking.js') {
    enviar('Fetch.continueRequest', { requestId: id }, sess);
    return;
  }
  if (host === 'wa.me' || host === 'api.whatsapp.com') {
    bloqueio.navegacoes.push(url);
    falhar();
    return;
  }
  if (host === 'www.hairzenith.com' || host === 'hairzenith.com') {
    const arquivo = arquivoDoSite(url);
    if (!arquivo || !fs.existsSync(arquivo) || !fs.statSync(arquivo).isFile()) {
      enviar('Fetch.fulfillRequest', {
        requestId: id,
        responseCode: 404,
        responseHeaders: [{ name: 'content-type', value: 'text/plain' }],
        body: Buffer.from('nao').toString('base64'),
      }, sess);
      return;
    }
    const dados = fs.readFileSync(arquivo);
    enviar('Fetch.fulfillRequest', {
      requestId: id,
      responseCode: 200,
      responseHeaders: [
        { name: 'content-type', value: tipoDoArquivo(arquivo) },
        { name: 'cache-control', value: 'no-store' },
      ],
      body: dados.toString('base64'),
    }, sess);
    return;
  }
  falhar();
}

async function testarGuardaDoClique() {
  await comChrome(0, async ({ enviar, bloqueio }) => {
    bloqueio.navegacoes = [];
    const criado = await enviar('Target.createTarget', { url: 'about:blank' });
    const anexo = await enviar('Target.attachToTarget', { targetId: criado.result.targetId, flatten: true });
    const sessao = anexo.result.sessionId;
    const cmd = (method, params) => enviar(method, params, sessao);
    await cmd('Page.enable');
    await cmd('Runtime.enable');
    await cmd('Fetch.enable', { patterns: [{ urlPattern: '*', requestStage: 'Request' }] });
    await cmd('Emulation.setDeviceMetricsOverride', {
      width: 1280, height: 900, deviceScaleFactor: 1, mobile: false,
    });
    const avaliar = async (expr) => {
      const res = await cmd('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
      if (res.result.exceptionDetails) {
        const detalhe = res.result.exceptionDetails;
        throw new Error(detalhe.exception ? detalhe.exception.description : detalhe.text);
      }
      return res.result.result.value;
    };
    await cmd('Page.navigate', { url: 'https://www.hairzenith.com/' });
    let pronto = null;
    for (let i = 0; i < 80; i += 1) {
      pronto = await avaliar(`(() => {
        const tag = document.querySelector('script[data-tracking-id]');
        return {
          host: location.hostname,
          form: !!document.getElementById('lead-form'),
          lead: !!(window.HairzenithLead && window.HairzenithLead.aoEnviar),
          ghl: tag ? (tag.dataset.hzEstado || '') : '',
          tracker: !!(window._lcTracking && window._lcTracking.tracker)
        };
      })()`);
      if (pronto && pronto.form && pronto.lead && pronto.ghl === 'ok' && pronto.tracker && pronto.host === 'www.hairzenith.com') break;
      if (pronto && pronto.ghl === 'erro') break;
      await esperar(150);
    }
    ok(pronto && pronto.host === 'www.hairzenith.com', 'home servida em www.hairzenith.com');
    ok(pronto && pronto.ghl === 'ok' && pronto.tracker, 'script do GHL carregou de verdade: ' + JSON.stringify(pronto));
    if (!pronto || pronto.ghl !== 'ok') {
      console.error('pedidos vistos', bloqueio.capturas.map((c) => c.method + ' ' + c.url).slice(0, 30));
      return;
    }

    const abriu = await avaliar(`(() => {
      const links = Array.from(document.querySelectorAll('a[href*="wa.me/"]'));
      const visivel = links.find((a) => {
        const r = a.getBoundingClientRect();
        const estilo = getComputedStyle(a);
        return r.width > 0 && r.height > 0 && estilo.display !== 'none' && estilo.visibility !== 'hidden';
      });
      if (!visivel) return '';
      visivel.scrollIntoView({ block: 'center' });
      visivel.click();
      return (visivel.textContent || '').replace(/\\s+/g, ' ').trim();
    })()`);
    ok(!!abriu, 'clique num link visível de wa.me abre o modal: ' + abriu);
    const modal = await avaliar(`document.getElementById('lead-modal').hidden === false && document.activeElement && document.activeElement.id`);
    ok(modal === 'lead-nome', 'modal aberto com foco no nome');

    const contar = () => enviosDeFormulario(bloqueio.capturas).length;
    const esperarEnvios = async (ms) => {
      const fim = Date.now() + ms;
      let ultimo = contar();
      while (Date.now() < fim) {
        await esperar(50);
        const agora = contar();
        if (agora !== ultimo) ultimo = agora;
      }
      return ultimo;
    };

    const vazio = await avaliar(`(() => {
      const botao = document.querySelector('#lead-form button[type="submit"]');
      let chegou = 0;
      const spy = () => { chegou += 1; };
      botao.addEventListener('click', spy, { capture: true });
      botao.querySelector('span').click();
      botao.removeEventListener('click', spy, { capture: true });
      const alerta = document.getElementById('lead-alerta');
      return { chegou, hidden: alerta.hidden, texto: alerta.textContent, host: location.hostname };
    })()`);
    const depoisVazio = await esperarEnvios(700);
    ok(vazio.chegou === 0, 'clique vazio não chega no listener do botão');
    ok(vazio.hidden === false && String(vazio.texto).includes('Informe seu nome'), 'clique vazio mostra o erro');
    ok(depoisVazio === 0 && vazio.host === 'www.hairzenith.com', 'clique vazio não envia external_form_submission');

    const parcial = await avaliar(`(() => {
      document.getElementById('lead-nome').value = 'a';
      document.getElementById('lead-phone').value = '123';
      document.querySelectorAll('#lead-form input[name="unidade"]').forEach((r) => { r.checked = false; });
      document.querySelector('#lead-form button[type="submit"] span').click();
      const alerta = document.getElementById('lead-alerta');
      return { hidden: alerta.hidden, texto: alerta.textContent };
    })()`);
    const depoisParcial = await esperarEnvios(700);
    ok(parcial.hidden === false && String(parcial.texto).includes('Informe seu nome') && String(parcial.texto).includes('Informe um celular'), 'parcial inválido mostra o erro');
    ok(depoisParcial === 0, 'nome "a" e telefone "123" não enviam external_form_submission');

    const caixa = await avaliar(`(() => {
      document.getElementById('lead-nome').value = '';
      document.getElementById('lead-phone').value = '';
      document.querySelectorAll('#lead-form input[name="unidade"]').forEach((r) => { r.checked = false; });
      const alerta = document.getElementById('lead-alerta');
      alerta.hidden = true;
      alerta.textContent = '';
      const nome = document.getElementById('lead-nome');
      nome.scrollIntoView({ block: 'center' });
      const r = nome.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height };
    })()`);
    ok(caixa && caixa.w > 0 && caixa.h > 0, 'campo do nome está visível para o Enter');
    await cmd('Input.dispatchMouseEvent', {
      type: 'mousePressed', x: caixa.x, y: caixa.y, button: 'left', clickCount: 1,
    });
    await cmd('Input.dispatchMouseEvent', {
      type: 'mouseReleased', x: caixa.x, y: caixa.y, button: 'left', clickCount: 1,
    });
    await cmd('Input.dispatchKeyEvent', {
      type: 'keyDown',
      key: 'Enter',
      code: 'Enter',
      windowsVirtualKeyCode: 13,
      nativeVirtualKeyCode: 13,
      text: '\r',
      unmodifiedText: '\r',
    });
    await cmd('Input.dispatchKeyEvent', {
      type: 'keyUp',
      key: 'Enter',
      code: 'Enter',
      windowsVirtualKeyCode: 13,
      nativeVirtualKeyCode: 13,
    });
    const enter = await avaliar(`(() => {
      const alerta = document.getElementById('lead-alerta');
      return {
        hidden: alerta.hidden,
        texto: alerta.textContent,
        host: location.hostname,
        foco: document.activeElement && document.activeElement.id
      };
    })()`);
    const depoisEnter = await esperarEnvios(700);
    ok(enter.hidden === false && String(enter.texto).includes('Informe seu nome'), 'Enter com campos vazios mostra o erro: ' + JSON.stringify(enter));
    ok(depoisEnter === 0 && enter.host === 'www.hairzenith.com', 'Enter com campos vazios não envia external_form_submission');

    const bloqueado = await avaliar(`(() => {
      const form = document.getElementById('lead-form');
      const botao = form.querySelector('button[type="submit"]');
      form.dataset.enviando = '1';
      let chegou = 0;
      const spy = () => { chegou += 1; };
      botao.addEventListener('click', spy, { capture: true });
      botao.querySelector('span').click();
      botao.removeEventListener('click', spy, { capture: true });
      delete form.dataset.enviando;
      return chegou;
    })()`);
    const depoisBloqueio = await esperarEnvios(400);
    ok(bloqueado === 0 && depoisBloqueio === 0, 'clique com enviando=1 não chega no botão nem no GHL');

    const antesValido = contar();
    const cliqueEm = Date.now();
    const eventosDl = await avaliar(`(() => {
      document.getElementById('lead-nome').value = 'Teste Silva';
      document.getElementById('lead-phone').value = '(22) 99999-1234';
      const unidade = document.querySelector('#lead-form input[name="unidade"][value="Cabo Frio"]');
      unidade.checked = true;
      document.querySelector('#lead-form button[type="submit"] span').click();
      return (window.dataLayer || []).filter((e) => e && e.event === 'generate_lead').map((e) => e.event + ':' + e.unidade);
    })()`);
    let corpo = null;
    for (let i = 0; i < 20; i += 1) {
      const vistos = enviosDeFormulario(bloqueio.capturas);
      if (vistos.length > antesValido) {
        corpo = vistos[vistos.length - 1];
        break;
      }
      await esperar(40);
    }
    await esperar(250);
    const achados = enviosDeFormulario(bloqueio.capturas).filter((c) => c.em >= cliqueEm && c.em - cliqueEm < 800);
    ok(achados.length === 1, 'dado válido gera um único external_form_submission (' + achados.length + ')');
    corpo = achados[0] || corpo;
    let dados = {};
    try { dados = JSON.parse((corpo && corpo.body) || '{}').formData || {}; } catch (erro) { dados = {}; }
    ok(dados.full_name === 'Teste Silva', 'payload traz full_name: ' + JSON.stringify(dados.full_name));
    ok(dados.phone === '(22) 99999-1234', 'payload traz phone: ' + JSON.stringify(dados.phone));
    ok(dados.first_name === 'Teste' && dados.last_name === 'Silva', 'payload traz o nome partido');
    ok(!!corpo && /leadconnectorhq\.com/.test(corpo.url) && corpo.abortado === true, 'POST ao CRM foi abortado: ' + (corpo && corpo.url));
    ok(Array.isArray(eventosDl) && eventosDl.includes('generate_lead:cabo_frio'), 'generate_lead com a unidade: ' + JSON.stringify(eventosDl));
    let destino = '';
    for (let i = 0; i < 40; i += 1) {
      destino = (bloqueio.navegacoes || []).find((u) => /wa\.me\/5522999037788/.test(u)) || '';
      if (destino) break;
      await esperar(50);
    }
    ok(/wa\.me\/5522999037788/.test(destino), 'navegação para o WhatsApp de Cabo Frio foi abortada: ' + destino);
    const ainda = await avaliar(`location.hostname`);
    ok(ainda === 'www.hairzenith.com', 'a página continua em www.hairzenith.com depois de abortar o wa.me');
    await esperar(1200);
    const repetidos = enviosDeFormulario(bloqueio.capturas).filter((c) => c.em >= cliqueEm);
    const nomes = repetidos.map((c) => {
      try { return JSON.parse(c.body).formData || {}; } catch (erro) { return {}; }
    });
    ok(repetidos.every((c) => c.abortado), 'todo external_form_submission foi abortado');
    ok(nomes.every((d) => d.full_name === 'Teste Silva' && d.phone === '(22) 99999-1234'), 'nenhum reenvio saiu vazio: ' + JSON.stringify(nomes.map((d) => d.full_name)));
    ok(repetidos.length >= 1 && repetidos.slice(1).every((c) => c.body === repetidos[0].body), 'o aborto faz o script repetir o mesmo payload (' + repetidos.length + ' POST abortado(s); 1 do clique)');
  }, {
    debugPort: 9344,
    args: [
      '--host-resolver-rules=MAP backend.leadconnectorhq.com 127.0.0.1, MAP staging.backend.leadconnectorhq.com 127.0.0.1',
    ],
    aoPausar: aoPausarHome,
  });
}

async function main() {
  testarFuncoes();
  testarBuild();
  const html = fs.readFileSync(path.join(SITE, 'index.html'), 'utf8');
  ok(html.includes('tk_32d9fa7d4ff44c5a9e02cc2dc4fe8065'), 'index.html gerado contém o tracking id');
  const server = await servir();
  const porta = server.address().port;
  try {
    await testarNavegador(porta);
  } finally {
    server.close();
  }
  await esperar(400);
  await testarPayloadDoScript();
  await esperar(400);
  await testarGuardaDoClique();
  if (falhas) {
    console.error(falhas + ' falha(s)');
    process.exit(1);
  }
  console.log('fluxo do lead ok');
}

main().catch((erro) => {
  console.error(erro);
  process.exit(1);
});
