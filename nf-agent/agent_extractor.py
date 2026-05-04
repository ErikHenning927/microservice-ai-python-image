"""
FastAPI Application - OCR NF Telecontrol

Main entry point para a API de extração de dados de Notas Fiscais.
Estrutura em camadas: Controllers → Services → Utils → Models
"""

from fastapi import FastAPI, File, UploadFile

from .config import Config
from .controllers import ExtractionController
from .models import ExtractedData
from .services import ExtractionService, CacheService


# =========================
# INICIALIZAÇÃO
# =========================

app = FastAPI(title=Config.APP_TITLE, version=Config.APP_VERSION)

# Instancia services
extraction_service = ExtractionService(api_key=Config.OPENAI_API_KEY)
cache_service = CacheService()

# Instancia controller
controller = ExtractionController(extraction_service=extraction_service, cache_service=cache_service)


# =========================
# ROTAS
# =========================

@app.post("/extract-agent", response_model=ExtractedData)
async def extract_pdf(file: UploadFile = File(...)) -> ExtractedData:
    """
    Extrai dados de uma Nota Fiscal (PDF ou imagem).
    
    - **file**: Arquivo PDF ou imagem da NF
    
    Retorna dados estruturados da NF com tokens e custo da requisição.
    """
    return await controller.extract_pdf(file)


@app.get("/cache-stats")
async def cache_stats() -> dict:
    """Retorna estatísticas do cache de extrações"""
    return controller.get_cache_stats()


@app.delete("/cache-clear")
async def cache_clear() -> dict:
    """Limpa o cache de extrações"""
    return controller.clear_cache()


@app.get("/health")
async def health() -> dict:
    """Health check da API"""
    return {"status": "ok", "version": Config.APP_VERSION}
