#!/usr/bin/env python3
"""Checa o HTML gerado em site/. Rode depois de build.py.

Falha (código 1) em title/description duplicados, H1 ausente ou repetido,
hierarquia de heading quebrada, imagem sem alt, canonical/Open Graph/Twitter
incompletos, WhatsApp divergente, link interno quebrado ou placeholder.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "site"
LOCAIS = ("Copacabana", "Cabo Frio", "Rio de Janeiro", "Rio")
PLACEHOLDERS = re.compile(
    r"lorem ipsum|seu nome aqui|exemplo\.com|G-X{4,}|GTM-X{4,}|pixel id 123|FIXME",
    re.I,
)
# Marca oficial: Hairzenith. "hairzenit" sem o h final é a grafia antiga.
GRAFIA_ERRADA = re.compile(r"Hairzenit(?!h)|Hair\s+Zenith", re.I)


class Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.metas = {}
        self.properties = {}
        self.links = []
        self.hrefs = []
        self.imgs = []
        self.headings = []
        self.ids = []
        self.schemas = []
        self._buf = []
        self._capturando = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "title":
            self._capturando = "title"
            self._buf = []
        elif tag == "meta":
            if a.get("name"):
                self.metas[a["name"]] = a.get("content", "")
            if a.get("property"):
                self.properties[a["property"]] = a.get("content", "")
        elif tag == "link":
            self.links.append(a)
        elif tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        elif tag == "img":
            self.imgs.append(a)
        elif tag in {f"h{i}" for i in range(1, 7)}:
            self.headings.append(int(tag[1]))
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._capturando = "ld"
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "title" and self._capturando == "title":
            self.title = "".join(self._buf).strip()
            self._capturando = None
        elif tag == "script" and self._capturando == "ld":
            self.schemas.append("".join(self._buf))
            self._capturando = None

    def handle_data(self, data):
        if self._capturando:
            self._buf.append(data)


def paginas_html():
    arquivos = [SITE / "index.html", SITE / "404.html"]
    arquivos += sorted(p for p in SITE.rglob("index.html") if p != SITE / "index.html")
    return arquivos


def caminho_de(arquivo):
    rel = arquivo.relative_to(SITE).as_posix()
    if rel == "index.html":
        return "/"
    if rel == "404.html":
        return "/404.html"
    return "/" + rel[: -len("index.html")]


def destino_local(href, origem):
    if href.startswith("#"):
        return origem, href[1:]
    bruto = href.split("?", 1)[0]
    caminho, _, ancora = bruto.partition("#")
    if not caminho:
        return origem, ancora
    if caminho.endswith("/"):
        arquivo = SITE / caminho.strip("/") / "index.html"
    else:
        arquivo = SITE / caminho.lstrip("/")
    return arquivo, ancora


def main():
    erros = []
    vistos_titulo = {}
    vistos_desc = {}
    numeros_wa = set()

    if not (SITE / "robots.txt").is_file() or not (SITE / "sitemap.xml").is_file():
        erros.append("faltam robots.txt ou sitemap.xml")

    robots = (SITE / "robots.txt").read_text(encoding="utf-8") if (SITE / "robots.txt").is_file() else ""
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8") if (SITE / "sitemap.xml").is_file() else ""
    if "Sitemap:" not in robots:
        erros.append("robots.txt sem a linha Sitemap")
    if "/404" in sitemap:
        erros.append("sitemap inclui a página 404")
    for nome, texto in (("robots.txt", robots), ("sitemap.xml", sitemap)):
        erros.extend(f"{nome}: {msg}" for msg in dominios_proibidos(texto))

    for icone in ("favicon.svg", "favicon-32.png", "apple-touch-icon.png", "icone-512.png"):
        if not (SITE / icone).is_file():
            erros.append(f"ícone ausente: {icone}")

    for arquivo in paginas_html():
        html = arquivo.read_text(encoding="utf-8")
        rota = caminho_de(arquivo)
        parser = Pagina()
        parser.feed(html)
        noindex = "noindex" in parser.metas.get("robots", "").lower()
        rotulo = rota

        if PLACEHOLDERS.search(html):
            erros.append(f"{rotulo}: texto de placeholder")
        if GRAFIA_ERRADA.search(html):
            erros.append(f"{rotulo}: a marca no texto precisa ser Hairzenith, sem espaço")

        if not parser.title:
            erros.append(f"{rotulo}: sem title")
        elif parser.title in vistos_titulo:
            erros.append(f"{rotulo}: title repetido com {vistos_titulo[parser.title]}")
        else:
            vistos_titulo[parser.title] = rotulo
        if parser.title and len(parser.title) > 70:
            erros.append(f"{rotulo}: title com {len(parser.title)} caracteres (máx. 70)")

        desc = parser.metas.get("description", "")
        if not desc:
            erros.append(f"{rotulo}: sem meta description")
        elif desc in vistos_desc:
            erros.append(f"{rotulo}: description repetida com {vistos_desc[desc]}")
        else:
            vistos_desc[desc] = rotulo
        if desc and not noindex and (len(desc) < 70 or len(desc) > 170):
            erros.append(f"{rotulo}: description com {len(desc)} caracteres")

        if not noindex:
            for campo, texto in (("title", parser.title), ("description", desc)):
                if texto and not any(t in texto for t in LOCAIS):
                    erros.append(f"{rotulo}: {campo} sem termo local")

        h1 = parser.headings.count(1)
        if h1 != 1:
            erros.append(f"{rotulo}: {h1} H1 (precisa ser 1)")
        anterior = 0
        for nivel in parser.headings:
            if anterior and nivel > anterior + 1:
                erros.append(f"{rotulo}: heading pula de H{anterior} para H{nivel}")
                break
            anterior = nivel

        if len(parser.ids) != len(set(parser.ids)):
            repetidos = sorted({i for i in parser.ids if parser.ids.count(i) > 1})
            erros.append(f"{rotulo}: id repetido {repetidos}")

        for img in parser.imgs:
            alt = img.get("alt")
            if alt is None or (alt.strip() == "" and not (img.get("width") == "1" and img.get("height") == "1")):
                src = img.get("src", "?")
                erros.append(f"{rotulo}: imagem sem alt ({src})")

        canonical = next((l.get("href", "") for l in parser.links if l.get("rel") == "canonical"), "")
        erros.extend(f"{rotulo}: {msg}" for msg in dominios_proibidos(html))
        if noindex:
            if canonical:
                erros.append(f"{rotulo}: 404 não deve ter canonical")
            if rota in sitemap or rota.rstrip("/") in sitemap:
                erros.append(f"{rotulo}: página noindex dentro do sitemap")
        else:
            if not canonical.startswith("https://"):
                erros.append(f"{rotulo}: canonical ausente ou relativo")
            elif urlparse(canonical).netloc != "www.hairzenith.com":
                erros.append(f"{rotulo}: canonical fora de https://www.hairzenith.com")
            elif urlparse(canonical).path != rota:
                erros.append(f"{rotulo}: canonical {canonical} não bate com {rota}")

        for prop in ("og:title", "og:description", "og:image", "og:image:width", "og:image:height", "og:image:alt"):
            if not parser.properties.get(prop):
                erros.append(f"{rotulo}: falta {prop}")
        for nome in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
            if not parser.metas.get(nome):
                erros.append(f"{rotulo}: falta {nome}")
        if parser.metas.get("twitter:card") not in (None, "summary_large_image"):
            erros.append(f"{rotulo}: twitter:card diferente de summary_large_image")

        imagem = parser.properties.get("og:image", "")
        if imagem:
            caminho_img = urlparse(imagem).path
            if not (SITE / caminho_img.lstrip("/")).is_file():
                erros.append(f"{rotulo}: og:image não existe no disco ({caminho_img})")
            if parser.metas.get("twitter:image") != imagem:
                erros.append(f"{rotulo}: twitter:image diferente de og:image")

        for href in ("/favicon.svg", "/favicon-32.png", "/apple-touch-icon.png"):
            if not any(l.get("href") == href for l in parser.links):
                erros.append(f"{rotulo}: falta link {href}")

        if not parser.schemas:
            erros.append(f"{rotulo}: sem JSON-LD")
        else:
            try:
                dados = json.loads(parser.schemas[0])
            except json.JSONDecodeError as exc:
                erros.append(f"{rotulo}: JSON-LD inválido ({exc})")
                dados = {}
            texto_schema = json.dumps(dados, ensure_ascii=False)
            if "Av. Nossa Senhora de Copacabana, 807" not in texto_schema:
                erros.append(f"{rotulo}: schema sem o endereço de Copacabana")
            if "Av. Henrique Terra, 808, Novo Portinho" not in texto_schema:
                erros.append(f"{rotulo}: schema sem o endereço de Cabo Frio")
            if "+55-21-97278-0789" not in texto_schema:
                erros.append(f"{rotulo}: schema sem o telefone do WhatsApp")

        for href in parser.hrefs:
            if "wa.me/" in href:
                numero = href.split("wa.me/", 1)[1].split("?", 1)[0]
                numeros_wa.add(numero)
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            if href.startswith("http://") or href.startswith("https://"):
                continue
            arquivo_dest, ancora = destino_local(href, arquivo)
            if not Path(arquivo_dest).is_file():
                erros.append(f"{rotulo}: link interno quebrado {href}")
                continue
            if ancora:
                destino = Pagina()
                destino.feed(Path(arquivo_dest).read_text(encoding="utf-8"))
                if unquote(ancora) not in destino.ids:
                    erros.append(f"{rotulo}: âncora inexistente {href}")

        if re.search(r"G-X{3,}|GTM-X{3,}|UA-0{3,}|fbq\('init','(?:0+|1234567890)'\)", html):
            erros.append(f"{rotulo}: ID de analytics placeholder")

    if numeros_wa != {"5521972780789"}:
        erros.append(f"WhatsApp divergente: {sorted(numeros_wa) or 'nenhum'}")
    if html_tem_mensagem_diferente():
        erros.append("há link de WhatsApp sem a mensagem padrão da marca")

    if erros:
        print(f"{len(erros)} problema(s):")
        for item in erros:
            print(f"- {item}")
        return 1
    print(f"ok: {len(list(paginas_html()))} páginas, titles únicos, WhatsApp {next(iter(numeros_wa))}")
    return 0


def dominios_proibidos(texto):
    """Padrões que o site publicado não pode ter. Estas strings existem só aqui, no lint."""
    achados = []
    if "hairzenit.com.br" in texto or "hairzenith.com.br" in texto:
        achados.append("ainda usa domínio .com.br")
    if re.search(r"https://(?!www\.)hairzenith\.com", texto):
        achados.append("URL de hairzenith.com sem www")
    if re.search(r"hairzenit(?!h)", texto, re.I):
        achados.append("ainda usa hairzenit sem o h")
    return achados


def html_tem_mensagem_diferente():
    """O atalho fixo pede consulta. O compositor e os atalhos da Larissa/equipe mudam o tipo, de propósito."""
    padrao = "Vim pelo site da Hairzenith"
    for arquivo in paginas_html():
        html = arquivo.read_text(encoding="utf-8")
        for href in re.findall(r'href="(https://wa\.me/[^"]+)"', html):
            if padrao not in unquote(href):
                return True
    return False


if __name__ == "__main__":
    sys.exit(main())
