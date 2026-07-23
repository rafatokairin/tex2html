"""Utilitários de baixo nível para limpeza de texto LaTeX.

São a base compartilhada por ``latex.py`` e ``bibliography.py`` — por isso ficam
isolados aqui, sem dependências de outros módulos do núcleo (evita import circular).
"""

from __future__ import annotations

import re


def clean_latex(text: str) -> str:
    """Remove comandos LaTeX simples de um trecho de texto.

    Substitui ``\\comando{conteudo}`` pelo conteúdo, remove comandos soltos
    (``\\comando``) e chaves remanescentes. Funde a lógica dos antigos scripts
    ``bibnorm.py``/``texnorm.py``, mas sem alterar os arquivos de origem.
    """
    if not text:
        return ""
    text = text.replace("~", " ")
    for _ in range(3):  # resolve comandos aninhados
        new = re.sub(r"\\[a-zA-Z]+\*?\s*\{([^{}]*)\}", r"\1", text)
        if new == text:
            break
        text = new
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    text = text.replace("{", "").replace("}", "")
    text = text.replace("\\&", "&").replace("\\%", "%").replace("\\_", "_")
    text = text.replace("---", "—").replace("--", "–")
    return text.strip()


def strip_comments(tex: str) -> str:
    """Remove comentários LaTeX (``%`` até o fim da linha), preservando ``\\%``.

    Além de ajudar o Pandoc, evita que figuras/ambientes comentados sejam contados
    e conserta ``\\includegraphics[...]%coment`` seguido do argumento na linha de baixo.
    """
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in tex.splitlines())


def extract_braced(text: str, command: str) -> str:
    """Extrai o conteúdo de ``\\command{...}`` respeitando chaves aninhadas."""
    match = re.search(r"\\" + re.escape(command) + r"\s*\{", text)
    if not match:
        return ""
    i = match.end()
    depth = 1
    start = i
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start:i - 1]
