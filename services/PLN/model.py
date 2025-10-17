from transformers import pipeline

class IntentClassifier:
    def __init__(self):
        # Carrega modelo de classificação zero-shot (sem precisar treinar)
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

        # Labels de intenções possíveis
        self.intencoes = [
            "gerar_relatorio",
            "consulta",
            "saudacao",
            "despedida"
        ]

    def prever_intencao(self, texto: str):
        # Faz a predição com base na frase do usuário
        resultado = self.classifier(texto, candidate_labels=self.intencoes)
        intencao_predita = resultado["labels"][0]
        confianca = resultado["scores"][0]

        print(f"🎯 Intenção detectada: {intencao_predita} (confiança: {confianca:.2f})")
        return intencao_predita