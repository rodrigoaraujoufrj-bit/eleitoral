import streamlit as st

from cargos_data import CARGOS
from components import render_cargo_card, render_salarios_resumo, render_vagas_resumo
from diagrama_poderes import montar_diagrama
from rj_data import CARGOS_RJ

st.title("Pleito Estadual e Federal")
st.caption("Deputado estadual, deputado federal, senador, governador e presidente, eleitos juntos em 2026")

cargos_gerais_rj = [c for c in CARGOS_RJ if c["pleito"] == "Estadual e Federal"]
cargos_gerais = [c for c in CARGOS if c["pleito"] == "Estadual e Federal"]

st.subheader("Quantas vagas no RJ")
render_vagas_resumo(cargos_gerais_rj)

st.subheader("Quanto ganha cada cargo")
render_salarios_resumo(cargos_gerais_rj)

st.subheader("Como o poder é organizado no estado")
st.caption("Presidente, senador e deputado federal atuam na esfera federal, não estadual. Este diagrama mostra apenas a organização do governo do estado.")
governador = next(c for c in cargos_gerais if c["cargo"] == "Governador")
deputado_estadual = next(c for c in cargos_gerais if c["cargo"] == "Deputado Estadual")
fig_diagrama = montar_diagrama(governador, deputado_estadual)
st.pyplot(fig_diagrama, use_container_width=True)

st.subheader("O que cada cargo faz")
for cargo in cargos_gerais:
    render_cargo_card(cargo)
