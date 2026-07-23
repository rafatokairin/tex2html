# Como gerar o executável (.exe) para Windows

O objetivo é entregar para a professora **um único arquivo `Tex2HTML.exe`** que ela
abre com dois cliques, sem precisar instalar Python, Pandoc ou qualquer biblioteca.

> **Importante:** o `.exe` do Windows precisa ser gerado **no Windows**. O
> PyInstaller não faz "cross-build" — se você rodar no Linux/WSL, sai um binário
> Linux. Faça os passos abaixo numa máquina/prompt Windows (pode ser a sua).

## Passo a passo (Windows)

1. Instale o [Python 3.10+](https://www.python.org/downloads/) marcando a opção
   **"Add Python to PATH"** durante a instalação.

2. Abra o **Prompt de Comando** na pasta do projeto e instale as dependências:

   ```bat
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. Gere o executável:

   ```bat
   pyinstaller build.spec
   ```

   > O `build.spec` já usa o `main.py` como ponto de entrada e embute o pacote
   > `tex2ojs`, os assets (`assets/`) e o Pandoc.

4. O arquivo final estará em **`dist\Tex2HTML.exe`**. É só esse arquivo que a
   professora precisa — pode copiar para o Desktop dela e abrir com dois cliques.

## Como a professora usa

1. Abre o `Tex2HTML.exe`.
2. Clica em **"Selecionar pasta…"** e escolhe a pasta do artigo (ex.: `Artigo46`,
   que contém o `.tex`, o `.bib` e a pasta de figuras).
3. Clica em **"Converter"**.
4. Ao terminar, clica em **"Abrir pasta de saída"**. Aparece a pasta
   `Artigo46_OJS` com:
   - o arquivo `.html` pronto, e
   - todas as figuras convertidas para `.png`.
5. No OJS, ela sobe o `.html` como galley HTML e cada `.png` como *dependent file*
   (arquivo dependente). Como o HTML referencia as imagens só pelo nome
   (`src="fig1.png"`), o OJS resolve os caminhos automaticamente.

## Observações

- O Pandoc já vem embutido no executável (via `pypandoc_binary`), então a máquina
  da professora **não precisa** ter o Pandoc instalado.
- Se o antivírus reclamar do `.exe` (comum com PyInstaller), é falso positivo;
  pode liberar/assinar o binário.
