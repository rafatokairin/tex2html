import pypandoc
from bs4 import BeautifulSoup
import re

file_path_bib = 'Article.bib'
tex_file_name = 'Article.tex'

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
                author_match = re.search(r'author\s*=\s*\{([^}]+)\}', entry)
                year_match = re.search(r'year\s*=\s*\{([^}]+)\}', entry)
                if author_match and year_match:
                    author = author_match.group(1)
                    year = year_match.group(1)
                    authors = author.split(' and ')
                    if len(authors) > 1:
                        if len(authors) > 2:
                            first_author = authors[0].split(',')[0]
                            replacements.append(f'{first_author} et al., <a href="#{key}">{year}</a>)')
                        else:
                            author_names = [name.split(',')[0] for name in authors]
                            replacements.append(f'{author_names[0]} & {author_names[1]}, <a href="#{key}">{year}</a>)')
                    else:
                        replacements.append(f'{authors[0].split(",")[0].split()[0]}, <a href="#{key}">{year}</a>)')
                else:
                    replacements.append(f'[{key} - missing information]')
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
                author_match = re.search(r'author\s*=\s*\{([^}]+)\}', entry)
                year_match = re.search(r'year\s*=\s*\{([^}]+)\}', entry)
                if author_match and year_match:
                    author = author_match.group(1)
                    year = year_match.group(1)
                    authors = author.split(' and ')
                    if len(authors) > 1:
                        if len(authors) > 2:
                            first_author = authors[0].split(',')[0]
                            replacements.append(f'{first_author} et al., (<a href="#{key}">{year}</a>)')
                        else:
                            author_names = [name.split(',')[0] for name in authors]
                            replacements.append(f'{author_names[0]} & {author_names[1]}, (<a href="#{key}">{year}</a>)')
                    else:
                        replacements.append(f'{authors[0].split(",")[0].split()[0]}, (<a href="#{key}">{year}</a>)')
                else:
                    replacements.append(f'[{key} - missing information]')
            else:
                replacements.append(f'[{key} - not found]')
        # Realiza a substituição no texto original
        replacements_text = '; '.join(replacements)
        text = text.replace(f'\\citeauthor{{{match}}}', f'{replacements_text}')
    return text

def adicionar_numero_caption(texto):
    numero = 1
    resultado = ""
    for linha in texto.splitlines():
        if "<caption>" in linha:
            resultado += linha.replace("<caption>", f"<caption><strong>Table {numero} - </strong>")
            numero += 1
        else:
            resultado += linha
        resultado += "\n"
    return resultado

def adicionar_numero_figcaption(texto):
    numero = 1
    resultado = ""
    for linha in texto.splitlines():
        if "<figcaption>" in linha:
            resultado += linha.replace("<figcaption>", f"<figcaption><strong>Figure {numero} - </strong>")
            numero += 1
        else:
            resultado += linha
        resultado += "\n"
    return resultado

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
        r"\\Area{(.+?)}",
        r"\\ArticleTitleENG{(.+?)}",
        r"\\AuthorHeader{(.+?)[\\\\}]",
        r"\\ReceivedDate{(.+?)[\\\\}]",
        r"\\RevisedDate{(.+?)[\\\\}]",
        r"\\AcceptedDate{(.+?)[\\\\}]",
        r"\\PublishedDate{(.+?)[\\\\}]",
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
    conteudo_atualizado = conteudo_atualizado.replace('\\textfractionsolidus', '/')
    conteudo_atualizado = conteudo_atualizado.replace('\\textbullet', '⋅')
    conteudo_atualizado = conteudo_atualizado.replace('\\textsc', '\\text')
    conteudo_atualizado = conteudo_atualizado.replace('\\footnotesize', '')
    conteudo_atualizado = conteudo_atualizado.replace('\\setlength', '')
    conteudo_atualizado = conteudo_atualizado.replace('\\centering', '')
    conteudo_atualizado = re.sub(r'\\hspace{.*?}', '', conteudo_atualizado)
    conteudo_atualizado = re.sub(r'\\cline{.*?}', '', conteudo_atualizado)
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
    conteudo_com_id = re.sub(r'&lt;|&gt;', lambda match: '<' if match.group() == '&lt;' else '>', conteudo_com_id)
    conteudo_com_id = re.sub(r'\(<a', r'<a', conteudo_com_id)
    conteudo_com_id = re.sub(r'a>\)', r'a>', conteudo_com_id)
    conteudo_com_id = re.sub(r'>\[(\d+)\]<', r'>(\1)<', conteudo_com_id)
    conteudo_com_id = re.sub(r'{\\arraycolsep}{\d+cm}', r'', conteudo_com_id)
    conteudo_com_id = conteudo_com_id.replace('\\textsuperscript{\\textregistered}', '&reg;')
    conteudo_com_id = conteudo_com_id.replace('\\textregistered', '&reg;')
    conteudo_com_id = conteudo_com_id.replace('\\copyright', '&copy;')
    conteudo_com_id = adicionar_numero_caption(conteudo_com_id)
    conteudo_com_id = adicionar_numero_figcaption(conteudo_com_id)
    conteudo_com_id = conteudo_com_id.replace('\n', ' ')
    conteudo_com_id = re.sub(r'class="math display">\\\[\\label\{([^}]*)\}', r'class="math display" id="\1">\\[', conteudo_com_id)
    conteudo_com_id = re.sub(r'class="math display">\\\[\\begin\{aligned\} \\label\{([^}]*)\}', r'class="math display" id="\1">\\[\\begin{aligned}', conteudo_com_id)
    conteudo_com_id = conteudo_com_id.replace('%\\', '\\')
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

# Extrair ID para outline
def extrair_ids_e_texto_h1(html):
    soup = BeautifulSoup(html, 'html.parser')
    elementos_h1 = soup.find_all('h1', id=True)
    ids = [elemento['id'] for elemento in elementos_h1]
    textos = [elemento.text for elemento in elementos_h1]
    return ids, textos

# Chame a função para realizar a conversão
html_content = convert_tex_to_html(conteudo_atualizado)
resultados = buscar_termos_arquivo_tex(tex_file_name)

# Extrair bib
def extract_info(bib_file):
    with open(bib_file, 'r') as file:
        bib_data = file.read()
    entries = re.findall(r'@(\w+)\{(.*?),\n(.*?)\n\}', bib_data, re.DOTALL)
    extracted_info = []

    for entry_type, entry_key, entry_content in entries:
        info = {'type': entry_type, 'key': entry_key}
        fields = re.findall(r'(\w+)\s*=\s*{(.+?)}', entry_content)
        for field_name, field_value in fields:
            info[field_name.lower()] = field_value
        extracted_info.append(info)
    return extracted_info

def format_info(bib_info):
    formatted_info = []
    for info in bib_info:
        formatted_entry = '<p id="{}">'.format(info['key'])
        if 'author' in info:
            authors = re.split(r'\s+and\s+', info['author'])
            if len(authors) > 1:
                formatted_authors = ', '.join(authors[:-1]) + ' & ' + authors[-1]
            else:
                formatted_authors = authors[0]
            formatted_entry += formatted_authors + ' '
        if 'year' in info:
            formatted_entry += '(' + info['year'] + ').'
        if 'title' in info:
            formatted_entry += ' ' + info['title'] + '.'
        if 'publisher' in info:
            formatted_entry += ' ' + info['publisher'] + '.'
        if 'volume' in info and 'number' in info:
            formatted_entry += ' ' + info['volume'] + '(' + info['number'] + '),'
        if 'pages' in info:
            formatted_entry += ' ' + info['pages'] + '.'
        if 'doi' in info:
            formatted_entry += ' <a target="_blank" href="https://doi.org/' + info['doi'] + '">https://doi.org/' + info['doi'] + '</a>'
        formatted_entry += '</p>'
        formatted_info.append(formatted_entry)
    return formatted_info

bib_info = extract_info(file_path_bib)
formatted_info = format_info(bib_info)

if html_content is not None:
    conteudo_com_id = substituir_conteudo(html_content)
    ids_h1, textos_h1 = extrair_ids_e_texto_h1(conteudo_com_id)
    menu_content = ''
    for id_h1, texto_h1 in zip(ids_h1, textos_h1):
        menu_content += f'<a href="#{id_h1}">{texto_h1}</a>'
    nome_arquivo_saida = 'begin.html'
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        html_content = f'''<!DOCTYPE html>
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
        else {{
            var searchUrl = "https://ojs.uel.br/revistas/uel/index.php/semexatas/search/index?query=" + encodeURIComponent(query);
            window.open(searchUrl, "_blank");
            return false;
        }}
    }}
    </script>
    <style>
        html {{
            scroll-behavior: smooth;
        }}

        a {{
            text-decoration: none;
        }}

        body {{
            font-family: 'Tinos', serif;
            word-break: normal;
            line-height: 1.5;
            text-align: justify;
            font-size: 15px;
            font-weight: 500;
            margin: 0;
            padding: 0;
        }}

        .article-content {{
            margin-right: 400px;
            margin-left: 400px;
        }}

        header {{
            width: 100%;
        }}

        .header-container {{
            margin: 0 !important;
            padding: 0 !important;
        }}

        .header-container img {{
            display: block;
            width: 100%;
            height: auto;
            min-width: 100vh;
            margin: 0 !important;
            padding: 0 !important;
        }}

        .image-text {{
            position: absolute;
            top: 25px;
            right: 50px;
            color: black;
            font-size: 18px;
            font-family: 'Josefin Sans', sans-serif;
            font-weight: 500;
            text-align: right;
            direction: rtl;
        }}

        .search {{
            float: left;
            margin-top: 0px;
            padding: 20px;
        }}

        .search_input input,
        .search_input button {{
            border-radius: 0; 
            height: 36px;
            font-size: 15px; 
            border: 1px solid #a0a0a0;
            font-weight: 500;
        }}

        .blue-background {{
            background-color: #346af3;
        }}

        .white-icon {{
            color: white;
            font-size: 15px;
            width: 36px;
        }}

        .search_input button:hover {{
        cursor: pointer;
        }}

        .menu {{
            position: fixed;
            margin-top: 0px;
            right: 0;
            padding: 10px;
            font-size: 18px;
        }}
        
        .menu a {{
            display: block;
            margin-bottom: 8px;
            text-decoration: none;
        }}

        figure p span {{
            float: right;
        }}

        h1, h2, h3 {{
            font-family: 'Josefin Sans', sans-serif;
            font-weight: 700;
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
            padding-bottom: 2px;
            padding-top: 2px;
            padding-left: 12px;
            padding-right: 12px;
            text-align: center;
        }}

        tbody td {{
            padding-bottom: 2px;
            padding-top: 2px;
            padding-left: 12px;
            padding-right: 12px;
            text-align: center;
        }}

        tbody tr.odd {{
            background-color: #f9f9f9;
        }}

        tbody tr:hover {{
            background-color: #e6e6e6;
        }}

        thead:before,
        thead:after {{
            content: "";
            display: table-row;
        }}

        table {{
            margin: 0 auto;
            border-collapse: collapse;
        }}

        p#data {{
            font-size: 12px;
        }}

        .nomes-container {{
        display: flex;
        gap: 10px;
        }}

        .nomes-container a {{
            float: left;
            display: flex;
            text-decoration: none;
        }}

        .nomes-container .orcid-icon {{
            height: 20px;
            margin-left: 5px;
        }}
        
        @media (max-width: 992px) {{
            .article-content {{
                margin: 10px;
            }}

            header {{
                display: none;
            }}
            
            .search {{
                display: none;
            }}

            .menu {{
                display: none;
            }}

            h1 {{
                font-size: 24px;
            }}
            
            p {{
                font-size: 14px;
            }}
        }}
    </style>
    <meta charset="utf-8">
</head>
<body>
    <header>
        <div class="header-container">
            <img src="Header.png">
            <div class="image-text">{list(resultados.values())[0]}</div>
        </div>
    </header>
    <div class="search">
        <form class="_cmp_form" method="get" action="https://ojs.uel.br/revistas/uel/index.php/semexatas/search/index" onsubmit="return openNewPage()">
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
        {menu_content}
        <a href="#article-references">References</a>
    </div>
    <div class="article-content">
        <h1>{list(resultados.values())[1]}</h1>
        <h3>{list(resultados.values())[2]}</h3>
        <p><strong>DOI</strong> {list(resultados.values())[7]}</p>
        <p><strong>Citation</strong> Semin., Ciênc. Exatas Tecnol.{''.join(list(resultados.values())[8:])}</p>
        <p id="data"><strong>Received:</strong> {list(resultados.values())[3]} <strong>Received in revised for:</strong> {list(resultados.values())[4]} <strong>Accepted:</strong> {list(resultados.values())[5]} <strong>Available online:</strong> {list(resultados.values())[6]}</p>
        <h3 id="article-abstract">Abstract:</h3>
        {conteudo_com_id}
        <h1 id="article-references">References</h1>
        {''.join(formatted_info)}
    </div>
</body>
</html>'''
        f.write(html_content)
