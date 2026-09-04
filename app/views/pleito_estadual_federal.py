import streamlit as st

from cargos_data import CARGOS
from components import render_cargo_card, render_vagas_resumo
from rj_data import CARGOS_RJ

st.title("Pleito Estadual e Federal")
st.caption("Deputado estadual, deputado federal, senador, governador e presidente, eleitos juntos em 2026")

cargos_gerais_rj = [c for c in CARGOS_RJ if c["pleito"] == "Estadual e Federal"]
cargos_gerais = [c for c in CARGOS if c["pleito"] == "Estadual e Federal"]

st.subheader("Quantas vagas no RJ")
render_vagas_resumo(cargos_gerais_rj)

st.subheader("O que cada cargo faz")
for cargo in cargos_gerais:
    render_cargo_card(cargo)
