# Catálogo de Produtos com Web Scraping

Aplicação web em Python que coleta produtos do [Scraping Sandbox](https://scrapingsandbox.com/), permite pesquisar por categoria e apresenta os resultados em uma tabela com um resumo de preços e avaliações.

> Utilizamos Cache para evitar a necessidade de pesquisar todos os produtos em toda requisição.

- **Flask:** aplicação web e renderização das páginas.
- **Requests:** acesso às páginas dos produtos.
- **Beautiful Soup:** extração dos dados do HTML.
- **HTML:** interface e apresentação dos resultados.
- **Cache:** utilizamos lista de dicionarios para guardar os dados do `cache`.

## Como executar

Você precisa de Python 3.9 ou superior.

### 1. Baixe o projeto

```bash
git clone https://github.com/FelipeKadanos/Web_Scrapping_py.git
cd Web_Scrapping_py
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

Se `python` não estiver disponível, tente `py` no Windows ou `python3` no Linux/macOS.

### 3. Instale as dependências e inicie a aplicação

No **Windows (PowerShell)**:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abra **http://127.0.0.1:5000** no navegador. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

## Atenção!
>O primeiro acesso pode demorar, pois a aplicação precisa coletar os produtos para o cache. O servidor é iniciado com `debug=True`, para desenvolvimento local.

## Como funciona

1. A aplicação consulta o cache. Se não houver dados válidos, inicia uma coleta.
2. O coletor acessa as páginas individuais dos produtos de ID 1 a 40 e extrai os dados do HTML.
3. As categorias encontradas são apresentadas no formulário.
4. Após a pesquisa, os produtos são filtrados e o resumo é calculado em uma única passagem pela lista filtrada.
5. Os resultados são enviados ao template HTML.

Os cálculos de preço ignoram valores ausentes. A média considera apenas produtos com preço disponível. Avaliações ausentes também são ignoradas. Em caso de empate, o primeiro produto encontrado é mantido.

## Estrutura do projeto

```text
Web_Scrapping_py/
├── templates/
│   └── index.html        # Formulário, resumo e tabela de produtos
├── .gitignore            # Arquivos ignorados no git
├── analise.py            # Filtro por categoria e cálculo do resumo
├── app.py                # Rotas, formulário, cache e envio dos dados ao HTML
├── README.md             # Doc do projeto
├── requirements.txt      # Dependências Python
├── requisitos.md         # Enunciado do trabalho (mesmo que foi postado no BlackBoard)
└── scraper.py            # Coleta e interpretação das páginas dos produtos
```

## Configurações

As configurações ficam no início dos respectivos arquivos:

| Arquivo | Variável | Valor atual | Finalidade |
| --- | --- | --- | --- |
| `app.py` | `CACHE_TTL` | `300` | Duração do cache, em segundos |
| `scraper.py` | `BASE_URL` | `https://scrapingsandbox.com` | Endereço usado para montar os links |
| `scraper.py` | `TOTAL_PRODUTOS` | `40` | Último ID consultado, começando em 1 |
| `scraper.py` | `TIMEOUT` | `20` | Limite de espera de conexão e inatividade de leitura, em segundos |
| `scraper.py` | `PAUSA` | `0.2` | Pausa em segundos entre as coletas de produtos |

## Limitações

- Os resultados representam somente os IDs consultados, e não necessariamente todo o catálogo do site.
- A coleta depende da disponibilidade do site e da estrutura do HTML. Mudanças nas páginas podem exigir ajustes nos seletores de `scraper.py`.
- Se uma requisição falhar ou uma página não fornecer o nome do produto, a coleta é interrompida para evitar um resumo baseado em uma coleta parcial.
- O cache fica apenas na memória do processo e é perdido quando o servidor reinicia.
- Os preços são exibidos com o símbolo `$`, conforme os dados coletados, sem conversão de moeda.
