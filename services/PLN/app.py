import json
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timedelta
from generator import gerar_relatorio_texto
from pipeline import PipelinePLN
from relatorio import RelatorioEstoque
from fastapi.middleware.cors import CORSMiddleware 
from salvarRelatorio import salvar_relatorio 
import os

# Models
class Consulta(BaseModel):
    usuario_id: int
    texto: str

class RelatorioRequest(BaseModel):
    usuario_id: int
    data_inicio: str
    data_fim: str
    topicos: List[str]
    incluir_todos_skus: bool
    skus: Optional[List[str]] = None

# ==============================
# Instâncias (suas - André)
# ==============================
pipeline_pln = PipelinePLN()

# ==============================
# FastAPI (alinhado: CORS da main + suas descrições - Felipe + André)
# ==============================
app = FastAPI(title="Assistente de Estoque", description="Chat para relatórios e consultas de estoque via PLN")

app.add_middleware(  # Da main (Felipe)
    CORSMiddleware,
    allow_origins=["*"],
)

# Rota principal: Chat unificado (sua - André)
@app.post("/chat")
def conversar(consulta: Consulta):
    resposta = pipeline_pln.processar_consulta(consulta.texto)
    return {"resposta": resposta}

# Endpoints fixos opcionais (suas, sem chat - André)
@app.get("/relatorio")
def gerar_relatorio_fixo():
    rel = RelatorioEstoque()
    return rel.geral()

@app.get("/relatorio-skus")
def gerar_relatorio_skus_fixo():
    rel = RelatorioEstoque()
    dados = rel.por_sku()
    texto = gerar_relatorio_texto(dados)
    return {"texto": texto}

# ==============================
# Rotas da main (adaptadas para usar sua classe e generator - Felipe + André)
# ==============================
@app.post("/relatorio")
def gerar_relatorio(request: RelatorioRequest):
    rel = RelatorioEstoque()  # Usa sua classe (André)
    dados = rel.geral()

    caminho = salvar_relatorio(  # Da main (Felipe)
        dados,
        tipo="geral",
        como_json=True,
        chat_id=1,
        usuario_id=request.usuario_id, 
        titulo="Relatório Geral"
    )

    return {"dados": [dados], "arquivo": caminho}

@app.post("/relatorio-skus")
def gerar_relatorio_skus(request: RelatorioRequest):
    rel = RelatorioEstoque()  # Usa sua classe (André)

    # Ajustar SKUs para o formato correto (da main - Felipe)
    skus_formatados = None
    if not request.incluir_todos_skus and request.skus:
        skus_formatados = [sku.replace("SKU", "SKU_") if "SKU_" not in sku else sku for sku in request.skus]

    dados = rel.por_sku(  # Usa sua por_sku com filtros (André + adição Felipe)
        data_inicio=request.data_inicio,
        data_fim=request.data_fim,
        skus=skus_formatados
    )

    # Filtrar tópicos (da main, mas usando normalize da main - Felipe)
    def normalize(text):  # Helper da main (Felipe)
        return ''.join(c.lower() for c in text if c.isalnum() or c.isspace())

    if request.topicos:
        topicos_normalizados = [normalize(t) for t in request.topicos]
        for sku in dados:
            dados[sku] = {k: v for k, v in dados[sku].items() if any(t in normalize(k) for t in topicos_normalizados)}

    texto = gerar_relatorio_texto(  # Usa seu generator alinhado (André + Felipe)
        dados, 
        topicos=request.topicos, 
        data_inicio=request.data_inicio, 
        data_fim=request.data_fim
    )

    caminho = salvar_relatorio(  # Da main (Felipe)
        texto,
        tipo="sku",
        como_json=True,
        chat_id=1,
        usuario_id=request.usuario_id,
        titulo="Relatório por SKU"
    )

    return {"dados": dados, "arquivo": caminho, "conteudo": texto}

@app.get("/relatorio/conteudo")  # Da main (Felipe)
def obter_conteudo(caminho: str):
    if not os.path.exists(caminho):
        return {"conteudo": "Arquivo não encontrado"}
    
    with open(caminho, "r", encoding="utf-8") as f:
        try:
            conteudo = json.load(f)
        except json.JSONDecodeError:
            conteudo = f.read()
    
    return {"conteudo": conteudo}

# Comando para rodar: uvicorn app:app --reload --port 5000