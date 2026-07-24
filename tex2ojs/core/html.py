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
            # Âncoras próprias (namespace xref-) DENTRO da legenda, para não colidir
            # com o id que o Pandoc já põe na <figure>/<table> a partir do \label
            # (e sem quebrar a regra de <caption> ser o 1º filho da <table>).
            anchors = "".join(f'<span id="xref-{l}"></span>' for l in found)
            linha = linha.replace(f"<{tag}>", f"<{tag}>{anchors}<strong>{rotulo} {numero} - </strong>")
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
        prefix = "".join(f'<span id="xref-{label}"></span>' for label in labels)
        return prefix + block

    return re.sub(r'<span\s+class="math display"[^>]*>.*?</span>', repl, html, flags=re.DOTALL)


def postprocess_html(html: str, fig_order=None, tab_order=None) -> str:
    """Ajusta o HTML gerado pelo Pandoc para o padrão do OJS."""
    # Remove os <span data-label=...> vazios que o Pandoc injeta para rótulos:
    # eles repetem o id já posto na <figure>/<table> (id duplicado) e são
    # redundantes, pois resolvemos as referências pelo nosso namespace xref-.
    html = re.sub(r'<span[^>]*\bdata-label="[^"]*"[^>]*>\s*</span>', "", html)
    html = re.sub(r">\[(\d+)\]<", r">(\1)<", html)
    html = re.sub(r"\{\\arraycolsep\}\{\d+cm\}", "", html)
    html = html.replace("\\textsuperscript{\\textregistered}", "&reg;")
    html = html.replace("\\textregistered", "&reg;")
    html = html.replace("\\copyright", "&copy;")
    html = number_captions(html, "caption", "Table", tab_order)
    html = number_captions(html, "figcaption", "Figure", fig_order)
    html = _anchor_equations(html)
    # NÃO colapsar '\n' -> ' ': quebraria a formatação dentro de <pre> (código).
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
