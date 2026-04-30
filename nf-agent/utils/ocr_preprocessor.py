import re


def preprocess_ocr_text(text: str) -> str:
    """Pré-processa texto OCR para melhorar a extração."""
    # Padroniza múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    # Melhora reconhecimento de números confusos (O -> 0, l -> 1, etc)
    # Procura por padrões de CNPJ malformados e tenta corrigir
    text = re.sub(r'\bCNPJ[:\s]*O+(\d+)', r'CNPJ: 0\1', text)  # O em vez de 0
    
    return text
