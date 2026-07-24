"""Orquestração da conversão: junta todas as etapas numa única função."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field

from ..media import images
from ..resources import asset_path
from . import template
from .bibliography import format_references, parse_bib
from .crossref import build_label_map
from .html import build_outline, postprocess_html, tex_to_html
from .latex import extract_metadata, preprocess_tex, referenced_figures
from .lint import lint_tex
from .links import LinkRegistry
from .text import strip_comments
from .validation import find_duplicate_ids, validate_document


@dataclass
class ConversionResult:
    output_dir: str
    html_file: str
    images: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def _find_source(article_dir: str, extension: str):
    candidates = []
    for name in sorted(os.listdir(article_dir)):
        full = os.path.join(article_dir, name)
        if os.path.isfile(full) and name.lower().endswith(extension):
            candidates.append(full)
    if not candidates:
        return None
    for c in candidates:  # prefere um arquivo chamado 'article'
        if os.path.basename(c).lower().startswith("article"):
            return c
    return candidates[0]


def convert_article(article_dir, output_dir=None, log=print) -> ConversionResult:
    """Converte uma pasta ``Artigo<N>`` num pacote pronto para o OJS.

    Parameters
    ----------
    article_dir : str
        Pasta contendo o ``.tex``, o ``.bib`` e a pasta de figuras.
    output_dir : str, optional
        Pasta de saída. Padrão: ``<article_dir>_OJS`` ao lado da original.
    log : callable
        Função para reportar progresso (recebe uma string).
    """
    article_dir = os.path.abspath(article_dir)
    if not os.path.isdir(article_dir):
        raise NotADirectoryError(f"Pasta não encontrada: {article_dir}")

    warnings = []

    tex_path = _find_source(article_dir, ".tex")
    if not tex_path:
        raise FileNotFoundError("Nenhum arquivo .tex encontrado na pasta do artigo.")
    bib_path = _find_source(article_dir, ".bib")

    log(f"Arquivo .tex: {os.path.basename(tex_path)}")
    log(f"Arquivo .bib: {os.path.basename(bib_path) if bib_path else '(nenhum)'}")

    with open(tex_path, "r", encoding="utf-8") as f:
        tex_raw = f.read()
    bib_text = ""
    if bib_path:
        with open(bib_path, "r", encoding="utf-8") as f:
            bib_text = f.read()

    entries = parse_bib(bib_text) if bib_text else []
    log(f"Referências encontradas: {len(entries)}")

    base = os.path.basename(article_dir.rstrip(os.sep)) or "artigo"
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(article_dir), f"{base}_OJS")
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Converte as figuras para PNG.
    figures_dir = images.find_figures_dir(article_dir)
    converted = []
    if figures_dir:
        log(f"Pasta de figuras: {os.path.relpath(figures_dir, article_dir)}")
        converted, img_warnings, _sizes = images.convert_images_to_png(figures_dir, output_dir, log=log)
        warnings.extend(img_warnings)
    else:
        warnings.append("Nenhuma pasta de figuras encontrada.")
        log("Aviso: nenhuma pasta de figuras encontrada.")

    log("Convertendo LaTeX -> HTML (Pandoc)…")
    # Trabalhamos sobre o .tex sem comentários (evita figuras/ambientes comentados
    # e conserta comandos quebrados por comentário no meio).
    tex_clean = strip_comments(tex_raw)
    stem_index = images.build_stem_index(figures_dir) if figures_dir else {}

    # Avisa sobre figuras citadas que não existem na pasta.
    for stem in referenced_figures(tex_clean):
        if stem.lower() not in stem_index:
            warnings.append(f"Figura citada no .tex mas não encontrada na pasta: '{stem}'.")
            log(f"Aviso: figura '{stem}' citada mas não encontrada.")

    labels, fig_order, tab_order = build_label_map(tex_clean)

    # Valida citações/referências/rótulos e avisa (sem interromper).
    for w in validate_document(tex_clean, entries, labels):
        warnings.append(w)
        log(f"Aviso: {w}")

    registry = LinkRegistry()
    tex_pre = preprocess_tex(tex_raw, entries, labels, registry, stem_index)

    try:
        raw_html = tex_to_html(tex_pre)
    except RuntimeError as exc:
        issues = lint_tex(tex_clean)
        msg = "Não foi possível converter o LaTeX deste artigo."
        if issues:
            msg += " Possível causa no arquivo .tex:\n  - " + "\n  - ".join(issues)
        else:
            msg += f"\n(Detalhe técnico do Pandoc: {str(exc)[:300]})"
        raise RuntimeError(msg) from None

    html_body = postprocess_html(raw_html, fig_order, tab_order)
    html_body = registry.apply(html_body)

    metadata = extract_metadata(tex_clean)
    menu_html = build_outline(html_body)
    references_html = format_references(entries)
    page = template.render_page(metadata, html_body, menu_html, references_html)

    # Rede de segurança: se sobrou algum id duplicado na página final, avisa (um
    # link poderia pular para o lugar errado).
    for dup in find_duplicate_ids(page):
        msg = f"Identificador duplicado no HTML: '{dup}' (verifique rótulos/chaves repetidos)."
        warnings.append(msg)
        log(f"Aviso: {msg}")

    html_file = os.path.join(output_dir, f"{base}.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(page)
    log(f"HTML gerado: {os.path.basename(html_file)}")

    # Copia os assets estáticos da revista (referenciados no HTML).
    for asset in ("Header.png", "orcid.png"):
        src = asset_path(asset)
        if os.path.isfile(src):
            shutil.copyfile(src, os.path.join(output_dir, asset))

    log(f"Concluído. Pasta de saída: {output_dir}")
    return ConversionResult(output_dir, html_file, converted, warnings)
