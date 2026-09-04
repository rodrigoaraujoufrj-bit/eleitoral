import streamlit as st

from theme import apply_branding

st.set_page_config(page_title="Eleitoral", layout="wide")
apply_branding()

st.title("Eleitoral")
st.caption("Análise geoespacial e dashboard interativo de dados eleitorais (dados abertos do TSE)")

with st.container(border=True):
    st.markdown(
        "Projeto em fase inicial. Ainda estamos definindo o pleito, o ano e o "
        "recorte geográfico de foco. Use o menu ao lado para acessar a página "
        "**Funções e Deveres**, que explica o que cada cargo eletivo faz de fato. "
        "Os próximos módulos, como mapas e indicadores, entram aqui conforme o "
        "escopo for definido."
    )
