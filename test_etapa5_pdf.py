#!/usr/bin/env python3
"""
Teste da Etapa 5: Geração do PDF final

Este script testa a geração do PDF usando WeasyPrint
a partir do HTML e CSS.
"""

import json
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar main
sys.path.insert(0, str(Path(__file__).parent))

from main import YouTubeEbookGenerator


def find_latest_html():
    """Encontra o arquivo HTML mais recente."""
    output_dir = Path('output')
    if not output_dir.exists():
        return None

    html_files = list(output_dir.glob('ebook_html_*.html'))
    if not html_files:
        return None

    # Retorna o arquivo mais recente
    return max(html_files, key=lambda f: f.stat().st_mtime)


def test_pdf_generation():
    """Testa a geração do PDF."""
    print('=' * 60)
    print('TESTE ETAPA 5: GERAÇÃO DO PDF FINAL')
    print('=' * 60)

    # Procura arquivo HTML
    html_file = find_latest_html()

    if not html_file:
        print('❌ Nenhum arquivo HTML encontrado!')
        print('💡 Execute primeiro: python test_etapa4_template.py')
        return False

    print(f'📁 Usando arquivo HTML: {html_file}')

    try:
        # Carrega o HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Procura informações do vídeo para o nome do arquivo
        transcription_files = list(Path('output').glob('transcricao_*.json'))
        if transcription_files:
            transcription_file = max(transcription_files, key=lambda f: f.stat().st_mtime)
            with open(transcription_file, 'r', encoding='utf-8') as f:
                transcription_data = json.load(f)
            video_info = transcription_data['video_info']
        else:
            video_info = {'title': 'Ebook_Teste'}

        print(f'\n📺 Vídeo: {video_info.get("title", "N/A")}')
        print(f'📄 Tamanho do HTML: {len(html_content):,} caracteres')

        with YouTubeEbookGenerator() as generator:
            print('\n🔄 Carregando CSS...')

            # Carrega o CSS
            css_content = generator.generate_css()
            print(f'✅ CSS carregado: {len(css_content):,} caracteres')

            print('\n🔄 Gerando PDF com WeasyPrint...')
            print('⏳ Este processo pode levar alguns minutos...')

            # Nome do arquivo PDF
            safe_title = ''.join(c for c in video_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            pdf_filename = f'ebook_teste_{safe_title[:30]}.pdf'

            # Gera o PDF
            pdf_path = generator.generate_pdf(html_content, css_content, pdf_filename)

            print('✅ PDF gerado com sucesso!')

            # Estatísticas do PDF
            pdf_file = Path(pdf_path)
            if pdf_file.exists():
                file_size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print('\n📊 Estatísticas do PDF:')
                print(f'   📁 Arquivo: {pdf_path}')
                print(f'   📊 Tamanho: {file_size_mb:.2f} MB')

                # Verifica se o arquivo não está vazio
                if file_size_mb > 0.1:  # Pelo menos 100KB
                    print('   ✅ Arquivo parece válido')
                else:
                    print('   ⚠️  Arquivo muito pequeno, pode estar corrompido')

                # Tenta abrir o arquivo para verificar se não está corrompido
                try:
                    with open(pdf_path, 'rb') as f:
                        header = f.read(8)
                    if header.startswith(b'%PDF'):
                        print('   ✅ Cabeçalho PDF válido')
                    else:
                        print('   ❌ Cabeçalho PDF inválido')
                except Exception as e:
                    print(f'   ❌ Erro ao verificar PDF: {e}')

            else:
                print('   ❌ Arquivo PDF não encontrado!')
                return False

            # Verifica se os templates existem
            template_checks = [
                ('template/ebook.html', 'Template HTML'),
                ('template/ebook.css', 'Template CSS'),
                ('template/cover.jpg', 'Imagem de capa'),
                ('template/OpenSans-VariableFont_wdth,wght.ttf', 'Fonte OpenSans'),
            ]

            print('\n✅ Verificações dos templates:')
            for file_path, description in template_checks:
                exists = Path(file_path).exists()
                status = '✅' if exists else '❌'
                print(f'   {status} {description}')

            return True

    except Exception as e:
        print(f'\n❌ Erro durante a geração do PDF: {str(e)}')
        import traceback

        print('📋 Detalhes do erro:')
        traceback.print_exc()
        return False


def main():
    """Função principal do teste."""
    success = test_pdf_generation()

    if success:
        print('\n' + '=' * 60)
        print('✅ TESTE DA ETAPA 5 CONCLUÍDO COM SUCESSO!')
        print('🎉 PDF gerado e pronto para uso!')
        print('=' * 60)
        return 0
    else:
        print('\n' + '=' * 60)
        print('❌ TESTE DA ETAPA 5 FALHOU!')
        print('=' * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
