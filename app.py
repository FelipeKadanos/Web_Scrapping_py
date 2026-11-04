import time

# Flask cria a aplicação web, render_template envia os dados para o HTML
# e request permite ler a categoria enviada pelo formulário.
from flask import Flask, render_template, request

from analise import calcular_resumo, filtrar_produtos
from scraper import coletar_produtos


app = Flask(__name__)

# O cache evita repetir as 40 requisições do scraper em toda pesquisa.
# Os produtos ficam disponíveis por cinco minutos enquanto o servidor estiver ativo.
CACHE_TTL = 300
_produtos_cache = None
_cache_expira_em = 0.0


def _obter_produtos():
    # Variáveis globais são usadas porque o cache precisa ser compartilhado
    # entre as chamadas da rota durante a execução do servidor.
    global _produtos_cache, _cache_expira_em

    agora = time.monotonic()

    # Se ainda existe uma coleta válida, reutilizamos os dados já obtidos.
    if _produtos_cache is not None and agora < _cache_expira_em:
        return _produtos_cache

    # O cache só é atualizado depois que a coleta termina com sucesso.
    produtos = coletar_produtos()
    _produtos_cache = produtos
    _cache_expira_em = agora + CACHE_TTL
    return produtos


def _categorias_disponiveis(produtos):
    # As categorias são obtidas dos produtos reais, sem cadastro manual.
    categorias = {}
    for produto in produtos:
        categoria = produto.get("categoria")
        if categoria and categoria.strip():
            texto = categoria.strip()

            # O dicionário elimina duplicidades ignorando maiúsculas/minúsculas,
            # mas preserva o primeiro texto encontrado para exibição.
            categorias.setdefault(texto.casefold(), texto)

    # A ordenação facilita a localização da categoria no formulário.
    return sorted(categorias.values(), key=str.casefold)


def _dados_iniciais(categorias=None, categoria_selecionada="", erro=None):
    # Esses são os valores enviados ao template antes de uma pesquisa válida
    # ou quando ocorre uma falha durante a coleta.
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
    # A mesma página atende tanto a abertura inicial quanto as pesquisas.
    dados = _dados_iniciais()

    try:
        produtos = _obter_produtos()
        dados["categorias"] = _categorias_disponiveis(produtos)
    except RuntimeError as erro:
        # A aplicação mostra o problema no HTML em vez de exibir resultados incompletos.
        dados["erro"] = f"Não foi possível coletar os produtos: {erro}"
        return render_template("index.html", **dados)

    if request.method == "POST":
        # O formulário usa o campo categoria para informar a escolha do usuário.
        categoria = request.form.get("categoria", "").strip()
        dados["categoria_selecionada"] = categoria

        # A comparação ignora diferenças de maiúsculas/minúsculas,
        # mas a categoria exibida continua com o texto original coletado.
        categoria_valida = next(
            (opcao for opcao in dados["categorias"] if opcao.casefold() == categoria.casefold()),
            None,
        )
        if not categoria:
            dados["erro"] = "Selecione uma categoria para pesquisar."
        elif categoria_valida is None:
            dados["erro"] = "A categoria selecionada não está disponível."
        else:
            # Primeiro filtramos os produtos e depois calculamos o resumo
            # somente sobre os produtos da categoria escolhida.
            dados["categoria_selecionada"] = categoria_valida
            dados["produtos"] = filtrar_produtos(produtos, categoria_valida)
            dados["resumo"] = calcular_resumo(dados["produtos"])
            dados["pesquisa_realizada"] = True

    return render_template("index.html", **dados)


if __name__ == "__main__":
    # Permite iniciar o servidor diretamente com: python app.py
    app.run(debug=True)
