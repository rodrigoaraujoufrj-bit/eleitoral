import streamlit as st

from theme import apply_branding

st.set_page_config(page_title="Eleitoral", layout="wide")
apply_branding()

pagina = st.navigation(
    {
        "Visão Geral": [st.Page("views/home.py", title="Home", url_path="home", default=True)],
        "Pleito Municipal": [
            st.Page("views/pleito_municipal.py", title="Vereador e Prefeito", url_path="pleito-municipal"),
        ],
        "Pleito Estadual e Federal": [
            st.Page(
                "views/pleito_estadual_federal.py",
                title="Governador, Senador, Deputados e Presidente",
                url_path="pleito-estadual-federal",
            ),
        ],
        "Análise do Eleitorado": [
            st.Page("views/perfil_eleitorado.py", title="Perfil por Zona", url_path="perfil-eleitorado"),
        ],
    }
)
pagina.run()
