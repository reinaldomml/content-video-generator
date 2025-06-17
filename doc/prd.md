# Product Requirements Document (PRD): Gerador de Ebook a partir de Vídeos do YouTube

## 1. Introdução

**1.1. Objetivo do Produto:**
Desenvolver um script Python que automatiza a criação de ebooks a partir do conteúdo de vídeos do YouTube. O script deverá:
    1.  Receber links de vídeos do YouTube como entrada.
    2.  Baixar o áudio dos vídeos especificados.
    3.  Transcrever o áudio utilizando a API de Speech-to-Text da OpenAI, obtendo timestamps palavra a palavra.
    4.  Processar a transcrição para gerar o conteúdo textual de um ebook.
    5.  Formatar o conteúdo em um arquivo PDF utilizando a biblioteca WeasyPrint.

**1.2. Leitor Alvo deste PRD:**
Modelo de Linguagem Grande (LLM) responsável pelo desenvolvimento do código do script.

## 2. Requisitos Funcionais (RF)

**RF001: Entrada de Dados**
    - O script DEVE aceitar uma ou mais URLs de vídeos do YouTube como entrada.
    - Formato de entrada: Lista de strings (URLs).

**RF002: Download de Áudio**
    - O script DEVE baixar o áudio dos vídeos do YouTube fornecidos.
    - Especificação da Biblioteca: Recomenda-se `yt-dlp` ou `pytube`.
    - Formato do Áudio: O áudio deve ser salvo em um formato compatível com a API da OpenAI (e.g., MP3, WAV, M4A).

**RF003: Transcrição de Áudio com OpenAI**
    - O script DEVE enviar o arquivo de áudio baixado para a API de Speech-to-Text da OpenAI.
    - Endpoint: API de Transcrição da OpenAI.
    - Requisito de Timestamps: O script DEVE requisitar timestamps em nível de palavra.
        - Parâmetro da API: `timestamp_granularities[]` configurado para `word`.
        - Referência: [OpenAI Speech-to-Text Timestamps](https://platform.openai.com/docs/guides/speech-to-text#timestamps)
    - O script DEVE manipular a resposta da API, que incluirá uma lista de palavras com `word`, `start` (tempo de início) e `end` (tempo de fim) para cada palavra.

**RF004: Processamento da Transcrição**
    - O script DEVE receber e processar a transcrição retornada pela API da OpenAI.
    - Dados a serem extraídos: Texto transcrito e os timestamps de cada palavra.

**RF005: Geração de Conteúdo do Ebook**
    - O script DEVE utilizar a transcrição detalhada (texto e timestamps) para gerar o conteúdo textual do ebook.
    - Estruturação do Conteúdo: O conteúdo deve ser organizado de forma lógica. Considerar a utilização de timestamps para identificar pausas ou mudanças de tópico que possam indicar seções ou capítulos.

**RF006: Formatação do Ebook com WeasyPrint**
    - O script DEVE formatar o conteúdo gerado em um arquivo PDF utilizando a biblioteca WeasyPrint.
    - Entrada para WeasyPrint: O conteúdo textual DEVE ser estruturado em HTML.
    - Estilização: CSS DEVE ser usado para definir o layout, fontes, margens, cabeçalhos, rodapés e outros aspectos visuais do ebook.
    - Referência: [Documentação WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/index.html)

**RF007: Saída do Ebook**
    - O script DEVE salvar o ebook gerado como um arquivo PDF no sistema de arquivos local.
    - Nome do Arquivo: Configurável, podendo ser derivado do título do vídeo ou especificado pelo usuário.

## 3. Requisitos Não Funcionais (RNF)

**RNF001: Modularidade do Código**
    - O script DEVE ser organizado em módulos ou funções distintas para cada etapa principal:
        1.  Interface de entrada de URLs.
        2.  Download de áudio.
        3.  Interação com API OpenAI.
        4.  Processamento de transcrição.
        5.  Geração de HTML para o ebook.
        6.  Geração de PDF com WeasyPrint.
        7. Exibir custo da API OpenAI por processamento com a moeda do Brasil, cotação de 1usd = 5,48BRL.
        8. Para teste use o link "<https://www.youtube.com/watch?v=5vfVUOFVPYg>"

**RNF002: Gerenciamento de Configuração**
    - Chaves de API (especificamente OpenAI API Key) DEVEM ser gerenciadas de forma segura e configurável (e.g., variáveis de ambiente, arquivo de configuração dedicado, ou argumentos de linha de comando). NÃO DEVEM ser hardcoded no script.

**RNF003: Tratamento de Erros**
    - O script DEVE implementar tratamento de erros para as seguintes situações (mínimo):
        - URL do YouTube inválida ou vídeo indisponível.
        - Falha no download do áudio.
        - Erros de comunicação com a API da OpenAI (e.g., autenticação, limites de taxa, erros de processamento).
        - Erros durante a geração do HTML.
        - Erros durante a conversão de HTML para PDF com WeasyPrint.
    - O script DEVE registrar logs de erros informativos.

**RNF004: Feedback ao Usuário/Executor**
    - O script DEVE fornecer feedback sobre o progresso do processamento (e.g., "Baixando áudio de URL X...", "Transcrevendo áudio...", "Gerando PDF...").
    - Ao final, DEVE indicar o caminho do arquivo PDF gerado ou a ocorrência de erros.

## 4. Pilha Tecnológica (Tech Stack)

**4.1. Linguagem de Programação:**
    - Python (versão 3.8 ou superior).

**4.2. Bibliotecas Principais:**
    - Para download do YouTube: `yt-dlp` (preferencial) ou `pytube`.
    - Para interação com API OpenAI: `openai`.
    - Para geração de PDF: `WeasyPrint`.

**4.3. APIs Externas:**
    - OpenAI API (Speech-to-Text).

## 5. Fluxo de Processamento de Dados

1. **Entrada:** O script recebe uma lista de URLs do YouTube.
2. **Iteração por URL:** Para cada URL na lista:
   a.  **Download do Áudio:** Utiliza a biblioteca de download para obter o arquivo de áudio. Salva temporariamente.
   b.  **Transcrição:** Envia o arquivo de áudio para a API da OpenAI, solicitando `timestamp_granularities[]=word`.
   c.  **Recepção e Análise da Transcrição:** Recebe os dados JSON da OpenAI, extraindo as palavras e seus timestamps `start` e `end`.
3. **Geração de Conteúdo Agregado (se múltiplos vídeos):** Define como as transcrições de múltiplos vídeos serão combinadas ou separadas no ebook (e.g., um vídeo por capítulo).
4. **Construção do HTML:**
   a.  A transcrição processada (com palavras e timestamps) é convertida em uma estrutura HTML.
   b.  Elementos HTML (parágrafos, cabeçalhos, etc.) são gerados com base no texto.
   c.  Timestamps podem ser usados para adicionar metadados ou notas (visíveis ou não no PDF final).
5. **Aplicação de Estilo (CSS):**
   a.  Um arquivo CSS (ou string CSS) define a aparência do ebook (fontes, margens, layout de página, numeração de página, etc.).
6. **Geração do PDF:**
   a.  WeasyPrint é invocado com o documento HTML e o CSS associado.
   b.  WeasyPrint renderiza o HTML+CSS para um arquivo PDF.
7. **Saída:** O arquivo PDF é salvo no diretório especificado.
8. **Limpeza:** Arquivos temporários (como áudios baixados) DEVEM ser removidos após o processamento.

## 6. Estrutura do Ebook (Formato de Saída)

**6.1. Formato do Arquivo:**
    - PDF.

**6.2. Conteúdo Mínimo:**
    - Título do Ebook (pode ser derivado do título do vídeo).
    - Corpo principal: Texto transcrito do(s) vídeo(s).
    - Os parágrafos devem ser formados a partir do texto transcrito.

**6.3. Estrutura Potencial (a ser definida no desenvolvimento do template HTML/CSS):**
    - Página de rosto (Título, Autor - se aplicável).
    - Sumário (opcional, especialmente para múltiplos vídeos/capítulos).
    - Capítulos/Seções (um por vídeo, ou baseado em segmentos lógicos da transcrição).
    - Numeração de páginas.
    - Cabeçalhos/Rodapés.

**6.4. Layout:**
    - Definido primariamente pelo CSS fornecido ao WeasyPrint.
    - Deve priorizar a legibilidade.

## 7. Considerações Adicionais

- **Desempenho:** Para vídeos muito longos, o processo de download e transcrição pode ser demorado. O script deve lidar com isso de forma eficiente.
- **Custos da API OpenAI:** O uso da API da OpenAI incorre em custos. O script deve ser usado conscientemente.
- **Qualidade da Transcrição:** A qualidade da transcrição depende da qualidade do áudio e da capacidade da API da OpenAI.
- **Direitos Autorais:** O usuário do script é responsável por garantir que tem o direito de baixar e processar o conteúdo dos vídeos do YouTube.
