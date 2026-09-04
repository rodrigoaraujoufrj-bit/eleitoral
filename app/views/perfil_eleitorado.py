import streamlit as st

from locais_votacao import carregar_locais_votacao, locais_votacao_disponivel
from mapa_perfil_eleitorado import carregar_zonas_geometria, montar_mapa_perfil
from perfil_eleitorado import (
    ORDEM_ESCOLARIDADE,
    ORDEM_FAIXA_ETARIA,
    ORDEM_GENERO,
    ORDEM_RACA_COR,
    carregar_perfil_eleitorado,
    eleitores_por_zona,
    perfil_eleitorado_disponivel,
)
from setores_censitarios import carregar_setores


@st.cache_data(show_spinner="Calculando a geometria de cada zona eleitoral...")
def _zonas_geometria_cache(_setores, _locais_votacao):
    return carregar_zonas_geometria(_setores, _locais_votacao)


st.title("Perfil do Eleitorado por Zona")
st.caption(
    "Combine filtros de gênero, faixa etária, escolaridade e raça/cor para ver em quais zonas "
    "eleitorais esse perfil está mais concentrado. Dado real do TSE (eleição de 04/10/2026), "
    "agregado por zona a partir do conjunto perfil_secao. É composição demográfica do "
    "eleitorado registrado, não dado de comportamento, consumo ou intenção de voto."
)

if not perfil_eleitorado_disponivel():
    st.caption("Rode `python src/tratar_perfil_secao.py` para gerar esse conjunto de dados.")
    st.stop()

if not locais_votacao_disponivel():
    st.caption("Locais de votação: rode `python src/restaurar_dados.py` para restaurar esse conjunto de dados do TSE.")
    st.stop()

perfil = carregar_perfil_eleitorado()

st.subheader("Filtros")
coluna_a, coluna_b = st.columns(2)
with coluna_a:
    generos = st.multiselect("Gênero", options=ORDEM_GENERO, default=ORDEM_GENERO)
    escolaridades = st.multiselect("Escolaridade", options=ORDEM_ESCOLARIDADE, default=ORDEM_ESCOLARIDADE)
with coluna_b:
    faixas_etarias = st.multiselect("Faixa etária", options=ORDEM_FAIXA_ETARIA, default=ORDEM_FAIXA_ETARIA)
    racas_cor = st.multiselect("Raça/cor", options=ORDEM_RACA_COR, default=ORDEM_RACA_COR)

resultado = eleitores_por_zona(perfil, generos, faixas_etarias, escolaridades, racas_cor)

st.subheader("Zonas onde esse perfil é mais forte")
metrica = st.radio(
    "Ordenar zonas por",
    options=["Total de eleitores (número)", "Concentração na zona (%)"],
    horizontal=True,
)
st.caption(
    "Total: quantos eleitores da zona passam no filtro, em número absoluto. Concentração: "
    "desses eleitores, qual fração é da zona toda, útil para achar onde um perfil é raro no "
    "resto do estado mas forte ali. Sem nenhum filtro restrito, concentração é sempre 100%."
)
coluna_metrica = "percentual" if metrica.startswith("Concentração") else "eleitores_filtro"
quantidade_alvo = st.slider("Quantas zonas destacar", min_value=3, max_value=30, value=10)

ordenado = resultado.sort_values(coluna_metrica, ascending=False)
zonas_alvo = ordenado.head(quantidade_alvo)["zona"].tolist()

tabela = ordenado.head(quantidade_alvo).rename(
    columns={
        "municipio": "Município",
        "zona": "Zona",
        "eleitores_filtro": "Eleitores no filtro",
        "eleitores_zona": "Total de eleitores na zona",
        "percentual": "Concentração (%)",
    }
)
tabela["Concentração (%)"] = tabela["Concentração (%)"].round(1)
st.dataframe(
    tabela[["Município", "Zona", "Eleitores no filtro", "Total de eleitores na zona", "Concentração (%)"]],
    hide_index=True,
    use_container_width=True,
)

ver_estado_inteiro = st.checkbox("Ver estado inteiro, sem zoom nas zonas de cima")

setores = carregar_setores()
locais = carregar_locais_votacao()
zonas_geometria = _zonas_geometria_cache(setores, locais)

valores_por_zona = resultado.set_index("zona")[coluna_metrica]
legenda = "Concentração (%)" if coluna_metrica == "percentual" else "Eleitores no filtro"
fig = montar_mapa_perfil(
    zonas_geometria, valores_por_zona, legenda, zonas_alvo=None if ver_estado_inteiro else zonas_alvo
)
st.pyplot(fig, use_container_width=True)
