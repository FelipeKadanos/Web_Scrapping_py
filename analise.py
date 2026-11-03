def filtrar_produtos(produtos: list[dict], categoria: str) -> list[dict]:
    categoria_normalizada = categoria.strip().casefold()
    produtos_filtrados = []

    for produto in produtos:
        categoria_produto = produto["categoria"]
        if categoria_produto is not None:
            categoria_produto_normalizada = categoria_produto.strip().casefold()
            if categoria_produto_normalizada == categoria_normalizada:
                produtos_filtrados.append(produto)
    return produtos_filtrados

def calcular_resumo(produtos_filtrados: list[dict]) -> dict:
    quantidade = len(produtos_filtrados)
    produtos_com_preco = []

    for produto in produtos_filtrados:
        if produto["preco"] is not None:
            produtos_com_preco.append(produto)

    produto_mais_barato = None

    for produto in produtos_com_preco:
        if produto_mais_barato is None or produto["preco"] < produto_mais_barato["preco"]:
            produto_mais_barato = produto

    produto_mais_caro = None

    for produto in produtos_com_preco:
        if produto_mais_caro is None or produto["preco"] > produto_mais_caro["preco"]:
            produto_mais_caro = produto

    preco_medio = None

    if produtos_com_preco:
        soma_precos = 0

        for produto in produtos_com_preco:
            soma_precos += produto["preco"]

        preco_medio = soma_precos / len(produtos_com_preco)

    produto_melhor_avaliado = None

    for produto in produtos_filtrados:
        if produto["avaliacao"] is not None:
            if produto_melhor_avaliado is None or produto["avaliacao"] > produto_melhor_avaliado["avaliacao"]:
                produto_melhor_avaliado = produto

    return {
        "quantidade": quantidade,
        "produto_mais_barato": produto_mais_barato,
        "produto_mais_caro": produto_mais_caro,
        "preco_medio": preco_medio,
        "produto_melhor_avaliado": produto_melhor_avaliado,
    }