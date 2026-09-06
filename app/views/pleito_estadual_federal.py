import streamlit as st

from cargos_data import CARGOS
from components import render_cargo_card, render_salarios_resumo, render_vagas_resumo
from diagrama_poderes import montar_diagrama
from locais_votacao import carregar_locais_votacao, locais_votacao_disponivel
from mapa_municipal import montar_mapa
from municipios_rj import MUNICIPIOS_RJ
from rj_data import CARGOS_RJ

CANONICO = {m["municipio"].upper(): m["municipio"] for m in MUNICIPIOS_RJ}

st.title("Pleito Estadual e Federal")
st.caption("Deputado estadual, deputado federal, senador, governador e presidente, eleitos juntos em 2026")

cargos_gerais_rj = [c for c in CARGOS_RJ if c["pleito"] == "Estadual e Federal"]
cargos_gerais = [c for c in CARGOS if c["pleito"] == "Estadual e Federal"]

st.subheader("Quantas vagas no RJ")
render_vagas_resumo(cargos_gerais_rj)

st.subheader("Quanto ganha cada cargo")
render_salarios_resumo(cargos_gerais_rj)

st.subheader("Mapa")
st.caption(
    "Governador, senador, deputado federal e deputado estadual não têm vaga por município (são "
    "eleitos pelo estado inteiro, por proporcionalidade), então o mapa mostra o eleitorado apto "
    "a votar em cada um, o dado real do TSE, não uma estimativa de população."
)
if locais_votacao_disponivel():
    locais = carregar_locais_votacao()
    eleitores_por_municipio = locais.groupby("municipio")["eleitores"].sum()
    municipios_eleitorado = [
        {"municipio": CANONICO[municipio], "eleitores": int(total)}
        for municipio, total in eleitores_por_municipio.items()
    ]

    locais_mapa = None
    if st.checkbox("Mostrar locais de votação (eleição de 04/10/2026)"):
        locais_mapa = locais

    fig = montar_mapa(municipios_eleitorado, "eleitores", "Eleitores aptos a votar", locais_votacao=locais_mapa)
    st.pyplot(fig, use_container_width=True)
else:
    st.caption("Locais de votação: rode `python src/restaurar_dados.py` para restaurar esse conjunto de dados do TSE.")

st.subheader("Como o poder é organizado no estado")
st.caption("Presidente, senador e deputado federal atuam na esfera federal, não estadual. Este diagrama mostra apenas a organização do governo do estado.")
governador = next(c for c in cargos_gerais if c["cargo"] == "Governador")
deputado_estadual = next(c for c in cargos_gerais if c["cargo"] == "Deputado Estadual")
fig_diagrama = montar_diagrama(governador, deputado_estadual)
st.pyplot(fig_diagrama, use_container_width=True)

st.subheader("O que cada cargo faz")
for cargo in cargos_gerais:
    render_cargo_card(cargo)
