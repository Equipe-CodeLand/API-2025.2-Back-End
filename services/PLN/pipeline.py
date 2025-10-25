from model import IntentClassifier
from relatorio import RelatorioEstoque
from generator import gerar_relatorio_texto
from param_extractor import ParamExtractor
import re  # Para matching flexível sem spaCy

class PipelinePLN:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.extractor = ParamExtractor()
        
        # Dicionário de explicações rápidas (expanda conforme necessário)
        self.explicacoes = {
            "aging": "Aging médio do estoque refere-se ao tempo médio (em semanas) que os itens permanecem estocados antes de serem consumidos ou vendidos. É calculado como a média dos 'dias_em_estoque' dividida por 7. Um valor alto (ex.: >12 semanas) indica risco de obsolescência; baixo sugere giro eficiente.",
            "frequencia": "Frequência de compra (em meses) mede quantos meses distintos tiveram compras ativas (peso líquido >0). Indica quão regular é o consumo.",
            "risco": "Risco de desabastecimento avalia se o estoque atual cobre o consumo futuro (em semanas). Alto risco: <4 semanas; Médio: 4-12; Baixo: >12.",
            "giro": "Giro SKU/cliente mede a rotatividade de um item por cliente. Alto giro sem estoque é um alerta para repor itens populares.",
            "consumo": "Consumo de estoque (em ton) é a soma total do 'es_totalestoque' no período analisado, representando o volume movimentado."
        }

    def processar_consulta(self, texto):
        # Verificação prioritária por explicação via keywords flexíveis (sem spaCy para evitar erros)
        if self._detectar_explicacao(texto):
            return self._handle_explicacao(texto)
        
        # Fluxo original: Classifier + Extractor
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
            # Garantia de formatação aprimorada: Quebras de parágrafo com \n\n após frases completas
            resposta = re.sub(r'([.!?])\s+', r'\1\n\n', resposta)
            resposta = resposta.strip()

        elif intencao == "consulta":
            # Cria rel só aqui
            dias = params.get("periodo_dias") or 365
            rel = RelatorioEstoque(dias=dias)
            metricas = rel.geral()
            # Formata como texto natural e conversacional, com \n para listas e \n\n para seções
            resposta = f"Claro! Aqui vai um resumo rápido do estoque (período de {dias} dias):\n\n"
            for chave, valor in metricas.items():
                if isinstance(valor, list) and valor:  # Evita listas vazias
                    valor_str = ", ".join([str(v) for v in valor[:5]]) + ("..." if len(valor) > 5 else "")
                else:
                    valor_str = str(valor) if valor is not None else "N/A"
                resposta += f"• {chave}: {valor_str}\n"
            resposta += "\n\nPrecisa de mais detalhes ou um relatório completo? 😊"

        elif intencao == "saudacao":
            resposta = "Oi! 👋 Tudo bem sim, e você?\n\nEstou aqui para ajudar com relatórios de estoque e faturamento. O que você quer saber hoje?\n\nEx.: 'Qual o consumo total?' ou 'Gera relatório dos 5 SKUs de risco'."

        elif intencao == "despedida":
            resposta = "Tchau! 👋 Qualquer coisa sobre relatórios, é só voltar.\n\nTenha um ótimo dia!"

        else:
            # Fallback para "outro" ou ambiguidades: Tenta responder baseado em keywords de relatórios
            resposta = self._handle_geral(texto, params)
            if not resposta:
                resposta = "Hmm, não peguei direito essa. 😅 Pode reformular?\n\nFalo sobre estoque, consumo, aging, riscos...\n\nEx.: 'Me explica o que é aging no relatório' ou 'Gera um resumo geral'."

        return resposta

    def _detectar_explicacao(self, texto):
        """
        Detecção prioritária para explicações usando keywords flexíveis (lida com misspellings como 'oque pe').
        Mais robusta que spaCy para evitar erros de modelo.
        """
        texto_lower = texto.lower().strip()
        
        # Keywords para inícios de pergunta/explicação
        inicio_explicacao = re.search(r'\b(o\s+que|oque|oq|defina|explique|significa|explica|o\s+que\s+é|oque\s+é|oq\s+é|o\s+que\s+pe|oque\s+pe)\b', texto_lower)
        
        # Keywords para termos técnicos
        termo_match = any(termo in texto_lower for termo in self.explicacoes.keys())
        
        # Match se tiver início de explicação E termo técnico
        return bool(inicio_explicacao and termo_match)

    def _handle_explicacao(self, texto):
        """
        Handling dedicado para explicações, extraindo termo e adicionando dados reais.
        """
        texto_lower = texto.lower().strip()
        
        # Extrai termo (flexível: busca o primeiro termo técnico na string)
        for termo in self.explicacoes.keys():
            if termo in texto_lower:
                explicacao_base = self.explicacoes[termo]
                break
        else:
            return "Não identifiquei o termo exato. Tente 'aging', 'frequência', 'risco' etc. 😊"
        
        # Adiciona dado real (como no _handle_geral)
        params = {}  # Placeholder; use extractor se precisar de mais
        dias = 365  # Default
        rel = RelatorioEstoque(dias=dias)
        
        if termo == "aging":
            aging_medio = rel.aging_estoque(rel.estoque)
            dado_real = f"No período atual ({dias} dias), o aging médio é {aging_medio} semanas."
        elif termo == "frequencia":
            freq = rel.frequencia_compra(rel.faturamento)
            dado_real = f"No período atual, a frequência média é de {freq} meses."
        elif termo == "risco":
            risco = rel.risco_desabastecimento(rel.estoque, rel.faturamento)
            dado_real = f"No período atual: {risco}."
        elif termo == "giro":
            # Exemplo simples; ajuste se precisar de métrica específica
            dado_real = "Monitore SKUs com alto giro sem estoque para evitar perdas."
        elif termo == "consumo":
            consumo = rel.estoque_consumido(rel.estoque)
            dado_real = f"No período atual ({dias} dias), o consumo total foi de {consumo} ton."
        else:
            dado_real = ""
        
        # Formatação em parágrafos com \n\n
        resposta = f"{explicacao_base}\n\n{dado_real}\n\nPrecisa de exemplos ou mais detalhes? 😊"
        return resposta

    def _handle_geral(self, texto, params):
        """
        Handling versátil para queries genéricas relacionadas a relatórios.
        Ex.: "O que é aging?" → Explicação + dado real.
        (Agora _handle_explicacao é prioritário, isso é backup)
        """
        texto_lower = texto.lower().strip()
        
        if re.search(r'\b(aging|dias em estoque)\b', texto_lower):
            dias = params.get("periodo_dias") or 365
            rel = RelatorioEstoque(dias=dias)
            aging_medio = rel.aging_estoque(rel.estoque)
            return f"Aging é o tempo médio que o estoque fica parado (em semanas).\n\nNo período atual ({dias} dias), o aging médio é {aging_medio} semanas.\n\nSKUs com alto aging precisam de atenção para evitar obsolescência! Quer um relatório focado nisso?"

        elif re.search(r'\b(risco|desabastecimento)\b', texto_lower):
            dias = params.get("periodo_dias") or 365
            rel = RelatorioEstoque(dias=dias)
            risco = rel.risco_desabastecimento(rel.estoque, rel.faturamento)
            return f"O risco de desabastecimento avalia se o estoque cobre a demanda futura.\n\nAtualmente: {risco}.\n\nPara mitigar, foque em itens de alto giro. Posso gerar um relatório com SKUs arriscados?"

        elif re.search(r'\b(consumo|faturamento)\b', texto_lower):
            dias = params.get("periodo_dias") or 365
            rel = RelatorioEstoque(dias=dias)
            consumo = rel.estoque_consumido(rel.estoque)
            return f"O consumo total de estoque no período ({dias} dias) foi de {consumo} ton.\n\nIsso inclui todos os SKUs.\n\nQuer detalhes por produto ou período customizado?"

        # Se não match, retorna None para fallback principal
        return None