from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Texto(BaseModel):
    conteudo: str

@app.post("/analisar")
def analisar_texto(texto: Texto):
    # Exemplo de "PLN" fake
    palavras = texto.conteudo.split()
    qtd_palavras = len(palavras)
    return {"qtd_palavras": qtd_palavras, "texto": texto.conteudo}

#uvicorn app:app --reload --port 5000