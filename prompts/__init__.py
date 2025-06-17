"""
Módulo de prompts para o Content Video Generator.

Este módulo contém todos os prompts utilizados pelo sistema de geração de ebooks.
"""

from .system_prompt_ebook import SYSTEM_PROMPT_EBOOK
from .user_prompt_ebook import get_user_prompt_ebook

__all__ = ['SYSTEM_PROMPT_EBOOK', 'get_user_prompt_ebook']
