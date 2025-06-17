#!/usr/bin/env python3
"""
Teste de Debug para JSON da OpenAI
Testa especificamente o parsing do JSON retornado pela OpenAI
"""

import json
import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))


def test_json_parsing():
    """Testa o parsing do JSON com diferentes estratégias."""
    print('=' * 60)
    print('TESTE DE DEBUG: PARSING JSON DA OPENAI')
    print('=' * 60)

    # Verifica se existe arquivo de debug
    debug_file = Path('output/debug_openai_response.txt')
    if debug_file.exists():
        print(f'📁 Arquivo de debug encontrado: {debug_file}')

        with open(debug_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print('📄 Conteúdo do arquivo de debug:')
        print('-' * 40)
        print(content[:500] + '...' if len(content) > 500 else content)
        print('-' * 40)

        # Extrai apenas a resposta da OpenAI
        if 'Resposta original da OpenAI:' in content:
            openai_response = content.split('Resposta original da OpenAI:')[1].split('\n\nErro de parse:')[0].strip()

            print('\n🔧 Testando estratégias de correção...')

            # Função de limpeza (copiada do main.py)
            def clean_json_content(json_str: str) -> str:
                """Limpa e corrige problemas comuns em JSON gerado por IA."""
                import re

                print(f'📝 JSON original (primeiros 200 chars): {json_str[:200]}...')

                # Remove markdown code blocks se existirem
                json_str = re.sub(r'```json\s*', '', json_str)
                json_str = re.sub(r'```\s*$', '', json_str)
                print('✓ Removidos code blocks markdown')

                # Remove texto antes e depois do JSON
                json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    print('✓ Extraído apenas o JSON')

                # Corrige aspas simples para duplas (problema comum)
                original_len = len(json_str)
                json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
                if len(json_str) != original_len:
                    print('✓ Corrigidas aspas simples para duplas')

                # Corrige trailing commas
                original_len = len(json_str)
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                if len(json_str) != original_len:
                    print('✓ Removidas trailing commas')

                # Corrige quebras de linha dentro de strings
                original_len = len(json_str)
                json_str = re.sub(r'"\s*\n\s*([^"]*)\s*\n\s*"', r'"\1"', json_str)
                if len(json_str) != original_len:
                    print('✓ Corrigidas quebras de linha em strings')

                print(f'📝 JSON limpo (primeiros 200 chars): {json_str[:200]}...')
                return json_str

            # Testa estratégias
            strategies = [
                ('Parse direto', lambda x: json.loads(x)),
                ('Com limpeza', lambda x: json.loads(clean_json_content(x))),
                (
                    'Com limpeza de caracteres',
                    lambda x: json.loads(
                        clean_json_content(''.join(ch for ch in x if ord(ch) >= 32 or ch in '\n\r\t'))
                    ),
                ),
            ]

            for strategy_name, strategy_func in strategies:
                try:
                    print(f'\n🧪 Testando: {strategy_name}')
                    result = strategy_func(openai_response)
                    print(f'✅ {strategy_name} - SUCESSO!')
                    print('📊 Estrutura encontrada:')
                    print(f'   - Título: {result.get("title", "N/A")}')
                    print(f'   - Capítulos: {len(result.get("chapters", []))}')
                    print(f'   - Pontos-chave: {len(result.get("key_points", []))}')

                    # Salva o JSON corrigido
                    fixed_file = Path('output/debug_json_fixed.json')
                    with open(fixed_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print(f'💾 JSON corrigido salvo em: {fixed_file}')

                    return True

                except json.JSONDecodeError as e:
                    print(f'❌ {strategy_name} - FALHOU: {e}')
                    # Mostra onde está o erro
                    lines = openai_response.split('\n')
                    if hasattr(e, 'lineno') and e.lineno <= len(lines):
                        print(f'   Linha {e.lineno}: {lines[e.lineno - 1] if e.lineno > 0 else "N/A"}')
                        if hasattr(e, 'colno'):
                            print(
                                f'   Coluna {e.colno}: {lines[e.lineno - 1][max(0, e.colno - 10) : e.colno + 10] if e.lineno > 0 else "N/A"}'
                            )
                except Exception as e:
                    print(f'❌ {strategy_name} - ERRO: {e}')

            print('\n❌ Todas as estratégias falharam!')
            return False

    else:
        print('❌ Arquivo de debug não encontrado!')
        print('Execute primeiro: python test_etapa3_processamento_gpt.py')
        return False


def main():
    """Função principal do teste."""
    success = test_json_parsing()

    if success:
        print('\n' + '=' * 60)
        print('✅ TESTE DE DEBUG CONCLUÍDO COM SUCESSO!')
        print('=' * 60)
        return 0
    else:
        print('\n' + '=' * 60)
        print('❌ TESTE DE DEBUG FALHOU!')
        print('=' * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
