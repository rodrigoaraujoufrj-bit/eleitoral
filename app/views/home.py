import streamlit as st

st.title("Eleitoral")
st.caption("Quantas vagas estão em disputa no Rio de Janeiro, e o que cada cargo realmente faz")

with st.container(border=True):
    st.markdown(
        "O app está organizado em dois pleitos, porque no Brasil eles "
        "acontecem em anos diferentes:\n\n"
        "- **Pleito Municipal**: vereador e prefeito\n"
        "- **Pleito Estadual e Federal**: deputado estadual, deputado "
        "federal, senador, governador e presidente\n\n"
        "Use o menu ao lado para ver, em cada pleito, quantas vagas estão "
        "em disputa no RJ e o que cada cargo realmente faz."
    )
