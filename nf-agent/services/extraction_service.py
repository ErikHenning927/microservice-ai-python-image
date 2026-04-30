from openai import AsyncOpenAI

from ..models import ExtractedData
from ..utils import clean_cnpj, extract_cnpj_from_chave


class ExtractionService:
    """Serviço responsável pela extração de dados via OpenAI"""
    
    PRICE_INPUT = 0.75 / 1_000_000  # $0.75 por 1M input tokens
    PRICE_OUTPUT = 4.50 / 1_000_000  # $4.50 por 1M output tokens
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def extract_fields(self, text: str, filename: str) -> ExtractedData:
        """Extrai campos da NF usando OpenAI"""
        
        prompt = f"""Você é um especialista em leitura de Notas Fiscais. Extraia com precisão os campos da NF abaixo. Retorne null se não encontrar.

REGRAS CRÍTICAS:
1. CNPJ da revenda: sempre 14 dígitos, vem no topo, é o emitente
2. CPF/CNPJ consumidor: referente ao destinatário
3. Se chave de acesso (44 dígitos) existir, extraia CNPJ dela (posição 6-20)
4. UF: apenas 2 letras (SP, RJ, MG, GO, etc)
5. Endereço do consumidor: procure por DESTINATÁRIO/REMETENTE
6. Corrija OCR: remova zeros iniciais em CNPJ com 15 dígitos

Texto OCR:
{text}"""
        
        response = await self.client.beta.chat.completions.parse(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": "Extraia informações de NFe com precisão em JSON. Seja conciso e rápido."},
                {"role": "user", "content": prompt}
            ],
            response_format=ExtractedData,
            temperature=0.0
        )
        
        extracted_data = response.choices[0].message.parsed
        extracted_data.arquivo_origem = filename
        
        # Captura tokens e calcula custo
        if response.usage:
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            extracted_data.total_tokens = total_tokens
            
            custo = (prompt_tokens * self.PRICE_INPUT) + (completion_tokens * self.PRICE_OUTPUT)
            extracted_data.custo_requisicao = round(custo, 6)
        
        # Pós-processamento: limpar dados
        self._cleanup_data(extracted_data)
        
        return extracted_data
    
    @staticmethod
    def _cleanup_data(extracted_data: ExtractedData):
        """Pós-processamento de limpeza de dados"""
        
        # Tentar extrair CNPJ correto da chave de acesso
        if extracted_data.chave_acesso:
            cnpj_from_chave = extract_cnpj_from_chave(extracted_data.chave_acesso)
            if cnpj_from_chave:
                extracted_data.cnpj_revenda = cnpj_from_chave
        
        # Limpar CNPJ da revenda como fallback
        if extracted_data.cnpj_revenda:
            cleaned_cnpj = clean_cnpj(extracted_data.cnpj_revenda)
            if cleaned_cnpj:
                extracted_data.cnpj_revenda = cleaned_cnpj
        
        # Limpar CPF do consumidor
        if extracted_data.cpf_consumidor:
            cleaned_cpf = clean_cnpj(extracted_data.cpf_consumidor)
            if cleaned_cpf:
                extracted_data.cpf_consumidor = cleaned_cpf
