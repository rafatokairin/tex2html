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


# Detecta um nome de autor escrito à mão imediatamente antes do \cite:
#  - termina em "et al." / "et al.,"  (ex.: "Al-Hemoud et al., \cite{...}")
#  - ou num sobrenome Capitalizado, com vírgula opcional (ex.: "Jeong, \cite{...}").
_AUTHOR_BEFORE = re.compile(r"(?:et\s+al\.?|[A-ZÀ-Ý][A-Za-zÀ-ÿ.'\-]*),?\s*$")


def _author_written_before(before: str) -> bool:
    if not before:
        return False
    return bool(_AUTHOR_BEFORE.search(before))


def replace_citations(text: str, entries: list, registry) -> str:
    """Substitui ``\\cite`` e ``\\citeauthor`` por citações no padrão da revista.

    O HTML é guardado no ``registry`` atrás de um token de texto puro (ver
    ``links.LinkRegistry``); o token é trocado pelo HTML depois do Pandoc.
    """
    bib_by_key = {e["key"]: e for e in entries}
    # Comandos "textuais" (Autor (ano)) vs "parentéticos" ((Autor, ano)).
    _TEXTUAL = {"citeauthor", "citet", "citealt", "textcite"}

    def build(match):
        cmd = match.group(1)
        keys = [k.strip() for k in match.group(2).split(",") if k.strip()]
        textual = cmd in _TEXTUAL
        before = text[:match.start()].rstrip()
        # Modo inteligente: se o autor já foi escrito à mão logo antes do \cite,
        # mostramos só o ano (evita "Autor et al., (Autor et al., ano)").
        author_before = not textual and _author_written_before(before)
        # Se o autor já abriu parêntese "(\cite{...})", não abrimos outro.
        open_before = before.endswith("(")
        parts = []
        for key in keys:
            entry = bib_by_key.get(key)
            if not entry:
                parts.append(f"[{key} - not found]")
                continue
            label, year = _authors_and_year(entry)
            link = f'<a href="#ref-{key}">{year}</a>'
            if textual:
                parts.append(f"{label} ({link})")
            elif author_before:
                parts.append(link)  # só o ano (autor já está no texto)
            else:
                parts.append(f"{label}, {link}")
        joined = "; ".join(parts)
        if textual or author_before or open_before:
            return registry.token(joined)  # sem parênteses próprios
        return registry.token(f"({joined})")

    # Cobre \cite, \citep, \citet, \citeauthor, \citeyear… e argumentos opcionais
    # como \cite[p. 5]{chave}.
    return re.sub(r"\\(cite[a-zA-Z]*)\s*(?:\[[^\]]*\])*\{([^}]+)\}", build, text)


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
