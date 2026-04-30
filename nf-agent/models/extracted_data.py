from typing import Optional
from pydantic import BaseModel, Field


class ExtractedData(BaseModel):
    """Modelo de dados extraídos da Nota Fiscal"""
    
    data_emissao: Optional[str] = Field(None, description="Data de emissão da nota fiscal, se presente.")
    numero_nf: str = Field("", description="Número da Nota Fiscal.")
    chave_acesso: Optional[str] = Field(None, description="Chave de acesso da NFe de 44 dígitos.")
    nome_consumidor: Optional[str] = Field(None, description="Nome ou Razão Social do consumidor/destinatário.")
    telefone_fixo_consumidor: Optional[str] = Field(None, description="Telefone fixo do consumidor.")
    telefone_celular_consumidor: Optional[str] = Field(None, description="Telefone celular do consumidor.")
    telefone_comercial_consumidor: Optional[str] = Field(None, description="Telefone comercial do consumidor.")
    cpf_consumidor: Optional[str] = Field(None, description="CPF ou CNPJ do consumidor/destinatário.")
    cep_consumidor: Optional[str] = Field(None, description="CEP do consumidor.")
    endereco_consumidor: Optional[str] = Field(None, description="Apenas o Logradouro/Rua/Avenida do consumidor. Ex: RUA ANTONIO MONTEIRO BASTOS. Não inclua número, bairro ou cidade aqui.")
    numero_consumidor: Optional[str] = Field(None, description="Número do endereço do consumidor. Ex: 13, 1234, SN, S/N")
    complemento: Optional[str] = Field(None, description="Complemento do endereço do consumidor. Ex: QD 20 LT 20, APTO 101, SALA 2")
    bairro_consumidor: Optional[str] = Field(None, description="Bairro do consumidor. Ex: RIO DA AREIA, CENTRO")
    cidade_consumidor: Optional[str] = Field(None, description="Cidade/Município do consumidor. Ex: SAQUAREMA, PADRE BERNARDO")
    estado_uf_consumidor: Optional[str] = Field(None, description="Sigla de 2 letras do estado (UF) brasileiro do consumidor. Ex: RJ, SP, GO, SC, PR. Ignore lixos de OCR.")
    nome_revenda: Optional[str] = Field(None, description="Nome ou Razão Social da revenda/empresa que emitiu a nota (emitente).")
    cnpj_revenda: Optional[str] = Field(None, description="CNPJ da revenda/empresa que emitiu a nota (emitente).")
    endereco_completo_revenda: Optional[str] = Field(None, description="Endereço completo da revenda/empresa emissora.")
    descricao_produto: str = Field("", description="Lista ou descrição dos produtos adquiridos.")
    ncm_produto: Optional[str] = Field(None, description="Código NCM do produto/produtos.")
    arquivo_origem: str = Field("")
    total_tokens: Optional[int] = Field(None, description="Total de tokens utilizados na requisição ao modelo de IA.")
    custo_requisicao: Optional[float] = Field(None, description="Custo da requisição em USD.")
    from_cache: bool = Field(False, description="Indica se o resultado foi obtido do cache")
