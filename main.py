#!/usr/bin/env python3
"""
Gerador de Ebook a partir de Vídeos do YouTube

Este script automatiza a criação de ebooks a partir do conteúdo de vídeos do YouTube.
Ele baixa o áudio, transcreve usando a API da OpenAI, processa o conteúdo com IA
para criar um ebook estruturado e gera um PDF formatado.
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import openai
import yt_dlp
from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

# Importa todas as configurações do projeto
from config import *
from prompts.system_prompt_ebook import SYSTEM_PROMPT_EBOOK
from prompts.user_prompt_ebook import get_user_prompt_ebook

# Configura logging usando as configurações centralizadas
logger = setup_logging()

# Configuração da API OpenAI
openai.api_key = OPENAI_API_KEY


class YouTubeEbookGenerator:
    """Classe principal para gerar ebooks a partir de vídeos do YouTube."""

    def __init__(self, output_dir: str = None):
        """
        Inicializa o gerador de ebooks.

        Args:
            output_dir: Diretório para salvar os arquivos de saída (usa DEFAULT_OUTPUT_DIR se None)
        """
        self.output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = None
        self.total_cost_usd = 0.0

        # Verifica se a API key está configurada
        if not openai.api_key:
            raise ValueError('OPENAI_API_KEY não encontrada. Configure a variável de ambiente.')

    def __enter__(self):
        """Context manager para gerenciar arquivos temporários."""
        self.temp_dir = tempfile.mkdtemp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Limpa arquivos temporários."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)
            logger.info(f'Arquivos temporários removidos: {self.temp_dir}')

    def download_audio(self, url: str) -> Dict[str, Any]:
        """
        Baixa o áudio de um vídeo do YouTube.

        Args:
            url: URL do vídeo do YouTube

        Returns:
            Dict com informações do vídeo e caminho do arquivo de áudio
        """
        logger.info(f'Baixando áudio de: {url}')

        # Configuração do yt-dlp usando configurações centralizadas
        ydl_opts = {
            'format': YT_DLP_FORMAT,
            'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': AUDIO_FORMAT,
                    'preferredquality': AUDIO_QUALITY,
                }
            ],
            'quiet': YT_DLP_QUIET,
            'no_warnings': YT_DLP_NO_WARNINGS,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extrai informações do vídeo
                info = ydl.extract_info(url, download=False)
                video_info = {
                    'title': info.get('title', 'Vídeo sem título'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Desconhecido'),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'url': url,
                }

                # Baixa o áudio
                ydl.download([url])

                # Encontra o arquivo de áudio baixado
                audio_files = list(Path(self.temp_dir).glob('*.mp3'))
                if not audio_files:
                    raise FileNotFoundError('Arquivo de áudio não encontrado após download')

                video_info['audio_path'] = str(audio_files[0])
                logger.info(f'Áudio baixado com sucesso: {video_info["title"]}')

                return video_info

        except Exception as e:
            logger.error(f'Erro ao baixar áudio de {url}: {str(e)}')
            raise

    def segment_audio(self, audio_path: str) -> List[str]:
        """
        Segmenta um arquivo de áudio em partes menores usando FFmpeg.

        Args:
            audio_path: Caminho para o arquivo de áudio original

        Returns:
            Lista com caminhos dos segmentos de áudio
        """
        import subprocess

        logger.info(f'Segmentando áudio: {audio_path}')

        # Obtém a duração do áudio
        duration_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', audio_path]

        try:
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
            duration_seconds = float(duration_result.stdout.strip())
            logger.info(f'Duração do áudio: {duration_seconds:.2f} segundos')
        except subprocess.CalledProcessError as e:
            logger.error(f'Erro ao obter duração do áudio: {e}')
            raise

        # Calcula o número de segmentos necessários
        segment_duration = AUDIO_SEGMENT_DURATION_MINUTES * 60
        num_segments = int(duration_seconds / segment_duration) + 1

        if num_segments == 1:
            logger.info('Áudio não precisa ser segmentado')
            return [audio_path]

        logger.info(f'Segmentando em {num_segments} partes de {AUDIO_SEGMENT_DURATION_MINUTES} minutos cada')

        segments = []
        base_name = Path(audio_path).stem

        for i in range(num_segments):
            start_time = i * segment_duration
            # Adiciona sobreposição exceto no primeiro segmento
            if i > 0:
                start_time -= AUDIO_SEGMENT_OVERLAP_SECONDS

            segment_path = os.path.join(self.temp_dir, f'{base_name}_segment_{i + 1:02d}.mp3')

            # Comando FFmpeg para extrair segmento
            ffmpeg_cmd = [
                'ffmpeg',
                '-i',
                audio_path,
                '-ss',
                str(start_time),
                '-t',
                str(segment_duration + AUDIO_SEGMENT_OVERLAP_SECONDS),
                '-acodec',
                'copy',
                '-y',
                segment_path,
            ]

            try:
                subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
                segments.append(segment_path)
                logger.info(f'Segmento {i + 1}/{num_segments} criado: {segment_path}')
            except subprocess.CalledProcessError as e:
                logger.error(f'Erro ao criar segmento {i + 1}: {e}')
                raise

        return segments

    def transcribe_audio_segments(self, segments: List[str]) -> Dict[str, Any]:
        """
        Transcreve múltiplos segmentos de áudio e combina os resultados.

        Args:
            segments: Lista de caminhos para segmentos de áudio

        Returns:
            Dict com transcrição combinada
        """
        logger.info(f'Transcrevendo {len(segments)} segmentos de áudio')

        all_transcriptions = []
        total_duration = 0

        for i, segment_path in enumerate(segments, 1):
            logger.info(f'Transcrevendo segmento {i}/{len(segments)}')

            try:
                with open(segment_path, 'rb') as audio_file:
                    # Calcula o custo estimado
                    file_size_mb = os.path.getsize(segment_path) / (1024 * 1024)
                    estimated_duration_minutes = file_size_mb / AUDIO_SIZE_DURATION_RATIO
                    estimated_cost = estimated_duration_minutes * OPENAI_WHISPER_COST_PER_MINUTE
                    self.total_cost_usd += estimated_cost

                    logger.info(f'Segmento {i}: {file_size_mb:.2f}MB - Custo estimado: ${estimated_cost:.4f} USD')

                    # Chama a API da OpenAI
                    response = openai.audio.transcriptions.create(
                        model=OPENAI_WHISPER_MODEL,
                        file=audio_file,
                        response_format='verbose_json',
                    )

                    all_transcriptions.append(response.text)
                    total_duration += response.duration if hasattr(response, 'duration') else 0

                    logger.info(f'Segmento {i} transcrito com sucesso')

            except Exception as e:
                logger.error(f'Erro na transcrição do segmento {i}: {str(e)}')
                raise

        # Combina todas as transcrições
        combined_text = ' '.join(all_transcriptions)

        logger.info('Todos os segmentos transcritos e combinados com sucesso')

        return {'text': combined_text, 'duration': total_duration, 'segments_count': len(segments)}

    def check_audio_size_and_transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Verifica o tamanho do áudio e decide se precisa segmentar antes de transcrever.

        Args:
            audio_path: Caminho para o arquivo de áudio

        Returns:
            Dict com a transcrição
        """
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        logger.info(f'Tamanho do arquivo de áudio: {file_size_mb:.2f}MB')

        if file_size_mb > MAX_AUDIO_FILE_SIZE_MB:
            logger.warning(f'Arquivo muito grande ({file_size_mb:.2f}MB > {MAX_AUDIO_FILE_SIZE_MB}MB)')
            logger.info('Segmentando áudio antes da transcrição...')

            segments = self.segment_audio(audio_path)
            return self.transcribe_audio_segments(segments)
        else:
            logger.info('Arquivo dentro do limite, transcrevendo diretamente')
            return self.transcribe_audio(audio_path)

    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcreve o áudio usando a API da OpenAI.

        Args:
            audio_path: Caminho para o arquivo de áudio

        Returns:
            Dict com a transcrição
        """
        logger.info(f'Transcrevendo áudio: {audio_path}')

        try:
            with open(audio_path, 'rb') as audio_file:
                # Calcula o custo estimado usando configurações centralizadas
                file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                estimated_duration_minutes = file_size_mb / AUDIO_SIZE_DURATION_RATIO
                estimated_cost = estimated_duration_minutes * OPENAI_WHISPER_COST_PER_MINUTE
                self.total_cost_usd += estimated_cost

                logger.info(f'Enviando para transcrição (custo estimado: ${estimated_cost:.4f} USD)')

                # Chama a API da OpenAI usando configurações centralizadas
                response = openai.audio.transcriptions.create(
                    model=OPENAI_WHISPER_MODEL,
                    file=audio_file,
                    response_format='verbose_json',
                )

                logger.info('Transcrição concluída com sucesso')
                return {
                    'text': response.text,
                    'duration': response.duration if hasattr(response, 'duration') else 0,
                }

        except Exception as e:
            logger.error(f'Erro na transcrição: {str(e)}')
            raise

    def save_transcription(self, transcription: Dict[str, Any], video_info: Dict[str, Any]) -> str:
        """
        Salva a transcrição em arquivo JSON para processamento posterior.

        Args:
            transcription: Dados da transcrição
            video_info: Informações do vídeo

        Returns:
            Caminho do arquivo de transcrição salvo
        """
        logger.info('Salvando transcrição em arquivo...')

        # Converte a transcrição para formato serializável
        serializable_transcription = {'text': transcription['text'], 'duration': transcription['duration']}

        # Prepara dados para salvar
        transcription_data = {
            'video_info': video_info,
            'transcription': serializable_transcription,
            'generated_at': datetime.now().isoformat(),
        }

        # Nome do arquivo baseado no título do vídeo
        safe_title = ''.join(c for c in video_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f'transcricao_{safe_title[:30]}.json'
        filepath = self.output_dir / filename

        # Salva o arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(transcription_data, f, ensure_ascii=False, indent=2)

        logger.info(f'Transcrição salva em: {filepath}')
        return str(filepath)

    def generate_ebook_content(self, transcription_file: str) -> Dict[str, Any]:
        """
        Processa a transcrição usando OpenAI para gerar conteúdo estruturado do ebook.

        Args:
            transcription_file: Caminho do arquivo de transcrição

        Returns:
            Dict com conteúdo estruturado do ebook
        """
        logger.info('Processando transcrição com OpenAI para gerar conteúdo do ebook...')

        # Carrega a transcrição
        with open(transcription_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        transcription_text = data['transcription']['text']
        video_info = data['video_info']

        # Prompt avançado para estruturar o conteúdo do ebook com máximo detalhamento
        system_prompt = SYSTEM_PROMPT_EBOOK
        user_prompt = get_user_prompt_ebook(video_info, transcription_text, self._format_duration)

        try:
            # Estima tokens para calcular custo
            estimated_tokens = len(transcription_text) // 3  # Estimativa aproximada
            estimated_cost = (estimated_tokens / 1000) * OPENAI_GPT_COST_PER_1K_TOKENS
            self.total_cost_usd += estimated_cost

            logger.info(f'Enviando para processamento GPT (custo estimado: ${estimated_cost:.4f} USD)')

            # Tenta processar com retry em caso de falha usando configurações centralizadas
            ebook_content = None

            for attempt in range(MAX_API_RETRIES + 1):
                try:
                    logger.info(f'Tentativa {attempt + 1}/{MAX_API_RETRIES + 1} de processamento GPT')

                    # Chama a API da OpenAI usando configurações centralizadas
                    response = openai.chat.completions.create(
                        model=OPENAI_GPT_MODEL,
                        messages=[
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': user_prompt},
                        ],
                        temperature=OPENAI_GPT_TEMPERATURE,
                        max_tokens=OPENAI_GPT_MAX_TOKENS,
                    )

                    break  # Sai do loop se a chamada foi bem-sucedida

                except Exception as api_error:
                    logger.warning(f'Tentativa {attempt + 1} falhou: {api_error}')
                    if attempt == MAX_API_RETRIES:
                        raise api_error
                    logger.info(f'Tentando novamente em {RETRY_DELAY} segundos...')
                    import time

                    time.sleep(RETRY_DELAY)

            # Extrai o conteúdo da resposta
            content = response.choices[0].message.content

            # Função para limpar e corrigir JSON malformado
            def clean_json_content(json_str: str) -> str:
                """Limpa e corrige problemas comuns em JSON gerado por IA."""
                import re

                # Remove markdown code blocks se existirem
                json_str = re.sub(r'```json\s*', '', json_str)
                json_str = re.sub(r'```\s*$', '', json_str)

                # Remove texto antes e depois do JSON
                json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if json_match:
                    json_str = json_match.group()

                # Corrige aspas simples para duplas (problema comum)
                json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)

                # Corrige trailing commas
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

                # Corrige quebras de linha dentro de strings
                json_str = re.sub(r'"\s*\n\s*([^"]*)\s*\n\s*"', r'"\1"', json_str)

                return json_str

            # Tenta fazer parse do JSON com múltiplas estratégias
            ebook_content = None
            original_content = content

            # Estratégia 1: Parse direto
            try:
                ebook_content = json.loads(content)
                logger.info('JSON parseado com sucesso na primeira tentativa')
            except json.JSONDecodeError as e:
                logger.warning(f'Primeira tentativa de parse falhou: {e}')

                # Estratégia 2: Limpar e tentar novamente
                try:
                    cleaned_content = clean_json_content(content)
                    ebook_content = json.loads(cleaned_content)
                    logger.info('JSON parseado com sucesso após limpeza')
                except json.JSONDecodeError as e:
                    logger.warning(f'Segunda tentativa de parse falhou: {e}')

                    # Estratégia 3: Tentar corrigir caracteres problemáticos
                    try:
                        # Remove caracteres de controle
                        import unicodedata

                        cleaned_content = ''.join(
                            ch for ch in content if unicodedata.category(ch)[0] != 'C' or ch in '\n\r\t'
                        )
                        cleaned_content = clean_json_content(cleaned_content)
                        ebook_content = json.loads(cleaned_content)
                        logger.info('JSON parseado com sucesso após limpeza de caracteres')
                    except json.JSONDecodeError as e:
                        logger.error(f'Todas as tentativas de parse falharam: {e}')

                        # Salva o conteúdo problemático para debug usando configurações centralizadas
                        debug_file = self.output_dir / DEBUG_OPENAI_RESPONSE_FILE
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(f'Resposta original da OpenAI:\n{original_content}\n\n')
                            f.write(f'Erro de parse: {e}\n')

                        logger.error(f'Resposta problemática salva em: {debug_file}')
                        raise ValueError(
                            f'Não foi possível fazer parse do JSON retornado pela OpenAI. Erro: {e}\nResposta salva em: {debug_file}'
                        )

            if ebook_content is None:
                raise ValueError('Falha crítica no processamento do JSON da OpenAI')

            # Valida a estrutura do JSON
            def validate_ebook_structure(data: dict) -> bool:
                """Valida se o JSON tem a estrutura esperada do ebook."""
                required_fields = ['title', 'subtitle', 'author', 'description', 'chapters', 'conclusion', 'key_points']

                for field in required_fields:
                    if field not in data:
                        logger.warning(f'Campo obrigatório ausente: {field}')
                        return False

                if not isinstance(data['chapters'], list) or len(data['chapters']) == 0:
                    logger.warning('Campo chapters deve ser uma lista não vazia')
                    return False

                for i, chapter in enumerate(data['chapters']):
                    if not isinstance(chapter, dict):
                        logger.warning(f'Capítulo {i} deve ser um objeto')
                        return False

                    chapter_required = ['title', 'content']
                    for field in chapter_required:
                        if field not in chapter:
                            logger.warning(f'Campo obrigatório ausente no capítulo {i}: {field}')
                            return False

                return True

            # Valida a estrutura
            if not validate_ebook_structure(ebook_content):
                logger.error('Estrutura do JSON inválida')
                # Salva para debug mesmo assim usando configurações centralizadas
                debug_file = self.output_dir / DEBUG_INVALID_STRUCTURE_FILE
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(ebook_content, f, ensure_ascii=False, indent=2)
                logger.error(f'JSON com estrutura inválida salvo em: {debug_file}')
                raise ValueError(f'JSON retornado pela OpenAI tem estrutura inválida. Arquivo salvo em: {debug_file}')

            logger.info('Estrutura do JSON validada com sucesso')

            # Salva o conteúdo estruturado
            safe_title = ''.join(c for c in video_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            content_filename = f'ebook_content_{safe_title[:30]}.json'
            content_filepath = self.output_dir / content_filename

            with open(content_filepath, 'w', encoding='utf-8') as f:
                json.dump(ebook_content, f, ensure_ascii=False, indent=2)

            logger.info(f'Conteúdo estruturado salvo em: {content_filepath}')
            logger.info('Processamento com OpenAI concluído com sucesso')

            return ebook_content

        except Exception as e:
            logger.error(f'Erro no processamento com OpenAI: {str(e)}')
            raise

    def _process_markdown(self, text: str) -> str:
        """
        Processa markdown simples para HTML (negrito, itálico, listas).

        Args:
            text: Texto com markdown simples

        Returns:
            Texto com HTML
        """
        if not text:
            return text

        import re

        # Converte **texto** para <strong>texto</strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

        # Converte *texto* para <em>texto</em> (mas não se for início de lista)
        text = re.sub(r'(?<!^)\*([^*\n]+?)\*', r'<em>\1</em>', text, flags=re.MULTILINE)

        # Processa listas simples (linhas que começam com - ou *)
        lines = text.split('\n')
        processed_lines = []
        in_list = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('- ') or stripped.startswith('* '):
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                item_text = stripped[2:].strip()
                processed_lines.append(f'<li>{item_text}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                processed_lines.append(line)

        if in_list:
            processed_lines.append('</ul>')

        return '\n'.join(processed_lines)

    def generate_html_content(self, ebook_content: Dict[str, Any], video_info: Dict[str, Any]) -> str:
        """
        Gera o conteúdo HTML do ebook usando o conteúdo estruturado.

        Args:
            ebook_content: Conteúdo estruturado do ebook
            video_info: Informações do vídeo original

        Returns:
            String com o HTML do ebook
        """
        logger.info('Gerando conteúdo HTML estruturado...')

        # Carrega o template HTML usando configurações centralizadas
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

        # Adiciona filtro personalizado para processar markdown
        env.filters['markdown'] = self._process_markdown

        template = env.get_template(HTML_TEMPLATE_NAME)

        # Prepara dados para o template
        template_data = {
            'ebook_title': ebook_content.get('title', video_info['title']),
            'ebook_subtitle': ebook_content.get('subtitle', 'Ebook gerado automaticamente'),
            'ebook_author': ebook_content.get('author', video_info['uploader']),
            'ebook_description': ebook_content.get('description', ''),
            'chapters': ebook_content.get('chapters', []),
            'conclusion': ebook_content.get('conclusion', ''),
            'key_points': ebook_content.get('key_points', []),
            'video_info': {**video_info, 'formatted_duration': self._format_duration(video_info['duration'])},
            'generation_date': datetime.now().strftime('%d/%m/%Y às %H:%M'),
        }

        # Renderiza o template
        html_content = template.render(**template_data)

        return html_content

    def _format_duration(self, seconds: int) -> str:
        """Formata duração em segundos para formato legível."""
        if not seconds:
            return 'Desconhecido'

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        if hours > 0:
            return f'{hours}h {minutes}m {seconds}s'
        elif minutes > 0:
            return f'{minutes}m {seconds}s'
        else:
            return f'{seconds}s'

    def _format_cost(self, usd: float) -> str:
        """Formata custo em dólares para formato legível."""
        brl = usd * USD_TO_BRL
        return f'${usd:.4f} USD ({brl:.2f} BRL)'

    def generate_css(self) -> str:
        """
        Carrega o CSS do arquivo template usando configurações centralizadas.

        Returns:
            String com o CSS
        """
        css_path = get_template_dir() / CSS_TEMPLATE_NAME

        if not css_path.exists():
            logger.error(f'Arquivo CSS não encontrado: {css_path}')
            raise FileNotFoundError(f'Template CSS não encontrado: {css_path}')

        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        return css_content

    def generate_pdf(self, html_content: str, css_content: str, output_filename: str) -> str:
        """
        Gera o PDF usando WeasyPrint com base_url correto para templates.

        Args:
            html_content: Conteúdo HTML
            css_content: Conteúdo CSS
            output_filename: Nome do arquivo de saída

        Returns:
            Caminho do arquivo PDF gerado
        """
        logger.info('Gerando PDF...')

        try:
            # Define o base_url para o diretório de templates usando configurações centralizadas
            template_dir = get_template_dir().absolute()
            base_url = template_dir.as_uri() + '/'

            # Cria objetos HTML e CSS com base_url correto
            html_doc = HTML(string=html_content, base_url=base_url)
            css_doc = CSS(string=css_content, base_url=base_url)

            # Gera o PDF
            output_path = self.output_dir / output_filename
            html_doc.write_pdf(output_path, stylesheets=[css_doc])

            logger.info(f'PDF gerado com sucesso: {output_path}')
            return str(output_path)

        except Exception as e:
            logger.error(f'Erro ao gerar PDF: {str(e)}')
            raise

    def display_cost_summary(self):
        """Exibe o resumo de custos da API OpenAI."""
        cost_brl = self.total_cost_usd * USD_TO_BRL

        print('\n' + '=' * 50)
        print('RESUMO DE CUSTOS DA API OPENAI')
        print('=' * 50)
        print(f'Custo total (USD): ${self.total_cost_usd:.4f}')
        print(f'Custo total (BRL): R$ {cost_brl:.2f}')
        print(f'Cotação utilizada: 1 USD = R$ {USD_TO_BRL}')
        print('=' * 50)

    def process_video(self, url: str, output_filename: Optional[str] = None) -> str:
        """
        Processa um vídeo do YouTube seguindo o novo fluxo:
        1. Download do áudio
        2. Transcrição com OpenAI Whisper
        3. Salvamento da transcrição
        4. Processamento com OpenAI GPT para gerar conteúdo estruturado
        5. Geração do ebook com template

        Args:
            url: URL do vídeo do YouTube
            output_filename: Nome do arquivo de saída (opcional)

        Returns:
            Caminho do arquivo PDF gerado
        """
        logger.info(f'Iniciando processamento do vídeo: {url}')

        try:
            # Etapa 1: Download do áudio
            logger.info('Etapa 1/5: Download do áudio')
            video_info = self.download_audio(url)

            # Etapa 2: Transcrição (com verificação de tamanho automática)
            logger.info('Etapa 2/5: Transcrição com OpenAI Whisper')
            transcription = self.check_audio_size_and_transcribe(video_info['audio_path'])

            # Etapa 3: Salvamento da transcrição
            logger.info('Etapa 3/5: Salvamento da transcrição')
            transcription_file = self.save_transcription(transcription, video_info)

            # Etapa 4: Processamento com OpenAI para gerar conteúdo estruturado
            logger.info('Etapa 4/5: Processamento com OpenAI GPT para estruturar conteúdo')
            ebook_content = self.generate_ebook_content(transcription_file)

            # Etapa 5: Geração do ebook
            logger.info('Etapa 5/5: Geração do ebook')

            # Gera o nome do arquivo se não fornecido
            if not output_filename:
                safe_title = ''.join(c for c in video_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_filename = f'{safe_title[:50]}.pdf'

            # Garante que o arquivo tenha extensão .pdf
            if not output_filename.endswith('.pdf'):
                output_filename += '.pdf'

            # Gera HTML e CSS
            html_content = self.generate_html_content(ebook_content, video_info)
            css_content = self.generate_css()

            # Gera PDF
            pdf_path = self.generate_pdf(html_content, css_content, output_filename)

            # Exibe resumo de custos
            self.display_cost_summary()

            logger.info('Processamento concluído com sucesso!')
            return pdf_path

        except Exception as e:
            logger.error(f'Erro durante o processamento: {str(e)}')
            raise


def main():
    """Função principal do script."""
    # URL de teste conforme especificado no PRD
    test_url = DEFAULT_TEST_URL

    print('Gerador de Ebook a partir de Vídeos do YouTube')
    print('=' * 50)
    print('Novo fluxo de processamento:')
    print('1. Download do áudio')
    print('2. Transcrição com OpenAI Whisper')
    print('3. Salvamento da transcrição')
    print('4. Processamento com OpenAI GPT para estruturar conteúdo')
    print('5. Geração do ebook com template')
    print('=' * 50)

    # Verifica se a API key está configurada
    if not os.getenv('OPENAI_API_KEY'):
        print('ERRO: Configure a variável de ambiente OPENAI_API_KEY')
        print("Exemplo: export OPENAI_API_KEY='sua-api-key-aqui'")
        return 1

    try:
        print(f'Processando vídeo de teste: {test_url}')

        # Processa o vídeo
        with YouTubeEbookGenerator() as generator:
            pdf_path = generator.process_video(test_url)

        print('\n✅ Ebook gerado com sucesso!')
        print(f'📁 Arquivo salvo em: {pdf_path}')
        print(f'📊 Tamanho do arquivo: {os.path.getsize(pdf_path) / 1024 / 1024:.2f} MB')

        return 0

    except Exception as e:
        logger.error(f'Erro durante a execução: {str(e)}')
        print(f'\n❌ Erro: {str(e)}')
        return 1


def app():
    """Ponto de entrada para o script como aplicação."""
    sys.exit(main())


if __name__ == '__main__':
    app()
