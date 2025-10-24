from model import IntentClassifier
from relatorio import RelatorioEstoque
from generator import gerar_relatorio_texto
from param_extractor import ParamExtractor

class PipelinePLN:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.extractor = ParamExtractor()

    def processar_consulta(self, texto):
        intencao = self.classifier.prever_intencao(texto)
        print(f"🧠 Intenção final: {intencao}")

        params = self.extractor.extrair_parametros(texto)
        print(f"📊 Parâmetros extraídos: {params}")

        rel = None  # Inicializa como None

        if intencao == "gerar_relatorio":
            # Cria rel só aqui, com handling de None para dias
            dias = params.get("periodo_dias") or 365  # Usa 365 se None ou ausente
            rel = RelatorioEstoque(dias=dias)
            dados = rel.por_sku(atributos=params.get("atributos", None))

            # Limitar SKUs
            if params["limite_skus"]:
                dados = dict(list(dados.items())[:params["limite_skus"]])

            resposta = gerar_relatorio_texto(dados, atributos=params.get("atributos", None))

        elif intencao == "consulta":
            # Cria rel só aqui
            dias = params.get("periodo_dias") or 365
            rel = RelatorioEstoque(dias=dias)
            metricas = rel.geral()
            # Formata como texto natural e conversacional
            resposta = f"Claro! Aqui vai um resumo rápido do estoque (período de {dias} dias):\n"
            for chave, valor in metricas.items():
                if isinstance(valor, list):
                    valor_str = ", ".join(valor[:5]) + ("..." if len(valor) > 5 else "")
                else:
                    valor_str = str(valor)
                resposta += f"• {chave}: {valor_str}\n"
            resposta += "\nPrecisa de mais detalhes ou um relatório completo? 😊"

        elif intencao == "saudacao":
            resposta = "Oi! 👋 Tudo bem sim, e você? Estou aqui para ajudar com relatórios de estoque e faturamento. O que você quer saber hoje? Ex.: 'Qual o consumo total?' ou 'Gera relatório dos 5 SKUs de risco'."

        elif intencao == "despedida":
            resposta = "Tchau! 👋 Qualquer coisa sobre relatórios, é só voltar. Tenha um ótimo dia!"

        else:
            # Fallback para "outro" ou ambiguidades: Tenta responder baseado em keywords de relatórios
            resposta = self._handle_geral(texto, params)
            if not resposta:
                resposta = "Hmm, não peguei direito essa. 😅 Pode reformular? Falo sobre estoque, consumo, aging, riscos... Ex.: 'Me explica o que é aging no relatório' ou 'Gera um resumo geral'."

        return resposta

    def _handle_geral(self, texto, params):
        """
        Handling versátil para queries genéricas relacionadas a relatórios.
        Ex.: "O que é aging?" → Explicação + dado real.
        """
        texto_lower = texto.lower()
        
        if any(palavra in texto_lower for palavra in ["aging", "dias em estoque"]):
            dias = params.get("periodo_dias") or 365
            rel = RelatorioEstoque(dias=dias)
            aging_medio = rel.aging_estoque(rel.estoque)
            return f"Aging é o tempo médio que o estoque fica parado (em semanas). No período atual ({dias} dias), o aging médio é {aging_medio} semanas. SKUs com alto aging precisam de atenção para evitar obsolescência! Quer um relatório focado nisso?"

        elif any(palavra in texto_lower for palavra in ["risco", "desabastecimento"]):
            dias = params.get("periodo_dias") or 365
            rel = RelatorioEstoque(dias=dias)
            risco = rel.risco_desabastecimento(rel.estoque, rel.faturamento)
            return f"O risco de desabastecimento avalia se o estoque cobre a demanda futura. Atualmente: {risco}. Para mitigar, foque em itens de alto giro. Posso gerar um relatório com SKUs arriscados?"

        elif "consumo" in texto_lower or "faturamento" in texto_lower:
            dias = params.get("periodo_dias") or 365
            rel = RelatorioEstoque(dias=dias)
            consumo = rel.estoque_consumido(rel.estoque)
            return f"O consumo total de estoque no período ({dias} dias) foi de {consumo} ton. Isso inclui todos os SKUs. Quer detalhes por produto ou período customizado?"

        # Se não match, retorna None para fallback principal
        return None