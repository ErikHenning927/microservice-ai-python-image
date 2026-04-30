import cv2
import pytesseract
import json
import re
import os
import numpy as np
from pdf2image import convert_from_path

# Configuração do caminho do Tesseract se estiver no Windows (no Linux não precisa na maioria das vezes)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Definição dos campos esperados e suas expressões regulares para limpeza/captura
# Você precisará ajustar as expressões regulares conforme o formato real do texto extraído
CAMPOS_REGEX = {
    "Data de emissão NF": r"(\d{2}/\d{2}/\d{4})",
    "Número da NF": r"N[ºo]?\s*[:.-]?\s*(\d+)",
    "Chave de Acesso da Nota": r"(\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4})",
    "Nome do consumidor/destinatario": r"NOME/RAZÃO SOCIAL\s*CNPJ/CPF[^\n]*\n([A-Z0-9\s.-]+?)\s+\d{11,14}",
    "CPF do consumidor/destinatario": r"NOME/RAZÃO SOCIAL\s*CNPJ/CPF[^\n]*\n.*?\s+(\d{11,14})",
    "CEP do consumidor/destinatario": r"(?:CEP\s+DATA\s+DA[^\n]*\n.*?(\d{8})|DATA\s+DA\s+SAÍDA[^\n]*\n[^\d]*(\d{8}))",
    "Endereço do consumidor/destinatario": r"ENDEREÇO\s+BAIRRO\s+CEP[^\n]*\n([^\n]+?)(?:\s+CENTRO|\s+[A-Z\s]{2,}?\s+\d{8})",
    "Bairro do consumidor/destinatario": r"BAIRRO\s+CEP[^\n]*\n\s*([A-Z\s]+?)\s+(?:\d{8}|$)|R\s+[^\n]+\s+(CENTRO|[A-Z\s]+?)\s+\d{8}",
    "Cidade do consumidor/destinatario": r"MUNICÍPIO\s+FONE/FAX[^\n]*\n\s*([A-Z\s]+?)\s+(?:\(|\d|$)",
    "Estado do consumidor/destinatario": r"(?:UF\s+INSCRIÇÃO[^\n]*\n\s*([A-Z]{2})|UF\s*\n\s*([A-Z]{2}))",
    "Telefone fixo do consumidor/destinatario": r"FONE/FAX\s+UF[^\n]*\n\s*((?:\(?\d{2}\)?[\s.-]?\d{4}[\s.-]?\d{4})|(?:\(\d{2}\)\s*\d{4}[\s.-]\d{4}))",
    "Descrição do Produto": r"DADOS DO PRODUTO / SERVIÇO\n\d{5,}\s+(.*?)\s+\d{8}",
    "NCM do Produto": r"DADOS DO PRODUTO / SERVIÇO\n\d{5,}\s+.*?\s+(\d{8})"
}

# Coordenadas dos quadrantes (x, y, largura, altura)
# ATENÇÃO: Você precisa descobrir essas coordenadas na sua imagem original
# Pode usar ferramentas como o Paint ou OpenCV (cv2.selectROI) para pegar as coordendas corretas.
QUADRANTES = {
    "bloco_vermelho_revenda": (50, 50, 800, 200),  # Exemplo: x, y, w, h
    "bloco_azul_destinatario": (50, 260, 800, 150),
    "bloco_produtos": (50, 420, 800, 300)
}

def preprocess_image(image_roi):
    """Aplica filtros para melhorar a precisão do Tesseract"""
    gray = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY)
    # Aumenta contraste, aplica thresholding se necessário
    _, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return threshold

def extract_data_from_document(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    # Se for PDF, converte a primeira página para imagem
    if file_path.lower().endswith('.pdf'):
        pages = convert_from_path(file_path, dpi=300)
        if not pages:
            raise ValueError("O PDF está vazio ou não pôde ser convertido.")
        # Converte PIL Image para array numpy no formato BGR do OpenCV
        img = cv2.cvtColor(np.array(pages[0]), cv2.COLOR_RGB2BGR)
    else:
        img = cv2.imread(file_path)
    
    # Processa a imagem inteira primeiro
    roi_processada = preprocess_image(img)
    texto_completo = pytesseract.image_to_string(roi_processada, lang='por', config='--psm 6')

    print("--- TEXTO EXTRAÍDO BRUTO ---")
    print(texto_completo)
    print("----------------------------\n")

    # Parsing dos dados usando os regex configurados
    dados_finais = {
        "Data de emissão NF": None,
        "Número da NF": None,
        "Chave de Acesso da Nota": None,
        "Nome do consumidor/destinatario": None,
        "Telefone fixo do consumidor/destinatario": None,
        "Telefone celular do consumidor/destinatario": None,
        "Telefone comercial do consumidor/destinatario": None,
        "CPF do consumidor/destinatario": None,
        "CEP do consumidor/destinatario": None,
        "Endereço do consumidor/destinatario": None,
        "Número do consumidor/destinatario": None,
        "Complemento": None,
        "Bairro do consumidor/destinatario": None,
        "Cidade do consumidor/destinatario": None,
        "Estado do consumidor/destinatario": None,
        "Nome da Revenda": None,
        "CNPJ da Revenda": None,
        "Endereço completo da Revenda": None,
        "Descrição do Produto": None,
        "NCM do Produto": None
    }

    for campo, padrao_regex in CAMPOS_REGEX.items():
        match = re.search(padrao_regex, texto_completo, re.IGNORECASE | re.DOTALL)
        if match:
            # Pega o primeiro grupo de captura que não for None
            for p in match.groups():
                if p:
                    dados_finais[campo] = p.strip()
                    break
            if not dados_finais[campo]:
                 dados_finais[campo] = match.group(0).strip()
        
        # Tratamento específico para extrair CNPJ de dentro da chave de acesso de 44 dígitos
        if campo == "CNPJ da Revenda" and dados_finais[campo]:
            somente_numeros = re.sub(r'\D', '', dados_finais[campo])
            if len(somente_numeros) >= 20:
                # O CNPJ do emissor fica entre a posição 6 e 20 da chave (índices 6 a 20)
                dados_finais[campo] = somente_numeros[6:20]

    return json.dumps(dados_finais, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    documento_teste = "Exemplo de Notas/32119.pdf"  # Agora lendo o arquivo PDF
    
    try:
        resultado_json = extract_data_from_document(documento_teste)
        print("=== RESULTADO JSON ===")
        print(resultado_json)
        
        # Salva o resultado
        with open("resultado_extracao.json", "w", encoding="utf-8") as f:
            f.write(resultado_json)
        print("\nArquivo 'resultado_extracao.json' gerado com sucesso!")
            
    except Exception as e:
        print(f"Erro ao processar imagem: {e}")
