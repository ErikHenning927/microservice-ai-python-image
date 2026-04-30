import re
from typing import Optional


def clean_cnpj(cnpj_str: Optional[str]) -> Optional[str]:
    """Limpa e valida CNPJ, removendo caracteres especiais e zeros à esquerda indevidos."""
    if not cnpj_str:
        return None
    
    # Remove espaços, pontos, barras, hífens
    cleaned = re.sub(r'[\s\.\-/]', '', cnpj_str)
    
    # Remove caracteres não numéricos
    cleaned = re.sub(r'[^\d]', '', cleaned)
    
    # Se tiver 15 dígitos, tenta remover zeros do início
    if len(cleaned) == 15:
        cleaned = cleaned.lstrip('0')  # Remove todos os zeros do início
    
    # Se tiver 14 dígitos começando com 0 (erro comum de OCR)
    if len(cleaned) == 14 and cleaned[0] == '0':
        cleaned = cleaned[1:]
        # Agora tem 13 dígitos, reconstrói adicionando na posição correta
        # ou simplesmente ignora esse e deixa para corrigir pela chave
        if len(cleaned) != 14:
            return None
    
    # CNPJ deve ter exatamente 14 dígitos
    if len(cleaned) != 14 or not cleaned.isdigit():
        return None
    
    return cleaned
