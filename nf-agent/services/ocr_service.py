import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, UnidentifiedImageError

from ..utils import preprocess_ocr_text


class OCRService:
    """Serviço responsável por extração de texto via OCR"""
    
    DPI = 100  # Configurável
    MAX_WORKERS = 6
    
    @staticmethod
    def extract_text_from_pdf(contents: bytes) -> str:
        """Extrai texto de PDF com OCR paralelo"""
        pages = convert_from_bytes(contents, dpi=OCRService.DPI)
        page_texts: List[str] = []
        
        def _ocr_page(page):
            # Comprime imagem antes do OCR para economizar recursos
            page.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            return pytesseract.image_to_string(page, lang="por", config='--psm 3')
        
        with ThreadPoolExecutor(max_workers=OCRService.MAX_WORKERS) as executor:
            futures = [executor.submit(_ocr_page, page) for page in pages]
            for future in as_completed(futures):
                page_texts.append(future.result())
        
        return "\n".join(page_texts)
    
    @staticmethod
    def extract_text_from_image(contents: bytes) -> str:
        """Extrai texto de imagem com OCR"""
        try:
            image = Image.open(io.BytesIO(contents))
        except UnidentifiedImageError as exc:
            raise ValueError("Arquivo de imagem inválido") from exc
        
        return pytesseract.image_to_string(image, lang="por")
    
    @staticmethod
    def extract_raw_text(contents: bytes, content_type: str, filename: str) -> str:
        """Detecta tipo de arquivo e extrai texto"""
        is_pdf = (
            (content_type or "").lower() == "application/pdf"
            or filename.lower().endswith(".pdf")
            or contents[:4] == b"%PDF"
        )
        
        if is_pdf:
            text = OCRService.extract_text_from_pdf(contents)
        elif (content_type or "").startswith("image/"):
            text = OCRService.extract_text_from_image(contents)
        else:
            raise ValueError("Arquivo deve ser PDF ou imagem")
        
        # Aplica pré-processamento
        text = preprocess_ocr_text(text)
        return text
