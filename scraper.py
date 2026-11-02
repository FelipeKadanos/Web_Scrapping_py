"""Coleta de produtos reais de https://scrapingsandbox.com/ (card 1).

O site pagina a listagem só com JavaScript (a URL não muda ao trocar de
página), então o requests não consegue percorrê-la. Por decisão do grupo,
cada página de produto (/product/1, /product/2, ...) é acessada e lida.
Os preços do site aparecem com o símbolo "$".
"""
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://scrapingsandbox.com"
TIMEOUT = 20           # segundos por requisição
TOTAL_PRODUTOS = 40    # coleta os produtos de id 1 até 40
PAUSA = 0.2            # o site aceita 60 requisições a cada 10 segundos


def _texto(soup, seletor):
    """Texto do primeiro elemento que casa com o seletor, ou None."""
    tag = soup.select_one(seletor)
    return tag.get_text(strip=True) if tag else None


def _numero(texto):
    """Converte '$107.53' em 107.53. Retorna None se não houver número."""
    try:
        return float(texto.replace("$", "").replace(",", "").strip())
    except (AttributeError, ValueError):
        return None


def _interpretar_produto(html, link):
    """Lê uma página de produto e devolve o dicionário do contrato."""
    soup = BeautifulSoup(html, "html.parser")
    return {
        "nome": _texto(soup, "h1"),
        "preco": _numero(_texto(soup, "span.text-3xl")),
        "categoria": _texto(soup, 'span[data-slot="badge"][data-variant="secondary"]'),
        "avaliacao": _numero(_texto(soup, "span.font-semibold")),
        "link": link,
    }


def coletar_produtos() -> list[dict]:
    """Retorna os produtos do site (nome, preco, categoria, avaliacao, link).

    Lança RuntimeError se alguma página não puder ser acessada ou lida.
    """
    produtos = []
    with requests.Session() as sessao:
        for id_produto in range(1, TOTAL_PRODUTOS + 1):
            link = f"{BASE_URL}/product/{id_produto}"  # um link por id: sem duplicados
            try:
                resposta = sessao.get(link, timeout=TIMEOUT)
                resposta.raise_for_status()
            except requests.RequestException as erro:
                raise RuntimeError(f"Falha ao acessar {link}: {erro}") from erro

            produto = _interpretar_produto(resposta.text, link)
            if produto["nome"] is None:
                raise RuntimeError(f"Não foi possível ler {link}: o HTML do site pode ter mudado.")
            produtos.append(produto)
            time.sleep(PAUSA)
    return produtos
