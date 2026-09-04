import pandas as pd
import streamlit as st

from cargos_data import CARGOS
from components import formatar_reais, render_cargo_card, render_salarios_resumo, render_vagas_resumo
from diagrama_poderes import montar_diagrama
from mapa_municipal import montar_mapa
from municipios_rj import MUNICIPIOS_RJ, SUBSIDIO_DEPUTADO_ESTADUAL_RJ
from rj_data import CARGOS_RJ

st.title("Pleito Municipal")
st.caption("Vereador e prefeito, eleitos juntos, no mesmo pleito municipal")

cargos_municipais_rj = [c for c in CARGOS_RJ if c["pleito"] == "Municipal"]
cargos_municipais = [c for c in CARGOS if c["pleito"] == "Municipal"]

st.subheader("Quantas vagas no RJ")
render_vagas_resumo(cargos_municipais_rj)

st.subheader("Quanto ganha cada cargo")
render_salarios_resumo(cargos_municipais_rj)

st.subheader("Vereadores e teto de subsídio por município")
st.caption(
    "Vereadores: depende da população (Censo 2022), Art. 29, IV da Constituição. "
    f"Teto de subsídio: percentual do subsídio de deputado estadual ({formatar_reais(SUBSIDIO_DEPUTADO_ESTADUAL_RJ)}), "
    "Art. 29, VI. É o valor MÁXIMO permitido, a Câmara de cada município pode fixar "
    "um valor menor por lei própria."
)
tabela = pd.DataFrame(MUNICIPIOS_RJ).rename(
    columns={
        "municipio": "Município",
        "populacao_2022": "População (2022)",
        "vereadores": "Vereadores",
        "teto_vereador": "Teto do subsídio (R$)",
    }
)
st.dataframe(tabela.sort_values("População (2022)", ascending=False), hide_index=True, use_container_width=True)

st.subheader("Mapa")
opcoes_mapa = {
    "População (2022)": "populacao_2022",
    "Vereadores": "vereadores",
    "Teto do subsídio de vereador (R$)": "teto_vereador",
}
escolha = st.selectbox("O que colorir no mapa", options=list(opcoes_mapa.keys()))
fig = montar_mapa(MUNICIPIOS_RJ, opcoes_mapa[escolha], escolha)
st.pyplot(fig, use_container_width=True)

st.subheader("Como o poder é organizado no município")
prefeito = next(c for c in cargos_municipais if c["cargo"] == "Prefeito")
vereador = next(c for c in cargos_municipais if c["cargo"] == "Vereador")
fig_diagrama = montar_diagrama(prefeito, vereador)
st.pyplot(fig_diagrama, use_container_width=True)

st.subheader("O que cada cargo faz")
for cargo in cargos_municipais:
    render_cargo_card(cargo)
