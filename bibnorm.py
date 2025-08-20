import re

def normalize_bib_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Substitui todos os primeiros @... por @article
    content = re.sub(r'@\w+{', '@article{', content)
    
    # 2. Remove os {{ e }}, deixando apenas { e }
    content = content.replace('{{', '{').replace('}}', '}')
    
    # 3. Remove comandos \ (como \textit, \text, etc.)
    content = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', content)
    content = re.sub(r'\\[a-zA-Z]+', '', content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

# Exemplo de uso:
input_file = 'Article.bib'
output_file = 'Article.bib'
normalize_bib_file(input_file, output_file)