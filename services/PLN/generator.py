from datetime import date
import heapq
from templates.pharases import templates_resumo, templates_consumo, templates_risco
import random

def gerar_relatorio_texto(dados, limite_destaques=5, limite_criticos=5):

    # Data e título
    data_atual = date.today()
    data_formatada = data_atual.strftime("%d/%m/%Y")
    titulo = "Relatório sobre estoque e faturamento - " + data_formatada

    # Consolidar informações gerais
    total_consumido = sum(v.get("1. Estoque consumido (ton)",0) for v in dados.values())
    freq_media = sum(v.get("2. Frequência de compra (meses)",0) for v in dados.values()) / len(dados)
    aging_medio = sum(v.get("3. Aging médio do estoque (semanas)",0) for v in dados.values()) / len(dados)

    # Parágrafo 1 – visão geral
    p1 = random.choice(templates_resumo).format(
        total_consumo=total_consumido,
        freq_media=freq_media,
        aging_medio=aging_medio
    )

    # Parágrafo 2 – destaques
    top_consumo = heapq.nlargest(limite_destaques, dados.items(), key=lambda x: x[1]["1. Estoque consumido (ton)"])
    top_aging = heapq.nlargest(limite_destaques, dados.items(), key=lambda x: x[1]["3. Aging médio do estoque (semanas)"])
    top_risco = [sku for sku, v in dados.items() if "Alto risco" in v["7. Risco de desabastecimento"]][:limite_destaques]

    print(top_aging)

    destaques = []
    if top_consumo:
        destaques.append(f"Os SKUs com maior consumo foram: {', '.join([sku for sku, _ in top_consumo])}.")
        for sku, v in top_consumo:
            frase = random.choice(templates_consumo["consumo"]).format(sku=sku, consumo=v["1. Estoque consumido (ton)"]) + "."
            destaques.append(frase)

    if top_aging:
        destaques.append(f"\nOs SKUs com maior aging foram: {', '.join([sku for sku, _ in top_aging])}.")
        for sku, v in top_aging:
            frase = random.choice(templates_consumo["aging_estoque"]).format(aging=v["3. Aging médio do estoque (semanas)"], sku=sku) + "."
            destaques.append(frase)

    if top_risco:
        destaques.append(f"\nOs SKUs em maior risco de desabastecimento incluem: {', '.join(top_risco)}.")
        for sku in top_risco:
            v = dados[sku]
            frase = random.choice(templates_risco["alto_risco"]).format(sku=sku, risco=v["7. Risco de desabastecimento"])
            destaques.append(frase)

    if not destaques:
        destaques.append("Não foram identificados SKUs de destaque relevantes no período.")
    
    p2 = " ".join(destaques)

    # Parágrafo 3 – críticos
    alto_giro = [sku for sku, v in dados.items() if v["5. SKUs de alto giro sem estoque"]]
    repor = [sku for sku, v in dados.items() if v["6. Itens a repor"]]

    if alto_giro:
        p3 = f"Até {limite_criticos} SKUs de alto giro sem estoque: {', '.join(alto_giro[:limite_criticos])}."
    else:
        p3 = "Não foram identificados SKUs de alto giro sem estoque no período."

    if repor:
        p3 += f" Até {limite_criticos} itens necessitam reposição: {', '.join(repor[:limite_criticos])}."
    else:
        p3 += " Também não há itens pendentes de reposição."

    # Parágrafo 4 – conclusão
    p4 = (
        "De forma geral, o cenário demonstra a importância de acompanhar de perto os SKUs com risco de "
        "desabastecimento e aqueles com baixo consumo histórico, garantindo o equilíbrio entre disponibilidade "
        "de estoque e demanda dos clientes."
    )

    return " ".join([titulo, p1, p2, p3, p4])

# print(gerar_relatorio_texto(relatorio_por_sku))