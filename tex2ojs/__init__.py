"""tex2ojs — conversor LaTeX → HTML para o OJS (revista Semina).

Ponto de entrada programático:

    from tex2ojs import convert_article
    result = convert_article("Artigo46/")
"""

from .core.pipeline import ConversionResult, convert_article

__all__ = ["convert_article", "ConversionResult"]
__version__ = "2.0.0"
