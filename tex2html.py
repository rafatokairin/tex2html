import os
import pypandoc
from bs4 import BeautifulSoup
import re

def copy_abstract_eng(tex_file_name):
    with open(tex_file_name, "r", encoding="utf-8") as f:
        conteudo = f.read()
        # Encontrar o texto do resumo em inglês
        start = conteudo.find(r"\AbstractENG{") + len(r"\AbstractENG{")
        end = start
        count = 1
        while count > 0 and end < len(conteudo):
            if conteudo[end] == '{':
                count += 1
            elif conteudo[end] == '}':
                count -= 1
            end += 1

        if start >= 0 and end >= 0:
            abstract = conteudo[start:end-1].strip()
        else:
            return "Texto não encontrado!"
        # Encontrar o texto das palavras-chave em inglês
        start = conteudo.find(r"\KeywordsENG{") + len(r"\KeywordsENG{")
        end = start
        count = 1
        while count > 0 and end < len(conteudo):
            if conteudo[end] == '{':
                count += 1
            elif conteudo[end] == '}':
                count -= 1
            end += 1
        if start >= 0 and end >= 0:
            keywords = conteudo[start:end-1].strip()
        else:
            return "Texto não encontrado!"
        # Adicionar as palavras-chave ao resumo em inglês
        abstract_with_keywords = abstract + "\n\nKeywords: " + keywords
        return abstract_with_keywords

def buscar_termos_arquivo_tex(filename):
    with open(filename, "r", encoding="utf-8") as f:
        conteudo = f.read()
    conteudo = conteudo.replace("~", " ")
    conteudo = conteudo.replace("\\\\", "")
    # Define uma lista com os termos que queremos buscar
    termos = [
        r"\\ArticleTitleENG{(.+?)}",
        r"\\AuthorHeader{(.+?)[\\\\}]",
        r"\\DOI{(.+?)[\\\\}]",
        r"\\Volume{(.+?)}",
        r"\\InitialPage{(.+?)}",
        r"\\Month{(.+?)}",
        r"\\Year{(.+?)}",
    ]
    # Cria um dicionário para armazenar os valores encontrados
    resultados = {}
    # Busca pelos termos no arquivo
    for termo in termos:
        match = re.search(termo, conteudo)
        if match:
            if termo == r"\\InitialPage{(.+?)}":
                resultados[termo] = ", p. " + match.group(1)
            elif termo == r"\\Volume{(.+?)}":
                resultados[termo] = ", v. " + match.group(1)
            elif termo == r"\\Month{(.+?)}":
                resultados[termo] = ", " + match.group(1)
            elif termo == r"\\AuthorHeader{(.+?)}":
                resultados[termo] = re.sub(r'~', ' ', match.group(1))
            elif termo == r"\\Year{(.+?)}":
                resultados[termo] = " " + match.group(1)
            else:
                resultados[termo] = match.group(1)
    return resultados

def replace_insert_figure(match):
    options = match.group(1)
    filename = match.group(2)
    label = match.group(3)
    caption = match.group(4)
    # Extração do valor da escala
    scale_match = re.search(r'scale=(\d+(\.\d+)?)', options)
    if scale_match:
        scale = scale_match.group(1)
        options = options.replace(f'scale={scale}', f'width={scale}\\textwidth')
    figure_content = fr'''
\begin{{figure}}
\begin{{center}}
\includegraphics{options}{{{filename}}}
\caption{{{caption}}}
\label{{fig:{label}}}
\end{{center}}
\end{{figure}}
'''
    return figure_content

# Nome do arquivo .tex de entrada (assumindo que esteja na mesma pasta do arquivo Python)
tex_file_name = 'Article1.tex'

# Lê o arquivo de entrada, remove os asteriscos
with open(tex_file_name, "r", encoding="utf-8") as f:
    conteudo = f.read()
    conteudo_sem_asteriscos = re.sub(r"\\(begin|end){([^}\s]+)\*}", r"\\\1{\2}", conteudo)
    # Substituições no conteúdo atualizado do arquivo tex
    conteudo_atualizado = re.sub(r"\\begin{equation}(\s*\\label{[^}]+})", r"\\begin{equation}\g<1>", conteudo_sem_asteriscos)
    conteudo_atualizado = re.sub(r"\\begin{eqnarray}(\s*\\label{[^}]+})", r"\\begin{eqnarray}\g<1>", conteudo_atualizado)
    conteudo_atualizado = conteudo_atualizado.replace('\\bm{', '\\mathbf{')
    conteudo_atualizado = conteudo_atualizado.replace('\\hdots', '\\dots')
    conteudo_atualizado = conteudo_atualizado.replace('\\centering', '')
    conteudo_atualizado = re.sub(r'\\hspace{.*?}', '', conteudo_atualizado)
    conteudo_atualizado = re.sub(r'\\InsertFigure(\[.*?\])?\{(.*?)\}\{(.*?)\}\{(.*?)\}', replace_insert_figure, conteudo_atualizado)
    conteudo_atualizado = re.sub(r'\\includegraphics(\[.*?\])?\{(.*?)(\.(?!jpeg$)\w+)?\}', lambda match: f'\\includegraphics{match.group(1)}{{{match.group(2)}{".png" if match.group(3) != ".jpeg" else match.group(3)}}}', conteudo_atualizado)
    conteudo_atualizado = re.sub(r"(\\begin{document})", r"\1\n" + copy_abstract_eng(tex_file_name) + "\n", conteudo_atualizado, 1, re.DOTALL)
    conteudo_atualizado = conteudo_atualizado.replace('\\resizebox{\columnwidth}{!}', '')
    conteudo_atualizado = conteudo_atualizado.replace('\\columnwidth', '\\textwidth')

def convert_tex_to_html(tex_content):
    try:
        # Converte o conteúdo .tex para .html com a opcao --mathjax
        output = pypandoc.convert_text(tex_content, 'html', format='tex', extra_args=['--mathjax'])
        return output
    except Exception as e:
        print(f'Ocorreu um erro durante a conversão: {e}')
        return None

# Define a função para substituir o conteúdo necessário do html
def substituir_conteudo(conteudo_com_id):
    conteudo_com_id = conteudo_com_id.replace('\\textsuperscript{\\textregistered}', '&reg;')
    conteudo_com_id = conteudo_com_id.replace('\\textregistered', '&reg;')
    conteudo_com_id = conteudo_com_id.replace('\\copyright', '&copy;')
    conteudo_com_id = re.sub(r'class="math display">\\\[\\label\{([^}]*)\}', r'class="math display" id="\1">\\[', conteudo_com_id)
    # Extrair o valor numérico do estilo (95.0)
    regex = r'style="width:(\d+\.\d+)%"'
    matches = re.findall(regex, conteudo_com_id)

    for match in matches:
        # Calcular o novo valor no formato desejado (calc(0.95*350px))
        valor = float(match)
        novo_valor = f'calc({valor/100}*350px)'
        # Substituir o valor original pelo novo valor no conteúdo
        conteudo_com_id = conteudo_com_id.replace(f'style="width:{match}%"', f'style="width:{novo_valor}"')
    return conteudo_com_id

# Chame a função para realizar a conversão
html_content = convert_tex_to_html(conteudo_atualizado)
resultados = buscar_termos_arquivo_tex(tex_file_name)

# Extrair bib
def extract_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        bib_data = file.read().replace(r'\&', '&')
    entries = bib_data.split('\n\n')
    output = ""
    for entry in entries:
        lines = entry.split('\n')
        info = {}
        for line in lines:
            line = line.strip()
            if line.startswith('@'):
                continue
            elif line.startswith('}'):
                break
            elif '=' in line:
                key, value = line.split('=', 1)
                info[key.strip()] = value.strip().strip(',{}')
        # Adiciona o conteúdo formatado à saída
        formatted_output = format_output(info)
        if formatted_output:
            output += formatted_output
    return output

def format_output(info):
    author = info.get('author')
    title = info.get('title')
    journal = info.get('journal')
    volume = info.get('volume')
    number = info.get('number')
    pages = info.get('pages')
    year = info.get('year')
    doi = info.get('doi')

    authors = ', '.join(author.split(' and ')) if author else ""
    title = title if title else ""
    journal = journal if journal else ""
    volume = volume if volume else ""
    number = number if number else ""
    pages = pages if pages else ""
    year = year if year else ""
    doi = doi if doi else ""

    output = ""
    if authors and year:
        output += f"<p>{authors} ({year})."
    if title:
        output += f" {title}."
    if journal:
        output += f" {journal},"
    if volume:
        output += f" {volume}"
    if number:
        output += f"({number})"
    if pages:
        output += f", {pages}."
    if doi:
        output += f" {doi}."
    output += "</p>"
    return output

file_path_bib = 'Article1.bib'
bib_output = extract_info(file_path_bib)

if html_content is not None:
    conteudo_com_id = substituir_conteudo(html_content)
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
    {conteudo_com_id}
    <h1>References</h1>
    {bib_output}
</body>
</html>'''
        f.write(html_content)
