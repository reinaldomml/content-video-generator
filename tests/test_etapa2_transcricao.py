#!/usr/bin/env python3
"""
Teste da Etapa 2: Transcrição do áudio

Este script testa a transcrição do áudio usando a API OpenAI Whisper.
Pode usar um arquivo de áudio existente ou baixar um novo.
"""

import json
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar main
sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_TEST_URL
from main import YouTubeEbookGenerator


def test_transcription():
    """Testa a transcrição do áudio."""
    print('=' * 60)
    print('TESTE ETAPA 2: TRANSCRIÇÃO DO ÁUDIO')
    print('=' * 60)

    # Verifica se existe um arquivo de vídeo info de teste anterior
    video_info_file = Path('output/video_info_test.json')

    try:
        with YouTubeEbookGenerator() as generator:
            if video_info_file.exists():
                print('📁 Usando arquivo de vídeo existente do teste anterior...')
                with open(video_info_file, 'r', encoding='utf-8') as f:
                    video_info = json.load(f)

                # Verifica se o arquivo de áudio ainda existe
                audio_path = Path(video_info['audio_path'])
                if not audio_path.exists():
                    print('⚠️  Arquivo de áudio não encontrado, baixando novamente...')
                    video_info = generator.download_audio(DEFAULT_TEST_URL)
            else:
                print('🔄 Baixando áudio do vídeo de teste...')
                video_info = generator.download_audio(DEFAULT_TEST_URL)

            print(f'\n📺 Vídeo: {video_info["title"]}')
            print(f'👤 Canal: {video_info["uploader"]}')
            print(f'⏱️  Duração: {generator._format_duration(video_info["duration"])}')

            # Estima custo da transcrição
            audio_path = Path(video_info['audio_path'])
            file_size_mb = audio_path.stat().st_size / (1024 * 1024)
            estimated_duration_minutes = file_size_mb / 1.5
            estimated_cost = estimated_duration_minutes * 0.006  # Custo do Whisper
            cost_brl = estimated_cost * 5.48

            print('\n💰 Custo estimado da transcrição:')
            print(f'   ${estimated_cost:.4f} USD (R$ {cost_brl:.2f} BRL)')

            # Confirma se deve prosseguir
            response = input('\n❓ Deseja prosseguir com a transcrição? (s/N): ').lower()
            if response not in ['s', 'sim', 'y', 'yes']:
                print('❌ Transcrição cancelada pelo usuário.')
                return False

            print('\n🔄 Iniciando transcrição...')
            transcription = generator.transcribe_audio(video_info['audio_path'])

            print('\n✅ Transcrição concluída com sucesso!')
            print('\n📊 Estatísticas da transcrição:')
            print(f'   📝 Caracteres: {len(transcription["text"])}')
            print(f'   📝 Palavras: {len(transcription["text"].split())}')
            print(f'   🎵 Duração: {generator._format_duration(transcription.get("duration", 0))}')
            print(f'   🔤 Palavras com timestamp: {len(transcription.get("words", []))}')

            # Mostra uma amostra do texto
            sample_text = (
                transcription['text'][:200] + '...' if len(transcription['text']) > 200 else transcription['text']
            )
            print('\n📄 Amostra do texto transcrito:')
            print(f'   "{sample_text}"')

            # Salva a transcrição
            transcription_file = generator.save_transcription(transcription, video_info)
            print(f'\n💾 Transcrição salva em: {transcription_file}')

            # Exibe resumo de custos
            generator.display_cost_summary()

            return True

    except Exception as e:
        print(f'\n❌ Erro durante a transcrição: {str(e)}')
        return False


def main():
    """Função principal do teste."""
    # Verifica se a API key está configurada
    if not os.getenv('OPENAI_API_KEY'):
        print('❌ ERRO: Configure a variável de ambiente OPENAI_API_KEY')
        print("Exemplo: export OPENAI_API_KEY='sua-api-key-aqui'")
        return 1

    success = test_transcription()

    if success:
        print('\n' + '=' * 60)
        print('✅ TESTE DA ETAPA 2 CONCLUÍDO COM SUCESSO!')
        print('=' * 60)
        return 0
    else:
        print('\n' + '=' * 60)
        print('❌ TESTE DA ETAPA 2 FALHOU!')
        print('=' * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
