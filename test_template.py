#!/usr/bin/env python3
"""
Script de teste para validar os templates WeasyPrint para ebooks.
Testa renderização HTML, CSS e geração de PDF.
"""

import sys
from datetime import datetime
from pathlib import Path


def test_template_files():
    """Testa se todos os arquivos do template existem."""
    template_dir = Path('template')
    required_files = [
        'ebook.html',
        'ebook.css',
        'cover.jpg',
        'OpenSans-VariableFont_wdth,wght.ttf',
        'config.py',
        'README.md',
    ]

    print('🔍 Verificando arquivos do template...')

    for file in required_files:
        filepath = template_dir / file
        if filepath.exists():
            size = filepath.stat().st_size
            print(f'  ✅ {file} ({size:,} bytes)')
        else:
            print(f'  ❌ {file} - AUSENTE')
            return False

    return True


def test_jinja2_rendering():
    """Testa renderização do template Jinja2."""
    try:
        from jinja2 import Environment, FileSystemLoader

        print('\n🔧 Testando renderização Jinja2...')

        # Configurar Jinja2
        env = Environment(loader=FileSystemLoader('template'))
        template = env.get_template('ebook.html')

        # Dados de teste para um vídeo único
        test_data = {
            'ebook_title': 'Ebook de Teste - Vídeo Único',
            'generation_date': datetime.now().strftime('%d/%m/%Y às %H:%M'),
            'videos': [
                {
                    'video_info': {
                        'title': 'Como Aprender Python em 2024',
                        'uploader': 'Canal Educativo',
                        'formatted_duration': '15m 30s',
                        'url': 'https://youtube.com/watch?v=exemplo123',
                    },
                    'paragraphs': [
                        'Este é o primeiro parágrafo da transcrição do vídeo. Aqui demonstramos como o conteúdo do vídeo seria formatado no ebook.',
                        'Este é o segundo parágrafo, mostrando como múltiplos parágrafos são organizados no template.',
                        'O terceiro parágrafo ilustra a continuidade do conteúdo transcrito, mantendo a formatação adequada para leitura.',
                        'Parágrafos adicionais são processados sequencialmente, criando um fluxo natural de leitura no ebook final.',
                    ],
                }
            ],
        }

        # Renderizar template
        html_content = template.render(**test_data)

        # Verificar se elementos essenciais estão presentes
        checks = [
            ('title', 'Ebook de Teste - Vídeo Único' in html_content),
            ('video info', 'Como Aprender Python em 2024' in html_content),
            ('paragraphs', 'primeiro parágrafo da transcrição' in html_content),
            ('main-content class', 'class="main-content"' in html_content),
            ('single video layout', 'class="transcription-content"' in html_content),
        ]

        for check_name, result in checks:
            if result:
                print(f'  ✅ {check_name} - OK')
            else:
                print(f'  ❌ {check_name} - FALHOU')
                return False, None

        print('  ✅ Template renderizado com sucesso!')
        return True, html_content

    except ImportError:
        print('  ❌ Jinja2 não está instalado. Execute: pip install jinja2')
        return False, None
    except Exception as e:
        print(f'  ❌ Erro na renderização: {e}')
        return False, None


def test_weasyprint_generation(html_content):
    """Testa geração de PDF com WeasyPrint."""
    try:
        from weasyprint import CSS, HTML

        print('\n🖨️  Testando geração de PDF...')

        # Configurar caminhos
        template_dir = Path('template').absolute()
        base_url = template_dir.as_uri() + '/'

        # Criar documento HTML
        html_doc = HTML(string=html_content, base_url=base_url)

        # Carregar CSS
        css_path = template_dir / 'ebook.css'
        css_doc = CSS(filename=str(css_path))

        # Gerar PDF de teste
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)

        pdf_path = output_dir / 'teste_ebook_video_unico.pdf'
        html_doc.write_pdf(str(pdf_path), stylesheets=[css_doc])

        # Verificar arquivo gerado
        if pdf_path.exists():
            size = pdf_path.stat().st_size
            print(f'  ✅ PDF gerado: {pdf_path} ({size:,} bytes)')

            # Verificar tamanho mínimo (deve ter conteúdo)
            if size > 10000:  # 10KB mínimo
                print('  ✅ Tamanho do PDF adequado')
                return True
            else:
                print('  ⚠️  PDF muito pequeno, pode ter problemas')
                return False
        else:
            print('  ❌ PDF não foi criado')
            return False

    except ImportError:
        print('  ❌ WeasyPrint não está instalado. Execute: pip install weasyprint')
        return False
    except Exception as e:
        print(f'  ❌ Erro na geração do PDF: {e}')
        return False


def test_font_loading():
    """Testa se a fonte OpenSans está acessível."""
    print('\n🔤 Testando fonte OpenSans...')

    font_path = Path('template/OpenSans-VariableFont_wdth,wght.ttf')

    if font_path.exists():
        size = font_path.stat().st_size
        print(f'  ✅ Fonte encontrada ({size:,} bytes)')

        # Verificar se é um arquivo TTF válido (verificação básica)
        try:
            with open(font_path, 'rb') as f:
                header = f.read(4)
                if header in [b'\x00\x01\x00\x00', b'OTTO', b'ttcf']:
                    print('  ✅ Arquivo TTF válido')
                    return True
                else:
                    print('  ⚠️  Arquivo pode não ser um TTF válido')
                    return False
        except Exception as e:
            print(f'  ❌ Erro ao verificar fonte: {e}')
            return False
    else:
        print('  ❌ Fonte OpenSans não encontrada')
        return False


def test_css_validation():
    """Testa se o CSS não tem erros básicos."""
    print('\n🎨 Validando CSS...')

    css_path = Path('template/ebook.css')

    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # Verificações básicas
        checks = [
            ('@font-face rule', '@font-face' in css_content),
            ('OpenSans font', 'OpenSans' in css_content),
            ('main-content class', '.main-content' in css_content),
            ('transcription-content class', '.transcription-content' in css_content),
            ('single video support', '.video-info' in css_content),
            ('drop caps removed', '::first-letter' not in css_content),
        ]

        for check_name, result in checks:
            if result:
                print(f'  ✅ {check_name} - OK')
            else:
                print(f'  ❌ {check_name} - FALHOU')

        return all(result for _, result in checks)

    except Exception as e:
        print(f'  ❌ Erro ao validar CSS: {e}')
        return False


def main():
    """Executa todos os testes."""
    print('🧪 TESTE DOS TEMPLATES WEASYPRINT - VÍDEO ÚNICO')
    print('=' * 50)

    # Verificar diretório de trabalho
    if not Path('template').exists():
        print("❌ Diretório 'template' não encontrado!")
        print('Execute este script a partir do diretório do projeto.')
        sys.exit(1)

    tests = [
        ('Arquivos do template', test_template_files),
        ('Fonte OpenSans', test_font_loading),
        ('Validação CSS', test_css_validation),
        ('Renderização Jinja2', test_jinja2_rendering),
    ]

    results = {}
    html_content = None

    for test_name, test_func in tests:
        print(f'\n{"=" * 20} {test_name.upper()} {"=" * 20}')

        if test_name == 'Renderização Jinja2':
            success, html_content = test_func()
            results[test_name] = success
        else:
            results[test_name] = test_func()

    # Teste de geração PDF (apenas se Jinja2 funcionou)
    if results.get('Renderização Jinja2') and html_content:
        print(f'\n{"=" * 20} GERAÇÃO PDF {"=" * 20}')
        results['Geração PDF'] = test_weasyprint_generation(html_content)

    # Relatório final
    print(f'\n{"=" * 20} RELATÓRIO FINAL {"=" * 20}')

    passed = 0
    total = len(results)

    for test_name, success in results.items():
        status = '✅ PASSOU' if success else '❌ FALHOU'
        print(f'{test_name:<20} {status}')
        if success:
            passed += 1

    print(f'\nResultado: {passed}/{total} testes passaram')

    if passed == total:
        print('\n🎉 TODOS OS TESTES PASSARAM!')
        print('✅ Template está funcionando corretamente para vídeos únicos')
        print('✅ Fonte OpenSans configurada')
        print('✅ Drop caps removido')
        print('✅ Layout otimizado para ebook de vídeo único')
    else:
        print(f'\n⚠️  {total - passed} teste(s) falharam')
        print('Verifique os erros acima e corrija os problemas.')
        sys.exit(1)


if __name__ == '__main__':
    main()
