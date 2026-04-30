import asyncio
from fastapi import File, HTTPException, UploadFile

from ..models import ExtractedData
from ..services import OCRService, CacheService, ExtractionService


class ExtractionController:
    """Controller responsável pelas rotas de extração"""
    
    def __init__(self, extraction_service: ExtractionService, cache_service: CacheService):
        self.extraction_service = extraction_service
        self.cache_service = cache_service
        self.ocr_service = OCRService()
    
    async def extract_pdf(self, file: UploadFile = File(...)) -> ExtractedData:
        """Extrai dados de PDF/imagem com cache e otimizações"""
        try:
            contents = await file.read()
            file_hash = CacheService.get_file_hash(contents)
            
            # Verifica se já foi processado
            cached_result = self.cache_service.get(file_hash)
            if cached_result:
                # Reconstrói o ExtractedData do cache
                data = ExtractedData(**cached_result)
                data.from_cache = True
                return data
            
            # Executa OCR em thread pool (libera o event loop)
            loop = asyncio.get_event_loop()
            raw_text = await loop.run_in_executor(
                None, 
                self.ocr_service.extract_raw_text, 
                contents, 
                file.content_type, 
                file.filename or "arquivo.pdf"
            )
            
            # Faz a chamada async à OpenAI
            result = await self.extraction_service.extract_fields(raw_text, file.filename or "arquivo.pdf")
            result.from_cache = False
            
            # Salva no cache
            self.cache_service.set(file_hash, result.dict())
            
            return result
            
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    def get_cache_stats(self) -> dict:
        """Retorna estatísticas do cache"""
        return self.cache_service.get_stats()
    
    def clear_cache(self) -> dict:
        """Limpa o cache"""
        self.cache_service.clear()
        return {"message": "Cache limpo com sucesso"}
