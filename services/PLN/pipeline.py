from model import IntentClassifier
from relatorio import RelatorioEstoque
from generator import gerar_relatorio_texto

class PipelinePLN:
    def __init__(self):
        self.classifier = IntentClassifier()

    def processar_consulta(self, texto):
        intencao = self.classifier.prever_intencao(texto)
        print(f"🧠 Intenção detectada: {intencao}")

        rel = RelatorioEstoque()

        if intencao == "gerar_relatorio":
            dados = rel.por_sku()
            resposta = gerar_relatorio_texto(dados)

        elif intencao == "consulta":
            resposta = rel.geral()

        elif intencao == "saudacao":
            resposta = "Olá! 👋 Como posso te ajudar? Você pode pedir, por exemplo, 'Gerar relatório de estoque'."

        elif intencao == "despedida":
            resposta = "Até mais! 👋 Foi um prazer te ajudar."

        else:
            resposta = "Desculpe, não entendi bem sua solicitação. Pode reformular?"

        return resposta