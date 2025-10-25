from datetime import date, datetime
import heapq
from templates.pharases import templates_resumo, templates_consumo, templates_risco  # Sua import (André)
import random  # Sua (André)

def gerar_relatorio_texto(dados, topicos=None, limite_destaques=5, data_inicio=None, data_fim=None, atributos=None):
    """
    Híbrido: Usa templates seus para variedade (André), mas filtra por topicos (Felipe) e formata datas.
    """
    if topicos is None:  # Default da main (Felipe)
        topicos = [
            "1. Estoque consumido (ton)",
            "2. Frequência de compra (meses)",
            "3. Aging médio do estoque (semanas)",
            "4. Nº clientes distintos",
            "5. SKUs de alto giro sem estoque",
            "6. Itens a repor",
            "7. Risco de desabastecimento"
        ]

    # Data e título (híbrido: seu + formatação da main - André + Felipe)
    data_atual = date.today().strftime("%d/%m/%Y")
    data_inicio_fmt = formatar_data(data_inicio) if data_inicio else ""
    data_fim_fmt = formatar_data(data_fim) if data_fim else ""
    periodo = f"entre {data_inicio_fmt} e {data_fim_fmt} " if data_inicio_fmt and data_fim_fmt else ""
    titulo = f"Relatório sobre estoque e faturamento - {periodo}gerado em {data_atual}"

    paragrafos = [titulo]

    # Consolidar gerais (seu, filtrado por topicos - André + Felipe)
    total_consumido = sum(v.get("1. Estoque consumido (ton)", 0) for v in dados.values() if "1. Estoque consumido (ton)" in v and "1. Estoque consumido (ton)" in topicos)
    freq_media = sum(v.get("2. Frequência de compra (meses)", 0) for v in dados.values() if "2. Frequência de compra (meses)" in v and "2. Frequência de compra (meses)" in topicos) / len(dados) if dados else 0
    aging_medio = sum(v.get("3. Aging médio do estoque (semanas)", 0) for v in dados.values() if "3. Aging médio do estoque (semanas)" in v and "3. Aging médio do estoque (semanas)" in topicos) / len(dados) if dados else 0

    # Parágrafo 1 – visão geral (seu template, mas só se topicos permitirem - André + Felipe)
    if any(t in topicos for t in ["1. Estoque consumido (ton)", "2. Frequência de compra (meses)", "3. Aging médio do estoque (semanas)"]):
        p1 = random.choice(templates_resumo).format(
            total_consumo=total_consumido,
            freq_media=freq_media,
            aging_medio=aging_medio
        )
    else:
        p1 = "Resumo geral baseado nos atributos solicitados."
    paragrafos.append(p1)

    # Parágrafo 2 – destaques (seu heapq + templates, filtrado por topicos - André + Felipe)
    destaques = []
    if "1. Estoque consumido (ton)" in topicos and "1. Estoque consumido (ton)" in next(iter(dados.values()), {}):
        top_consumo = heapq.nlargest(limite_destaques, dados.items(), key=lambda x: x[1].get("1. Estoque consumido (ton)", 0))
        if top_consumo:
            destaques.append(f"Os SKUs com maior consumo foram: {', '.join([sku for sku, _ in top_consumo])}.")
            for sku, v in top_consumo:
                # Fallback se templates não existirem
                if 'templates_consumo' in globals() and templates_consumo and "consumo" in templates_consumo:
                    frase = random.choice(templates_consumo["consumo"]).format(sku=sku, consumo=v["1. Estoque consumido (ton)"]) + "."
                else:
                    frase = f"O SKU {sku} consumiu {v['1. Estoque consumido (ton)']:.2f} toneladas." + "."
                destaques.append(frase)

    if "3. Aging médio do estoque (semanas)" in topicos and "3. Aging médio do estoque (semanas)" in next(iter(dados.values()), {}):
        top_aging = heapq.nlargest(limite_destaques, dados.items(), key=lambda x: x[1].get("3. Aging médio do estoque (semanas)", 0))
        if top_aging:
            destaques.append(f"\nOs SKUs com maior aging foram: {', '.join([sku for sku, _ in top_aging])}.")
            for sku, v in top_aging:
                if 'templates_consumo' in globals() and templates_consumo and "aging_estoque" in templates_consumo:
                    frase = random.choice(templates_consumo["aging_estoque"]).format(aging=v["3. Aging médio do estoque (semanas)"], sku=sku) + "."
                else:
                    frase = f"O SKU {sku} tem aging médio de {v['3. Aging médio do estoque (semanas)']:.1f} semanas." + "."
                destaques.append(frase)

    if "7. Risco de desabastecimento" in topicos and "7. Risco de desabastecimento" in next(iter(dados.values()), {}):
        top_risco = [sku for sku, v in dados.items() if "Alto risco" in v["7. Risco de desabastecimento"]][:limite_destaques]
        if top_risco:
            destaques.append(f"\nOs SKUs em maior risco de desabastecimento incluem: {', '.join(top_risco)}.")
            for sku in top_risco:
                v = dados[sku]
                if 'templates_risco' in globals() and templates_risco and "alto_risco" in templates_risco:
                    frase = random.choice(templates_risco["alto_risco"]).format(sku=sku, risco=v["7. Risco de desabastecimento"])
                else:
                    frase = f"O SKU {sku} está em {v['7. Risco de desabastecimento']}."
                destaques.append(frase)

    if not destaques:
        destaques.append("Não foram identificados SKUs de destaque relevantes no período.")
    paragrafos.append(" ".join(destaques))

    # Parágrafo 3 – críticos (híbrido: seu + filtros da main - André + Felipe)
    alto_giro = [sku for sku, v in dados.items() if v.get("5. SKUs de alto giro sem estoque", False) and "5. SKUs de alto giro sem estoque" in topicos]
    repor = [sku for sku, v in dados.items() if v.get("6. Itens a repor", False) and "6. Itens a repor" in topicos]

    p3 = ""
    if alto_giro:
        p3 += f"Até {limite_destaques} SKUs de alto giro sem estoque: {', '.join(alto_giro[:limite_destaques])}."
    else:
        p3 += "Não foram identificados SKUs de alto giro sem estoque no período."

    if repor:
        p3 += f" Até {limite_destaques} itens necessitam reposição: {', '.join(repor[:limite_destaques])}."
    else:
        p3 += " Também não há itens pendentes de reposição."
    paragrafos.append(p3)

    # Parágrafo 4 – conclusão (seu - André)
    p4 = (
        "De forma geral, o cenário demonstra a importância de acompanhar de perto os SKUs com risco de "
        "desabastecimento e aqueles com baixo consumo histórico, garantindo o equilíbrio entre disponibilidade "
        "de estoque e demanda dos clientes."
    )
    paragrafos.append(p4)

    return " ".join(paragrafos)

def formatar_data(data_str):  # Da main (Felipe)
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return data_str