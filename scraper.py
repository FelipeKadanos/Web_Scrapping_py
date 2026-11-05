"""Coleta de produtos reais de https://scrapingsandbox.com/ (card 1).

O site pagina a listagem só com JavaScript (a URL não muda ao trocar de
página), então o requests não consegue percorrê-la. Por decisão do grupo,
cada página de produto (/product/1, /product/2, ...) é acessada e lida.
Os preços do site aparecem com o símbolo "$".
"""
import time

import requests
from bs4 import BeautifulSoup

# URL base usada para montar os links dos produtos.
BASE_URL = "https://scrapingsandbox.com"
TIMEOUT = 20           # segundos por requisição
TOTAL_PRODUTOS = 40    # coleta os produtos de id 1 até 40
PAUSA = 0.2            # o site aceita 60 requisições a cada 10 segundos


# Procura o elemento no HTML de seletor e retorna seu texto. Retorna None se não encontrar.
def _texto(soup, seletor):
    tag = soup.select_one(seletor) # .select_one() retorna o primeiro elemento com o seletor fonecido. Procura HTML e CSS
    return tag.get_text(strip=True) if tag else None


# Os valores são convertidos para float para que possam ser usados nos cálculos.
# Converte '$107.53' em 107.53. Retorna None se não houver número
def _numero(texto):
    try:
        return float(texto.replace("$", "").replace(",", "").strip())
    except (AttributeError, ValueError):
        return None


# Lê uma página de produto e devolve o dicionário do no formato que esperamos para outros módulos
def _interpretar_produto(html, link):
    soup = BeautifulSoup(html, "html.parser") # PERGUNTA: O que html.parser faz?
    return {
        "nome": _texto(soup, "h1"),
        "preco": _numero(_texto(soup, "span.text-3xl")),
        "categoria": _texto(soup, 'span[data-slot="badge"][data-variant="secondary"]'),
        "avaliacao": _numero(_texto(soup, "span.font-semibold")),
        "link": link,
    }


# Retorna os produtos do site(nome, preco, categoria, avaliacao, link). 
# Retorna erro se não puder acessar alguma página ou ler o HTML.
def coletar_produtos() -> list[dict]: # O -> list[dict] indica que retorna uma lista de dicionários
    produtos = []
    with requests.Session() as sessao: # .Session() cria a conexão e mantem as informações (cookies e etc). O with fecha ela no final

        # O site apresenta os produtos em páginas individuais. Acessamos vários IDs para obter dados dos produtos.
        for id_produto in range(1, TOTAL_PRODUTOS + 1):
            link = f"{BASE_URL}/product/{id_produto}"  # um link por id: sem duplicados
            try:
                resposta = sessao.get(link, timeout=TIMEOUT) # Tentamos acessar a página do produto. timeout=: Limite de tempo para a requisição. TIMEOUT foi defindo acima com 20 seg
                resposta.raise_for_status() # PERGUNTA: O que o .raise_for_status() faz?

            except requests.RequestException as erro:
                # Caso ocorra algum erro, retornamos erro para não retornarmos uma lista parcial como se estivesse completa.
                # Não podemos continuar apenas com uma lista parcial pois precisamos de dados o suficientes para calcular o resumo da categoria
                raise RuntimeError(f"Falha ao acessar {link}: {erro}") from erro

            produto = _interpretar_produto(resposta.text, link)
            
            if produto["nome"] is None: # Usamos nome para verificar se a página foi lida
                raise RuntimeError(f"Não foi possível ler {link}: o HTML do site pode ter mudado.")

            produtos.append(produto) # Add produto à lista de produtos coletados
            time.sleep(PAUSA) # ***IMPORTANTE***: Fazemos uma pausa pois o site so aceita 60 requisições a cada 10 segundos 

    return produtos
