import time

from flask import Flask, render_template, request

from analise import calcular_resumo, filtrar_produtos
from scraper import coletar_produtos


app = Flask(__name__)
CACHE_TTL = 300
_produtos_cache = None
_cache_expira_em = 0.0


def _obter_produtos():
    global _produtos_cache, _cache_expira_em

    agora = time.monotonic()
    if _produtos_cache is not None and agora < _cache_expira_em:
        return _produtos_cache

    produtos = coletar_produtos()
    _produtos_cache = produtos
    _cache_expira_em = agora + CACHE_TTL
    return produtos


def _categorias_disponiveis(produtos):
    categorias = {}
    for produto in produtos:
        categoria = produto.get("categoria")
        if categoria and categoria.strip():
            texto = categoria.strip()
            categorias.setdefault(texto.casefold(), texto)
    return sorted(categorias.values(), key=str.casefold)


def _dados_iniciais(categorias=None, categoria_selecionada="", erro=None):
    return {
        "categorias": categorias or [],
        "categoria_selecionada": categoria_selecionada,
        "produtos": [],
        "resumo": None,
        "pesquisa_realizada": False,
        "erro": erro,
    }


@app.route("/", methods=["GET", "POST"])
def inicio():
    dados = _dados_iniciais()

    try:
        produtos = _obter_produtos()
        dados["categorias"] = _categorias_disponiveis(produtos)
    except RuntimeError as erro:
        dados["erro"] = f"Não foi possível coletar os produtos: {erro}"
        return render_template("index.html", **dados)

    if request.method == "POST":
        categoria = request.form.get("categoria", "").strip()
        dados["categoria_selecionada"] = categoria

        categoria_valida = next(
            (opcao for opcao in dados["categorias"] if opcao.casefold() == categoria.casefold()),
            None,
        )
        if not categoria:
            dados["erro"] = "Selecione uma categoria para pesquisar."
        elif categoria_valida is None:
            dados["erro"] = "A categoria selecionada não está disponível."
        else:
            dados["categoria_selecionada"] = categoria_valida
            dados["produtos"] = filtrar_produtos(produtos, categoria_valida)
            dados["resumo"] = calcular_resumo(dados["produtos"])
            dados["pesquisa_realizada"] = True

    return render_template("index.html", **dados)


if __name__ == "__main__":
    app.run(debug=True)
