# Estrutura do Projeto - OCR NF Telecontrol

## Arquitetura em Camadas (Layered Architecture)

```
agent/
├── agent_extractor.py          # Main entry point - Define rotas e inicializa app
├── config.py                   # Configurações centralizadas
├── __init__.py                 # Package initialization
│
├── models/                     # Camada de Dados
│   ├── __init__.py
│   └── extracted_data.py       # Modelo Pydantic de dados extraídos
│
├── controllers/                # Camada de Controle (HTTP Layer)
│   ├── __init__.py
│   └── extraction_controller.py # Handler das requisições HTTP
│
├── services/                   # Camada de Negócio (Business Logic)
│   ├── __init__.py
│   ├── extraction_service.py   # Orquestra chamadas à OpenAI
│   ├── cache_service.py        # Gerencia cache de extrações
│   └── ocr_service.py          # Processa OCR (Tesseract)
│
└── utils/                      # Utilitários (Helper Functions)
    ├── __init__.py
    ├── cnpj_cleaner.py         # Valida e limpa CNPJs
    ├── chave_extractor.py      # Extrai CNPJ da chave de acesso
    └── ocr_preprocessor.py     # Pré-processa texto OCR
```

## Fluxo de Requisição

```
HTTP Request (PDF/Imagem)
        ↓
[agent_extractor.py] - Route Handler
        ↓
[ExtractionController] - Orquestra lógica
        ├─→ [CacheService] - Verifica cache
        ├─→ [OCRService] - Extrai texto
        ├─→ [ExtractionService] - Chama OpenAI
        └─→ [Cache] - Salva resultado
        ↓
HTTP Response (JSON com dados)
```

## Responsabilidades por Camada

### Models (`models/`)
- Define estruturas de dados com Pydantic
- Validação automática de tipos
- Documentação via docstrings

### Controllers (`controllers/`)
- Recebe requisições HTTP
- Orquestra chamadas entre services
- Trata exceções e retorna respostas

### Services (`services/`)
- **ExtractionService**: Lógica de extração (OpenAI)
- **OCRService**: Processamento de OCR com threading
- **CacheService**: Persistência e gerenciamento de cache

### Utils (`utils/`)
- Funções reutilizáveis e independentes
- Sem dependências de outras camadas
- Fáceis de testar

### Config (`config.py`)
- Centraliza todas as configurações
- Valores padrão sensatos
- Carrega de `.env`

## Benefícios da Arquitetura

✅ **Separação de Responsabilidades** - Cada classe faz uma coisa bem
✅ **Testabilidade** - Services podem ser mockados e testados isoladamente
✅ **Reutilização** - Utils podem ser usados em diferentes contextos
✅ **Manutenibilidade** - Fácil encontrar e modificar funcionalidades
✅ **Escalabilidade** - Fácil adicionar novos controllers/services
✅ **Injeção de Dependências** - Constructor injection torna fácil mockar

## Como Adicionar Novas Features

### 1. Novo Endpoint
```python
# Em controllers/extraction_controller.py
def new_feature(self, ...):
    # Lógica aqui
    pass

# Em agent_extractor.py
@app.post("/new-endpoint")
async def new_endpoint(...):
    return controller.new_feature(...)
```

### 2. Nova Utility
```python
# Em utils/novo_modulo.py
def minha_funcao(parametro):
    return resultado

# Em utils/__init__.py - adicionar import
from .novo_modulo import minha_funcao

# Usar em services/services.py
from ..utils import minha_funcao
```

### 3. Novo Service
```python
# Em services/novo_service.py
class NovoService:
    def fazer_algo(self):
        pass

# Em services/__init__.py - adicionar import
from .novo_service import NovoService

# Injetar em controller
self.novo_service = NovoService()
```

## Rotas Disponíveis

```
POST   /extract-agent   - Extrai dados de NF
GET    /cache-stats     - Estatísticas do cache
DELETE /cache-clear     - Limpa cache
GET    /health          - Health check
```

## Performance

- **OCR Paralelo**: 6 workers processam múltiplas páginas
- **Async/Await**: Não bloqueia durante I/O
- **Cache**: Resultados persistem 24h no disco
- **DPI Otimizado**: 100 DPI para velocidade

## Próximas Melhorias Possíveis

- [ ] Adicionar logging estruturado
- [ ] Implementar rate limiting
- [ ] Adicionar métricas (Prometheus)
- [ ] Testes unitários para cada service
- [ ] GraphQL endpoint
- [ ] Message Queue para processamento assíncrono
- [ ] Banco de dados para histórico
