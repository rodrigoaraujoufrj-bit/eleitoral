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
- Análise geoespacial e dashboard interativo com mapas e indicadores, navegável pelo navegador

## Páginas do app

- **Home**: apresentação do projeto
- **Pleito Municipal**: vereador e prefeito — quantas vagas no RJ e o que cada cargo faz
- **Pleito Estadual e Federal**: deputado estadual, deputado federal, senador, governador e presidente — quantas vagas no RJ e o que cada cargo faz

## Stack

- **Python** para tratamento de dados (pandas, geopandas)
- **folium** / **plotly** para mapas e gráficos
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

Esta sessão roda num ambiente sem acesso de rede a sites externos (TSE, IBGE, Wikipédia bloqueados). A população dos municípios (para o cálculo de vereadores) foi colada manualmente a partir da Wikipédia. O item abaixo ainda depende de um arquivo ou de valores compartilhados com o projeto:

- **Salário de cada cargo**: subsídio de presidente, governador, senador, deputado federal, deputado estadual, prefeito e vereador (esses dois últimos variam por município e têm teto definido por lei).

## Próximos passos

- [x] Página de funções e deveres dos cargos eletivos
- [x] Identidade visual (tema roxo ardósia + âmbar)
- [x] Definir recorte geográfico (RJ, 92 municípios)
- [x] Definir pleitos e separar o app em duas seções (municipal / estadual e federal)
- [x] Quantidade de vagas por cargo no RJ
- [x] Vereadores por município (1.376 no total), com base na população do Censo 2022
- [ ] Adicionar salário de cada cargo
- [ ] Prototipar o primeiro mapa
