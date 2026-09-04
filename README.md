# Eleitoral

Projeto de análise geoespacial e dashboard interativo sobre a política eletiva do estado do Rio de Janeiro (RJ), a partir de dados abertos do TSE (Tribunal Superior Eleitoral) e do IBGE.

## Escopo

- **Recorte geográfico**: estado do Rio de Janeiro e seus 92 municípios (sem outros estados)
- **Sem dados históricos**: o foco é o pleito atual/próximo de cada cargo, não série histórica de eleições passadas
- **Dois pleitos**, porque no Brasil eles acontecem em anos diferentes:
  - **Pleito Municipal**: vereador e prefeito
  - **Pleito Estadual e Federal**: deputado estadual, deputado federal, senador, governador e presidente (eleição geral de 2026)

## Ideia geral

- Explicar de forma clara o que cada cargo eletivo faz de fato, para direcionar melhor a cobrança política e o voto
- Mostrar quantas vagas de cada cargo estão em disputa no RJ (por município, quando for o caso)
- Mostrar quanto cada cargo ganha (subsídio), incluindo o teto de vereador por município
- Análise geoespacial e dashboard interativo com mapas e indicadores, navegável pelo navegador

## Páginas do app

- **Home**: apresentação do projeto
- **Pleito Municipal**: vereador e prefeito — quantas vagas no RJ e o que cada cargo faz
- **Pleito Estadual e Federal**: deputado estadual, deputado federal, senador, governador e presidente — quantas vagas no RJ e o que cada cargo faz

## Stack

- **Python** para tratamento de dados (pandas, geopandas)
- **geopandas** / **matplotlib** para os mapas coropléticos (estáticos, sem depender de internet em tempo de execução) e **plotly** para outros gráficos
- **Streamlit** para o webapp/dashboard, com navegação em seções (`st.navigation`) separando os dois pleitos

## Identidade visual

Paleta roxo ardósia (base) e âmbar (destaque), com cinza neutro, escolhida entre 4 direções para evitar qualquer associação partidária (nada de vermelho, azul saturado ou verde-amarelo). Tom moderno e acessível, fonte Manrope. Configurada em `.streamlit/config.toml` (tema principal e tema da barra lateral) e aplicada em todas as páginas via `app/theme.py`.

## Estrutura

```
eleitoral/
├── .streamlit/
│   └── config.toml               # tema visual (cores, fonte, cantos)
├── app/
│   ├── app.py                    # roteador (st.navigation entre os pleitos)
│   ├── theme.py                  # marca do app, aplicada em cada página
│   ├── components.py             # cards e resumo de vagas, reutilizados nas páginas
│   ├── cargos_data.py            # funções e deveres de cada cargo, com o pleito a que pertence
│   ├── rj_data.py                # quantidade de vagas de cada cargo no RJ
│   ├── municipios_rj.py          # população e vereadores dos 92 municípios do RJ
│   ├── mapa_municipal.py         # mapa coroplético dos municípios do RJ
│   ├── geo/
│   │   └── rj_municipios.geojson # contorno dos 92 municípios (fonte: GitHub, tbrugz/geodata-br)
│   └── views/
│       ├── home.py
│       ├── pleito_municipal.py
│       └── pleito_estadual_federal.py
├── src/            # scripts de ingestão e tratamento de dados
├── data/
│   ├── raw/        # dados brutos baixados do TSE/IBGE (não versionados)
│   └── processed/  # dados já tratados (não versionados)
├── notebooks/      # exploração e prototipagem
├── requirements.txt
└── README.md
```

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

## Dados pendentes

Esta sessão roda num ambiente sem acesso de rede a sites externos (TSE, IBGE, Wikipédia bloqueados). A população dos municípios e os salários foram obtidos por busca (com fonte) ou colados manualmente a partir da Wikipédia, não baixados de um arquivo oficial.

- **Salário de prefeito por município**: não existe fórmula constitucional (é fixado por lei de cada Câmara Municipal). Hoje o app mostra só o exemplo da capital.
- **Salário efetivo de vereador por município**: o app mostra o teto legal (máximo permitido), não o valor que cada Câmara efetivamente paga, que pode ser menor.

O contorno geográfico dos municípios (para o mapa) veio de um repositório público no GitHub (`raw.githubusercontent.com`, não bloqueado aqui), então esse item não teve o mesmo problema.

Sobre o mapa em si: a primeira versão usava Leaflet (via `folium`), mas a biblioteca e as camadas de mapa (tiles) vêm de CDNs externos (jsdelivr, CartoDB, OpenStreetMap), todos bloqueados nesta sessão. Trocado por um mapa estático com `geopandas`/`matplotlib`, que não depende de nada externo em tempo de execução, nem aqui nem para quem for rodar o app.

## Próximos passos

- [x] Página de funções e deveres dos cargos eletivos
- [x] Identidade visual (tema roxo ardósia + âmbar)
- [x] Definir recorte geográfico (RJ, 92 municípios)
- [x] Definir pleitos e separar o app em duas seções (municipal / estadual e federal)
- [x] Quantidade de vagas por cargo no RJ
- [x] Vereadores por município (1.376 no total), com base na população do Censo 2022
- [x] Salário de presidente, governador, senador, deputado federal e deputado estadual
- [x] Teto legal de subsídio de vereador por município
- [x] Primeiro mapa coroplético (população, vereadores ou teto de subsídio por município)
- [ ] Salário efetivo de prefeito e vereador por município (além do teto/exemplo)
- [ ] Mapas para o Pleito Estadual e Federal
- [ ] Cruzar com dados eleitorais de fato (candidatos, votação) quando o pleito de 2026 tiver dados
