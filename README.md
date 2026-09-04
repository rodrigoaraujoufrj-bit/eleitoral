# Eleitoral

Projeto de análise geoespacial e dashboard interativo de dados eleitorais, a partir dos dados abertos do TSE (Tribunal Superior Eleitoral).

## Status

Em fase de definição de escopo. Ainda estamos decidindo:

- Qual pleito (federal, estadual, municipal) e qual ano
- Qual recorte geográfico (nacional, estado, município específico)
- Quais perguntas o projeto deve responder

## Ideia geral

- Baixar e tratar dados abertos do TSE (resultados de votação, perfil do eleitorado, dados geográficos das zonas/seções eleitorais)
- Análise geoespacial: mapas de concentração de votos, comparações regionais
- Dashboard interativo com mapas e indicadores, navegável pelo navegador

## Stack

- **Python** para tratamento de dados (pandas, geopandas)
- **folium** / **plotly** para mapas e gráficos
- **Streamlit** para o webapp/dashboard

## Estrutura

```
eleitoral/
├── app/            # aplicação Streamlit (ponto de entrada)
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

- [ ] Definir pleito e ano de foco
- [ ] Definir recorte geográfico
- [ ] Baixar dados do repositório de dados abertos do TSE
- [ ] Prototipar o primeiro mapa
