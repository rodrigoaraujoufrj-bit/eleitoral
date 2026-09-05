import streamlit as st

from locais_votacao import carregar_locais_votacao, locais_votacao_disponivel
from mapa_municipal import carregar_geodataframe
from mapa_perfil_eleitorado import CRS_PROJETADA, carregar_zonas_geometria, montar_mapa_perfil
from municipios_rj import MUNICIPIOS_RJ
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

NOMES_MUNICIPIOS = sorted(m["municipio"] for m in MUNICIPIOS_RJ)


@st.cache_data(show_spinner="Calculando a geometria de cada zona eleitoral...")
def _zonas_geometria_cache(_setores, _locais_votacao, municipios: tuple[str, ...]):
    return carregar_zonas_geometria(_setores, _locais_votacao, municipios=list(municipios) or None)


st.title("Perfil do Eleitorado por Zona")
st.caption(
    "Combine um recorte de município com filtros de gênero, faixa etária, escolaridade e "
    "raça/cor para ver em quais zonas eleitorais esse perfil está mais concentrado. Dado real "
    "do TSE (eleição de 04/10/2026), agregado por zona a partir do conjunto perfil_secao. É "
    "composição demográfica do eleitorado registrado, não dado de comportamento, consumo ou "
    "intenção de voto."
)

if not perfil_eleitorado_disponivel():
    st.caption("Rode `python src/tratar_perfil_secao.py` para gerar esse conjunto de dados.")
    st.stop()

if not locais_votacao_disponivel():
    st.caption("Locais de votação: rode `python src/restaurar_dados.py` para restaurar esse conjunto de dados do TSE.")
    st.stop()

perfil = carregar_perfil_eleitorado()

st.subheader("Onde")
municipios_selecionados = st.multiselect(
    "Município (deixe vazio para o estado inteiro)",
    options=NOMES_MUNICIPIOS,
    default=[],
    help="Um candidato a vereador ou prefeito só disputa no próprio município: escolha um ou "
    "mais para não misturar com áreas de fora.",
)
municipios_filtro = [m.upper() for m in municipios_selecionados]

st.subheader("Quem")
coluna_a, coluna_b = st.columns(2)
with coluna_a:
    generos = st.multiselect("Gênero", options=ORDEM_GENERO, default=ORDEM_GENERO)
    escolaridades = st.multiselect("Escolaridade", options=ORDEM_ESCOLARIDADE, default=ORDEM_ESCOLARIDADE)
with coluna_b:
    faixas_etarias = st.multiselect("Faixa etária", options=ORDEM_FAIXA_ETARIA, default=ORDEM_FAIXA_ETARIA)
    racas_cor = st.multiselect("Raça/cor", options=ORDEM_RACA_COR, default=ORDEM_RACA_COR)

resultado = eleitores_por_zona(
    perfil, generos, faixas_etarias, escolaridades, racas_cor, municipios=municipios_filtro or None
)

if resultado.empty:
    st.warning("Nenhuma zona encontrada para esse recorte.")
    st.stop()

st.subheader("Zonas onde esse perfil é mais forte")
metrica = st.radio(
    "Ordenar zonas por",
    options=["Total de eleitores (número)", "Concentração na zona (%)"],
    horizontal=True,
)
st.caption(
    "Total: quantos eleitores do recorte passam no filtro, em número absoluto. Concentração: "
    "desses eleitores, qual fração é do recorte todo, útil para achar onde um perfil é raro no "
    "resto mas forte ali. Sem nenhum filtro de gênero/faixa/escolaridade/raça restrito, "
    "concentração é sempre 100%. Com município selecionado, os dois já ignoram eleitores de "
    "fora dele."
)
coluna_metrica = "percentual" if metrica.startswith("Concentração") else "eleitores_filtro"

teto_zonas = min(30, len(resultado))
piso_zonas = min(3, teto_zonas)
quantidade_alvo = st.slider(
    "Quantas zonas destacar", min_value=piso_zonas, max_value=teto_zonas, value=min(10, teto_zonas)
)

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

rotulo_zoom = (
    "Ver o(s) município(s) inteiro(s), sem destacar as zonas de cima"
    if municipios_filtro
    else "Ver estado inteiro, sem zoom nas zonas de cima"
)
sem_destaque = st.checkbox(rotulo_zoom)

setores = carregar_setores()
locais = carregar_locais_votacao()
zonas_geometria = _zonas_geometria_cache(setores, locais, tuple(municipios_filtro))

municipios_geometria = None
if municipios_filtro:
    gdf_municipios = carregar_geodataframe().to_crs(CRS_PROJETADA)
    municipios_geometria = gdf_municipios[gdf_municipios["name"].str.upper().isin(municipios_filtro)]

valores_por_zona = resultado.set_index("zona")[coluna_metrica]
legenda = "Concentração (%)" if coluna_metrica == "percentual" else "Eleitores no filtro"
fig = montar_mapa_perfil(
    zonas_geometria,
    valores_por_zona,
    legenda,
    zonas_alvo=None if sem_destaque else zonas_alvo,
    municipios_geometria=municipios_geometria,
)
st.pyplot(fig, use_container_width=True)
