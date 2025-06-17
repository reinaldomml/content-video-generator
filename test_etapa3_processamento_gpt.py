#!/usr/bin/env python3
"""
Teste da Etapa 3: Processamento com GPT-4o-mini

Este script testa o processamento da transcrição usando GPT-4o-mini
para gerar conteúdo estruturado do ebook.
"""

import json
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar main
sys.path.insert(0, str(Path(__file__).parent))

from main import YouTubeEbookGenerator


def find_latest_transcription():
    """Encontra o arquivo de transcrição mais recente."""
    output_dir = Path('output')
    if not output_dir.exists():
        return None

    transcription_files = list(output_dir.glob('transcricao_*.json'))
    if not transcription_files:
        return None

    # Retorna o arquivo mais recente
    return max(transcription_files, key=lambda f: f.stat().st_mtime)


def test_gpt_processing():
    """Testa o processamento com GPT-4o-mini."""
    print('=' * 60)
    print('TESTE ETAPA 3: PROCESSAMENTO COM GPT-4O-MINI')
    print('=' * 60)

    # Procura arquivo de transcrição existente
    transcription_file = find_latest_transcription()

    if not transcription_file:
        print('❌ Nenhum arquivo de transcrição encontrado!')
        print('💡 Execute primeiro: python test_etapa2_transcricao.py')
        return False

    print(f'📁 Usando arquivo de transcrição: {transcription_file}')

    try:
        # Carrega a transcrição para mostrar informações
        with open(transcription_file, 'r', encoding='utf-8') as f:
            transcription_data = json.load(f)

        video_info = transcription_data['video_info']
        transcription_text = transcription_data['transcription']['text']

        print(f'\n📺 Vídeo: {video_info["title"]}')
        print(f'👤 Canal: {video_info["uploader"]}')
        print(f'📝 Caracteres da transcrição: {len(transcription_text)}')
        print(f'📝 Palavras: {len(transcription_text.split())}')

        # Estima custo do processamento GPT
        estimated_tokens = len(transcription_text) // 3  # Estimativa aproximada
        estimated_cost = (estimated_tokens / 1000) * 0.00015  # Custo GPT-4o-mini
        cost_brl = estimated_cost * 5.48

        print('\n💰 Custo estimado do processamento GPT:')
        print(f'   Tokens estimados: {estimated_tokens:,}')
        print(f'   ${estimated_cost:.4f} USD (R$ {cost_brl:.2f} BRL)')

        # Mostra amostra da transcrição
        sample_text = transcription_text[:300] + '...' if len(transcription_text) > 300 else transcription_text
        print('\n📄 Amostra da transcrição a ser processada:')
        print(f'   "{sample_text}"')

        # Confirma se deve prosseguir
        response = input('\n❓ Deseja prosseguir com o processamento GPT? (s/N): ').lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print('❌ Processamento cancelado pelo usuário.')
            return False

        with YouTubeEbookGenerator() as generator:
            print('\n🔄 Iniciando processamento com GPT-4o-mini...')
            print('⏳ Este processo pode levar alguns minutos...')

            # Processa com GPT
            ebook_content = generator.generate_ebook_content(str(transcription_file))

            print('\n✅ Processamento concluído com sucesso!')

            # Mostra estatísticas do conteúdo gerado
            print('\n📊 Estatísticas do conteúdo estruturado:')
            print(f'   📖 Título: {ebook_content.get("title", "N/A")}')
            print(f'   👤 Autor: {ebook_content.get("author", "N/A")}')
            print(f'   📚 Capítulos: {len(ebook_content.get("chapters", []))}')
            print(f'   🔑 Pontos principais: {len(ebook_content.get("key_points", []))}')
            print(f'   📝 Conclusão: {"Sim" if ebook_content.get("conclusion") else "Não"}')

            # Mostra títulos dos capítulos
            chapters = ebook_content.get('chapters', [])
            if chapters:
                print('\n📚 Títulos dos capítulos:')
                for i, chapter in enumerate(chapters, 1):
                    title = chapter.get('title', f'Capítulo {i}')
                    subsections = len(chapter.get('subsections', []))
                    print(f'   {i}. {title} ({subsections} subseções)')

            # Mostra pontos principais
            key_points = ebook_content.get('key_points', [])
            if key_points:
                print('\n🔑 Pontos principais:')
                for i, point in enumerate(key_points[:3], 1):  # Mostra apenas os 3 primeiros
                    print(f'   {i}. {point}')
                if len(key_points) > 3:
                    print(f'   ... e mais {len(key_points) - 3} pontos')

            # Mostra amostra da conclusão
            conclusion = ebook_content.get('conclusion', '')
            if conclusion:
                sample_conclusion = conclusion[:200] + '...' if len(conclusion) > 200 else conclusion
                print('\n📄 Amostra da conclusão:')
                print(f'   "{sample_conclusion}"')

            # Exibe resumo de custos
            generator.display_cost_summary()

            # Informa onde o arquivo foi salvo
            safe_title = ''.join(c for c in video_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            content_filename = f'ebook_content_{safe_title[:30]}.json'
            content_filepath = Path('output') / content_filename
            print(f'\n💾 Conteúdo estruturado salvo em: {content_filepath}')

            return True

    except Exception as e:
        print(f'\n❌ Erro durante o processamento: {str(e)}')
        return False


def main():
    """Função principal do teste."""
    # Verifica se a API key está configurada
    if not os.getenv('OPENAI_API_KEY'):
        print('❌ ERRO: Configure a variável de ambiente OPENAI_API_KEY')
        print("Exemplo: export OPENAI_API_KEY='sua-api-key-aqui'")
        return 1

    success = test_gpt_processing()

    if success:
        print('\n' + '=' * 60)
        print('✅ TESTE DA ETAPA 3 CONCLUÍDO COM SUCESSO!')
        print('=' * 60)
        return 0
    else:
        print('\n' + '=' * 60)
        print('❌ TESTE DA ETAPA 3 FALHOU!')
        print('=' * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
