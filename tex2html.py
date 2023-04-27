import os
import pypandoc
# pypandoc.download_pandoc()

def convert_tex_to_html(tex_file_path):
    try:
        # Converte o arquivo .tex para .html com a opcao --mathjax
        output = pypandoc.convert_file(tex_file_path, 'html', extra_args=['--mathjax'])
        return output
    except Exception as e:
        print(f'Ocorreu um erro durante a conversão: {e}')
        return None

# Nome do arquivo .tex de entrada (assumindo que esteja na mesma pasta do arquivo Python)
tex_file_name = 'main.tex'
# Caminho do arquivo .tex de entrada
tex_file_path = os.path.abspath(tex_file_name)
# Funcao que realiza a conversao
html_content = convert_tex_to_html(tex_file_path)

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
        f.write(html_content)
        f.write('</body>\n')
        f.write('</html>')
