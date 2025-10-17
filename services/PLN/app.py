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
app = FastAPI()

@app.get("/relatorio")
def gerar_relatorio():
    rel = RelatorioEstoque()
    return rel.geral()

@app.get("/relatorio-skus")
def gerar_relatorio_skus():
    rel = RelatorioEstoque()
    dados = rel.por_sku()
    texto = gerar_relatorio_texto(dados)
    return texto


@app.post("/interpretar")
def interpretar(consulta: Consulta):
    resultado = pipeline_pln.processar_consulta(consulta.texto)
    return {"resposta": resultado}

@app.post("/chat")
def conversar(consulta: Consulta):
    resposta = pipeline_pln.processar_consulta(consulta.texto)
    return {"resposta": resposta}


#uvicorn app:app --reload --port 5000