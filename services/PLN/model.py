from transformers import pipeline

class IntentClassifier:
    def __init__(self):
        # Modelo multilíngue para melhor suporte a PT (zero-shot)
        self.classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

        # Labels de intenções (em PT para melhor matching)
        self.intencoes = [
            "gerar_relatorio",  # Ex.: "gera relatório dos SKUs"
            "consulta",         # Ex.: "qual o consumo total?"
            "saudacao",         # Ex.: "oi", "olá", "tudo bem?"
            "despedida"         # Ex.: "tchau", "obrigado"
        ]

    def prever_intencao(self, texto: str):
        # Faz a predição
        resultado = self.classifier(texto, candidate_labels=self.intencoes)
        intencao_predita = resultado["labels"][0]
        confianca = resultado["scores"][0]

        print(f"🎯 Intenção detectada: {intencao_predita} (confiança: {confianca:.2f})")
        
        # Threshold: Se baixa confiança, retorna "outro" para fallback
        if confianca < 0.5:
            intencao_predita = "outro"
            print(f"⚠️ Confiança baixa, usando fallback: {intencao_predita}")

        return intencao_predita