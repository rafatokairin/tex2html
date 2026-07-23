"""Checagem amigável das dependências (Pandoc, Pillow, BeautifulSoup)."""

from __future__ import annotations


def check_dependencies() -> list:
    """Retorna uma lista de mensagens de problema (vazia se estiver tudo ok)."""
    problems = []

    try:
        import pypandoc
        try:
            pypandoc.get_pandoc_version()
        except OSError:
            problems.append(
                "Pandoc não encontrado. Instale o Pandoc (https://pandoc.org/installing.html) "
                "ou rode uma vez em Python: import pypandoc; pypandoc.download_pandoc()."
            )
    except ImportError:
        problems.append(
            "Biblioteca 'pypandoc' não instalada. Rode: pip install pypandoc_binary"
        )

    try:
        import PIL  # noqa: F401
    except ImportError:
        problems.append("Biblioteca 'Pillow' não instalada. Rode: pip install Pillow")

    try:
        import bs4  # noqa: F401
    except ImportError:
        problems.append(
            "Biblioteca 'beautifulsoup4' não instalada. Rode: pip install beautifulsoup4"
        )

    return problems
