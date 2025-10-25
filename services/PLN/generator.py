from datetime import date, datetime
import heapq

def gerar_relatorio_texto(dados, topicos=None, limite_destaques=5, data_inicio=None, data_fim=None):
    if topicos is None:
        topicos = [
            "1. Estoque consumido (ton)",
            "2. Frequência de compra (meses)",
            "3. Aging médio do estoque (semanas)",
            "4. Nº clientes distintos",
            "5. SKUs de alto giro sem estoque",
            "6. Itens a repor",
            "7. Risco de desabastecimento"
        ]

    paragrafos = []

    data_inicio_fmt = formatar_data(data_inicio) if data_inicio else ""
    data_fim_fmt = formatar_data(data_fim) if data_fim else ""

    # Título com período e data de geração
    data_atual = date.today().strftime("%d/%m/%Y")
    periodo = ""
    if data_inicio_fmt and data_fim_fmt:
        periodo = f"entre {data_inicio_fmt} e {data_fim_fmt} "
    titulo = f"Relatório sobre estoque e faturamento da empresa, {periodo}- gerado em {data_atual}"
    paragrafos.append(titulo)

    # 1° paragrafo: Resumo geral
    if any(t in topicos for t in ["1. Estoque consumido (ton)", "2. Frequência de compra (meses)", "3. Aging médio do estoque (semanas)"]):
        total_consumo = sum(v.get("1. Estoque consumido (ton)",0) for v in dados.values())
        freq_media = sum(v.get("2. Frequência de compra (meses)",0) for v in dados.values()) / max(len(dados),1)
        aging_medio = sum(v.get("3. Aging médio do estoque (semanas)",0) for v in dados.values()) / max(len(dados),1)
        paragrafos.append(
            f"No período analisado, os SKUs tiveram consumo total de {total_consumo:.2f} toneladas, "
            f"frequência média de compra de {freq_media:.1f} meses e aging médio do estoque de {aging_medio:.1f} semanas."
        )

    # 2° paragrafo: Maiores consumos, agings e frequencia de compras
    frases = []

    if "1. Estoque consumido (ton)" in topicos:
        top_consumo = heapq.nlargest(limite_destaques, dados.items(), key=lambda x: x[1].get("1. Estoque consumido (ton)",0))
        frases.append("Considerando os SKUs com maior consumo no período analisado:")
        for sku, v in top_consumo:
            frases.append(f"{sku} consumiu {v.get('1. Estoque consumido (ton)',0):.2f} toneladas.")

    if "3. Aging médio do estoque (semanas)" in topicos:
        top_aging = heapq.nlargest(limite_destaques, dados.items(), key=lambda x: x[1].get("3. Aging médio do estoque (semanas)",0))
        frases.append("Os SKUs que registraram os maiores aging médios em seus estoque foram:")
        for sku, v in top_aging:
            frases.append(f"{sku} permanece em estoque há {v.get('3. Aging médio do estoque (semanas)',0):.1f} semanas.")

    if "2. Frequência de compra (meses)" in topicos:
        top_freq = heapq.nlargest(limite_destaques, dados.items(), key=lambda x: x[1].get("2. Frequência de compra (meses)",float('inf')))
        frases.append("Os SKUs com maior frequência média de compra foram:")
        for sku, v in top_freq:
            frases.append(f"{sku} tem frequência média de compra de {v.get('2. Frequência de compra (meses)',0):.1f} meses.")

    if frases:
        paragrafos.append(" ".join(frases))

    # 3° paragrafo: Risco de desabastecimento
    if "7. Risco de desabastecimento" in topicos:
        alto_risco = {sku for sku,v in dados.items() if "Alto risco" in v.get("7. Risco de desabastecimento","")}
        medio_risco = [sku for sku,v in dados.items() if "Médio risco" in v.get("7. Risco de desabastecimento","")]
        baixo_risco = [sku for sku,v in dados.items() if "Baixo risco" in v.get("7. Risco de desabastecimento","")]
        sem_consumo = [sku for sku,v in dados.items() if "Sem consumo" in v.get("7. Risco de desabastecimento","")]

        frases_risco = []

        # Detalhar todos os skus com alto risco
        if alto_risco:
            frases_risco.append(
                f"Os seguintes SKUs estão em ALTO RISCO de desabastecimento: {', '.join(alto_risco)}."
            )
        else:
            frases_risco.append("Nenhum SKU foi classificado com alto risco de desabastecimento.")

        # Outras categorias: só quantidade
        if medio_risco:
            frases_risco.append(f"Também foram encontrados {len(medio_risco)} SKUs em médio risco,")

        if baixo_risco:
            frases_risco.append(f"além de {len(baixo_risco)} SKUs em baixo risco")
        if sem_consumo:
            frases_risco.append(f"e {len(sem_consumo)} SKUs sem consumo registrado.")

        if frases_risco:
            paragrafos.append(" ".join(frases_risco))

    # 4° paragrafo: Alto giro / itens a repor
    frases = []
    if "5. SKUs de alto giro sem estoque" in topicos:
        alto_giro = [sku for sku,v in dados.items() if v.get("5. SKUs de alto giro sem estoque")]
        if alto_giro:
            top_skus = alto_giro[:limite_destaques]
            restante = len(alto_giro) - len(top_skus)
            frases_critico = [f"{sku} está sem estoque, além de possuir alto giro." for sku in top_skus]
            if restante > 0:
                frases_critico.append(f"Entre outros {restante} SKUs de alto giro sem estoque.")
            frases.append(" ".join(frases_critico))
        else:
            frases.append("Não foram identificados SKUs de alto giro sem estoque.")

    if "6. Itens a repor" in topicos:
        repor = [sku for sku,v in dados.items() if v.get("6. Itens a repor")]
        if repor:
            top_skus = repor[:limite_destaques]
            restante = len(repor) - len(top_skus)
            frases_repor = [f"{sku} necessita reposição." for sku in top_skus]
            if restante > 0:
                frases_repor.append(f"Entre outros {restante} SKUs a repor.")
            frases.append(" ".join(frases_repor))
        else:
            frases.append("Não há itens pendentes de reposição.")
    if frases:
        paragrafos.append(" ".join(frases))

    return paragrafos

def formatar_data(data_str):
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return data_str