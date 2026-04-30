import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class CacheService:
    """Serviço responsável por gerenciamento de cache de extrações"""
    
    def __init__(self, cache_file: str = "nf_cache.json", ttl_hours: int = 24):
        self.cache_file = cache_file
        self.ttl_hours = ttl_hours
        self.file_cache: Dict[str, Any] = {}
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Carrega cache do disco ao iniciar"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.file_cache = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar cache: {e}")
                self.file_cache = {}
    
    def _save_to_disk(self):
        """Salva cache no disco"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    @staticmethod
    def get_file_hash(contents: bytes) -> str:
        """Gera hash SHA256 do arquivo"""
        return hashlib.sha256(contents).hexdigest()
    
    def _is_cache_valid(self, file_hash: str) -> bool:
        """Verifica se o cache ainda é válido (não expirou)"""
        if file_hash not in self.file_cache:
            return False
        
        cached_time = datetime.fromisoformat(self.file_cache[file_hash].get('timestamp'))
        expiration = cached_time + timedelta(hours=self.ttl_hours)
        
        if datetime.now() > expiration:
            del self.file_cache[file_hash]
            self._save_to_disk()
            return False
        
        return True
    
    def get(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Retorna resultado do cache se válido"""
        if self._is_cache_valid(file_hash):
            return self.file_cache[file_hash].get('data')
        return None
    
    def set(self, file_hash: str, data: Dict[str, Any]):
        """Salva resultado no cache"""
        self.file_cache[file_hash] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self._save_to_disk()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "total_cached": len(self.file_cache),
            "cache_file": self.cache_file,
            "ttl_hours": self.ttl_hours,
            "cache_size_mb": os.path.getsize(self.cache_file) / (1024 * 1024) if os.path.exists(self.cache_file) else 0
        }
    
    def clear(self):
        """Limpa o cache - escreve arquivo vazio em vez de remover"""
        self.file_cache = {}
        self._save_to_disk()
