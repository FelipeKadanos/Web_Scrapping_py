import time

# Flask cria a aplicação web, render_template envia dados para o HTML e request permite ler a categoria enviada pelo formulário.
from flask import Flask, render_template, request

from analise import calcular_resumo, filtrar_produtos
from scraper import coletar_produtos


# Flask(): Cria um objeto que representa a aplicação web.
# __name__: Variável do Python que guarda o modulo atual ( Nesse caso é "__main__")
# app: é a variável que guarda o objeto da aplicação web
app = Flask(__name__)

# Usamos cache em memória para não repetirmos a coleta de pdts toda requisição.
CACHE_TTL = 300 # Tempo de vida do cache em seg. 5 min
_produtos_cache = None # Guarda os pdts coletados. "cache"
_cache_expira_em = 0.0 # Tempo em que o cache expira.


# Verifica se o cache ainda é valido, se não for faz uma nova coleta. Retorna os pdts coletados
def _obter_produtos():
    # Usamos variáveis globais para o cache ser acessivel por outras as funções.
    global _produtos_cache, _cache_expira_em

    agora = time.monotonic() # Retorna o tempo em seg desde que o PC foi ligado.

    # Se ainda existe cache válido, reutilizamos os dados já obtidos.
    if _produtos_cache is not None and agora < _cache_expira_em:
        return _produtos_cache

    # coletamos os dados para o cache
    produtos = coletar_produtos()
    _produtos_cache = produtos
    _cache_expira_em = agora + CACHE_TTL # Atualiza o tempo de expiração do cache

    return produtos


# Retorna a lista de categorias. A lista é em ordem alfabética e não tem duplicatas
def _categorias_disponiveis(produtos):
    categorias = {}
    for produto in produtos:
        categoria = produto.get("categoria")
        if categoria and categoria.strip():
            texto = categoria.strip()

            # setdefault(): Adiciona o par (chave e valor) ao dicionário se a chave não existir
            # casefold(): Retorna a string em letra minúscula
            categorias.setdefault(texto.casefold(), texto) # Pra cada pdt, se a categoria não esta na lista de categorias, adiciona ela.

    # sorted(): Retorna uma lista ordenada (o padrão é ordem alfabética/crescente). Para decresente use reverse=True
    # key=str.casefold: Ordena a lista ignorando diferenças de maiúsculas/minúsculas
    return sorted(categorias.values(), key=str.casefold)


# Retorna dados inicias para o template
def _dados_iniciais(categorias=None, categoria_selecionada="", erro=None): 
    return {
        "categorias": categorias or [],
        "categoria_selecionada": categoria_selecionada,
        "produtos": [],
        "resumo": None,
        "pesquisa_realizada": False,
        "erro": erro,
    }


# @app.route(): Diz ao Flask que a função inicio() deve ser chamada quando o usuário acessar a rota "/".
# methods=["GET", "POST"]: Diz que a função inicio() deve ser chamada para GET e POST.
@app.route("/", methods=["GET", "POST"]) 
def inicio():
    dados = _dados_iniciais()

    try:
        produtos = _obter_produtos()
        dados["categorias"] = _categorias_disponiveis(produtos)
    except RuntimeError as erro:
        # Caso aconteça algum erro exibimos ele na página inicial
        dados["erro"] = f"Não foi possível coletar os produtos: {erro}"
        return render_template("index.html", **dados) # render_template(): Carrega o template HTML e envia os dados para ele. **dados: Chaves viram variáveis usadas no template.

    if request.method == "POST": # No POST o unico dado é a categoria escolhida
        categoria = request.form.get("categoria", "").strip()
        dados["categoria_selecionada"] = categoria

        # Esse bloco existe para caso a categoria enviada não exista mais na lista de categorias.
        # next(): Retorna a primeira categoria que for igual a categoria escolhida. Se não encontrar retorna None
        categoria_valida = next( 
            (opcao for opcao in dados["categorias"] if opcao.casefold() == categoria.casefold()),
            None,
        )

        if not categoria:
            dados["erro"] = "Selecione uma categoria para pesquisar."
        elif categoria_valida is None:
            dados["erro"] = "A categoria selecionada não está disponível."
        else:
            # Filtramos os produtos e calculamos o resumo dos produtos da categoria escolhida.
            dados["categoria_selecionada"] = categoria_valida
            dados["produtos"] = filtrar_produtos(produtos, categoria_valida)
            dados["resumo"] = calcular_resumo(dados["produtos"])
            dados["pesquisa_realizada"] = True

    return render_template("index.html", **dados) # Os ** dizem para o python descompactar o dicionário, então cada chave equivale a uma variável no template.


app.run(debug=True)