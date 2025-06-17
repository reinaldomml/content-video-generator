# Scripts de Teste - Gerador de Ebook

Este documento descreve como usar os scripts de teste para validar cada etapa do processo de geração de ebook.

## 📋 Visão Geral

O sistema foi dividido em 5 etapas principais, cada uma com seu próprio script de teste:

1. **Download do áudio** (`test_etapa1_download.py`)
2. **Transcrição** (`test_etapa2_transcricao.py`)
3. **Processamento GPT** (`test_etapa3_processamento_gpt.py`)
4. **Geração HTML** (`test_etapa4_template.py`)
5. **Geração PDF** (`test_etapa5_pdf.py`)

## 🚀 Configuração Inicial

### 1. Ativar Ambiente Virtual
```bash
source .venv/bin/activate
```

### 2. Configurar API Key da OpenAI
```bash
export OPENAI_API_KEY='sua-api-key-aqui'
```

### 3. Verificar Dependências
```bash
pip install -r requirements.txt
```

## 🧪 Scripts de Teste Individuais

### Etapa 1: Download do Áudio
```bash
python test_etapa1_download.py
```

**O que faz:**
- Baixa áudio do vídeo de teste
- Salva informações do vídeo em `output/video_info_test.json`
- **Não usa API da OpenAI** (sem custo)

**Arquivos gerados:**
- `output/video_info_test.json`

---

### Etapa 2: Transcrição
```bash
python test_etapa2_transcricao.py
```

**O que faz:**
- Usa arquivo de áudio da Etapa 1 (ou baixa novamente)
- Transcreve usando OpenAI Whisper
- Salva transcrição em `output/transcricao_*.json`
- **USA API DA OPENAI** (~$0.006 por minuto)

**Arquivos gerados:**
- `output/transcricao_*.json`

---

### Etapa 3: Processamento GPT
```bash
python test_etapa3_processamento_gpt.py
```

**O que faz:**
- Usa transcrição da Etapa 2
- Processa com GPT-4o-mini para estruturar conteúdo
- Salva conteúdo estruturado em `output/ebook_content_*.json`
- **USA API DA OPENAI** (~$0.00015 por 1000 tokens)

**Arquivos gerados:**
- `output/ebook_content_*.json`

---

### Etapa 4: Geração HTML
```bash
python test_etapa4_template.py
```

**O que faz:**
- Usa conteúdo estruturado da Etapa 3
- Gera HTML usando template Jinja2
- Salva HTML em `output/ebook_html_*.html`
- **Não usa API da OpenAI** (sem custo)

**Arquivos gerados:**
- `output/ebook_html_*.html`

---

### Etapa 5: Geração PDF
```bash
python test_etapa5_pdf.py
```

**O que faz:**
- Usa HTML da Etapa 4
- Gera PDF usando WeasyPrint
- Salva PDF em `output/ebook_teste_*.pdf`
- **Não usa API da OpenAI** (sem custo)

**Arquivos gerados:**
- `output/ebook_teste_*.pdf`

## 🎯 Teste Completo

### Executar Todas as Etapas
```bash
python test_all_etapas.py
```

**O que faz:**
- Executa todos os testes em sequência
- Para na primeira falha
- Mostra resumo final
- **USA API DA OPENAI** (custo total estimado)

### Teste Sem APIs (Simulado)
```bash
python test_template_simulado.py
```

**O que faz:**
- Testa template com dados simulados
- Gera HTML e PDF completos
- **Não usa API da OpenAI** (sem custo)
- Ideal para testar template e layout

**Arquivos gerados:**
- `output/ebook_simulado.html`
- `output/ebook_simulado.pdf`
- `output/dados_simulados.json`

## 💰 Estimativa de Custos

### Por Etapa:
- **Etapa 1**: Gratuito
- **Etapa 2**: ~$0.006 por minuto de áudio
- **Etapa 3**: ~$0.00015 por 1000 tokens
- **Etapa 4**: Gratuito
- **Etapa 5**: Gratuito

### Exemplo (vídeo de 10 minutos):
- Transcrição: $0.06 USD
- Processamento GPT: $0.03 USD
- **Total**: ~$0.09 USD (~R$ 0.50)

## 📁 Estrutura de Arquivos Gerados

```
output/
├── video_info_test.json          # Etapa 1
├── transcricao_*.json            # Etapa 2
├── ebook_content_*.json          # Etapa 3
├── ebook_html_*.html             # Etapa 4
├── ebook_teste_*.pdf             # Etapa 5
├── ebook_simulado.html           # Teste simulado
├── ebook_simulado.pdf            # Teste simulado
└── dados_simulados.json          # Teste simulado
```

## 🔧 Resolução de Problemas

### Erro: "OPENAI_API_KEY não encontrada"
```bash
export OPENAI_API_KEY='sua-api-key-aqui'
```

### Erro: "Template não encontrado"
Verifique se a pasta `template/` existe com os arquivos:
- `ebook.html`
- `ebook.css`
- `cover.jpg`
- `OpenSans-VariableFont_wdth,wght.ttf`

### Erro: "WeasyPrint failed"
Instale dependências do sistema:
```bash
# Ubuntu/Debian
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# macOS
brew install pango
```

### Erro: "yt-dlp failed"
Verifique conexão com internet e URL do vídeo.

## 📊 Interpretando Resultados

### ✅ Sucesso
- Todos os testes passaram
- Arquivos gerados corretamente
- PDF válido criado

### ❌ Falha
- Verifique logs de erro
- Confirme configuração da API
- Teste etapas individualmente

## 💡 Dicas

1. **Teste o template primeiro** com `test_template_simulado.py`
2. **Execute etapas individualmente** para debug
3. **Use dados existentes** - etapas reutilizam arquivos anteriores
4. **Monitore custos** - confirme antes de usar APIs
5. **Verifique dependências** - WeasyPrint precisa de libs do sistema

## 🎨 Personalização

Para testar com dados próprios:

1. Modifique `config.py` para alterar URL de teste
2. Edite `test_template_simulado.py` para dados customizados
3. Ajuste templates em `template/` conforme necessário

## 📞 Suporte

Se encontrar problemas:

1. Verifique logs detalhados nos scripts
2. Execute `test_template_simulado.py` primeiro
3. Confirme todas as dependências instaladas
4. Verifique configuração da API OpenAI