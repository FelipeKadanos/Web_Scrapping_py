def filtrar_produtos(produtos: list[dict], categoria: str) -> list[dict]: # O -> list[dict] indica que a função retorna uma lista de dicionários

    # Ignoramos espaços e diferenças de maiúsculas/minúsculas
    categoria_normalizada = categoria.strip().casefold()
    produtos_filtrados = []

    for produto in produtos:

        if produto["categoria"] is not None:
            
            # Comparamos se a categoria do produto é igual à categoria escolhida
            if produto["categoria"].strip().casefold() == categoria_normalizada:
                produtos_filtrados.append(produto)

    return produtos_filtrados

def calcular_resumo(produtos_filtrados: list[dict]) -> dict: # O -> list[dict] indica que a função retorna uma lista de dicionários
    pdt_mais_barato = None
    pdt_mais_caro = None
    pdt_melhor_avaliado = None

    soma_precos = 0
    qtd_com_preco = 0

    for pdt in produtos_filtrados:

        # Preços ausentes não entram nos cálculos.
        if pdt["preco"] is not None:
            soma_precos += pdt["preco"]
            qtd_com_preco += 1

            if pdt_mais_barato is None or pdt["preco"] < pdt_mais_barato["preco"]:
                pdt_mais_barato = pdt # Pra cada pdt com preço, se o preço dele for menor que o atual menor preço, ele se torna o menor preço

            if pdt_mais_caro is None or pdt["preco"] > pdt_mais_caro["preco"]:
                pdt_mais_caro = pdt # Pra cada pdt com preço, se ele for maior que o atual maior preço, ele se torna o maior preço

        if pdt["avaliacao"] is not None:
            if (pdt_melhor_avaliado is None or pdt["avaliacao"] > pdt_melhor_avaliado["avaliacao"]):
                pdt_melhor_avaliado = pdt # Se o pdt tem avaliação e ela for maior que a atual melhor avaliação, ele se torna o melhor avaliado

    preco_medio = None

    if qtd_com_preco > 0:
        preco_medio = soma_precos / qtd_com_preco

    return {
        "quantidade": len(produtos_filtrados),
        "produto_mais_barato": pdt_mais_barato,
        "produto_mais_caro": pdt_mais_caro,
        "preco_medio": preco_medio,
        "produto_melhor_avaliado": pdt_melhor_avaliado,
    }