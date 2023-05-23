import pypandoc

def convert_tex_to_html(tex_file, html_file):
    try:
        # Convertendo o arquivo TeX para HTML usando pypandoc
        pypandoc.convert_file(tex_file, 'html', outputfile=html_file, extra_args=['--mathjax'])
        print("Conversão concluída com sucesso!")
    except OSError as e:
        print("Erro ao converter o arquivo:", e)

def generate_html_with_mathjax(html_file):
    # Conteúdo HTML com o script do MathJax
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Exemplo de arquivo HTML com MathJax</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
    <script>
        MathJax = {
            tex: {
                packages: {'[+]': ['ams']},
                inlineMath: [['$', '$'], ['\\(', '\\)']]
            },
            options: {
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }
        };
    </script>
</head>
<body>
'''

    # Lendo o conteúdo do arquivo HTML gerado pela conversão
    with open(html_file, 'rb') as f:
        tex_content = f.read().decode('utf-8')

    # Substituindo os comandos específicos do LaTeX por equivalentes compatíveis com o MathJax
    tex_content = tex_content.replace('\\bm{', '\\mathbf{')
    tex_content = tex_content.replace('\\textsuperscript{\\textregistered}', '&reg;')
    tex_content = tex_content.replace('\\textregistered', '&reg;')
    tex_content = tex_content.replace('\\copyright', '&copy;')
    tex_content = tex_content.replace('\\hdots', '\\dots')

    # Adicionando o conteúdo do arquivo HTML gerado à estrutura do HTML com MathJax
    html_content += tex_content

    # Fechando as tags do HTML
    html_content += '''
</body>
</html>
'''

    # Escrevendo o conteúdo HTML completo no arquivo final
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Arquivo HTML com MathJax gerado com sucesso!")

# Caminho do arquivo TeX de entrada e arquivo HTML de saída
tex_file_path = 'arquivo.tex'
html_file_path = 'arquivo.html'

# Chamando a função para converter o arquivo TeX para HTML
convert_tex_to_html(tex_file_path, html_file_path)

# Chamando a função para gerar o arquivo HTML com MathJax
generate_html_with_mathjax(html_file_path)
