# Microservice Agent - OCR NF Telecontrol

Este microserviço é responsável pela extração de dados de Notas Fiscais (NF) utilizando OCR (Tesseract) e a API da OpenAI para estruturação dos dados extraídos. O projeto segue uma arquitetura em camadas para facilitar a manutenção, testabilidade e escalabilidade.

## Arquitetura em Camadas (Layered Architecture)

O projeto é estruturado da seguinte forma:

```text
nf-agent/
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

### Fluxo de Requisição

```text
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

## Pré-requisitos

### Sistema Operacional
- Linux (recomendado) ou macOS
- Python 3.9+
- Tesseract OCR instalado

### Instalação do Tesseract
**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Baixe do: [Wiki Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto (ou modifique o `.env.example` existente):
```env
OPENAI_API_KEY=sua_chave_aqui
DEBUG=false
```

## Instalação do Projeto

1. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

## Como Executar

### Iniciar o Servidor
Você pode executar o projeto usando o Docker (via `docker-compose up`) ou diretamente via Python:

```bash
cd nf-agent
python agent_extractor.py
```

Ou com reload automático (modo desenvolvimento):
```bash
uvicorn agent_extractor:app --reload --host 0.0.0.0 --port 9001
```

O servidor estará disponível em: `http://localhost:9001`

### Testar Endpoints

#### 1. Health Check
```bash
curl http://localhost:9001/health
```

#### 2. Extrair Dados de NF
```bash
curl -X POST \
  -F "file=@documento.pdf" \
  http://localhost:9001/extract-agent
```

#### 3. Estatísticas do Cache
```bash
curl http://localhost:9001/cache-stats
```

#### 4. Limpar Cache
```bash
curl -X DELETE http://localhost:9001/cache-clear
```

## Performance - Benchmarks

| Operação | Tempo | Notas |
|----------|-------|-------|
| OCR (1 página) | 1-2s | 6 workers paralelos, DPI=100 |
| API OpenAI | 2-3s | gpt-4-mini, parsing estruturado |
| Cache hit | <10ms | JSON em disco |
| **Total (novo)** | **~5s** | Paralelo (OCR + API) |
| **Total (cache)** | **<20ms** | Cache + validação |

## Desenvolvimento

Para adicionar novas funcionalidades:

1. **Novo Endpoint:** Adicione no controller em `controllers/extraction_controller.py` e registre a rota no `agent_extractor.py`.
2. **Novo Modelo:** Adicione o campo Pydantic em `models/extracted_data.py`.
3. **Novo Serviço:** Crie em `services/` e injete no controller.
4. **Nova Utilitária:** Adicione em `utils/` garantindo que seja independente.

### Próximas Features Planejadas
- [ ] Adicionar logging estruturado
- [ ] Implementar rate limiting
- [ ] Adicionar métricas (Prometheus)
- [ ] Testes unitários para cada service
- [ ] Suporte a lote (batch processing)
- [ ] Banco de dados para histórico
