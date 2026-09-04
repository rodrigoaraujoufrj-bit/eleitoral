import streamlit as st

from cargos_data import CARGOS
from components import render_cargo_card, render_vagas_resumo
from rj_data import CARGOS_RJ

st.title("Pleito Municipal")
st.caption("Vereador e prefeito, eleitos juntos, no mesmo pleito municipal")

cargos_municipais_rj = [c for c in CARGOS_RJ if c["pleito"] == "Municipal"]
cargos_municipais = [c for c in CARGOS if c["pleito"] == "Municipal"]

st.subheader("Quantas vagas no RJ")
render_vagas_resumo(cargos_municipais_rj)

st.subheader("O que cada cargo faz")
for cargo in cargos_municipais:
    render_cargo_card(cargo)
