"""Gera as imagens otimizadas do site a partir de fotos-originais/.

Uso (na raiz do projeto):  python3 tools/imagens.py
Requer Pillow. Cada entrada define o arquivo de origem, a proporção do recorte e o
ponto de foco vertical/horizontal (0 = topo/esquerda, 1 = base/direita).
Saída: site/assets/img/<nome>.jpg e <nome>-p.jpg, mais imagens.json com as dimensões.
"""
import site
import sys

sys.path.append(site.getusersitepackages())

import json
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "fotos-originais"
DESTINO = RAIZ / "site" / "assets" / "img"
PEDRA = (214, 208, 199)  # --field, fundo dos retratos recortados

# nome: (arquivo, proporção largura/altura, foco x, foco y, larguras)
IMAGENS = {
    # Larissa Pessoa
    "larissa-poltrona": ("ANA_4352.jpg", 3 / 4, 0.5, 0.45, (1400, 760)),
    "larissa-sentada": ("ANA_4383-2880w.jpg", 4 / 5, 0.5, 0.35, (1400, 760)),
    "larissa-blazer": ("ANA_4259---Editado.png", 3 / 4, 0.5, 0.2, (1400, 760)),
    "larissa-rosa": ("3f6c22a0-2d25-4d48-9b64-f95c2ea1b64f-5fc403d7-2880w.png", 16 / 10, 0.62, 0.4, (1600, 900)),
    "larissa-rosa-retrato": ("3f6c22a0-2d25-4d48-9b64-f95c2ea1b64f-5fc403d7-75adc9ca-07862fa0.png", 4 / 5, 0.5, 0.15, (1200, 640)),
    "og-hairzenit": ("3f6c22a0-2d25-4d48-9b64-f95c2ea1b64f-5fc403d7-2880w.png", 1200 / 630, 0.6, 0.4, (1200, 600)),
    # Clínica e procedimentos
    "tricoscopio": ("0A7A6778--281-29-2880w.png", 1, 0.5, 0.42, (1200, 640)),
    "tricoscopio-retrato": ("0A7A6778--281-29-2880w.png", 4 / 5, 0.5, 0.4, (1400, 760)),
    "tela-tricoscopia": ("_MG_8819-1920w.jpg", 21 / 9, 0.5, 0.33, (2000, 1000)),
    "tela-tricoscopia-retrato": ("_MG_8819-1920w.jpg", 4 / 5, 0.5, 0.35, (1400, 760)),
    "mesoject": ("_MG_8769-2880w.jpg", 16 / 10, 0.5, 0.45, (1800, 900)),
    "mesoject-retrato": ("_MG_8769-2880w.jpg", 4 / 5, 0.48, 0.5, (1200, 640)),
    "microinfusao": ("_MG_8762.jpg", 4 / 5, 0.5, 0.5, (1200, 640)),
    "laser-led": ("_MG_8825.jpg", 4 / 5, 0.5, 0.5, (1200, 640)),
    "analise-imagens": ("DSC_3925.jpg", 4 / 5, 0.5, 0.55, (1200, 640)),
    # Banco de imagens do site anterior
    "escovando": ("AdobeStock_377067790-1920w.jpeg", 16 / 10, 0.5, 0.5, (1600, 900)),
    "escova-fios": ("Tratamento-para-queda-de-cabelo-2880w.png", 16 / 10, 0.5, 0.5, (1600, 900)),
    "homem-entradas": ("Tratamento_para_calvicie-2880w.jpeg", 16 / 10, 0.5, 0.4, (1600, 900)),
    "homem-entradas-retrato": ("Tratamento_para_calvicie-2880w.jpeg", 4 / 5, 0.42, 0.4, (1200, 640)),
    "espelho": ("AdobeStock_486445543-2880w.png", 16 / 10, 0.5, 0.5, (1600, 900)),
    "espelho-retrato": ("AdobeStock_486445543-2880w.png", 4 / 5, 0.62, 0.5, (1200, 640)),
    "fio-na-mao": ("Especialista_em_tricologia_no_Rio_de_Janeiro_Quando_a_queda_de_cabelo_nao_e_normal.png", 3 / 2, 0.5, 0.5, (712, 600)),
    "textura-loira": ("AdobeStock_481109349-2880w.jpeg", 21 / 9, 0.5, 0.5, (1800, 900)),
    "textura-castanha": ("JsvcKabjSDqFp4kkOqxf_AdobeStock_306899500.v2.0000000-1920w.jpg", 21 / 9, 0.5, 0.5, (1800, 900)),
    # Acervo aberto (créditos em site/assets/img/creditos.json)
    "cowper-1698": ("acervo-aberto/the-anatomy-of-humane-bodies-skin-and.jpg", 3 / 4, 0.5, 0.45, (1100, 640)),
    "avenida-copacabana": ("acervo-aberto/avenida-nossa-senhora-de-copacabana-1.jpg", 4 / 5, 0.5, 0.5, (1000, 600)),
}

# Antes e depois (fotos de pacientes do site anterior, 1:1)
RESULTADOS = [
    "WhatsApp_Image_2025-11-05_at_16.33.39.jpeg",
    "WhatsApp_Image_2025-11-05_at_16.33.39_(2).jpeg",
    "WhatsApp_Image_2025-11-05_at_16.33.39_(3).jpeg",
    "WhatsApp_Image_2025-11-05_at_16.33.39_(4).jpeg",
    "WhatsApp_Image_2025-11-05_at_16.33.39_(5).jpeg",
    "WhatsApp_Image_2025-11-05_at_16.33.40_(1).jpeg",
    "WhatsApp_Image_2025-11-05_at_16.33.40_(2).jpeg",
]


def abrir(caminho):
    im = Image.open(caminho)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        fundo = Image.new("RGB", im.size, PEDRA)
        fundo.paste(im, mask=im.split()[-1])
        return fundo
    return im.convert("RGB")


def aparar(im):
    """Remove as faixas brancas em volta das montagens de antes e depois."""
    from PIL import ImageChops
    fundo = Image.new("RGB", im.size, (255, 255, 255))
    caixa = ImageChops.difference(im, fundo).convert("L").point(lambda v: 255 if v > 18 else 0).getbbox()
    return im.crop(caixa) if caixa else im


def recortar(im, proporcao, fx, fy):
    w, h = im.size
    if w / h > proporcao:
        nw, nh = round(h * proporcao), h
    else:
        nw, nh = w, round(w / proporcao)
    x = min(max(round(fx * w - nw / 2), 0), w - nw)
    y = min(max(round(fy * h - nh / 2), 0), h - nh)
    return im.crop((x, y, x + nw, y + nh))


MANIFESTO = {}


def salvar(im, nome, larguras):
    """Grava <nome>.jpg (grande) e <nome>-p.jpg (pequena) e anota as dimensões reais."""
    MANIFESTO[nome] = {}
    for sufixo, lw in zip(("", "-p"), larguras):
        lw = min(lw, im.width)
        out = im.resize((lw, round(im.height * lw / im.width)), Image.LANCZOS)
        out.save(DESTINO / f"{nome}{sufixo}.jpg", "JPEG", quality=80, optimize=True, progressive=True)
        MANIFESTO[nome]["g" if not sufixo else "p"] = list(out.size)


def icones():
    """Marca do zênite: um ponto acima da linha do horizonte."""
    from PIL import ImageDraw
    tinta, bronze, osso = (34, 28, 23), (201, 159, 104), (241, 240, 237)
    for lado, nome in ((32, "favicon-32.png"), (180, "apple-touch-icon.png"), (512, "icone-512.png")):
        escala = 8
        L = lado * escala
        im = Image.new("RGB", (L, L), tinta)
        d = ImageDraw.Draw(im)
        r = L * 0.094
        d.ellipse((L / 2 - r, L * 0.3125 - r, L / 2 + r, L * 0.3125 + r), fill=bronze)
        d.rectangle((L * 0.22, L * 0.625, L * 0.78, L * 0.6875), fill=osso)
        im.resize((lado, lado), Image.LANCZOS).save(RAIZ / "site" / nome)


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, (arquivo, prop, fx, fy, larguras) in IMAGENS.items():
        salvar(recortar(abrir(ORIGEM / arquivo), prop, fx, fy), nome, larguras)
    for i, arquivo in enumerate(RESULTADOS, 1):
        salvar(aparar(abrir(ORIGEM / arquivo)), f"resultado-{i}", (1000, 560))
    icones()
    (DESTINO / "imagens.json").write_text(json.dumps(MANIFESTO, indent=1))
    print("ok:", len(list(DESTINO.glob("*.jpg"))), "arquivos")


if __name__ == "__main__":
    main()
