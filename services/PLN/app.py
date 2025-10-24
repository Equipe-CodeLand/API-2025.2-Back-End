import json
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timedelta
from generator import gerar_relatorio_texto
from fastapi.middleware.cors import CORSMiddleware
from salvarRelatorio import salvar_relatorio
import os

# ==============================
# Models
# ==============================
class RelatorioRequest(BaseModel):
    usuario_id: int
    data_inicio: str
    data_fim: str
    topicos: List[str]
    incluir_todos_skus: bool
    skus: Optional[List[str]] = None

# ==============================
# FastAPI
# ==============================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)

# ==============================
# Classe de Relatório
# ==============================
class RelatorioEstoque:
    def __init__(self, estoque_csv="estoque 1.csv", faturamento_csv="faturamento 1.csv", semanas=52):
        # Carregamento
        self.estoque = pd.read_csv(estoque_csv, sep="|")
        self.faturamento = pd.read_csv(faturamento_csv, sep="|")

        # Normalizar SKUs: garantir SKU_1, SKU_2...
        self.estoque["SKU"] = self.estoque["SKU"].apply(lambda x: x if "SKU_" in x else f"SKU_{x.split('SKU')[-1]}")
        self.faturamento["SKU"] = self.faturamento["SKU"].apply(lambda x: x if "SKU_" in x else f"SKU_{x.split('SKU')[-1]}")

        # Converter datas
        self.estoque["data"] = pd.to_datetime(self.estoque["data"], errors="coerce")
        self.faturamento["data"] = pd.to_datetime(self.faturamento["data"], errors="coerce")

        # Janela de tempo
        hoje = max(self.estoque["data"].max(), self.faturamento["data"].max())
        inicio = hoje - timedelta(weeks=semanas)

        self.estoque = self.estoque[self.estoque["data"] >= inicio]
        self.faturamento = self.faturamento[self.faturamento["data"] >= inicio]

    # ==============================
    # Funções de métricas
    # ==============================
    def estoque_consumido(self, df):
        return round(df["es_totalestoque"].sum(), 2)

    def frequencia_compra(self, df):
        meses = df[df["zs_peso_liquido"] > 0]["data"].dt.to_period("M").nunique()
        return int(meses)

    def aging_estoque(self, df):
        return round(df["dias_em_estoque"].mean() / 7, 2) if not df.empty else 0

    def clientes_consumo(self, df):
        return df["cod_cliente"].nunique() if "cod_cliente" in df.columns else 0

    def alto_giro_sem_estoque(self, df_est, df_fat):
        media_giro = df_fat["giro_sku_cliente"].mean()
        alto_giro = df_fat[df_fat["giro_sku_cliente"] > media_giro]["SKU"].unique()
        sem_estoque = df_est[df_est["es_totalestoque"] <= 0]["SKU"].unique()
        return list(set(alto_giro) & set(sem_estoque))

    def itens_a_repor(self, df):
        return df[df["es_totalestoque"] <= 0]["SKU"].unique().tolist()

    def risco_desabastecimento(self, df_est, df_fat):
        estoque_total = df_est["es_totalestoque"].sum()
        consumo_total = df_fat["zs_peso_liquido"].sum()

        if consumo_total == 0:
            return "Sem consumo histórico"

        semanas_cobertura = estoque_total / (consumo_total / 52)
        if semanas_cobertura < 4:
            return f"Alto risco (cobre {semanas_cobertura:.1f} semanas)"
        elif semanas_cobertura < 12:
            return f"Médio risco (cobre {semanas_cobertura:.1f} semanas)"
        else:
            return f"Baixo risco (cobre {semanas_cobertura:.1f} semanas)"

    # ==============================
    # Relatórios
    # ==============================
    def geral(self):
        return {
            "1. Estoque consumido (ton)": self.estoque_consumido(self.estoque),
            "2. Frequência de compra (meses)": self.frequencia_compra(self.faturamento),
            "3. Aging médio do estoque (semanas)": self.aging_estoque(self.estoque),
            "4. Nº clientes distintos": self.clientes_consumo(self.faturamento),
            "5. SKUs de alto giro sem estoque": self.alto_giro_sem_estoque(self.estoque, self.faturamento),
            "6. Itens a repor": self.itens_a_repor(self.estoque),
            "7. Risco de desabastecimento (geral)": self.risco_desabastecimento(self.estoque, self.faturamento),
        }

    def por_sku(self, data_inicio=None, data_fim=None, skus=None):
        df_est = self.estoque.copy()
        df_fat = self.faturamento.copy()

        # Filtrar por período
        if data_inicio:
            df_est = df_est[df_est["data"] >= data_inicio]
            df_fat = df_fat[df_fat["data"] >= data_inicio]
        if data_fim:
            df_est = df_est[df_est["data"] <= data_fim]
            df_fat = df_fat[df_fat["data"] <= data_fim]

        # Filtrar por SKUs
        if skus:
            df_est = df_est[df_est["SKU"].isin(skus)]
            df_fat = df_fat[df_fat["SKU"].isin(skus)]

        resultado = {}
        for sku in df_est["SKU"].unique():
            est_sku = df_est[df_est["SKU"] == sku]
            fat_sku = df_fat[df_fat["SKU"] == sku]

            resultado[sku] = {
                "1. Estoque consumido (ton)": self.estoque_consumido(est_sku),
                "2. Frequência de compra (meses)": self.frequencia_compra(fat_sku),
                "3. Aging médio do estoque (semanas)": self.aging_estoque(est_sku),
                "4. Nº clientes que consomem": self.clientes_consumo(fat_sku),
                "5. SKUs de alto giro sem estoque": self.alto_giro_sem_estoque(est_sku, fat_sku),
                "6. Itens a repor": self.itens_a_repor(est_sku),
                "7. Risco de desabastecimento": self.risco_desabastecimento(est_sku, fat_sku),
            }

        # Garantir que todos os SKUs pedidos aparecem mesmo que não tenham dados
        if skus:
            for sku in skus:
                if sku not in resultado:
                    resultado[sku] = {
                        "1. Estoque consumido (ton)": 0,
                        "2. Frequência de compra (meses)": 0,
                        "3. Aging médio do estoque (semanas)": 0,
                        "4. Nº clientes que consomem": 0,
                        "5. SKUs de alto giro sem estoque": [],
                        "6. Itens a repor": [],
                        "7. Risco de desabastecimento": "Sem dados",
                    }

        return resultado

# ==============================
# Helpers
# ==============================
def normalize(text):
    return ''.join(c.lower() for c in text if c.isalnum() or c.isspace())

# ==============================
# Rotas FastAPI
# ==============================
@app.post("/relatorio")
def gerar_relatorio(request: RelatorioRequest):
    rel = RelatorioEstoque()
    dados = rel.geral()

    caminho = salvar_relatorio(
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
    rel = RelatorioEstoque()

    # Ajustar SKUs para o formato correto
    skus_formatados = None
    if not request.incluir_todos_skus and request.skus:
        skus_formatados = [sku.replace("SKU", "SKU_") if "SKU_" not in sku else sku for sku in request.skus]

    dados = rel.por_sku(
        data_inicio=request.data_inicio,
        data_fim=request.data_fim,
        skus=skus_formatados
    )

    # Filtrar tópicos
    if request.topicos:
        topicos_normalizados = [normalize(t) for t in request.topicos]
        for sku in dados:
            dados[sku] = {k: v for k, v in dados[sku].items() if any(t in normalize(k) for t in topicos_normalizados)}

    texto = gerar_relatorio_texto(dados, topicos=request.topicos, data_inicio=request.data_inicio, data_fim=request.data_fim)

    caminho = salvar_relatorio(
        texto,
        tipo="sku",
        como_json=True,
        chat_id=1,
        usuario_id=request.usuario_id,
        titulo="Relatório por SKU"
    )

    return {"dados": dados, "arquivo": caminho, "conteudo": texto}

@app.get("/relatorio/conteudo")
def obter_conteudo(caminho: str):
    if not os.path.exists(caminho):
        return {"conteudo": "Arquivo não encontrado"}
    
    with open(caminho, "r", encoding="utf-8") as f:
        try:
            conteudo = json.load(f)
        except json.JSONDecodeError:
            conteudo = f.read()
    
    return {"conteudo": conteudo}
