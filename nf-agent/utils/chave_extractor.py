import re
from typing import Optional


def extract_cnpj_from_chave(chave_acesso: Optional[str]) -> Optional[str]:
    """Extrai o CNPJ embutido na chave de acesso da NFe."""
    if not chave_acesso:
        return None
    
    # Remove caracteres especiais
    chave = re.sub(r'[\s\.\-/]', '', chave_acesso)
    chave = re.sub(r'[^\d]', '', chave)
    
    # Chave deve ter 44 dígitos
    if len(chave) != 44:
        return None
    
    # O CNPJ fica na posição 6-19 (14 dígitos) na chave de acesso
    # Formato da chave NFe (44 dígitos): AAYYYYCCCCCCNNNNNNNNNNNNMMDDDD...
    # Posição 0-1: UF (2 dígitos)
    # Posição 2-5: Ano (4 dígitos)
    # Posição 6-19: CNPJ (14 dígitos) <- aqui!
    # Posição 20-21: Mês (2 dígitos)
    # Posição 22-23: Dia (2 dígitos)
    cnpj_from_chave = chave[6:20]  # Extrai 14 dígitos começando na posição 6
    
    if cnpj_from_chave.isdigit() and len(cnpj_from_chave) == 14:
        return cnpj_from_chave
    
    return None
