import re

# Tags-alvo a serem limpas
tags_to_clean = {
    "InitialPage",
    "Volume",
    "Month",
    "Year",
    "DOI",
    "ArticleID",
    "Area",
    "Category",
    "ArticleTitleENG",
    "ArticleTitlePTBR",
    "TitleHeader",
    "ReceivedDate",
    "RevisedDate",
    "AcceptedDate",
    "PublishedDate"
}

# Regex para remover comandos LaTeX dentro do conteúdo das tags
def clean_tag_content(content):
    # Remove comandos como \textit{...}
    content = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', content)
    # Remove qualquer comando restante do tipo \algo
    content = re.sub(r'\\[a-zA-Z]+', '', content)
    # Remove chaves extras
    content = content.replace('{', '').replace('}', '')
    return content.strip()

def process_tex_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed_lines = []
    for line in lines:
        # Remove comentários (mantendo os que estiverem dentro de comandos, ex: \textit{...%...})
        if not line.lstrip().startswith('%'):
            # Remove parte comentada da linha (com cuidado para não quebrar dentro de comandos)
            line = re.sub(r'(?<!\\)%.*', '', line)

            # Verifica se a linha corresponde a uma tag específica
            match = re.match(r'\\(\w+)\{(.+)\}', line.strip())
            if match:
                tag, content = match.groups()
                if tag in tags_to_clean:
                    cleaned_content = clean_tag_content(content)
                    line = f'\\{tag}{{{cleaned_content}}}\n'

            processed_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)

# === Exemplo de uso ===
process_tex_file("Article.tex", "Article.tex")
