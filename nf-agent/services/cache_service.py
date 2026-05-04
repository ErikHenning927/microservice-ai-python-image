import json
import redis
import hashlib
from typing import Optional, Dict, Any
from ..config import Config


class CacheService:
    """Serviço responsável por gerenciamento de cache de extrações usando Redis"""
    
    def __init__(self, ttl_hours: Optional[int] = None):
        self.ttl_seconds = (ttl_hours or Config.CACHE_TTL_HOURS) * 3600
        self.redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
            db=Config.REDIS_DB,
            decode_responses=True
        )
    
    @staticmethod
    def get_file_hash(contents: bytes) -> str:
        """Gera hash SHA256 do arquivo"""
        return hashlib.sha256(contents).hexdigest()
    
    def get(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Retorna resultado do cache se válido"""
        try:
            cached_data = self.redis_client.get(file_hash)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Erro ao buscar no Redis: {e}")
        return None
    
    def set(self, file_hash: str, data: Dict[str, Any]):
        """Salva resultado no cache com TTL"""
        try:
            self.redis_client.setex(
                file_hash,
                self.ttl_seconds,
                json.dumps(data, ensure_ascii=False)
            )
        except Exception as e:
            print(f"Erro ao salvar no Redis: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache Redis"""
        try:
            info = self.redis_client.info()
            return {
                "total_cached_keys": self.redis_client.dbsize(),
                "used_memory_human": info.get('used_memory_human'),
                "ttl_hours": self.ttl_seconds / 3600,
                "redis_version": info.get('redis_version')
            }
        except Exception as e:
            return {"error": str(e)}
    
    def clear(self):
        """Limpa o cache do banco atual"""
        try:
            self.redis_client.flushdb()
        except Exception as e:
            print(f"Erro ao limpar Redis: {e}")
