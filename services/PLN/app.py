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
from assertividade import RelatorioAssertividade
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
    dados = rel.geral()

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

@app.post("/relatorio-skus-assertividade")
def gerar_assertividade_skus(request: RelatorioRequest):
    """
    Gera relatório de assertividade dos SKUs
    Calcula métricas de confiabilidade e qualidade dos dados
    Salva o relatório como arquivo e retorna resumo + arquivo
    """
    try:
        print(f"Iniciando assertividade com: {request}")
        rel = RelatorioEstoque()
        
        # Ajustar SKUs para o formato correto
        skus_formatados = None
        if not request.incluir_todos_skus and request.skus:
            skus_formatados = [sku.replace("SKU", "SKU_") if "SKU_" not in sku else sku for sku in request.skus]
        
        # Gerar dados dos SKUs
        print(f"Gerando dados por SKU...")
        dados = rel.por_sku(
            data_inicio=request.data_inicio,
            data_fim=request.data_fim,
            skus=skus_formatados
        )
        print(f"Dados gerados: {len(dados)} SKUs")
        
        # Calcular assertividade
        print(f"Calculando assertividade...")
        assertividade = RelatorioAssertividade(dados)
        relatorio_assertividade = assertividade.gerar_relatorio()
        
        # Salvar relatório como arquivo
        print(f"Salvando relatório em arquivo...")
        caminho = salvar_relatorio(
            relatorio_assertividade,
            tipo="assertividade",
            como_json=True,
            chat_id=1,
            usuario_id=request.usuario_id,
            titulo="Relatório de Assertividade dos SKUs"
        )
        
        print(f"Relatório gerado e salvo com sucesso")
        return {
            "resumo": relatorio_assertividade["resumo"],
            "melhores_skus": relatorio_assertividade["melhores_skus"],
            "piores_skus": relatorio_assertividade["piores_skus"],
            "arquivo": caminho,
            "status": "sucesso"
        }
    except Exception as e:
        print(f"Erro ao gerar assertividade: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"erro": str(e), "status": "erro"}

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
