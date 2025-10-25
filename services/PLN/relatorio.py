import pandas as pd
from datetime import timedelta

class RelatorioEstoque:
    def __init__(self, estoque_csv="estoque 1.csv", faturamento_csv="faturamento 1.csv", dias=365):
        # Carregamento
        self.estoque = pd.read_csv(estoque_csv, sep="|")
        self.faturamento = pd.read_csv(faturamento_csv, sep="|")

        # Normalização de SKUs (adição da main - Felipe)
        self.estoque["SKU"] = self.estoque["SKU"].apply(lambda x: x if "SKU_" in x else f"SKU_{x.split('SKU')[-1]}")
        self.faturamento["SKU"] = self.faturamento["SKU"].apply(lambda x: x if "SKU_" in x else f"SKU_{x.split('SKU')[-1]}")

        # Converter datas
        self.estoque["data"] = pd.to_datetime(self.estoque["data"], errors="coerce")
        self.faturamento["data"] = pd.to_datetime(self.faturamento["data"], errors="coerce")

        # Janela de tempo em dias (seu padrão; main usa semanas=52, mas convertemos para dias=365 para alinhar)
        hoje = max(self.estoque["data"].max(), self.faturamento["data"].max())
        inicio = hoje - timedelta(days=dias)

        self.estoque = self.estoque[self.estoque["data"] >= inicio]
        self.faturamento = self.faturamento[self.faturamento["data"] >= inicio]

    # ==============================
    # Funções de métricas (suas, sem mudanças - André)
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

        # Corrige: _get_dias() retorna float (número de dias) - sua correção (André)
        num_dias = self._get_dias()
        if num_dias <= 0:
            return "Período inválido ou sem dados"

        num_semanas = num_dias / 7
        consumo_por_semana = consumo_total / num_semanas
        semanas_cobertura = estoque_total / consumo_por_semana if consumo_por_semana > 0 else float('inf')

        if semanas_cobertura < 4:
            return f"Alto risco (cobre {semanas_cobertura:.1f} semanas)"
        elif semanas_cobertura < 12:
            return f"Médio risco (cobre {semanas_cobertura:.1f} semanas)"
        else:
            return f"Baixo risco (cobre {semanas_cobertura:.1f} semanas)"

    def _get_dias(self):
        """
        Retorna o número de dias no período como float (corrigido para evitar Timedelta) - sua correção (André)
        """
        if self.estoque.empty:
            return 365.0  # Default
        diff = (self.estoque["data"].max() - self.estoque["data"].min())
        return diff.days if pd.notna(diff) else 365.0  # Usa .days para converter Timedelta para int

    # ==============================
    # Relatórios (suas, com adições da main para filtros - André + Felipe)
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

    def por_sku(self, data_inicio=None, data_fim=None, skus=None, atributos=None):
        """
        Retorna métricas por SKU, com filtros de data/SKU (da main - Felipe) e atributos (sua - André).
        """
        df_est = self.estoque.copy()
        df_fat = self.faturamento.copy()

        # Filtros de data (adição da main - Felipe)
        if data_inicio:
            df_est = df_est[df_est["data"] >= pd.to_datetime(data_inicio)]
            df_fat = df_fat[df_fat["data"] >= pd.to_datetime(data_inicio)]
        if data_fim:
            df_est = df_est[df_est["data"] <= pd.to_datetime(data_fim)]
            df_fat = df_fat[df_fat["data"] <= pd.to_datetime(data_fim)]

        # Filtro por SKUs (adição da main - Felipe)
        if skus:
            df_est = df_est[df_est["SKU"].isin(skus)]
            df_fat = df_fat[df_fat["SKU"].isin(skus)]

        resultado = {}
        skus_unicos = df_est["SKU"].unique().tolist()

        for sku in skus_unicos:
            est_sku = df_est[df_est["SKU"] == sku]
            fat_sku = df_fat[df_fat["SKU"] == sku]

            metricas_sku = {
                "1. Estoque consumido (ton)": self.estoque_consumido(est_sku),
                "2. Frequência de compra (meses)": self.frequencia_compra(fat_sku),
                "3. Aging médio do estoque (semanas)": self.aging_estoque(est_sku),
                "4. Nº clientes que consomem": self.clientes_consumo(fat_sku),
                "5. SKUs de alto giro sem estoque": self.alto_giro_sem_estoque(est_sku, fat_sku),
                "6. Itens a repor": self.itens_a_repor(est_sku),
                "7. Risco de desabastecimento": self.risco_desabastecimento(est_sku, fat_sku),
            }

            # Filtra atributos se solicitado (sua feature - André)
            if atributos:
                resultado[sku] = {k: v for k, v in metricas_sku.items() if any(attr in k.lower() for attr in atributos)}
            else:
                resultado[sku] = metricas_sku

        # Garantir que todos os SKUs pedidos aparecem mesmo que não tenham dados (da main - Felipe)
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