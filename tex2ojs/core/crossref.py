"""Referências cruzadas (``\\ref``, ``\\eqref``, ``\\autoref``) e numeração.

O Pandoc não resolve referências cruzadas de LaTeX cru: ele simplesmente descarta
``\\ref{...}``. Aqui montamos um mapa ``rótulo -> número`` percorrendo o documento
na ordem (figuras, tabelas e equações) e:

- trocamos ``\\ref``/``\\eqref``/``\\autoref`` por links HTML numerados que apontam
  para a âncora do alvo (o HTML é injetado no .tex e o Pandoc o escapa; o
  pós-processamento o desescapa, igual às citações);
- injetamos ``\\tag{N}`` nas equações rotuladas para que o número apareça ao lado
  da equação (renderizado pelo MathJax) — mantendo consistência com o link.

A numeração de figuras/tabelas segue a mesma ordem usada na numeração das legendas
(ver ``html.number_captions``), garantindo que o número do link bata com a legenda.
"""

from __future__ import annotations

import re

# Ambientes de equação numerados (as versões com ``*`` não são numeradas e, por
# não terem chave sem ``*``, não são capturadas pelas regex abaixo).
_MATH_ENVS = "equation|eqnarray|align|gather|multline|displaymath|flalign"


def build_label_map(tex: str):
    """Percorre o .tex e devolve ``(labels, fig_order, tab_order)``.

    - ``labels``: ``{rótulo: (tipo, número)}`` com ``tipo`` em ``fig``/``tab``/``eq``.
    - ``fig_order`` / ``tab_order``: rótulos (ou ``None``) na ordem em que as
      figuras/tabelas aparecem — para casar com a numeração das legendas.
    """
    labels = {}
    fig_order = []
    tab_order = []

    def scan_floats(env, prefix, order):
        n = 0
        # Aceita também a versão com ``*`` (figure*/table*) usada em layout 2 colunas.
        pattern = re.compile(r"\\begin\{" + env + r"\*?\}(.*?)\\end\{" + env + r"\*?\}", re.DOTALL)
        for match in pattern.finditer(tex):
            block = match.group(1)
            if "\\caption" not in block:  # sem legenda -> não é numerada
                continue
            n += 1
            # Um float pode ter vários \label (todos apontam para o mesmo número).
            found = re.findall(r"\\label\{([^}]*)\}", block)
            order.append(found)
            for label in found:
                labels[label] = (prefix, n)

    scan_floats("figure", "fig", fig_order)
    scan_floats("table", "tab", tab_order)

    # Equações: numeramos cada \label encontrado dentro de um ambiente de equação,
    # na ordem do documento.
    n_eq = 0
    env_re = re.compile(r"\\begin\{(" + _MATH_ENVS + r")\}(.*?)\\end\{\1\}", re.DOTALL)
    for match in env_re.finditer(tex):
        for label_match in re.finditer(r"\\label\{([^}]*)\}", match.group(2)):
            n_eq += 1
            labels[label_match.group(1)] = ("eq", n_eq)

    return labels, fig_order, tab_order


def inject_equation_tags(tex: str, labels: dict) -> str:
    """Adiciona ``\\tag{N}`` às equações rotuladas para exibir o número."""
    def repl(match):
        label = match.group(1)
        info = labels.get(label)
        if info and info[0] == "eq":
            return f"\\label{{{label}}}\\tag{{{info[1]}}}"
        return match.group(0)

    return re.sub(r"\\label\{([^}]*)\}", repl, tex)


def resolve_references(tex: str, labels: dict, registry) -> str:
    """Troca ``\\ref``/``\\eqref``/``\\autoref``/``\\cref`` por links numerados.

    O HTML vai para o ``registry`` (token de texto puro trocado após o Pandoc),
    evitando injetar ``#``/``<`` no LaTeX (o que faria o Pandoc abortar).
    Rótulos desconhecidos viram um marcador visível ``(?)`` — nunca somem em
    silêncio, para a professora perceber.
    """
    def link(match, parenthesized):
        label = match.group(1)
        info = labels.get(label)
        if not info:
            html = '<span class="ref-missing">(?)</span>'
            return registry.token(html)
        number = info[1]
        anchor = f'<a href="#{label}">{number}</a>'
        return registry.token(f"({anchor})" if parenthesized else anchor)

    tex = re.sub(r"\\eqref\{([^}]*)\}", lambda m: link(m, True), tex)
    tex = re.sub(r"\\(?:ref|autoref|cref|Cref)\{([^}]*)\}", lambda m: link(m, False), tex)
    return tex
