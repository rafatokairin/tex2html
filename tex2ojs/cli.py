"""Modo linha de comando: ``python main.py PASTA [-o SAIDA]``."""

from __future__ import annotations

import argparse
import sys

from .deps import check_dependencies


def run_cli(argv) -> int:
    parser = argparse.ArgumentParser(
        prog="tex2ojs",
        description="Converte uma pasta Artigo<N> (LaTeX) em HTML pronto para o OJS.",
    )
    parser.add_argument("pasta", help="Pasta do artigo (com .tex, .bib e figuras).")
    parser.add_argument("-o", "--saida", help="Pasta de saída (padrão: <pasta>_OJS).")
    args = parser.parse_args(argv)

    problems = check_dependencies()
    if problems:
        print("Dependências faltando:\n - " + "\n - ".join(problems), file=sys.stderr)
        return 2

    from . import convert_article

    try:
        result = convert_article(args.pasta, args.saida, log=print)
    except Exception as exc:  # noqa: BLE001
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1

    print(f"\nOK! {len(result.images)} imagem(ns) convertida(s).")
    print(f"Pasta pronta para o OJS: {result.output_dir}")
    if result.warnings:
        print("\nAvisos:")
        for w in result.warnings:
            print(f" - {w}")
    return 0
