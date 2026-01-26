# Conversão LaTeX para HTML para OJS

Este repositório contém um **script em Python** desenvolvido para **automatizar a conversão de arquivos LaTeX (.tex) para HTML**, com foco na publicação de artigos científicos no **sistema OJS (Open Journal Systems)**.

O projeto foi desenvolvido no contexto do **Semina: Ciências Exatas e Tecnológicas**, com o objetivo de garantir **formatação correta**, **acessibilidade** e **compatibilidade com a web** durante a publicação dos artigos.

Site do periódico:

https://ojs.uel.br/revistas/uel/index.php/semexatas

---

## Objetivo

- Automatizar a geração de **templates HTML** a partir de arquivos **LaTeX**
- Preservar fórmulas matemáticas e estrutura científica dos artigos
- Facilitar a integração dos conteúdos convertidos ao **OJS**
- Melhorar a acessibilidade e padronização dos artigos publicados

---

## Passo a Passo da Solução

### 1. Conversão LaTeX → HTML
- Utilização da biblioteca **Pandoc** para converter arquivos `.tex` em `.html`
- A conversão suporta fórmulas matemáticas usando **MathJax**

### 2. Extração e Manipulação do HTML
- Uso da biblioteca **BeautifulSoup** para:
  - Extrair informações do HTML gerado
  - Ajustar estrutura, tags e conteúdo conforme o padrão do OJS

### 3. Substituição de Padrões de Texto
- Utilização da biblioteca **re** para:
  - Substituições textuais
  - Ajustes de padrões e correções automáticas no HTML

### 4. Manipulação de Arquivos
- Uso da biblioteca **os** para:
  - Leitura e escrita de arquivos
  - Organização de diretórios e fluxos de conversão

---

## Bibliotecas Utilizadas

- **pypandoc** – Interface Python para o Pandoc, responsável pela conversão `.tex → .html`
- **BeautifulSoup (bs4)** – Extração e manipulação do HTML
- **re** – Expressões regulares para substituição de padrões
- **os** – Manipulação de arquivos e diretórios

---

## Instalação das Dependências

Execute os comandos abaixo para instalar as bibliotecas necessárias:

```
pip install pypandoc --pre
pip install beautifulsoup4
```

### Observação importante:

É necessário chamar uma única vez a função abaixo para fazer o download do executável do Pandoc:

```
pypandoc.download_pandoc()
```

## Suporte a Fórmulas Matemáticas

- A opção --mathjax é utilizada durante a conversão

- As fórmulas matemáticas são geradas em MathML

- O MathJax (biblioteca JavaScript) é responsável por renderizar corretamente as fórmulas nas páginas HTML

## Contexto do Projeto

Este trabalho foi desenvolvido com base na contribuição ao:

OJS System Development – Semina Journal

### Contribuição no desenvolvimento e aprimoramento do sistema OJS

- Melhoria da interface e da experiência do usuário

- Automação da geração de templates HTML a partir de arquivos LaTeX

- Garantia de formatação correta e acessibilidade dos artigos científicos

## Licença

Este projeto pode ser utilizado para fins acadêmicos e educacionais.
