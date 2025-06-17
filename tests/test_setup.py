#!/usr/bin/env python3
"""
Script de teste para verificar se todas as dependências estão instaladas corretamente.
"""

import subprocess
import sys
from pathlib import Path


def test_imports():
    """Testa se todas as bibliotecas necessárias podem ser importadas."""
    print('🔍 Testando importações...')

    try:
        import yt_dlp

        print('✅ yt-dlp: OK')
    except ImportError as e:
        print(f'❌ yt-dlp: {e}')
        return False

    try:
        import openai

        print('✅ openai: OK')
    except ImportError as e:
        print(f'❌ openai: {e}')
        return False

    try:
        import weasyprint

        print('✅ weasyprint: OK')
    except ImportError as e:
        print(f'❌ weasyprint: {e}')
        return False

    try:
        from dotenv import load_dotenv

        print('✅ python-dotenv: OK')
    except ImportError as e:
        print(f'❌ python-dotenv: {e}')
        return False

    return True


def test_ffmpeg():
    """Testa se o FFmpeg está disponível no sistema."""
    print('\n🔍 Testando FFmpeg...')

    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f'✅ FFmpeg: {version_line}')
            return True
        else:
            print('❌ FFmpeg: Comando falhou')
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print('❌ FFmpeg: Não encontrado no PATH')
        print('   Instale com: sudo apt install ffmpeg (Ubuntu/Debian)')
        print('   Ou: brew install ffmpeg (macOS)')
        return False


def test_openai_key():
    """Testa se a chave da API OpenAI está configurada."""
    print('\n🔍 Testando configuração da API OpenAI...')

    import os

    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print('❌ OPENAI_API_KEY: Não configurada')
        print("   Configure com: export OPENAI_API_KEY='sua-chave-aqui'")
        print('   Ou crie um arquivo .env com: OPENAI_API_KEY=sua-chave-aqui')
        return False
    elif api_key.startswith('sk-') and len(api_key) > 20:
        print('✅ OPENAI_API_KEY: Configurada (formato válido)')
        return True
    else:
        print('❌ OPENAI_API_KEY: Formato inválido')
        print("   A chave deve começar com 'sk-' e ter mais de 20 caracteres")
        return False


def test_directories():
    """Testa se os diretórios necessários podem ser criados."""
    print('\n🔍 Testando criação de diretórios...')

    try:
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)

        if output_dir.exists() and output_dir.is_dir():
            print("✅ Diretório 'output': OK")
            return True
        else:
            print("❌ Diretório 'output': Falha na criação")
            return False
    except Exception as e:
        print(f"❌ Diretório 'output': {e}")
        return False


def main():
    """Executa todos os testes."""
    print('🧪 TESTE DE CONFIGURAÇÃO DO AMBIENTE')
    print('=' * 50)

    tests = [
        ('Importações', test_imports),
        ('FFmpeg', test_ffmpeg),
        ('API OpenAI', test_openai_key),
        ('Diretórios', test_directories),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f'❌ {test_name}: Erro inesperado - {e}')
            results.append((test_name, False))

    # Resumo
    print('\n' + '=' * 50)
    print('📊 RESUMO DOS TESTES')
    print('=' * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = '✅ PASSOU' if result else '❌ FALHOU'
        print(f'{test_name:15}: {status}')
        if result:
            passed += 1

    print('=' * 50)
    print(f'Resultado: {passed}/{total} testes passaram')

    if passed == total:
        print('\n🎉 Todos os testes passaram! O ambiente está pronto.')
        print('Execute: python main.py')
        return 0
    else:
        print('\n⚠️  Alguns testes falharam. Corrija os problemas antes de continuar.')
        return 1


if __name__ == '__main__':
    sys.exit(main())
