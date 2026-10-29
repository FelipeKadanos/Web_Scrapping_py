# Catálogo de Produtos com Web Scraping

Guia de escopo e colaboração para os quatro integrantes e suas IAs.

**Status: projeto planejado, ainda não implementado.** A estrutura, os contratos e os comandos abaixo descrevem a entrega esperada. Este documento deve acompanhar o código na raiz do novo repositório.

**Objetivo: entregar a solução mais simples que cumpra todos os requisitos avaliados pelo professor.** Código simples, funcionamento correto e compreensão pelos integrantes têm prioridade. Não há garantia de nota.

## Regra obrigatória para as IAs

> Implemente exclusivamente a tarefa atribuída ao integrante neste card. Altere somente os arquivos necessários à sua responsabilidade e autorizados na tarefa. Não implemente tarefas de outros integrantes, não antecipe etapas e não faça melhorias, refatorações ou correções fora da tarefa.
>
> Se faltar uma parte de outro integrante, informe a dependência e pare no limite da sua tarefa. Não crie uma implementação substituta. Se precisar alterar um arquivo compartilhado ou um contrato de integração, explique a necessidade ao integrante e aguarde a combinação antes de fazê-lo.
>
> Priorize a solução mais simples que atenda aos requisitos do professor. Não adicione funcionalidades, bibliotecas, camadas de arquitetura ou arquivos sem necessidade para a entrega. O código deve ser curto, legível e compreensível pelos alunos.
>
> Ao finalizar, informe o que foi alterado, como foi verificado e quais dependências permanecem pendentes. Não continue com outras tarefas.

**Sem integrante, card e arquivos autorizados identificados, a IA deve pedir essas informações antes de escrever código.** Este README descreve o projeto inteiro para dar contexto; não autoriza uma IA a implementar o projeto inteiro.

## 1. Objetivo e requisitos do professor

A aplicação permitirá escolher uma categoria, coletará produtos de <https://scrapingsandbox.com/>, filtrará os dados em Python e apresentará os resultados no navegador.

O enunciado original está em [requisitos.md](requisitos.md) e é a referência para as exigências do professor. As seções seguintes detalham decisões do grupo para cumprir essas exigências com o mínimo de complexidade. Se surgir conflito, sinalize-o ao integrante antes de mudar o escopo.

Entrega obrigatória:

- Flask com formulário HTML, escolha de categoria e botão “Pesquisar”.
- `requests` para acessar páginas e `BeautifulSoup` para interpretar HTML.
- Produtos reais coletados automaticamente, sem cadastro manual no código.
- Coleta em mais de uma página. Não é necessário coletar o site inteiro, mas deve haver dados suficientes para as análises e para demonstrar duas categorias.
- Identificação da categoria e filtragem em Python, depois da coleta. Não automatizar filtros ou cliques do site.
- Exibição de nome, preço, categoria, avaliação e link de cada produto, quando disponíveis.
- Análises somente dos produtos da categoria escolhida: quantidade, produto de menor preço, produto de maior preço, preço médio e produto com melhor avaliação disponível.
- Resultados em HTML/Jinja, e não somente no terminal.
- Arquivos necessários para executar e demonstrar a aplicação.

Fluxo esperado:

```text
Formulário → Flask → coleta → filtro em Python → cálculos → HTML/Jinja
```

## 2. Decisões de simplicidade do grupo

- Python 3.11 ou superior.
- Dependências diretas: `Flask`, `requests` e `beautifulsoup4`.
- Uma rota, três módulos Python e um template.
- Funções simples e dicionários; sem arquitetura em camadas, classes ou abstrações sem necessidade.
- Uma página com formulário, resumo e tabela. CSS mínimo no próprio HTML.
- Execução local, sem cache ou persistência.
- Comentários curtos onde ajudarem a explicar coleta, paginação e cálculos.
- Verificações manuais e chamadas isoladas das funções são suficientes; não é necessário criar infraestrutura de testes.

Fora do escopo: login, cadastro, banco de dados, gráficos, exportações, API separada, frameworks frontend, JavaScript de interface, Selenium, Playwright, Pandas, Docker, deploy e design sofisticado. Não adicionar essas funcionalidades “para melhorar” o trabalho.

Estrutura prevista na raiz do novo repositório:

```text
README.md
requisitos.md
requirements.txt
.gitignore
app.py
scraper.py
analise.py
templates/
    index.html
```

O ambiente `.venv/` é local e não deve entrar no Git. A pessoa 3 deverá incluir `.venv/`, `__pycache__/` e `*.pyc` no `.gitignore`.

## 3. Contratos de integração

Estes nomes e formatos devem ser respeitados por todos. Não renomear funções, campos ou variáveis de template unilateralmente.

### 3.1. Coleta — `scraper.py`

Interface pública:

```python
def coletar_produtos() -> list[dict]:
    ...
```

Cada produto terá todas as chaves abaixo:

| Chave | Tipo | Significado |
| --- | --- | --- |
| `nome` | `str` ou `None` | Nome encontrado no site |
| `preco` | `float` ou `None` | Preço numérico, sem símbolo de moeda |
| `categoria` | `str` ou `None` | Categoria identificada no site |
| `avaliacao` | `float` ou `None` | Avaliação numérica disponível |
| `link` | `str` | URL absoluta do produto |

Exemplo apenas do formato, não para alimentar a aplicação real:

```python
{
    "nome": "Produto de exemplo",
    "preco": 99.90,
    "categoria": "Categoria de exemplo",
    "avaliacao": None,
    "link": "https://example.com/produto"
}
```

Responsabilidades da coleta:

- Inspecionar o HTML real antes de escolher seletores, endereços e mecanismo de paginação. Não inventar categorias ou URLs.
- Acessar pelo menos duas páginas distintas de produtos; aumentar a cobertura se necessário para demonstrar duas categorias com dados.
- Retornar a coleção coletada antes de qualquer filtro pela categoria escolhida pelo usuário.
- Converter preços e avaliações para números, respeitando o formato encontrado no site. Valor ausente é `None`, nunca zero inventado.
- Transformar links relativos em absolutos e eliminar duplicações pelo link.
- Usar timeout de 20 segundos por requisição e verificar erros HTTP.
- Em falha de rede, HTTP ou interpretação que impeça a coleta, lançar `RuntimeError` com uma mensagem compreensível. Não retornar uma coleção parcial como se a coleta estivesse completa.
- Não importar Flask nem produzir HTML.

A moeda deve ser confirmada durante a inspeção do site e comunicada à pessoa 4. Não presumir reais nem realizar conversão monetária. Não misturar moedas em uma mesma análise.

### 3.2. Filtro e cálculos — `analise.py`

Interfaces públicas:

```python
def filtrar_produtos(produtos: list[dict], categoria: str) -> list[dict]:
    ...

def calcular_resumo(produtos_filtrados: list[dict]) -> dict:
    ...
```

O filtro compara a categoria inteira após `strip()` e `casefold()`, sem alterar os textos originais. Produtos sem categoria não correspondem a uma categoria selecionada. Não usar correspondência parcial.

O resumo terá exatamente estas chaves:

```python
{
    "quantidade": 0,
    "produto_mais_barato": None,
    "produto_mais_caro": None,
    "preco_medio": None,
    "produto_melhor_avaliado": None
}
```

Regras:

- `quantidade` conta todos os produtos filtrados.
- `produto_mais_barato` e `produto_mais_caro` contêm o dicionário completo do produto correspondente, ou `None` se não houver preços disponíveis.
- `preco_medio` considera apenas produtos com preço disponível. Retorna número ou `None`; a formatação de duas casas fica no HTML.
- `produto_melhor_avaliado` contém o produto completo com maior avaliação disponível, ou `None`.
- Em empates, retornar o primeiro produto na ordem da lista.
- Lista vazia retorna o resumo acima, sem divisão por zero.
- Zero é valor numérico válido; não confundir com `None`.
- Não modificar os produtos recebidos, acessar a rede ou importar Flask.

### 3.3. Coordenação — `app.py`

Usar apenas a rota `/`, com métodos `GET` e `POST`, e o campo de formulário `categoria`.

No `GET`:

1. Chamar `coletar_produtos()` para obter as categorias disponíveis.
2. Montar uma lista ordenada de categorias únicas e não vazias, desconsiderando diferenças de maiúsculas/minúsculas e espaços externos.
3. Renderizar a página inicial sem exibir uma pesquisa como concluída.

No `POST`:

1. Receber `categoria` por `request.form`.
2. Realizar nova coleta e reconstruir as opções de categoria.
3. Validar que a categoria foi informada e corresponde a uma opção disponível.
4. Chamar `filtrar_produtos()` e depois `calcular_resumo()`.
5. Renderizar os resultados na mesma página, mantendo a categoria selecionada.

Não duplicar no Flask a lógica de scraping ou de cálculos. Usar `render_template()` e capturar o `RuntimeError` da coleta para mostrar uma mensagem na página. Categoria ausente ou inválida também gera mensagem, sem calcular resultados.

Enviar sempre estas variáveis ao template:

| Variável | Tipo / estado inicial |
| --- | --- |
| `categorias` | Lista de textos; `[]` se indisponível |
| `categoria_selecionada` | Texto; `""` inicialmente |
| `produtos` | Lista filtrada; `[]` inicialmente ou em erro |
| `resumo` | Dicionário de resumo; `None` antes de pesquisa bem-sucedida |
| `pesquisa_realizada` | `True` após pesquisa bem-sucedida, inclusive sem produtos; `False` inicialmente ou em erro |
| `erro` | Mensagem em texto ou `None` |

Se a coleta falhar, não apresentar produtos ou análises como resultados válidos. Permitir tentar novamente recarregando a página.

### 3.4. Interface — `templates/index.html`

- Formulário com `method="post"`, destino `/`, `<select name="categoria">` e botão “Pesquisar”.
- Opções geradas a partir de `categorias`, sem cadastrar categorias fictícias.
- Título visível e layout simples, com CSS mínimo no próprio arquivo.
- Exibição de `erro` quando existir.
- Resumo e resultados somente quando `pesquisa_realizada` for verdadeiro.
- Exibição da categoria pesquisada e dos cinco resultados exigidos. Menor preço, maior preço e melhor avaliação devem identificar o produto e seu valor.
- Tabela com nome, preço, categoria, avaliação e link clicável.
- Campos ausentes apresentados como “Não disponível”, preservando valores iguais a zero.
- Preços com duas casas decimais e identificação da moeda confirmada no site.
- Mensagem “Nenhum produto encontrado” para pesquisa bem-sucedida com lista vazia; não mostrá-la na abertura inicial.
- Sem cálculos de negócio no template; usar os valores recebidos do Flask.

## 4. Divisão de tarefas

| Integrante | Responsabilidade | Arquivos da tarefa principal |
| --- | --- | --- |
| Pessoa 1 | Coleta, campos e paginação | `scraper.py` |
| Pessoa 2 | Filtragem e cálculos | `analise.py` |
| Pessoa 3 | Flask, dependências e execução | `app.py`, `requirements.txt`, `.gitignore` |
| Pessoa 4 | Formulário e apresentação dos resultados | `templates/index.html` |

Substituir os rótulos pelos nomes do grupo quando definidos. As pessoas podem desenvolver em paralelo respeitando os contratos, mas a execução completa depende de todas as entregas.

A integração será um card explícito da pessoa 3 após as entregas individuais. Esse card deve indicar os arquivos autorizados. Ser responsável pela integração não autoriza sua IA a implementar antecipadamente o trabalho das outras pessoas.

Validação final: pessoas 1 e 2 conferem coleta e cálculos; pessoas 3 e 4 conferem execução e interface. Todos participam da demonstração e devem entender o fluxo completo.

## 5. Fluxo de colaboração e Trello

Listas sugeridas: **A fazer → Fazendo → Revisão → Concluído**.

Cada card deve conter responsável, objetivo, arquivos autorizados, dependências e critério de conclusão. A IA recebe somente autorização para o card informado.

1. Atualizar a cópia local a partir da `main` antes de iniciar.
2. Criar uma branch por tarefa, por exemplo `feat/coleta-produtos`.
3. Implementar exclusivamente o card, com commits pequenos e descritivos.
4. Revisar o código gerado pela IA e executar as verificações possíveis da própria parte.
5. Abrir pull request para `main`, descrevendo o que mudou, o que foi verificado e eventuais dependências.
6. Revisar e integrar a entrega com o grupo.

Não enviar `.venv`, caches ou arquivos temporários. Não sobrescrever trabalho alheio nem fazer refatorações gerais durante uma tarefa específica.

Se um contrato precisar mudar, combinar com os integrantes afetados e registrar a decisão neste README antes da integração. A edição do README também deve estar autorizada no card correspondente.

## 6. Prompt para cada integrante copiar para sua IA

Preencha todos os campos antes de enviar:

```text
Você está colaborando em um trabalho acadêmico de quatro pessoas.

Integrante: [nome e número da pessoa]
Card: [título e descrição da tarefa]
Arquivos autorizados: [lista exata]
Critério de conclusão: [resultado verificável]
Dependências conhecidas: [partes necessárias de outros integrantes]

Leia README.md, requisitos.md e o código existente relacionado à tarefa.
O README dá contexto do projeto inteiro, mas sua autorização se limita ao card acima.
Se integrante, tarefa ou arquivos autorizados não estiverem identificados, peça
essas informações antes de escrever código.

Implemente exclusivamente a tarefa atribuída ao integrante neste card. Altere
somente os arquivos necessários à sua responsabilidade e autorizados na tarefa.
Não implemente tarefas de outros integrantes, não antecipe etapas e não faça
melhorias, refatorações ou correções fora da tarefa.

Se faltar uma parte de outro integrante, informe a dependência e pare no limite
da sua tarefa. Não crie uma implementação substituta. Se precisar alterar um
arquivo compartilhado ou um contrato de integração, explique a necessidade ao
integrante e aguarde a combinação antes de fazê-lo.

Priorize a solução mais simples que atenda aos requisitos do professor. Não
adicione funcionalidades, bibliotecas, camadas de arquitetura ou arquivos sem
necessidade para a entrega. O código deve ser curto, legível e compreensível
pelos alunos. Respeite os nomes e formatos definidos no README.

Não cadastre produtos fictícios na aplicação real. Exemplos artificiais são
permitidos apenas em verificações isoladas, nunca como substitutos da coleta.
Não presuma seletores, categorias ou URLs do site sem verificá-los quando essa
inspeção fizer parte da sua tarefa.

Verifique o que for possível da sua parte sem implementar partes alheias.
Não afirme ter executado testes que não executou.

Ao finalizar, informe o que foi alterado, como foi verificado e quais dependências
permanecem pendentes. Não continue com outras tarefas.
```

## 7. Instalação e execução previstas

Estes comandos serão utilizáveis quando os módulos, o template e o arquivo de dependências estiverem implementados e integrados. Executar na raiz do novo repositório, que deverá ter seu próprio ambiente virtual.

Conteúdo previsto de `requirements.txt`:

```text
Flask
requests
beautifulsoup4
```

Windows / PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

A pessoa 3 deverá configurar `app.py` para iniciar o servidor local ao executar o arquivo diretamente. Acessar `http://127.0.0.1:5000/` no navegador. É necessário acesso à internet para a coleta. Encerrar o servidor com `Ctrl+C`.

## 8. Checklist de entrega e apresentação

- [ ] Um clone do repositório funciona com ambiente virtual novo seguindo este README.
- [ ] A página inicial apresenta título, categorias e botão de pesquisa.
- [ ] Os produtos são obtidos do site real usando requests e BeautifulSoup.
- [ ] A coleta acessa pelo menos duas páginas distintas e não duplica produtos.
- [ ] Há dados suficientes para pesquisar e demonstrar duas categorias diferentes.
- [ ] A categoria é filtrada em Python depois da coleta.
- [ ] Os resultados não misturam categorias.
- [ ] Nome, preço, categoria, avaliação e link aparecem quando disponíveis.
- [ ] Quantidade, menor preço, maior preço, média e melhor avaliação estão corretos e foram conferidos manualmente.
- [ ] Produtos de menor/maior preço e melhor avaliação são identificados no resumo.
- [ ] Valores ausentes, valores zero, empates e lista vazia são tratados corretamente.
- [ ] Falha de rede gera mensagem compreensível, sem resultados parciais apresentados como completos.
- [ ] É possível realizar outra pesquisa na mesma página.
- [ ] O código entregue contém somente o necessário ao trabalho.
- [ ] Todos os integrantes revisaram e conseguem explicar sua parte e o fluxo geral.

Roteiro de demonstração: iniciar o Flask, abrir o navegador, pesquisar uma categoria, mostrar produtos e cálculos, pesquisar outra categoria e explicar coleta, paginação, filtro e análise. Cada integrante deve estar preparado para explicar trechos do código e fazer uma pequena alteração solicitada pelo professor.
