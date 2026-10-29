// Hairzenit — comportamento interativo de alta precisão. Sem dependências externas.

// 1. Revelação suave ao entrar na tela (apenas para elementos abaixo da dobra inicial)
(() => {
  const targets = document.querySelectorAll('[data-reveal]');
  if (!targets.length || !('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.remove('reveal-pending');
      entry.target.classList.add('is-in');
      io.unobserve(entry.target);
    }
  }, { rootMargin: '120px 0px 120px 0px', threshold: 0.01 });

  targets.forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.top > window.innerHeight * 1.05) {
      el.classList.add('reveal-pending');
      io.observe(el);
    } else {
      el.classList.add('is-in');
    }
  });
})();

// 2. Efeito Spotlight 21st.dev (rastreamento sutil do cursor em cartões de luxo)
(() => {
  const cards = document.querySelectorAll('[data-spotlight]');
  if (!cards.length || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  cards.forEach((card) => {
    card.addEventListener('pointermove', (e) => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
      card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
    }, { passive: true });
  });
})();

// 3. Menu Mobile Editorial
(() => {
  const toggle = document.querySelector('.menu-toggle');
  const menu = document.getElementById('menu');
  if (!toggle || !menu) return;
  const close = menu.querySelector('.menu__close');
  const set = (open) => {
    if (open) menu.setAttribute('data-open', '');
    else menu.removeAttribute('data-open');
    toggle.setAttribute('aria-expanded', String(open));
    document.documentElement.style.overflow = open ? 'hidden' : '';
    (open ? close : toggle).focus();
  };
  toggle.addEventListener('click', () => set(true));
  close.addEventListener('click', () => set(false));
  menu.addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
})();

// 4. Atlas do Zênite: sincroniza a cabeça vista de cima com a lista de sinais
(() => {
  const map = document.querySelector('.zmap');
  if (!map) return;
  const caption = map.querySelector('.zmap__caption');
  const rows = document.querySelectorAll('.row[data-zone]');
  const info = {};
  rows.forEach((row) => {
    info[row.dataset.zone] = {
      name: row.dataset.name,
      text: row.dataset.text,
      href: row.getAttribute('href'),
    };
  });
  const show = (zone) => {
    map.dataset.on = zone;
    rows.forEach((r) => r.toggleAttribute('data-active', r.dataset.zone === zone));
    const z = info[zone];
    if (z && caption) {
      caption.innerHTML = `${z.text} <a class="link" href="${z.href}">${z.name} &rarr;<span class="sr-only">: ver página</span></a>`;
    }
  };
  rows.forEach((row) => {
    row.addEventListener('mouseenter', () => show(row.dataset.zone));
    row.addEventListener('focus', () => show(row.dataset.zone));
  });
  map.querySelectorAll('[data-zone-hit]').forEach((hit) => {
    const pick = (e) => { e.preventDefault(); show(hit.dataset.zoneHit); };
    hit.addEventListener('click', pick);
    hit.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') pick(e); });
  });
  if (rows.length) show(map.dataset.on || 'calvicie-masculina');
})();

// 5. Carrossel Arrastável (Os 7 Atos da Consulta)
(() => {
  document.querySelectorAll('[data-drag]').forEach((block) => {
    const row = block.querySelector('.moments__row');
    const bar = block.querySelector('.progress span');
    const prev = block.querySelector('[data-prev]');
    const next = block.querySelector('[data-next]');
    if (!row) return;
    const update = () => {
      const max = row.scrollWidth - row.clientWidth;
      const p = max > 0 ? row.scrollLeft / max : 1;
      const share = row.clientWidth / row.scrollWidth;
      if (bar) bar.style.setProperty('--p', Math.min(1, share + p * (1 - share)).toFixed(3));
      if (prev) prev.disabled = row.scrollLeft < 4;
      if (next) next.disabled = row.scrollLeft > max - 4;
    };
    const step = () => (row.querySelector('.moment')?.getBoundingClientRect().width || 320) + 24;
    prev?.addEventListener('click', () => row.scrollBy({ left: -step(), behavior: 'smooth' }));
    next?.addEventListener('click', () => row.scrollBy({ left: step(), behavior: 'smooth' }));
    row.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();

    let down = false, startX = 0, startLeft = 0, moved = false;
    row.addEventListener('pointerdown', (e) => {
      if (e.pointerType !== 'mouse') return;
      down = true;
      moved = false;
      startX = e.clientX;
      startLeft = row.scrollLeft;
      row.style.scrollSnapType = 'none';
    });
    window.addEventListener('pointermove', (e) => {
      if (!down) return;
      const dx = e.clientX - startX;
      if (Math.abs(dx) > 4) moved = true;
      row.scrollLeft = startLeft - dx;
    });
    window.addEventListener('pointerup', () => {
      if (!down) return;
      down = false;
      row.style.scrollSnapType = '';
    });
    row.addEventListener('click', (e) => {
      if (moved) { e.preventDefault(); moved = false; }
    }, true);
  });
})();

// 6. Índice Cinético com Prévia de Imagem (Lumina Preview List)
(() => {
  document.querySelectorAll('[data-preview-list]').forEach((list) => {
    const img = document.querySelector(list.dataset.previewList);
    if (!img) return;
    list.querySelectorAll('a[data-src]').forEach((a) => {
      const swap = () => {
        if (img.getAttribute('src') === a.dataset.src) return;
        img.style.opacity = '0';
        setTimeout(() => {
          img.src = a.dataset.src;
          img.alt = a.dataset.alt || '';
          img.style.opacity = '1';
        }, 160);
      };
      a.addEventListener('mouseenter', swap);
      a.addEventListener('focus', swap);
    });
  });
})();

// 7. Contagem Regressiva para a Nova Clínica (Março de 2027)
document.querySelectorAll('[data-countdown]').forEach((el) => {
  const target = new Date(el.dataset.countdown + 'T09:00:00-03:00');
  const days = Math.ceil((target - new Date()) / 86400000);
  const n = el.querySelector('[data-days]');
  const unit = el.querySelector('[data-unit]');
  if (!n || !unit) return;
  if (days > 0) {
    n.textContent = days;
    unit.textContent = days === 1 ? 'dia para a inauguração' : 'dias para a inauguração';
  } else {
    n.textContent = 'Aberta';
    unit.textContent = 'A nova Hairzenit já recebe pacientes';
  }
});

// 8. Compositor Concierge de Mensagem para o WhatsApp
(() => {
  const form = document.querySelector('[data-composer]');
  if (!form) return;
  const out = form.querySelector('[data-message]');
  const go = form.querySelector('[data-send]');
  const phone = form.dataset.composer;
  const build = () => {
    const data = new FormData(form);
    const tipo = data.get('tipo');
    const unidade = data.get('unidade');
    const periodo = data.get('periodo');
    const queixa = data.get('queixa');
    let msg = `Olá! Vim pelo site da Hairzenit e gostaria de agendar a ${tipo}`;
    msg += unidade === 'Tanto faz' ? '.' : `, em ${unidade}.`;
    if (queixa && queixa !== 'Prefiro contar na consulta') msg += ` Meu principal incômodo é: ${queixa.toLowerCase()}.`;
    if (periodo && periodo !== 'Qualquer horário') msg += ` Tenho preferência pelo período da ${periodo.toLowerCase()}.`;
    out.textContent = msg;
    go.href = `https://wa.me/${phone}?text=${encodeURIComponent(msg)}`;
  };
  form.addEventListener('change', build);
  form.addEventListener('submit', (e) => { e.preventDefault(); window.open(go.href, '_blank', 'noopener'); });
  build();
})();

// 9. Lightbox de Alta Resolução para Casos Clínicos e Imagens Ampliáveis
(() => {
  const items = document.querySelectorAll('[data-lightbox]');
  if (!items.length) return;
  const modal = document.createElement('div');
  modal.className = 'lightbox';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-label', 'Visualização ampliada');
  modal.innerHTML = '<button type="button" class="lightbox__close">Fechar &times;</button><img class="lightbox__img" alt="">';
  document.body.appendChild(modal);

  const modalImg = modal.querySelector('.lightbox__img');
  const closeBtn = modal.querySelector('.lightbox__close');
  const close = () => modal.classList.remove('is-open');

  items.forEach((item) => {
    item.addEventListener('click', () => {
      const img = item.querySelector('img');
      if (!img) return;
      modalImg.src = img.currentSrc || img.src;
      modalImg.alt = img.alt || '';
      modal.classList.add('is-open');
    });
  });

  closeBtn.addEventListener('click', close);
  modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
})();
