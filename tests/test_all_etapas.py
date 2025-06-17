#!/usr/bin/env python3
"""
Teste Completo: Todas as etapas

Este script executa todos os testes das etapas em sequência,
permitindo testar o fluxo completo do sistema.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_test(script_name, description):
    """Executa um teste específico."""
    print(f'\n{"=" * 80}')
    print(f'🚀 EXECUTANDO: {description}')
    print(f'📄 Script: {script_name}')
    print(f'{"=" * 80}')

    try:
        # Executa o script de teste
        result = subprocess.run(
            [sys.executable, script_name], capture_output=False, text=True, cwd=Path(__file__).parent
        )

        if result.returncode == 0:
            print(f'\n✅ {description} - SUCESSO!')
            return True
        else:
            print(f'\n❌ {description} - FALHOU!')
            return False

    except Exception as e:
        print(f'\n❌ Erro ao executar {script_name}: {str(e)}')
        return False


def main():
    """Executa todos os testes em sequência."""
    print('🎯 TESTE COMPLETO DO SISTEMA DE GERAÇÃO DE EBOOK')
    print('=' * 80)
    print('Este script executará todas as etapas do processo:')
    print('1. Download do áudio')
    print('2. Transcrição com OpenAI Whisper')
    print('3. Processamento com GPT-4o-mini')
    print('4. Geração do template HTML')
    print('5. Geração do PDF final')
    print('=' * 80)

    # Verifica se a API key está configurada
    if not os.getenv('OPENAI_API_KEY'):
        print('❌ ERRO: Configure a variável de ambiente OPENAI_API_KEY')
        print("Exemplo: export OPENAI_API_KEY='sua-api-key-aqui'")
        return 1

    # Define os testes a serem executados
    tests = [
        ('test_etapa1_download.py', 'Etapa 1: Download do áudio'),
        ('test_etapa2_transcricao.py', 'Etapa 2: Transcrição com OpenAI Whisper'),
        ('test_etapa3_processamento_gpt.py', 'Etapa 3: Processamento com GPT-4o-mini'),
        ('test_etapa4_template.py', 'Etapa 4: Geração do template HTML'),
        ('test_etapa5_pdf.py', 'Etapa 5: Geração do PDF final'),
    ]

    # Verifica se todos os scripts existem
    missing_scripts = []
    for script_name, _ in tests:
        if not Path(script_name).exists():
            missing_scripts.append(script_name)

    if missing_scripts:
        print('❌ Scripts de teste não encontrados:')
        for script in missing_scripts:
            print(f'   - {script}')
        return 1

    # Pergunta se deve continuar
    print('\n⚠️  ATENÇÃO: Este teste irá usar a API da OpenAI e incorrer em custos!')
    print('💰 Custos estimados:')
    print('   - Whisper (transcrição): ~$0.006 por minuto de áudio')
    print('   - GPT-4o-mini: ~$0.00015 por 1000 tokens')
    print('   - Total estimado para vídeo de 10 min: ~$0.10 USD (~R$ 0.55)')

    response = input('\n❓ Deseja continuar com todos os testes? (s/N): ').lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print('❌ Testes cancelados pelo usuário.')
        return 0

    # Executa os testes
    success_count = 0
    total_tests = len(tests)

    for i, (script_name, description) in enumerate(tests, 1):
        print(f'\n🔄 PROGRESSO: {i}/{total_tests}')

        success = run_test(script_name, description)
        if success:
            success_count += 1
        else:
            print('\n💥 Teste falhou! Interrompendo execução.')
            break

    # Resultado final
    print(f'\n{"=" * 80}')
    print('📊 RESULTADO FINAL')
    print(f'{"=" * 80}')
    print(f'✅ Testes executados com sucesso: {success_count}/{total_tests}')
    print(f'❌ Testes que falharam: {total_tests - success_count}/{total_tests}')

    if success_count == total_tests:
        print('\n🎉 TODOS OS TESTES PASSARAM!')
        print('✅ Sistema funcionando corretamente!')
        print("📁 Verifique a pasta 'output/' para os arquivos gerados")
        return 0
    else:
        print(f'\n💥 {total_tests - success_count} TESTE(S) FALHARAM!')
        print('❌ Sistema apresenta problemas!')
        return 1


if __name__ == '__main__':
    sys.exit(main())
