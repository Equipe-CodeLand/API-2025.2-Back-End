templates_risco = {
    "sem_consumo": [
        "O {sku} não apresentou consumo, o que pode indicar obsolescência ou baixa relevância.",
        "Observa-se que o {sku} permaneceu sem consumo histórico recente.",
        "O {sku} não teve movimentação de estoque no período analisado.",
        "Nenhum consumo foi registrado para o {sku}",
    ],
    "alto_risco": [
        "O {sku} com seu risco de desabatecimento {risco}, necessário atenção imediata.",
        "O {sku} apresenta um cenário preocupante de risco elevado de desabastecimento, categorizado como {risco}.",
        "O risco de desabastecimento do {sku} é {risco}, exigindo monitoramento constante.",
        "O {sku} está classificado com {risco} para seu desabastecimento, o que demanda ações preventivas."
    ],
    "baixo_risco": [
        "O {sku} mantém uma posição estável, com risco de desabastecimento {risco}.",
        "O risco de desabastecimento para o {sku} não é preocupante, atualmente classificado como {risco}.",
        "O {sku} apresenta um risco de desabastecimento {risco}, indicando uma situação controlada.",
        "O {sku} está em uma condição segura, com risco de desabastecimento {risco}."
    ],
    "medio_risco": [
        "O {sku} apresenta um risco moderado de desabastecimento, classificado como {risco}.",
        "O risco de desabastecimento do {sku} é {risco}, sugerindo a necessidade de atenção regular.",
        "O {sku} está em uma situação de risco categorizado como {risco} para desabastecimento.",
        "O {sku} possui um risco de desabastecimento {risco}, o que requer monitoramento periodico."
    ]
}

templates_resumo = [
    "No período, o conjunto de SKUs analisados apresentou um consumo total de {total_consumo:.2f} toneladas, com uma frequência média de compra de {freq_media:.1f} meses e um aging médio do estoque de {aging_medio:.1f} semanas.",
    "Durante o intervalo analisado, os SKUs tiveram um consumo agregado de {total_consumo:.2f} toneladas, com frequência média de compra de {freq_media:.1f} meses e aging médio do estoque de {aging_medio:.1f} semanas.",
    "Ao longo do período, o consumo total dos SKUs foi de {total_consumo:.2f} toneladas, apresentando uma frequência média de compra de {freq_media:.1f} meses e um aging médio do estoque de {aging_medio:.1f} semanas.",
    "No intervalo considerado, os SKUs analisados consumiram um total de {total_consumo:.2f} toneladas, com frequência média de compra de {freq_media:.1f} meses e aging médio do estoque de {aging_medio:.1f} semanas."
]

templates_consumo = {
    "consumo": [
        "O {sku} teve consumo de {consumo:.2f} toneladas",
        "Durante o período, o {sku} apresentou um consumo de {consumo:.2f} toneladas",
        "No intervalo analisado, o {sku} consumiu {consumo:.2f} toneladas de estoque",
        "O {sku} registrou um consumo de {consumo:.2f} toneladas"
    ],
    "frequencia_compra": [
        "com uma frequência de compra de {frequencia:.1f} meses no periodo analisado",
        "apresentando uma frequência média de compra de {frequencia:.1f} meses no intervalo considerado",
        "com frequência de compra estimada em {frequencia:.1f} meses durante o período",
        "registrando uma frequência de compra de {frequencia:.1f} meses dentro do intervalo analisado"
    ],
    "aging_estoque": [
        "O {sku} apresentou um aging médio do estoque de {aging:.1f} semanas",
        "Se tratando do {sku} o estoque possui um aging médio calculado em {aging:.1f} semanas",
        "O {sku} atualmente possui um aging médio do estoque de {aging:.1f} semanas",
        "Considerando o {sku} seu aging médio do estoque está estimado em {aging:.1f} semanas"
    ]
}

templates_conclusao = [
    "De forma geral, o cenário demonstra a importância de acompanhar de perto os SKUs com risco de desabastecimento e aqueles com baixo consumo histórico, garantindo o equilíbrio entre disponibilidade de estoque e demanda dos clientes.",
    "Em resumo, é crucial monitorar os SKUs com risco de desabastecimento e aqueles com baixo consumo histórico para manter um equilíbrio adequado entre a disponibilidade de estoque e a demanda dos clientes.",
    "Concluindo, a gestão eficaz dos SKUs com risco de desabastecimento e baixo consumo histórico é essencial para assegurar um equilíbrio entre a disponibilidade de estoque e as necessidades dos clientes.",
    "Resumidamente, é vital acompanhar os SKUs com risco de desabastecimento e baixo consumo histórico para garantir que a disponibilidade de estoque atenda à demanda dos clientes, mantendo um equilíbrio saudável entre ambos."
]