templates_risco = {
    "alto_risco": [
        "O {sku} apresenta alto risco de desabastecimento risco, exigindo atenção imediata.",
        "{sku} com risco elevado de desabastecimento ({risco}).",
        "A situação do {sku} indica {risco}, medidas preventivas são recomendadas.",
        "O {sku} encontra-se em alto risco ({risco}), potencialmente afetando a disponibilidade.",
        "Risco crítico de desabastecimento para {sku} ({risco})."
    ],
    "medio_risco": [
        "O {sku} apresenta risco moderado de desabastecimento ({risco}), requer monitoramento.",
        "Situação do {sku} classificada como {risco}, atenção periódica recomendada.",
        "{sku} encontra-se com risco intermediário ({risco}), sem ação imediata necessária.",
        "O {sku} possui risco moderado ({risco}), acompanhar tendências de estoque."
    ],
    "baixo_risco": [
        "O {sku} possui risco baixo ({risco}), estoque estável.",
        "Situação segura para {sku} ({risco}), sem necessidade de ação urgente.",
        "{sku} apresenta condição confortável ({risco}), disponibilidade preservada.",
        "O {sku} mantém risco controlado ({risco}), estoque adequado."
    ],
    "sem_consumo": [
        "O {sku} não apresentou consumo no período, pode indicar baixa demanda ou obsolescência.",
        "{sku} permaneceu sem movimentação de estoque durante o intervalo.",
        "Nenhum consumo registrado para {sku} neste período.",
        "O {sku} não teve saída registrada, permanecendo inativo no estoque."
    ]
}

templates_resumo = [
    "No período, os SKUs analisados tiveram consumo total de {total_consumo:.2f} toneladas, frequência média de compra de {freq_media:.1f} meses e aging médio de {aging_medio:.1f} semanas.",
    "Durante o intervalo, o consumo agregado dos SKUs foi de {total_consumo:.2f} toneladas, frequência média de compra {freq_media:.1f} meses e aging médio de {aging_medio:.1f} semanas.",
    "O balanço do período indica {total_consumo:.2f} toneladas consumidas, frequência de compra média de {freq_media:.1f} meses e aging médio de {aging_medio:.1f} semanas."
]

templates_consumo = {
    "1. Estoque consumido (ton)": [
        "O {sku} consumiu {consumo:.2f} toneladas no período.",
        "Registro de consumo do {sku}: {consumo:.2f} toneladas.",
        "{sku} movimentou {consumo:.2f} toneladas em estoque.",
        "Consumo total do {sku}: {consumo:.2f} toneladas."
    ],
    "2. Frequência de compra (meses)": [
        "O {sku} teve frequência média de compra de {frequencia:.1f} meses.",
        "{sku} apresenta intervalo médio de compras de {frequencia:.1f} meses.",
        "Frequência de aquisição do {sku}: {frequencia:.1f} meses.",
        "Intervalo médio de compras para {sku}: {frequencia:.1f} meses."
    ],
    "3. Aging médio do estoque (semanas)": [
        "{sku} possui aging médio do estoque de {aging:.1f} semanas.",
        "O tempo médio em estoque do {sku} é de {aging:.1f} semanas.",
        "A permanência do {sku} no estoque foi de {aging:.1f} semanas."
    ],
    "4. Nº clientes distintos": [
        "{sku} foi consumido por {n_clientes} clientes distintos.",
        "{sku} atendeu {n_clientes} clientes diferentes.",
        "O consumo do {sku} envolve {n_clientes} clientes distintos."
    ]
}
