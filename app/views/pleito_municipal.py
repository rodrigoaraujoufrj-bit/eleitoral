import pandas as pd
import streamlit as st

from cargos_data import CARGOS
from components import render_cargo_card, render_vagas_resumo
from municipios_rj import MUNICIPIOS_RJ
from rj_data import CARGOS_RJ

st.title("Pleito Municipal")
st.caption("Vereador e prefeito, eleitos juntos, no mesmo pleito municipal")

cargos_municipais_rj = [c for c in CARGOS_RJ if c["pleito"] == "Municipal"]
cargos_municipais = [c for c in CARGOS if c["pleito"] == "Municipal"]

st.subheader("Quantas vagas no RJ")
render_vagas_resumo(cargos_municipais_rj)

st.subheader("Vereadores por município")
st.caption("Depende da população de cada município (Censo 2022), conforme a Constituição (Art. 29, IV)")
tabela = pd.DataFrame(MUNICIPIOS_RJ).rename(
    columns={"municipio": "Município", "populacao_2022": "População (2022)", "vereadores": "Vereadores"}
)
st.dataframe(tabela.sort_values("População (2022)", ascending=False), hide_index=True, use_container_width=True)

st.subheader("O que cada cargo faz")
for cargo in cargos_municipais:
    render_cargo_card(cargo)
