import re
from datetime import timedelta

class ParamExtractor:
    def __init__(self):
        pass

    def extrair_parametros(self, texto: str):
        texto = texto.lower()
        params = {
            "limite_skus": None,
            "periodo_dias": None,
            "atributos": []
        }

        # Extrai número de SKUs (mais flexível)
        match_sku = re.search(r"(\d+)\s*(?:skus?|produtos?|itens?|top\s+\d+)", texto)
        if match_sku:
            params["limite_skus"] = int(match_sku.group(1))

        # Extrai período (mais robusto: dias, semanas, meses, ou "último mês")
        match_periodo = re.search(r"últimos?\s*(\d+)\s*(dias?|semanas?|meses?)|período\s+de\s*(\d+)", texto)
        if match_periodo:
            qtd = int(match_periodo.group(1) or match_periodo.group(3))
            unidade = match_periodo.group(2) or "dias"
            if "semana" in unidade:
                params["periodo_dias"] = qtd * 7
            elif "mes" in unidade:
                params["periodo_dias"] = qtd * 30
            else:
                params["periodo_dias"] = qtd
        # Fallback para "mês atual" ou similar
        elif "mês" in texto or "atual" in texto:
            params["periodo_dias"] = 30

        # Extrai atributos específicos (expandido)
        atributos_possiveis = {
            "consumo": ["consumo", "consumido", "vendas"],
            "aging": ["aging", "dias em estoque"],
            "frequencia": ["frequência", "compra", "giro"],
            "clientes": ["clientes", "clientes distintos"],
            "estoque": ["estoque", "repor"],
            "risco": ["risco", "desabastecimento"]
        }
        for attr, keywords in atributos_possiveis.items():
            if any(kw in texto for kw in keywords):
                params["atributos"].append(attr)

        return params