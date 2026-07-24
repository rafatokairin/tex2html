"""Template HTML/CSS da revista (Semina: Ciências Exatas e Tecnológicas).

Mantém o layout/estilo originais do OJS, isolado da lógica de conversão e usando
campos nomeados (em vez de índices posicionais frágeis).
"""

from __future__ import annotations

from ..resources import asset_path  # noqa: F401  (reexportado por conveniência)

CSS = """
        html { scroll-behavior: smooth; }
        a { text-decoration: none; }
        body {
            font-family: 'Tinos', serif;
            word-break: normal;
            line-height: 1.5;
            text-align: justify;
            font-size: 15px;
            font-weight: 500;
            margin: 0;
            padding: 0;
        }
        .article-content { margin-right: 400px; margin-left: 400px; }
        header { width: 100%; }
        .header-container { margin: 0 !important; padding: 0 !important; }
        .header-container img {
            display: block;
            width: 100%;
            height: auto;
            min-width: 100vh;
            margin: 0 !important;
            padding: 0 !important;
        }
        .image-text {
            position: absolute;
            top: 25px;
            right: 50px;
            color: black;
            font-size: 18px;
            font-family: 'Josefin Sans', sans-serif;
            font-weight: 500;
            text-align: right;
            direction: rtl;
        }
        .search { float: left; margin-top: 0px; padding: 20px; }
        .search_input input,
        .search_input button {
            border-radius: 0;
            height: 36px;
            font-size: 15px;
            border: 1px solid #a0a0a0;
            font-weight: 500;
        }
        .blue-background { background-color: #346af3; }
        .white-icon { color: white; font-size: 15px; width: 36px; }
        .search_input button:hover { cursor: pointer; }
        .menu {
            position: fixed;
            margin-top: 0px;
            right: 0;
            padding: 10px;
            font-size: 18px;
        }
        .menu a { display: block; margin-bottom: 8px; text-decoration: none; }
        figure p span { float: right; }
        h1, h2, h3 { font-family: 'Josefin Sans', sans-serif; font-weight: 700; }
        img { display: block; max-width: 100%; height: auto; margin-left: auto !important; margin-right: auto !important; }
        table { border-collapse: collapse; margin-top: 20px; text-align: center !important; }
        thead th {
            background-color: #f2f2f2;
            font-weight: bold;
            padding: 2px 12px;
            text-align: center;
        }
        tbody td { padding: 2px 12px; text-align: center; }
        tbody tr.odd { background-color: #f9f9f9; }
        tbody tr:hover { background-color: #e6e6e6; }
        thead:before, thead:after { content: ""; display: table-row; }
        table { margin: 0 auto; border-collapse: collapse; }
        p#data { font-size: 12px; }

        /* Imagens com altura uniforme; clicar abre em tela cheia (lightbox). */
        .article-content figure img { max-height: 360px; width: auto; cursor: zoom-in; }
        #lightbox {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 9999;
            background: rgba(0, 0, 0, 0.88);
            justify-content: center;
            align-items: center;
            cursor: zoom-out;
            padding: 20px;
        }
        #lightbox img { max-width: 96%; max-height: 96%; box-shadow: 0 0 40px rgba(0,0,0,.6); }

        /* Código (verbatim, lstlisting, minted, \\texttt, \\verb). */
        code, pre { font-family: 'Consolas', 'Courier New', monospace; }
        code { background: #f4f4f4; padding: 1px 5px; border-radius: 3px; font-size: .92em; }
        pre { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px;
              padding: 12px 14px; overflow-x: auto; line-height: 1.45; text-align: left; }
        pre code { background: none; padding: 0; }
        div.sourceCode { overflow-x: auto; background: #f6f8fa; border: 1px solid #e1e4e8;
              border-radius: 6px; margin: 14px 0; padding: 4px 10px; }
        div.sourceCode pre { border: 0; background: none; padding: 8px 0; }
        code span.kw { color: #007020; font-weight: bold; }
        code span.dt { color: #902000; }
        code span.dv, code span.bn, code span.fl { color: #40a070; }
        code span.st, code span.ch, code span.sc, code span.vs { color: #4070a0; }
        code span.co { color: #60a0b0; font-style: italic; }
        code span.cf, code span.kw { color: #007020; font-weight: bold; }
        code span.op { color: #666666; }
        code span.fu { color: #06287e; }
        code span.im { color: #008000; font-weight: bold; }
        code span.va { color: #19177c; }
        code span.pp { color: #bc7a00; }
        code span.at { color: #7d9029; }

        /* Notas de rodapé (\\footnote). */
        section.footnotes { font-size: .85em; border-top: 1px solid #ccc;
              margin-top: 26px; padding-top: 8px; color: #333; }

        .nomes-container { display: flex; gap: 10px; }
        .nomes-container a { float: left; display: flex; text-decoration: none; }
        .nomes-container .orcid-icon { height: 20px; margin-left: 5px; }
        @media (max-width: 992px) {
            .article-content { margin: 10px; }
            header { display: none; }
            .search { display: none; }
            .menu { display: none; }
            h1 { font-size: 24px; }
            p { font-size: 14px; }
        }
"""

_SEARCH_ACTION = "https://ojs.uel.br/revistas/uel/index.php/semexatas/search/index"


def render_page(metadata: dict, body_html: str, menu_html: str, references_html: str) -> str:
    """Monta a página HTML completa a partir das partes já processadas."""
    m = metadata
    return f"""<!DOCTYPE html>
<html lang="en-US">
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Tinos&display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Josefin+Sans&display=swap">
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
    <script>
    function openNewPage() {{
        var query = document.getElementById("query").value;
        if (query.trim() === "")
            return false;
        var searchUrl = "{_SEARCH_ACTION}?query=" + encodeURIComponent(query);
        window.open(searchUrl, "_blank");
        return false;
    }}
    </script>
    <style>{CSS}    </style>
    <meta charset="utf-8">
</head>
<body>
    <header>
        <div class="header-container">
            <img src="Header.png">
            <div class="image-text">{m['area']}</div>
        </div>
    </header>
    <div class="search">
        <form class="_cmp_form" method="get" action="{_SEARCH_ACTION}" onsubmit="return openNewPage()">
            <div class="search_input">
                <input type="text" id="query" name="query" value="" class="query form-control" placeholder="Search">
                <button class="btn btn-primary btn-lg blue-background" type="submit">
                    <i class="fas fa-search white-icon"></i>
                </button>
            </div>
        </form>
    </div>
    <div class="menu">
        <h3>Outline:</h3>
        <a href="#article-abstract">Abstract</a>
        {menu_html}
        <a href="#article-references">References</a>
    </div>
    <div class="article-content">
        <h1>{m['title']}</h1>
        <h3>{m['author_header']}</h3>
        <p><strong>DOI</strong> {m['doi']}</p>
        <p><strong>Citation</strong> {m['citation']}</p>
        <p id="data"><strong>Received:</strong> {m['received']} <strong>Received in revised for:</strong> {m['revised']} <strong>Accepted:</strong> {m['accepted']} <strong>Available online:</strong> {m['published']}</p>
        <h3 id="article-abstract">Abstract:</h3>
        {body_html}
        <h1 id="article-references">References</h1>
        {references_html}
    </div>
    <div id="lightbox" onclick="this.style.display='none'"><img alt=""></div>
    <script>
    document.addEventListener("DOMContentLoaded", function () {{
        var box = document.getElementById("lightbox");
        var big = box.querySelector("img");
        document.querySelectorAll(".article-content figure img").forEach(function (img) {{
            img.addEventListener("click", function () {{
                big.src = img.currentSrc || img.src;
                box.style.display = "flex";
            }});
        }});
    }});
    </script>
</body>
</html>"""
