import os
import pypandoc
from bs4 import BeautifulSoup
import re

file_path_bib = 'Article1.bib'
tex_file_name = 'Article1.tex'

def replace_cite(text, bib_file):
    # Lê o arquivo .bib e armazena as informações em um dicionário
    bib_entries = {}
    with open(bib_file, 'r', encoding='utf-8') as file:
        entry = ''
        key = ''
        for line in file:
            if line.startswith('@'):
                entry = line.strip().split('{')[1][:-1]
                key = entry.split(',')[0]
            elif line.strip() == '}':
                bib_entries[key] = entry
            else:
                entry += line
    # Encontra as citações no texto usando expressões regulares
    pattern = r'\\cite\{([^}]+)\}'
    matches = re.findall(pattern, text)
    # Substitui as citações pelos formatos desejados
    for match in matches:
        citation = match.split(',')
        replacements = []
        for key in citation:
            key = key.strip()
            if key in bib_entries:
                entry = bib_entries[key]
                author = re.search(r'author\s*=\s*\{([^}]+)\}', entry).group(1)
                year = re.search(r'year\s*=\s*\{([^}]+)\}', entry).group(1)

                authors = author.split(' and ')
                if len(authors) > 1:
                    if len(authors) > 2:
                        first_author = authors[0].split(',')[0]
                        replacements.append(f'{first_author} et al., {year}')
                    else:
                        author_names = [name.split(',')[0] for name in authors]
                        replacements.append(f'{author_names[0]} & {author_names[1]}, {year}')
                else:
                    replacements.append(f'{authors[0].split(",")[0].split()[0]}, {year}')
            else:
                replacements.append(f'[{key} - not found]')
        # Realiza a substituição no texto original
        replacements_text = '; '.join(replacements)
        text = text.replace(f'\\cite{{{match}}}', f'({replacements_text})')
    return text

def replace_citeauthor(text, bib_file):
    # Lê o arquivo .bib e armazena as informações em um dicionário
    bib_entries = {}
    with open(bib_file, 'r', encoding='utf-8') as file:
        entry = ''
        key = ''
        for line in file:
            if line.startswith('@'):
                entry = line.strip().split('{')[1][:-1]
                key = entry.split(',')[0]
            elif line.strip() == '}':
                bib_entries[key] = entry
            else:
                entry += line
    # Encontra as citações no texto usando expressões regulares
    pattern = r'\\citeauthor\{([^}]+)\}'
    matches = re.findall(pattern, text)
    # Substitui as citações pelos formatos desejados
    for match in matches:
        citation = match.split(',')
        replacements = []
        for key in citation:
            key = key.strip()
            if key in bib_entries:
                entry = bib_entries[key]
                author = re.search(r'author\s*=\s*\{([^}]+)\}', entry).group(1)
                year = re.search(r'year\s*=\s*\{([^}]+)\}', entry).group(1)

                authors = author.split(' and ')
                if len(authors) > 1:
                    if len(authors) > 2:
                        first_author = authors[0].split(',')[0]
                        replacements.append(f'{first_author} et al. ({year})')
                    else:
                        author_names = [name.split(',')[0] for name in authors]
                        replacements.append(f'{author_names[0]} & {author_names[1]} ({year})')
                else:
                    replacements.append(f'{authors[0].split(",")[0].split()[0]} ({year})')
            else:
                replacements.append(f'[{key} - not found]')
        # Realiza a substituição no texto original
        replacements_text = '; '.join(replacements)
        text = text.replace(
            f'\\citeauthor{{{match}}}', f'{replacements_text}')
    return text

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
        r"\\Year{(.+?)}",
        r"\\Volume{(.+?)}",
        r"\\ArticleID{(.+?)}",
    ]
    # Cria um dicionário para armazenar os valores encontrados
    resultados = {}
    # Busca pelos termos no arquivo
    for termo in termos:
        match = re.search(termo, conteudo)
        if match:
            if termo == r"\\Volume{(.+?)}":
                resultados[termo] = ", v. " + match.group(1)
            elif termo == r"\\ArticleID{(.+?)}":
                resultados[termo] = ": " + match.group(1)
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
# Lê o arquivo de entrada, remove os asteriscos
with open(tex_file_name, "r", encoding="utf-8") as f:
    conteudo = f.read()
    conteudo_sem_asteriscos = re.sub(r"\\(begin|end){([^}\s]+)\*}", r"\\\1{\2}", conteudo)
    # Substituições no conteúdo atualizado do arquivo tex
    conteudo_atualizado = re.sub(r"\\begin{equation}(\s*\\label{[^}]+})", r"\\begin{equation}\g<1>", conteudo_sem_asteriscos)
    conteudo_atualizado = re.sub(r"\\begin{eqnarray}(\s*\\label{[^}]+})", r"\\begin{eqnarray}\g<1>", conteudo_atualizado)
    conteudo_atualizado = conteudo_atualizado.replace('\\bm{', '\\mathbf{')
    conteudo_atualizado = conteudo_atualizado.replace('\\hdots', '\\dots')
    conteudo_atualizado = re.sub(r'\\parbox{\d+cm}', r'', conteudo_atualizado)
    conteudo_atualizado = conteudo_atualizado.replace('\\centering', '')
    conteudo_atualizado = re.sub(r'\\hspace{.*?}', '', conteudo_atualizado)
    conteudo_atualizado = re.sub(r'\\InsertFigure(\[.*?\])?\{(.*?)\}\{(.*?)\}\{(.*?)\}', replace_insert_figure, conteudo_atualizado)
    conteudo_atualizado = re.sub(r'\\includegraphics(\[.*?\])?\{(.*?)(\.(?!jpeg$)\w+)?\}', lambda match: f'\\includegraphics{match.group(1)}{{{match.group(2)}{".png" if match.group(3) != ".jpeg" else match.group(3)}}}', conteudo_atualizado)
    conteudo_atualizado = re.sub(r"(\\begin{document})", r"\1\n" + copy_abstract_eng(tex_file_name) + "\n", conteudo_atualizado, 1, re.DOTALL)
    conteudo_atualizado = conteudo_atualizado.replace('\\resizebox{\columnwidth}{!}', '')
    conteudo_atualizado = conteudo_atualizado.replace('\\columnwidth', '\\textwidth')
    conteudo_atualizado = re.sub(r'\\begin\{([^}]*)\} \\label\{([^}]*)\}', r'\\begin{figure} {(\2)} \\end{figure} \\begin{\1} \\label{\2}', conteudo_atualizado)
    conteudo_atualizado = replace_cite(conteudo_atualizado, file_path_bib)
    conteudo_atualizado = replace_citeauthor(conteudo_atualizado, file_path_bib)

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
    conteudo_com_id = re.sub(r'\(<a', r'<a', conteudo_com_id)
    conteudo_com_id = re.sub(r'a>\)', r'a>', conteudo_com_id)
    conteudo_com_id = re.sub(r'>\[(\d+)\]<', r'>(\1)<', conteudo_com_id)
    conteudo_com_id = conteudo_com_id.replace('\\textsuperscript{\\textregistered}', '&reg;')
    conteudo_com_id = conteudo_com_id.replace('\\textregistered', '&reg;')
    conteudo_com_id = conteudo_com_id.replace('\\copyright', '&copy;')
    conteudo_com_id = re.sub(r'class="math display">\\\[\\label\{([^}]*)\}', r'class="math display" id="\1">\\[', conteudo_com_id)
    conteudo_com_id = conteudo_com_id.replace('class="math display">\\[\\begin{aligned}', 'class="math display">\\[\\egin{aligned}')
    conteudo_com_id = re.sub(r'class="math display">\\\[\\egin\{aligned\}\n\n\\label\{([^}]*)\}', r'class="math display" id="\1">\\[\\begin{aligned}', conteudo_com_id)
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
        bib_data = bib_data.replace('--', '–')
        bib_data = re.sub(r'\{|\}', '', bib_data)

    entries = bib_data.split('\n\n')
    output = ""
    for entry in entries:
        lines = entry.split('\n')
        info = {}
        ignore_entry = False # Variável para indicar se o registro deve ser ignorado
        for line in lines:
            line = line.strip()
            if line.startswith('@'):
                if line.lower().startswith('@proceedings'):
                    ignore_entry = True # Marca o registro para ser ignorado
                continue
            elif line.startswith('}'):
                break
            elif '=' in line and not ignore_entry:
                key, value = line.split('=', 1)
                info[key.strip()] = value.strip().strip(',{}')

        if not ignore_entry:
            # Adiciona o conteúdo formatado à saída
            formatted_output = format_output(info)
            if formatted_output:
                output += formatted_output
        output = output.replace('&,', '&')
    return output

def format_output(info):
    author = info.get('author')
    title = info.get('title')
    institution = info.get('institution')
    journal = info.get('journal')
    publisher = info.get('publisher')
    volume = info.get('volume')
    number = info.get('number')
    pages = info.get('pages')
    year = info.get('year')
    doi = info.get('doi')

    author_list = author.split(' and ') if author else []
    formatted_authors = []

    for i, name in enumerate(author_list):
        name_parts = name.strip().split()
        last_name = name_parts[0]
        initials = ' '.join(part[0].upper() + '.' for part in name_parts[1:]) if len(name_parts) > 1 else ""
        formatted_author = f"{last_name} {initials}"
        formatted_authors.append(formatted_author)
        if i == len(author_list) - 2:
            formatted_authors.append("&")

    authors = ', '.join(formatted_authors)

    title = title if title else ""
    institution = institution if institution else ""
    journal = journal if journal else ""
    publisher = publisher if publisher and not journal else ""
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
    if institution:
        output += f" {institution}."
    if journal:
        output += f" <em>{journal}</em>,"
    if publisher:
        output += f" {publisher}."
    if volume:
        output += f" <em>{volume}</em>"
    if number:
        output += f"({number})"
    if pages:
        output += f", {pages}."
    if doi:
        output += f" {doi}."
    output += "</p>"
    return output

bib_output = extract_info(file_path_bib)

if html_content is not None:
    conteudo_com_id = substituir_conteudo(html_content)
    nome_arquivo_saida = 'begin.html'
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        html_content = f'''<!DOCTYPE html>
<html lang="en-US">
<head>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
    <style>
        html {{
            scroll-behavior: smooth;
        }}

        a {{
            text-decoration: none;
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

        figure p span {{
            float: right;
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
    <p><strong>Citation</strong> Semin., Ciênc. Exatas Tecnol.{''.join(list(resultados.values())[3:])}</p>
    <h3>Abstract:</h3>
    {conteudo_com_id}
    <h1>References</h1>
    {bib_output}
</body>
</html>'''
        f.write(html_content)

def substituir_texto(texto):
    texto_modificado = re.sub(r'class="math display">\\\[\\egin\{aligned\}\n\n\\label\{([^}]*)\}', r'class="math display" id="\1">\\[\\begin{aligned}', texto)
    return texto_modificado

with open(nome_arquivo_saida, "r", encoding="utf-8") as arquivo:
    texto_original = arquivo.read()

texto_modificado = substituir_texto(texto_original)

with open(nome_arquivo_saida, "w", encoding="utf-8") as arquivo_saida:
    arquivo_saida.write(texto_modificado)
