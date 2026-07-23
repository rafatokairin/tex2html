"""Registro de links via *placeholders* seguros para o Pandoc.

Injetar HTML (``<a href="#x">``) diretamente no LaTeX antes do Pandoc é frágil:
caracteres como ``#``, ``<``, ``>``, ``&`` são especiais no TeX (por exemplo,
``#1`` é lido como parâmetro de macro e o Pandoc aborta). A solução é substituir
cada citação/referência por um *token* de texto puro (só letras e dígitos, que o
Pandoc não mexe), converter, e só então trocar os tokens pelo HTML final.
"""

from __future__ import annotations


class LinkRegistry:
    """Guarda o HTML de cada citação/referência atrás de um token seguro."""

    def __init__(self):
        self.map = {}
        self._n = 0

    def token(self, html: str) -> str:
        """Registra um HTML e devolve o token (texto puro) a inserir no .tex."""
        tok = f"XREF{self._n:05d}XREF"
        self._n += 1
        self.map[tok] = html
        return tok

    def apply(self, html_out: str) -> str:
        """Substitui todos os tokens pelo HTML final (após o Pandoc)."""
        for tok, html in self.map.items():
            html_out = html_out.replace(tok, html)
        return html_out
