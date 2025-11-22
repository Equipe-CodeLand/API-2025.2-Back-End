"""
Módulo de Assertividade para Relatórios de SKU
Calcula métricas de confiabilidade e qualidade dos relatórios
"""

class RelatorioAssertividade:
    def __init__(self, dados_sku):
        """
        Calcula métricas de assertividade baseado nos dados dos SKUs
        
        Args:
            dados_sku: dict com formato {"SKU_xxx": {"1. Métrica": valor, ...}, ...}
        """
        self.dados = dados_sku
        self.total_skus = len(dados_sku)
    
    def _calcular_assertividade_por_sku(self, sku_data):
        """
        Calcula score de assertividade (0-100) para um SKU individual
        Baseado em: dados disponíveis, consistência e risco
        """
        if not sku_data:
            return 0
        
        score = 100
        razoes_reducao = []
        
        # Verificar dados vazios (reduz 20 pontos)
        valores_vazios = 0
        for v in sku_data.values():
            try:
                is_empty = False
                if v == 0:
                    is_empty = True
                elif isinstance(v, list) and len(v) == 0:
                    is_empty = True
                elif "Sem dados" in str(v):
                    is_empty = True
                if is_empty:
                    valores_vazios += 1
            except (TypeError, ValueError):
                pass
        
        if valores_vazios > 0:
            reducao = min(20, valores_vazios * 5)
            score -= reducao
            if reducao > 0:
                razoes_reducao.append(f"Dados incompletos ({valores_vazios} campos vazios)")
        
        # Verificar risco alto (reduz 15 pontos)
        risco = sku_data.get("7. Risco de desabastecimento", "")
        if "Alto risco" in str(risco):
            score -= 15
            razoes_reducao.append("Alto risco de desabastecimento")
        
        # Verificar alto giro sem estoque (reduz 10 pontos)
        alto_giro = sku_data.get("5. SKUs de alto giro sem estoque", [])
        try:
            if len(alto_giro) > 0:
                score -= 10
                razoes_reducao.append("Alto giro sem estoque")
        except (TypeError, ValueError):
            pass
        
        # Verificar itens a repor (reduz 8 pontos)
        repor = sku_data.get("6. Itens a repor", [])
        try:
            if len(repor) > 0:
                score -= 8
                razoes_reducao.append("Itens a repor")
        except (TypeError, ValueError):
            pass
        
        # Aging muito alto (reduz 5 pontos)
        aging = sku_data.get("3. Aging médio do estoque (semanas)", 0)
        if aging > 16:  # Mais de 16 semanas
            score -= 5
            razoes_reducao.append(f"Aging elevado ({aging:.1f} semanas)")
        
        return max(0, score), razoes_reducao
    
    def gerar_relatorio(self):
        """
        Gera relatório completo de assertividade
        """
        if not self.dados:
            return {
                "status": "sem_dados",
                "mensagem": "Nenhum dado disponível para análise",
                "total_skus": 0,
                "skus_analisados": []
            }
        
        scores = {}
        detalhes = {}
        
        for sku, dados in self.dados.items():
            score, razoes = self._calcular_assertividade_por_sku(dados)
            scores[sku] = score
            detalhes[sku] = razoes
        
        # Cálculos agregados
        media_score = sum(scores.values()) / len(scores) if scores else 0
        skus_assertivos = sum(1 for s in scores.values() if s >= 80)  # >= 80 = assertivo
        skus_moderados = sum(1 for s in scores.values() if 50 <= s < 80)
        skus_criticos = sum(1 for s in scores.values() if s < 50)
        
        # Classificação geral
        if media_score >= 80:
            classificacao_geral = "Excelente"
        elif media_score >= 60:
            classificacao_geral = "Bom"
        elif media_score >= 40:
            classificacao_geral = "Moderado"
        else:
            classificacao_geral = "Crítico"
        
        # Top 5 melhores e piores
        top_melhores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        top_piores = sorted(scores.items(), key=lambda x: x[1])[:5]
        
        return {
            "resumo": {
                "classificacao_geral": classificacao_geral,
                "media_assertividade": round(media_score, 1),
                "total_skus": self.total_skus,
                "skus_assertivos": skus_assertivos,
                "skus_moderados": skus_moderados,
                "skus_criticos": skus_criticos,
                "percentual_assertivo": round((skus_assertivos / self.total_skus * 100), 1) if self.total_skus > 0 else 0,
                "percentual_critico": round((skus_criticos / self.total_skus * 100), 1) if self.total_skus > 0 else 0
            },
            "detalhes_por_sku": {
                sku: {
                    "score": scores[sku],
                    "razoes": detalhes[sku]
                }
                for sku in scores
            },
            "melhores_skus": [
                {"sku": sku, "score": score}
                for sku, score in top_melhores
            ],
            "piores_skus": [
                {"sku": sku, "score": score, "razoes": detalhes[sku]}
                for sku, score in top_piores
            ]
        }
