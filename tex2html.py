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
        r"\\newcommand{\\autorcabecalho}{(.+?)}",
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

# Lê o arquivo de entrada, remove os asteriscos e adiciona \[
with open(tex_file_name, "r", encoding="utf-8") as f:
    conteudo = f.read()
    conteudo_sem_asteriscos = re.sub(r"\\(begin|end){([^}\s]+)\*}", r"\\\1{\2}", conteudo)
    # Substituições no conteúdo atualizado do arquivo tex
    conteudo_atualizado = re.sub(r"\\begin{equation}(\s*\\label{[^}]+})", r"\\begin{equation}\g<1>\[", conteudo_sem_asteriscos)
    conteudo_atualizado = conteudo_atualizado.replace('\\bm{', '\\mathbf{')
    conteudo_atualizado = conteudo_atualizado.replace('\\textsuperscript{\\textregistered}', '&reg;')
    conteudo_atualizado = conteudo_atualizado.replace('\\textregistered', '&reg;')
    conteudo_atualizado = conteudo_atualizado.replace('\\copyright', '&copy;')
    conteudo_atualizado = conteudo_atualizado.replace('\\hdots', '\\dots')
    conteudo_atualizado = re.sub(r'\\parbox\{.*?\}', '', conteudo_atualizado)
    conteudo_atualizado = conteudo_atualizado.replace('\\centering', '')

def convert_tex_to_html(tex_content):
    try:
        # Converte o conteúdo .tex para .html com a opcao --mathjax e encontra e armazena todos h1 em um vetor de strings
        output = pypandoc.convert_text(tex_content, 'html', format='tex', extra_args=['--mathjax'])
        soup = BeautifulSoup(output, 'html.parser')
        h1_list = [h1.get_text() for h1 in soup.find_all('h1')]
        h1_list = [h1.lstrip() if h1.startswith(' ') else h1 for h1 in h1_list]
        h1_list = [h1.rstrip().replace(' ', '-') if h1.endswith(' ') else h1.replace(' ', '-') for h1 in h1_list]
        return str(soup), h1_list
    except Exception as e:
        print(f'Ocorreu um erro durante a conversão: {e}')
        return None, None

# Define a função para substituir o conteúdo necessário
def substituir_conteudo(html_content):
    padrao = r'<span class="math display">\\\[\\label{([^}]+)}'
    conteudo_com_id = re.sub(padrao, r'<span class="math display" id="\1">', html_content)
    return conteudo_com_id

# Chame a função para realizar a conversão
html_content, h1_list = convert_tex_to_html(conteudo_atualizado)
resultados = buscar_termos_arquivo_tex(tex_file_name)

if html_content is not None:
    conteudo_com_id = substituir_conteudo(html_content)
    new_html_file = f"{os.path.splitext(tex_file_name)[0]}.html"
    with open(new_html_file, 'w', encoding='utf-8') as f:
        html_content = f'''<!DOCTYPE html>
<html lang="en-US">
<head>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
    <link rel="stylesheet" type="text/css" href="style.css">
    <meta charset="utf-8">
</head>
<body>
    <h1>{list(resultados.values())[0]}</h1>
    <p>{list(resultados.values())[1]}</p>
    <p>DOI {list(resultados.values())[2]}</p>
    <p>Semina: Ciências Exatas e Tecnológicas, Londrina{''.join(list(resultados.values())[3:])}</p>
    <div id="index">
        <h2>Outline:</h2>
        <ol>
'''
        for h1 in h1_list:
            html_content += f'<li><a href="#{h1.lower()}">{h1.replace("-", " ")}</a></li>\n'
        html_content += '''
        </ol>
    </div>
    ''' + conteudo_com_id + '''
</body>
</html>'''
        f.write(html_content)
