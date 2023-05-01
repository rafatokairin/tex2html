import os
import pypandoc
from bs4 import BeautifulSoup

def convert_tex_to_html(tex_file_path):
    try:
        # Converte o arquivo .tex para .html com a opcao --mathjax e encontra e armazena todos h1 em um vetor de strings
        output = pypandoc.convert_file(tex_file_path, 'html', extra_args=['--mathjax'])
        soup = BeautifulSoup(output, 'html.parser')
        h1_list = [h1.get_text() for h1 in soup.find_all('h1')]
        h1_list = [h1.lstrip() if h1.startswith(' ') else h1 for h1 in h1_list]
        h1_list = [h1.rstrip().replace(' ', '-') if h1.endswith(' ') else h1.replace(' ', '-') for h1 in h1_list]
        return str(soup), h1_list
    except Exception as e:
        print(f'Ocorreu um erro durante a conversão: {e}')
        return None, None


# Nome do arquivo .tex de entrada (assumindo que esteja na mesma pasta do arquivo Python)
tex_file_name = 'main.tex'
# Caminho do arquivo .tex de entrada
tex_file_path = os.path.abspath(tex_file_name)
# Chame a função para realizar a conversão
html_content, h1_list = convert_tex_to_html(tex_file_path)

if html_content is not None:
    with open(f"{os.path.splitext(tex_file_name)[0]}.html", 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="en-US">\n')
        f.write('<head>\n')
        # Biblioteca MathJax
        f.write('<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>\n')
        # CSS
        f.write('<link rel="stylesheet" type="text/css" href="style.css">\n')
        f.write('<meta charset="utf-8">\n')
        f.write('</head>\n')
        f.write('<body>\n')
        # Adiciona o índice
        f.write('<div id="index">\n')
        f.write('<h2>Outline:</h2>\n')
        f.write('<ol>\n')
        for h1 in h1_list:
            f.write(f'<li><a href="#{h1.lower()}">{h1.replace("-", " ")}</a></li>\n')
        f.write('</ol>\n')
        f.write('</div>\n')
        f.write(html_content)
        f.write('</body>\n')
        f.write('</html>')
