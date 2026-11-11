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
  const msg = lead.mensagemWhatsapp('Ana Souza', 'Cabo Frio', 'Olá! Vim pelo site da Hairzenith e gostaria de agendar a Consulta com Larissa Pessoa.');
  ok(msg.includes('Ana Souza') && msg.includes('Cabo Frio') && msg.includes('Larissa Pessoa'), 'mensagem curta com nome e unidade');

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

async function comChrome(porta, fn) {
  const userDir = fs.mkdtempSync('/tmp/hz-chrome-');
  const proc = spawn('google-chrome', [
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
    '--remote-debugging-port=9333',
    `--user-data-dir=${userDir}`,
    'about:blank',
  ], { stdio: 'ignore' });
  let versao = null;
  for (let i = 0; i < 40; i += 1) {
    try {
      versao = await fetch('http://127.0.0.1:9333/json/version').then((r) => r.json());
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
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pendentes.has(msg.id)) {
      pendentes.get(msg.id)(msg);
      pendentes.delete(msg.id);
    } else if (msg.method) {
      eventos.push(msg);
    }
  });
  const enviar = (method, params, sessionId) => {
    const id = ++seq;
    const pacote = { id, method, params: params || {} };
    if (sessionId) pacote.sessionId = sessionId;
    ws.send(JSON.stringify(pacote));
    return new Promise((resolve) => pendentes.set(id, resolve));
  };
  try {
    await fn({ enviar, eventos, porta });
  } finally {
    ws.close();
    proc.kill('SIGKILL');
  }
}

async function testarNavegador(porta) {
  await comChrome(porta, async ({ enviar, eventos }) => {
    const criado = await enviar('Target.createTarget', { url: 'about:blank' });
    const targetId = criado.result.targetId;
    const anexo = await enviar('Target.attachToTarget', { targetId, flatten: true });
    const sessao = anexo.result.sessionId;
    const cmd = (method, params) => enviar(method, params, sessao);
    await cmd('Page.enable');
    await cmd('Runtime.enable');
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
      document.getElementById('lead-phone').value = '(22) 99903-7788';
      document.getElementById('lead-email').value = 'ana@example.com';
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
