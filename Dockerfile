# Usar imagem oficial Python
FROM python:3.11-slim

# Metadados
LABEL maintainer="OCR NF Telecontrol"
LABEL description="FastAPI application for NF data extraction using OCR and OpenAI"

# Definir diretório de trabalho
WORKDIR /app

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependências do sistema (incluindo Tesseract OCR, Poppler para PDF e dados da língua portuguesa)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    libtesseract-dev \
    poppler-utils \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 9001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9001/health', timeout=5)"

# Comando para iniciar a aplicação
CMD ["python", "run.py"]
