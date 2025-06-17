# Gerador de Ebook a partir de Vídeos do YouTube

Este script Python automatiza a criação de ebooks a partir do conteúdo de vídeos do YouTube. Ele baixa o áudio, transcreve usando a API da OpenAI e gera um PDF formatado.

## Funcionalidades

- ✅ Download de áudio de vídeos do YouTube
- ✅ Transcrição com timestamps palavra por palavra usando OpenAI Whisper
- ✅ Processamento inteligente de texto em parágrafos
- ✅ Geração de PDF profissional com WeasyPrint
- ✅ Cálculo de custos da API OpenAI em USD e BRL
- ✅ Tratamento de erros robusto
- ✅ Logs detalhados do processo

## Pré-requisitos

- Python 3.9 ou superior
- Chave da API OpenAI
- FFmpeg (para processamento de áudio)

### Instalação do FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Baixe de https://ffmpeg.org/download.html

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd content-video-generator
```

2. Crie um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -e .
```

4. Teste a instalação:
```bash
python test_setup.py
```

## Configuração

1. Obtenha sua chave da API OpenAI em: https://platform.openai.com/api-keys

2. Configure a variável de ambiente:
```bash
export OPENAI_API_KEY='sua-chave-api-aqui'
```

Ou crie um arquivo `.env` na raiz do projeto:
```
# Configurações do OpenAI
OPENAI_API_KEY=sk-proj-your-key-here
```

O projeto já inclui um arquivo `config.py` que centraliza todas as configurações e carrega automaticamente as variáveis do arquivo `.env`.

### Configurações Disponíveis

O arquivo `config.py` permite personalizar:

- **Custos e Cotação**: USD_TO_BRL (cotação do dólar)
- **Qualidade de Áudio**: AUDIO_QUALITY, AUDIO_FORMAT
- **Processamento**: PARAGRAPH_BREAK_THRESHOLD (pausas para quebra de parágrafo)
- **PDF**: Tamanho da página, margens, fontes, cores
- **URL de Teste**: DEFAULT_TEST_URL

## Uso

### Executar com URL de teste
```bash
python main.py
```

### Executar como aplicação instalada
```bash
content-video-generator
```

### Uso programático
```python
from main import YouTubeEbookGenerator

urls = [
    "https://www.youtube.com/watch?v=VIDEO_ID1",
    "https://www.youtube.com/watch?v=VIDEO_ID2"
]

with YouTubeEbookGenerator() as generator:
    pdf_path = generator.process_videos(urls, "meu_ebook.pdf")
    print(f"Ebook gerado: {pdf_path}")
```

## Estrutura do Ebook Gerado

O PDF gerado contém:

1. **Página de Rosto** - Título, subtítulo e data de geração
2. **Sumário** - Links para cada capítulo
3. **Capítulos** - Um para cada vídeo processado, contendo:
   - Título do vídeo
   - Informações do canal e duração
   - URL original
   - Conteúdo transcrito formatado em parágrafos

## Custos da API

O script calcula automaticamente os custos da API OpenAI:
- Modelo Whisper: $0.006 por minuto de áudio
- Conversão para BRL usando cotação configurável (padrão: 1 USD = 5.48 BRL)

## Arquivos Gerados

- `output/` - Diretório com os PDFs gerados
- `ebook_generator.log` - Log detalhado das operações
- Arquivos temporários são automaticamente removidos

## Limitações

- Vídeos muito longos podem ser custosos para transcrever
- Qualidade da transcrição depende da qualidade do áudio
- Respeite os direitos autorais dos vídeos processados

## Desenvolvimento

### Executar com Ruff (linting)
```bash
ruff check .
ruff format .
```

### Estrutura do Código

- `YouTubeEbookGenerator` - Classe principal
- `download_audio()` - Download usando yt-dlp
- `transcribe_audio()` - Transcrição com OpenAI
- `process_transcription()` - Processamento de texto
- `generate_html_content()` - Geração de HTML
- `generate_pdf()` - Conversão para PDF

## Troubleshooting

### Erro: "OPENAI_API_KEY não encontrada"
Configure a variável de ambiente com sua chave da API OpenAI.

### Erro: "FFmpeg not found"
Instale o FFmpeg seguindo as instruções dos pré-requisitos.

### Erro: "Vídeo indisponível"
Verifique se a URL está correta e o vídeo é público.

### Erro de transcrição
Verifique sua conta OpenAI e limites de uso da API.

## Licença

MIT License - veja o arquivo LICENSE para detalhes.