"""Parsing do ``.bib``, substituição de citações e formatação de referências."""

from __future__ import annotations

import re

from .text import clean_latex


# --------------------------------------------------------------------------- #
# Parser de .bib (robusto, ciente de chaves)
# --------------------------------------------------------------------------- #

def _parse_fields(body: str) -> dict:
    fields = {}
    i, n = 0, len(body)
    name_re = re.compile(r"([A-Za-z][A-Za-z0-9_\-]*)\s*=\s*")
    while i < n:
        m = name_re.search(body, i)
        if not m:
            break
        name = m.group(1).lower()
        i = m.end()
        if i >= n:
            break
        char = body[i]
        if char == "{":
            depth, i, start = 1, i + 1, i + 1
            while i < n and depth > 0:
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                i += 1
            value = body[start:i - 1]
        elif char == '"':
            i += 1
            start = i
            while i < n and body[i] != '"':
                i += 1
            value = body[start:i]
            i += 1
        else:
            start = i
            while i < n and body[i] not in ",\n":
                i += 1
            value = body[start:i]
        fields[name] = value.strip()
        comma = body.find(",", i)
        if comma == -1:
            break
        i = comma + 1
    return fields


def parse_bib(text: str) -> list:
    """Converte o conteúdo de um ``.bib`` numa lista de dicionários.

    Cada entrada vira ``{"type": ..., "key": ..., "author": ..., ...}``.
    A ordem das entradas no arquivo é preservada.
    """
    entries = []
    i, n = 0, len(text)
    while True:
        at = text.find("@", i)
        if at == -1:
            break
        brace = text.find("{", at)
        if brace == -1:
            break
        entry_type = text[at + 1:brace].strip().lower()
        depth, j = 1, brace + 1
        while j < n and depth > 0:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        body = text[brace + 1:j - 1]
        comma = body.find(",")
        if comma == -1:
            key, fields_str = body.strip(), ""
        else:
            key, fields_str = body[:comma].strip(), body[comma + 1:]
        if key and not entry_type.startswith("comment"):
            entry = {"type": entry_type, "key": key}
            entry.update(_parse_fields(fields_str))
            entries.append(entry)
        i = j
    return entries


# --------------------------------------------------------------------------- #
# Citações no texto (\cite e \citeauthor)
# --------------------------------------------------------------------------- #

def _surname(name: str) -> str:
    """Sobrenome de um autor em 'Sobrenome, Nome' ou 'Nome Sobrenome'."""
    name = clean_latex(name).strip()
    if "," in name:
        return name.split(",")[0].strip()
    parts = name.split()
    return parts[-1] if parts else name


def _authors_and_year(entry: dict):
    authors_raw = entry.get("author", "")
    year = clean_latex(entry.get("year", ""))
    authors = [a for a in re.split(r"\s+and\s+", authors_raw) if a.strip()]
    # Em BibTeX, "and others" equivale a "et al.".
    has_others = any(clean_latex(a).lower() == "others" for a in authors)
    surnames = [_surname(a) for a in authors if clean_latex(a).lower() != "others"]
    if not surnames:
        label = clean_latex(authors_raw)
    elif has_others or len(surnames) > 2:
        label = f"{surnames[0]} et al."
    elif len(surnames) == 1:
        label = surnames[0]
    else:
        label = f"{surnames[0]} & {surnames[1]}"
    return label, year


def _inside_open_paren(before: str) -> bool:
    """True se a citação está dentro de um '(' aberto pelo autor (ainda sem fechar).

    Conta parênteses no texto anterior (em prosa eles se equilibram; um '(' a mais
    significa que estamos dentro de um grupo aberto, como numa lista de citações).
    Usado para não duplicar parênteses (ex.: "Autor et al., (\\citeyear{...})").
    """
    return before.count("(") > before.count(")")


# Cada comando de citação define O QUE mostrar (o autor escolhe o comando certo).
# Cobrimos natbib E biblatex (textcite/parencite/autocite…).
_TEXTUAL = {"citet", "citealt", "citealp", "textcite"}   # Autor (ano)
# author-only / year-only são detectados por conterem "author"/"year" no nome.
# Demais (cite, citep, parencite, autocite, footcite, …) -> "(Autor, ano)".


def replace_citations(text: str, entries: list, registry) -> str:
    """Substitui os comandos de citação pelo formato da revista, honrando o tipo:

    - ``\\cite``/``\\citep`` -> ``(Autor, ano)``
    - ``\\citet``            -> ``Autor (ano)``
    - ``\\citeauthor``       -> ``Autor``
    - ``\\citeyear``         -> ``(ano)`` (só o ano — evita duplicar o nome quando o
      autor já o escreveu à mão, ex.: "Hemoud et al., \\citeyear{...}")

    O HTML vai para o ``registry`` atrás de um token de texto puro (ver
    ``links.LinkRegistry``); o token é trocado pelo HTML depois do Pandoc.
    """
    bib_by_key = {e["key"]: e for e in entries}

    def build(match):
        cmd = match.group(1).lower()
        keys = [k.strip() for k in match.group(2).split(",") if k.strip()]
        author_only = "author" in cmd
        year_only = "year" in cmd or "date" in cmd
        textual = cmd in _TEXTUAL
        inside_parens = _inside_open_paren(text[:match.start()])
        parts = []
        for key in keys:
            entry = bib_by_key.get(key)
            if not entry:
                parts.append(f"[{key} - not found]")
                continue
            label, year = _authors_and_year(entry)
            year_link = f'<a href="#ref-{key}">{year}</a>'
            if author_only:
                parts.append(f'<a href="#ref-{key}">{label}</a>')
            elif year_only:
                parts.append(year_link)
            elif textual:
                parts.append(f"{label} ({year_link})")
            else:  # cite, citep, parencite, autocite…
                parts.append(f"{label}, {year_link}")
        joined = "; ".join(parts)
        # \citet/\textcite/\citeauthor não levam parênteses externos; os demais
        # recebem "(...)" só se ainda não estivermos dentro de parênteses do autor.
        no_wrap = textual or author_only or inside_parens
        return registry.token(joined if no_wrap else f"({joined})")

    # Cobre natbib e biblatex: \cite, \citep, \citet, \citeauthor, \citeyear,
    # \textcite, \parencite, \autocite, \footcite… variantes com ``*`` e
    # argumentos opcionais como \cite[p. 5]{chave}.
    return re.sub(r"\\([A-Za-z]*cite[A-Za-z]*)\*?\s*(?:\[[^\]]*\])*\{([^}]+)\}", build, text)


# --------------------------------------------------------------------------- #
# Lista de referências
# --------------------------------------------------------------------------- #

# Tipos cujo "título" é a própria obra (fica em itálico, estilo APA).
_STANDALONE_TYPES = {
    "book", "booklet", "proceedings", "manual", "phdthesis",
    "mastersthesis", "techreport", "misc", "unpublished",
}


def _initials(given: str) -> str:
    """'Rosana Laira' -> 'R. L.' (iniciais no estilo APA)."""
    parts = [p for p in re.split(r"[\s.\-]+", given) if p]
    return " ".join(f"{p[0].upper()}." for p in parts)


def _format_author_apa(raw: str) -> str:
    """Formata um autor como 'Sobrenome, I. I.' (ou mantém nomes institucionais)."""
    raw = raw.strip()
    institutional = raw.startswith("{")  # ex.: {{ContExt}} / {{Instituto Silva}}
    name = clean_latex(raw).strip()
    if not name:
        return ""
    if institutional or ("," not in name and len(name.split()) == 1):
        return name
    if "," in name:
        surname, given = name.split(",", 1)
        surname, given = surname.strip(), given.strip()
    else:
        parts = name.split()
        surname, given = parts[-1], " ".join(parts[:-1])
    ini = _initials(given)
    return f"{surname}, {ini}" if ini else surname


def _format_authors(raw: str) -> str:
    """Lista de autores no estilo APA: 'A, F., B, G., & C, H.' (ou '… et al.')."""
    authors = [a for a in re.split(r"\s+and\s+", raw) if a.strip()]
    has_others = any(clean_latex(a).lower() == "others" for a in authors)
    formatted = [_format_author_apa(a) for a in authors if clean_latex(a).lower() != "others"]
    formatted = [f for f in formatted if f]
    if not formatted:
        return ""
    if has_others:
        return ", ".join(formatted) + ", et al."
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + ", & " + formatted[-1]


def format_references(entries: list) -> str:
    """Formata a lista de referências (uma ``<p>`` por entrada, âncora ``#chave``).

    Segue um estilo APA-simplificado, com iniciais dos autores, título do
    periódico/livro em itálico, volume(número), páginas e DOI/URL clicável.
    """
    out = []
    seen = set()
    for info in entries:
        if info["key"] in seen:  # chave duplicada no .bib: mantém só a 1ª (evita id repetido)
            continue
        seen.add(info["key"])
        etype = info.get("type", "")
        get = lambda k: clean_latex(info.get(k, ""))
        parts = []

        authors = _format_authors(info.get("author", ""))
        if authors:
            parts.append(authors + ("" if authors.endswith(".") else "."))
        if get("year"):
            parts.append(f"({get('year')}).")

        title = get("title")
        if title:
            parts.append(f"<em>{title}</em>." if etype in _STANDALONE_TYPES else f"{title}.")

        journal, booktitle = get("journal"), get("booktitle")
        vol, num, pages = get("volume"), get("number"), get("pages")
        if journal:
            s = f"<em>{journal}</em>"
            if vol:
                s += f", <em>{vol}</em>"
            if num:
                s += f"({num})"
            if pages:
                s += f", {pages}"
            parts.append(s + ".")
        elif booktitle:
            s = f"In <em>{booktitle}</em>"
            if pages:
                s += f" (pp. {pages})"
            parts.append(s + ".")
            if get("publisher"):
                parts.append(f"{get('publisher')}.")
        else:
            for field in ("publisher", "institution", "school", "organization"):
                if get(field):
                    parts.append(f"{get(field)}.")
                    break
            if pages and not journal:
                parts.append(f"pp. {pages}.")

        if etype in _STANDALONE_TYPES and get("howpublished") and not (journal or booktitle):
            parts.append(f"{get('howpublished')}.")

        doi, url = get("doi"), get("url")
        if doi:
            parts.append(f'<a target="_blank" href="https://doi.org/{doi}">https://doi.org/{doi}</a>')
        elif url:
            parts.append(f'<a target="_blank" href="{url}">{url}</a>')
        if get("note"):
            parts.append(f"{get('note')}.")

        body = " ".join(p for p in parts if p)
        out.append(f'<p id="ref-{info["key"]}">{body}</p>')
    return "".join(out)
