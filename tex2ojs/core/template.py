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

        /* Autores: nome + ícone ORCID (SVG) do tamanho da linha do texto. */
        h3.authors { font-weight: 500; line-height: 1.8; }
        .authors .author { white-space: nowrap; }
        .authors .orcid-link { text-decoration: none; }
        .orcid-icon {
            height: 1em;
            width: 1em;
            vertical-align: -0.15em;
            margin-left: 3px;
        }

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

        @media (max-width: 992px) {
            .article-content { margin: 10px; }
            header { display: none; }
            .search { display: none; }
            .menu { display: none; }
            h1 { font-size: 24px; }
            p { font-size: 14px; }
        }


        .iThenticate_logo{
            display:flex; 
            justify-content:flex-end;
        }

        figure table {
            width: auto;
            border-collapse: separate;
        }
        figure th, figure td {
            padding: 0px 0px;
            border-bottom: 0px solid #000;
            border-right: 0px solid #000;
        }
        figure thead th {
            border-bottom: 0px solid #000; /* destaca o cabeçalho */
            border-right: 0px solid #000;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 6px 8px;
            border-bottom: 1px solid #000;
        }

        thead th {
            border-bottom: 2px solid #000; /* destaca o cabeçalho */
        }

"""

#O último trecho de 6 props do CSS foi colocado agora para formatar tabelas e figuras dentro de tabelas

_SEARCH_ACTION = "https://ojs.uel.br/revistas/uel/index.php/semexatas/search/index"


# Logo oficial do ORCID (iD) como SVG inline — sempre renderiza, sem depender de
# um arquivo de imagem (que poderia não carregar e mostrar o texto "ORCID").
ORCID_SVG = (
    '<svg class="orcid-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" '
    'role="img" aria-label="ORCID">'
    '<path fill="#A6CE39" d="M256 128c0 70.7-57.3 128-128 128S0 198.7 0 128 57.3 0 128 0s128 57.3 128 128z"/>'
    '<path fill="#FFF" d="M86.3 186.2H70.9V79.1h15.4v107.1z"/>'
    '<path fill="#FFF" d="M108.9 79.1h41.6c39.6 0 57 28.3 57 53.6 0 27.5-21.5 53.6-56.8 53.6h-41.8V79.1zm15.4 93.4h24.5c34.9 0 42.9-26.5 42.9-39.8 0-21.5-13.7-39.7-43.7-39.7h-23.7v79.5z"/>'
    '<path fill="#FFF" d="M88.7 56.8c0 5.5-4.5 10.1-10.1 10.1s-10.1-4.6-10.1-10.1c0-5.6 4.5-10.1 10.1-10.1 5.6 0 10.1 4.6 10.1 10.1z"/>'
    "</svg>"
)


def _render_authors(metadata: dict) -> str:
    """Nomes completos dos autores, cada um com o ícone ORCID linkado ao lado."""
    authors = metadata.get("authors") or []
    if not authors:
        return metadata.get("author_header", "")
    partes = []
    for a in authors:
        nome = a["name"]
        orcid = a.get("orcid", "").strip()
        if orcid:
            url = orcid if orcid.startswith("http") else f"https://orcid.org/{orcid}"
            nome += (f' <a class="orcid-link" href="{url}" target="_blank" '
                     f'title="ORCID de {nome}">{ORCID_SVG}</a>')
        partes.append(f'<span class="author">{nome}</span>')
    return ", ".join(partes)


def render_page(metadata: dict, body_html: str, menu_html: str, references_html: str) -> str:
    """Monta a página HTML completa a partir das partes já processadas."""
    m = metadata
    authors_html = _render_authors(m)
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




    
    <div class="iThenticate_logo">
        <div style="
        width:200px; height:80px;
        background-image:url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTI0IiBoZWlnaHQ9IjI3NCIgdmlld0JveD0iMCAwIDkyNCAyNzQiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik04MjMgMTAzLjlIODI0LjJWMTAwLjdIODI0LjlDODI1LjggMTAwLjcgODI2LjIgMTAxIDgyNy4xIDEwMi43TDgyNy44IDEwMy45SDgyOS4zTDgyOC40IDEwMi40QzgyNy44IDEwMS40IDgyNy4zIDEwMC43IDgyNi42IDEwMC41QzgyNy45IDEwMC40IDgyOC44IDk5LjUgODI4LjggOTguM0M4MjguOCA5Ny41IDgyOC4yIDk2LjMgODI2LjMgOTYuM0g4MjNWMTAzLjlaTTgyNC4yIDk5LjZWOTcuNEg4MjYuMkM4MjcgOTcuNCA4MjcuNiA5Ny45IDgyNy42IDk4LjVDODI3LjYgOTkuMyA4MjcgOTkuNyA4MjYgOTkuN0g4MjQuMlY5OS42Wk04MzEuOSAxMDBDODMxLjkgMTAzLjIgODI5LjMgMTA1LjkgODI2IDEwNS45QzgyMi43IDEwNS45IDgyMC4xIDEwMy4zIDgyMC4xIDEwMEM4MjAuMSA5Ni43IDgyMi43IDk0LjEgODI2IDk0LjFDODI5LjMgOTQuMSA4MzEuOSA5Ni43IDgzMS45IDEwMFpNODMzLjEgMTAwQzgzMy4xIDk2LjEgODI5LjkgOTMgODI2IDkzQzgyMi4xIDkzIDgxOSA5Ni4xIDgxOSAxMDBDODE5IDEwMy45IDgyMi4xIDEwNy4xIDgyNiAxMDcuMUM4MjkuOSAxMDcgODMzLjEgMTAzLjkgODMzLjEgMTAwWiIgZmlsbD0iIzAwM0M0NiIvPgo8cGF0aCBkPSJNMjM5LjEgMTc5LjhWMTE3LjlIMjUzLjZWMTc5LjhIMjM5LjFaIiBmaWxsPSIjMDAzQzQ2Ii8+CjxwYXRoIGQ9Ik0yODYuOSAxNzkuOFYxMTEuN0gyNjMuNFY5Ny42MDAxSDMyNi40VjExMS43SDMwMi4yVjE3OS44SDI4Ni45WiIgZmlsbD0iIzAwM0M0NiIvPgo8cGF0aCBkPSJNMzg1LjEgMTI3LjlDMzgzLjUgMTI0LjEgMzgxLjEgMTIxLjMgMzc3LjkgMTE5LjRDMzc0LjggMTE3LjUgMzcwLjkgMTE2LjYgMzY2LjIgMTE2LjZDMzYyLjkgMTE2LjYgMzU5LjcgMTE3LjMgMzU2LjYgMTE4LjdDMzUzLjUgMTIwLjEgMzUwLjggMTIyIDM0OC41IDEyNC4zQzM0Ny44IDEyNSAzNDcuMiAxMjUuNyAzNDYuNiAxMjYuNVY5Mi44SDMzMi4zVjE3OS43QzMzMy4zIDE3OS43IDMzNC40IDE3OS43IDMzNS42IDE3OS43QzMzNi45IDE3OS43IDMzOC4yIDE3OS43IDMzOS42IDE3OS43SDM0Ni44VjE0Mi4zQzM0Ni44IDE0MC40IDM0Ny4yIDEzOC43IDM0Ny45IDEzNy4xQzM0OC43IDEzNS41IDM0OS43IDEzNC4yIDM1MSAxMzNDMzUyLjMgMTMxLjcgMzUzLjkgMTMwLjggMzU1LjYgMTMwLjJDMzU3LjQgMTI5LjUgMzU5LjQgMTI5LjEgMzYxLjUgMTI5LjFDMzY0LjEgMTI5IDM2Ni4zIDEyOS41IDM2OC4xIDEzMC41QzM2OS45IDEzMS40IDM3MS4yIDEzMyAzNzIuMSAxMzUuMUMzNzMgMTM3LjEgMzczLjQgMTM5LjcgMzczLjQgMTQyLjlWMTc5LjdIMzg3LjlWMTQxLjlDMzg3LjYgMTM2LjQgMzg2LjggMTMxLjcgMzg1LjEgMTI3LjlaIiBmaWxsPSIjMDAzQzQ2Ii8+CjxwYXRoIGQ9Ik00NTIuNCAxNDdDNDUyLjUgMTQyLjYgNDUxLjggMTM4LjYgNDUwLjQgMTM0LjlDNDQ5LjEgMTMxLjEgNDQ3LjEgMTI3LjkgNDQ0LjUgMTI1LjNDNDQxLjkgMTIyLjYgNDM4LjkgMTIwLjQgNDM1LjMgMTE4LjhDNDMxLjggMTE3LjIgNDI4IDExNi41IDQyMy45IDExNi41QzQxOS4zIDExNi41IDQxNSAxMTcuMyA0MTEuMSAxMTlDNDA3LjMgMTIwLjYgNDAzLjkgMTIyLjggNDAxLjEgMTI1LjhDMzk4LjQgMTI4LjcgMzk2LjIgMTMyLjEgMzk0LjYgMTM2LjFDMzkzIDE0MC4xIDM5Mi4yIDE0NC41IDM5Mi4yIDE0OS40QzM5Mi4yIDE1NS41IDM5My42IDE2MSAzOTYuMyAxNjUuN0MzOTkuMSAxNzAuNCA0MDMgMTc0LjEgNDA3LjkgMTc2LjlDNDEyLjkgMTc5LjYgNDE4LjcgMTgxIDQyNS4yIDE4MUM0MjguMSAxODEgNDMxIDE4MC42IDQzNCAxNzkuOEM0MzcgMTc5IDQzOS44IDE3OCA0NDIuNSAxNzYuNkM0NDUuMiAxNzUuMiA0NDcuNyAxNzMuNSA0NDkuOCAxNzEuNUw0NDIuNiAxNjEuNUM0MzkuOCAxNjMuOSA0MzcuMiAxNjUuNiA0MzQuNyAxNjYuNkM0MzIuMyAxNjcuNSA0MjkuNiAxNjggNDI2LjcgMTY4QzQyMi41IDE2OCA0MTguOSAxNjcuMiA0MTUuOCAxNjUuN0M0MTIuNyAxNjQuMSA0MTAuNCAxNjEuNyA0MDguNiAxNTguOEM0MDcuNSAxNTYuOCA0MDYuOCAxNTQuNiA0MDYuNCAxNTIuMUg0NTIuMUw0NTIuNCAxNDdaTTQxNC4yIDEzMS41QzQxNi45IDEzMCA0MjAuMSAxMjkuMyA0MjQgMTI5LjNDNDI2LjUgMTI5LjMgNDI4LjggMTI5LjggNDMwLjggMTMwLjlDNDMyLjkgMTMxLjkgNDM0LjYgMTMzLjQgNDM2IDEzNS4yQzQzNy4zIDEzNyA0MzguMSAxMzkuMSA0MzguMyAxNDEuNVYxNDIuMUg0MDYuOUM0MDcuMiAxNDAuNSA0MDcuNyAxMzkuMSA0MDguMyAxMzcuOUM0MDkuNiAxMzUuMiA0MTEuNiAxMzMgNDE0LjIgMTMxLjVaIiBmaWxsPSIjMDAzQzQ2Ii8+CjxwYXRoIGQ9Ik01MTEuNSAxMjcuOUM1MDkuOSAxMjQuMSA1MDcuNSAxMjEuMyA1MDQuMyAxMTkuNEM1MDEuMiAxMTcuNSA0OTcuMyAxMTYuNiA0OTIuNiAxMTYuNkM0ODkuMyAxMTYuNiA0ODYuMSAxMTcuMyA0ODMgMTE4LjdDNDc5LjkgMTIwLjEgNDc3LjIgMTIyIDQ3NC45IDEyNC4zQzQ3NC4yIDEyNSA0NzMuNSAxMjUuOCA0NzIuOSAxMjYuNkw0NzIuNyAxMTcuOUg0NTguNlYxNzkuOEM0NTkuNiAxNzkuOCA0NjAuNyAxNzkuOCA0NjEuOSAxNzkuOEM0NjMuMiAxNzkuOCA0NjQuNSAxNzkuOCA0NjUuOSAxNzkuOEg0NzMuMVYxNDIuNEM0NzMuMSAxNDAuNSA0NzMuNSAxMzguOCA0NzQuMiAxMzcuMkM0NzUgMTM1LjYgNDc2IDEzNC4zIDQ3Ny4zIDEzMy4xQzQ3OC42IDEzMS44IDQ4MC4yIDEzMC45IDQ4MS45IDEzMC4zQzQ4My43IDEyOS42IDQ4NS43IDEyOS4yIDQ4Ny44IDEyOS4yQzQ5MC40IDEyOS4xIDQ5Mi42IDEyOS42IDQ5NC40IDEzMC42QzQ5Ni4yIDEzMS41IDQ5Ny41IDEzMy4xIDQ5OC40IDEzNS4yQzQ5OS4zIDEzNy4yIDQ5OS43IDEzOS44IDQ5OS43IDE0M1YxNzkuOEg1MTRWMTQyQzUxNCAxMzYuNCA1MTMuMiAxMzEuNyA1MTEuNSAxMjcuOVoiIGZpbGw9IiMwMDNDNDYiLz4KPHBhdGggZD0iTTU2NC42IDE3OS44VjExNy45SDU3OVYxNzkuOEg1NjQuNloiIGZpbGw9IiMwMDNDNDYiLz4KPHBhdGggZD0iTTYxNy40IDE4MUM2MTEuNiAxODEgNjA2LjQgMTc5LjYgNjAxLjggMTc2LjhDNTk3LjIgMTc0IDU5My41IDE3MC4xIDU5MC45IDE2NS4zQzU4OC4yIDE2MC40IDU4Ni45IDE1NSA1ODYuOSAxNDguOUM1ODYuOSAxNDIuOCA1ODguMiAxMzcuMyA1OTAuOSAxMzIuNUM1OTMuNiAxMjcuNyA1OTcuMiAxMjMuOCA2MDEuOCAxMjFDNjA2LjQgMTE4LjIgNjExLjYgMTE2LjggNjE3LjQgMTE2LjhDNjIzIDExNi44IDYyOCAxMTcuOSA2MzIuNiAxMjBDNjM3LjEgMTIyLjEgNjQwLjcgMTI1LjEgNjQzLjIgMTI4LjhMNjM1LjIgMTM4LjRDNjM0IDEzNi44IDYzMi41IDEzNS4zIDYzMC43IDEzMy45QzYyOC45IDEzMi42IDYyNyAxMzEuNSA2MjQuOSAxMzAuN0M2MjIuOSAxMjkuOSA2MjAuOCAxMjkuNSA2MTguOCAxMjkuNUM2MTUuNCAxMjkuNSA2MTIuMyAxMzAuNCA2MDkuNSAxMzIuMUM2MDYuOCAxMzMuNyA2MDQuNyAxMzYuMSA2MDMuMiAxMzlDNjAxLjYgMTQxLjkgNjAwLjkgMTQ1LjIgNjAwLjkgMTQ4LjlDNjAwLjkgMTUyLjYgNjAxLjcgMTU1LjkgNjAzLjIgMTU4LjhDNjA0LjggMTYxLjcgNjA3IDE2NCA2MDkuOCAxNjUuN0M2MTIuNSAxNjcuNCA2MTUuNiAxNjguMyA2MTkgMTY4LjNDNjIxIDE2OC4zIDYyMyAxNjggNjI0LjkgMTY3LjRDNjI2LjkgMTY2LjcgNjI4LjcgMTY1LjcgNjMwLjQgMTY0LjVDNjMyLjEgMTYzLjIgNjMzLjcgMTYxLjcgNjM1LjIgMTU5LjhMNjQzLjIgMTY5LjZDNjQwLjUgMTczIDYzNi45IDE3NS45IDYzMi4yIDE3OC4xQzYyNy41IDE3OS45IDYyMi42IDE4MSA2MTcuNCAxODFaIiBmaWxsPSIjMDAzQzQ2Ii8+CjxwYXRoIGQ9Ik02OTQuOCAxMTcuOVYxMjYuN0M2OTMuNiAxMjQuOSA2OTIuMiAxMjMuMiA2OTAuNSAxMjEuOEM2ODguNSAxMjAuMiA2ODYuMyAxMTguOSA2ODMuNyAxMThDNjgxLjEgMTE3LjEgNjc4LjMgMTE2LjYgNjc1LjEgMTE2LjZDNjY5LjcgMTE2LjYgNjY0LjggMTE4IDY2MC41IDEyMC43QzY1Ni4yIDEyMy40IDY1Mi44IDEyNy4yIDY1MC4zIDEzMi4xQzY0Ny44IDEzNyA2NDYuNSAxNDIuNSA2NDYuNSAxNDguN0M2NDYuNSAxNTQuOSA2NDcuOCAxNjAuNCA2NTAuMyAxNjUuM0M2NTIuOCAxNzAuMiA2NTYuMSAxNzQgNjYwLjMgMTc2LjhDNjY0LjUgMTc5LjYgNjY5LjEgMTgxIDY3NC4yIDE4MUM2NzcuMiAxODEgNjgwIDE4MC41IDY4Mi41IDE3OS42QzY4NS4yIDE3OC43IDY4Ny42IDE3Ny40IDY4OS43IDE3NkM2OTEuNyAxNzQuNiA2OTMuNCAxNzIuOSA2OTQuOCAxNzEuMlYxNzkuOUg3MDkuNVYxMThINjk0LjhWMTE3LjlaTTY4NyAxNjUuN0M2ODQuNCAxNjcuMyA2ODEuNCAxNjguMiA2NzguMSAxNjguMkM2NzQuNyAxNjguMiA2NzEuOCAxNjcuNCA2NjkuMiAxNjUuN0M2NjYuNyAxNjQuMSA2NjQuNyAxNjEuOCA2NjMuMyAxNTguOUM2NjEuOSAxNTUuOSA2NjEuMiAxNTIuNSA2NjEuMiAxNDguN0M2NjEuMiAxNDQuOSA2NjEuOSAxNDEuNiA2NjMuMyAxMzguN0M2NjQuNyAxMzUuOCA2NjYuNyAxMzMuNSA2NjkuMiAxMzEuOUM2NzEuOCAxMzAuMyA2NzQuOCAxMjkuNCA2NzguMSAxMjkuNEM2ODEuNSAxMjkuNCA2ODQuNCAxMzAuMiA2ODcgMTMxLjlDNjg5LjYgMTMzLjUgNjkxLjYgMTM1LjggNjkzIDEzOC43QzY5NC41IDE0MS42IDY5NS4yIDE0NC45IDY5NS4yIDE0OC43QzY5NS4yIDE1Mi41IDY5NC41IDE1NS45IDY5MyAxNTguOUM2OTEuNiAxNjEuOCA2ODkuNiAxNjQuMSA2ODcgMTY1LjdaIiBmaWxsPSIjMDAzQzQ2Ii8+CjxwYXRoIGQ9Ik04MjMuMiAxNDdDODIzLjMgMTQyLjYgODIyLjYgMTM4LjYgODIxLjIgMTM0LjlDODE5LjkgMTMxLjEgODE3LjkgMTI3LjkgODE1LjMgMTI1LjNDODEyLjcgMTIyLjYgODA5LjcgMTIwLjQgODA2LjEgMTE4LjhDODAyLjYgMTE3LjIgNzk4LjggMTE2LjUgNzk0LjcgMTE2LjVDNzkwLjEgMTE2LjUgNzg1LjggMTE3LjMgNzgxLjkgMTE5Qzc3OC4xIDEyMC42IDc3NC43IDEyMi44IDc3MS45IDEyNS44Qzc2OS4yIDEyOC43IDc2NyAxMzIuMSA3NjUuNCAxMzYuMUM3NjMuOCAxNDAuMSA3NjMuMSAxNDQuNSA3NjMuMSAxNDkuNEM3NjMuMSAxNTUuNSA3NjQuNSAxNjEgNzY3LjIgMTY1LjdDNzcwIDE3MC40IDc3My45IDE3NC4xIDc3OC44IDE3Ni45Qzc4My44IDE3OS42IDc4OS42IDE4MSA3OTYuMSAxODFDNzk5IDE4MSA4MDEuOSAxODAuNiA4MDQuOSAxNzkuOEM4MDcuOSAxNzkgODEwLjcgMTc4IDgxMy40IDE3Ni42QzgxNi4xIDE3NS4yIDgxOC42IDE3My41IDgyMC43IDE3MS41TDgxMy41IDE2MS41QzgxMC43IDE2My45IDgwOC4xIDE2NS42IDgwNS42IDE2Ni42QzgwMy4yIDE2Ny41IDgwMC41IDE2OCA3OTcuNiAxNjhDNzkzLjQgMTY4IDc4OS44IDE2Ny4yIDc4Ni43IDE2NS43Qzc4My42IDE2NC4xIDc4MS4zIDE2MS43IDc3OS41IDE1OC44Qzc3OC40IDE1Ni44IDc3Ny43IDE1NC42IDc3Ny4zIDE1Mi4xSDgyM0w4MjMuMiAxNDdaTTc4NSAxMzEuNUM3ODcuNyAxMzAgNzkwLjkgMTI5LjMgNzk0LjggMTI5LjNDNzk3LjMgMTI5LjMgNzk5LjYgMTI5LjggODAxLjYgMTMwLjlDODAzLjcgMTMxLjkgODA1LjQgMTMzLjQgODA2LjggMTM1LjJDODA4LjEgMTM3IDgwOC45IDEzOS4xIDgwOS4xIDE0MS41VjE0Mi4xSDc3Ny43Qzc3OCAxNDAuNSA3NzguNSAxMzkuMSA3NzkuMSAxMzcuOUM3ODAuNSAxMzUuMiA3ODIuNCAxMzMgNzg1IDEzMS41WiIgZmlsbD0iIzAwM0M0NiIvPgo8cGF0aCBkPSJNNTQzLjIgMTAyLjhINTI5LjRWMTE4SDUxN1YxMzEuNkg1MjkuM1YxNjMuNUw1MjkuNCAxNjMuNEM1MzAuMSAxNzUuMiA1MzUuNCAxNzkuOCA1NDcuOSAxNzkuOEM1NTIgMTc5LjggNTU0LjIgMTc5LjYgNTU0LjMgMTc5LjZMNTU1LjMgMTc5LjVWMTY2LjhMNTU0LjEgMTY2LjlDNTU0LjEgMTY2LjkgNTUxLjUgMTY3LjEgNTUwLjMgMTY3LjFDNTQ0LjQgMTY3LjEgNTQzLjIgMTY1LjcgNTQzLjIgMTU5VjEzMS42SDU1N1YxMThINTQzLjJWMTAyLjhaIiBmaWxsPSIjMDAzQzQ2Ii8+CjxwYXRoIGQ9Ik03NDMuMiAxMDIuOEg3MjkuNFYxMThINzE3VjEzMS42SDcyOS4zVjE2My41TDcyOS40IDE2My40QzczMC4xIDE3NS4yIDczNS40IDE3OS44IDc0Ny45IDE3OS44Qzc1MiAxNzkuOCA3NTQuMiAxNzkuNiA3NTQuMyAxNzkuNkw3NTUuMyAxNzkuNVYxNjYuOEw3NTQuMSAxNjYuOUM3NTQuMSAxNjYuOSA3NTEuNSAxNjcuMSA3NTAuMyAxNjcuMUM3NDQuNCAxNjcuMSA3NDMuMiAxNjUuNyA3NDMuMiAxNTlWMTMxLjZINzU3VjExOEg3NDMuMlYxMDIuOFoiIGZpbGw9IiMwMDNDNDYiLz4KPHBhdGggZD0iTTI1NC44IDk4LjQwMDJDMjU0LjggMTAzIDI1MS4xIDEwNi42IDI0Ni42IDEwNi42QzI0Mi4xIDEwNi42IDIzOC40IDEwMi45IDIzOC40IDk4LjQwMDJDMjM4LjQgOTMuODAwMiAyNDIuMSA5MC4yMDAyIDI0Ni42IDkwLjIwMDJDMjUxLjEgOTAuMjAwMiAyNTQuOCA5My45MDAyIDI1NC44IDk4LjQwMDJaIiBmaWxsPSIjMDAzQzQ2Ii8+CjxwYXRoIGQ9Ik01ODAuNSA5OC40MDAyQzU4MC41IDEwMyA1NzYuOCAxMDYuNiA1NzIuMyAxMDYuNkM1NjcuOCAxMDYuNiA1NjQuMSAxMDIuOSA1NjQuMSA5OC40MDAyQzU2NC4xIDkzLjgwMDIgNTY3LjggOTAuMjAwMiA1NzIuMyA5MC4yMDAyQzU3Ni44IDkwLjIwMDIgNTgwLjUgOTMuOTAwMiA1ODAuNSA5OC40MDAyWiIgZmlsbD0iIzAwM0M0NiIvPgo8cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTIxMyAxMDUuOUwxNDQuMiAxNzYuNUMxMzkuOSAxODAuOSAxMzIuOCAxODEuMSAxMjguMiAxNzdMOTAgMTQyTDEwNS41IDEyNS4xTDEzNS41IDE1Mi42TDE5Ni41IDkwTDIxMyAxMDUuOVoiIGZpbGw9IiMwMDk2RkYiLz4KPC9zdmc+Cg==');
        background-repeat:no-repeat;
        background-position:right center;
        background-size:contain;">
        </div>
    </div>




    <div class="menu">
        <h3>Outline:</h3>
        <a href="#article-abstract">Abstract</a>
        {menu_html}
        <a href="#article-references">References</a>
    </div>
    <div class="article-content">
        <h1>{m['title']}</h1>
        <h3 class="authors">{authors_html}</h3>
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
