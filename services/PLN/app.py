from fastapi import FastAPI
from pydantic import BaseModel
from generator import gerar_relatorio_texto
from pipeline import PipelinePLN
from relatorio import RelatorioEstoque

class Consulta(BaseModel):
    texto: str

pipeline_pln = PipelinePLN()

# ==============================
# FastAPI
# ==============================
app = FastAPI(title="Assistente de Estoque", description="Chat para relatórios e consultas de estoque via PLN")

# Rota principal: Chat unificado (interpreta intenção + busca + resposta)
@app.post("/chat")
def conversar(consulta: Consulta):
    resposta = pipeline_pln.processar_consulta(consulta.texto)
    return {"resposta": resposta}

# Endpoints fixos opcionais (para testes rápidos, sem chat)
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

# Rode com: uvicorn app:app --reload --port 5000