"""Conversão via Pandoc e pós-processamento do HTML gerado."""

from __future__ import annotations

import re


def tex_to_html(tex_content: str) -> str:
    """Converte LaTeX em HTML usando o Pandoc (com MathJax para as fórmulas)."""
    import pypandoc

    return pypandoc.convert_text(tex_content, "html", format="tex", extra_args=["--mathjax"])


def number_captions(texto: str, tag: str, rotulo: str, order=None) -> str:
    """Numera as legendas (``<caption>``/``<figcaption>``) na ordem de aparição.

    ``order`` é uma lista (por posição) com os rótulos de cada float. Como um float
    pode ter vários ``\\label``, o primeiro vira o ``id`` da legenda e os demais
    ganham âncoras ``<span id="...">`` — assim qualquer ``\\ref`` chega ao alvo.
    """
    order = order or []
    numero = 0
    linhas = []
    for linha in texto.splitlines():
        if f"<{tag}>" in linha:
            found = order[numero] if numero < len(order) else []
            if isinstance(found, str):  # tolera formato antigo (um rótulo só)
                found = [found]
            numero += 1
            extra = "".join(f'<span id="{l}"></span>' for l in found[1:])
            abre = f'<{tag} id="{found[0]}">' if found else f"<{tag}>"
            linha = linha.replace(f"<{tag}>", f"{extra}{abre}<strong>{rotulo} {numero} - </strong>")
        linhas.append(linha)
    return "\n".join(linhas)


def _anchor_equations(html: str) -> str:
    """Cria uma âncora ``<span id="rótulo">`` antes de cada equação rotulada.

    O Pandoc mantém ``\\begin{equation}...\\end{equation}`` dentro de ``\\[...\\]``
    (renderizado pelo MathJax), sem gerar um ``id``. Injetamos a âncora para que
    os links de ``\\ref``/``\\eqref`` cheguem à equação certa.
    """
    def repl(match):
        block = match.group(0)
        labels = re.findall(r"\\label\{([^}]*)\}", block)
        prefix = "".join(f'<span id="{label}"></span>' for label in labels)
        return prefix + block

    return re.sub(r'<span\s+class="math display"[^>]*>.*?</span>', repl, html, flags=re.DOTALL)


def postprocess_html(html: str, fig_order=None, tab_order=None) -> str:
    """Ajusta o HTML gerado pelo Pandoc para o padrão do OJS."""
    html = re.sub(r">\[(\d+)\]<", r">(\1)<", html)
    html = re.sub(r"\{\\arraycolsep\}\{\d+cm\}", "", html)
    html = html.replace("\\textsuperscript{\\textregistered}", "&reg;")
    html = html.replace("\\textregistered", "&reg;")
    html = html.replace("\\copyright", "&copy;")
    html = number_captions(html, "caption", "Table", tab_order)
    html = number_captions(html, "figcaption", "Figure", fig_order)
    html = _anchor_equations(html)
    html = html.replace("\n", " ")
    html = html.replace("%\\", "\\")
    for match in re.findall(r'style="width:(\d+\.\d+)%"', html):
        valor = float(match) / 100
        html = html.replace(f'style="width:{match}%"', f'style="width:calc({valor}*350px)"')
    return html


def build_outline(html: str) -> str:
    """Monta os links do menu 'Outline' a partir dos <h1 id=...> do corpo."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    links = []
    for h1 in soup.find_all("h1", id=True):
        links.append(f'<a href="#{h1["id"]}">{h1.get_text()}</a>')
    return "".join(links)
