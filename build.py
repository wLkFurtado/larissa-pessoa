#!/usr/bin/env python3
"""Gera o site estático da Hairzenith dentro de site/.

Uso:  python3 build.py
Depois, para ver localmente:  python3 -m http.server 8080 --directory site

Todo o texto do site está neste arquivo. Para trocar um contato, um endereço ou a data da
inauguração, edite as constantes logo abaixo e rode o script de novo.
"""
import html
import json
import math
import os
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote, urlparse

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "site"

# ---------------------------------------------------------------- dados da clínica
def _site():
    """Origem canônica. O domínio final é https://www.hairzenith.com.
    SITE_URL troca canonical, sitemap, Open Graph e JSON-LD num lugar só."""
    bruto = os.environ.get("SITE_URL", "").strip() or "https://www.hairzenith.com"
    bruto = bruto.rstrip("/")
    partes = urlparse(bruto)
    if partes.scheme != "https" or not partes.netloc or partes.path not in ("", "/") or partes.query or partes.fragment:
        raise SystemExit(
            "SITE_URL precisa ser uma origem https, sem caminho. Ex.: https://www.hairzenith.com"
        )
    return f"https://{partes.netloc}"


SITE = _site()
ATUALIZADO = "2026-11-10"
# Nome oficial: Hairzenith. Domínio final: https://www.hairzenith.com (com www, sem .br).
MARCA = "Hairzenith"
WHATS = "5521972780789"
WHATS_TEXTO = "(21) 97278-0789"
EMAIL = "lamptricologia@gmail.com"
# GTM padrão do site. O GA4 (G-7K4L9ZHTSR) e o Pixel entram por esse container,
# não como gtag ou fbq no HTML. A variável de ambiente ainda pode trocar o ID.
META_PIXEL_ID = os.environ.get("META_PIXEL_ID", "").strip()
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "").strip()
GTM_ID = os.environ.get("GTM_ID", "").strip() or "GTM-59VNHFK6"
# External Tracking da subconta LARISSA PESSOA. O id é público (vai no HTML).
# Para trocar sem editar o arquivo, exporte na hora do build:
#   GHL_TRACKING_SRC e GHL_TRACKING_ID
#   ou GHL_TRACKING_SCRIPT com o <script> inteiro copiado do GHL
# (Settings → External Tracking → Copy Script).
GHL_TRACKING_SRC = "https://link.growave.com.br/js/external-tracking.js"
GHL_TRACKING_ID = "tk_32d9fa7d4ff44c5a9e02cc2dc4fe8065"
INSTAGRAM = "https://www.instagram.com/larissapessoatricologia"
INSTAGRAM_TEXTO = "@larissapessoatricologia"
SITE_ANTIGO = "https://www.larissapessoa.com/"
INAUGURACAO = "2027-03-01"

UNIDADES = [
    {
        "id": "copacabana",
        "nome": "Copacabana",
        "rua": "Av. Nossa Senhora de Copacabana, 807, sala 702",
        "bairro": "Copacabana, Rio de Janeiro",
        "cidade": "Rio de Janeiro",
        "coords": "22°58'S 43°11'W",
        # CEP vazio de propósito. lat/lon acompanham o grau e minuto já impressos no site
        # e não foram medidos no prédio: confirmar o pin e o CEP antes de publicar.
        "cep": "",
        "mapa": "https://www.google.com/maps/search/?api=1&query=" + quote("Av. Nossa Senhora de Copacabana, 807, Copacabana, Rio de Janeiro"),
        "lat": -22.9667, "lon": -43.1856,
        "whats": "5521972780789",
        "whats_texto": "(21) 97278-0789",
    },
    {
        "id": "cabo-frio",
        "nome": "Cabo Frio",
        "rua": "Av. Henrique Terra, 808",
        "bairro": "Novo Portinho, Cabo Frio",
        "cidade": "Cabo Frio",
        "coords": "22°53'S 42°02'W",
        "cep": "",
        "mapa": "https://www.google.com/maps/search/?api=1&query=" + quote("Av. Henrique Terra, 808, Novo Portinho, Cabo Frio, RJ"),
        "lat": -22.8860, "lon": -42.0330,
        "whats": "5522999037788",
        "whats_texto": "(22) 99903-7788",
    },
]

ARTIGOS = [
    {
        "titulo": "Impacts of Personalized Multimodal Treatment in the Clinical Management of Androgenetic Alopecia: A Case Report",
        "curto": "Tratamento multimodal personalizado na alopecia androgenética",
        "autores": ["Larissa Mota Barros Pessoa", "Lara Junqueira", "Thaina Candido de Souza"],
        "doi": "10.62742/2965-7911.2025.2.bjhh20",
        "url": "https://brazjhairhealth.com/index.php/BJHH/article/view/36",
        "data": "2025-02-11",
    },
    {
        "titulo": "Integrated Therapeutic Approaches in the Treatment of Female Androgenetic Alopecia: A Case Report",
        "curto": "Abordagens integradas na alopecia androgenética feminina",
        "autores": ["Lara Junqueira", "Larissa Mota Barros Pessoa", "Thaina Candido de Souza"],
        "doi": "10.62742/2965-7911.2025.2.bjhh22",
        "url": "https://brazjhairhealth.com/index.php/BJHH/article/view/35",
        "data": "2025-02-22",
    },
]

CREDITOS = (
    "Gravura: William Cowper, <i>The anatomy of humane bodies</i>, 1698, Wellcome Collection, "
    '<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. '
    "Av. Nossa Senhora de Copacabana: foto de Andrevruas, "
    '<a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>, via Wikimedia Commons.'
)

MANIFESTO = json.loads((SAIDA / "assets" / "img" / "imagens.json").read_text())
AVALIACOES = json.loads((SAIDA / "assets" / "data" / "reviews.json").read_text(encoding="utf-8"))

MSG_PADRAO = "Olá! Vim pelo site da Hairzenith e gostaria de agendar uma consulta."
MSG_LARISSA = "Olá! Vim pelo site da Hairzenith e gostaria de agendar a Consulta Signature, com a Dra. Larissa Pessoa."
MSG_EQUIPE = "Olá! Vim pelo site da Hairzenith e gostaria de agendar a Consulta Expert."

ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def href_artigo(artigo):
    """A página da revista abre. Em 10/11/2026 o DOI ...bjhh20 respondia 404 no doi.org."""
    return artigo["url"]


def wa(msg=MSG_PADRAO, numero=None):
    return f"https://wa.me/{numero or WHATS}?text={quote(msg)}"


def telefone_internacional(numero=None):
    """WhatsApp no formato do schema.org. Sem número, usa o de Copacabana."""
    d = numero or WHATS
    if len(d) == 13 and d.startswith("55"):
        return f"+{d[:2]}-{d[2:4]}-{d[4:9]}-{d[9:]}"
    return "+" + d


def fones_unidades():
    return " · ".join(f'{u["nome"]} {u["whats_texto"]}' for u in UNIDADES)


def e(texto):
    return html.escape(texto, quote=True)


def abrir_whatsapp(documento):
    """Todo link de WhatsApp abre em outra aba, com o mesmo número."""
    def troca(ocorrencia):
        tag = ocorrencia.group(0)
        if "target=" in tag:
            return tag
        return tag[:-1] + ' target="_blank" rel="noopener noreferrer">'

    return re.sub(r'<a\b[^>]*href="https://wa\.me/[^"]*"[^>]*>', troca, documento)


# ---------------------------------------------------------------- imagens
def pic(nome, alt, sizes="(max-width: 900px) 100vw, 40vw", prioridade=False):
    m = MANIFESTO[nome]
    g, p = m["g"], m["p"]
    carregamento = ' fetchpriority="high"' if prioridade else ' loading="lazy" decoding="async"'
    img = (
        f'<img src="~/assets/img/{nome}.jpg" srcset="~/assets/img/{nome}-p.jpg {p[0]}w, ~/assets/img/{nome}.jpg {g[0]}w" '
        f'sizes="{sizes}" width="{g[0]}" height="{g[1]}" alt="{e(alt)}"{carregamento}>'
    )
    fontes = []
    for tipo in ("avif", "webp"):
        grande = SAIDA / "assets" / "img" / f"{nome}.{tipo}"
        pequena = SAIDA / "assets" / "img" / f"{nome}-p.{tipo}"
        if not grande.is_file():
            continue
        if pequena.is_file():
            srcset = f"~/assets/img/{nome}-p.{tipo} {p[0]}w, ~/assets/img/{nome}.{tipo} {g[0]}w"
        else:
            srcset = f"~/assets/img/{nome}.{tipo} {g[0]}w"
        fontes.append(f'<source type="image/{tipo}" srcset="{srcset}" sizes="{sizes}">')
    if not fontes:
        return img
    return f'<picture>{"".join(fontes)}{img}</picture>'


def pic_pasta(pasta, nome, alt, grande, pequena, sizes):
    """Antes e depois que só existem em AVIF e WebP, com a versão -p no srcset."""
    gw, gh = grande
    pw, _ph = pequena
    fontes = []
    for tipo in ("avif", "webp"):
        srcset = f"~/assets/img/{pasta}/{nome}-p.{tipo} {pw}w, ~/assets/img/{pasta}/{nome}.{tipo} {gw}w"
        fontes.append(f'<source type="image/{tipo}" srcset="{srcset}" sizes="{sizes}">')
    img = (
        f'<img src="~/assets/img/{pasta}/{nome}.webp" '
        f'srcset="~/assets/img/{pasta}/{nome}-p.webp {pw}w, ~/assets/img/{pasta}/{nome}.webp {gw}w" '
        f'sizes="{sizes}" width="{gw}" height="{gh}" alt="{e(alt)}" loading="lazy" decoding="async">'
    )
    return f'<picture>{"".join(fontes)}{img}</picture>'


def moldura(nome, alt, sizes="(max-width: 900px) 100vw, 40vw", attrs="data-open", prioridade=False, classe="frame"):
    return f'<div class="{classe}" {attrs}>{pic(nome, alt, sizes, prioridade)}</div>'


# ---------------------------------------------------------------- desenhos (Atlas Topográfico & Carta Costeira)
def mapa_zenite():
    """Atlas Topográfico Craniano vista do zênite (instrumento clínico em ouro e obsidiana)."""
    cx, cy, rx, ry = 200, 262, 132, 174

    def bez(p0, p1, p2, p3, n=14):
        pts = []
        for i in range(n + 1):
            t = i / n
            a = (1 - t) ** 3
            b = 3 * (1 - t) ** 2 * t
            c = 3 * (1 - t) * t * t
            d = t ** 3
            pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
        return pts

    def quad(p0, p1, p2, n=6):
        return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]

    # Linha frontal e silhueta folicular
    linha = []
    linha += bez((76, 204), (84, 180), (100, 162), (114, 156))
    linha += quad((114, 156), (128, 165), (140, 170))[1:]
    linha += bez((140, 170), (150, 148), (174, 134), (200, 131))[1:]
    linha += bez((200, 131), (226, 134), (250, 148), (260, 170))[1:]
    linha += quad((260, 170), (272, 165), (286, 156))[1:]
    linha += bez((286, 156), (300, 162), (316, 180), (324, 204))[1:]
    t0 = math.atan2((204 - cy) / ry, (324 - cx) / rx)
    t1 = math.atan2((204 - cy) / ry, (76 - cx) / rx) + 2 * math.pi
    arco = [(cx + rx * math.cos(t0 + (t1 - t0) * i / 60), cy + ry * math.sin(t0 + (t1 - t0) * i / 60)) for i in range(1, 61)]
    borda = linha + arco

    # Vetores foliculares delicados irradiando do redemoinho da coroa
    seg = [math.dist(borda[i], borda[(i + 1) % len(borda)]) for i in range(len(borda))]
    total = sum(seg)
    wx, wy = 204, 344
    fios = []
    n = 72
    for k in range(n):
        alvo = total * k / n
        acc, i = 0, 0
        while acc + seg[i] < alvo:
            acc += seg[i]
            i += 1
        f = (alvo - acc) / seg[i]
        ex = borda[i][0] + (borda[(i + 1) % len(borda)][0] - borda[i][0]) * f
        ey = borda[i][1] + (borda[(i + 1) % len(borda)][1] - borda[i][1]) * f
        ang = math.atan2(ey - wy, ex - wx)
        r0 = 6 + (k % 3) * 3
        sx, sy = wx + r0 * math.cos(ang + 0.95), wy + r0 * math.sin(ang + 0.95)
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        giro = 0.36
        qx = wx + (mx - wx) * math.cos(giro) - (my - wy) * math.sin(giro)
        qy = wy + (mx - wx) * math.sin(giro) + (my - wy) * math.cos(giro)
        fios.append(f"M{sx:.1f} {sy:.1f}Q{qx:.1f} {qy:.1f} {ex:.1f} {ey:.1f}")

    cabelo = (
        "M76 204C84 180 100 162 114 156Q128 165 140 170C150 148 174 134 200 131C226 134 250 148 260 170"
        "Q272 165 286 156C300 162 316 180 324 204A132 174 0 1 1 76 204Z"
    )
    soltos = [
        "M46 458q14 -10 28 -4t24 -8", "M76 482q10 4 22 -6t28 2", "M294 462q12 -12 26 -6t20 -10",
        "M318 488q-14 -2 -22 6t-24 -2", "M154 492q16 -8 28 0t22 -6", "M34 416q10 10 6 24",
        "M364 410q-8 12 -2 26", "M224 496q12 -6 24 2t20 -4",
    ]
    zonas = {
        "calvicie-masculina": '<ellipse cx="128" cy="160" rx="28" ry="18" transform="rotate(-35 128 160)"/>'
                              '<ellipse cx="272" cy="160" rx="28" ry="18" transform="rotate(35 272 160)"/>'
                              f'<circle cx="{wx}" cy="{wy}" r="48"/>',
        "calvicie-feminina": '<path d="M200 132Q218 218 205 314Q184 218 200 132Z"/>',
        "couro-cabeludo-aparente": '<ellipse cx="200" cy="248" rx="74" ry="86"/>',
        "perda-de-densidade-capilar": f'<path d="{cabelo}"/>',
    }
    nomes_zona = {
        "perda-de-densidade-capilar": "Perda de densidade: o cabelo inteiro",
        "couro-cabeludo-aparente": "Couro cabeludo aparente: o topo",
        "calvicie-feminina": "Calvície feminina: a risca",
        "calvicie-masculina": "Calvície masculina: entradas e coroa",
        "queda-de-cabelo": "Queda de cabelo: fios soltos",
    }
    acertos = [
        ("perda-de-densidade-capilar", f'<path d="{cabelo}"/>'),
        ("couro-cabeludo-aparente", '<ellipse cx="200" cy="238" rx="58" ry="60"/>'),
        ("calvicie-feminina", '<path d="M200 128Q226 218 206 304Q174 218 200 128Z"/>'),
        ("calvicie-masculina", zonas["calvicie-masculina"]),
        ("queda-de-cabelo", '<path d="M10 400H120V520H10ZM280 400H392V520H280ZM120 480H280V520H120Z"/>'),
    ]
    # Anéis micrométricos e retículo topográfico
    reticulo = (
        '<g class="zmap-grid" aria-hidden="true">'
        '<circle cx="200" cy="262" r="190" fill="none" stroke="currentColor" stroke-opacity="0.12" stroke-dasharray="2 6"/>'
        '<circle cx="200" cy="262" r="156" fill="none" stroke="currentColor" stroke-opacity="0.09"/>'
        '<line x1="200" y1="36" x2="200" y2="490" stroke="currentColor" stroke-opacity="0.12" stroke-dasharray="3 5"/>'
        '<line x1="24" y1="262" x2="376" y2="262" stroke="currentColor" stroke-opacity="0.12" stroke-dasharray="3 5"/>'
        '<text x="200" y="26" text-anchor="middle" class="zmap-axis">REGIÃO FRONTAL • 0°</text>'
        '<text x="200" y="512" text-anchor="middle" class="zmap-axis">VÉRTICE &amp; COROA • 180°</text>'
        '</g>'
    )
    partes = [
        '<svg viewBox="0 0 400 524" role="group" aria-label="Atlas topográfico da cabeça vista do zênite, com zonas de avaliação clínica">',
        '<defs>'
        '<clipPath id="zc"><path d="' + cabelo + '"/></clipPath>'
        '<radialGradient id="goldGlow" cx="50%" cy="50%" r="55%">'
        '<stop offset="0%" stop-color="#E5C888" stop-opacity="0.92"/>'
        '<stop offset="65%" stop-color="#C5A059" stop-opacity="0.55"/>'
        '<stop offset="100%" stop-color="#C5A059" stop-opacity="0"/>'
        '</radialGradient>'
        '</defs>',
        reticulo,
        '<path class="skin" d="M188 90Q200 62 212 90Z"/>',
        f'<ellipse class="skin" cx="66" cy="268" rx="11" ry="25"/><ellipse class="skin" cx="334" cy="268" rx="11" ry="25"/>',
        f'<ellipse class="skin" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>',
        f'<path class="hair" d="{cabelo}"/>',
        '<g class="strands" clip-path="url(#zc)"><path d="' + "".join(fios) + '"/></g>',
        '<g class="loose"><path d="' + "".join(soltos) + '"/></g>',
    ]
    for zona, forma in zonas.items():
        partes.append(f'<g class="zone z-{zona}">{forma}</g>')
    for zona, forma in acertos:
        partes.append(
            f'<g class="zone-hit" data-zone-hit="{zona}" tabindex="0" role="button" aria-label="{e(nomes_zona[zona])}">{forma}</g>'
        )
    partes.append("</svg>")
    return "".join(partes)


def mapa_litoral():
    """Carta cartográfica do litoral do Rio a Cabo Frio, com as duas unidades marcadas."""
    lon0, lon1, lat0 = -43.25, -41.95, -22.56
    W = 520
    k = W / ((lon1 - lon0) * math.cos(math.radians(22.9)))
    H = round(W / 1.31)

    def xy(lon, lat):
        return ((lon - lon0) * math.cos(math.radians(22.9)) * k, (lat0 - lat) * k)

    costa = [
        (-43.30, -23.010), (-43.245, -22.995), (-43.205, -22.988), (-43.188, -22.982), (-43.172, -22.968),
        (-43.156, -22.955), (-43.150, -22.935), (-43.135, -22.932), (-43.120, -22.945), (-43.090, -22.960),
        (-43.030, -22.973), (-42.920, -22.962), (-42.780, -22.957), (-42.620, -22.938), (-42.480, -22.933),
        (-42.320, -22.940), (-42.180, -22.960), (-42.080, -22.976), (-42.025, -22.990), (-42.003, -22.975),
        (-42.012, -22.930), (-42.000, -22.880), (-41.960, -22.845), (-41.900, -22.790),
    ]
    pts = [xy(*p) for p in costa]

    def suave(p):
        d = f"M{p[0][0]:.1f} {p[0][1]:.1f}"
        for i in range(len(p) - 1):
            p0, p1, p2 = p[max(i - 1, 0)], p[i], p[i + 1]
            p3 = p[min(i + 2, len(p) - 1)]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
        return d

    curva_costa = suave(pts)
    terra = curva_costa + f"L{W + 20} -20L-20 -20Z"
    grade = (
        f'<g class="map-grid" aria-hidden="true">'
        f'<line x1="0" y1="{H*0.33:.1f}" x2="{W}" y2="{H*0.33:.1f}"/>'
        f'<line x1="0" y1="{H*0.66:.1f}" x2="{W}" y2="{H*0.66:.1f}"/>'
        f'<line x1="{W*0.25:.1f}" y1="0" x2="{W*0.25:.1f}" y2="{H}"/>'
        f'<line x1="{W*0.75:.1f}" y1="0" x2="{W*0.75:.1f}" y2="{H}"/>'
        f'</g>'
    )
    pontos = []
    for u in UNIDADES:
        x, y = xy(u["lon"], u["lat"])
        leste = u["id"] == "cabo-frio"
        tx = x + 10 if leste else x - 10
        ancora = "end" if leste else "start"
        ty = xy(-42.01, -23.0)[1] + 34 if leste else y + 42
        pontos.append(
            f'<circle class="map-pulse" cx="{x:.1f}" cy="{y:.1f}" r="18"/>'
            f'<circle class="map-ring" cx="{x:.1f}" cy="{y:.1f}" r="10"/>'
            f'<circle class="map-dot" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/>'
            f'<text class="map-label" x="{tx:.1f}" y="{ty:.1f}" text-anchor="{ancora}">{u["nome"]}</text>'
            f'<text class="map-coords" x="{tx:.1f}" y="{ty + 15:.1f}" text-anchor="{ancora}">{u["coords"]}</text>'
        )
    return (
        f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" '
        'aria-label="Mapa do litoral do Rio de Janeiro a Cabo Frio, com as unidades de Copacabana e Cabo Frio marcadas">'
        f'<rect class="map-sea" width="{W}" height="{H}"/>'
        f'{grade}'
        f'<path class="map-land" d="{terra}"/>'
        f'<path class="map-shore" d="{curva_costa}" fill="none"/>'
        + "".join(pontos)
        + "</svg>"
    )


# ---------------------------------------------------------------- problemas (páginas de SEO)
PROBLEMAS = [
    {
        "slug": "queda-de-cabelo",
        "nome": "Queda de cabelo",
        "titulo": "Queda de cabelo em Copacabana e Cabo Frio | Hairzenith",
        "descricao": "Queda acima de 100 fios por dia tem causa e tratamento. Tricologista em Copacabana e Cabo Frio, com tricoscopia na Hairzenith e plano na primeira consulta.",
        "casos": ["resultado-13", "resultado-15"],
        "lead": "Perder de 50 a 100 fios por dia faz parte do ciclo do cabelo. Quando a queda passa disso, ou não para, ela tem uma causa que pode ser encontrada e tratada.",
        "onde": "No ralo e na escova",
        "zona": "Fios soltos no travesseiro, no ralo e na escova, em quantidade acima do habitual.",
        "condicao": ("Queda de cabelo", ["Eflúvio telógeno", "Queda capilar"]),
        "alto": ("espelho-retrato", "Mulher penteia o cabelo diante do espelho"),
        "quadrado": ("escova-fios", "Fios presos nas cerdas de uma escova"),
        "lateral": ("escovando", "Mulher observa os fios enquanto escova o cabelo"),
        "sinais": [
            ("Mais de 100 fios por dia", "No travesseiro, no ralo e na escova, de forma contínua."),
            ("Fio que cai com a raiz", "O bulbo aparece na ponta do fio, em grande quantidade."),
            ("Queda depois de um evento", "Dois a três meses após febre alta, cirurgia, parto, dieta restritiva ou estresse intenso."),
            ("Couro cabeludo irritado", "Coceira, descamação, sensibilidade ou oleosidade junto com a queda."),
            ("Falhas arredondadas", "Áreas lisas e circulares, que pedem avaliação sem demora."),
            ("Rabo de cavalo mais fino", "O volume diminui mesmo sem você notar os fios caindo."),
        ],
        "causas": [
            ("Eflúvio telógeno", "Queda difusa que aparece semanas depois de um gatilho: febre, cirurgia, parto, perda rápida de peso, estresse. Costuma ser reversível quando o gatilho é tratado."),
            ("Alterações hormonais", "Tireoide, pós-parto, menopausa e o início ou a suspensão de anticoncepcionais mudam o ciclo do fio."),
            ("Deficiências nutricionais", "Ferro, ferritina, vitamina D, zinco e proteína baixos aparecem com frequência nos exames de quem perde cabelo."),
            ("Inflamação do couro cabeludo", "Dermatite seborreica, psoríase e infecções fúngicas enfraquecem o folículo e mantêm a queda ativa."),
            ("Predisposição genética", "Quando a queda vem com afinamento progressivo, pode ser o início da alopecia androgenética, a calvície."),
            ("Medicamentos", "Alguns remédios têm a queda como efeito colateral. A investigação inclui a lista do que você usa."),
        ],
        "causas_pic": ("analise-imagens", "Paciente revisa no notebook as imagens ampliadas dos próprios fios"),
        "tratamentos": [
            ("Tratar a causa", "Corrigir deficiências, controlar a inflamação do couro cabeludo e, quando a origem é hormonal, trabalhar junto com o médico que acompanha você."),
            ("Laser e LED capilar", "Estimulam o folículo e a circulação do couro cabeludo. Indicados para queda difusa e afinamento."),
            ("Microinfusão de ativos", "Ativos levados diretamente ao couro cabeludo para reduzir a queda e fortalecer o fio."),
            ("Mesoject", "Eletroporação: os ativos entram no couro cabeludo sem agulhas, com conforto."),
            ("Cuidado em casa", "Produtos e rotina definidos para o seu couro cabeludo, entre uma sessão e outra."),
        ],
        "trat_pic": ("laser-led", "Capacete de laser e LED posicionado sobre a cabeça de uma paciente"),
        "faq": [
            ("Quantos fios é normal perder por dia?", "Entre 50 e 100, variando com a genética, a estação do ano e a rotina de lavagem. Queda contínua acima disso, falhas visíveis ou fios mais finos pedem avaliação."),
            ("Queda de cabelo tem tratamento?", "Tem, quando o tratamento é dirigido à causa. Por isso a consulta começa pela investigação: história clínica, tricoscopia e, se necessário, exames."),
            ("Em quanto tempo aparece resultado?", "Os primeiros sinais costumam aparecer entre 60 e 90 dias, conforme a causa e o protocolo. A evolução é acompanhada nas reavaliações."),
            ("Preciso fazer exames de sangue?", "Nem sempre. Quando a história e a tricoscopia sugerem uma causa interna, como anemia, tireoide ou falta de vitaminas, os exames confirmam o diagnóstico."),
            ("Lavar o cabelo todo dia aumenta a queda?", "Não. Os fios que caem na lavagem já estavam soltos. Lavar com menos frequência só acumula esses fios para o dia seguinte."),
        ],
    },
    {
        "slug": "calvicie-feminina",
        "nome": "Calvície feminina",
        "titulo": "Calvície feminina em Copacabana e Cabo Frio | Hairzenith",
        "descricao": "Risca mais larga e menos volume no topo. Tratamento sem cirurgia na Hairzenith, com tricoscopia em Copacabana e Cabo Frio, para a calvície feminina.",
        "casos": ["resultado-08", "resultado-14"],
        "lead": "Na mulher, a calvície raramente forma entradas. Ela aparece como uma risca que se alarga e um topo que perde volume, enquanto a linha da testa continua no lugar.",
        "onde": "Na risca do cabelo",
        "zona": "A risca central se alarga e o topo fica mais ralo; a linha da testa costuma se manter.",
        "condicao": ("Alopecia androgenética feminina", ["Calvície feminina", "Alopecia de padrão feminino"]),
        "alto": ("analise-imagens", "Paciente revisa no notebook as imagens ampliadas dos próprios fios"),
        "quadrado": ("resultado-4", "Risca central de uma paciente em três momentos do tratamento"),
        "lateral": ("espelho", "Mulher penteia o cabelo diante do espelho"),
        "sinais": [
            ("Risca mais larga", "Dá para ver mais pele ao longo da risca central do que antes."),
            ("Topo com menos volume", "O cabelo assenta mais rente ao couro cabeludo no alto da cabeça."),
            ("Rabo de cavalo mais fino", "O elástico dá mais voltas do que dava alguns anos atrás."),
            ("Fios de espessuras diferentes", "Fios finos e curtos misturados aos normais, sinal de miniaturização."),
            ("Couro cabeludo sob a luz", "Em fotos com flash ou sob luz de cima, o topo aparece."),
        ],
        "causas": [
            ("Alopecia androgenética", "Predisposição genética e sensibilidade do folículo aos hormônios androgênios. O fio afina a cada ciclo até ficar quase invisível."),
            ("Mudanças hormonais", "Menopausa, pós-parto, síndrome dos ovários policísticos e a suspensão de anticoncepcionais podem iniciar ou acelerar o quadro."),
            ("Queda associada", "Falta de ferro, alterações de tireoide e estresse se somam à calvície e aumentam a perda de volume."),
            ("Microinflamação", "Inflamação discreta ao redor do folículo, visível na tricoscopia, que contribui para a miniaturização."),
        ],
        "causas_pic": ("cowper-1698", "Gravura de 1698 com cortes de pele e folículos capilares ampliados"),
        "tratamentos": [
            ("Plano multimodal", "Tecnologias, ativos e cuidado em casa combinados conforme o grau da calvície. É a abordagem descrita no estudo de caso da equipe sobre alopecia androgenética feminina, publicado em 2025."),
            ("MMP", "Microinfusão de medicamentos na pele: ativos aplicados diretamente na região afetada para estimular as unidades foliculares."),
            ("Laser e LED capilar", "Estimulam o folículo e a circulação, com sessões sem dor e sem tempo de recuperação."),
            ("Mesoject", "Ativos levados ao couro cabeludo por eletroporação, sem agulhas."),
            ("Fator hormonal", "Quando há componente hormonal, o tratamento é conduzido junto com a ginecologista ou a endocrinologista."),
        ],
        "trat_pic": ("microinfusao", "Aplicação de ativos ao longo da risca do cabelo"),
        "faq": [
            ("Calvície feminina tem cura?", "Não existe cura definitiva, mas existe controle. O tratamento contínuo desacelera a miniaturização, recupera densidade e preserva os fios que você tem."),
            ("Como diferenciar calvície de queda?", "Na queda, você vê fios caindo. Na calvície, você vê o volume diminuir, muitas vezes sem queda perceptível. A tricoscopia mostra a miniaturização e separa os dois quadros, que podem acontecer juntos."),
            ("Em quanto tempo aparece resultado?", "Os primeiros sinais aparecem entre 60 e 120 dias, conforme o estágio. A calvície pede acompanhamento contínuo, com reavaliações periódicas."),
            ("Vou precisar de transplante?", "Na maioria dos casos tratados cedo, não. O tratamento clínico recupera e mantém densidade sem cirurgia. Em quadros muito avançados, a avaliação indica se vale considerar o transplante."),
            ("A menopausa piora a calvície?", "Pode acelerar. Com a queda do estrogênio, o folículo fica mais exposto aos androgênios. Por isso a avaliação considera a sua fase hormonal."),
        ],
    },
    {
        "slug": "calvicie-masculina",
        "nome": "Calvície masculina",
        "titulo": "Calvície masculina em Copacabana e Cabo Frio | Hairzenith",
        "descricao": "Entradas subindo e coroa abrindo. Tratamento sem cirurgia na Hairzenith, com tricologista em Copacabana e Cabo Frio, a partir da primeira consulta.",
        "casos": ["resultado-09", "resultado-10"],
        "lead": "As entradas sobem, a coroa abre. A calvície masculina é progressiva, e quanto antes é tratada, mais fios ainda podem ser preservados.",
        "onde": "Nas entradas e na coroa",
        "zona": "Entradas que sobem nas têmporas e uma coroa que se abre no alto da cabeça.",
        "condicao": ("Alopecia androgenética masculina", ["Calvície masculina", "Alopecia de padrão masculino"]),
        "alto": ("homem-entradas-retrato", "Homem de barba grisalha examina as entradas no espelho"),
        "quadrado": ("resultado-7", "Topo da cabeça de um paciente antes e depois do tratamento"),
        "lateral": ("homem-entradas", "Homem de barba grisalha examina as entradas no espelho"),
        "sinais": [
            ("Entradas mais fundas", "As têmporas recuam e a linha da testa ganha a forma de um M."),
            ("Coroa aparente", "O redemoinho no alto da cabeça se abre e mostra o couro cabeludo."),
            ("Fios mais finos na frente", "O cabelo da região frontal fica mais curto e mais fraco que o das laterais."),
            ("Histórico na família", "Pai, avô ou tios com calvície aumentam a chance, dos dois lados da família."),
            ("Fotos antigas", "A comparação com fotos de alguns anos atrás mostra o que o espelho do dia a dia esconde."),
        ],
        "causas": [
            ("Alopecia androgenética", "A di-hidrotestosterona (DHT) age sobre folículos geneticamente sensíveis e os miniaturiza a cada ciclo."),
            ("Herança genética", "A sensibilidade do folículo é herdada e pode vir tanto do lado materno quanto do paterno."),
            ("O que acelera", "Estresse, tabagismo, deficiências nutricionais e inflamação do couro cabeludo podem acelerar o processo."),
            ("Hormônios e anabolizantes", "Substâncias que elevam a testosterona aceleram a calvície em quem tem predisposição."),
        ],
        "causas_pic": ("tricoscopio-retrato", "Tricoscópio digital apoiado no couro cabeludo durante a avaliação"),
        "tratamentos": [
            ("Protocolo por estágio", "O grau da calvície define a combinação de tecnologias e ativos. Entradas iniciais pedem um plano; coroas abertas, outro."),
            ("MMP", "Microinfusão de medicamentos na pele, diretamente nas regiões afetadas, para estimular as unidades foliculares."),
            ("Laser e LED capilar", "Estímulo ao folículo e à circulação, em sessões sem dor e sem afastamento da rotina."),
            ("Microinfusão de ativos", "Ativos que fortalecem o fio e reduzem a queda associada."),
            ("Manutenção", "A calvície é crônica. Depois da fase intensiva, um plano de manutenção preserva o que foi recuperado."),
        ],
        "trat_pic": ("mesoject-retrato", "Caneta do Mesoject aplicada sobre o couro cabeludo"),
        "faq": [
            ("Calvície tem cura?", "Não, mas pode ser controlada. Com tratamento contínuo é possível desacelerar a evolução, recuperar densidade e preservar os fios existentes, sem cirurgia."),
            ("Quando começar o tratamento?", "Assim que as entradas ou a coroa começam a mudar. Um folículo miniaturizado ainda responde ao tratamento; um folículo perdido, não."),
            ("Em quanto tempo aparece resultado?", "Os primeiros sinais aparecem entre 60 e 120 dias, conforme o estágio e o protocolo."),
            ("O tratamento substitui o transplante?", "Em estágios iniciais e intermediários, o tratamento clínico pode evitar a cirurgia. Em quem já fez transplante, ele protege os fios nativos ao redor."),
        ],
    },
    {
        "slug": "couro-cabeludo-aparente",
        "nome": "Couro cabeludo aparente",
        "titulo": "Couro cabeludo aparente em Copacabana e Cabo Frio | Hairzenith",
        "descricao": "Couro cabeludo visível no topo, na risca ou sob a luz. Avaliação com tricoscopia na Hairzenith, em Copacabana e Cabo Frio, para recuperar cobertura sem cirurgia.",
        "casos": ["resultado-11", "resultado-15"],
        "lead": "Sob a luz do banheiro, no flash do celular, com o cabelo molhado: quando o couro cabeludo começa a aparecer, os fios perderam número, espessura ou os dois.",
        "onde": "Sob a luz, no topo",
        "zona": "O topo da cabeça aparece sob luz forte, no flash ou com o cabelo molhado.",
        "condicao": ("Rarefação capilar", ["Couro cabeludo aparente", "Baixa cobertura capilar"]),
        "alto": ("tela-tricoscopia-retrato", "Imagem ampliada dos fios na tela durante a tricoscopia"),
        "quadrado": ("resultado-5", "Topo da cabeça de uma paciente em três momentos do tratamento"),
        "lateral": ("tela-tricoscopia", "Imagem ampliada dos fios na tela durante a tricoscopia"),
        "sinais": [
            ("No flash e sob luz de cima", "O couro cabeludo aparece em fotos e em elevadores, mesmo com o cabelo seco."),
            ("Com o cabelo molhado", "Os fios se agrupam e deixam caminhos de pele visíveis."),
            ("Na risca e no redemoinho", "As duas regiões abrem primeiro, porque já separam os fios naturalmente."),
            ("Penteados que mudaram", "Você passou a escolher a risca ou o volume para esconder o topo."),
        ],
        "causas": [
            ("Miniaturização", "Os fios continuam lá, mas mais finos. Cobrem menos e deixam a pele aparecer: é o caminho da calvície."),
            ("Menos fios por área", "Uma queda que se prolonga reduz o número de fios em cada unidade folicular."),
            ("Unidades foliculares vazias", "Na tricoscopia, aparecem como pontos sem fio, onde o folículo parou de produzir."),
            ("Couro cabeludo inflamado", "Vermelhidão e descamação deixam a pele mais visível e prejudicam o crescimento."),
        ],
        "causas_pic": ("cowper-1698", "Gravura de 1698 com cortes de pele e folículos capilares ampliados"),
        "tratamentos": [
            ("Mapear antes de tratar", "A tricoscopia mostra onde a cobertura caiu e por quê: fio mais fino, menos fios ou inflamação."),
            ("Laser e LED capilar", "Estimulam os folículos ainda ativos a produzir fios mais grossos."),
            ("MMP", "Ativos aplicados diretamente nas áreas de menor cobertura."),
            ("Microinfusão de ativos", "Fortalece o fio e reduz a queda que mantém o topo ralo."),
            ("Acompanhamento por imagem", "Fotos padronizadas do topo em cada reavaliação mostram a evolução da cobertura."),
        ],
        "trat_pic": ("tricoscopio-retrato", "Tricoscópio digital apoiado no couro cabeludo durante a avaliação"),
        "faq": [
            ("Couro cabeludo aparente é sempre calvície?", "Não. Pode ser calvície, queda prolongada, inflamação ou uma combinação delas. A tricoscopia diferencia os quadros."),
            ("Dá para recuperar a cobertura?", "Quando o folículo ainda está ativo, sim: tratar a causa e estimular o fio devolve espessura e densidade. Por isso a avaliação cedo faz diferença."),
            ("Maquiagem e pigmentação capilar resolvem?", "Disfarçam, e podem ser usadas durante o tratamento. Não tratam a causa."),
            ("Quanto tempo leva?", "Os primeiros sinais aparecem entre 60 e 120 dias. A cobertura melhora de forma gradual ao longo dos meses de acompanhamento."),
        ],
    },
    {
        "slug": "afinamento-dos-fios",
        "nome": "Afinamento dos fios",
        "titulo": "Afinamento dos fios em Copacabana e Cabo Frio | Hairzenith",
        "descricao": "Fios mais finos, curtos e frágeis podem ser miniaturização. Tricologista em Copacabana e Cabo Frio, na Hairzenith, com plano definido na consulta.",
        "casos": ["resultado-13", "resultado-14"],
        "lead": "Muitas vezes o primeiro sinal não é a queda, é o fio. Ele nasce mais fino, cresce menos e quebra mais fácil, e o volume vai embora sem que você veja os fios caindo.",
        "onde": "No rabo de cavalo",
        "zona": "Os fios ficam mais finos em toda a cabeça e o rabo de cavalo perde espessura.",
        "condicao": ("Miniaturização capilar", ["Afinamento dos fios", "Afinamento capilar"]),
        "alto": ("tricoscopio-retrato", "Tricoscópio digital apoiado no couro cabeludo durante a avaliação"),
        "quadrado": ("fio-na-mao", "Mulher segura entre os dedos um fio que caiu"),
        "lateral": ("textura-castanha", "Fios castanhos lisos vistos de perto"),
        "sinais": [
            ("Rabo de cavalo mais fino", "A mesma quantidade de cabelo dá mais voltas no elástico."),
            ("Fios que não crescem", "O comprimento parece travado: o fio cai antes de chegar onde chegava."),
            ("Pontas finas e quebradiças", "O fio perde diâmetro e se parte com facilidade."),
            ("Fios curtos no topo", "Fios finos e curtos aparecem no meio do cabelo, principalmente na risca."),
        ],
        "causas": [
            ("Miniaturização", "A cada ciclo o folículo produz um fio mais fino. É o mecanismo da calvície, feminina e masculina."),
            ("Deficiências nutricionais", "Proteína, ferro e vitaminas em falta comprometem a fabricação do fio."),
            ("Danos químicos e térmicos", "Descolorações, alisamentos e calor frequente afinam e quebram o fio, sem afetar a raiz."),
            ("Fase hormonal", "Pós-parto, menopausa e alterações de tireoide mudam a espessura do fio."),
        ],
        "causas_pic": ("cowper-1698", "Gravura de 1698 com cortes de pele e folículos capilares ampliados"),
        "tratamentos": [
            ("Raiz ou haste", "A tricoscopia mostra se o problema está no folículo, que produz um fio fino, ou na haste, danificada depois de nascer."),
            ("Laser e LED capilar", "Estimulam o folículo a voltar a produzir fios de maior diâmetro."),
            ("Microinfusão de ativos", "Ativos que nutrem o folículo e fortalecem o fio desde a raiz."),
            ("Terapia capilar", "Cuidados com foco terapêutico, não só estético, para a saúde do couro cabeludo e da fibra."),
            ("Rotina em casa", "Produtos e hábitos ajustados ao seu tipo de fio entre uma sessão e outra."),
        ],
        "trat_pic": ("laser-led", "Capacete de laser e LED posicionado sobre a cabeça de uma paciente"),
        "faq": [
            ("Fio fino volta a engrossar?", "Quando o folículo ainda está ativo, sim. Tratado a tempo, ele volta a produzir fios mais grossos ao longo dos ciclos seguintes."),
            ("Afinamento é o começo da calvície?", "Pode ser. Fios de espessuras diferentes na mesma região são o sinal mais precoce da alopecia androgenética. Mas também há causas nutricionais e hormonais, que a avaliação separa."),
            ("Química e escova estragam a raiz?", "Danificam a haste, o fio que já nasceu. A raiz continua produzindo normalmente. A tricoscopia mostra qual dos dois está acontecendo."),
            ("Quanto tempo para ver diferença?", "O fio novo leva meses para ganhar comprimento. Os primeiros sinais aparecem entre 60 e 120 dias, com melhora progressiva."),
        ],
    },
    {
        "slug": "perda-de-densidade-capilar",
        "nome": "Perda de densidade capilar",
        "titulo": "Perda de densidade capilar em Copacabana e Cabo Frio | Hairzenith",
        "descricao": "Menos volume e menos fios por área. Tratamento na Hairzenith, clínica de tricologia em Copacabana e Cabo Frio, com acompanhamento por imagem.",
        "casos": ["resultado-08", "resultado-11"],
        "lead": "Densidade é a quantidade de fios por centímetro quadrado. Quando ela cai, o cabelo perde corpo e volume, mesmo antes de qualquer falha ficar visível.",
        "onde": "No volume, ano a ano",
        "zona": "O cabelo inteiro perde corpo e volume, sem uma falha localizada.",
        "condicao": ("Perda de densidade capilar", ["Rarefação capilar difusa"]),
        "alto": ("laser-led", "Capacete de laser e LED posicionado sobre a cabeça de uma paciente"),
        "quadrado": ("textura-loira", "Mechas loiras onduladas vistas de perto"),
        "lateral": ("textura-loira", "Mechas loiras onduladas vistas de perto"),
        "sinais": [
            ("Menos volume que antes", "O cabelo parece mais leve e mais rente à cabeça, com o mesmo corte."),
            ("Penteados que não seguram", "O volume não se sustenta ao longo do dia."),
            ("Fios mais espaçados", "Ao separar o cabelo em mechas, há mais espaço entre os fios."),
            ("Diferença em fotos antigas", "O contraste aparece ao comparar com fotos de dois ou três anos atrás."),
        ],
        "causas": [
            ("Calvície em estágio inicial", "A alopecia androgenética reduz a densidade antes de abrir falhas visíveis."),
            ("Queda crônica", "Um eflúvio que se prolonga por meses diminui o número de fios em crescimento."),
            ("Envelhecimento do folículo", "Com a idade, parte dos folículos passa a produzir menos fios por unidade folicular."),
            ("Saúde geral", "Tireoide, anemia, dietas restritivas e estresse prolongado se refletem na densidade."),
        ],
        "causas_pic": ("tela-tricoscopia-retrato", "Imagem ampliada dos fios na tela durante a tricoscopia"),
        "tratamentos": [
            ("Medir para comparar", "A densidade é registrada na primeira consulta e comparada nas reavaliações, com fotos na mesma posição."),
            ("Laser e LED capilar", "Estímulo contínuo aos folículos ativos para recuperar fios em crescimento."),
            ("MMP", "Ativos aplicados nas regiões de menor densidade."),
            ("Mesoject", "Ativos por eletroporação, sem agulhas, para quem busca conforto."),
            ("Plano contínuo", "A densidade se recupera ciclo a ciclo. O plano prevê uma fase intensiva e uma de manutenção."),
        ],
        "trat_pic": ("mesoject-retrato", "Caneta do Mesoject aplicada sobre o couro cabeludo"),
        "faq": [
            ("Como se mede a densidade capilar?", "Pela tricoscopia, que amplia o couro cabeludo e permite contar fios e unidades foliculares em uma área definida."),
            ("A densidade perdida volta?", "Enquanto os folículos estiverem ativos, é possível recuperar parte da densidade e preservar o restante. A resposta varia de pessoa para pessoa."),
            ("Qual a diferença entre densidade e espessura?", "Densidade é quantos fios você tem; espessura é o diâmetro de cada fio. As duas definem o volume, e o tratamento considera as duas."),
            ("Em quanto tempo aparece resultado?", "Os primeiros sinais aparecem entre 60 e 120 dias. A densidade melhora de forma progressiva ao longo do acompanhamento."),
        ],
    },
]
POR_SLUG = {p["slug"]: p for p in PROBLEMAS}

RESULTADOS = [
    ("resultado-1", "Coroa", "antes e depois", "Coroa: fotos de antes e depois do tratamento"),
    ("resultado-7", "Topo da cabeça", "antes e depois", "Topo da cabeça: fotos de antes e depois do tratamento"),
    ("resultado-4", "Risca central", "três etapas", "Risca central: fotos de antes e depois do tratamento"),
    ("resultado-2", "Linha frontal", "antes e depois", "Linha frontal: fotos de antes e depois do tratamento"),
    ("resultado-5", "Topo", "três etapas", "Topo: fotos de antes e depois do tratamento"),
    ("resultado-3", "Têmpora", "antes e depois", "Têmpora: fotos de antes e depois do tratamento"),
    ("resultado-6", "Região frontal", "antes e depois", "Região frontal: fotos de antes e depois do tratamento"),
    ("resultado-08", "Risca central", "antes e depois", "Risca central: antes e depois do tratamento, com a divisão mais fechada na segunda foto"),
    ("resultado-09", "Coroa", "antes e depois", "Coroa: antes e depois do tratamento, com mais cobertura no topo na segunda foto"),
    ("resultado-10", "Linha frontal", "antes e depois", "Linha frontal: antes e depois do tratamento, com a testa mais coberta na segunda foto"),
    ("resultado-11", "Coroa", "antes e depois", "Coroa: antes e depois do tratamento, com a falha do topo mais preenchida na segunda foto"),
    ("resultado-12", "Topo da cabeça", "antes e depois", "Topo da cabeça: antes e depois do tratamento, com mais densidade na segunda foto"),
    ("resultado-13", "Risca e topo", "antes e depois", "Risca e topo: antes e depois do tratamento, com mais volume ao longo da divisão na segunda foto"),
    ("resultado-14", "Risca", "antes e depois", "Risca: antes e depois do tratamento, com menos couro cabeludo visível na segunda foto"),
    ("resultado-15", "Topo", "antes e depois", "Topo: antes e depois do tratamento, com a coroa mais coberta na segunda foto"),
]
MEDIDAS_NOVAS = {
    "resultado-08": ((1200, 789), (600, 395)),
    "resultado-09": ((1200, 695), (600, 348)),
    "resultado-10": ((1200, 654), (600, 327)),
    "resultado-11": ((1200, 673), (600, 336)),
    "resultado-12": ((1200, 821), (600, 411)),
    "resultado-13": ((1200, 724), (600, 362)),
    "resultado-14": ((1200, 603), (600, 301)),
    "resultado-15": ((1200, 827), (600, 413)),
}

MOMENTOS = [
    ("Primeiro, a sua história", "Você conta quando a queda começou, o que mudou na rotina e o que espera do tratamento.", "larissa-sentada", "Dra. Larissa Pessoa sentada em uma poltrona clara", "Anamnese Clínica"),
    ("Depois, a tricoscopia", "O couro cabeludo é examinado com ampliação de até 200 vezes: inflamação, descamação, afinamento, unidades foliculares vazias.", "tricoscopio-retrato", "Tricoscópio digital apoiado no couro cabeludo", "Exame Óptico 200×"),
    ("Na tela, com você", "As imagens ampliadas aparecem na tela, e cada achado é explicado durante a consulta.", "tela-tricoscopia-retrato", "Imagem ampliada dos fios na tela durante a tricoscopia", "Mapeamento Visual"),
    ("Exames, se precisar", "Quando a causa pede investigação, são solicitados exames: ferro, vitaminas, tireoide, hormônios.", "analise-imagens", "Paciente revisa no notebook as imagens dos próprios fios", "Investigação Sistêmica"),
    ("O plano de tratamento", "Em casa, no consultório ou nos dois, com tecnologias escolhidas para a causa: laser e LED, MMP, microinfusão, Mesoject.", "microinfusao", "Aplicação de ativos ao longo da risca do cabelo", "Protocolo Sob Medida"),
    ("Os primeiros sinais", "Os resultados costumam aparecer entre 60 e 120 dias, conforme a causa e o protocolo.", "laser-led", "Capacete de laser e LED sobre a cabeça de uma paciente", "Ciclo de Resposta"),
    ("As reavaliações", "A evolução é fotografada e comparada a cada retorno, e o plano é ajustado a cada etapa.", "mesoject-retrato", "Caneta do Mesoject aplicada sobre o couro cabeludo", "Controle Evolutivo"),
]

GLOSSARIO = [
    ("Tricoscopia", "Exame que amplia o couro cabeludo e os fios, na Hairzenith em até 200 vezes, para ver o que o olho não alcança: inflamação, miniaturização, densidade."),
    ("Folículo piloso", "A estrutura dentro da pele que produz o fio. Enquanto está ativo, pode ser estimulado; quando se perde, não volta."),
    ("Unidade folicular", "O grupo natural de um a quatro fios que nascem juntos. Unidades com menos fios, ou vazias, indicam perda de densidade."),
    ("Miniaturização", "Afinamento progressivo do fio a cada ciclo, típico da alopecia androgenética. O folículo encolhe e produz fios cada vez mais finos e curtos."),
    ("Alopecia androgenética", "O nome técnico da calvície, feminina e masculina. Tem base genética e hormonal e evolui aos poucos."),
    ("Eflúvio telógeno", "Queda difusa e intensa que aparece semanas depois de um gatilho, como febre, parto, cirurgia ou estresse. Costuma ser reversível."),
    ("Densidade capilar", "A quantidade de fios por centímetro quadrado de couro cabeludo. É ela que define o volume, junto com a espessura de cada fio."),
    ("Ciclo capilar", "As fases de vida de cada fio: crescimento, transição e repouso, até cair e dar lugar a um novo. A queda e a calvície alteram esse ciclo."),
]

TECNOLOGIAS = [
    ("Tricoscopia digital", "Amplia o couro cabeludo e os fios em até 200 vezes para identificar inflamação, miniaturização, densidade e unidades foliculares vazias."),
    ("Laser e LED capilar", "Luz de baixa intensidade que estimula o crescimento, melhora a circulação do couro cabeludo e fortalece os fios. Indicado para queda difusa e afinamento."),
    ("MMP", "Microinfusão de medicamentos na pele: ativos aplicados diretamente no couro cabeludo para estimular as unidades foliculares."),
    ("Microinfusão de ativos", "Regeneração capilar com ativos direcionados para fortalecer os fios, reduzir a queda e melhorar a vitalidade do cabelo."),
    ("Mesoject", "Tecnologia de eletroporação que leva ativos ao couro cabeludo sem agulhas. Para quem busca conforto aliado à eficiência."),
    ("Terapia capilar", "Cuidados preventivos e terapêuticos para identificar, tratar e controlar disfunções do couro cabeludo e do fio."),
]


# ---------------------------------------------------------------- blocos de página
EMBLEMA_SVG = (
    '<svg class="crest" viewBox="0 0 36 36" aria-hidden="true">'
    '<circle cx="18" cy="18" r="16.5" fill="none" stroke="currentColor" stroke-opacity="0.35" stroke-width="0.9"/>'
    '<circle cx="18" cy="10.5" r="2.6" fill="#C5A059"/>'
    '<path d="M9 23.5H27" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>'
    '<path d="M13 27.5H23" stroke="#C5A059" stroke-width="0.9" stroke-linecap="round" stroke-opacity="0.7"/>'
    '</svg>'
)


def cabecalho(ativo):
    links = [
        ("tratamentos", "Tratamentos", "~/tratamentos/"),
        ("equipe", "Equipe", "~/equipe/"),
        ("consulta", "Consulta", "~/consulta/"),
        ("sobre", "Sobre", "~/sobre/"),
        ("nova-clinica", "Nova clínica", "~/nova-clinica/"),
        ("conteudo", "Conteúdo", "~/conteudo/"),
    ]

    def item(chave, rotulo, href):
        atual = ' aria-current="page"' if chave == ativo else ""
        return f'<a href="{href}"{atual}>{rotulo}</a>'

    nav = "".join(item(*l) for l in links)
    menu = "".join(
        f'<li style="--i:{i}"><span class="menu__roman">{ROMANOS[i]}</span>{item(*l)}</li>'
        for i, l in enumerate([("inicio", "Início", "~/")] + links)
    )
    return f"""
<header class="site-header">
  <div class="notice"><div class="wrap notice__inner"><span class="notice__tag">TRANSIÇÃO DE MARCA</span><p>Larissa Pessoa Tricologia agora é <strong>Hairzenith</strong>. A nova clínica chega em março de 2027. <a class="link" href="~/nova-clinica/">Acompanhe a obra &rarr;</a></p></div></div>
  <div class="nav-shell">
    <nav class="nav wrap" aria-label="Principal">
      <a class="wordmark" href="~/" aria-label="Hairzenith, página inicial">
        {EMBLEMA_SVG}
        <span class="wordmark__text">
          <span class="wordmark__name">Hairzenith</span>
          <span class="wordmark__sub">Tricologia • Dra. Larissa Pessoa</span>
        </span>
      </a>
      <div class="nav__links">{nav}</div>
      <div class="nav__actions">
        <a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu"><span>Menu</span></button>
      </div>
    </nav>
  </div>
  <div class="menu" id="menu" role="dialog" aria-modal="true" aria-label="Menu">
    <div class="menu__top">
      <span class="wordmark">{EMBLEMA_SVG}<span class="wordmark__text"><span class="wordmark__name">Hairzenith</span><span class="wordmark__sub">Tricologia • Dra. Larissa Pessoa</span></span></span>
      <button class="menu__close" type="button">Fechar &times;</button>
    </div>
    <ul>{menu}</ul>
    <div class="menu__footer">
      <a class="button button--gold" href="{wa()}"><span>Agendar pelo WhatsApp</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>
      <p class="menu__note">{fones_unidades()}.</p>
    </div>
  </div>
</header>"""


def rodape():
    colunas = []
    for idx, u in enumerate(UNIDADES):
        colunas.append(
            f'<ul class="foot__col" id="{u["id"]}"><li><span class="foot__kicker">0{idx + 1} • UNIDADE</span>{u["nome"]}</li>'
            f'<li>{u["rua"]}</li><li>{u["bairro"]}</li>'
            f'<li class="foot__coords">{u["coords"]}</li>'
            f'<li><a href="{wa(numero=u["whats"])}">WhatsApp {u["whats_texto"]}</a></li>'
            f'<li><a class="foot__maplink" href="{u["mapa"]}" rel="noopener">Traçar rota no mapa &rarr;</a></li></ul>'
        )
    colunas.append(
        '<ul class="foot__col"><li><span class="foot__kicker">03 • CLÍNICA</span>Hairzenith</li>'
        '<li><a href="~/tratamentos/">Tratamentos</a></li><li><a href="~/equipe/">Equipe</a></li>'
        '<li><a href="~/equipe/larissa-pessoa/">Dra. Larissa Pessoa</a></li>'
        '<li><a href="~/consulta/">Consulta</a></li><li><a href="~/sobre/">Sobre</a></li>'
        '<li><a href="~/nova-clinica/">Nova clínica</a></li><li><a href="~/conteudo/">Conteúdo</a></li></ul>'
    )
    colunas.append(
        f'<ul class="foot__col"><li><span class="foot__kicker">04 • CONTATO</span>Contato</li>'
        f'<li><a href="{wa()}">WhatsApp {WHATS_TEXTO}</a></li>'
        f'<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>'
        f'<li><a href="{INSTAGRAM}" rel="noopener">Instagram {INSTAGRAM_TEXTO}</a></li>'
        "<li>Atendimento exclusivo com hora marcada</li></ul>"
    )
    return f"""
<footer class="foot">
  <div class="wrap">
    <div class="foot__ribbon">
      <div class="foot__brand">
        {EMBLEMA_SVG}
        <div>
          <p class="foot__ribbon-kicker">ALTA TRICOLOGIA INTEGRATIVA</p>
          <p class="foot__ribbon-title">O ponto mais alto do cuidado capilar.</p>
        </div>
      </div>
      <a class="button button--gold" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>
    </div>
    <div class="foot__cols grid">{''.join(colunas)}</div>
    <div class="foot__word" aria-hidden="true"><svg viewBox="0 0 1100 170"><text x="550" y="140" text-anchor="middle" font-family="Cormorant Garamond, Georgia, serif" font-size="150" font-weight="300" letter-spacing="8">HAIRZENITH</text></svg></div>
    <div class="foot__legal">
      <p>© 2026 Hairzenith, antiga Larissa Pessoa Tricologia Integrativa. As informações deste site têm caráter informativo e não substituem uma consulta clínica.</p>
      <p>{CREDITOS}</p>
    </div>
  </div>
</footer>"""


def fecho(frase, pergunta="Qual consulta é para você?", retrato=("larissa-sentada", "Dra. Larissa Pessoa sorri sentada em uma poltrona clara"), comparar=True):
    extra = '<li><a class="link" href="~/consulta/">Comparar as consultas &rarr;</a></li>' if comparar else ""
    return f"""
<section class="close wrap" aria-labelledby="h-agendar">
  <div class="close__card grid" data-spotlight>
    <div class="close__copy">
      <span class="kicker"><span class="kicker__dot"></span> ATENDIMENTO PERSONALIZADO</span>
      <p class="close__sentence" data-reveal>{frase}</p>
    </div>
    <div class="close__portrait">{moldura(retrato[0], retrato[1], "(max-width: 900px) 30vw, 14vw")}</div>
    <div class="close__links" data-reveal style="--i:2">
      <h2 id="h-agendar">{pergunta}</h2>
      <ul class="close__list">
        <li><a class="button button--shimmer" href="{wa()}"><span>Agendar pelo WhatsApp</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a></li>
        {extra}
      </ul>
      <p class="small">Copacabana e Cabo Frio, com hora marcada. WhatsApp {fones_unidades()}.</p>
    </div>
  </div>
</section>"""


def momentos(titulo="O que acontece na sua consulta", id_="h-consulta"):
    colunas = "".join(
        f'<article class="moment" data-spotlight>'
        f'<div class="moment__meta"><span class="moment__num">{idx + 1:02d}</span><span class="moment__tag">{tag}</span></div>'
        f'{moldura(img, alt, "(max-width: 900px) 76vw, 340px")}'
        f'<div class="moment__body"><h3>{t}</h3><p>{d}</p></div>'
        f'</article>'
        for idx, (t, d, img, alt, tag) in enumerate(MOMENTOS)
    )
    return f"""
<section class="moments" data-drag aria-labelledby="{id_}">
  <div class="wrap">
    <div class="moments__top">
      <div>
        <span class="kicker" data-reveal><span class="kicker__dot"></span> PROTOCOLO DE AVALIAÇÃO</span>
        <h2 id="{id_}" class="head" data-reveal>{titulo}</h2>
      </div>
      <div class="moments__buttons"><button type="button" data-prev aria-label="Voltar">&larr;</button><button type="button" data-next aria-label="Avançar">&rarr;</button></div>
    </div>
    <div class="progress" aria-hidden="true"><span></span></div>
  </div>
  <div class="moments__row" tabindex="0" aria-label="Etapas da consulta, role para o lado">{colunas}</div>
</section>"""


def frame_resultado(nome, alt, i, sizes):
    if nome in MEDIDAS_NOVAS:
        grande, pequena = MEDIDAS_NOVAS[nome]
        w, h = grande
        interno = pic_pasta("resultados", nome, alt, grande, pequena, sizes)
    else:
        w, h = MANIFESTO[nome]["g"]
        interno = pic(nome, alt, sizes)
    return f'<div class="frame" data-open data-lightbox style="--i:{i};--r:{w}/{h}">{interno}</div>'


def resultados(ids=None, id_="h-resultados", titulo="Veja a cobertura voltar, sem cirurgia"):
    por_id = {item[0]: item for item in RESULTADOS}
    itens = [por_id[i] for i in ids] if ids else list(RESULTADOS)
    fotos = []
    sizes = "(max-width: 900px) 88vw, 420px"
    for i, (img, regiao, fato, alt) in enumerate(itens):
        cls = "shot shot--lifted" if i == 0 else "shot"
        numero = img.rsplit("-", 1)[-1].zfill(2)
        fotos.append(
            f'<figure class="{cls}" data-spotlight>'
            f'<div class="shot__header"><span>CASO CLÍNICO {numero}</span><span>{fato.upper()}</span></div>'
            f'{frame_resultado(img, alt, i, sizes)}'
            f"<figcaption><span>{regiao}</span><span class=\"shot__zoom\">Ampliar registro &#8599;</span></figcaption></figure>"
        )
    return f"""
<section class="run wrap" aria-labelledby="{id_}">
  <div class="grid">
    <div class="run__aside">
      <span class="kicker" data-reveal><span class="kicker__dot"></span> ANTES E DEPOIS</span>
      <h2 id="{id_}" data-reveal>{titulo}</h2>
      <p class="run__lead" data-reveal>Fotos de pacientes atendidos pela equipe, no mesmo ângulo, antes e depois do tratamento clínico, sem cirurgia.</p>
      <a class="button button--shimmer" href="{wa()}"><span>Agendar uma avaliação</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>
      <p class="run__note">Os resultados variam de pessoa para pessoa. As fotos não identificam quem foi atendido.</p>
    </div>
    <div class="run__track" tabindex="0" aria-label="Fotos de antes e depois, role para o lado">{''.join(fotos)}</div>
  </div>
</section>"""


def nota_pt(valor):
    return f"{float(valor):.1f}".replace(".", ",")


def data_relativa(iso, hoje=None):
    """Data relativa congelada no HTML. O build usa o dia em que o site é gerado."""
    hoje = hoje or date.today()
    dia = datetime.fromisoformat(iso).date()
    dias = max(0, (hoje - dia).days)
    if dias == 0:
        return "hoje"
    if dias == 1:
        return "ontem"
    if dias < 7:
        return f"há {dias} dias"
    meses = (hoje.year - dia.year) * 12 + hoje.month - dia.month
    if hoje.day < dia.day:
        meses -= 1
    if meses < 1:
        semanas = max(1, dias // 7)
        return "há 1 semana" if semanas == 1 else f"há {semanas} semanas"
    if meses < 12:
        return "há 1 mês" if meses == 1 else f"há {meses} meses"
    anos = meses // 12
    return "há 1 ano" if anos == 1 else f"há {anos} anos"


def texto_avaliacao(texto):
    return texto.replace("começanda", "começando")


def estrelas(nota, rotulo=True):
    cheias = int(round(float(nota)))
    icones = []
    for i in range(5):
        opacidade = "1" if i < cheias else "0.28"
        icones.append(
            f'<svg viewBox="0 0 20 20" aria-hidden="true"><path fill="currentColor" fill-opacity="{opacidade}" '
            'd="M10 1.6l2.1 4.6 5 .7-3.6 3.5.9 5L10 13.2 5.6 15.4l.9-5L2.9 6.9l5-.7z"/></svg>'
        )
    acesso = f'role="img" aria-label="{cheias} de 5"' if rotulo else 'aria-hidden="true"'
    return f'<span class="estrelas" {acesso}>{"".join(icones)}</span>'


def faixa_google():
    place = AVALIACOES["place"]
    nota = nota_pt(place["rating"])
    total = place["review_count"]
    frase = f"{nota} no Google · {total} avaliações"
    return f"""
<aside class="google-faixa wrap">
  <a class="google-faixa__link" href="{e(place["url"])}" target="_blank" rel="noopener noreferrer">
    {estrelas(place["rating"], rotulo=False)}
    <span class="google-faixa__texto">{frase}</span>
    <span class="google-faixa__ir" aria-hidden="true">&#8599;</span>
  </a>
</aside>"""


def avatar_avaliacao(review):
    nome = review["first_name"]
    arquivo = review.get("avatar")
    caminho = SAIDA / "assets" / "img" / "depoimentos" / arquivo if arquivo else None
    if caminho and caminho.is_file():
        return (
            f'<img class="depoimento__foto" src="~/assets/img/depoimentos/{e(arquivo)}" width="96" height="96" '
            f'alt="Foto de perfil de {e(nome)} no Google" loading="lazy" decoding="async">'
        )
    paleta = ("#3C342C", "#5A4632", "#2E3A40", "#6B5340", "#243028", "#4A3A32")
    cor = paleta[sum(ord(c) for c in nome) % len(paleta)]
    inicial = nome[:1].upper()
    return f'<span class="depoimento__inicial" style="background:{cor}" aria-hidden="true">{e(inicial)}</span>'


def card_avaliacao(review):
    nome = review["first_name"]
    nota = int(review["rating"])
    quando = data_relativa(review["date"])
    texto = "<br>".join(e(parte) for parte in texto_avaliacao(review["text"]).split("\n"))
    return f"""
<article class="depoimento" data-spotlight>
  <div class="depoimento__quem">
    {avatar_avaliacao(review)}
    <div>
      <p class="depoimento__nome">{e(nome)}</p>
      {estrelas(nota)}
    </div>
  </div>
  <p class="depoimento__quando"><time datetime="{e(review["date"][:10])}">{e(quando)}</time></p>
  <blockquote class="depoimento__texto">{texto}</blockquote>
  <p class="depoimento__selo">Avaliação no Google</p>
</article>"""


def secao_depoimentos(qtd=None, id_="h-depoimentos", titulo="Pacientes contam o que mudou no cabelo"):
    reviews = AVALIACOES["reviews"][:qtd] if qtd else AVALIACOES["reviews"]
    cards = "".join(card_avaliacao(r) for r in reviews)
    return f"""
<section class="depoimentos wrap" aria-labelledby="{id_}">
  <div class="depoimentos__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> AVALIAÇÕES NO GOOGLE</span>
    <h2 id="{id_}" data-reveal>{titulo}</h2>
  </div>
  <div class="depoimentos__lista">{cards}</div>
</section>"""


def passos():
    itens = [
        ("01", "Conte quando a queda começou", "Você diz o que mudou, há quanto tempo e o que espera do tratamento.", "larissa-sentada", "Dra. Larissa Pessoa sentada em uma poltrona clara"),
        ("02", "Veja o couro cabeludo ampliado", "A tricoscopia mostra inflamação, afinamento e densidade, com ampliação de até 200 vezes.", "tricoscopio-retrato", "Tricoscópio digital apoiado no couro cabeludo"),
        ("03", "Saia com um plano", "Em casa, no consultório ou nos dois. Os primeiros sinais costumam aparecer entre 60 e 120 dias.", "microinfusao", "Aplicação de ativos ao longo da risca do cabelo"),
    ]
    cards = "".join(
        f'<article class="passo" data-spotlight><span class="passo__num">{n}</span>'
        f'{moldura(img, alt, "(max-width: 900px) 84vw, 28vw")}'
        f"<h3>{t}</h3><p>{d}</p></article>"
        for n, t, d, img, alt in itens
    )
    return f"""
<section class="passos wrap" id="como" aria-labelledby="h-como">
  <div class="passos__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> COMO FUNCIONA</span>
    <h2 id="h-como" class="head" data-reveal>Descubra a causa da sua queda em 1 consulta</h2>
  </div>
  <div class="passos__lista">{cards}</div>
</section>"""


def escolha_unidade(id_="h-unidades"):
    cards = []
    for u in UNIDADES:
        cards.append(
            f'<article class="unidade" data-spotlight data-unidade="{e(u["nome"])}">'
            f'<span class="kicker"><span class="kicker__dot"></span> {u["coords"]}</span>'
            f'<h3>{u["nome"]}</h3>'
            f'<p>{u["rua"]}<br>{u["bairro"]}</p>'
            f'<p class="unidade__fone">WhatsApp {u["whats_texto"]}</p>'
            f'<a class="button button--gold" href="{wa(numero=u["whats"])}" data-unidade="{e(u["nome"])}">'
            f'<span>Agendar em {u["nome"]}</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>'
            f'<a class="link" href="{u["mapa"]}" rel="noopener">Como chegar &rarr;</a>'
            f"</article>"
        )
    return f"""
<section class="unidades wrap" id="unidades" aria-labelledby="{id_}">
  <div class="unidades__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> DUAS UNIDADES ABERTAS</span>
    <h2 id="{id_}" data-reveal>Escolha sua unidade</h2>
    <p data-reveal>O atendimento é com hora marcada. Cada botão abre o agendamento com a unidade já escolhida.</p>
  </div>
  <div class="unidades__lista">{''.join(cards)}</div>
</section>"""


FAQ_HOME = [
    ("A queda que eu vejo tem tratamento?", "Tem, quando o tratamento é dirigido à causa. A consulta começa pela investigação: história clínica, tricoscopia e, se necessário, exames."),
    ("Em quanto tempo aparece resultado?", "Os primeiros sinais costumam aparecer entre 60 e 120 dias, conforme a causa e o protocolo. A evolução é acompanhada nas reavaliações."),
    ("Vocês atendem em Copacabana e em Cabo Frio?", "Sim. As duas unidades estão abertas, com hora marcada. Copacabana fica na Av. Nossa Senhora de Copacabana, 807, sala 702. Cabo Frio fica na Av. Henrique Terra, 808, Novo Portinho."),
    ("Quanto custa a consulta?", "O valor é informado no agendamento, pelo WhatsApp."),
    ("Atendem homens e mulheres?", "Sim. A Hairzenith trata queda e calvície em mulheres e homens, sem cirurgia."),
]


def nomes(titulo, grupos, id_="h-nomes"):
    blocos = []
    for idx, g in enumerate(grupos):
        itens = "".join(f"<li>{x}</li>" for x in g)
        blocos.append(
            f'<div class="names__card" data-spotlight data-reveal style="--i:{idx}">'
            f'<span class="names__index">{ROMANOS[idx]}</span>'
            f'<ul class="names__group">{itens}</ul>'
            f'</div>'
        )
    return f"""
<section class="names" aria-labelledby="{id_}">
  <div class="wrap grid">
    <div class="names__head">
      <span class="kicker" data-reveal><span class="kicker__dot"></span> CREDENCIAIS &amp; RIGOR CIENTÍFICO</span>
      <h2 id="{id_}" data-reveal>{titulo}</h2>
    </div>
    <div class="names__cols">{''.join(blocos)}</div>
  </div>
</section>"""


def grupos_ciencia(com_tecnologias=True, com_publicacoes=True):
    arts = [f'<a href="{href_artigo(a)}" rel="noopener">{a["curto"]} &#8599;</a>' for a in ARTIGOS]
    grupos = [
        ["Equipe", '<a href="~/equipe/larissa-pessoa/">Dra. Larissa Pessoa, fundadora</a>', '<a href="~/equipe/#thaina">Thaina Candido de Souza</a>', '<a href="~/equipe/#julia">Júlia</a>'],
    ]
    if com_publicacoes:
        grupos.append(["Publicado em", "Brazilian Journal of Hair Health, 2025"] + arts)
        grupos.append(["Coautoria", "Lara Junqueira, Faculdade de Farmácia da UFRJ"])
    if com_tecnologias:
        grupos.append(["Tecnologias", "Tricoscopia digital", "Laser e LED capilar", "MMP", "Microinfusão de ativos", "Mesoject"])
    grupos.append(["Atendimento", "Mulheres e homens", "Copacabana, Rio de Janeiro", "Novo Portinho, Cabo Frio"])
    return grupos


def reunidas(titulo, texto, link, fotos, id_="h-reunidas"):
    itens = "".join(
        f'<li class="gather__item" data-spotlight>{moldura(img, alt, "(max-width: 900px) 45vw, 260px", attrs=f"data-open data-lightbox style=\"--i:{i}\"")}</li>'
        for i, (img, alt) in enumerate(fotos)
    )
    return f"""
<section class="gather wrap" aria-labelledby="{id_}">
  <div class="gather__card" data-spotlight>
    <div class="gather__head" data-reveal>
      <span class="kicker"><span class="kicker__dot"></span> ARQUITETURA &amp; EXPANSÃO • 2027</span>
      <h2 id="{id_}">{titulo}</h2>
      <p>{texto}</p>
      <div class="gather__cta">{link}</div>
    </div>
    <ul class="gather__pics">{itens}</ul>
  </div>
</section>"""


def phero(h1, lead, texto, alto, quadrado, acoes, id_="titulo"):
    linhas = h1 if isinstance(h1, list) else [h1]
    spans = "".join(f'<span class="line"><span data-line style="--i:{i}">{l}</span></span>' for i, l in enumerate(linhas))
    return f"""
<section class="phero wrap grid" aria-labelledby="{id_}">
  <div class="phero__main">
    <span class="kicker" data-load style="--d:120ms"><span class="kicker__dot"></span> HAIRZENITH • ALTA TRICOLOGIA</span>
    <h1 id="{id_}" class="lines">{spans}</h1>
    <div class="phero__text">
      <p class="lead" data-load style="--d:320ms">{lead}</p>
      {f'<p data-load style="--d:400ms">{texto}</p>' if texto else ''}
      <div class="actions" data-load style="--d:480ms">{acoes}</div>
    </div>
  </div>
  <div class="phero__visuals">
    <figure class="phero__tall">{moldura(alto[0], alto[1], "(max-width: 900px) 78vw, 34vw", attrs="data-shutter", prioridade=True)}</figure>
    <figure class="phero__small">{moldura(quadrado[0], quadrado[1], "(max-width: 900px) 45vw, 18vw", attrs="data-load style=\"--d:580ms\"")}</figure>
  </div>
</section>"""


def tabela_sinais(titulo, linhas, foto, id_="h-sinais"):
    h = titulo if isinstance(titulo, list) else [titulo]
    cab = f'<span class="indent">{h[0]}</span>' + (f" <em>{h[1]}</em>" if len(h) > 1 else "")
    rows = "".join(
        f'<div class="trow" data-spotlight data-reveal style="--i:{i}">'
        f'<span class="trow__idx">0{i + 1}</span>'
        f'<p class="trow__name">{a}</p>'
        f'<p class="trow__text">{b}</p></div>'
        for i, (a, b) in enumerate(linhas)
    )
    return f"""
<section class="signs signs--page wrap" aria-labelledby="{id_}">
  <div class="signs__header">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> SINAIS CLÍNICOS DE ALERTA</span>
    <h2 id="{id_}" class="head" data-reveal>{cab}</h2>
  </div>
  <div class="signs__body grid">
    <figure class="signs__map signs__pic">{moldura(foto[0], foto[1], "(max-width: 900px) 80vw, 34vw")}</figure>
    <div class="signs__table">{rows}</div>
  </div>
</section>"""


def definicoes(titulo, intro, itens, foto, id_="h-def"):
    dl = "".join(
        f'<div class="defs__card" data-spotlight data-reveal style="--i:{i % 2}">'
        f'<span class="defs__num">0{i + 1}</span>'
        f'<dt>{a}</dt><dd>{b}</dd></div>'
        for i, (a, b) in enumerate(itens)
    )
    return f"""
<section class="defs wrap grid" aria-labelledby="{id_}">
  <div class="defs__header">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> FUNDAMENTAÇÃO CLÍNICA</span>
    <h2 id="{id_}" data-reveal>{titulo}</h2>
    <p class="defs__intro" data-reveal style="--i:1">{intro}</p>
  </div>
  <dl class="defs__list">{dl}</dl>
  <figure class="defs__pic">{moldura(foto[0], foto[1], "(max-width: 900px) 70vw, 28vw")}</figure>
</section>"""


def dividida(titulo, foto, corpo, id_="h-div", inverte=False):
    cls = "split wrap grid split--flip" if inverte else "split wrap grid"
    figura = f'<figure class="split__fig">{moldura(foto[0], foto[1], "(max-width: 900px) 84vw, 34vw")}</figure>' if foto else ""
    return f"""
<section class="{cls}" aria-labelledby="{id_}">
  <div class="split__head"><span class="kicker" data-reveal><span class="kicker__dot"></span> ABORDAGEM TERAPÊUTICA</span><h2 id="{id_}" data-reveal>{titulo}</h2>{figura}</div>
  <div class="split__body" data-reveal style="--i:1">{corpo}</div>
</section>"""


def faixa(titulo, texto, foto, acoes, id_="h-faixa"):
    return f"""
<section class="band" aria-labelledby="{id_}">
  <div class="wrap grid">
    <div class="band__content">
      <span class="kicker kicker--gold" data-reveal><span class="kicker__dot"></span> DIAGNÓSTICO DE ALTA PRECISÃO</span>
      <h2 id="{id_}" data-reveal>{titulo}</h2>
      <div class="band__text" data-reveal style="--i:1">{texto}</div>
      <div class="actions" data-reveal style="--i:2">{acoes}</div>
    </div>
    <figure class="band__pic">{moldura(foto[0], foto[1], "(max-width: 900px) 84vw, 38vw")}</figure>
  </div>
</section>"""


def perguntas(titulo, itens, id_="h-faq"):
    det = "".join(
        f'<details data-spotlight><summary><span class="faq__q">{q}</span><span class="faq__icon" aria-hidden="true"></span></summary><div class="faq__ans"><p>{a}</p></div></details>'
        for q, a in itens
    )
    return f"""
<section class="faq wrap grid" aria-labelledby="{id_}">
  <div class="faq__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> DÚVIDAS FREQUENTES</span>
    <h2 id="{id_}" data-reveal>{titulo}</h2>
  </div>
  <div class="faq__list" data-reveal style="--i:1">{det}</div>
</section>"""


def indice(titulo, atual=None, id_="h-indice"):
    itens = []
    primeiro = None
    for idx, p in enumerate(PROBLEMAS):
        img = p["alto"][0]
        src = f"~/assets/img/{img}-p.jpg"
        primeiro = primeiro or (src, p["alto"][1])
        cur = ' aria-current="page"' if p["slug"] == atual else ""
        itens.append(
            f'<li><a href="~/{p["slug"]}/" data-src="{src}" data-alt="{e(p["alto"][1])}"{cur}>'
            f'<span class="index__num">0{idx + 1}</span>'
            f'<span class="index__name">{p["nome"]}</span>'
            f'<span class="index__where">{p["onde"]}</span>'
            f'<span class="index__arrow" aria-hidden="true">&rarr;</span></a></li>'
        )
    return f"""
<section class="index wrap grid" aria-labelledby="{id_}">
  <div class="index__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> ÍNDICE DE CONDIÇÕES CAPILARES</span>
    <h2 id="{id_}" data-reveal>{titulo}</h2>
  </div>
  <ul class="index__list" data-preview-list="#previa-{id_}">{''.join(itens)}</ul>
  <figure class="index__preview"><div class="frame"><img id="previa-{id_}" src="{primeiro[0]}" alt="{e(primeiro[1])}" width="760" height="950" loading="lazy" decoding="async"></div></figure>
</section>"""


# ---------------------------------------------------------------- dados estruturados
ORG_ID = SITE + "/#hairzenith"
LARISSA_ID = SITE + "/equipe/larissa-pessoa/#larissa"
THAINA_ID = SITE + "/equipe/#thaina"
JULIA_ID = SITE + "/equipe/#julia"


def endereco(u):
    """Junta a rua ao bairro quando o bairro ainda não está no logradouro.
    Novo Portinho, por exemplo, só aparece na segunda linha do rodapé."""
    rua = u["rua"]
    bairro = u["bairro"].split(",")[0].strip()
    if bairro and bairro.lower() not in rua.lower():
        rua = f"{rua}, {bairro}"
    dados = {
        "@type": "PostalAddress",
        "streetAddress": rua,
        "addressLocality": u["cidade"],
        "addressRegion": "RJ",
        "addressCountry": "BR",
    }
    if u.get("cep"):
        dados["postalCode"] = u["cep"]
    return dados


def schema_org():
    return {
        "@type": "MedicalClinic",
        "@id": ORG_ID,
        "name": "Hairzenith",
        "alternateName": ["Larissa Pessoa Tricologia Integrativa", "Dra. Larissa Pessoa Tricologia", "Clínica Larissa Pessoa"],
        "description": "Clínica de tricologia especializada em queda de cabelo, calvície e perda de densidade capilar, fundada pela Dra. Larissa Pessoa. Nova clínica em construção, com inauguração prevista para março de 2027.",
        "url": SITE + "/",
        "logo": SITE + "/icone-512.png",
        "image": SITE + "/assets/img/og-hairzenith.jpg",
        "telephone": telefone_internacional(),
        "email": EMAIL,
        "address": endereco(UNIDADES[0]),
        "areaServed": ["Rio de Janeiro", "Cabo Frio", "Região dos Lagos"],
        "founder": {"@id": LARISSA_ID},
        "employee": [{"@id": LARISSA_ID}, {"@id": THAINA_ID}, {"@id": JULIA_ID}],
        "knowsAbout": ["Tricologia", "Queda de cabelo", "Calvície feminina", "Calvície masculina", "Alopecia androgenética", "Afinamento dos fios", "Perda de densidade capilar", "Tricoscopia"],
        "sameAs": [INSTAGRAM, SITE_ANTIGO, AVALIACOES["place"]["url"]],
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": AVALIACOES["place"]["rating"],
            "reviewCount": AVALIACOES["place"]["review_count"],
            "bestRating": 5,
        },
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "telephone": telefone_internacional(u["whats"]),
                "email": EMAIL,
                "contactType": "customer service",
                "availableLanguage": ["Portuguese"],
                "areaServed": "BR",
                "url": f"https://wa.me/{u['whats']}",
            }
            for u in UNIDADES
        ],
        "department": [{"@id": f"{SITE}/#{u['id']}"} for u in UNIDADES],
    }


def schema_unidades():
    """Uma ficha por endereço, com o WhatsApp da própria unidade.
    Sem CRM, CEP ou horário: esses dados não estão no projeto."""
    nos = []
    for u in UNIDADES:
        nos.append({
            "@type": ["MedicalClinic", "LocalBusiness"],
            "@id": f"{SITE}/#{u['id']}",
            "name": f"Hairzenith {u['nome']}",
            "parentOrganization": {"@id": ORG_ID},
            "url": f"{SITE}/#{u['id']}",
            "image": f"{SITE}/assets/img/og-hairzenith.jpg",
            "telephone": telefone_internacional(u["whats"]),
            "email": EMAIL,
            "address": endereco(u),
            "geo": {"@type": "GeoCoordinates", "latitude": u["lat"], "longitude": u["lon"]},
            "hasMap": u["mapa"],
        })
    return nos


def schema_larissa():
    return {
        "@type": "Person",
        "@id": LARISSA_ID,
        "name": "Larissa Pessoa",
        "honorificPrefix": "Dra.",
        "alternateName": ["Dra. Larissa Pessoa", "Larissa Mota Barros Pessoa"],
        "jobTitle": "Fundadora, CEO e tricologista",
        "description": "Tricologista especializada em queda de cabelo e calvície, fundadora e CEO da Hairzenith.",
        "worksFor": {"@id": ORG_ID},
        "url": SITE + "/equipe/larissa-pessoa/",
        "image": SITE + "/assets/img/larissa-blazer.jpg",
        "knowsAbout": ["Tricologia", "Alopecia androgenética", "Queda de cabelo", "Calvície"],
        "sameAs": [INSTAGRAM, SITE_ANTIGO],
    }


def schema_artigos():
    return [
        {
            "@type": "ScholarlyArticle",
            "headline": a["titulo"],
            "datePublished": a["data"],
            "url": a["url"],
            **({"sameAs": "https://doi.org/" + a["doi"]} if a["doi"].endswith("bjhh22") else {}),
            "isPartOf": {"@type": "Periodical", "name": "Brazilian Journal of Hair Health"},
            "author": [
                {"@id": LARISSA_ID} if "Larissa" in n else ({"@id": THAINA_ID} if "Thaina" in n else {"@type": "Person", "name": n})
                for n in a["autores"]
            ],
        }
        for a in ARTIGOS
    ]


def migalhas(itens):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(itens)],
    }


# ---------------------------------------------------------------- montagem
PAGINAS = []


FONTES = (
    "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,400"
    "&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap"
)


def imagem_social(nome):
    """Card 1,91:1. Retrato e faixas estreitas são recortados mal no WhatsApp e no X."""
    g = MANIFESTO.get(nome, {}).get("g")
    if g and 1.7 <= (g[0] / g[1]) <= 2.1:
        return nome, g[0], g[1]
    g = MANIFESTO["og-hairzenith"]["g"]
    return "og-hairzenith", g[0], g[1]


def rastreamento():
    """Só entra no HTML com ID no formato da plataforma. Sem ID, não há tag placeholder."""
    if getattr(rastreamento, "pronto", None) is not None:
        return rastreamento.pronto
    if GTM_ID and not re.fullmatch(r"GTM-[A-Z0-9]+", GTM_ID):
        print(f"aviso: GTM_ID ignorado ({GTM_ID!r})")
    if GA_MEASUREMENT_ID and not re.fullmatch(r"G-[A-Z0-9]+", GA_MEASUREMENT_ID):
        print(f"aviso: GA_MEASUREMENT_ID ignorado ({GA_MEASUREMENT_ID!r})")
    if META_PIXEL_ID and not re.fullmatch(r"\d{8,20}", META_PIXEL_ID):
        print(f"aviso: META_PIXEL_ID ignorado ({META_PIXEL_ID!r})")

    blocos = []
    gtm_ok = bool(re.fullmatch(r"GTM-[A-Z0-9]+", GTM_ID))
    ga_ok = bool(re.fullmatch(r"G-[A-Z0-9]+", GA_MEASUREMENT_ID))
    pixel_ok = bool(re.fullmatch(r"\d{8,20}", META_PIXEL_ID))
    if gtm_ok and (ga_ok or pixel_ok):
        print("aviso: GTM_ID está definido, então GA4 e Pixel não entram no HTML. Configure os dois dentro do Tag Manager.")
        ga_ok = False
        pixel_ok = False
    if gtm_ok:
        blocos.append(
            "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src="
            "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);"
            f"}})(window,document,'script','dataLayer','{GTM_ID}');</script>"
        )
    elif ga_ok:
        blocos.append(
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>\n'
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
            f"gtag('js',new Date());gtag('config','{GA_MEASUREMENT_ID}');</script>"
        )
    if pixel_ok:
        blocos.append(
            "<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?"
            "n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;"
            "n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;"
            "t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,"
            "'script','https://connect.facebook.net/en_US/fbevents.js');"
            f"fbq('init','{META_PIXEL_ID}');fbq('track','PageView');</script>\n"
            f'<noscript><img height="1" width="1" alt="" src="https://www.facebook.com/tr?id={META_PIXEL_ID}&ev=PageView&noscript=1"></noscript>'
        )
    rastreamento.pronto = "\n".join(blocos)
    return rastreamento.pronto


def gtm_noscript():
    """Iframe do GTM, logo após o <body>, para quem está sem JavaScript."""
    if not re.fullmatch(r"GTM-[A-Z0-9]+", GTM_ID):
        return ""
    return (
        f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}" '
        f'height="0" width="0" style="display:none;visibility:hidden" title="Google Tag Manager"></iframe></noscript>'
    )


def _ghl_src_valido(src):
    partes = urlparse(src)
    return partes.scheme == "https" and bool(partes.netloc) and partes.path.endswith("/js/external-tracking.js")


def _ghl_id_valido(tid):
    return bool(re.fullmatch(r"tk_[A-Za-z0-9]{8,64}", tid))


def _extrair_script_ghl(bruto):
    """Aceita o <script> inteiro, só a URL do src, ou só o data-tracking-id."""
    src = re.search(r"""src=["']([^"']+)["']""", bruto)
    tid = re.search(r"""data-tracking-id=["']([^"']+)["']""", bruto)
    if src and tid:
        return src.group(1).strip(), tid.group(1).strip()
    if bruto.startswith("https://") and " " not in bruto:
        return bruto, ""
    if re.fullmatch(r"tk_[A-Za-z0-9]{8,64}", bruto):
        return "", bruto
    return None


def resolver_rastreio_ghl():
    """Padrão do repositório, sobrescrito por variável de ambiente na hora do build."""
    if getattr(resolver_rastreio_ghl, "pronto", None):
        return resolver_rastreio_ghl.pronto
    src = os.environ.get("GHL_TRACKING_SRC", "").strip()
    tid = os.environ.get("GHL_TRACKING_ID", "").strip()
    bruto = os.environ.get("GHL_TRACKING_SCRIPT", "").strip()
    if bruto:
        extraido = _extrair_script_ghl(bruto)
        if not extraido:
            print("aviso: GHL_TRACKING_SCRIPT inválido; usando o padrão do GHL")
        else:
            src = extraido[0] or src
            tid = extraido[1] or tid
    src = src or GHL_TRACKING_SRC
    tid = tid or GHL_TRACKING_ID
    if not (_ghl_src_valido(src) and _ghl_id_valido(tid)):
        print(f"aviso: rastreio GHL inválido ({src!r}, {tid!r}); usando o padrão")
        src, tid = GHL_TRACKING_SRC, GHL_TRACKING_ID
    resolver_rastreio_ghl.pronto = (src, tid)
    return resolver_rastreio_ghl.pronto


def script_ghl():
    """External Tracking no fim do body. async para não segurar o site.js."""
    src, tid = resolver_rastreio_ghl()
    return (
        f'<script src="{e(src)}" data-tracking-id="{e(tid)}" async '
        "onload=\"this.dataset.hzEstado='ok'\" "
        "onerror=\"this.dataset.hzEstado='erro'\"></script>"
    )


def boot_lead():
    """Registra o submit antes do script do GHL, para o first-touch entrar no form."""
    return """<script>
window.addEventListener('submit', function (e) {
  var form = e.target;
  if (!form || form.nodeName !== 'FORM') return;
  if (form.id === 'lead-form' && window.HairzenithLead) {
    window.HairzenithLead.aoEnviar(e);
    return;
  }
  if (form.hasAttribute('data-composer')) {
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    if (window.registrarWhatsapp) window.registrarWhatsapp();
    var destino = form.querySelector('[data-send]');
    if (window.HairzenithLead && destino) window.HairzenithLead.abrir(destino);
  }
}, true);
</script>"""


def formulario_lead():
    """Formulário real no DOM. O modal só esconde; o GHL não lê iframe."""
    # type=hidden é descartado pelo external-tracking.js. O campo fica fora da tela, visível para o script.
    ocultos = "".join(
        f'<input class="lead-modal__partes" type="text" name="{nome}" tabindex="-1" autocomplete="off" aria-hidden="true" value="">'
        for nome in (
            "gclid", "gbraid", "wbraid",
            "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
            "origem", "pagina_origem", "landing_page",
        )
    )
    return f"""
<div class="lead-modal" id="lead-modal" hidden>
  <div class="lead-modal__card" role="dialog" aria-modal="true" aria-labelledby="lead-titulo" aria-describedby="lead-confianca">
    <button type="button" class="lead-modal__fechar" data-lead-fechar>Fechar</button>
    <p class="kicker"><span class="kicker__dot"></span> Agendamento</p>
    <h2 id="lead-titulo">Agende sua avaliação — respondemos rapidinho no WhatsApp</h2>
    <p id="lead-confianca" class="lead-modal__confianca">Seus dados são usados só para o agendamento.</p>
    <form id="lead-form" name="agendamento-whatsapp" method="post" action="#lead-form" novalidate>
      <div class="lead-modal__campo">
        <label for="lead-nome">Nome</label>
        <input id="lead-nome" name="full_name" type="text" autocomplete="name" required maxlength="80" aria-required="true">
      </div>
      <input class="lead-modal__partes" name="first_name" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" value="">
      <input class="lead-modal__partes" name="last_name" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" value="">
      <div class="lead-modal__campo">
        <label for="lead-phone">Telefone</label>
        <input id="lead-phone" name="phone" type="tel" inputmode="numeric" autocomplete="tel" required aria-required="true" placeholder="(21) 90000-0000">
      </div>
      <fieldset class="lead-modal__campo">
        <legend>Qual unidade?</legend>
        <div class="choices" role="radiogroup" aria-label="Qual unidade?">
          <label><input type="radio" name="unidade" value="Cabo Frio"><span>Cabo Frio</span></label>
          <label><input type="radio" name="unidade" value="Copacabana"><span>Copacabana (Rio)</span></label>
        </div>
      </fieldset>
      {ocultos}
      <p class="lead-modal__alerta" id="lead-alerta" role="alert" hidden></p>
      <button class="button button--gold" type="submit"><span>Continuar no WhatsApp</span><span class="button__arrow" aria-hidden="true">&rarr;</span></button>
    </form>
  </div>
</div>"""


def pagina(caminho, titulo, descricao, corpo, ativo=None, schema=None, imagem="og-hairzenith", tipo="website", indexar=True):
    grafo = [schema_org(), *schema_unidades()] + (schema or [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, separators=(",", ":"))
    url = SITE + caminho
    social, largura, altura = imagem_social(imagem)
    social_url = f"{SITE}/assets/img/{social}.jpg"
    social_alt = "Dra. Larissa Pessoa, fundadora da Hairzenith, clínica de tricologia em Copacabana e Cabo Frio"
    opcionais = []
    if indexar:
        opcionais.append(f'<link rel="canonical" href="{url}">')
        opcionais.append(f'<meta property="og:url" content="{url}">')
    else:
        opcionais.append('<meta name="robots" content="noindex, follow">')
    rastreio = rastreamento()
    if rastreio:
        opcionais.append(rastreio)
    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
{chr(10).join(opcionais)}
<meta property="og:type" content="{tipo}">
<meta property="og:site_name" content="{MARCA}">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:image" content="{social_url}">
<meta property="og:image:width" content="{largura}">
<meta property="og:image:height" content="{altura}">
<meta property="og:image:alt" content="{e(social_alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titulo)}">
<meta name="twitter:description" content="{e(descricao)}">
<meta name="twitter:image" content="{social_url}">
<meta name="twitter:image:alt" content="{e(social_alt)}">
<meta name="theme-color" content="#120F0D">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTES}">
<link rel="stylesheet" href="/assets/css/site.css">
<script>document.documentElement.classList.add('js')</script>
<script type="application/ld+json">{ld}</script>
</head>
<body>
{gtm_noscript()}
{cabecalho(ativo)}
<main id="conteudo">
{corpo}
</main>
{rodape()}
{formulario_lead()}
{boot_lead()}
{script_ghl()}
<script src="/assets/js/lead.js" defer></script>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""
    doc = abrir_whatsapp(doc.replace("~/", "/"))
    destino = SAIDA / "index.html" if caminho == "/" else SAIDA / caminho.strip("/") / "index.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(doc, encoding="utf-8")
    PAGINAS.append(caminho)


# ---------------------------------------------------------------- páginas
def home():
    linhas = "".join(
        f'<a class="row" data-spotlight href="~/{p["slug"]}/" data-zone="{p["slug"]}" data-name="{p["nome"]}" data-text="{e(p["zona"])}">'
        f'<span class="row__idx">0{idx + 1}</span>'
        f'<span class="row__main"><span class="row__name">{p["nome"]}</span><span class="row__kind">{p["onde"]}</span></span>'
        f'<span class="row__go">Explorar <span class="arrow" aria-hidden="true">&rarr;</span></span></a>'
        for idx, p in enumerate(PROBLEMAS)
    )
    fatos = [("Fundadora", "Dra. Larissa Pessoa"), ("Especialidade", "Queda e calvície"), ("Atendimento", "Copacabana e Cabo Frio"), ("Nova clínica", "Março de 2027")]
    dl = "".join(f"<div class=\"mosaic__fact-card\" data-spotlight><dt>{a}</dt><dd>{b}</dd></div>" for a, b in fatos)
    corpo = f"""
<section class="hero wrap" aria-labelledby="titulo">
  <div class="hero__grid grid">
    <div class="hero__copy">
      <span class="kicker" data-load style="--d:100ms"><span class="kicker__dot"></span> CLÍNICA DE ALTA TRICOLOGIA • RIO DE JANEIRO &amp; CABO FRIO</span>
      <h1 id="titulo" class="lines">
        <span class="line"><span data-line style="--i:0">Especialistas em</span></span>
        <span class="line"><span data-line style="--i:1"><em>queda e calvície</em></span></span>
      </h1>
      <p class="hero__lead" data-load style="--d:320ms">A Hairzenith é a clínica de tricologia fundada pela Dra. Larissa Pessoa para tratar queda, calvície e perda de densidade capilar.</p>
      <p class="hero__sub" data-load style="--d:400ms">Na consulta, a tricoscopia mostra a causa. O plano pode ser em casa, no consultório ou nos dois.</p>
      <div class="actions" data-load style="--d:480ms">
        <a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>
      </div>
      <dl class="hero__metrics" data-load style="--d:560ms">
        <div><dt>Diagnóstico</dt><dd>Tricoscopia 200&times;</dd></div>
        <div><dt>Unidades</dt><dd>Copacabana &amp; Cabo Frio</dd></div>
      </dl>
    </div>
    <div class="hero__stage">
      <figure class="hero__tall">
        {moldura("larissa-poltrona", "Dra. Larissa Pessoa, de terno claro, sentada em uma poltrona", "(max-width: 900px) 84vw, 34vw", attrs="data-shutter", prioridade=True)}
        <figcaption>Dra. Larissa Pessoa, fundadora e CEO da Hairzenith</figcaption>
      </figure>
      <figure class="hero__square" data-load style="--d:260ms">
        {moldura("tricoscopio", "Tricoscópio digital apoiado no couro cabeludo de uma paciente", "(max-width: 900px) 45vw, 14vw", attrs="")}
        <div class="hero__float-caption">
          <span class="hero__float-tag">PRECISÃO ÓPTICA</span>
          <p>Análise folicular ampliada em até 200 vezes</p>
        </div>
      </figure>
      <div class="hero__wide" data-load style="--d:620ms">
        <figure class="hero__wide-pic">
          {moldura("mesoject", "Caneta do Mesoject aplicada sobre o couro cabeludo de uma paciente", "(max-width: 900px) 100vw, 22vw", attrs="")}
          <figcaption>Mesoject: ativos no couro cabeludo, sem agulhas</figcaption>
        </figure>
        <a class="hero__note" href="#como">
          <span class="hero__note-kicker">PRIMEIRA CONSULTA</span>
          <span class="hero__days">1</span>
          <span class="hero__unit">consulta para a causa</span>
          <span class="link">Como funciona &rarr;</span>
        </a>
      </div>
    </div>
  </div>
</section>

<section class="pano" aria-labelledby="h-zenite">
  <div class="wrap">
    <div class="pano__header grid">
      <div class="pano__title-col">
        <span class="kicker kicker--gold" data-reveal><span class="kicker__dot"></span> TRICOSCOPIA NA CONSULTA</span>
        <h2 id="h-zenite" class="display" data-reveal>Veja a causa com ampliação de até <em>200 vezes</em></h2>
      </div>
      <div class="pano__captions">
        <p data-reveal style="--i:1">Hairzenith vem de zênite, o ponto mais alto. É de cima que a tricologia examina o couro cabeludo: a risca, a coroa e a densidade de uma só vez.</p>
        <p data-reveal style="--i:2">Toda consulta começa assim, com tricoscopia digital que amplia os fios em até 200 vezes.</p>
      </div>
    </div>
    <figure class="pano__image" data-open data-lightbox>
      <div class="pano__hud" aria-hidden="true"><span>TRICOSCOPIA DIGITAL • 200&times;</span><span>MAPEAMENTO FOLICULAR NÃO INVASIVO</span></div>
      {pic("tela-tricoscopia", "Fios do couro cabeludo ampliados na tela durante uma tricoscopia", "100vw")}
    </figure>
  </div>
</section>

<section class="signs wrap" aria-labelledby="h-sinais">
  <div class="signs__header">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> SEIS SINAIS, SEIS PÁGINAS</span>
    <h2 id="h-sinais" class="head" data-reveal><span class="indent">Encontre o tratamento</span> <em>pelo que você vê</em></h2>
  </div>
  <div class="signs__body grid">
    <div class="signs__map zmap" data-on="calvicie-masculina" data-reveal data-spotlight>
      <div class="zmap__topbar"><span>VISTA DE CIMA</span><span>SELECIONE UMA REGIÃO</span></div>
      {mapa_zenite()}
      <p class="zmap__caption" aria-live="polite">Passe o cursor pela lista ou toque no desenho para ver onde cada sinal aparece.</p>
    </div>
    <div class="signs__right">
      <p class="signs__label">06 QUADROS CLÍNICOS PRINCIPAIS</p>
      <div class="signs__table">{linhas}</div>
      <div class="signs__foot"><p>Cada sinal tem uma página com causas, exames e tratamentos. <a class="link" href="~/tratamentos/">Todos os tratamentos &rarr;</a></p></div>
    </div>
  </div>
</section>

<section class="mosaic wrap" aria-labelledby="h-nasce">
  <div class="grid">
    <div class="mosaic__header">
      <span class="kicker" data-reveal><span class="kicker__dot"></span> A CLÍNICA</span>
      <h2 id="h-nasce" class="head" data-reveal>Uma clínica só para queda e calvície</h2>
      <p class="mosaic__lead lead" data-reveal>Depois de anos atendendo pacientes com queda e calvície, a Dra. Larissa Pessoa decidiu transformar sua experiência em uma clínica especializada, com equipe, método e estrutura dedicados à saúde capilar.</p>
    </div>
    <figure class="mosaic__photo">
      {moldura("larissa-rosa", "Dra. Larissa Pessoa de vestido rosé em uma sala clara", "(max-width: 900px) 100vw, 58vw")}
      <div class="mosaic__paper" data-spotlight>
        <span class="kicker"><span class="kicker__dot"></span> EMPATIA CLÍNICA</span>
        <p>A Dra. Larissa Pessoa já passou pela queda de cabelo e conhece o impacto dela na autoestima. Essa experiência orienta o jeito como cada paciente é recebido. <a class="link" href="~/sobre/">A história da marca &rarr;</a></p>
      </div>
    </figure>
    <div class="mosaic__side" data-reveal style="--i:2">
      <div class="mosaic__tile" data-spotlight>
        <div class="mosaic__tile-bar"><span>COPACABANA • CABO FRIO</span><span>02 UNIDADES ATIVAS</span></div>
        {mapa_litoral()}
      </div>
      <dl class="mosaic__facts">{dl}</dl>
    </div>
  </div>
</section>

{nomes("Quem atende", grupos_ciencia(False, False), "h-ciencia")}

{reunidas("A nova clínica chega em março de 2027", "Enquanto a obra avança, a equipe segue atendendo em Copacabana e Cabo Frio.", '<a class="button button--gold" href="~/nova-clinica/"><span>Acompanhe a obra</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>', [
        ("microinfusao", "Aplicação de ativos ao longo da risca do cabelo"),
        ("tela-tricoscopia-retrato", "Fios ampliados na tela da tricoscopia"),
        ("laser-led", "Capacete de laser e LED sobre a cabeça de uma paciente"),
        ("tricoscopio-retrato", "Tricoscópio apoiado no couro cabeludo"),
        ("larissa-sentada", "Dra. Larissa Pessoa sentada em uma poltrona clara"),
        ("mesoject-retrato", "Caneta do Mesoject sobre o couro cabeludo"),
    ])}
"""
    corpo = (
        corpo.split('<section class="pano"', 1)[0]
        + faixa_google()
        + resultados()
        + secao_depoimentos()
        + passos()
        + escolha_unidade()
        + perguntas("Dúvidas antes de agendar", FAQ_HOME)
        + fecho("A equipe responde no WhatsApp com os horários.", "Agende sua avaliação em Copacabana ou Cabo Frio", comparar=False)
        + '<section class="pano"'
        + corpo.split('<section class="pano"', 1)[1]
    )
    schema = [
        {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Hairzenith", "alternateName": "Larissa Pessoa Tricologia", "inLanguage": "pt-BR", "publisher": {"@id": ORG_ID}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_HOME]},
        schema_larissa(),
    ]
    pagina("/", "Tricologista em Copacabana e Cabo Frio | Hairzenith",
           "Clínica de tricologia da Dra. Larissa Pessoa em Copacabana, no Rio de Janeiro, e em Cabo Frio. Avaliação da queda, da calvície e da perda de densidade, com tricoscopia.",
           corpo, schema=schema)


def problema(p):
    trat = "".join(f'<div class="treat-step" data-spotlight><h3>{a}</h3><p>{b}</p></div>' for a, b in p["tratamentos"])
    if p["slug"] == "calvicie-feminina":
        trat += f'<p class="treat-study"><a class="link" href="{href_artigo(ARTIGOS[1])}" rel="noopener">Ler o estudo de caso publicado no Brazilian Journal of Hair Health &rarr;</a></p>'
    acoes = f'<a class="button button--shimmer" href="{wa(MSG_PADRAO)}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="#h-faq">Perguntas frequentes</a>'
    corpo = (
        phero(p["nome"], p["lead"], None, p["alto"], p["quadrado"], acoes)
        + faixa_google()
        + secao_depoimentos(2, "h-depoimentos", "Quem já tratou conta no Google")
        + resultados(p["casos"], "h-casos", "Antes e depois, sem cirurgia")
        + tabela_sinais(["Quando procurar", "uma avaliação"], p["sinais"], p["lateral"])
        + definicoes("Por que acontece", "A mesma aparência pode ter causas diferentes, e cada causa pede um tratamento. Estas são as mais comuns.", p["causas"], p["causas_pic"])
        + dividida("Como tratamos", p["trat_pic"], f"<p class=\"lead\">O plano parte do diagnóstico, nunca de um pacote pronto. Os tratamentos da Hairzenith são clínicos e sem cirurgia.</p><div class=\"treat-grid\">{trat}</div>", "h-trat")
        + faixa(
            "Tudo começa pela tricoscopia",
            "<p>Na consulta, o couro cabeludo é examinado com ampliação de até 200 vezes. Com a história clínica e, se necessário, exames, a tricologista define a causa e monta o plano: em casa, no consultório ou nos dois.</p>"
            "<p>O atendimento pode ser com a equipe Hairzenith ou com a Dra. Larissa Pessoa, fundadora da clínica.</p>",
            ("tela-tricoscopia-retrato", "Imagem ampliada dos fios na tela durante a tricoscopia"),
            f'<a class="button button--gold" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/consulta/">Como é a consulta &rarr;</a>',
        )
        + perguntas("Perguntas frequentes", p["faq"])
        + indice("Outros sinais", p["slug"])
        + fecho(f"{p['nome']} tem tratamento. Comece pela causa.", "Pronto para a avaliação?")
    )
    nome_cond, alternativos = p["condicao"]
    schema = [
        {
            "@type": "MedicalWebPage",
            "@id": SITE + f"/{p['slug']}/#pagina",
            "url": SITE + f"/{p['slug']}/",
            "name": p["titulo"],
            "inLanguage": "pt-BR",
            "lastReviewed": ATUALIZADO,
            "reviewedBy": {"@id": LARISSA_ID},
            "publisher": {"@id": ORG_ID},
            "about": {
                "@type": "MedicalCondition",
                "name": nome_cond,
                "alternateName": alternativos,
                "signOrSymptom": [{"@type": "MedicalSignOrSymptom", "name": a} for a, _ in p["sinais"]],
                "possibleTreatment": [{"@type": "MedicalTherapy", "name": a} for a, _ in p["tratamentos"]],
            },
        },
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
        migalhas([("Hairzenith", "/"), ("Tratamentos", "/tratamentos/"), (p["nome"], f"/{p['slug']}/")]),
        schema_larissa(),
    ]
    pagina(f"/{p['slug']}/", p["titulo"], p["descricao"], corpo, ativo="tratamentos", schema=schema)


def tratamentos():
    acoes = f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/consulta/">Como é a consulta &rarr;</a>'
    corpo = (
        phero(["Tratamentos para", "queda e calvície"], "Cada tratamento começa por um diagnóstico. Escolha o que você está percebendo para entender as causas, os sinais e como tratamos.", None,
              ("mesoject-retrato", "Caneta do Mesoject aplicada sobre o couro cabeludo"), ("tricoscopio", "Tricoscópio digital apoiado no couro cabeludo"), acoes)
        + indice("O que você está percebendo", None, "h-problemas")
        + definicoes("Tecnologias", "Equipamentos e protocolos escolhidos para tratar a causa, sem cirurgia. O plano combina o que o seu caso pede.", TECNOLOGIAS, ("laser-led", "Capacete de laser e LED posicionado sobre a cabeça de uma paciente"), "h-tecnologias")
        + faixa(
            "Seu cabelo, sem cirurgia",
            "<p>Os tratamentos da Hairzenith são clínicos: recuperam e preservam o seu próprio cabelo, sem cirurgia. Em casa, no consultório ou nos dois, com acompanhamento a cada etapa.</p>"
            "<p>Em casos muito avançados, a avaliação indica com franqueza se o transplante deve ser considerado.</p>",
            ("microinfusao", "Aplicação de ativos ao longo da risca do cabelo"),
            f'<a class="button button--gold" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>',
            "h-sem-cirurgia",
        )
        + momentos()
        + fecho("Não sabe por onde começar? A consulta existe para isso.", "Vamos descobrir a causa?")
    )
    schema = [
        {"@type": "MedicalWebPage", "url": SITE + "/tratamentos/", "name": "Tratamentos para queda e calvície", "inLanguage": "pt-BR", "publisher": {"@id": ORG_ID},
         "hasPart": [{"@type": "MedicalWebPage", "url": SITE + f"/{p['slug']}/", "name": p["nome"]} for p in PROBLEMAS]},
        {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["nome"], "url": SITE + f"/{p['slug']}/"} for i, p in enumerate(PROBLEMAS)]},
        migalhas([("Hairzenith", "/"), ("Tratamentos", "/tratamentos/")]),
        schema_larissa(),
    ]
    pagina("/tratamentos/", "Tratamentos de tricologia em Copacabana e Cabo Frio | Hairzenith",
           "Tratamentos sem cirurgia para queda, calvície, couro cabeludo aparente e afinamento. Hairzenith em Copacabana e Cabo Frio, com tricoscopia na consulta.",
           corpo, ativo="tratamentos", schema=schema)


ALTS_RETRATO = {
    "thaina": "Thaina Candido de Souza, tricologista da Hairzenith, de blazer preto em retrato de rosto",
    "julia": "Júlia, tricologista da Hairzenith, de blusa branca e calça vermelha, sentada num banquinho",
}


def membro(id_, nome, texto, itens, i):
    """Uma tricologista da equipe. Quando houver retrato em MANIFESTO com o mesmo id, ele entra no topo."""
    alt = ALTS_RETRATO.get(id_, f"Retrato de {nome}")
    retrato = moldura(id_, alt, "(max-width: 900px) 100vw, 40vw") if id_ in MANIFESTO else ""
    iniciais = "".join(p[0] for p in nome.split()[:2]).upper()
    monograma = "" if retrato else f'<div class="member__monogram" aria-hidden="true"><span>{iniciais}</span></div>'
    lista = "".join(f"<li>{x}</li>" for x in itens)
    return (
        f'<article class="member" id="{id_}" data-spotlight data-reveal style="--i:{i}">{retrato}{monograma}'
        f'<span class="kicker"><span class="kicker__dot"></span> CORPO CLÍNICO HAIRZENITH</span>'
        f'<h3>{nome}</h3>'
        f'<p class="member__role">Tricologista Hairzenith</p><p>{texto}</p><ul class="member__list">{lista}</ul></article>'
    )


def equipe():
    acoes = f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/consulta/">As duas consultas &rarr;</a>'
    corpo = (
        phero("Equipe Hairzenith", "Três tricologistas, um mesmo método. A Hairzenith nasce como clínica, com equipe própria e uma fundadora presente.", None,
              ("larissa-blazer", "Dra. Larissa Pessoa de blazer branco, com a mão no rosto"), ("tricoscopio", "Tricoscópio digital apoiado no couro cabeludo"), acoes)
        + f"""
<section class="founder wrap grid" aria-labelledby="h-larissa" id="larissa">
  <figure class="founder__pic">{moldura("larissa-poltrona", "Dra. Larissa Pessoa sentada em uma poltrona clara", "(max-width: 900px) 100vw, 40vw")}</figure>
  <div class="founder__text" data-reveal>
    <span class="kicker"><span class="kicker__dot"></span> DIREÇÃO CLÍNICA &amp; FUNDAÇÃO</span>
    <h2 id="h-larissa">Dra. Larissa Pessoa</h2>
    <p class="founder__role">Fundadora e CEO da Hairzenith. Tricologista.</p>
    <p>A Dra. Larissa Pessoa construiu sua trajetória no tratamento da queda de cabelo e da calvície, primeiro com a clínica que levava o seu nome, Larissa Pessoa Tricologia Integrativa, em Copacabana e Cabo Frio. Hoje dirige a Hairzenith e segue atendendo pacientes.</p>
    <p>É autora, com a equipe, de dois estudos de caso sobre alopecia androgenética publicados no Brazilian Journal of Hair Health.</p>
    <div class="actions"><a class="button button--shimmer" href="{wa(MSG_LARISSA)}"><span>Agendar Consulta Signature</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/equipe/larissa-pessoa/">A trajetória da Dra. Larissa Pessoa &rarr;</a></div>
  </div>
</section>

<section class="pair wrap grid" aria-labelledby="h-tricologistas">
  <div class="pair__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> ESPECIALISTAS</span>
    <h2 id="h-tricologistas" data-reveal>Tricologistas Hairzenith</h2>
  </div>
  {membro("thaina", "Thaina Candido de Souza", "Coautora, com a Dra. Larissa Pessoa, dos dois estudos de caso sobre alopecia androgenética publicados pela clínica em 2025. Conduz a Consulta Expert para pacientes com queda, calvície e perda de densidade.", ["Consulta Expert", "Estudos publicados no Brazilian Journal of Hair Health"], 0)}
  {membro("julia", "Júlia Macedo", "Conduz a Consulta Expert com o protocolo completo da clínica: história clínica, tricoscopia, exames quando necessários e um plano de tratamento acompanhado de perto.", ["Consulta Expert", "Queda, calvície e perda de densidade"], 1)}
</section>
"""
        + dividida(
            "Um método, três profissionais",
            ("tela-tricoscopia-retrato", "Imagem ampliada dos fios na tela durante a tricoscopia"),
            "<p class=\"lead\">Na Hairzenith, a consulta não depende de quem está na agenda. O método é o mesmo para todas as tricologistas.</p>"
            "<div class=\"treat-grid\">"
            "<div class=\"treat-step\" data-spotlight><h3>A mesma avaliação</h3><p>História clínica, tricoscopia com ampliação de até 200 vezes e exames complementares quando a causa pede investigação.</p></div>"
            "<div class=\"treat-step\" data-spotlight><h3>Os mesmos protocolos</h3><p>Planos de tratamento construídos a partir da experiência clínica da Dra. Larissa Pessoa e revisados em equipe nos casos mais complexos.</p></div>"
            "<div class=\"treat-step\" data-spotlight><h3>O mesmo acompanhamento</h3><p>Reavaliações com fotos padronizadas, para comparar a evolução e ajustar o plano a cada etapa.</p></div>"
            "</div>",
            "h-metodo",
        )
        + nomes("Publicações", [["Brazilian Journal of Hair Health, 2025"] + [f'<a href="{href_artigo(a)}" rel="noopener">{a["curto"]} &#8599;</a>' for a in ARTIGOS],
                                 ["Autoras", "Larissa Mota Barros Pessoa", "Thaina Candido de Souza", "Lara Junqueira, UFRJ"]], "h-publicacoes")
        + fecho("Consulta Expert ou Consulta Signature: o método é o mesmo.", "Com quem você quer ser atendido?")
    )
    schema = [
        schema_larissa(),
        {"@type": "Person", "@id": THAINA_ID, "name": "Thaina Candido de Souza", "jobTitle": "Tricologista", "worksFor": {"@id": ORG_ID}, "url": SITE + "/equipe/#thaina", "image": SITE + "/assets/img/thaina.jpg"},
        {"@type": "Person", "@id": JULIA_ID, "name": "Júlia", "jobTitle": "Tricologista", "worksFor": {"@id": ORG_ID}, "url": SITE + "/equipe/#julia", "image": SITE + "/assets/img/julia.jpg"},
        migalhas([("Hairzenith", "/"), ("Equipe", "/equipe/")]),
    ] + schema_artigos()
    pagina("/equipe/", "Equipe de tricologia em Copacabana e Cabo Frio | Hairzenith",
           "Dra. Larissa Pessoa, Dra. Thaina Candido de Souza e Dra. Júlia Macedo atendem queda e calvície na Hairzenith, em Copacabana e Cabo Frio, com o mesmo método de avaliação.",
           corpo, ativo="equipe", schema=schema)


def larissa():
    acoes = f'<a class="button button--shimmer" href="{wa(MSG_LARISSA)}"><span>Agendar Consulta Signature</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/consulta/">As duas consultas &rarr;</a>'
    arts = "".join(
        f'<div class="treat-step" data-spotlight><h3>{a["titulo"]}</h3><p>{", ".join(a["autores"])}. Brazilian Journal of Hair Health, v. 2, n. 1, 2025. '
        f'<a class="link" href="{href_artigo(a)}" rel="noopener">Ler na revista &#8599;</a> (DOI {a["doi"]})</p></div>'
        for a in ARTIGOS
    )
    corpo = (
        phero("Dra. Larissa Pessoa", "Fundadora e CEO da Hairzenith. Tricologista especializada em queda de cabelo e calvície.", None,
              ("larissa-blazer", "Dra. Larissa Pessoa de blazer branco, com a mão no rosto"), ("larissa-rosa-retrato", "Retrato da Dra. Larissa Pessoa de vestido rosé"), acoes)
        + dividida(
            "Da clínica com o seu nome à Hairzenith",
            ("larissa-sentada", "Dra. Larissa Pessoa sorri sentada em uma poltrona clara"),
            "<p class=\"lead\">Por anos, a clínica levou o nome dela: Larissa Pessoa Tricologia Integrativa, em Copacabana e Cabo Frio.</p>"
            "<p>O consultório cresceu, a equipe também, e o método que a Dra. Larissa Pessoa desenvolveu passou a ser conduzido por outras tricologistas. A Hairzenith é a forma desse crescimento: uma clínica com estrutura, equipe e nome próprios, fundada e dirigida por ela.</p>"
            "<p>Quem procura pela Dra. Larissa Pessoa continua encontrando a Dra. Larissa Pessoa. Ela segue atendendo, agora dentro da Hairzenith, na Consulta Signature.</p>",
            "h-trajetoria",
        )
        + faixa(
            "Uma história com a queda",
            "<p>A Dra. Larissa Pessoa já passou pela queda de cabelo. Conhece de perto o efeito dela na autoestima, e é isso que orienta o jeito como cada consulta é conduzida: tempo para ouvir, explicação clara de cada achado e acompanhamento próximo.</p>"
            "<p>É também o que explica a escolha de trabalhar só com um assunto. Queda e calvície, em mulheres e homens, sem cirurgia.</p>",
            ("larissa-rosa", "Dra. Larissa Pessoa de vestido rosé em uma sala clara"),
            f'<a class="button button--gold" href="{wa(MSG_LARISSA)}"><span>Agendar Consulta Signature</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>',
            "h-historia",
        )
        + dividida("Publicações", ("cowper-1698", "Gravura de 1698 com cortes de pele e folículos capilares ampliados"),
                   "<p class=\"lead\">Dois estudos de caso sobre alopecia androgenética, escritos com a equipe da clínica e a Faculdade de Farmácia da UFRJ.</p><div class=\"treat-grid\">" + arts + "</div>",
                   "h-publicacoes", inverte=True)
        + fecho("A Consulta Signature tem agenda própria e valor diferenciado.", "Quer ser atendido pela Dra. Larissa Pessoa?", ("larissa-rosa-retrato", "Retrato da Dra. Larissa Pessoa de vestido rosé"))
    )
    schema = [schema_larissa(), {"@type": "ProfilePage", "url": SITE + "/equipe/larissa-pessoa/", "mainEntity": {"@id": LARISSA_ID}},
              migalhas([("Hairzenith", "/"), ("Equipe", "/equipe/"), ("Dra. Larissa Pessoa", "/equipe/larissa-pessoa/")])] + schema_artigos()
    pagina("/equipe/larissa-pessoa/", "Dra. Larissa Pessoa, tricologista em Copacabana | Hairzenith",
           "A Dra. Larissa Pessoa é fundadora e CEO da Hairzenith. Tricologista em queda de cabelo e calvície, com atendimento em Copacabana e em Cabo Frio.",
           corpo, ativo="equipe", schema=schema, imagem="larissa-blazer", tipo="profile")


FAQ_CONSULTA = [
    ("Qual a diferença entre as duas consultas?", "O método é o mesmo: história clínica, tricoscopia, exames quando necessários e plano de tratamento. Na Consulta Signature, quem conduz é a Dra. Larissa Pessoa, fundadora e CEO, com agenda própria e valor diferenciado."),
    ("Quanto custa a consulta?", "Os valores das duas modalidades são informados no agendamento, pelo WhatsApp."),
    ("O tratamento começa na mesma consulta?", "A consulta é de avaliação e planejamento. O tratamento começa depois, em casa, no consultório ou nos dois, conforme o plano definido."),
    ("O que levar?", "Exames de sangue recentes, se você tiver, e a lista dos medicamentos e suplementos que usa."),
    ("Vocês atendem homens e mulheres?", "Sim. A Hairzenith trata queda e calvície em mulheres e homens."),
]


def consulta():
    def caminho(cls, selo, titulo, texto, foto, linhas, acao):
        dl = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in linhas)
        return (
            f'<article class="way {cls}" data-spotlight data-reveal>'
            f'<div class="way__top"><span class="way__badge">{selo}</span></div>'
            f'{moldura(foto[0], foto[1], "(max-width: 900px) 100vw, 44vw")}'
            f'<div class="way__body"><h3>{titulo}</h3><p>{texto}</p><dl>{dl}</dl><div class="actions">{acao}</div></div></article>'
        )

    comum = [("Avaliação", "História clínica e tricoscopia de até 200x"), ("Exames", "Solicitados quando a causa pede investigação"), ("Plano", "Em casa, no consultório ou nos dois")]
    equipe_ = caminho("way--team", "COM AS TRICOLOGISTAS DA HAIRZENITH", "Consulta Expert", "Uma avaliação individualizada, conduzida por profissionais da nossa equipe, para compreender suas necessidades capilares e orientar os próximos passos.",
                      ("tricoscopio-retrato", "Tricoscópio digital apoiado no couro cabeludo durante a avaliação"),
                      [("Quem conduz", "Dra. Thaina Cândido – Copacabana<br>Dra. Júlia Macedo – Cabo Frio")] + comum + [("Valor", "Informado no agendamento")],
                      f'<a class="button button--shimmer" href="{wa(MSG_EQUIPE)}"><span>Agendar Consulta Expert</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>')
    fundadora = caminho("way--founder", "DIRETAMENTE COM A CEO", "Consulta Signature", "Uma experiência personalizada para quem deseja ser atendida diretamente pela fundadora da Hairzenith, com sua experiência e olhar profissional.",
                        ("larissa-blazer", "Dra. Larissa Pessoa de blazer branco"),
                        [("Quem conduz", "Dra. Larissa Pessoa, fundadora e CEO da Hairzenith")] + comum + [("Valor", "Diferenciado, informado no agendamento")],
                        f'<a class="button button--gold" href="{wa(MSG_LARISSA)}"><span>Agendar Consulta Signature</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>')

    def escolha(nome, opcoes, marcada):
        return "".join(
            f'<label><input type="radio" name="{nome}" value="{e(o)}"{" checked" if o == marcada else ""}><span>{o}</span></label>' for o in opcoes
        )

    lugares = "".join(
        f'<div class="place" data-spotlight data-unidade="{u["nome"]}"><span class="kicker"><span class="kicker__dot"></span> {u["coords"]}</span>'
        f'<h3>{u["nome"]}</h3><p>{u["rua"]}<br>{u["bairro"]}</p>'
        f'<p>WhatsApp {u["whats_texto"]}</p>'
        f'<a class="link" href="{u["mapa"]}" rel="noopener">Como chegar &rarr;</a> '
        f'<a class="link" href="{wa(numero=u["whats"])}" data-unidade="{u["nome"]}">Agendar nesta unidade &rarr;</a></div>'
        for u in UNIDADES
    )
    acoes = f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="#h-modalidades">Comparar as modalidades &rarr;</a>'
    corpo = (
        phero("Consulta de tricologia", "Duas modalidades, um mesmo método. O que muda é quem conduz a sua consulta.", None,
              ("tela-tricoscopia-retrato", "Imagem ampliada dos fios na tela durante a tricoscopia"), ("larissa-sentada", "Dra. Larissa Pessoa sentada em uma poltrona clara"), acoes)
        + f"""
<section class="ways wrap grid" aria-labelledby="h-modalidades">
  <div class="ways__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> MODALIDADES DE ATENDIMENTO</span>
    <h2 id="h-modalidades" data-reveal>A mesma filosofia de cuidado.</h2>
    <p class="ways__intro" data-reveal style="--i:1">Duas formas de viver a experiência Hairzenith.</p>
  </div>
  {equipe_}
  {fundadora}
</section>
"""
        + momentos("O que acontece na sua consulta", "h-etapas")
        + f"""
<section class="composer" aria-labelledby="h-mensagem">
  <div class="wrap grid">
    <div class="composer__head">
      <span class="kicker" data-reveal><span class="kicker__dot"></span> AGENDAMENTO</span>
      <h2 id="h-mensagem" data-reveal>Monte sua mensagem</h2>
      <p class="composer__intro" data-reveal style="--i:1">Escolha a consulta, a unidade e o que você está sentindo. A mensagem fica pronta para enviar pelo WhatsApp, e a equipe responde com os horários e o valor.</p>
    </div>
    <form class="composer__form" data-composer="{WHATS}" data-spotlight>
      <fieldset><legend>01 • Modalidade de Consulta</legend><div class="choices">{escolha("tipo", ["Consulta Expert", "Consulta Signature"], "Consulta Expert")}</div></fieldset>
      <fieldset><legend>02 • Unidade de Preferência</legend><div class="choices">{escolha("unidade", ["Copacabana", "Cabo Frio", "Tanto faz"], "Copacabana")}</div></fieldset>
      <fieldset><legend>03 • O que você está percebendo</legend><div class="choices">{escolha("queixa", ["Queda de cabelo", "Calvície", "Couro cabeludo aparente", "Fios mais finos", "Perda de volume", "Prefiro contar na consulta"], "Prefiro contar na consulta")}</div></fieldset>
      <fieldset><legend>04 • Período Preferencial</legend><div class="choices">{escolha("periodo", ["Manhã", "Tarde", "Qualquer horário"], "Qualquer horário")}</div></fieldset>
      <div class="composer__preview" aria-live="polite">
        <span class="composer__preview-label">MENSAGEM PRONTA PARA ENVIO</span>
        <p data-message>{MSG_EQUIPE}</p>
      </div>
      <div><a class="button button--shimmer" data-send href="{wa(MSG_EQUIPE)}" target="_blank" rel="noopener"><span>Enviar pelo WhatsApp</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a></div>
    </form>
  </div>
</section>

<section class="places wrap grid" aria-labelledby="h-unidades">
  <div class="places__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> ENDEREÇOS EXCLUSIVOS</span>
    <h2 id="h-unidades" data-reveal>Onde atendemos</h2>
  </div>
  <figure class="places__pic">{moldura("avenida-copacabana", "A Avenida Nossa Senhora de Copacabana, com prédios e árvores dos dois lados", "(max-width: 900px) 84vw, 34vw")}<figcaption>Avenida Nossa Senhora de Copacabana</figcaption></figure>
  <div class="places__list" data-reveal>{lugares}<div class="place place--dark" data-spotlight><span class="kicker kicker--gold"><span class="kicker__dot"></span> EXPANSÃO • 2027</span><h3>Março de 2027</h3><p>A nova Hairzenith abre as portas. Até lá, os atendimentos seguem nestes dois endereços.</p><a class="link" href="~/nova-clinica/">A nova clínica &rarr;</a></div></div>
</section>
"""
        + perguntas("Perguntas frequentes", FAQ_CONSULTA)
        + fecho("Agende pelo WhatsApp e receba os horários das duas consultas.", "Pronto para agendar?")
    )
    schema = [
        {"@type": "WebPage", "url": SITE + "/consulta/", "name": "Consulta de tricologia", "inLanguage": "pt-BR",
         "mainEntity": [
             {"@type": "Service", "name": "Consulta Expert", "serviceType": "Consulta de tricologia", "provider": {"@id": ORG_ID}, "description": "Consulta conduzida por uma tricologista da equipe Hairzenith, com tricoscopia de até 200x e plano de tratamento."},
             {"@type": "Service", "name": "Consulta Signature", "serviceType": "Consulta de tricologia", "provider": {"@id": LARISSA_ID}, "description": "Consulta conduzida pela fundadora da Hairzenith, com agenda própria e valor diferenciado."},
         ]},
        migalhas([("Hairzenith", "/"), ("Consulta", "/consulta/")]),
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_CONSULTA]},
        schema_larissa(),
    ]
    pagina("/consulta/", "Consulta com tricologista em Copacabana | Hairzenith",
           "Consulta com a equipe Hairzenith ou com a Dra. Larissa Pessoa. Tricoscopia em Copacabana e Cabo Frio. Horários e o valor da avaliação são informados no WhatsApp.",
           corpo, ativo="consulta", schema=schema)


def sobre():
    acoes = f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/nova-clinica/">A nova clínica &rarr;</a>'
    corpo = (
        phero("Sobre a Hairzenith", "Depois de anos atendendo pacientes com queda e calvície, a Dra. Larissa Pessoa decidiu transformar sua experiência em uma clínica especializada.", None,
              ("larissa-rosa-retrato", "Retrato da Dra. Larissa Pessoa de vestido rosé"), ("tricoscopio", "Tricoscópio digital apoiado no couro cabeludo"), acoes)
        + dividida(
            "Por que a marca nasce",
            ("larissa-poltrona", "Dra. Larissa Pessoa sentada em uma poltrona clara"),
            "<p class=\"lead\">Durante anos, o consultório levou o nome da Dra. Larissa Pessoa. E a pergunta que chegava a ele era quase sempre a mesma: vou ficar careca?</p>"
            "<p>Responder exigia tempo. Exigia examinar o couro cabeludo de perto, investigar a causa, montar um plano e acompanhar cada etapa, por meses. Exigia, cada vez mais, uma equipe.</p>"
            "<p>A Hairzenith é a resposta a essa demanda: uma clínica dedicada a um único assunto, a queda e a calvície, com equipe, método e estrutura para atender mais pessoas com o mesmo cuidado. Um método que não depende de uma pessoa só para existir, e uma fundadora que continua presente.</p>",
            "h-por-que",
        )
        + f"""
<section class="mosaic wrap" aria-labelledby="h-nome">
  <div class="grid">
    <div class="mosaic__header">
      <span class="kicker" data-reveal><span class="kicker__dot"></span> ETIMOLOGIA &amp; VISÃO</span>
      <h2 id="h-nome" class="head" data-reveal>O nome</h2>
      <p class="mosaic__lead lead" data-reveal>Zênite é o ponto mais alto do céu, bem acima de quem olha. Na tricologia, é de cima que se avalia o couro cabeludo: a vista do topo mostra a risca, a coroa e a densidade de uma só vez.</p>
    </div>
    <figure class="mosaic__photo">{moldura("tela-tricoscopia", "Fios ampliados na tela durante uma tricoscopia", "(max-width: 900px) 100vw, 58vw")}<div class="mosaic__paper" data-spotlight><span class="kicker"><span class="kicker__dot"></span> PERSPECTIVA SUPERIOR</span><p>Hairzenith junta as duas ideias: o cabelo visto do ponto mais alto, e uma clínica que trabalha para levar cada caso ao melhor resultado possível.</p></div></figure>
    <div class="mosaic__side zmap" data-on="couro-cabeludo-aparente" data-reveal style="--i:2" data-spotlight><div class="zmap__topbar"><span>ATLAS DO ZÊNITE</span><span>PERSPECTIVA 90°</span></div><div class="mosaic__tile" style="aspect-ratio:auto;padding:1.25rem 2rem;background:transparent">{mapa_zenite()}</div><p class="zmap__caption small">A cabeça vista do zênite: a frente no alto, a coroa embaixo.</p></div>
  </div>
</section>
"""
        + dividida(
            "O que muda e o que continua",
            None,
            "<div class=\"treat-grid\">"
            "<div class=\"treat-step\" data-spotlight><h3>Muda</h3><ul><li>O nome: Larissa Pessoa Tricologia Integrativa passa a se chamar Hairzenith.</li><li>A estrutura: uma nova clínica, em construção, com inauguração em março de 2027.</li><li>A equipe ganha nome e lugar: Thaina Candido de Souza e Júlia são tricologistas Hairzenith.</li></ul></div>"
            f"<div class=\"treat-step\" data-spotlight><h3>Continua</h3><ul><li>Os atendimentos em Copacabana e Cabo Frio, até a inauguração.</li><li>Os WhatsApp de Copacabana, {UNIDADES[0]['whats_texto']}, e de Cabo Frio, {UNIDADES[1]['whats_texto']}, e o Instagram {INSTAGRAM_TEXTO}.</li><li>O método de avaliação e tratamento, sem cirurgia.</li><li>A Dra. Larissa Pessoa, que dirige a clínica e segue atendendo.</li></ul></div>"
            "</div>",
            "h-transicao",
        )
        + faixa(
            "Dra. Larissa Pessoa e a Hairzenith",
            "<p>A Dra. Larissa Pessoa é fundadora e CEO da Hairzenith e segue como tricologista da clínica. Quem procurava por ela continua encontrando, agora dentro de uma estrutura maior.</p>",
            ("larissa-blazer", "Dra. Larissa Pessoa de blazer branco"),
            f'<a class="button button--gold" href="{wa(MSG_LARISSA)}"><span>Agendar Consulta Signature</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/equipe/larissa-pessoa/">A trajetória da Dra. Larissa Pessoa &rarr;</a>',
            "h-fundadora",
        )
        + fecho("Mesma equipe, mesmos endereços, novo nome. Agende pelo WhatsApp.", "Vamos conversar?")
    )
    schema = [
        {"@type": "AboutPage", "url": SITE + "/sobre/", "name": "Sobre a Hairzenith", "inLanguage": "pt-BR", "mainEntity": {"@id": ORG_ID}},
        migalhas([("Hairzenith", "/"), ("Sobre", "/sobre/")]),
        schema_larissa(),
    ]
    pagina("/sobre/", "Sobre a Hairzenith: tricologia em Copacabana e Cabo Frio",
           "A clínica de tricologia fundada pela Dra. Larissa Pessoa. Atendimento em Copacabana, no Rio de Janeiro, e em Cabo Frio, com o mesmo método e a mesma equipe.",
           corpo, ativo="sobre", schema=schema)


def nova_clinica():
    acoes = f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="#h-diario">Diário de obra &rarr;</a>'
    entradas = [
        ("Outubro de 2026", "A marca Hairzenith é apresentada", "Larissa Pessoa Tricologia Integrativa passa a se chamar Hairzenith. Equipe, endereços e contatos continuam os mesmos.", "done"),
        ("Em andamento", "Obra da nova clínica", "A construção avança conforme o projeto arquitetônico. Cada etapa da obra entra neste diário.", "now"),
        ("Março de 2027", "Inauguração", "A nova Hairzenith abre as portas e os atendimentos passam para a nova sede.", "next"),
    ]
    log = "".join(
        f'<li data-state="{s}" data-spotlight data-reveal style="--i:{i}"><div class="log__meta"><span class="log__roman">{ROMANOS[i]}</span><p class="log__when">{q}</p></div><div><h3>{t}</h3><p>{d}</p></div></li>'
        for i, (q, t, d, s) in enumerate(entradas)
    )
    corpo = (
        phero("Nova clínica Hairzenith", "A nova Hairzenith chega em março de 2027.", "Uma clínica construída do zero para a saúde capilar. Enquanto a obra avança, nossa equipe segue atendendo em Copacabana e Cabo Frio.",
              ("larissa-rosa-retrato", "Retrato da Dra. Larissa Pessoa de vestido rosé"), ("mesoject", "Caneta do Mesoject sobre o couro cabeludo"), acoes)
        + f"""
<section class="count" aria-labelledby="h-marco" data-countdown="{INAUGURACAO}">
  <div class="wrap grid">
    <div class="count__copy">
      <span class="kicker kicker--gold" data-reveal><span class="kicker__dot"></span> NOVA SEDE • CONTAGEM REGRESSIVA</span>
      <h2 id="h-marco" data-reveal>Março de 2027</h2>
      <p data-reveal style="--i:1">É quando a Hairzenith passa a ter a sua própria casa: um espaço pensado a partir do atendimento em tricologia, da chegada do paciente à reavaliação.</p>
    </div>
    <p class="count__n" aria-live="polite"><span data-days>Março</span> <small data-unit>de 2027</small></p>
  </div>
</section>

<section class="log wrap grid" aria-labelledby="h-diario">
  <div class="log__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> CRONOGRAMA ARQUITETÔNICO</span>
    <h2 id="h-diario" data-reveal>Diário de obra</h2>
    <p class="log__intro" data-reveal style="--i:1">O projeto arquitetônico e a evolução da construção, etapa por etapa, até a inauguração.</p>
  </div>
  <ol>{log}</ol>
</section>
"""
        + reunidas("Enquanto isso, seguimos atendendo", "Em Copacabana e em Cabo Frio, com a mesma equipe e o mesmo método.", f'<a class="button button--gold" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>', [
            ("tricoscopio-retrato", "Tricoscópio apoiado no couro cabeludo"),
            ("microinfusao", "Aplicação de ativos ao longo da risca"),
            ("larissa-sentada", "Dra. Larissa Pessoa sentada em uma poltrona clara"),
            ("laser-led", "Capacete de laser e LED sobre a cabeça de uma paciente"),
            ("tela-tricoscopia-retrato", "Fios ampliados na tela da tricoscopia"),
            ("analise-imagens", "Paciente revisa as imagens dos próprios fios"),
        ], "h-enquanto")
        + fecho("A obra não interrompe os atendimentos.", "Quer agendar agora?")
    )
    schema = [
        {"@type": "WebPage", "url": SITE + "/nova-clinica/", "name": "Nova clínica Hairzenith", "inLanguage": "pt-BR", "about": {"@id": ORG_ID}},
        {"@type": "Event", "name": "Inauguração da nova clínica Hairzenith", "startDate": INAUGURACAO, "eventStatus": "https://schema.org/EventScheduled",
         "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "organizer": {"@id": ORG_ID},
         "location": {"@type": "Place", "name": "Hairzenith", "address": {"@type": "PostalAddress", "addressLocality": "Rio de Janeiro", "addressRegion": "RJ", "addressCountry": "BR"}}},
        migalhas([("Hairzenith", "/"), ("Nova clínica", "/nova-clinica/")]),
    ]
    pagina("/nova-clinica/", "Nova clínica em 2027 | Hairzenith Copacabana e Cabo Frio",
           "A nova sede da Hairzenith chega em março de 2027. Até a inauguração, a equipe segue atendendo em Copacabana e em Cabo Frio, com hora marcada.",
           corpo, ativo="nova-clinica", schema=schema)


ARTIGO = {
    "slug": "quando-a-queda-de-cabelo-nao-e-normal",
    "titulo": "Quando a queda de cabelo não é normal?",
    "resumo": "A queda de cabelo não é normal quando ultrapassa o limite fisiológico diário, causa falhas visíveis ou vem acompanhada de afinamento dos fios.",
    "data": "2025-12-05",
    "data_texto": "5 de dezembro de 2025",
    "corpo": [
        ("p", "A queda de cabelo faz parte do ciclo natural dos fios, mas muita gente não sabe identificar quando ela passa do limite saudável. Reconhecer os sinais de alerta é o que permite buscar ajuda no momento certo, e um especialista em tricologia consegue diferenciar causas comuns de quadros que pedem intervenção rápida."),
        ("p", "Nem sempre a queda é evidente. Muitas vezes o primeiro sintoma é o afinamento dos fios, a perda de volume ou a dificuldade de crescimento. São sinais de alterações no ciclo capilar que precisam ser avaliadas com exame clínico e, quando necessário, laboratorial."),
        ("p", "Estresse, genética, alterações hormonais, deficiências nutricionais e doenças do couro cabeludo provocam tipos diferentes de queda. Cada caso pede uma abordagem específica: tratamentos genéricos podem não resolver e ainda atrasar o diagnóstico. Quando a queda é identificada cedo, as chances de recuperação são muito maiores."),
        ("h2", "Quando a queda de cabelo passa do normal?"),
        ("p", "A queda natural varia entre 50 e 100 fios por dia, conforme a genética, os hábitos e a rotina. Quando passa desse limite, se torna contínua ou aparece em grande quantidade no travesseiro, no ralo ou na escova, já é um indicativo de que algo mudou."),
        ("p", "Outro sinal de alerta é o fio que cai com a raiz, com o bulbo visível, em grande volume. Isso pode indicar eflúvio telógeno, efeito de uma fase de estresse ou de uma doença sistêmica. Sem avaliação, o quadro tende a se prolongar."),
        ("p", "Também vale observar o couro cabeludo: sensibilidade, irritação, coceira ou aumento da oleosidade, somados a uma queda acima da média, sugerem processos inflamatórios ou infecciosos que pedem tratamento especializado."),
        ("h2", "Quais sinais indicam que é hora de procurar um tricologista?"),
        ("p", "Falhas circulares ou áreas mais ralas no topo, nas entradas ou nas laterais indicam distúrbios do ciclo capilar, como a alopecia androgenética e a alopecia areata, que se beneficiam de diagnóstico precoce."),
        ("p", "Fios que ficam progressivamente mais finos ao longo dos meses revelam miniaturização capilar. Sem tratamento, o processo pode levar à perda definitiva dos folículos. Quanto antes a intervenção, maiores as chances de estabilizar e recuperar."),
        ("p", "Descamação intensa, caspa persistente, coceira ou excesso de oleosidade também justificam a consulta. Podem estar ligados a dermatites ou fungos que fragilizam os fios e desencadeiam queda."),
        ("h2", "Quais são as causas mais comuns?"),
        ("p", "O tricologista identifica desde causas simples, como estresse e carências nutricionais, até condições mais complexas, como as alopecias inflamatórias. O estresse acelera o ciclo de queda e dificulta o crescimento adequado dos fios."),
        ("p", "Alterações hormonais, como pós-parto, menopausa e distúrbios da tireoide, também provocam quedas importantes. Nesses casos, exames complementares direcionam o tratamento para a origem do problema."),
        ("p", "Doenças do couro cabeludo, como dermatite seborreica, psoríase e infecções fúngicas, enfraquecem o folículo e mantêm a queda ativa. Sem tratamento, podem evoluir para afinamento permanente."),
        ("h2", "Quais exames avaliam a queda de cabelo?"),
        ("p", "A avaliação começa pela tricoscopia, exame que amplia a imagem dos fios e do couro cabeludo em até 200 vezes. Ela mostra inflamações, miniaturização, densidade capilar e os padrões característicos de cada tipo de alopecia. É rápida e indolor."),
        ("p", "Exames laboratoriais investigam anemia, alterações hormonais, deficiências de vitaminas e doenças autoimunes, condições que interferem diretamente no ciclo do fio. Em casos específicos, testes de tração, biópsia do couro cabeludo ou mapeamento digital de densidade podem ser indicados para aprofundar o diagnóstico."),
        ("h2", "Quais tratamentos são usados?"),
        ("p", "Os tratamentos variam conforme o diagnóstico e incluem ativos tópicos, estimuladores capilares, suplementação, controle hormonal e terapias de fortalecimento. O objetivo é interromper a queda e estimular o crescimento saudável."),
        ("p", "Entre os procedimentos mais usados estão a microinfusão de ativos no couro cabeludo, o laser e o LED terapêuticos, o microagulhamento e as terapias combinadas. Em casos avançados, abordagens integradas ou até o transplante capilar podem ser considerados. A escolha depende do estágio e da causa, e o acompanhamento regular aumenta as chances de resultado."),
        ("h2", "Em resumo"),
        ("p", "Reconhecer quando a queda de cabelo não é normal é o primeiro passo para evitar que o problema evolua. Com diagnóstico correto e acompanhamento, é possível recuperar volume, fortalecer os fios e prevenir falhas permanentes."),
    ],
}


def conteudo():
    a = ARTIGO
    corpo = (
        phero(["Saúde capilar,", "explicada"], "Textos da equipe Hairzenith sobre queda, calvície e cuidados com o couro cabeludo, com fundamento clínico e linguagem direta.", None,
              ("escovando", "Mulher observa os fios enquanto escova o cabelo"), ("fio-na-mao", "Mulher segura entre os dedos um fio que caiu"), f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>')
        + f"""
<section class="posts wrap grid" aria-labelledby="h-artigos">
  <h2 id="h-artigos" class="sr-only">Artigos</h2>
  <a class="post" href="~/conteudo/{a['slug']}/" data-reveal data-spotlight>
    {moldura("fio-na-mao", "Mulher segura entre os dedos um fio que caiu", "(max-width: 900px) 100vw, 44vw", attrs="")}
    <div class="post__text">
      <span class="kicker"><span class="kicker__dot"></span> ARTIGO EM DESTAQUE</span>
      <h2>{a['titulo']}</h2>
      <p>{a['resumo']}</p>
      <p class="small">Por Dra. Larissa Pessoa • {a['data_texto']} • <span class="link">Ler artigo completo &rarr;</span></p>
    </div>
  </a>
</section>
"""
        + nomes("Publicações científicas", [["Brazilian Journal of Hair Health, 2025"] + [f'<a href="{href_artigo(x)}" rel="noopener">{x["curto"]} &#8599;</a>' for x in ARTIGOS],
                                           ["Autoras", "Larissa Mota Barros Pessoa", "Thaina Candido de Souza", "Lara Junqueira, UFRJ"]], "h-cientificas")
        + definicoes("Glossário", "Os termos que aparecem na consulta e nos exames, explicados sem rodeios.", GLOSSARIO,
                     ("cowper-1698", "Gravura de 1698 com cortes de pele e folículos capilares ampliados"), "h-glossario")
        + indice("Guias por sinal", None, "h-guias")
        + fecho("Leu e se reconheceu em algum sinal? A avaliação mostra a causa.", "Quer uma avaliação?")
    )
    schema = [
        {"@type": "Blog", "url": SITE + "/conteudo/", "name": "Saúde capilar, explicada", "publisher": {"@id": ORG_ID}, "inLanguage": "pt-BR",
         "blogPost": [{"@type": "BlogPosting", "headline": a["titulo"], "url": SITE + f"/conteudo/{a['slug']}/"}]},
        migalhas([("Hairzenith", "/"), ("Conteúdo", "/conteudo/")]),
        schema_larissa(),
    ]
    pagina("/conteudo/", "Conteúdo de tricologia em Copacabana | Hairzenith",
           "Textos da equipe sobre queda, calvície e couro cabeludo. Clínica de tricologia Hairzenith em Copacabana e Cabo Frio, com linguagem direta e base clínica.",
           corpo, ativo="conteudo", schema=schema)

    texto = []
    for tag, t in a["corpo"]:
        texto.append(f"<{tag} data-reveal>{t}</{tag}>")
    corpo = f"""
<article class="article wrap grid" aria-labelledby="titulo">
  <div class="article__header">
    <span class="kicker" data-load style="--d:100ms"><span class="kicker__dot"></span> CONTEÚDO • HAIRZENITH</span>
    <h1 id="titulo" class="lines"><span class="line"><span data-line>{a['titulo']}</span></span></h1>
    <p class="article__meta" data-load style="--d:300ms">Por <a href="~/equipe/larissa-pessoa/">Dra. Larissa Pessoa</a>, fundadora da Hairzenith • Publicado em {a['data_texto']}.</p>
  </div>
  <figure class="article__pic">{moldura("escova-fios", "Fios presos nas cerdas de uma escova", "100vw", attrs="data-shutter", prioridade=True)}</figure>
  <div class="article__body"><p class="lead">{a['resumo']}</p>{''.join(texto)}</div>
  <aside class="article__aside" aria-label="Sobre a autora" data-reveal data-spotlight>
    <span class="kicker"><span class="kicker__dot"></span> AUTORA</span>
    {moldura("larissa-sentada", "Dra. Larissa Pessoa sentada em uma poltrona clara", "(max-width: 900px) 60vw, 22vw")}
    <p>A Dra. Larissa Pessoa é tricologista, fundadora e CEO da Hairzenith. <a class="link" href="~/equipe/larissa-pessoa/">Conheça a trajetória &rarr;</a></p>
  </aside>
</article>
""" + indice("Guias por sinal", None, "h-guias") + fecho("Se a sua queda passou do normal, a avaliação mostra a causa.", "Quer uma avaliação?")
    schema = [
        {"@type": "BlogPosting", "headline": a["titulo"], "description": a["resumo"], "datePublished": a["data"], "dateModified": ATUALIZADO,
         "author": {"@id": LARISSA_ID}, "publisher": {"@id": ORG_ID}, "image": SITE + "/assets/img/escova-fios.jpg",
         "mainEntityOfPage": SITE + f"/conteudo/{a['slug']}/", "inLanguage": "pt-BR"},
        migalhas([("Hairzenith", "/"), ("Conteúdo", "/conteudo/"), (a["titulo"], f"/conteudo/{a['slug']}/")]),
        schema_larissa(),
    ]
    pagina(
        f"/conteudo/{a['slug']}/",
        "Queda de cabelo fora do normal | Copacabana e Cabo Frio",
        "Queda acima de 100 fios por dia, falhas visíveis ou fios mais finos: quando procurar um tricologista em Copacabana ou Cabo Frio, na clínica Hairzenith.",
        corpo,
        ativo="conteudo",
        schema=schema,
        imagem="escova-fios",
        tipo="article",
    )


def nao_encontrada():
    corpo = (
        phero("Página não encontrada", "O endereço mudou ou não existe. As páginas da antiga Larissa Pessoa Tricologia agora fazem parte da Hairzenith.", None,
              ("larissa-poltrona", "Dra. Larissa Pessoa sentada em uma poltrona clara"), ("tricoscopio", "Tricoscópio digital apoiado no couro cabeludo"),
              f'<a class="button button--shimmer" href="~/"><span>Ir para o início</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/tratamentos/">Tratamentos &rarr;</a>')
        + indice("Talvez você procure", None, "h-talvez")
    )
    pagina("/404/", "Página não encontrada | Hairzenith", "Esta página não existe. Veja os tratamentos da Hairzenith.", corpo, indexar=False)
    # Servida pelo host em qualquer endereço desconhecido. Links já são absolutos.
    doc = (SAIDA / "404" / "index.html").read_text(encoding="utf-8")
    (SAIDA / "404.html").write_text(doc, encoding="utf-8")
    (SAIDA / "404" / "index.html").unlink()
    (SAIDA / "404").rmdir()
    PAGINAS.remove("/404/")


# ---------------------------------------------------------------- arquivos de apoio
REDIRECIONAMENTOS = [
    ("/clinica-de-tricologia-no-rio-de-janeiro", "/sobre/"),
    ("/tratamento-para-queda-de-cabelo-no-rio-de-janeiro", "/queda-de-cabelo/"),
    ("/tratamento-para-calvice-no-rio-de-janeiro", "/tratamentos/"),
    ("/especialista-em-tricologia-no-rio-de-janeiro-quando-a-queda-de-cabelo-nao-e-normal", "/conteudo/quando-a-queda-de-cabelo-nao-e-normal/"),
    ("/blog-de-saude-capilar", "/conteudo/"),
    ("/publicacoes", "/equipe/larissa-pessoa/"),
    ("/index.html", "/"),
]


def apoio():
    favicon = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#120F0D"/>'
        '<circle cx="32" cy="32" r="26" fill="none" stroke="#C5A059" stroke-opacity="0.35" stroke-width="1.5"/>'
        '<circle cx="32" cy="20" r="5.5" fill="#C5A059"/><rect x="16" y="40" width="32" height="3" rx="1.5" fill="#FAF7F2"/></svg>'
    )
    (SAIDA / "favicon.svg").write_text(favicon)
    (SAIDA / "site.webmanifest").write_text(json.dumps({
        "name": "Hairzenith", "short_name": "Hairzenith", "lang": "pt-BR", "start_url": "/", "display": "browser",
        "background_color": "#FAF7F2", "theme_color": "#120F0D",
        "icons": [{"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}, {"src": "/icone-512.png", "sizes": "512x512", "type": "image/png"}],
    }, ensure_ascii=False, indent=1))
    prioridade = {"/": "1.0"}
    urls = "".join(
        f"<url><loc>{SITE}{c}</loc><lastmod>{ATUALIZADO}</lastmod><priority>{prioridade.get(c, '0.8' if c.count('/') == 2 else '0.6')}</priority></url>"
        for c in PAGINAS
    )
    (SAIDA / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (SAIDA / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    # Netlify / Cloudflare Pages. /index.html não ganha barra extra.
    linhas_redirect = []
    for origem, destino in REDIRECIONAMENTOS:
        linhas_redirect.append(f"{origem} {destino} 301\n")
        if not origem.endswith(".html"):
            linhas_redirect.append(f"{origem}/ {destino} 301\n")
    (SAIDA / "_redirects").write_text("".join(linhas_redirect))
    # Vercel: trailingSlash redireciona /caminho para /caminho/ antes da regra,
    # então a origem precisa existir com e sem barra.
    regras = []
    for origem, destino in REDIRECIONAMENTOS:
        regras.append({"source": origem, "destination": destino, "permanent": True})
        if not origem.endswith(".html"):
            regras.append({"source": origem + "/", "destination": destino, "permanent": True})
    vercel_cfg = {
        "buildCommand": "npm run build",
        "outputDirectory": "site",
        "trailingSlash": True,
        "redirects": regras,
    }
    (SAIDA / "vercel.json").write_text(json.dumps({
        "trailingSlash": True,
        "redirects": vercel_cfg["redirects"],
    }, indent=2))
    (RAIZ / "vercel.json").write_text(json.dumps(vercel_cfg, indent=2))


def main():
    home()
    for p in PROBLEMAS:
        problema(p)
    tratamentos()
    equipe()
    larissa()
    consulta()
    sobre()
    nova_clinica()
    conteudo()
    nao_encontrada()
    apoio()
    print(f"{len(PAGINAS)} páginas geradas em {SAIDA}")
    print(f"domínio: {SITE}")
    src, tid = resolver_rastreio_ghl()
    print(f"tag manager: {GTM_ID} (GA4 e Pixel ficam dentro do GTM, sem gtag no HTML)")
    print(f"external tracking: {tid} ({urlparse(src).netloc})")


if __name__ == "__main__":
    main()
