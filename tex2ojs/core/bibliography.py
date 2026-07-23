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


def replace_citations(text: str, entries: list, registry) -> str:
    """Substitui ``\\cite`` e ``\\citeauthor`` por citações no padrão da revista.

    O HTML é guardado no ``registry`` atrás de um token de texto puro (ver
    ``links.LinkRegistry``); o token é trocado pelo HTML depois do Pandoc.
    """
    bib_by_key = {e["key"]: e for e in entries}

    def build(match, is_author):
        keys = [k.strip() for k in match.group(1).split(",") if k.strip()]
        parts = []
        for key in keys:
            entry = bib_by_key.get(key)
            if not entry:
                parts.append(f"[{key} - not found]")
                continue
            label, year = _authors_and_year(entry)
            link = f'<a href="#{key}">{year}</a>'
            if is_author:
                parts.append(f"{label} ({link})")
            else:
                parts.append(f"{label}, {link}")
        joined = "; ".join(parts)
        html = joined if is_author else f"({joined})"
        return registry.token(html)

    text = re.sub(r"\\citeauthor\{([^}]+)\}", lambda m: build(m, True), text)
    text = re.sub(r"\\cite\{([^}]+)\}", lambda m: build(m, False), text)
    return text


# --------------------------------------------------------------------------- #
# Lista de referências
# --------------------------------------------------------------------------- #

def format_references(entries: list) -> str:
    """Formata a lista de referências (uma <p> por entrada, com âncora #chave)."""
    out = []
    for info in entries:
        p = f'<p id="{info["key"]}">'
        if info.get("author"):
            authors = [clean_latex(a) for a in re.split(r"\s+and\s+", info["author"]) if a.strip()]
            others = bool(authors) and authors[-1].lower() == "others"
            if others:
                authors = authors[:-1]
            if others:
                formatted = ", ".join(authors) + " et al." if authors else "et al."
            elif len(authors) > 1:
                formatted = ", ".join(authors[:-1]) + " & " + authors[-1]
            else:
                formatted = authors[0] if authors else ""
            p += formatted + " "
        if info.get("year"):
            p += "(" + clean_latex(info["year"]) + ")."
        if info.get("title"):
            p += " " + clean_latex(info["title"]) + "."
        if info.get("publisher"):
            p += " " + clean_latex(info["publisher"]) + "."
        if info.get("volume") and info.get("number"):
            p += " " + clean_latex(info["volume"]) + "(" + clean_latex(info["number"]) + "),"
        if info.get("pages"):
            p += " " + clean_latex(info["pages"]) + "."
        if info.get("doi"):
            doi = clean_latex(info["doi"])
            p += f' <a target="_blank" href="https://doi.org/{doi}">https://doi.org/{doi}</a>'
        p += "</p>"
        out.append(p)
    return "".join(out)
