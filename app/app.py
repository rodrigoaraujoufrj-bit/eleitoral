import streamlit as st

st.set_page_config(page_title="Eleitoral", layout="wide")

st.title("Eleitoral")
st.caption("Análise geoespacial e dashboard interativo de dados eleitorais (dados abertos do TSE)")

st.info(
    "Projeto em fase inicial. Ainda estamos definindo o pleito, o ano e o "
    "recorte geográfico de foco. Use o menu ao lado para acessar a página "
    "'Funções e Deveres', que explica o que cada cargo eletivo faz de fato. "
    "Os próximos módulos, como mapas e indicadores, entram aqui conforme o "
    "escopo for definido."
)
