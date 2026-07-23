"""Localização de assets e do Pandoc — funciona tanto em desenvolvimento
quanto no executável gerado pelo PyInstaller (``sys._MEIPASS``)."""

from __future__ import annotations

import os
import sys


def _base_dir() -> str:
    """Pasta base onde ficam os assets.

    - Executável (PyInstaller): ``sys._MEIPASS``.
    - Desenvolvimento: a raiz do projeto (pasta que contém o pacote ``tex2ojs``).
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return meipass
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def asset_path(name: str) -> str:
    """Caminho absoluto de um arquivo dentro de ``assets/``."""
    return os.path.join(_base_dir(), "assets", name)


def setup_bundled_pandoc() -> None:
    """Aponta o pypandoc para um Pandoc empacotado em ``assets/``, se existir.

    Só é necessário quando o Pandoc é distribuído junto do executável. Com
    ``pypandoc_binary``, o Pandoc já vem dentro do pacote e isto vira no-op.
    """
    for name in ("pandoc.exe", "pandoc"):
        candidate = asset_path(name)
        if os.path.isfile(candidate):
            os.environ.setdefault("PYPANDOC_PANDOC", candidate)
            return
