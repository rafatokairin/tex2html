"""Pré-processamento do ``.tex`` (limpezas antes do Pandoc) e extração de metadados."""

from __future__ import annotations

import os
import re

from .bibliography import replace_citations
from .crossref import inject_equation_tags, resolve_references
from .text import clean_latex, extract_braced, strip_comments


# --------------------------------------------------------------------------- #
# Figuras
# --------------------------------------------------------------------------- #

# Regex tolerante: aceita espaço/quebra de linha entre o comando, as opções e o
# argumento (ex.: "\includegraphics[scale=.5]%coment\n{fig.png}").
_INCLUDEGRAPHICS = re.compile(r"\\includegraphics\s*(\[[^\]]*\])?\s*\{([^}]+)\}")


def _resolve_stem(referenced: str, stem_index: dict) -> str:
    """Resolve o nome citado no .tex para o nome real do arquivo (ignora caixa)."""
    stem = os.path.splitext(os.path.basename(referenced))[0]
    return stem_index.get(stem.lower(), stem)


def referenced_figures(tex: str) -> list:
    """Lista os nomes-base de figura citados via ``\\includegraphics``."""
    return [os.path.splitext(os.path.basename(m.group(2)))[0]
            for m in _INCLUDEGRAPHICS.finditer(tex)]

def _replace_insert_figure(match) -> str:
    options = match.group(1) or ""
    filename = match.group(2)
    label = match.group(3)
    caption = match.group(4)
    scale_match = re.search(r"scale=(\d+(\.\d+)?)", options)
    if scale_match:
        scale = scale_match.group(1)
        options = options.replace(f"scale={scale}", f"width={scale}\\textwidth")
    return (
        "\n\\begin{figure}\n\\begin{center}\n"
        f"\\includegraphics{options}{{{filename}}}\n"
        f"\\caption{{{caption}}}\n\\label{{fig:{label}}}\n"
        "\\end{center}\n\\end{figure}\n"
    )


_INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")


def resolve_inputs(tex: str, base_dir: str, depth: int = 0, seen=None) -> str:
    """Inclui o conteúdo de ``\\input{arquivo}`` / ``\\include{arquivo}`` (recursivo).

    O LaTeX permite dividir o artigo em vários .tex; sem isso, o conteúdo incluído
    sumiria do HTML. Arquivos ausentes são ignorados; evita loop com ``seen``.
    """
    if seen is None:
        seen = set()
    if depth > 15:
        return tex

    def repl(match):
        name = match.group(1).strip()
        candidate = name if os.path.splitext(name)[1] else name + ".tex"
        path = os.path.normpath(os.path.join(base_dir, candidate))
        if not os.path.isfile(path) or path in seen:
            return ""
        seen.add(path)
        sub = strip_comments(open(path, encoding="utf-8", errors="ignore").read())
        return resolve_inputs(sub, os.path.dirname(path), depth + 1, seen)

    return _INPUT_RE.sub(repl, tex)


def _unwrap_boxes(text: str) -> str:
    """Desembrulha comandos de "caixa" mantendo o CONTEÚDO (último argumento).

    O Pandoc descarta o conteúdo de ``\\resizebox``/``\\scalebox``/``\\raisebox``/
    ``\\rotatebox`` — e, pior, uma tabela dentro de ``\\resizebox{...}{...}{ ... }``
    faz o Pandoc dropar a tabela inteira. Aqui removemos o comando e seus argumentos
    de tamanho/ângulo, preservando o conteúdo (tabela, imagem, etc.).

    ``specs``: nº de argumentos obrigatórios ``{}`` ANTES do conteúdo.
    """
    specs = {"resizebox": 2, "scalebox": 1, "raisebox": 1, "rotatebox": 1, "reflectbox": 0}
    for name, nargs in specs.items():
        text = _unwrap_one_box(text, name, nargs)
    return text


def _unwrap_one_box(text: str, name: str, nargs: int) -> str:
    token = "\\" + name
    out = []
    i = 0
    n = len(text)

    def skip_ws(p):
        while p < n and text[p] in " \t\n":
            p += 1
        return p

    def skip_braced(p):
        """Se em '{', pula o grupo balanceado; devolve (fim, conteudo_interno) ou (None,None)."""
        if p >= n or text[p] != "{":
            return None, None
        depth, p, start = 1, p + 1, p + 1
        while p < n and depth:
            if text[p] == "{":
                depth += 1
            elif text[p] == "}":
                depth -= 1
            p += 1
        return p, text[start:p - 1]

    while True:
        j = text.find(token, i)
        if j == -1:
            out.append(text[i:])
            break
        k = j + len(token)
        if k < n and text[k].isalpha():  # não é exatamente este comando
            out.append(text[i:k])
            i = k
            continue
        p = skip_ws(k)
        while p < n and text[p] == "[":  # argumentos opcionais [..]
            q = text.find("]", p)
            if q == -1:
                break
            p = skip_ws(q + 1)
        ok = True
        for _ in range(nargs):  # argumentos obrigatórios de tamanho/ângulo
            p = skip_ws(p)
            end, _inner = skip_braced(p)
            if end is None:
                ok = False
                break
            p = end
        p = skip_ws(p)
        end, content = (skip_braced(p) if ok else (None, None))
        if end is None:  # padrão inesperado: deixa como está
            out.append(text[i:k])
            i = k
            continue
        out.append(text[i:j])
        out.append(content)  # mantém só o conteúdo
        i = end
    return "".join(out)


def _unwrap_makecell(text: str) -> str:
    """Desembrulha ``\\makecell[..]{a\\\\b}`` / ``\\thead{...}`` mantendo o conteúdo.

    O Pandoc não conhece o pacote ``makecell`` e DESCARTA o comando com o conteúdo
    (perda silenciosa em células de tabela). Aqui mantemos o texto, trocando a
    quebra ``\\\\`` interna por um espaço.
    """
    def repl(match):
        inner = match.group(1)
        return re.sub(r"\\\\\s*(?:\[[^\]]*\])?", " ", inner)

    pattern = r"\\(?:makecell|thead)\s*(?:\[[^\]]*\])?\s*\{((?:[^{}]|\{[^{}]*\})*)\}"
    return re.sub(pattern, repl, text)


def _fix_includegraphics(text: str, stem_index: dict) -> str:
    """Força toda figura para ``nome.png`` sem prefixo de pasta (padrão do OJS).

    Resolve o nome pelo arquivo real (ignorando maiúsculas), garantindo que o
    ``src`` do HTML case exatamente com o PNG gerado — inclusive no OJS (Linux).
    """
    def repl(match):
        options = match.group(1) or ""
        stem = _resolve_stem(match.group(2), stem_index)
        return f"\\includegraphics{options}{{{stem}.png}}"

    return _INCLUDEGRAPHICS.sub(repl, text)


# --------------------------------------------------------------------------- #
# Pré-processamento
# --------------------------------------------------------------------------- #

# Um argumento {...} tolerando um nível de chaves aninhadas (ex.: font={small}).
_BRACE_ARG = r"\{(?:[^{}]|\{[^{}]*\})*\}"


def _strip_layout_commands(content: str) -> str:
    """Remove comandos de layout JUNTO com seus argumentos.

    O código antigo removia só ``\\setlength`` e deixava ``{\\tabcolsep}{3pt}``,
    que o Pandoc renderizava como o texto solto ``3pt`` dentro de um ``<span>``.
    Aqui removemos o comando e os argumentos de uma vez.
    """
    # Ambientes só de layout que o Pandoc não conhece: remove os \begin{...}{args}
    # e \end{...}, mas mantém o conteúdo (senão os args vazam como texto, ex.:
    # \begin{adjustwidth}{1cm}{0cm} deixava "1cm 0cm" no meio do parágrafo).
    for env in ("adjustwidth", "adjustbox", "changemargin", "spacing"):
        content = re.sub(
            r"\\begin\{" + env + r"\}(\s*(\[[^\]]*\]|" + _BRACE_ARG + r"))*", "", content
        )
        content = re.sub(r"\\end\{" + env + r"\}", "", content)
    # Comandos com 2 argumentos.
    content = re.sub(r"\\setlength\s*" + _BRACE_ARG + r"\s*" + _BRACE_ARG, "", content)
    content = re.sub(r"\\addtolength\s*" + _BRACE_ARG + r"\s*" + _BRACE_ARG, "", content)
    content = re.sub(r"\\renewcommand\s*\{\\arraystretch\}\s*" + _BRACE_ARG, "", content)
    # Comandos com 1 argumento (espaçamento/estilo irrelevantes no HTML).
    for cmd in ("vspace", "hspace", "linespread", "captionsetup", "vskip", "hskip"):
        content = re.sub(r"\\" + cmd + r"\*?\s*" + _BRACE_ARG, "", content)
    # Quebras de linha de tabela com espaçamento opcional: \\[3pt] -> \\
    content = re.sub(r"\\\\\s*\[[^\]]*\]", r"\\\\", content)
    # Tokens de layout remanescentes (sem argumento). Usa limite de palavra para
    # não estragar comandos que começam igual (ex.: \small vs \smallskip).
    for token in ("centering", "footnotesize", "arraystretch", "tabcolsep",
                  "columnsep", "raggedright", "raggedleft", "small", "normalsize"):
        content = re.sub(r"\\" + token + r"(?![a-zA-Z])", "", content)
    return content

def preprocess_tex(tex: str, entries: list, labels: dict, registry, stem_index: dict | None = None) -> str:
    """Aplica todas as limpezas de LaTeX antes de chamar o Pandoc.

    Citações e referências viram tokens no ``registry`` (trocados pelo HTML após
    o Pandoc) — ver ``links.LinkRegistry``.
    """
    labels = labels or {}
    stem_index = stem_index or {}
    tex = strip_comments(tex)
    # Resolve referências cruzadas e numera equações antes de qualquer limpeza.
    tex = inject_equation_tags(tex, labels)
    tex = resolve_references(tex, labels, registry)

    content = re.sub(r"\\(begin|end)\{([^}\s]+)\*\}", r"\\\1{\2}", tex)
    content = re.sub(r"\\begin\{equation\}(\s*\\label\{[^}]+\})", r"\\begin{equation}\g<1>", content)
    content = re.sub(r"\\begin\{eqnarray\}(\s*\\label\{[^}]+\})", r"\\begin{eqnarray}\g<1>", content)
    content = content.replace("\\bm{", "\\mathbf{")
    content = content.replace("\\hdots", "\\dots")
    content = re.sub(r"\\parbox\{\d+cm\}", "", content)
    content = content.replace("\\textfractionsolidus", "/")
    content = content.replace("\\textbullet", "⋅")
    content = content.replace("\\textsc", "\\text")
    content = _strip_layout_commands(content)
    content = re.sub(r"\\cline\{.*?\}", "", content)
    content = _unwrap_boxes(content)     # \resizebox/\raisebox/… -> mantém conteúdo
    content = _unwrap_makecell(content)
    content = re.sub(r"\\InsertFigure(\[.*?\])?\{(.*?)\}\{(.*?)\}\{(.*?)\}", _replace_insert_figure, content)
    content = _fix_includegraphics(content, stem_index)

    abstract = extract_braced(tex, "AbstractENG").strip()
    keywords = extract_braced(tex, "KeywordsENG").strip()
    if abstract or keywords:
        block = abstract
        if keywords:
            block = (block + "\n\nKeywords: " + keywords).strip()
        marker = "\\begin{document}"
        idx = content.find(marker)
        if idx != -1:
            insert_at = idx + len(marker)
            content = content[:insert_at] + "\n" + block + "\n" + content[insert_at:]

    content = content.replace("\\columnwidth", "\\textwidth")
    content = re.sub(
        r"\\begin\{([^}]*)\} \\label\{([^}]*)\}",
        r"\\begin{figure} {(\2)} \\end{figure} \\begin{\1} \\label{\2}",
        content,
    )
    content = replace_citations(content, entries, registry)
    return content


# --------------------------------------------------------------------------- #
# Autores (nome completo + ORCID)
# --------------------------------------------------------------------------- #

def _strip_command(text: str, cmd: str) -> str:
    """Remove ``\\cmd{...}`` (com chaves balanceadas, qualquer profundidade)."""
    out = []
    i = 0
    token = "\\" + cmd
    while True:
        j = text.find(token, i)
        if j == -1:
            out.append(text[i:])
            break
        k = j + len(token)
        if k < len(text) and text[k].isalpha():  # ex.: \thanksgiving — não é \thanks
            out.append(text[i:k])
            i = k
            continue
        while k < len(text) and text[k] in " \t\n":
            k += 1
        if k < len(text) and text[k] == "{":
            depth, k = 1, k + 1
            while k < len(text) and depth:
                if text[k] == "{":
                    depth += 1
                elif text[k] == "}":
                    depth -= 1
                k += 1
            out.append(text[i:j])
            i = k
        else:
            out.append(text[i:j + len(token)])
            i = j + len(token)
    return "".join(out)


def _clean_author_name(seg: str) -> str:
    """Limpa o nome de um autor de marcadores de afiliação e de layout.

    Remove ``$^2$``/``$^{1,2}$`` (afiliação em math), ``\\textsuperscript{}``,
    quebras ``\\\\``/``\\\\[..]``, ``\\vspace{}``, ``\\orcidlink{}`` e superíndices
    soltos — deixando só o nome legível.
    """
    seg = re.sub(r"\\orcidlink\s*\{[^}]*\}", "", seg)
    seg = re.sub(r"\\textsuperscript\s*\{[^}]*\}", "", seg)
    seg = re.sub(r"\\(?:inst|footnotemark|thanksmark|IEEEauthorrefmark)\s*\{[^}]*\}", "", seg)
    seg = re.sub(r"\$[^$]*\$", "", seg)                 # $^2$, $^{1,2}$…
    seg = re.sub(r"\\\\\s*(?:\[[^\]]*\])?", " ", seg)   # \\ e \\[-0.25cm] -> espaço
    seg = re.sub(r"\\vspace\*?\s*\{[^}]*\}", "", seg)
    seg = re.sub(r"\^\{?[\d,\s*†‡§¶]+\}?", "", seg)     # superíndices soltos ^2, ^{1,2}
    return re.sub(r"\s+", " ", clean_latex(seg)).strip(" ,;.")


def extract_authors(tex: str) -> list:
    """Extrai ``[{name, orcid}]`` do bloco ``\\author{...}``.

    Cada autor aparece como ``Nome\\thanks{...}\\email{...}\\orcidlink{ID}``,
    separados por vírgula. As quebras ``\\\\`` são só layout (não separam autores),
    então viram espaço — assim um nome quebrado em duas linhas não se divide.
    """
    block = extract_braced(tex, "author")
    if not block:
        return []
    for cmd in ("thanks", "email", "footnote", "affiliation"):
        block = _strip_command(block, cmd)
    # Quebras de linha não separam autores: viram espaço antes de dividir por vírgula.
    block = re.sub(r"\\\\\s*(?:\[[^\]]*\])?", " ", block)

    authors = []
    for seg in block.split(","):
        orcid_match = re.search(r"\\orcidlink\s*\{([^}]*)\}", seg)
        orcid = orcid_match.group(1).strip() if orcid_match else ""
        name = _clean_author_name(seg)
        if name:
            authors.append({"name": name, "orcid": orcid})
    return authors


# --------------------------------------------------------------------------- #
# Metadados do cabeçalho
# --------------------------------------------------------------------------- #

def extract_metadata(tex: str) -> dict:
    """Extrai os campos do cabeçalho do artigo (título, DOI, datas, etc.)."""
    def field(cmd):
        return clean_latex(extract_braced(tex, cmd)).strip()

    title = field("ArticleTitleENG") or field("ArticleTitlePTBR")
    year = field("Year")
    volume = field("Volume")
    article_id = field("ArticleID")

    citation = "Semin., Ciênc. Exatas Tecnol."
    if year:
        citation += f" {year}"
    if volume:
        citation += f", v. {volume}"
    if article_id:
        citation += f": {article_id}"

    return {
        "area": field("Area"),
        "title": title,
        "authors": extract_authors(tex),
        "author_header": field("AuthorHeader"),
        "doi": field("DOI"),
        "received": field("ReceivedDate"),
        "revised": field("RevisedDate"),
        "accepted": field("AcceptedDate"),
        "published": field("PublishedDate"),
        "citation": citation,
    }
