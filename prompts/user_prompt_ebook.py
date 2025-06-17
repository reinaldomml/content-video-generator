def get_user_prompt_ebook(video_info, transcription_text, format_duration_func):
    """
    Gera o prompt do usuário para o modelo GPT, formatando com as informações do vídeo e transcrição.
    """
    return f"""INFORMAÇÕES DO VÍDEO:
Título: {video_info['title']}
Canal: {video_info['uploader']}
Duração: {format_duration_func(video_info['duration'])}

CONTEXTO PARA ANÁLISE:
- Este é um vídeo educacional/informativo que contém conhecimento valioso
- O objetivo é criar um ebook COMPLETO e DETALHADO que maximize o valor educacional
- Expanda e enriqueça o conteúdo além do que foi dito literalmente no vídeo
- Foque em criar um material de referência robusto e profissional

TRANSCRIÇÃO COMPLETA:
{transcription_text}

INSTRUÇÕES ESPECÍFICAS PARA ESTA TRANSCRIÇÃO:
1. Analise TODO o conteúdo da transcrição linha por linha
2. Identifique TODOS os conceitos, dados, estratégias e insights mencionados
3. Expanda cada conceito com explicações detalhadas e contexto
4. Crie capítulos substanciais que desenvolvam completamente cada tema
5. Use **negrito** extensivamente para destacar informações importantes
6. Garanta que cada capítulo tenha conteúdo suficiente para ser educacionalmente valioso
7. Inclua subseções quando houver subtemas distintos
8. Desenvolva pontos importantes específicos e detalhados para cada capítulo

RESULTADO ESPERADO: Um ebook educacional completo, detalhado e profissional que transforme esta transcrição em um material de referência valioso.

IMPORTANTE: Responda APENAS com o JSON válido, sem texto adicional antes ou depois. Use aspas duplas para todas as strings e certifique-se de que o JSON esteja bem formatado."""
