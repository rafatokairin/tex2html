"""Validações do documento que viram avisos mostrados no programa.

Não interrompem a conversão (diferente de ``lint``, que trata erros que fariam o
Pandoc abortar): apenas alertam sobre problemas que geram links quebrados ou
referências inconsistentes, para o usuário corrigir no LaTeX.
"""

from __future__ import annotations

import re
from collections import Counter

from .text import strip_comments

_CITE = re.compile(r"\\cite(?:author|p|t|year|al)?\*?\s*(?:\[[^\]]*\])*\{([^}]*)\}")
_REF = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{([^}]*)\}")
_LABEL = re.compile(r"\\label\{([^}]*)\}")


def validate_document(tex: str, entries: list, labels: dict) -> list:
    """Retorna avisos sobre citações/referências/rótulos inconsistentes."""
    warnings = []
    tex = strip_comments(tex)
    keys = [e["key"] for e in entries]
    keyset = set(keys)

    # 1. Chaves de bibliografia duplicadas.
    for key, count in Counter(keys).items():
        if count > 1:
            warnings.append(f"Chave de bibliografia duplicada no .bib: '{key}' ({count}×).")

    # 2. Citações sem entrada no .bib.
    cited = set()
    for m in _CITE.finditer(tex):
        cited.update(k.strip() for k in m.group(1).split(",") if k.strip())
    for key in sorted(cited - keyset):
        warnings.append(f"Citação para '{key}' não tem entrada no .bib (link ficaria quebrado).")

    # 3. Referências \\ref para rótulos inexistentes.
    missing_refs = sorted({m.group(1).strip() for m in _REF.finditer(tex)
                           if m.group(1).strip() and m.group(1).strip() not in labels})
    for lab in missing_refs:
        warnings.append(f"Referência \\ref para '{lab}' não encontrada (figura/tabela/equação inexistente).")

    # 4. Rótulos \\label duplicados (mesmo nome definido mais de uma vez).
    for lab, count in Counter(m.group(1) for m in _LABEL.finditer(tex)).items():
        if count > 1:
            warnings.append(f"Rótulo \\label{{{lab}}} definido {count}× (pode confundir referências).")

    return warnings


def find_duplicate_ids(html: str) -> list:
    """Rede de segurança: retorna ids repetidos no HTML final (não deveria haver)."""
    ids = re.findall(r'\sid="([^"]+)"', html)
    return [i for i, c in Counter(ids).items() if c > 1]
