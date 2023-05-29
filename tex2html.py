import os
import pypandoc
from bs4 import BeautifulSoup
import re

def buscar_termos_arquivo_tex(filename):
    with open(filename, "r", encoding="utf-8") as f:
        conteudo = f.read()
    # Define uma lista com os termos que queremos buscar
    termos = [
        r"\\newcommand{\\titulocabecalho}{(.+?)}",
        r"\\newcommand{\\autorcabecalho}{(.+?)[\\\\}]",
        r"\\newcommand{\\doi}{(.+?)[\\\\}]",
        r"\\newcommand{\\volume}{(.+?)}",
        r"\\newcommand{\\numero}{(.+?)}",
        r"\\newcommand{\\paginainicial}{(.+?)}",
        r"\\newcommand{\\mes}{(.+?)}",
        r"\\newcommand{\\ano}{(.+?)}",
    ]

    # Cria um dicionário para armazenar os valores encontrados
    resultados = {}
    # Busca pelos termos no arquivo
    for termo in termos:
        match = re.search(termo, conteudo)
        if match:
            if termo == r"\\newcommand{\\paginainicial}{(.+?)}":
                resultados[termo] = ", p. " + match.group(1)
            elif termo == r"\\newcommand{\\volume}{(.+?)}":
                resultados[termo] = ", v. " + match.group(1)
            elif termo == r"\\newcommand{\\numero}{(.+?)}":
                resultados[termo] = ", n. " + match.group(1)
            elif termo == r"\\newcommand{\\mes}{(.+?)}":
                resultados[termo] = ", " + match.group(1)
            elif termo == r"\\newcommand{\\autorcabecalho}{(.+?)}":
                resultados[termo] = re.sub(r'~', ' ', match.group(1))
            else:
                resultados[termo] = match.group(1)
    return resultados

# Nome do arquivo .tex de entrada (assumindo que esteja na mesma pasta do arquivo Python)
tex_file_name = 'main.tex'

# Lê o arquivo de entrada, remove os asteriscos
with open(tex_file_name, "r", encoding="utf-8") as f:
    conteudo = f.read()
    conteudo_sem_asteriscos = re.sub(r"\\(begin|end){([^}\s]+)\*}", r"\\\1{\2}", conteudo)
    # Substituições no conteúdo atualizado do arquivo tex
    conteudo_atualizado = re.sub(r"\\begin{equation}(\s*\\label{[^}]+})", r"\\begin{equation}\g<1>", conteudo_sem_asteriscos)
    conteudo_atualizado = conteudo_atualizado.replace('\\bm{', '\\mathbf{')
    conteudo_atualizado = conteudo_atualizado.replace('\\hdots', '\\dots')
    conteudo_atualizado = re.sub(r'\\parbox\{.*?\}', '', conteudo_atualizado)
    conteudo_atualizado = conteudo_atualizado.replace('\\centering', '')
    conteudo_atualizado = conteudo_atualizado.replace(r'\begin{otherlanguage}{brazil}', '')
    conteudo_atualizado = re.sub(r'\\includegraphics(\[.*?\])?\{(.*?)(\.(?!jpeg$)\w+)?\}', lambda match: f'\\includegraphics{match.group(1)}{{{match.group(2)}{".png" if match.group(3) != ".jpeg" else match.group(3)}}}', conteudo_atualizado)

def convert_tex_to_html(tex_content):
    try:
        # Converte o conteúdo .tex para .html com a opcao --mathjax e encontra e armazena todos h1 em um vetor de strings
        output = pypandoc.convert_text(tex_content, 'html', format='tex', extra_args=['--mathjax'])
        soup = BeautifulSoup(output, 'html.parser')
        return str(soup)
    except Exception as e:
        print(f'Ocorreu um erro durante a conversão: {e}')
        return None, None

# Define a função para substituir o conteúdo necessário do html
def substituir_conteudo(conteudo_com_id):
    conteudo_com_id = conteudo_com_id.replace('\\textsuperscript{\\textregistered}', '&reg;')
    conteudo_com_id = conteudo_com_id.replace('\\textregistered', '&reg;')
    conteudo_com_id = conteudo_com_id.replace('\\copyright', '&copy;')
    return conteudo_com_id

def substituir_span(html):
    pattern = r'\\label\{([\w:]+)\}'
    matches = re.findall(pattern, html)
    ids = []

    for label in matches:
        ids.append(label)
        html = html.replace(f'\\label{{{label}}}', '')
    span_pattern = r'<span class="math display">'
    spans = re.split(span_pattern, html)

    for i, span in enumerate(spans[1:]):
        if i < len(ids):
            span_id = f'id="{ids[i]}"'
            spans[i + 1] = f'<span {span_id} class="math display">{span.strip()}</span>'
    html = ''.join(spans)
    return html

# Chame a função para realizar a conversão
html_content = convert_tex_to_html(conteudo_atualizado)
resultados = buscar_termos_arquivo_tex(tex_file_name)

if html_content is not None:
    substuido = substituir_conteudo(html_content)
    conteudo_com_id = substituir_span(substuido)
    new_html_file = f"{os.path.splitext(tex_file_name)[0]}.html"
    with open(new_html_file, 'w', encoding='utf-8') as f:
        html_content = f'''<!DOCTYPE html>
<html lang="en-US">
<head>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
    <style>
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Noto Sans, Ubuntu, Droid Sans, Helvetica Neue, sans-serif;
            word-break: normal;
            line-height: 2;
            text-align: justify;
            font-size: 15px;
            font-weight: 400;
            margin-right: 400px;
            margin-left: 400px;
            display: block;
            justify-content: center;
            align-items: center;
        }}

        h1, h2, h3 {{
            font-weight: 400;
        }}

        img {{
            max-height: 350px !important;
            max-width: 350px !important;
            display: block;
            margin-left: auto !important;
            margin-right: auto !important;
        }}

        table {{
            border-collapse: collapse;
            margin-top: 20px;
            text-align: center !important;
        }}

        thead th {{
            background-color: #f2f2f2;
            font-weight: bold;
            padding: 10px;
            text-align: center;
        }}

        tbody td {{
            padding: 10px;
            text-align: center;
        }}

        tbody tr.odd {{
            background-color: #f9f9f9;
        }}

        tbody tr:hover {{
            background-color: #e6e6e6;
        }}

        table tbody tr:last-child td {{
            border-bottom: 1px solid black;
        }}

        thead:before,
        thead:after {{
            content: "";
            display: table-row;
            border-bottom: 1px solid black;
        }}

        table {{
            margin: 0 auto;
            border-collapse: collapse;
        }} 
    </style>
    <meta charset="utf-8">
</head>
<body>
    <h1>{list(resultados.values())[0]}</h1>
    <h3>{list(resultados.values())[1]}</h3>
    <p><strong>DOI</strong> {list(resultados.values())[2]}</p>
    <p><strong>Citation</strong> Semina: Ciências Exatas e Tecnológicas, Londrina{''.join(list(resultados.values())[3:])}</p>
    <h3>Abstract:</h3>
    ''' + conteudo_com_id + '''
</body>
</html>'''
        f.write(html_content)
