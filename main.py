#!/usr/bin/env python3
"""Ponto de entrada do conversor Tex2HTML (LaTeX → HTML para o OJS).

    python main.py            -> abre a interface gráfica
    python main.py PASTA      -> converte pela linha de comando
    python main.py PASTA -o SAIDA

A pasta deve conter o arquivo .tex, o .bib e a pasta de figuras (ex.: Artigo46/).
A saída é uma pasta pronta para o OJS: o HTML + todas as imagens em PNG.
"""

from __future__ import annotations

import sys

from tex2ojs.resources import setup_bundled_pandoc

setup_bundled_pandoc()


def main() -> int:
    args = sys.argv[1:]
    if args:
        from tex2ojs.cli import run_cli
        return run_cli(args)

    try:
        from tex2ojs.ui.app import run_gui
        return run_gui()
    except Exception as exc:  # noqa: BLE001 - ex.: ambiente sem display/Tkinter
        print(f"Não foi possível abrir a interface gráfica: {exc}", file=sys.stderr)
        print("Use pela linha de comando: python main.py PASTA", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
