#!/usr/bin/env python3
"""Gera o site estático da Hairzenit dentro de site/.

Uso:  python3 build.py
Depois, para ver localmente:  python3 -m http.server 8080 --directory site

Todo o texto do site está neste arquivo. Para trocar um contato, um endereço ou a data da
inauguração, edite as constantes logo abaixo e rode o script de novo.
"""
import html
import json
import math
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "site"

# ---------------------------------------------------------------- dados da clínica
SITE = "https://www.hairzenit.com.br"  # domínio definitivo (ainda a registrar)
ATUALIZADO = "2026-10-28"
WHATS = "5521972780789"
WHATS_TEXTO = "(21) 97278-0789"
EMAIL = "lamptricologia@gmail.com"
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
        "cep": "",
        "mapa": "https://www.google.com/maps/search/?api=1&query=" + quote("Av. Nossa Senhora de Copacabana, 807, Copacabana, Rio de Janeiro"),
        "lat": -22.9667, "lon": -43.1856,
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

MSG_PADRAO = "Olá! Vim pelo site da Hairzenit e gostaria de agendar uma consulta."
MSG_LARISSA = "Olá! Vim pelo site da Hairzenit e gostaria de agendar a Consulta com Larissa Pessoa."
MSG_EQUIPE = "Olá! Vim pelo site da Hairzenit e gostaria de agendar a Consulta Hairzenit."

ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def wa(msg=MSG_PADRAO):
    return f"https://wa.me/{WHATS}?text={quote(msg)}"


def e(texto):
    return html.escape(texto, quote=True)


# ---------------------------------------------------------------- imagens
def pic(nome, alt, sizes="(max-width: 900px) 100vw, 40vw", prioridade=False):
    m = MANIFESTO[nome]
    g, p = m["g"], m["p"]
    carregamento = ' fetchpriority="high"' if prioridade else ' decoding="async"'
    return (
        f'<img src="~/assets/img/{nome}.jpg" srcset="~/assets/img/{nome}-p.jpg {p[0]}w, ~/assets/img/{nome}.jpg {g[0]}w" '
        f'sizes="{sizes}" width="{g[0]}" height="{g[1]}" alt="{e(alt)}"{carregamento}>'
    )


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
        "titulo": "Queda de cabelo: avaliação e tratamento no Rio de Janeiro | Hairzenit",
        "descricao": "Queda acima de 100 fios por dia tem causa, e a causa tem tratamento. Avaliação com tricoscopia e plano personalizado na Hairzenit, em Copacabana e Cabo Frio.",
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
        "titulo": "Calvície feminina: tratamento sem cirurgia no Rio de Janeiro | Hairzenit",
        "descricao": "Risca mais larga, topo com menos volume, fios mais finos: sinais de calvície feminina. Avaliação com tricoscopia e tratamento personalizado na Hairzenit.",
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
        "titulo": "Calvície masculina: tratamento sem cirurgia no Rio de Janeiro | Hairzenit",
        "descricao": "Entradas subindo e coroa abrindo? A calvície masculina pode ser controlada sem cirurgia. Tricoscopia, protocolo por estágio e acompanhamento na Hairzenit.",
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
        "titulo": "Couro cabeludo aparente: causas e tratamento no Rio de Janeiro | Hairzenit",
        "descricao": "Couro cabeludo aparecendo no topo, na risca ou sob a luz? Entenda as causas e como a Hairzenit avalia e trata a perda de cobertura capilar.",
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
        "titulo": "Afinamento dos fios: causas e tratamento no Rio de Janeiro | Hairzenit",
        "descricao": "Fios mais finos, curtos e frágeis são o primeiro sinal de miniaturização. Veja como a Hairzenit avalia e trata o afinamento capilar.",
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
        "titulo": "Perda de densidade capilar: tratamento no Rio de Janeiro | Hairzenit",
        "descricao": "Cabelo com menos volume e menos fios por área? A perda de densidade capilar tem tratamento. Avaliação com tricoscopia e protocolo personalizado na Hairzenit.",
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
    ("resultado-1", "Coroa", "antes e depois"),
    ("resultado-7", "Topo da cabeça", "antes e depois"),
    ("resultado-4", "Risca central", "três etapas"),
    ("resultado-2", "Linha frontal", "antes e depois"),
    ("resultado-5", "Topo", "três etapas"),
    ("resultado-3", "Têmpora", "antes e depois"),
    ("resultado-6", "Região frontal", "antes e depois"),
]

MOMENTOS = [
    ("Primeiro, a sua história", "Você conta quando a queda começou, o que mudou na rotina e o que espera do tratamento.", "larissa-sentada", "Larissa Pessoa sentada em uma poltrona clara", "Anamnese Clínica"),
    ("Depois, a tricoscopia", "O couro cabeludo é examinado com ampliação de até 200 vezes: inflamação, descamação, afinamento, unidades foliculares vazias.", "tricoscopio-retrato", "Tricoscópio digital apoiado no couro cabeludo", "Exame Óptico 200×"),
    ("Na tela, com você", "As imagens ampliadas aparecem na tela, e cada achado é explicado durante a consulta.", "tela-tricoscopia-retrato", "Imagem ampliada dos fios na tela durante a tricoscopia", "Mapeamento Visual"),
    ("Exames, se precisar", "Quando a causa pede investigação, são solicitados exames: ferro, vitaminas, tireoide, hormônios.", "analise-imagens", "Paciente revisa no notebook as imagens dos próprios fios", "Investigação Sistêmica"),
    ("O plano de tratamento", "Em casa, no consultório ou nos dois, com tecnologias escolhidas para a causa: laser e LED, MMP, microinfusão, Mesoject.", "microinfusao", "Aplicação de ativos ao longo da risca do cabelo", "Protocolo Sob Medida"),
    ("Os primeiros sinais", "Os resultados costumam aparecer entre 60 e 120 dias, conforme a causa e o protocolo.", "laser-led", "Capacete de laser e LED sobre a cabeça de uma paciente", "Ciclo de Resposta"),
    ("As reavaliações", "A evolução é fotografada e comparada a cada retorno, e o plano é ajustado a cada etapa.", "mesoject-retrato", "Caneta do Mesoject aplicada sobre o couro cabeludo", "Controle Evolutivo"),
]

GLOSSARIO = [
    ("Tricoscopia", "Exame que amplia o couro cabeludo e os fios, na Hairzenit em até 200 vezes, para ver o que o olho não alcança: inflamação, miniaturização, densidade."),
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
  <div class="notice"><div class="wrap notice__inner"><span class="notice__tag">TRANSIÇÃO DE MARCA</span><p>Larissa Pessoa Tricologia agora é <strong>Hairzenit</strong>. A nova clínica chega em março de 2027. <a class="link" href="~/nova-clinica/">Acompanhe a obra &rarr;</a></p></div></div>
  <div class="nav-shell">
    <nav class="nav wrap" aria-label="Principal">
      <a class="wordmark" href="~/" aria-label="Hairzenit, página inicial">
        {EMBLEMA_SVG}
        <span class="wordmark__text">
          <span class="wordmark__name">Hairzenit</span>
          <span class="wordmark__sub">Tricologia • Larissa Pessoa</span>
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
      <span class="wordmark">{EMBLEMA_SVG}<span class="wordmark__text"><span class="wordmark__name">Hairzenit</span><span class="wordmark__sub">Maison de Tricologia</span></span></span>
      <button class="menu__close" type="button">Fechar &times;</button>
    </div>
    <ul>{menu}</ul>
    <div class="menu__footer">
      <a class="button button--gold" href="{wa()}"><span>Agendar pelo WhatsApp</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>
      <p class="menu__note">Copacabana (RJ) e Novo Portinho (Cabo Frio) • WhatsApp {WHATS_TEXTO}.</p>
    </div>
  </div>
</header>"""


def rodape():
    colunas = []
    for idx, u in enumerate(UNIDADES):
        colunas.append(
            f'<ul class="foot__col"><li><span class="foot__kicker">0{idx + 1} • UNIDADE</span>{u["nome"]}</li>'
            f'<li>{u["rua"]}</li><li>{u["bairro"]}</li>'
            f'<li class="foot__coords">{u["coords"]}</li>'
            f'<li><a class="foot__maplink" href="{u["mapa"]}" rel="noopener">Traçar rota no mapa &rarr;</a></li></ul>'
        )
    colunas.append(
        '<ul class="foot__col"><li><span class="foot__kicker">03 • MAISON</span>Hairzenit</li>'
        '<li><a href="~/tratamentos/">Tratamentos &amp; Sinais</a></li><li><a href="~/equipe/">Corpo Clínico</a></li>'
        '<li><a href="~/equipe/larissa-pessoa/">Dra. Larissa Pessoa</a></li>'
        '<li><a href="~/consulta/">Modalidades de Consulta</a></li><li><a href="~/sobre/">A História da Marca</a></li>'
        '<li><a href="~/nova-clinica/">Sede Março 2027</a></li><li><a href="~/conteudo/">Journal &amp; Glossário</a></li></ul>'
    )
    colunas.append(
        f'<ul class="foot__col"><li><span class="foot__kicker">04 • CONCIERGE PRIVADO</span>Contato</li>'
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
      <a class="button button--gold" href="{wa()}"><span>Agendar Atendimento</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>
    </div>
    <div class="foot__cols grid">{''.join(colunas)}</div>
    <div class="foot__word" aria-hidden="true"><svg viewBox="0 0 1000 185"><text x="500" y="152" text-anchor="middle" font-family="Cormorant Garamond, Georgia, serif" font-size="188" font-weight="300" letter-spacing="18">HAIRZENIT</text></svg></div>
    <div class="foot__legal">
      <p>© 2026 Hairzenit, antiga Larissa Pessoa Tricologia Integrativa. As informações deste site têm caráter informativo e não substituem uma consulta clínica.</p>
      <p>{CREDITOS}</p>
    </div>
  </div>
</footer>
<a class="concierge-float" href="{wa()}" aria-label="Agendar consulta pelo WhatsApp">
  <span class="concierge-float__dot" aria-hidden="true"></span>
  <span class="concierge-float__label">Concierge WhatsApp</span>
</a>"""


def fecho(frase, pergunta="Qual consulta é para você?", retrato=("larissa-sentada", "Larissa Pessoa sorri sentada em uma poltrona clara")):
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
        <li><a class="link" href="~/consulta/">Comparar as consultas &rarr;</a></li>
      </ul>
      <p class="small">Copacabana e Cabo Frio, com hora marcada. WhatsApp {WHATS_TEXTO}.</p>
    </div>
  </div>
</section>"""


def momentos(titulo="Como é a consulta", id_="h-consulta"):
    colunas = "".join(
        f'<article class="moment" data-spotlight>'
        f'<div class="moment__meta"><span class="moment__num">ATO {ROMANOS[idx]}</span><span class="moment__tag">{tag}</span></div>'
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


def resultados():
    fotos = []
    for i, (img, nome, fato) in enumerate(RESULTADOS):
        cls = "shot shot--lifted" if i == 0 else "shot"
        sizes = "(max-width: 900px) 88vw, 420px"
        w, h = MANIFESTO[img]["g"]
        fotos.append(
            f'<figure class="{cls}" data-spotlight>'
            f'<div class="shot__header"><span>CASO CLÍNICO 0{i + 1}</span><span>{fato.upper()}</span></div>'
            f'{moldura(img, f"{nome}: fotos de antes e depois do tratamento", sizes, attrs=f"data-open data-lightbox style=--i:{i};--r:{w}/{h}")}'
            f"<figcaption><span>{nome}</span><span class=\"shot__zoom\">Ampliar registro &#8599;</span></figcaption></figure>"
        )
    return f"""
<section class="run wrap" aria-labelledby="h-resultados">
  <div class="grid">
    <div class="run__aside">
      <span class="kicker" data-reveal><span class="kicker__dot"></span> PORTFÓLIO CLÍNICO</span>
      <h2 id="h-resultados" data-reveal>Resultados documentados</h2>
      <p class="run__lead" data-reveal>Registros padronizados sob o mesmo ângulo e iluminação, demonstrando a recuperação de cobertura e densidade sem intervenção cirúrgica.</p>
      <a class="button button--shimmer" href="{wa()}"><span>Agendar uma avaliação</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>
      <p class="run__note">Pacientes atendidos pela equipe, fotografados de cima, antes e depois do tratamento. Os resultados variam de pessoa para pessoa.</p>
    </div>
    <div class="run__track" tabindex="0" aria-label="Fotos de antes e depois, role para o lado">{''.join(fotos)}</div>
  </div>
</section>"""


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


def grupos_ciencia():
    arts = [f'<a href="https://doi.org/{a["doi"]}" rel="noopener">{a["curto"]} &#8599;</a>' for a in ARTIGOS]
    return [
        ["Equipe", '<a href="~/equipe/larissa-pessoa/">Larissa Pessoa, fundadora</a>', '<a href="~/equipe/#thaina">Thaina Candido de Souza</a>', '<a href="~/equipe/#julia">Júlia</a>'],
        ["Publicado em", "Brazilian Journal of Hair Health, 2025"] + arts,
        ["Coautoria", "Lara Junqueira, Faculdade de Farmácia da UFRJ"],
        ["Tecnologias", "Tricoscopia digital", "Laser e LED capilar", "MMP", "Microinfusão de ativos", "Mesoject"],
        ["Atendimento", "Mulheres e homens", "Copacabana, Rio de Janeiro", "Novo Portinho, Cabo Frio"],
    ]


def reunidas(titulo, texto, link, fotos, id_="h-reunidas"):
    itens = "".join(
        f'<li class="gather__item" data-spotlight>{moldura(img, alt, "(max-width: 900px) 45vw, 260px", attrs=f"data-open data-lightbox style=--i:{i}")}</li>'
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
    <span class="kicker" data-load style="--d:120ms"><span class="kicker__dot"></span> HAIRZENIT • ALTA TRICOLOGIA</span>
    <h1 id="{id_}" class="lines">{spans}</h1>
    <div class="phero__text">
      <p class="lead" data-load style="--d:320ms">{lead}</p>
      {f'<p data-load style="--d:400ms">{texto}</p>' if texto else ''}
      <div class="actions" data-load style="--d:480ms">{acoes}</div>
    </div>
  </div>
  <div class="phero__visuals">
    <figure class="phero__tall">{moldura(alto[0], alto[1], "(max-width: 900px) 78vw, 34vw", attrs="data-shutter", prioridade=True)}</figure>
    <figure class="phero__small">{moldura(quadrado[0], quadrado[1], "(max-width: 900px) 45vw, 18vw", attrs="data-load style=--d:580ms")}</figure>
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
ORG_ID = SITE + "/#hairzenit"
LARISSA_ID = SITE + "/equipe/larissa-pessoa/#larissa"
THAINA_ID = SITE + "/equipe/#thaina"
JULIA_ID = SITE + "/equipe/#julia"


def endereco(u):
    return {"@type": "PostalAddress", "streetAddress": u["rua"], "addressLocality": u["cidade"], "addressRegion": "RJ", "addressCountry": "BR"}


def schema_org():
    return {
        "@type": "MedicalClinic",
        "@id": ORG_ID,
        "name": "Hairzenit",
        "alternateName": ["Larissa Pessoa Tricologia Integrativa", "Dra. Larissa Pessoa Tricologia", "Clínica Larissa Pessoa"],
        "description": "Clínica de tricologia especializada em queda de cabelo, calvície e perda de densidade capilar, fundada por Larissa Pessoa. Nova clínica em construção, com inauguração prevista para março de 2027.",
        "url": SITE + "/",
        "logo": SITE + "/icone-512.png",
        "image": SITE + "/assets/img/og-hairzenit.jpg",
        "telephone": "+55-21-97278-0789",
        "email": EMAIL,
        "address": endereco(UNIDADES[0]),
        "areaServed": ["Rio de Janeiro", "Cabo Frio", "Região dos Lagos"],
        "founder": {"@id": LARISSA_ID},
        "employee": [{"@id": LARISSA_ID}, {"@id": THAINA_ID}, {"@id": JULIA_ID}],
        "knowsAbout": ["Tricologia", "Queda de cabelo", "Calvície feminina", "Calvície masculina", "Alopecia androgenética", "Afinamento dos fios", "Perda de densidade capilar", "Tricoscopia"],
        "sameAs": [INSTAGRAM, SITE_ANTIGO],
        "department": [
            {"@type": "MedicalClinic", "name": f"Hairzenit {u['nome']}", "address": endereco(u), "telephone": "+55-21-97278-0789",
             "geo": {"@type": "GeoCoordinates", "latitude": u["lat"], "longitude": u["lon"]}, "hasMap": u["mapa"]}
            for u in UNIDADES
        ],
    }


def schema_larissa():
    return {
        "@type": "Person",
        "@id": LARISSA_ID,
        "name": "Larissa Pessoa",
        "alternateName": ["Dra. Larissa Pessoa", "Larissa Mota Barros Pessoa"],
        "jobTitle": "Fundadora, CEO e tricologista",
        "description": "Tricologista especializada em queda de cabelo e calvície, fundadora e CEO da Hairzenit.",
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
            "sameAs": "https://doi.org/" + a["doi"],
            "url": a["url"],
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


def pagina(caminho, titulo, descricao, corpo, ativo=None, schema=None, imagem="og-hairzenit", tipo="website"):
    profundidade = caminho.strip("/").count("/") + 1 if caminho != "/" else 0
    pre = "../" * profundidade
    grafo = [schema_org()] + (schema or [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, separators=(",", ":"))
    url = SITE + caminho
    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{tipo}">
<meta property="og:site_name" content="Hairzenit">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/{imagem}.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#120F0D">
<link rel="icon" href="~/favicon.svg" type="image/svg+xml">
<link rel="icon" href="~/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="~/apple-touch-icon.png">
<link rel="manifest" href="~/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap">
<link rel="stylesheet" href="~/assets/css/site.css">
<script>document.documentElement.classList.add('js')</script>
<script type="application/ld+json">{ld}</script>
</head>
<body>
{cabecalho(ativo)}
<main id="conteudo">
{corpo}
</main>
{rodape()}
<script src="~/assets/js/site.js" defer></script>
</body>
</html>
"""
    doc = doc.replace('href="~/"', f'href="{pre or "./"}"').replace("~/", pre)
    destino = SAIDA / caminho.strip("/") / "index.html" if caminho != "/" else SAIDA / "index.html"
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
    fatos = [("Fundadora", "Larissa Pessoa"), ("Especialidade", "Queda e calvície"), ("Atendimento", "Copacabana e Cabo Frio"), ("Nova clínica", "Março de 2027")]
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
      <p class="hero__lead" data-load style="--d:320ms">A Hairzenit é a clínica de tricologia fundada por Larissa Pessoa para tratar queda, calvície e perda de densidade capilar.</p>
      <p class="hero__sub" data-load style="--d:400ms"><strong>Uma nova clínica está sendo construída.</strong> Enquanto isso, nossa equipe segue atendendo em Copacabana e Cabo Frio.</p>
      <div class="actions" data-load style="--d:480ms">
        <a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>
        <a class="link" href="~/consulta/">As duas consultas &rarr;</a>
      </div>
      <dl class="hero__metrics" data-load style="--d:560ms">
        <div><dt>Diagnóstico</dt><dd>Tricoscopia 200&times;</dd></div>
        <div><dt>Pesquisa</dt><dd>Publicações BJHH '25</dd></div>
        <div><dt>Unidades</dt><dd>Copacabana &amp; Cabo Frio</dd></div>
      </dl>
    </div>
    <div class="hero__stage">
      <figure class="hero__tall">
        {moldura("larissa-poltrona", "Larissa Pessoa, de terno claro, sentada em uma poltrona", "(max-width: 900px) 84vw, 34vw", attrs="data-shutter", prioridade=True)}
        <figcaption>Larissa Pessoa, fundadora e CEO da Hairzenit</figcaption>
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
        <a class="hero__note" href="~/nova-clinica/" data-countdown="{INAUGURACAO}">
          <span class="hero__note-kicker">NOVA SEDE • 2027</span>
          <span class="hero__days" data-days>Março</span>
          <span class="hero__unit" data-unit>de 2027</span>
          <span class="link">A nova clínica &rarr;</span>
        </a>
      </div>
    </div>
  </div>
</section>

<section class="pano" aria-labelledby="h-zenite">
  <div class="wrap">
    <div class="pano__header grid">
      <div class="pano__title-col">
        <span class="kicker kicker--gold" data-reveal><span class="kicker__dot"></span> O PONTO MAIS ALTO DO DIAGNÓSTICO</span>
        <h2 id="h-zenite" class="display" data-reveal>Vista de cima, <em>fio a fio</em></h2>
      </div>
      <div class="pano__captions">
        <p data-reveal style="--i:1">Hairzenit vem de zênite, o ponto mais alto. É de cima que a tricologia examina o couro cabeludo: a risca, a coroa e a densidade de uma só vez.</p>
        <p data-reveal style="--i:2">Toda consulta começa assim, com tricoscopia digital que amplia os fios em até 200 vezes.</p>
      </div>
    </div>
    <figure class="pano__image" data-open data-lightbox>
      <div class="pano__hud" aria-hidden="true"><span>TRICOSCOPIA DIGITAL • 200&times;</span><span>MAPEAMENTO FOLICULAR NÃO INVASIVO</span></div>
      {pic("tela-tricoscopia", "Fios do couro cabeludo ampliados na tela durante uma tricoscopia", "100vw", prioridade=True)}
    </figure>
  </div>
</section>

<section class="signs wrap" aria-labelledby="h-sinais">
  <div class="signs__header">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> ATLAS DE DIAGNÓSTICO INTERATIVO</span>
    <h2 id="h-sinais" class="head" data-reveal><span class="indent">Comece pelo que você</span> <em>percebe no espelho</em></h2>
  </div>
  <div class="signs__body grid">
    <div class="signs__map zmap" data-on="calvicie-masculina" data-reveal data-spotlight>
      <div class="zmap__topbar"><span>VISTA DO ZÊNITE</span><span>SELECIONE UMA REGIÃO</span></div>
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
      <span class="kicker" data-reveal><span class="kicker__dot"></span> A TRAJETÓRIA DA MARCA</span>
      <h2 id="h-nasce" class="head" data-reveal>Por que a Hairzenit nasce</h2>
      <p class="mosaic__lead lead" data-reveal>Depois de anos atendendo pacientes com queda e calvície, Larissa Pessoa decidiu transformar sua experiência em uma clínica especializada, com equipe, método e estrutura dedicados à saúde capilar.</p>
    </div>
    <figure class="mosaic__photo">
      {moldura("larissa-rosa", "Larissa Pessoa de vestido rosé em uma sala clara", "(max-width: 900px) 100vw, 58vw")}
      <div class="mosaic__paper" data-spotlight>
        <span class="kicker"><span class="kicker__dot"></span> EMPATIA CLÍNICA</span>
        <p>Larissa já passou pela queda de cabelo e conhece o impacto dela na autoestima. Essa experiência orienta o jeito como cada paciente é recebido. <a class="link" href="~/sobre/">A história da marca &rarr;</a></p>
      </div>
    </figure>
    <div class="mosaic__side" data-reveal style="--i:2">
      <div class="mosaic__tile" data-spotlight>
        <div class="mosaic__tile-bar"><span>CARTA COSTEIRA • RJ</span><span>02 UNIDADES ATIVAS</span></div>
        {mapa_litoral()}
      </div>
      <dl class="mosaic__facts">{dl}</dl>
    </div>
  </div>
</section>

{momentos()}

{resultados()}

{nomes("Ciência e método", grupos_ciencia(), "h-ciencia")}

{reunidas("A nova Hairzenit chega em março de 2027", "Uma clínica construída para a saúde capilar. Enquanto a obra avança, seguimos atendendo em Copacabana e Cabo Frio.", '<a class="button button--gold" href="~/nova-clinica/"><span>Acompanhe a obra</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>', [
        ("microinfusao", "Aplicação de ativos ao longo da risca do cabelo"),
        ("tela-tricoscopia-retrato", "Fios ampliados na tela da tricoscopia"),
        ("laser-led", "Capacete de laser e LED sobre a cabeça de uma paciente"),
        ("tricoscopio-retrato", "Tricoscópio apoiado no couro cabeludo"),
        ("larissa-sentada", "Larissa Pessoa sentada em uma poltrona clara"),
        ("mesoject-retrato", "Caneta do Mesoject sobre o couro cabeludo"),
    ])}

{fecho("Duas formas de consulta: com a equipe Hairzenit ou com Larissa Pessoa.")}
"""
    schema = [
        {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Hairzenit", "alternateName": "Larissa Pessoa Tricologia", "inLanguage": "pt-BR", "publisher": {"@id": ORG_ID}},
        schema_larissa(),
    ]
    pagina("/", "Hairzenit | Especialistas em queda, calvície e perda de densidade capilar",
           "Hairzenit é a clínica de tricologia fundada por Larissa Pessoa, especializada em queda de cabelo, calvície e perda de densidade capilar. Atendimento em Copacabana e Cabo Frio.",
           corpo, schema=schema)


def problema(p):
    trat = "".join(f'<div class="treat-step" data-spotlight><h3>{a}</h3><p>{b}</p></div>' for a, b in p["tratamentos"])
    if p["slug"] == "calvicie-feminina":
        trat += f'<p class="treat-study"><a class="link" href="https://doi.org/{ARTIGOS[1]["doi"]}" rel="noopener">Ler o estudo de caso publicado no Brazilian Journal of Hair Health &rarr;</a></p>'
    acoes = f'<a class="button button--shimmer" href="{wa(MSG_PADRAO)}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="#h-faq">Perguntas frequentes</a>'
    corpo = (
        phero(p["nome"], p["lead"], None, p["alto"], p["quadrado"], acoes)
        + tabela_sinais(["Quando procurar", "uma avaliação"], p["sinais"], p["lateral"])
        + definicoes("Por que acontece", "A mesma aparência pode ter causas diferentes, e cada causa pede um tratamento. Estas são as mais comuns.", p["causas"], p["causas_pic"])
        + dividida("Como tratamos", p["trat_pic"], f"<p class=\"lead\">O plano parte do diagnóstico, nunca de um pacote pronto. Os tratamentos da Hairzenit são clínicos e sem cirurgia.</p><div class=\"treat-grid\">{trat}</div>", "h-trat")
        + faixa(
            "Tudo começa pela tricoscopia",
            "<p>Na consulta, o couro cabeludo é examinado com ampliação de até 200 vezes. Com a história clínica e, se necessário, exames, a tricologista define a causa e monta o plano: em casa, no consultório ou nos dois.</p>"
            "<p>Você pode ser atendida pela equipe Hairzenit ou por Larissa Pessoa, fundadora da clínica.</p>",
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
        migalhas([("Hairzenit", "/"), ("Tratamentos", "/tratamentos/"), (p["nome"], f"/{p['slug']}/")]),
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
            "<p>Os tratamentos da Hairzenit são clínicos: recuperam e preservam o seu próprio cabelo, sem cirurgia. Em casa, no consultório ou nos dois, com acompanhamento a cada etapa.</p>"
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
        migalhas([("Hairzenit", "/"), ("Tratamentos", "/tratamentos/")]),
        schema_larissa(),
    ]
    pagina("/tratamentos/", "Tratamentos para queda de cabelo e calvície no Rio de Janeiro | Hairzenit",
           "Tratamentos sem cirurgia para queda de cabelo, calvície feminina e masculina, couro cabeludo aparente, afinamento dos fios e perda de densidade. Hairzenit, Rio de Janeiro e Cabo Frio.",
           corpo, ativo="tratamentos", schema=schema)


def membro(id_, nome, texto, itens, i):
    """Uma tricologista da equipe. Quando houver retrato em MANIFESTO com o mesmo id, ele entra no topo."""
    retrato = moldura(id_, f"Retrato de {nome}", "(max-width: 900px) 100vw, 40vw") if id_ in MANIFESTO else ""
    iniciais = "".join(p[0] for p in nome.split()[:2]).upper()
    monograma = "" if retrato else f'<div class="member__monogram" aria-hidden="true"><span>{iniciais}</span></div>'
    lista = "".join(f"<li>{x}</li>" for x in itens)
    return (
        f'<article class="member" id="{id_}" data-spotlight data-reveal style="--i:{i}">{retrato}{monograma}'
        f'<span class="kicker"><span class="kicker__dot"></span> CORPO CLÍNICO HAIRZENIT</span>'
        f'<h3>{nome}</h3>'
        f'<p class="member__role">Tricologista Hairzenit</p><p>{texto}</p><ul class="member__list">{lista}</ul></article>'
    )


def equipe():
    acoes = f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/consulta/">As duas consultas &rarr;</a>'
    corpo = (
        phero("Equipe Hairzenit", "Três tricologistas, um mesmo método. A Hairzenit nasce como clínica, com equipe própria e uma fundadora presente.", None,
              ("larissa-blazer", "Larissa Pessoa de blazer branco, com a mão no rosto"), ("tricoscopio", "Tricoscópio digital apoiado no couro cabeludo"), acoes)
        + f"""
<section class="founder wrap grid" aria-labelledby="h-larissa" id="larissa">
  <figure class="founder__pic">{moldura("larissa-poltrona", "Larissa Pessoa sentada em uma poltrona clara", "(max-width: 900px) 100vw, 40vw")}</figure>
  <div class="founder__text" data-reveal>
    <span class="kicker"><span class="kicker__dot"></span> DIREÇÃO CLÍNICA &amp; FUNDAÇÃO</span>
    <h2 id="h-larissa">Larissa Pessoa</h2>
    <p class="founder__role">Fundadora e CEO da Hairzenit. Tricologista.</p>
    <p>Larissa construiu sua trajetória no tratamento da queda de cabelo e da calvície, primeiro com a clínica que levava o seu nome, Larissa Pessoa Tricologia Integrativa, em Copacabana e Cabo Frio. Hoje dirige a Hairzenit e segue atendendo pacientes.</p>
    <p>É autora, com a equipe, de dois estudos de caso sobre alopecia androgenética publicados no Brazilian Journal of Hair Health.</p>
    <div class="actions"><a class="button button--shimmer" href="{wa(MSG_LARISSA)}"><span>Consulta com Larissa</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/equipe/larissa-pessoa/">A trajetória de Larissa &rarr;</a></div>
  </div>
</section>

<section class="pair wrap grid" aria-labelledby="h-tricologistas">
  <div class="pair__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> ESPECIALISTAS</span>
    <h2 id="h-tricologistas" data-reveal>Tricologistas Hairzenit</h2>
  </div>
  {membro("thaina", "Thaina Candido de Souza", "Coautora, com Larissa Pessoa, dos dois estudos de caso sobre alopecia androgenética publicados pela clínica em 2025. Conduz a Consulta Hairzenit para pacientes com queda, calvície e perda de densidade.", ["Consulta Hairzenit", "Estudos publicados no Brazilian Journal of Hair Health"], 0)}
  {membro("julia", "Júlia", "Conduz a Consulta Hairzenit com o protocolo completo da clínica: história clínica, tricoscopia, exames quando necessários e um plano de tratamento acompanhado de perto.", ["Consulta Hairzenit", "Queda, calvície e perda de densidade"], 1)}
</section>
"""
        + dividida(
            "Um método, três profissionais",
            ("tela-tricoscopia-retrato", "Imagem ampliada dos fios na tela durante a tricoscopia"),
            "<p class=\"lead\">Na Hairzenit, a consulta não depende de quem está na agenda. O método é o mesmo para todas as tricologistas.</p>"
            "<div class=\"treat-grid\">"
            "<div class=\"treat-step\" data-spotlight><h3>A mesma avaliação</h3><p>História clínica, tricoscopia com ampliação de até 200 vezes e exames complementares quando a causa pede investigação.</p></div>"
            "<div class=\"treat-step\" data-spotlight><h3>Os mesmos protocolos</h3><p>Planos de tratamento construídos a partir da experiência clínica de Larissa Pessoa e revisados em equipe nos casos mais complexos.</p></div>"
            "<div class=\"treat-step\" data-spotlight><h3>O mesmo acompanhamento</h3><p>Reavaliações com fotos padronizadas, para comparar a evolução e ajustar o plano a cada etapa.</p></div>"
            "</div>",
            "h-metodo",
        )
        + nomes("Publicações", [["Brazilian Journal of Hair Health, 2025"] + [f'<a href="https://doi.org/{a["doi"]}" rel="noopener">{a["curto"]} &#8599;</a>' for a in ARTIGOS],
                                 ["Autoras", "Larissa Mota Barros Pessoa", "Thaina Candido de Souza", "Lara Junqueira, UFRJ"]], "h-publicacoes")
        + fecho("Consulta Hairzenit ou Consulta com Larissa Pessoa: o método é o mesmo.", "Com quem você quer ser atendido?")
    )
    schema = [
        schema_larissa(),
        {"@type": "Person", "@id": THAINA_ID, "name": "Thaina Candido de Souza", "jobTitle": "Tricologista", "worksFor": {"@id": ORG_ID}, "url": SITE + "/equipe/#thaina"},
        {"@type": "Person", "@id": JULIA_ID, "name": "Júlia", "jobTitle": "Tricologista", "worksFor": {"@id": ORG_ID}, "url": SITE + "/equipe/#julia"},
        migalhas([("Hairzenit", "/"), ("Equipe", "/equipe/")]),
    ] + schema_artigos()
    pagina("/equipe/", "Equipe Hairzenit: Larissa Pessoa, Thaina Candido de Souza e Júlia",
           "Conheça a equipe da Hairzenit: Larissa Pessoa, fundadora, CEO e tricologista, e as tricologistas Thaina Candido de Souza e Júlia. Um mesmo método de avaliação e tratamento.",
           corpo, ativo="equipe", schema=schema)


def larissa():
    acoes = f'<a class="button button--shimmer" href="{wa(MSG_LARISSA)}"><span>Agendar com Larissa</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/consulta/">As duas consultas &rarr;</a>'
    arts = "".join(
        f'<div class="treat-step" data-spotlight><h3>{a["titulo"]}</h3><p>{", ".join(a["autores"])}. Brazilian Journal of Hair Health, v. 2, n. 1, 2025. '
        f'<a class="link" href="https://doi.org/{a["doi"]}" rel="noopener">doi.org/{a["doi"]} &#8599;</a></p></div>'
        for a in ARTIGOS
    )
    corpo = (
        phero("Larissa Pessoa", "Fundadora e CEO da Hairzenit. Tricologista especializada em queda de cabelo e calvície.", None,
              ("larissa-blazer", "Larissa Pessoa de blazer branco, com a mão no rosto"), ("larissa-rosa-retrato", "Retrato de Larissa Pessoa de vestido rosé"), acoes)
        + dividida(
            "Da clínica com o seu nome à Hairzenit",
            ("larissa-sentada", "Larissa Pessoa sorri sentada em uma poltrona clara"),
            "<p class=\"lead\">Por anos, a clínica levou o nome dela: Larissa Pessoa Tricologia Integrativa, em Copacabana e Cabo Frio.</p>"
            "<p>O consultório cresceu, a equipe também, e o método que Larissa desenvolveu passou a ser conduzido por outras tricologistas. A Hairzenit é a forma desse crescimento: uma clínica com estrutura, equipe e nome próprios, fundada e dirigida por ela.</p>"
            "<p>Quem procura por Larissa Pessoa continua encontrando Larissa Pessoa. Ela segue atendendo, agora dentro da Hairzenit, na Consulta com Larissa Pessoa.</p>",
            "h-trajetoria",
        )
        + faixa(
            "Uma história com a queda",
            "<p>Larissa já passou pela queda de cabelo. Conhece de perto o efeito dela na autoestima, e é isso que orienta o jeito como cada consulta é conduzida: tempo para ouvir, explicação clara de cada achado e acompanhamento próximo.</p>"
            "<p>É também o que explica a escolha de trabalhar só com um assunto. Queda e calvície, em mulheres e homens, sem cirurgia.</p>",
            ("larissa-rosa", "Larissa Pessoa de vestido rosé em uma sala clara"),
            f'<a class="button button--gold" href="{wa(MSG_LARISSA)}"><span>Agendar com Larissa</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>',
            "h-historia",
        )
        + dividida("Publicações", ("cowper-1698", "Gravura de 1698 com cortes de pele e folículos capilares ampliados"),
                   "<p class=\"lead\">Dois estudos de caso sobre alopecia androgenética, escritos com a equipe da clínica e a Faculdade de Farmácia da UFRJ.</p><div class=\"treat-grid\">" + arts + "</div>",
                   "h-publicacoes", inverte=True)
        + fecho("A Consulta com Larissa Pessoa tem agenda própria e valor diferenciado.", "Quer ser atendido por Larissa?", ("larissa-rosa-retrato", "Retrato de Larissa Pessoa de vestido rosé"))
    )
    schema = [schema_larissa(), {"@type": "ProfilePage", "url": SITE + "/equipe/larissa-pessoa/", "mainEntity": {"@id": LARISSA_ID}},
              migalhas([("Hairzenit", "/"), ("Equipe", "/equipe/"), ("Larissa Pessoa", "/equipe/larissa-pessoa/")])] + schema_artigos()
    pagina("/equipe/larissa-pessoa/", "Larissa Pessoa, fundadora da Hairzenit e tricologista no Rio de Janeiro",
           "Larissa Pessoa é tricologista, fundadora e CEO da Hairzenit, clínica especializada em queda de cabelo e calvície no Rio de Janeiro. Antes, Larissa Pessoa Tricologia Integrativa.",
           corpo, ativo="equipe", schema=schema, imagem="larissa-blazer", tipo="profile")


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
    equipe_ = caminho("way--team", "CORPO CLÍNICO HAIRZENIT", "Consulta Hairzenit", "Conduzida por uma tricologista da equipe, com o protocolo completo da clínica.",
                      ("tricoscopio-retrato", "Tricoscópio digital apoiado no couro cabeludo durante a avaliação"),
                      [("Quem conduz", "Thaina Candido de Souza ou Júlia, tricologistas Hairzenit")] + comum + [("Valor", "Informado no agendamento")],
                      f'<a class="button button--shimmer" href="{wa(MSG_EQUIPE)}"><span>Agendar Consulta Hairzenit</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>')
    fundadora = caminho("way--founder", "SIGNATURE • COM A FUNDADORA", "Consulta com Larissa Pessoa", "Conduzida pela fundadora da Hairzenit, para quem deseja ser acompanhado por ela.",
                        ("larissa-blazer", "Larissa Pessoa de blazer branco"),
                        [("Quem conduz", "Larissa Pessoa, fundadora e tricologista")] + comum + [("Valor", "Diferenciado, informado no agendamento")],
                        f'<a class="button button--gold" href="{wa(MSG_LARISSA)}"><span>Agendar com Larissa</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>')

    def escolha(nome, opcoes, marcada):
        return "".join(
            f'<label><input type="radio" name="{nome}" value="{e(o)}"{" checked" if o == marcada else ""}><span>{o}</span></label>' for o in opcoes
        )

    lugares = "".join(
        f'<div class="place" data-spotlight><span class="kicker"><span class="kicker__dot"></span> {u["coords"]}</span><h3>{u["nome"]}</h3><p>{u["rua"]}<br>{u["bairro"]}</p><a class="link" href="{u["mapa"]}" rel="noopener">Como chegar &rarr;</a></div>'
        for u in UNIDADES
    )
    acoes = f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="#h-modalidades">Comparar as modalidades &rarr;</a>'
    corpo = (
        phero("Consulta de tricologia", "Duas modalidades, um mesmo método. O que muda é quem conduz a sua consulta.", None,
              ("tela-tricoscopia-retrato", "Imagem ampliada dos fios na tela durante a tricoscopia"), ("larissa-sentada", "Larissa Pessoa sentada em uma poltrona clara"), acoes)
        + f"""
<section class="ways wrap grid" aria-labelledby="h-modalidades">
  <div class="ways__head">
    <span class="kicker" data-reveal><span class="kicker__dot"></span> MODALIDADES DE ATENDIMENTO</span>
    <h2 id="h-modalidades" data-reveal>Escolha como ser atendido</h2>
    <p class="ways__intro" data-reveal style="--i:1">As duas consultas seguem o mesmo protocolo de avaliação e o mesmo cuidado. A diferença está em quem conduz e na agenda.</p>
  </div>
  {equipe_}
  {fundadora}
</section>
"""
        + momentos("Como é a consulta", "h-etapas")
        + f"""
<section class="composer" aria-labelledby="h-mensagem">
  <div class="wrap grid">
    <div class="composer__head">
      <span class="kicker" data-reveal><span class="kicker__dot"></span> CONCIERGE DIGITAL</span>
      <h2 id="h-mensagem" data-reveal>Monte sua mensagem</h2>
      <p class="composer__intro" data-reveal style="--i:1">Escolha a consulta, a unidade e o que você está sentindo. A mensagem fica pronta para enviar pelo WhatsApp, e a equipe responde com os horários e o valor.</p>
    </div>
    <form class="composer__form" data-composer="{WHATS}" data-spotlight>
      <fieldset><legend>01 • Modalidade de Consulta</legend><div class="choices">{escolha("tipo", ["Consulta Hairzenit", "Consulta com Larissa Pessoa"], "Consulta Hairzenit")}</div></fieldset>
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
  <div class="places__list" data-reveal>{lugares}<div class="place place--dark" data-spotlight><span class="kicker kicker--gold"><span class="kicker__dot"></span> EXPANSÃO • 2027</span><h3>Março de 2027</h3><p>A nova Hairzenit abre as portas. Até lá, os atendimentos seguem nestes dois endereços.</p><a class="link" href="~/nova-clinica/">A nova clínica &rarr;</a></div></div>
</section>
"""
        + perguntas("Perguntas frequentes", [
            ("Qual a diferença entre as duas consultas?", "O método é o mesmo: história clínica, tricoscopia, exames quando necessários e plano de tratamento. Na Consulta com Larissa Pessoa, quem conduz é a fundadora, com agenda própria e valor diferenciado."),
            ("Quanto custa a consulta?", "Os valores das duas modalidades são informados no agendamento, pelo WhatsApp."),
            ("O tratamento começa na mesma consulta?", "A consulta é de avaliação e planejamento. O tratamento começa depois, em casa, no consultório ou nos dois, conforme o plano definido."),
            ("O que levar?", "Exames de sangue recentes, se você tiver, e a lista dos medicamentos e suplementos que usa."),
            ("Vocês atendem homens e mulheres?", "Sim. A Hairzenit trata queda e calvície em mulheres e homens."),
        ])
        + fecho("Agende pelo WhatsApp e receba os horários das duas consultas.", "Pronto para agendar?")
    )
    schema = [
        {"@type": "WebPage", "url": SITE + "/consulta/", "name": "Consulta de tricologia", "inLanguage": "pt-BR",
         "mainEntity": [
             {"@type": "Service", "name": "Consulta Hairzenit", "serviceType": "Consulta de tricologia", "provider": {"@id": ORG_ID}, "description": "Consulta conduzida por uma tricologista da equipe Hairzenit, com tricoscopia de até 200x e plano de tratamento."},
             {"@type": "Service", "name": "Consulta com Larissa Pessoa", "serviceType": "Consulta de tricologia", "provider": {"@id": LARISSA_ID}, "description": "Consulta conduzida pela fundadora da Hairzenit, com agenda própria e valor diferenciado."},
         ]},
        migalhas([("Hairzenit", "/"), ("Consulta", "/consulta/")]),
        schema_larissa(),
    ]
    pagina("/consulta/", "Consulta de tricologia no Rio de Janeiro: Hairzenit ou Larissa Pessoa",
           "Duas modalidades: Consulta Hairzenit, com a equipe, e Consulta com Larissa Pessoa, com valor diferenciado. Tricoscopia de até 200x, em Copacabana e Cabo Frio.",
           corpo, ativo="consulta", schema=schema)


def sobre():
    acoes = f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/nova-clinica/">A nova clínica &rarr;</a>'
    corpo = (
        phero("Sobre a Hairzenit", "Depois de anos atendendo pacientes com queda e calvície, Larissa Pessoa decidiu transformar sua experiência em uma clínica especializada.", None,
              ("larissa-rosa-retrato", "Retrato de Larissa Pessoa de vestido rosé"), ("tricoscopio", "Tricoscópio digital apoiado no couro cabeludo"), acoes)
        + dividida(
            "Por que a marca nasce",
            ("larissa-poltrona", "Larissa Pessoa sentada em uma poltrona clara"),
            "<p class=\"lead\">Durante anos, o consultório levou o nome de Larissa. E a pergunta que chegava a ele era quase sempre a mesma: vou ficar careca?</p>"
            "<p>Responder exigia tempo. Exigia examinar o couro cabeludo de perto, investigar a causa, montar um plano e acompanhar cada etapa, por meses. Exigia, cada vez mais, uma equipe.</p>"
            "<p>A Hairzenit é a resposta a essa demanda: uma clínica dedicada a um único assunto, a queda e a calvície, com equipe, método e estrutura para atender mais pessoas com o mesmo cuidado. Um método que não depende de uma pessoa só para existir, e uma fundadora que continua presente.</p>",
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
    <figure class="mosaic__photo">{moldura("tela-tricoscopia", "Fios ampliados na tela durante uma tricoscopia", "(max-width: 900px) 100vw, 58vw")}<div class="mosaic__paper" data-spotlight><span class="kicker"><span class="kicker__dot"></span> PERSPECTIVA SUPERIOR</span><p>Hairzenit junta as duas ideias: o cabelo visto do ponto mais alto, e uma clínica que trabalha para levar cada caso ao melhor resultado possível.</p></div></figure>
    <div class="mosaic__side zmap" data-on="couro-cabeludo-aparente" data-reveal style="--i:2" data-spotlight><div class="zmap__topbar"><span>ATLAS DO ZÊNITE</span><span>PERSPECTIVA 90°</span></div><div class="mosaic__tile" style="aspect-ratio:auto;padding:1.25rem 2rem;background:transparent">{mapa_zenite()}</div><p class="zmap__caption small">A cabeça vista do zênite: a frente no alto, a coroa embaixo.</p></div>
  </div>
</section>
"""
        + dividida(
            "O que muda e o que continua",
            None,
            "<div class=\"treat-grid\">"
            "<div class=\"treat-step\" data-spotlight><h3>Muda</h3><ul><li>O nome: Larissa Pessoa Tricologia Integrativa passa a se chamar Hairzenit.</li><li>A estrutura: uma nova clínica, em construção, com inauguração em março de 2027.</li><li>A equipe ganha nome e lugar: Thaina Candido de Souza e Júlia são tricologistas Hairzenit.</li></ul></div>"
            f"<div class=\"treat-step\" data-spotlight><h3>Continua</h3><ul><li>Os atendimentos em Copacabana e Cabo Frio, até a inauguração.</li><li>O WhatsApp {WHATS_TEXTO} e o Instagram {INSTAGRAM_TEXTO}.</li><li>O método de avaliação e tratamento, sem cirurgia.</li><li>Larissa Pessoa, que dirige a clínica e segue atendendo.</li></ul></div>"
            "</div>",
            "h-transicao",
        )
        + faixa(
            "Larissa Pessoa e a Hairzenit",
            "<p>Larissa Pessoa é fundadora e CEO da Hairzenit e segue como tricologista da clínica. Quem procurava por ela continua encontrando, agora dentro de uma estrutura maior.</p>",
            ("larissa-blazer", "Larissa Pessoa de blazer branco"),
            f'<a class="button button--gold" href="{wa(MSG_LARISSA)}"><span>Consulta com Larissa</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/equipe/larissa-pessoa/">A trajetória de Larissa &rarr;</a>',
            "h-fundadora",
        )
        + fecho("Mesma equipe, mesmos endereços, novo nome. Agende pelo WhatsApp.", "Vamos conversar?")
    )
    schema = [
        {"@type": "AboutPage", "url": SITE + "/sobre/", "name": "Sobre a Hairzenit", "inLanguage": "pt-BR", "mainEntity": {"@id": ORG_ID}},
        migalhas([("Hairzenit", "/"), ("Sobre", "/sobre/")]),
        schema_larissa(),
    ]
    pagina("/sobre/", "Sobre a Hairzenit: a clínica de tricologia fundada por Larissa Pessoa",
           "A Hairzenit nasce da experiência de Larissa Pessoa no tratamento de queda e calvície: uma clínica especializada, com equipe, método e estrutura dedicados à saúde capilar.",
           corpo, ativo="sobre", schema=schema)


def nova_clinica():
    acoes = f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="#h-diario">Diário de obra &rarr;</a>'
    entradas = [
        ("Outubro de 2026", "A marca Hairzenit é apresentada", "Larissa Pessoa Tricologia Integrativa passa a se chamar Hairzenit. Equipe, endereços e contatos continuam os mesmos.", "done"),
        ("Em andamento", "Obra da nova clínica", "A construção avança conforme o projeto arquitetônico. Cada etapa da obra entra neste diário.", "now"),
        ("Março de 2027", "Inauguração", "A nova Hairzenit abre as portas e os atendimentos passam para a nova sede.", "next"),
    ]
    log = "".join(
        f'<li data-state="{s}" data-spotlight data-reveal style="--i:{i}"><div class="log__meta"><span class="log__roman">{ROMANOS[i]}</span><p class="log__when">{q}</p></div><div><h3>{t}</h3><p>{d}</p></div></li>'
        for i, (q, t, d, s) in enumerate(entradas)
    )
    corpo = (
        phero("Nova clínica Hairzenit", "A nova Hairzenit chega em março de 2027.", "Uma clínica construída do zero para a saúde capilar. Enquanto a obra avança, nossa equipe segue atendendo em Copacabana e Cabo Frio.",
              ("larissa-rosa-retrato", "Retrato de Larissa Pessoa de vestido rosé"), ("mesoject", "Caneta do Mesoject sobre o couro cabeludo"), acoes)
        + f"""
<section class="count" aria-labelledby="h-marco" data-countdown="{INAUGURACAO}">
  <div class="wrap grid">
    <div class="count__copy">
      <span class="kicker kicker--gold" data-reveal><span class="kicker__dot"></span> NOVA SEDE • CONTAGEM REGRESSIVA</span>
      <h2 id="h-marco" data-reveal>Março de 2027</h2>
      <p data-reveal style="--i:1">É quando a Hairzenit passa a ter a sua própria casa: um espaço pensado a partir do atendimento em tricologia, da chegada do paciente à reavaliação.</p>
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
            ("larissa-sentada", "Larissa Pessoa sentada em uma poltrona clara"),
            ("laser-led", "Capacete de laser e LED sobre a cabeça de uma paciente"),
            ("tela-tricoscopia-retrato", "Fios ampliados na tela da tricoscopia"),
            ("analise-imagens", "Paciente revisa as imagens dos próprios fios"),
        ], "h-enquanto")
        + fecho("A obra não interrompe os atendimentos.", "Quer agendar agora?")
    )
    schema = [
        {"@type": "WebPage", "url": SITE + "/nova-clinica/", "name": "Nova clínica Hairzenit", "inLanguage": "pt-BR", "about": {"@id": ORG_ID}},
        {"@type": "Event", "name": "Inauguração da nova clínica Hairzenit", "startDate": INAUGURACAO, "eventStatus": "https://schema.org/EventScheduled",
         "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "organizer": {"@id": ORG_ID},
         "location": {"@type": "Place", "name": "Hairzenit", "address": {"@type": "PostalAddress", "addressLocality": "Rio de Janeiro", "addressRegion": "RJ", "addressCountry": "BR"}}},
        migalhas([("Hairzenit", "/"), ("Nova clínica", "/nova-clinica/")]),
    ]
    pagina("/nova-clinica/", "Nova clínica Hairzenit: inauguração em março de 2027",
           "A nova Hairzenit está em construção e chega em março de 2027. Acompanhe o projeto e a obra. Enquanto isso, a equipe segue atendendo em Copacabana e Cabo Frio.",
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
        phero(["Saúde capilar,", "explicada"], "Textos da equipe Hairzenit sobre queda, calvície e cuidados com o couro cabeludo, com fundamento clínico e linguagem direta.", None,
              ("escovando", "Mulher observa os fios enquanto escova o cabelo"), ("fio-na-mao", "Mulher segura entre os dedos um fio que caiu"), f'<a class="button button--shimmer" href="{wa()}"><span>Agendar consulta</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a>')
        + f"""
<section class="posts wrap grid" aria-labelledby="h-artigos">
  <h2 id="h-artigos" class="sr-only">Artigos</h2>
  <a class="post" href="~/conteudo/{a['slug']}/" data-reveal data-spotlight>
    {moldura("fio-na-mao", "Mulher segura entre os dedos um fio que caiu", "(max-width: 900px) 100vw, 44vw", attrs="")}
    <div class="post__text">
      <span class="kicker"><span class="kicker__dot"></span> ARTIGO EM DESTAQUE • JOURNAL</span>
      <h2>{a['titulo']}</h2>
      <p>{a['resumo']}</p>
      <p class="small">Por Larissa Pessoa • {a['data_texto']} • <span class="link">Ler artigo completo &rarr;</span></p>
    </div>
  </a>
</section>
"""
        + nomes("Publicações científicas", [["Brazilian Journal of Hair Health, 2025"] + [f'<a href="https://doi.org/{x["doi"]}" rel="noopener">{x["curto"]} &#8599;</a>' for x in ARTIGOS],
                                           ["Autoras", "Larissa Mota Barros Pessoa", "Thaina Candido de Souza", "Lara Junqueira, UFRJ"]], "h-cientificas")
        + definicoes("Glossário", "Os termos que aparecem na consulta e nos exames, explicados sem rodeios.", GLOSSARIO,
                     ("cowper-1698", "Gravura de 1698 com cortes de pele e folículos capilares ampliados"), "h-glossario")
        + indice("Guias por sinal", None, "h-guias")
        + fecho("Leu e se reconheceu em algum sinal? A avaliação mostra a causa.", "Quer uma avaliação?")
    )
    schema = [
        {"@type": "Blog", "url": SITE + "/conteudo/", "name": "Saúde capilar, explicada", "publisher": {"@id": ORG_ID}, "inLanguage": "pt-BR",
         "blogPost": [{"@type": "BlogPosting", "headline": a["titulo"], "url": SITE + f"/conteudo/{a['slug']}/"}]},
        migalhas([("Hairzenit", "/"), ("Conteúdo", "/conteudo/")]),
        schema_larissa(),
    ]
    pagina("/conteudo/", "Conteúdo sobre saúde capilar, queda e calvície | Hairzenit",
           "Textos da equipe Hairzenit sobre queda de cabelo, calvície e saúde do couro cabeludo, e os estudos de caso publicados pela clínica no Brazilian Journal of Hair Health.",
           corpo, ativo="conteudo", schema=schema)

    texto = []
    for tag, t in a["corpo"]:
        texto.append(f"<{tag} data-reveal>{t}</{tag}>")
    corpo = f"""
<article class="article wrap grid" aria-labelledby="titulo">
  <div class="article__header">
    <span class="kicker" data-load style="--d:100ms"><span class="kicker__dot"></span> JOURNAL CLÍNICO • HAIRZENIT</span>
    <h1 id="titulo" class="lines"><span class="line"><span data-line>{a['titulo']}</span></span></h1>
    <p class="article__meta" data-load style="--d:300ms">Por <a href="~/equipe/larissa-pessoa/">Larissa Pessoa</a>, fundadora da Hairzenit • Publicado em {a['data_texto']}.</p>
  </div>
  <figure class="article__pic">{moldura("escova-fios", "Fios presos nas cerdas de uma escova", "100vw", attrs="data-shutter", prioridade=True)}</figure>
  <div class="article__body"><p class="lead">{a['resumo']}</p>{''.join(texto)}</div>
  <aside class="article__aside" aria-label="Sobre a autora" data-reveal data-spotlight>
    <span class="kicker"><span class="kicker__dot"></span> AUTORA</span>
    {moldura("larissa-sentada", "Larissa Pessoa sentada em uma poltrona clara", "(max-width: 900px) 60vw, 22vw")}
    <p>Larissa Pessoa é tricologista, fundadora e CEO da Hairzenit. <a class="link" href="~/equipe/larissa-pessoa/">Conheça a trajetória &rarr;</a></p>
  </aside>
</article>
""" + indice("Guias por sinal", None, "h-guias") + fecho("Se a sua queda passou do normal, a avaliação mostra a causa.", "Quer uma avaliação?")
    schema = [
        {"@type": "BlogPosting", "headline": a["titulo"], "description": a["resumo"], "datePublished": a["data"], "dateModified": ATUALIZADO,
         "author": {"@id": LARISSA_ID}, "publisher": {"@id": ORG_ID}, "image": SITE + "/assets/img/escova-fios.jpg",
         "mainEntityOfPage": SITE + f"/conteudo/{a['slug']}/", "inLanguage": "pt-BR"},
        migalhas([("Hairzenit", "/"), ("Conteúdo", "/conteudo/"), (a["titulo"], f"/conteudo/{a['slug']}/")]),
        schema_larissa(),
    ]
    pagina(f"/conteudo/{a['slug']}/", f"{a['titulo']} | Hairzenit", a["resumo"], corpo, ativo="conteudo", schema=schema, imagem="escova-fios", tipo="article")


def nao_encontrada():
    corpo = (
        phero("Página não encontrada", "O endereço mudou ou não existe. As páginas da antiga Larissa Pessoa Tricologia agora fazem parte da Hairzenit.", None,
              ("larissa-poltrona", "Larissa Pessoa sentada em uma poltrona clara"), ("tricoscopio", "Tricoscópio digital apoiado no couro cabeludo"),
              f'<a class="button button--shimmer" href="~/"><span>Ir para o início</span><span class="button__arrow" aria-hidden="true">&rarr;</span></a><a class="link" href="~/tratamentos/">Tratamentos &rarr;</a>')
        + indice("Talvez você procure", None, "h-talvez")
    )
    pagina("/404/", "Página não encontrada | Hairzenit", "Esta página não existe. Veja os tratamentos da Hairzenit.", corpo)
    # 404 na raiz com caminhos absolutos, para funcionar em qualquer profundidade
    doc = (SAIDA / "404" / "index.html").read_text(encoding="utf-8").replace('="../', '="/').replace("../", "/")
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
]


def apoio():
    favicon = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#120F0D"/>'
        '<circle cx="32" cy="32" r="26" fill="none" stroke="#C5A059" stroke-opacity="0.35" stroke-width="1.5"/>'
        '<circle cx="32" cy="20" r="5.5" fill="#C5A059"/><rect x="16" y="40" width="32" height="3" rx="1.5" fill="#FAF7F2"/></svg>'
    )
    (SAIDA / "favicon.svg").write_text(favicon)
    (SAIDA / "site.webmanifest").write_text(json.dumps({
        "name": "Hairzenit", "short_name": "Hairzenit", "lang": "pt-BR", "start_url": "/", "display": "browser",
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
    # Netlify / Cloudflare Pages
    (SAIDA / "_redirects").write_text("".join(f"{a} {b} 301\n{a}/ {b} 301\n" for a, b in REDIRECIONAMENTOS))
    # Vercel (dentro de site/ e na raiz do repositório)
    vercel_cfg = {
        "buildCommand": "npm run build",
        "outputDirectory": "site",
        "trailingSlash": True,
        "redirects": [{"source": a, "destination": b, "permanent": True} for a, b in REDIRECIONAMENTOS],
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


if __name__ == "__main__":
    main()
