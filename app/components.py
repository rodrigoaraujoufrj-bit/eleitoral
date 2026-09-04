import streamlit as st


def render_cargo_card(cargo: dict):
    """Card com mandato, eleição, o que faz e o que não faz de um cargo."""
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


def render_vagas_resumo(cargos_rj: list):
    """Linha de métricas com a quantidade de vagas de cada cargo no RJ."""
    colunas = st.columns(len(cargos_rj))
    for coluna, cargo in zip(colunas, cargos_rj):
        with coluna:
            valor = cargo["vagas"] if cargo["vagas"] is not None else "?"
            st.metric(cargo["cargo"], valor)
            st.caption(cargo["explicacao"])


def formatar_numero(valor: float, casas_decimais: int = 2) -> str:
    texto = f"{valor:,.{casas_decimais}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_reais(valor: float, casas_decimais: int = 2) -> str:
    return f"R$ {formatar_numero(valor, casas_decimais)}"


def render_salarios_resumo(cargos_rj: list):
    """Linha de métricas com o salário (subsídio) de cada cargo no RJ."""
    colunas = st.columns(len(cargos_rj))
    for coluna, cargo in zip(colunas, cargos_rj):
        with coluna:
            if cargo["salario"] is not None:
                # Sem centavos no cartão, para caber; valor exato na legenda.
                st.metric(cargo["cargo"], formatar_reais(cargo["salario"], 0))
                st.caption(f"Valor exato: {formatar_reais(cargo['salario'])}")
            elif cargo.get("salario_min") is not None and cargo.get("salario_max") is not None:
                # Só um "R$" na string toda: dois cifrões no mesmo texto do
                # metric fazem o Streamlit interpretar o meio como fórmula.
                minimo = formatar_numero(cargo["salario_min"], 0)
                maximo = formatar_numero(cargo["salario_max"], 0)
                st.metric(cargo["cargo"], f"R$ {minimo} a {maximo}")
            else:
                st.metric(cargo["cargo"], "Varia")
            if cargo.get("salario_nota"):
                st.caption(cargo["salario_nota"])
