# Guia de Execução - OCR NF Telecontrol

## Pré-requisitos

### Sistema Operacional
- Linux (recomendado) ou macOS
- Python 3.9+
- Tesseract OCR instalado

### Instalação de Dependências do Sistema

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

#### Windows
Baixe do: https://github.com/UB-Mannheim/tesseract/wiki

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:
```env
OPENAI_API_KEY=sua_chave_aqui
DEBUG=false
```

## Instalação do Projeto

1. **Instalar dependências Python**
```bash
pip install -r requirements.txt
```

2. **Estrutura de Diretórios** (deve estar assim)
```
ocr-nf-telecontrol/
├── agent/
│   ├── models/
│   ├── services/
│   ├── controllers/
│   ├── utils/
│   ├── config.py
│   ├── agent_extractor.py
│   └── __init__.py
├── .env
└── requirements.txt
```

## Como Executar

### Iniciar o Servidor

```bash
cd agent
python agent_extractor.py
```

Ou com reload automático:
```bash
uvicorn agent_extractor:app --reload --host 0.0.0.0 --port 9001
```

Servidor estará disponível em: `http://localhost:9001`

### Testar Endpoints

#### 1. Health Check
```bash
curl http://localhost:9001/health
```

Resposta esperada:
```json
{"status": "ok", "version": "1.0.0"}
```

#### 2. Extrair Dados de NF
```bash
curl -X POST \
  -F "file=@documento.pdf" \
  http://localhost:9001/extract-agent
```

Resposta esperada (JSON):
```json
{
  "numero_nf": "12345",
  "chave_acesso": "35241108291650000162551010001288391234567890",
  "cnpj_revenda": "12345678000195",
  "nome_consumidor": "João Silva",
  "cpf_consumidor": "12345678901",
  "estado_uf_consumidor": "SP",
  "total_tokens": 450,
  "custo_requisicao": 0.00234,
  "from_cache": false,
  ...
}
```

#### 3. Estatísticas do Cache
```bash
curl http://localhost:9001/cache-stats
```

Resposta esperada:
```json
{
  "total_entries": 5,
  "cache_hits": 12,
  "cache_size_mb": 0.25,
  "oldest_entry_age_hours": 6
}
```

#### 4. Limpar Cache
```bash
curl -X DELETE http://localhost:9001/cache-clear
```

Resposta esperada:
```json
{"message": "Cache cleared successfully"}
```

## Entendendo os Arquivos

### Arquivo `result_extraction.json`
- Arquivo histórico com resultados anteriores
- Pode ser deletado - é apenas para referência

### Arquivo `nf_cache.json` (gerado automaticamente)
- Cache local com resultados já processados
- Persiste 24 horas
- Usado para evitar re-processamento

### Arquivo `Campos para Leitura NF.txt`
- Template com lista de campos a extrair
- Referência para validação

## Troubleshooting

### Erro: "Tesseract is not installed"
```bash
# Linux
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### Erro: "OpenAI API key not found"
- Verifique arquivo `.env` existe
- Verifique que `OPENAI_API_KEY` está definida
- Exemplo correto: `OPENAI_API_KEY=sk-...`

### Erro: "Module not found"
```bash
# Reinstale dependências
pip install --upgrade -r requirements.txt

# Ou use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### Lentidão na Extração
- Primeira execução: ~5-7 segundos (inclui OCR + API)
- Cache hit: <10ms
- Se > 10s, verifique:
  - CPU disponível (6 workers OCR)
  - Conexão com OpenAI
  - Tamanho do PDF (páginas múltiplas)

### CNPJ Incorreto
O projeto extrai automaticamente do campo correto:
1. Da chave de acesso (primeira opção, mais confiável)
2. Do campo CNPJ do revenda (segunda opção)
3. Auto-corrige formato se necessário

Se ainda houver problemas, verifique o PDF original.

## Desenvolvimento

### Adicionar Novo Campo
1. Editar [models/extracted_data.py](models/extracted_data.py) - adicionar campo Pydantic
2. Editar `extraction_service.py` - adicionar ao prompt
3. Testar com `curl`

### Adicionar Novo Serviço
1. Criar em `services/novo_service.py`
2. Importar em `services/__init__.py`
3. Injetar em `controllers/extraction_controller.py`
4. Usar no controller

### Debugging
```python
# Em agent_extractor.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Em qualquer service
import logging
logger = logging.getLogger(__name__)
logger.debug("Mensagem de debug")
```

## Performance - Benchmarks

| Operação | Tempo | Notas |
|----------|-------|-------|
| OCR (1 página) | 1-2s | 6 workers paralelos, DPI=100 |
| API OpenAI | 2-3s | gpt-4-mini, parsing estruturado |
| Cache hit | <10ms | JSON em disco |
| **Total (novo)** | **~5s** | Paralelo (OCR + API) |
| **Total (cache)** | **<20ms** | Cache + validação |

## Próximas Features Planejadas

- [ ] Suporte a lote (batch processing)
- [ ] Webhook para notificações
- [ ] Histórico completo em DB
- [ ] Dashboard com estatísticas
- [ ] Export para CSV/Excel
- [ ] Integração com WhatsApp
