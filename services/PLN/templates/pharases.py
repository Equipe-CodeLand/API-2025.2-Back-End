templates_risco = {
    "alto_risco": [
        "O {sku} com seu risco de desabastecimento {risco}, necessário atenção imediata.",
        "O {sku} apresenta um cenário preocupante de risco elevado de desabastecimento, categorizado como {risco}.",
        "O risco de desabastecimento do {sku} é {risco}, exigindo monitoramento constante.",
        "O {sku} está classificado com {risco} para seu desabastecimento, o que demanda ações preventivas.",
        "Há um risco crítico de desabastecimento para o {sku}, classificado como {risco}, exigindo pronta intervenção.",
        "O {sku} encontra-se em condição de alto risco {risco}, podendo comprometer a disponibilidade futura.",
        "O {sku} apresenta {risco}, tornando necessária a priorização de medidas corretivas.",
        "A classificação de {risco} para o {sku} reforça a urgência de estratégias preventivas."
    ],
    "medio_risco": [
        "O {sku} apresenta um risco moderado de desabastecimento, classificado como {risco}.",
        "O risco de desabastecimento do {sku} é {risco}, sugerindo a necessidade de atenção regular.",
        "O {sku} está em uma situação de risco categorizado como {risco} para desabastecimento.",
        "O {sku} possui um risco de desabastecimento {risco}, o que requer monitoramento periódico.",
        "A condição de risco {risco} do {sku} não é crítica, mas requer acompanhamento contínuo.",
        "O {sku} encontra-se em nível intermediário de risco {risco}, merecendo planejamento preventivo.",
        "A classificação {risco} do {sku} demanda medidas de acompanhamento sem urgência imediata.",
        "O risco de desabastecimento do {sku}, classificado como {risco}, sugere atenção preventiva."
    ],
    "baixo_risco": [
        "O {sku} mantém uma posição estável, com risco de desabastecimento {risco}.",
        "O risco de desabastecimento para o {sku} não é preocupante, atualmente classificado como {risco}.",
        "O {sku} apresenta um risco de desabastecimento {risco}, indicando uma situação controlada.",
        "O {sku} está em uma condição segura, com risco de desabastecimento {risco}.",
        "O {sku} encontra-se em situação confortável, apresentando {risco}.",
        "O risco {risco} do {sku} demonstra equilíbrio entre estoque e demanda.",
        "O {sku} apresenta uma condição estável, com {risco}, sem necessidade de ações urgentes.",
        "Com {risco}, o {sku} mantém estabilidade em termos de disponibilidade de estoque."
    ],
    "sem_consumo": [
        "O {sku} não apresentou consumo, o que pode indicar obsolescência ou baixa relevância.",
        "Observa-se que o {sku} permaneceu sem consumo histórico recente.",
        "O {sku} não teve movimentação de estoque no período analisado.",
        "Nenhum consumo foi registrado para o {sku}",
        "O {sku} está inativo, sem registros de saída no período considerado.",
        "Durante a análise, o {sku} não demonstrou qualquer movimentação de consumo.",
        "O {sku} permaneceu estagnado em estoque, sem registros de utilização.",
        "Não houve consumo identificado para o {sku}, sugerindo possível excesso de estoque."
    ]
}

templates_resumo = [
    "No período, o conjunto de SKUs analisados apresentou um consumo total de {total_consumo:.2f} toneladas, com uma frequência média de compra de {freq_media:.1f} meses e um aging médio do estoque de {aging_medio:.1f} semanas.",
    "Durante o intervalo analisado, os SKUs tiveram um consumo agregado de {total_consumo:.2f} toneladas, com frequência média de compra de {freq_media:.1f} meses e aging médio do estoque de {aging_medio:.1f} semanas.",
    "Ao longo do período, o consumo total dos SKUs foi de {total_consumo:.2f} toneladas, apresentando uma frequência média de compra de {freq_media:.1f} meses e um aging médio do estoque de {aging_medio:.1f} semanas.",
    "No intervalo considerado, os SKUs analisados consumiram um total de {total_consumo:.2f} toneladas, com frequência média de compra de {freq_media:.1f} meses e aging médio do estoque de {aging_medio:.1f} semanas.",
    "O balanço do período mostra que os SKUs registraram consumo total de {total_consumo:.2f} toneladas, frequência média de compra em {freq_media:.1f} meses e aging médio de {aging_medio:.1f} semanas.",
    "O consolidado da análise aponta {total_consumo:.2f} toneladas consumidas, com frequência de compra média de {freq_media:.1f} meses e aging médio de {aging_medio:.1f} semanas.",
    "Considerando os SKUs avaliados, o consumo chegou a {total_consumo:.2f} toneladas, frequência média de compra de {freq_media:.1f} meses e aging médio de {aging_medio:.1f} semanas.",
    "No período avaliado, o consumo agregado dos SKUs foi de {total_consumo:.2f} toneladas, acompanhado de uma frequência média de {freq_media:.1f} meses e aging médio de {aging_medio:.1f} semanas."
]


templates_consumo = {
    "consumo": [
        "O {sku} teve consumo de {consumo:.2f} toneladas",
        "Durante o período, o {sku} apresentou um consumo de {consumo:.2f} toneladas",
        "No intervalo analisado, o {sku} consumiu {consumo:.2f} toneladas de estoque",
        "O {sku} registrou um consumo de {consumo:.2f} toneladas",
        "O consumo do {sku} atingiu {consumo:.2f} toneladas ao longo do período",
        "O {sku} movimentou {consumo:.2f} toneladas em consumo",
        "Foram consumidas {consumo:.2f} toneladas do {sku} durante o período analisado",
        "O total consumido do {sku} foi de {consumo:.2f} toneladas"
    ],
    "frequencia_compra": [
        "com uma frequência de compra de {frequencia:.1f} meses no período analisado",
        "apresentando uma frequência média de compra de {frequencia:.1f} meses no intervalo considerado",
        "com frequência de compra estimada em {frequencia:.1f} meses durante o período",
        "registrando uma frequência de compra de {frequencia:.1f} meses dentro do intervalo analisado",
        "sendo sua frequência de compra de {frequencia:.1f} meses",
        "com intervalo médio de compras de {frequencia:.1f} meses",
        "mantendo uma frequência de compra de {frequencia:.1f} meses",
        "alcançando uma frequência de compra de {frequencia:.1f} meses"
    ],
    "aging_estoque": [
        "O {sku} apresentou um aging médio do estoque de {aging:.1f} semanas",
        "Se tratando do {sku}, o estoque possui um aging médio calculado em {aging:.1f} semanas",
        "O {sku} atualmente possui um aging médio do estoque de {aging:.1f} semanas",
        "Considerando o {sku}, seu aging médio do estoque está estimado em {aging:.1f} semanas",
        "O aging médio do estoque do {sku} foi de {aging:.1f} semanas",
        "O {sku} permaneceu em estoque, por {aging:.1f} semanas",
        "O tempo médio em estoque do {sku} foi calculado em {aging:.1f} semanas",
        "O {sku} teve aging registrado em {aging:.1f} semanas"
    ],
    "n_clientes": [
        "sendo consumido por {n_clientes} clientes distintos",
        "com um total de {n_clientes} clientes distintos que o consomem",
        "também é requisitado por {n_clientes} clientes distintos",
        "contando com {n_clientes} clientes distintos em seu consumo"
    ]
}

templates_conclusao = [
    "De forma geral, o cenário demonstra a importância de acompanhar de perto os SKUs com risco de desabastecimento e aqueles com baixo consumo histórico, garantindo o equilíbrio entre disponibilidade de estoque e demanda dos clientes.",
    "Em resumo, é crucial monitorar os SKUs com risco de desabastecimento e aqueles com baixo consumo histórico para manter um equilíbrio adequado entre a disponibilidade de estoque e a demanda dos clientes.",
    "Concluindo, a gestão eficaz dos SKUs com risco de desabastecimento e baixo consumo histórico é essencial para assegurar um equilíbrio entre a disponibilidade de estoque e as necessidades dos clientes.",
    "Resumidamente, é vital acompanhar os SKUs com risco de desabastecimento e baixo consumo histórico para garantir que a disponibilidade de estoque atenda à demanda dos clientes, mantendo um equilíbrio saudável entre ambos.",
    "A análise reforça a necessidade de estratégias de monitoramento contínuo, sobretudo para SKUs críticos e com baixa movimentação, a fim de equilibrar estoque e consumo.",
    "Manter o controle sobre itens com risco e baixo giro é fundamental para evitar excessos ou rupturas, assegurando a eficiência do estoque.",
    "A gestão equilibrada entre consumo e risco de desabastecimento deve ser prioridade para assegurar disponibilidade e evitar perdas.",
    "Em linhas gerais, o acompanhamento de SKUs críticos e de baixo consumo é peça-chave para alinhar a oferta de estoque com a demanda efetiva."
]