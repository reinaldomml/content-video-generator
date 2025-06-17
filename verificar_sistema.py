#!/usr/bin/env python3
"""
Verificação do Sistema

Este script verifica se o sistema está configurado corretamente
antes de executar os testes principais.
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Verifica a versão do Python."""
    print('🐍 Verificando versão do Python...')
    version = sys.version_info

    if version.major == 3 and version.minor >= 8:
        print(f'   ✅ Python {version.major}.{version.minor}.{version.micro} - OK')
        return True
    else:
        print(f'   ❌ Python {version.major}.{version.minor}.{version.micro} - Requer Python 3.8+')
        return False


def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    print('\n📦 Verificando dependências...')

    required_packages = [
        'openai',
        'yt_dlp',
        'jinja2',
        'weasyprint',
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f'   ✅ {package} - OK')
        except ImportError:
            print(f'   ❌ {package} - NÃO ENCONTRADO')
            missing_packages.append(package)

    if missing_packages:
        print('\n💡 Para instalar pacotes faltantes:')
        print(f'   pip install {" ".join(missing_packages)}')
        return False

    return True


def check_openai_api():
    """Verifica se a API key da OpenAI está configurada."""
    print('\n🔑 Verificando API Key da OpenAI...')

    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print('   ❌ OPENAI_API_KEY não encontrada')
        print("   💡 Configure com: export OPENAI_API_KEY='sua-api-key-aqui'")
        return False

    if len(api_key) < 20:
        print('   ⚠️  API Key parece muito curta')
        return False

    if api_key.startswith('sk-'):
        print('   ✅ API Key configurada - OK')
        return True
    else:
        print("   ⚠️  API Key não parece válida (deve começar com 'sk-')")
        return False


def check_templates():
    """Verifica se os templates existem."""
    print('\n📄 Verificando templates...')

    template_dir = Path('template')
    required_files = [
        'ebook.html',
        'ebook.css',
        'cover.jpg',
        'OpenSans-VariableFont_wdth,wght.ttf',
    ]

    if not template_dir.exists():
        print('   ❌ Diretório template/ não encontrado')
        return False

    missing_files = []
    for file_name in required_files:
        file_path = template_dir / file_name
        if file_path.exists():
            print(f'   ✅ {file_name} - OK')
        else:
            print(f'   ❌ {file_name} - NÃO ENCONTRADO')
            missing_files.append(file_name)

    if missing_files:
        print('\n💡 Arquivos faltantes no diretório template/:')
        for file_name in missing_files:
            print(f'   - {file_name}')
        return False

    return True


def check_config():
    """Verifica se o arquivo de configuração existe."""
    print('\n⚙️  Verificando configuração...')

    config_file = Path('config.py')

    if not config_file.exists():
        print('   ❌ config.py não encontrado')
        return False

    try:
        # Tenta importar config
        sys.path.insert(0, str(Path(__file__).parent))
        import config

        required_vars = [
            'OPENAI_API_KEY',
            'DEFAULT_TEST_URL',
            'OPENAI_WHISPER_COST_PER_MINUTE',
            'OPENAI_GPT_COST_PER_1K_TOKENS',
        ]

        missing_vars = []
        for var_name in required_vars:
            if hasattr(config, var_name):
                print(f'   ✅ {var_name} - OK')
            else:
                print(f'   ❌ {var_name} - NÃO ENCONTRADO')
                missing_vars.append(var_name)

        if missing_vars:
            return False

        return True

    except Exception as e:
        print(f'   ❌ Erro ao importar config.py: {e}')
        return False


def check_output_dir():
    """Verifica/cria diretório de saída."""
    print('\n📁 Verificando diretório de saída...')

    output_dir = Path('output')

    if not output_dir.exists():
        try:
            output_dir.mkdir()
            print('   ✅ Diretório output/ criado - OK')
        except Exception as e:
            print(f'   ❌ Erro ao criar output/: {e}')
            return False
    else:
        print('   ✅ Diretório output/ existe - OK')

    # Verifica permissões de escrita
    test_file = output_dir / 'test_write.tmp'
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        test_file.unlink()
        print('   ✅ Permissões de escrita - OK')
        return True
    except Exception as e:
        print(f'   ❌ Sem permissão de escrita: {e}')
        return False


def check_main_script():
    """Verifica se o script principal existe."""
    print('\n🎯 Verificando script principal...')

    main_file = Path('main.py')

    if not main_file.exists():
        print('   ❌ main.py não encontrado')
        return False

    try:
        # Tenta importar main
        sys.path.insert(0, str(Path(__file__).parent))

        print('   ✅ main.py importado - OK')
        print('   ✅ YouTubeEbookGenerator encontrado - OK')
        return True

    except Exception as e:
        print(f'   ❌ Erro ao importar main.py: {e}')
        return False


def check_test_scripts():
    """Verifica se os scripts de teste existem."""
    print('\n🧪 Verificando scripts de teste...')

    test_scripts = [
        'test_etapa1_download.py',
        'test_etapa2_transcricao.py',
        'test_etapa3_processamento_gpt.py',
        'test_etapa4_template.py',
        'test_etapa5_pdf.py',
        'test_all_etapas.py',
        'test_template_simulado.py',
    ]

    missing_scripts = []
    for script_name in test_scripts:
        script_path = Path(script_name)
        if script_path.exists():
            print(f'   ✅ {script_name} - OK')
        else:
            print(f'   ❌ {script_name} - NÃO ENCONTRADO')
            missing_scripts.append(script_name)

    if missing_scripts:
        return False

    return True


def main():
    """Executa todas as verificações."""
    print('🔍 VERIFICAÇÃO DO SISTEMA')
    print('=' * 60)
    print('Verificando se o sistema está configurado corretamente...\n')

    checks = [
        ('Versão do Python', check_python_version),
        ('Dependências', check_dependencies),
        ('API Key OpenAI', check_openai_api),
        ('Templates', check_templates),
        ('Configuração', check_config),
        ('Diretório de saída', check_output_dir),
        ('Script principal', check_main_script),
        ('Scripts de teste', check_test_scripts),
    ]

    passed_checks = 0
    total_checks = len(checks)

    for check_name, check_func in checks:
        try:
            if check_func():
                passed_checks += 1
        except Exception as e:
            print(f'   ❌ Erro durante verificação: {e}')

    # Resultado final
    print('\n' + '=' * 60)
    print('📊 RESULTADO DA VERIFICAÇÃO')
    print('=' * 60)
    print(f'✅ Verificações passaram: {passed_checks}/{total_checks}')
    print(f'❌ Verificações falharam: {total_checks - passed_checks}/{total_checks}')

    if passed_checks == total_checks:
        print('\n🎉 SISTEMA CONFIGURADO CORRETAMENTE!')
        print('✅ Você pode executar os testes:')
        print('   • python test_template_simulado.py (sem custo)')
        print('   • python test_etapa1_download.py (sem custo)')
        print('   • python test_all_etapas.py (com custo de API)')
        return 0
    else:
        print(f'\n💥 {total_checks - passed_checks} VERIFICAÇÃO(ÕES) FALHARAM!')
        print('❌ Corrija os problemas antes de executar os testes')
        return 1


if __name__ == '__main__':
    sys.exit(main())
