import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cargos_data import CARGOS

st.set_page_config(page_title="Funções e Deveres", layout="wide")

st.title("Funções e Deveres dos Cargos Eletivos")
st.markdown(
    "Muita cobrança política é feita ao cargo errado. Segurança pública, "
    "por exemplo, não é atribuição do prefeito, é do governador. Esta "
    "página resume o que cada cargo realmente faz, com base na "
    "Constituição Federal, para ajudar a direcionar a cobrança e o voto "
    "de forma mais informada."
)

esferas = ["Federal", "Estadual", "Municipal"]
abas = st.tabs(esferas)

for aba, esfera in zip(abas, esferas):
    with aba:
        cargos_da_esfera = [c for c in CARGOS if c["esfera"] == esfera]
        for cargo in cargos_da_esfera:
            with st.expander(f"{cargo['cargo']} ({cargo['poder']})", expanded=False):
                col_info, col_faz, col_nao_faz = st.columns([1, 1.4, 1.4])

                with col_info:
                    st.markdown("**Mandato**")
                    st.write(cargo["mandato"])
                    st.markdown("**Eleição**")
                    st.write(cargo["eleicao"])

                with col_faz:
                    st.markdown("**O que faz**")
                    for item in cargo["atribuicoes"]:
                        st.markdown(f"- {item}")

                with col_nao_faz:
                    st.markdown("**O que não faz (equívocos comuns)**")
                    for item in cargo["nao_atribuicoes"]:
                        st.markdown(f"- {item}")
