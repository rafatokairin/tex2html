"""Verificação de erros comuns de LaTeX que fazem o Pandoc abortar.

Serve para transformar um crash críptico do Pandoc num aviso claro e acionável
para o usuário (ex.: "chave '{' sem fechar por volta da linha 324").
"""

from __future__ import annotations

import re

from .text import strip_comments


def lint_tex(tex: str) -> list:
    """Retorna uma lista de problemas prováveis (vazia se nada suspeito)."""
    issues = []
    body = strip_comments(tex)

    # Chaves desbalanceadas (causa mais comum de "unexpected \\end{document}").
    stack = []
    for i, line in enumerate(body.splitlines(), 1):
        for m in re.finditer(r"(?<!\\)[{}]", line):
            if m.group() == "{":
                stack.append(i)
            elif stack:
                stack.pop()
            else:
                issues.append(f"Chave '}}' a mais por volta da linha {i} (sem '{{' correspondente).")
    if stack:
        issues.append(
            f"Há {len(stack)} chave(s) '{{' sem fechar — a primeira sem par está por volta da "
            f"linha {stack[-1]}. Procure um '{{' que ficou sem o '}}' correspondente."
        )

    # Matemática inline sem par.
    dollars = len(re.findall(r"(?<!\\)\$", body))
    if dollars % 2 == 1:
        issues.append("Há um '$' de matemática sem par (quantidade ímpar de '$').")

    return issues
