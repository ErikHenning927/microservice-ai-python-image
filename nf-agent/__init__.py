"""
OCR NF Telecontrol - Agente de Extração de Dados de Notas Fiscais
Estrutura modular com Controllers, Services e Utils
"""

from .config import Config
from .models import ExtractedData
from .services import ExtractionService, CacheService, OCRService
from .controllers import ExtractionController

__version__ = "1.0.0"
__author__ = "OCR NF Telecontrol"

__all__ = [
    "Config",
    "ExtractedData",
    "ExtractionService",
    "CacheService",
    "OCRService",
    "ExtractionController",
]
