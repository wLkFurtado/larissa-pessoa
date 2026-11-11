// Formulário de agendamento antes do WhatsApp.
// O External Tracking do GHL lê este <form> no submit e também 50 ms depois do
// clique no botão, mesmo se o submit for cancelado. O token da API não entra aqui.

(function (root) {
  const CHAVES = ['gclid', 'gbraid', 'wbraid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
  const JANELA_MS = 90 * 24 * 60 * 60 * 1000;
  const ESPERA_MS = 1000;
  const FONES = { 'Cabo Frio': '5522999037788', Copacabana: '5521972780789' };
  const SLUGS = { 'Cabo Frio': 'cabo_frio', Copacabana: 'copacabana' };
  const DDDS = new Set([
    11, 12, 13, 14, 15, 16, 17, 18, 19,
    21, 22, 24, 27, 28,
    31, 32, 33, 34, 35, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48, 49,
    51, 53, 54, 55,
    61, 62, 63, 64, 65, 66, 67, 68, 69,
    71, 73, 74, 75, 77, 79,
    81, 82, 83, 84, 85, 86, 87, 88, 89,
    91, 92, 93, 94, 95, 96, 97, 98, 99,
  ]);
  let gatilho = null;

  function mascararTelefone(valor) {
    let d = String(valor || '').replace(/\D/g, '');
    if (d.startsWith('55') && d.length > 11) d = d.slice(2);
    d = d.slice(0, 11);
    if (!d) return '';
    if (d.length < 3) return '(' + d;
    if (d.length < 8) return '(' + d.slice(0, 2) + ') ' + d.slice(2);
    return '(' + d.slice(0, 2) + ') ' + d.slice(2, 7) + '-' + d.slice(7);
  }

  function normalizarTelefone(entrada) {
    let d = String(entrada || '').replace(/\D/g, '');
    if (d.startsWith('55') && d.length === 13) d = d.slice(2);
    if (d.length !== 11) return '';
    if (!DDDS.has(Number(d.slice(0, 2)))) return '';
    if (d[2] !== '9') return '';
    if (/^(\d)\1{8}$/.test(d.slice(2))) return '';
    return d;
  }

  function validarNome(nome) {
    const limpo = String(nome || '').replace(/\s+/g, ' ').trim();
    if (limpo.length < 2 || limpo.length > 80) return false;
    if (/https?:|www\.|@/i.test(limpo)) return false;
    return /^[\p{L}][\p{L}\s'.-]*$/u.test(limpo);
  }

  function validarEmail(email) {
    const limpo = String(email || '').trim();
    if (!limpo) return true;
    return limpo.length <= 120 && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(limpo);
  }

  function partirNome(nome) {
    const limpo = String(nome || '').replace(/\s+/g, ' ').trim();
    const partes = limpo ? limpo.split(' ') : [];
    const first = partes.shift() || '';
    return { full: limpo, first: first, last: partes.join(' ') };
  }

  function mensagemWhatsapp(nome, unidade, texto) {
    const original = String(texto || '');
    let pedido = 'gostaria de agendar uma consulta';
    if (/Larissa Pessoa/i.test(original)) pedido = 'gostaria de agendar a Consulta com Larissa Pessoa';
    else if (/Consulta Hairzenith/i.test(original)) pedido = 'gostaria de agendar a Consulta Hairzenith';
    let msg = 'Olá! Sou ' + nome + ' e ' + pedido + ' na unidade ' + unidade + '.';
    const incomodo = original.match(/Meu principal incômodo é:\s*([^.]+)\./i);
    if (incomodo) msg += ' Incômodo: ' + incomodo[1].trim() + '.';
    const periodo = original.match(/período da\s+([^.]+)\./i);
    if (periodo) msg += ' Período: ' + periodo[1].trim() + '.';
    return msg;
  }

  function registroValido(reg, agora) {
    return !!(reg && typeof reg.ts === 'number' && reg.ts <= agora && agora - reg.ts < JANELA_MS);
  }

  function utmVazio(valor) {
    return valor == null || String(valor).trim() === '';
  }

  // O workflow do GHL não oferece gclid como condição. O registro salvo
  // (e portanto o hidden) ganha utm_source/utm_medium só quando estão vazios.
  function completarUtmGoogle(dados) {
    if (!dados) return false;
    if (utmVazio(dados.gclid) && utmVazio(dados.gbraid) && utmVazio(dados.wbraid)) return false;
    let mudou = false;
    if (utmVazio(dados.utm_source)) {
      dados.utm_source = 'google';
      mudou = true;
    }
    if (dados.utm_source === 'google' && utmVazio(dados.utm_medium)) {
      dados.utm_medium = 'cpc';
      mudou = true;
    }
    return mudou;
  }

  function textoLc(valor) {
    return String(valor || '').trim().toLowerCase();
  }

  function hostDe(url) {
    try { return new URL(url).hostname.toLowerCase(); } catch (erro) { return ''; }
  }

  function ehBuscaGoogle(host) {
    const h = String(host || '').replace(/^www\./, '');
    return /^google\.(com|com\.br|[a-z]{2}|co\.[a-z]{2})$/.test(h);
  }

  function ehInstagram(host) {
    const h = String(host || '').replace(/^www\./, '');
    return h === 'instagram.com' || h === 'l.instagram.com' || h.endsWith('.instagram.com');
  }

  function ehReferrerExterno(host) {
    if (!host) return false;
    const h = host.replace(/^www\./, '');
    return h !== 'hairzenith.com' && h !== 'localhost' && h !== '127.0.0.1';
  }

  function temUtm(dados) {
    return ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].some((chave) => !utmVazio(dados[chave]));
  }

  // Slug do workflow. A ordem é a prioridade. UTM já preenchida não é reescrita aqui.
  function classificarOrigem(dados) {
    const fonte = textoLc(dados.utm_source);
    const meio = textoLc(dados.utm_medium);
    const host = hostDe(dados.referrer);
    const pagosGoogle = { cpc: 1, ppc: 1, paid: 1, pmax: 1 };
    const fontesMeta = { facebook: 1, fb: 1, instagram: 1, ig: 1, meta: 1 };
    const pagosMeta = { paid: 1, cpc: 1, ads: 1, paid_social: 1 };
    const meiosGmb = { gmb: 1, gbp: 1, maps: 1 };
    const cliqueGoogle = !utmVazio(dados.gclid) || !utmVazio(dados.gbraid) || !utmVazio(dados.wbraid);
    if (cliqueGoogle || (fonte === 'google' && pagosGoogle[meio])) return 'google_ads';
    if (!utmVazio(dados.fbclid) || (fontesMeta[fonte] && pagosMeta[meio])) return 'meta_ads';
    if (fonte === 'instagram' && meio === 'bio') return 'instagram_bio';
    if (fonte === 'instagram' || (ehInstagram(host) && !(fontesMeta[fonte] && pagosMeta[meio]))) return 'instagram_organico';
    if (fonte === 'google' && meiosGmb[meio]) return 'google_meu_negocio';
    if (fonte === 'whatsapp' && meio === 'status') return 'whatsapp_status';
    if (ehBuscaGoogle(host)) return 'google_organico';
    if (ehReferrerExterno(host)) return 'outro_site';
    if (temUtm(dados)) return 'utm_outro';
    return 'direto';
  }

  function aplicarOrigem(dados) {
    if (!dados || !utmVazio(dados.origem)) return false;
    dados.origem = classificarOrigem(dados);
    return true;
  }

  function resolverAtribuicao(estado, visita, agora) {
    const cookie = registroValido(estado && estado.cookie, agora) ? estado.cookie : null;
    const storage = registroValido(estado && estado.storage, agora) ? estado.storage : null;
    let atual = null;
    if (cookie && storage) atual = cookie.ts <= storage.ts ? cookie : storage;
    else atual = cookie || storage;
    if (atual) {
      const mudouUtm = completarUtmGoogle(atual);
      const mudouOrigem = aplicarOrigem(atual);
      return { dados: atual, novo: false, sincronizar: mudouUtm || mudouOrigem || !cookie || !storage };
    }
    const params = new URLSearchParams(visita.search || '');
    const dados = {
      v: 1,
      ts: agora,
      landing: String(visita.href || '').split('#')[0].slice(0, 500),
      referrer: String((visita && visita.referrer) || '').slice(0, 500),
    };
    CHAVES.forEach((chave) => {
      const valor = (params.get(chave) || '').trim();
      if (valor) dados[chave] = valor.slice(0, 200);
    });
    const fbclid = (params.get('fbclid') || '').trim();
    if (fbclid) dados.fbclid = fbclid.slice(0, 200);
    completarUtmGoogle(dados);
    aplicarOrigem(dados);
    return { dados: dados, novo: true, sincronizar: true };
  }

  function lerJson(texto) {
    if (!texto) return null;
    try {
      const dados = JSON.parse(texto);
      return dados && typeof dados === 'object' ? dados : null;
    } catch (erro) {
      return null;
    }
  }

  const api = {
    CHAVES: CHAVES,
    JANELA_MS: JANELA_MS,
    ESPERA_MS: ESPERA_MS,
    FONES: FONES,
    SLUGS: SLUGS,
    mascararTelefone: mascararTelefone,
    normalizarTelefone: normalizarTelefone,
    validarNome: validarNome,
    validarEmail: validarEmail,
    partirNome: partirNome,
    mensagemWhatsapp: mensagemWhatsapp,
    classificarOrigem: classificarOrigem,
    resolverAtribuicao: resolverAtribuicao,
  };
  root.HairzenithLead = api;
  if (!root.document) return;

  const doc = root.document;

  function lerCookie() {
    const prefixo = 'hz_ft=';
    const partes = doc.cookie ? doc.cookie.split('; ') : [];
    for (let i = 0; i < partes.length; i += 1) {
      if (partes[i].indexOf(prefixo) === 0) {
        try { return decodeURIComponent(partes[i].slice(prefixo.length)); } catch (erro) { return ''; }
      }
    }
    return '';
  }

  function capturar() {
    const agora = Date.now();
    let storage = null;
    try { storage = lerJson(root.localStorage.getItem('hz_ft')); } catch (erro) { storage = null; }
    const resultado = resolverAtribuicao(
      { cookie: lerJson(lerCookie()), storage: storage },
      { href: root.location.href, search: root.location.search, referrer: root.document.referrer || '' },
      agora
    );
    if (resultado.novo || resultado.sincronizar) {
      const json = JSON.stringify(resultado.dados);
      const restante = Math.max(60, Math.floor((resultado.dados.ts + JANELA_MS - agora) / 1000));
      const seguro = root.location.protocol === 'https:' ? '; Secure' : '';
      doc.cookie = 'hz_ft=' + encodeURIComponent(json) + '; Max-Age=' + restante + '; Path=/; SameSite=Lax' + seguro;
      try { root.localStorage.setItem('hz_ft', json); } catch (erro) { /* modo privado */ }
    }
    return resultado.dados;
  }

  function preencherCampos() {
    const form = doc.getElementById('lead-form');
    const dados = capturar();
    if (!form) return dados;
    CHAVES.forEach((chave) => {
      const campo = form.querySelector('input[name="' + chave + '"]');
      if (campo) campo.value = dados[chave] || '';
    });
    const pagina = form.querySelector('input[name="pagina_origem"]');
    if (pagina) pagina.value = root.location.href.split('#')[0].slice(0, 500);
    const landing = form.querySelector('input[name="landing_page"]');
    if (landing) landing.value = dados.landing || '';
    const origem = form.querySelector('input[name="origem"]');
    if (origem) origem.value = dados.origem || '';
    return dados;
  }

  function textoDoLink(link) {
    try { return new URL(link.href).searchParams.get('text') || ''; } catch (erro) { return ''; }
  }

  function unidadeMarcada(el) {
    if (!el || !el.getAttribute) return '';
    const valor = el.getAttribute('data-unidade');
    if (valor === 'Cabo Frio' || valor === 'Copacabana') return valor;
    return '';
  }

  function unidadeDoLink(link) {
    const direta = unidadeMarcada(link);
    if (direta) return direta;
    const bloco = link.closest && link.closest('[data-unidade]');
    const doBloco = unidadeMarcada(bloco);
    if (doBloco) return doBloco;
    if (link.closest && link.closest('#cabo-frio')) return 'Cabo Frio';
    if (link.closest && link.closest('#copacabana')) return 'Copacabana';
    const compositor = link.closest && link.closest('[data-composer]');
    if (compositor) {
      const marcada = new FormData(compositor).get('unidade');
      if (marcada === 'Cabo Frio' || marcada === 'Copacabana') return marcada;
    }
    return '';
  }

  function limparErros(form) {
    const alerta = doc.getElementById('lead-alerta');
    if (alerta) {
      alerta.hidden = true;
      alerta.textContent = '';
    }
    form.querySelectorAll('[aria-invalid="true"]').forEach((campo) => campo.removeAttribute('aria-invalid'));
  }

  function mostrarErros(form, erros) {
    const ordem = ['full_name', 'phone', 'email', 'unidade'];
    const textos = [];
    ordem.forEach((chave) => { if (erros[chave]) textos.push(erros[chave]); });
    const alerta = doc.getElementById('lead-alerta');
    if (alerta) {
      alerta.hidden = false;
      alerta.textContent = textos.join(' ');
    }
    const nome = form.querySelector('[name="full_name"]');
    const phone = form.querySelector('[name="phone"]');
    const email = form.querySelector('[name="email"]');
    if (erros.full_name && nome) nome.setAttribute('aria-invalid', 'true');
    if (erros.phone && phone) phone.setAttribute('aria-invalid', 'true');
    if (erros.email && email) email.setAttribute('aria-invalid', 'true');
    const foco = (erros.full_name && nome) || (erros.phone && phone) || (erros.email && email)
      || (erros.unidade && form.querySelector('[name="unidade"]'));
    if (foco) foco.focus();
  }

  function errosDoForm(form) {
    const dados = new FormData(form);
    const erros = {};
    if (!validarNome(dados.get('full_name'))) erros.full_name = 'Informe seu nome.';
    if (!normalizarTelefone(dados.get('phone'))) erros.phone = 'Informe um celular com DDD.';
    const email = String(dados.get('email') || '').trim();
    if (!validarEmail(email)) erros.email = 'Confira o e-mail ou deixe em branco.';
    if (!FONES[String(dados.get('unidade') || '')]) erros.unidade = 'Escolha a unidade.';
    return erros;
  }

  function normalizarCampos(form) {
    const nome = form.querySelector('[name="full_name"]');
    const email = form.querySelector('[name="email"]');
    const phone = form.querySelector('[name="phone"]');
    if (nome) nome.value = nome.value.replace(/\s+/g, ' ').trim();
    const partes = partirNome(nome ? nome.value : '');
    const primeiro = form.querySelector('[name="first_name"]');
    const ultimo = form.querySelector('[name="last_name"]');
    if (primeiro) primeiro.value = partes.first;
    if (ultimo) ultimo.value = partes.last;
    if (email) email.value = email.value.trim();
    if (phone) phone.value = mascararTelefone(phone.value);
  }

  function fecharMenu() {
    const menu = doc.getElementById('menu');
    if (!menu || !menu.hasAttribute('data-open')) return;
    menu.removeAttribute('data-open');
    const toggle = doc.querySelector('.menu-toggle');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
    doc.documentElement.style.overflow = '';
  }

  function focarDeVolta() {
    const menu = doc.getElementById('menu');
    if (gatilho && menu && menu.contains(gatilho) && !menu.hasAttribute('data-open')) {
      const toggle = doc.querySelector('.menu-toggle');
      if (toggle) toggle.focus();
      return;
    }
    if (gatilho && gatilho.focus) gatilho.focus();
  }

  function restaurarBotao(form) {
    const botao = form.querySelector('[type="submit"]');
    if (!botao) return;
    botao.disabled = false;
    botao.removeAttribute('aria-busy');
    const rotulo = botao.querySelector('span');
    if (rotulo) rotulo.textContent = 'Continuar no WhatsApp';
  }

  function fechar() {
    const modal = doc.getElementById('lead-modal');
    const form = doc.getElementById('lead-form');
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    doc.documentElement.style.overflow = '';
    if (form) {
      delete form.dataset.enviando;
      restaurarBotao(form);
    }
    focarDeVolta();
  }

  function abrir(link) {
    const modal = doc.getElementById('lead-modal');
    const form = doc.getElementById('lead-form');
    if (!modal || !form) return;
    fecharMenu();
    gatilho = link || gatilho;
    if (link) form.dataset.texto = textoDoLink(link);
    const unidade = link ? unidadeDoLink(link) : '';
    form.querySelectorAll('input[name="unidade"]').forEach((radio) => {
      radio.checked = radio.value === unidade;
    });
    preencherCampos();
    limparErros(form);
    delete form.dataset.enviando;
    restaurarBotao(form);
    modal.hidden = false;
    doc.documentElement.style.overflow = 'hidden';
    const nome = doc.getElementById('lead-nome');
    if (nome) nome.focus();
  }

  function rastreioPronto() {
    const tag = doc.querySelector('script[data-tracking-id]');
    return !!(tag && tag.dataset.hzEstado === 'ok');
  }

  function esperarRastreio() {
    if (!rastreioPronto()) return Promise.resolve();
    const tag = doc.querySelector('script[data-tracking-id]');
    let host = '';
    try { host = new URL(tag.src).host; } catch (erro) { host = ''; }
    return new Promise((resolve) => {
      let feito = false;
      const restaurar = [];
      const fim = () => {
        if (feito) return;
        feito = true;
        restaurar.forEach((fn) => { try { fn(); } catch (erro) { /* restaura o que der */ } });
        resolve();
      };
      const timer = root.setTimeout(fim, ESPERA_MS);
      const bate = (url) => {
        if (!url || !host) return;
        try {
          if (new URL(url, root.location.href).host === host) {
            root.clearTimeout(timer);
            root.setTimeout(fim, 80);
          }
        } catch (erro) { /* url relativa irrelevante */ }
      };
      try {
        if (typeof root.navigator.sendBeacon === 'function') {
          const original = root.navigator.sendBeacon.bind(root.navigator);
          root.navigator.sendBeacon = function (url, dados) {
            const resposta = original(url, dados);
            bate(url);
            return resposta;
          };
          restaurar.push(() => { root.navigator.sendBeacon = original; });
        }
        if (typeof root.fetch === 'function') {
          const original = root.fetch;
          root.fetch = function (entrada, init) {
            const url = typeof entrada === 'string' ? entrada : (entrada && entrada.url) || '';
            const resposta = original.call(this, entrada, init);
            bate(url);
            return resposta;
          };
          restaurar.push(() => { root.fetch = original; });
        }
        const XHR = root.XMLHttpRequest;
        if (XHR && XHR.prototype) {
          const abrirXhr = XHR.prototype.open;
          const enviarXhr = XHR.prototype.send;
          XHR.prototype.open = function (metodo, url) {
            this.__hzUrl = url;
            return abrirXhr.apply(this, arguments);
          };
          XHR.prototype.send = function () {
            bate(this.__hzUrl);
            return enviarXhr.apply(this, arguments);
          };
          restaurar.push(() => {
            XHR.prototype.open = abrirXhr;
            XHR.prototype.send = enviarXhr;
          });
        }
      } catch (erro) {
        /* sem o gancho, o tempo de 1s ainda segura a saída */
      }
    });
  }

  function irParaWhatsapp(url) {
    root.location.assign(url);
  }

  async function iniciarSaida(form) {
    const dados = new FormData(form);
    const nome = String(dados.get('full_name') || '').replace(/\s+/g, ' ').trim();
    const unidade = String(dados.get('unidade') || '');
    const msg = mensagemWhatsapp(nome, unidade, form.dataset.texto || '');
    const url = 'https://wa.me/' + FONES[unidade] + '?text=' + encodeURIComponent(msg);
    root.dataLayer = root.dataLayer || [];
    root.dataLayer.push({ event: 'generate_lead', unidade: SLUGS[unidade] });
    const botao = form.querySelector('[type="submit"]');
    if (botao) {
      botao.disabled = true;
      botao.setAttribute('aria-busy', 'true');
      const rotulo = botao.querySelector('span');
      if (rotulo) rotulo.textContent = 'Abrindo WhatsApp…';
    }
    try { await esperarRastreio(); } catch (erro) { /* o WhatsApp abre mesmo assim */ }
    irParaWhatsapp(url);
  }

  function aoEnviar(e) {
    const form = e.target;
    if (!form || form.id !== 'lead-form') return;
    if (form.dataset.enviando === '1') {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      return;
    }
    preencherCampos();
    normalizarCampos(form);
    const erros = errosDoForm(form);
    if (Object.keys(erros).length) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      mostrarErros(form, erros);
      return;
    }
    e.preventDefault();
    limparErros(form);
    form.dataset.enviando = '1';
    iniciarSaida(form);
  }

  function aoClicarEnvio(e) {
    const alvo = e.target;
    if (!alvo || !alvo.closest) return;
    const botao = alvo.closest('button[type="submit"], input[type="submit"], [data-submission-type="submit"]');
    if (!botao) return;
    const form = botao.form || botao.closest('form');
    if (!form || form.id !== 'lead-form') return;
    if (form.dataset.enviando === '1') {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      return;
    }
    normalizarCampos(form);
    const erros = errosDoForm(form);
    if (!Object.keys(erros).length) return;
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    mostrarErros(form, erros);
  }

  api.abrir = abrir;
  api.fechar = fechar;
  api.aoEnviar = aoEnviar;
  api.preencherCampos = preencherCampos;

  // Capture na window corre antes do listener que o GHL registra no botão.
  root.addEventListener('click', aoClicarEnvio, { capture: true });

  preencherCampos();

  const phone = doc.getElementById('lead-phone');
  if (phone) {
    phone.addEventListener('input', () => {
      const fim = phone.selectionStart === phone.value.length;
      phone.value = mascararTelefone(phone.value);
      if (fim && phone.setSelectionRange) phone.setSelectionRange(phone.value.length, phone.value.length);
    });
  }

  doc.addEventListener('click', (e) => {
    const alvo = e.target.closest && e.target.closest('a[href*="wa.me/"], a[href*="api.whatsapp.com/"]');
    if (!alvo) return;
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    abrir(alvo);
  });

  doc.addEventListener('click', (e) => {
    const modal = doc.getElementById('lead-modal');
    if (!modal || modal.hidden) return;
    if (e.target === modal) fechar();
    if (e.target.closest && e.target.closest('[data-lead-fechar]')) fechar();
  });

  doc.addEventListener('keydown', (e) => {
    const modal = doc.getElementById('lead-modal');
    if (!modal || modal.hidden) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      fechar();
      return;
    }
    if (e.key !== 'Tab') return;
    const focaveis = Array.from(modal.querySelectorAll('button, input, [href], [tabindex]:not([tabindex="-1"])'))
      .filter((el) => !el.disabled && el.offsetParent !== null);
    if (!focaveis.length) return;
    const primeiro = focaveis[0];
    const ultimo = focaveis[focaveis.length - 1];
    if (e.shiftKey && doc.activeElement === primeiro) {
      e.preventDefault();
      ultimo.focus();
    } else if (!e.shiftKey && doc.activeElement === ultimo) {
      e.preventDefault();
      primeiro.focus();
    }
  });
})(typeof globalThis !== 'undefined' ? globalThis : this);
