#!/usr/bin/env python3
"""
Teste da Etapa 4: Geração do template HTML

Este script testa a geração do HTML usando o conteúdo estruturado
e o template Jinja2.
"""

import json
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar main
sys.path.insert(0, str(Path(__file__).parent))

from main import YouTubeEbookGenerator


def find_latest_ebook_content():
    """Encontra o arquivo de conteúdo estruturado mais recente."""
    output_dir = Path('output')
    if not output_dir.exists():
        return None

    content_files = list(output_dir.glob('ebook_content_*.json'))
    if not content_files:
        return None

    # Retorna o arquivo mais recente
    return max(content_files, key=lambda f: f.stat().st_mtime)


def test_template_generation():
    """Testa a geração do template HTML."""
    print('=' * 60)
    print('TESTE ETAPA 4: GERAÇÃO DO TEMPLATE HTML')
    print('=' * 60)

    # Procura arquivo de conteúdo estruturado
    content_file = find_latest_ebook_content()

    if not content_file:
        print('❌ Nenhum arquivo de conteúdo estruturado encontrado!')
        print('💡 Execute primeiro: python test_etapa3_processamento_gpt.py')
        return False

    print(f'📁 Usando arquivo de conteúdo: {content_file}')

    try:
        # Carrega o conteúdo estruturado
        with open(content_file, 'r', encoding='utf-8') as f:
            ebook_content = json.load(f)

        # Procura informações do vídeo original
        transcription_files = list(Path('output').glob('transcricao_*.json'))
        if not transcription_files:
            print('❌ Arquivo de transcrição não encontrado!')
            return False

        transcription_file = max(transcription_files, key=lambda f: f.stat().st_mtime)
        with open(transcription_file, 'r', encoding='utf-8') as f:
            transcription_data = json.load(f)

        video_info = transcription_data['video_info']

        print(f'\n📺 Vídeo: {video_info["title"]}')
        print(f'👤 Canal: {video_info["uploader"]}')
        print(f'📖 Título do ebook: {ebook_content.get("title", "N/A")}')
        print(f'📚 Capítulos: {len(ebook_content.get("chapters", []))}')

        with YouTubeEbookGenerator() as generator:
            print('\n🔄 Gerando HTML do ebook...')

            # Gera o HTML
            html_content = generator.generate_html_content(ebook_content, video_info)

            print('✅ HTML gerado com sucesso!')

            # Estatísticas do HTML
            print('\n📊 Estatísticas do HTML:')
            print(f'   📝 Caracteres: {len(html_content):,}')
            print(f'   📄 Linhas: {len(html_content.splitlines()):,}')

            # Salva o HTML para inspeção
            output_dir = Path('output')
            safe_title = ''.join(c for c in video_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            html_filename = f'ebook_html_{safe_title[:30]}.html'
            html_filepath = output_dir / html_filename

            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f'\n💾 HTML salvo em: {html_filepath}')
            print('🌐 Você pode abrir este arquivo no navegador para visualizar')

            # Verifica elementos importantes no HTML
            checks = [
                ('Título principal', '<h1>' in html_content),
                ('Informações do vídeo', 'video-info' in html_content),
                ('Capítulos', 'chapter' in html_content),
                ('Conclusão', 'conclusion' in html_content and ebook_content.get('conclusion')),
                ('Pontos principais', 'key-points' in html_content and ebook_content.get('key_points')),
                ('CSS linkado', 'ebook.css' in html_content),
            ]

            print('\n✅ Verificações do HTML:')
            for check_name, check_result in checks:
                status = '✅' if check_result else '⚠️'
                print(f'   {status} {check_name}')

            # Mostra amostra do HTML
            html_lines = html_content.splitlines()
            print('\n📄 Amostra do HTML (primeiras 10 linhas):')
            for i, line in enumerate(html_lines[:10], 1):
                print(f'   {i:2d}: {line[:80]}{"..." if len(line) > 80 else ""}')

            return True

    except Exception as e:
        print(f'\n❌ Erro durante a geração do HTML: {str(e)}')
        return False


def main():
    """Função principal do teste."""
    success = test_template_generation()

    if success:
        print('\n' + '=' * 60)
        print('✅ TESTE DA ETAPA 4 CONCLUÍDO COM SUCESSO!')
        print('=' * 60)
        return 0
    else:
        print('\n' + '=' * 60)
        print('❌ TESTE DA ETAPA 4 FALHOU!')
        print('=' * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
