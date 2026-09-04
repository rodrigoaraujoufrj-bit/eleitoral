# Eleitoral

Projeto de análise geoespacial e dashboard interativo de dados eleitorais, a partir dos dados abertos do TSE (Tribunal Superior Eleitoral).

## Status

Em fase de definição de escopo. Ainda estamos decidindo:

- Qual pleito (federal, estadual, municipal) e qual ano
- Qual recorte geográfico (nacional, estado, município específico)
- Quais perguntas o projeto deve responder

## Ideia geral

- Explicar de forma clara o que cada cargo eletivo faz de fato, para direcionar melhor a cobrança política e o voto
- Baixar e tratar dados abertos do TSE (resultados de votação, perfil do eleitorado, dados geográficos das zonas/seções eleitorais)
- Análise geoespacial: mapas de concentração de votos, comparações regionais
- Dashboard interativo com mapas e indicadores, navegável pelo navegador

## Páginas do app

- **Home**: apresentação do projeto e status atual
- **Funções e Deveres**: o que cada cargo eletivo (presidente, governador, senador, deputado federal, deputado estadual, prefeito e vereador) realmente faz, com base na Constituição Federal, incluindo os equívocos mais comuns sobre cada um

## Stack

- **Python** para tratamento de dados (pandas, geopandas)
- **folium** / **plotly** para mapas e gráficos
- **Streamlit** para o webapp/dashboard

## Estrutura

```
eleitoral/
├── app/
│   ├── app.py              # página inicial (Home)
│   ├── cargos_data.py      # conteúdo sobre funções e deveres de cada cargo
│   └── pages/
│       └── 1_Funções_e_Deveres.py
├── src/            # scripts de ingestão e tratamento de dados
├── data/
│   ├── raw/        # dados brutos baixados do TSE (não versionados)
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

## Próximos passos

- [x] Página de Funções e Deveres dos cargos eletivos
- [ ] Definir pleito e ano de foco
- [ ] Definir recorte geográfico
- [ ] Baixar dados do repositório de dados abertos do TSE
- [ ] Prototipar o primeiro mapa
