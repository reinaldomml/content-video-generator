#!/usr/bin/env python3
"""
Teste do Template com Dados Simulados

Este script testa o template HTML/CSS usando dados simulados,
sem precisar usar as APIs da OpenAI.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Adiciona o diretório raiz ao path para importar main
sys.path.insert(0, str(Path(__file__).parent))

from main import YouTubeEbookGenerator


def create_mock_data():
    """Cria dados simulados para teste do template."""

    # Dados simulados do vídeo
    video_info = {
        'title': 'Como Criar Aplicações Web Modernas com Python',
        'uploader': 'Canal Tech Educativo',
        'duration': 1800,  # 30 minutos
        'upload_date': '20240101',
        'description': 'Aprenda a criar aplicações web modernas usando Python, Flask e outras tecnologias.',
        'url': 'https://www.youtube.com/watch?v=exemplo123',
    }

    # Conteúdo estruturado simulado
    ebook_content = {
        'title': 'Desenvolvimento Web Moderno com Python',
        'subtitle': 'Um guia completo para criar aplicações web robustas',
        'author': 'Canal Tech Educativo',
        'description': 'Este ebook apresenta conceitos fundamentais e práticas avançadas para desenvolvimento web usando Python, cobrindo desde conceitos básicos até implementações complexas.',
        'chapters': [
            {
                'title': 'Introdução ao Desenvolvimento Web',
                'content': 'O desenvolvimento web moderno exige conhecimento de múltiplas tecnologias e ferramentas. Neste capítulo, vamos explorar os fundamentos que todo desenvolvedor deve conhecer.\n\nPython se tornou uma das linguagens mais populares para desenvolvimento web devido à sua simplicidade e poder. Com frameworks como Flask e Django, é possível criar aplicações robustas e escaláveis.',
                'subsections': [
                    {
                        'title': 'História e Evolução',
                        'content': 'A web evoluiu drasticamente desde seus primórdios. O que começou como páginas estáticas se transformou em aplicações complexas e interativas.',
                    },
                    {
                        'title': 'Tecnologias Fundamentais',
                        'content': 'HTML, CSS e JavaScript formam a base do desenvolvimento web front-end, enquanto Python oferece excelentes opções para o back-end.',
                    },
                ],
            },
            {
                'title': 'Flask: Framework Minimalista',
                'content': 'Flask é um micro-framework web para Python que oferece flexibilidade e simplicidade. Sua arquitetura modular permite que desenvolvedores escolham exatamente quais componentes usar.\n\nCom Flask, você pode começar com uma aplicação simples e expandir conforme necessário, adicionando funcionalidades como autenticação, banco de dados e APIs REST.',
                'subsections': [
                    {
                        'title': 'Instalação e Configuração',
                        'content': 'A instalação do Flask é simples através do pip. Configurar um ambiente virtual é uma prática recomendada para manter dependências organizadas.',
                    },
                    {
                        'title': 'Rotas e Views',
                        'content': 'O sistema de rotas do Flask permite mapear URLs para funções Python, criando endpoints para sua aplicação web.',
                    },
                    {
                        'title': 'Templates com Jinja2',
                        'content': 'Jinja2 é o sistema de templates padrão do Flask, permitindo criar páginas HTML dinâmicas com lógica Python incorporada.',
                    },
                ],
            },
            {
                'title': 'Banco de Dados e ORM',
                'content': 'O gerenciamento de dados é crucial em aplicações web. SQLAlchemy oferece um ORM poderoso que simplifica operações de banco de dados.\n\nCom SQLAlchemy, você pode trabalhar com objetos Python em vez de SQL direto, mantendo a flexibilidade quando necessário.',
                'subsections': [
                    {
                        'title': 'Configuração do SQLAlchemy',
                        'content': 'Configurar SQLAlchemy com Flask é direto usando Flask-SQLAlchemy, que oferece integração perfeita.',
                    },
                    {
                        'title': 'Modelos e Relacionamentos',
                        'content': 'Definir modelos em SQLAlchemy permite representar tabelas de banco de dados como classes Python.',
                    },
                ],
            },
            {
                'title': 'APIs REST e Autenticação',
                'content': 'Criar APIs REST é essencial para aplicações modernas. Flask oferece ferramentas excelentes para construir APIs robustas e seguras.\n\nA autenticação e autorização são aspectos críticos que devem ser implementados corretamente desde o início do projeto.',
                'subsections': [
                    {
                        'title': 'Construindo APIs com Flask-RESTful',
                        'content': 'Flask-RESTful simplifica a criação de APIs REST, oferecendo classes e decoradores úteis.',
                    },
                    {
                        'title': 'JWT e Autenticação',
                        'content': 'JSON Web Tokens (JWT) oferecem uma forma segura e escalável de gerenciar autenticação em APIs.',
                    },
                ],
            },
        ],
        'conclusion': 'O desenvolvimento web com Python oferece um ecossistema rico e maduro para criar aplicações modernas. Flask, com sua simplicidade e flexibilidade, é uma excelente escolha para projetos de qualquer tamanho.\n\nContinue praticando e explorando as diversas bibliotecas disponíveis. A comunidade Python é acolhedora e sempre disposta a ajudar desenvolvedores em sua jornada de aprendizado.',
        'key_points': [
            'Python é uma linguagem excelente para desenvolvimento web devido à sua simplicidade e poder',
            'Flask oferece flexibilidade e permite começar pequeno e escalar conforme necessário',
            'SQLAlchemy simplifica operações de banco de dados através de seu ORM intuitivo',
            'APIs REST são fundamentais para aplicações modernas e Flask facilita sua implementação',
            'Autenticação e segurança devem ser consideradas desde o início do projeto',
            'A comunidade Python oferece excelente suporte e documentação para desenvolvedores',
        ],
    }

    return video_info, ebook_content


def test_template_with_mock_data():
    """Testa o template usando dados simulados."""
    print('=' * 60)
    print('TESTE DO TEMPLATE COM DADOS SIMULADOS')
    print('=' * 60)

    try:
        # Cria dados simulados
        print('🔄 Criando dados simulados...')
        video_info, ebook_content = create_mock_data()

        print(f'📺 Vídeo simulado: {video_info["title"]}')
        print(f'👤 Canal: {video_info["uploader"]}')
        print(f'📚 Capítulos: {len(ebook_content["chapters"])}')
        print(f'🔑 Pontos principais: {len(ebook_content["key_points"])}')

        with YouTubeEbookGenerator() as generator:
            print('\n🔄 Gerando HTML com dados simulados...')

            # Gera HTML
            html_content = generator.generate_html_content(ebook_content, video_info)

            print('✅ HTML gerado com sucesso!')
            print(f'📊 Tamanho: {len(html_content):,} caracteres')

            # Salva HTML
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)

            html_file = output_dir / 'ebook_simulado.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f'💾 HTML salvo em: {html_file}')

            print('\n🔄 Carregando CSS...')
            css_content = generator.generate_css()
            print(f'✅ CSS carregado: {len(css_content):,} caracteres')

            print('\n🔄 Gerando PDF simulado...')
            pdf_path = generator.generate_pdf(html_content, css_content, 'ebook_simulado.pdf')

            print('✅ PDF gerado com sucesso!')

            # Estatísticas do PDF
            pdf_file = Path(pdf_path)
            if pdf_file.exists():
                file_size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print('\n📊 Estatísticas do PDF:')
                print(f'   📁 Arquivo: {pdf_path}')
                print(f'   📊 Tamanho: {file_size_mb:.2f} MB')

                # Verifica cabeçalho PDF
                with open(pdf_path, 'rb') as f:
                    header = f.read(8)
                if header.startswith(b'%PDF'):
                    print('   ✅ PDF válido gerado')
                else:
                    print('   ❌ PDF inválido')
                    return False

            # Salva dados simulados para referência
            mock_data = {
                'video_info': video_info,
                'ebook_content': ebook_content,
                'generated_at': datetime.now().isoformat(),
            }

            mock_file = output_dir / 'dados_simulados.json'
            with open(mock_file, 'w', encoding='utf-8') as f:
                json.dump(mock_data, f, ensure_ascii=False, indent=2)

            print(f'\n💾 Dados simulados salvos em: {mock_file}')

            # Verificações do template
            checks = [
                ('Título principal', '<h1>' in html_content),
                ('Autor', ebook_content['author'] in html_content),
                ('Capítulos', 'chapter' in html_content),
                ('Conclusão', 'conclusion' in html_content),
                ('Pontos principais', 'key-points' in html_content),
                ('CSS linkado', 'ebook.css' in html_content),
                ('Informações do vídeo', 'video-info' in html_content),
            ]

            print('\n✅ Verificações do template:')
            all_passed = True
            for check_name, check_result in checks:
                status = '✅' if check_result else '❌'
                print(f'   {status} {check_name}')
                if not check_result:
                    all_passed = False

            return all_passed

    except Exception as e:
        print(f'\n❌ Erro durante o teste: {str(e)}')
        import traceback

        traceback.print_exc()
        return False


def main():
    """Função principal do teste."""
    success = test_template_with_mock_data()

    if success:
        print('\n' + '=' * 60)
        print('✅ TESTE DO TEMPLATE CONCLUÍDO COM SUCESSO!')
        print('🎉 Template funcionando corretamente!')
        print("📁 Arquivos gerados na pasta 'output/'")
        print('=' * 60)
        return 0
    else:
        print('\n' + '=' * 60)
        print('❌ TESTE DO TEMPLATE FALHOU!')
        print('=' * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
