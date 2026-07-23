# Tex2HTML — Conversor LaTeX → HTML para o OJS

Ferramenta que converte um artigo em **LaTeX** (do Overleaf) para **HTML** pronto
para publicar no **OJS (Open Journal Systems)** da revista
**Semina: Ciências Exatas e Tecnológicas**.

Site do periódico: https://ojs.uel.br/revistas/uel/index.php/semexatas

## O que ela faz

Você joga a **pasta do artigo** (ex.: `Artigo46`) na interface e ela devolve uma
pasta pronta para o OJS. A pasta de entrada deve conter:

```
Artigo46/
├── article.tex          (o texto em LaTeX)
├── article.bib          (as referências)
└── Figures/             (as figuras — .png, .jpg, .jpeg…)
    ├── fig1.jpg
    ├── fig2ab.png
    └── ...
```

A pasta de saída (`Artigo46_OJS/`) sai com:

```
Artigo46_OJS/
├── Artigo46.html        (HTML pronto para o galley)
├── Header.png           (cabeçalho da revista)
├── fig1.png             (todas as figuras convertidas para PNG)
├── fig2ab.png
└── ...
```

Durante a conversão a ferramenta:

- converte o LaTeX em HTML com o **Pandoc**, preservando as fórmulas (MathJax);
- monta o cabeçalho do artigo (título, DOI, citação, datas) a partir do `.tex`;
- transforma `\cite`/`\citeauthor` em citações no padrão da revista, com links
  para as referências;
- resolve as **referências cruzadas** (`\ref`, `\eqref`, `\autoref`, `\cref`) de
  figuras, tabelas e equações em links numerados que apontam para o alvo — e
  numera as equações com `\tag` (renderizado pelo MathJax);
- numera automaticamente as legendas de **figuras** e **tabelas**;
- **dimensiona as imagens** de acordo com o `scale` do LaTeX (que o Pandoc
  descarta), usando o tamanho real em pixels, com `max-width:100%` para nenhuma
  imagem estourar a largura da página;
- **resolve nomes de figura ignorando maiúsculas/minúsculas** (o `.tex` cita
  `fig6Nova`, o arquivo é `fig6NOVA`) — isso evita imagem quebrada no OJS, cujo
  servidor (Linux) diferencia maiúsculas, ao contrário do Windows;
- **remove comentários** do LaTeX e avisa sobre figuras citadas que não existem;
- quando o `.tex` tem um erro real (ex.: chave `{` sem fechar), mostra uma
  **mensagem clara com a linha aproximada** em vez de travar com erro técnico.
- monta a lista de **referências** a partir do `.bib`;
- **converte todas as figuras para PNG** e referencia cada imagem no HTML
  **apenas pelo nome do arquivo** (`src="fig1.png"`) — que é o formato que o OJS
  resolve automaticamente quando as imagens são enviadas como *dependent files*.

## Como usar (interface gráfica)

```bash
python main.py
```

1. Clique em **"Selecionar pasta…"** e escolha a pasta do artigo.
2. Clique em **"Converter"**.
3. Ao terminar, clique em **"Abrir pasta de saída"**.

No OJS, envie o `.html` como galley HTML e cada `.png` como *dependent file*.

## Como usar (linha de comando)

```bash
python main.py Artigo46/                 # gera Artigo46_OJS/ ao lado
python main.py Artigo46/ -o saida/       # escolhe a pasta de saída
```

## Instalação

```bash
pip install -r requirements.txt
```

O `pypandoc_binary` já traz o **Pandoc embutido** — não é preciso instalá-lo à parte.

## Executável para Windows (.exe)

Para entregar a alguém que não tem Python instalado, dá para gerar um único
`Tex2HTML.exe`. Veja o passo a passo em **[BUILD.md](BUILD.md)**.

## Estrutura do projeto

```
main.py                      → ponto de entrada (abre a interface / modo CLI)
build.spec                   → configuração do PyInstaller para gerar o .exe
assets/                      → Header.png e orcid.png (embutidos no executável)
tex2ojs/                     → pacote principal
├── resources.py             → localização de assets e do Pandoc
├── deps.py                  → checagem de dependências
├── cli.py                   → modo linha de comando
├── core/                    → núcleo da conversão
│   ├── text.py              → limpeza de comandos LaTeX / remoção de comentários
│   ├── bibliography.py      → parsing do .bib, citações e referências
│   ├── crossref.py          → referências cruzadas (\ref, \eqref) e numeração
│   ├── links.py             → tokens seguros p/ inserir links após o Pandoc
│   ├── lint.py              → detecção de erros de LaTeX (chaves/$ desbalanceados)
│   ├── latex.py             → pré-processamento do .tex e metadados
│   ├── html.py              → Pandoc + pós-processamento do HTML
│   ├── template.py          → template HTML/CSS da revista
│   └── pipeline.py          → orquestração (convert_article)
├── media/
│   └── images.py            → descoberta e conversão das figuras para PNG
└── ui/
    └── app.py               → interface gráfica (Tkinter)
```

Uso como biblioteca:

```python
from tex2ojs import convert_article
result = convert_article("Artigo46/")
print(result.output_dir, result.images, result.warnings)
```

> A normalização de LaTeX que antes ficava em `bibnorm.py`/`texnorm.py` agora é
> feita automaticamente durante a conversão (em `core/text.py`), sem alterar os
> arquivos originais.

## Licença

Uso acadêmico e educacional.
