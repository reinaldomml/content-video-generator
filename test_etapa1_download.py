#!/usr/bin/env python3
"""
Teste da Etapa 1: Download do áudio

Este script testa apenas o download do áudio de um vídeo do YouTube,
sem fazer transcrição ou processamento posterior.
"""

import json
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar main
sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_TEST_URL
from main import YouTubeEbookGenerator


def test_download_audio():
    """Testa o download do áudio de um vídeo do YouTube."""
    print('=' * 60)
    print('TESTE ETAPA 1: DOWNLOAD DO ÁUDIO')
    print('=' * 60)

    # URL de teste
    test_url = DEFAULT_TEST_URL
    print(f'URL de teste: {test_url}')

    try:
        # Cria o gerador
        with YouTubeEbookGenerator() as generator:
            print('\n🔄 Iniciando download do áudio...')

            # Testa o download
            video_info = generator.download_audio(test_url)

            print('\n✅ Download concluído com sucesso!')
            print('\n📋 Informações do vídeo:')
            print(f'  📺 Título: {video_info["title"]}')
            print(f'  👤 Canal: {video_info["uploader"]}')
            print(f'  ⏱️  Duração: {generator._format_duration(video_info["duration"])}')
            print(f'  📅 Data de upload: {video_info["upload_date"]}')
            print(f'  🎵 Arquivo de áudio: {video_info["audio_path"]}')

            # Verifica se o arquivo existe
            audio_path = Path(video_info['audio_path'])
            if audio_path.exists():
                file_size_mb = audio_path.stat().st_size / (1024 * 1024)
                print(f'  📊 Tamanho do arquivo: {file_size_mb:.2f} MB')
            else:
                print('  ❌ Arquivo de áudio não encontrado!')
                return False

            # Salva as informações do vídeo para uso em outros testes
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)

            video_info_file = output_dir / 'video_info_test.json'
            with open(video_info_file, 'w', encoding='utf-8') as f:
                json.dump(video_info, f, ensure_ascii=False, indent=2)

            print(f'\n💾 Informações salvas em: {video_info_file}')
            print('\n🎯 Este arquivo pode ser usado nos próximos testes!')

            return True

    except Exception as e:
        print(f'\n❌ Erro durante o download: {str(e)}')
        return False


def main():
    """Função principal do teste."""
    success = test_download_audio()

    if success:
        print('\n' + '=' * 60)
        print('✅ TESTE DA ETAPA 1 CONCLUÍDO COM SUCESSO!')
        print('=' * 60)
        return 0
    else:
        print('\n' + '=' * 60)
        print('❌ TESTE DA ETAPA 1 FALHOU!')
        print('=' * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
