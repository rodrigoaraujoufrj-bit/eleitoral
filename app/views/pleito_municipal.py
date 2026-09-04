import pandas as pd
import streamlit as st

from areas_influencia import montar_mapa_areas_influencia
from cargos_data import CARGOS
from components import formatar_reais, render_cargo_card, render_salarios_resumo, render_vagas_resumo
from diagrama_poderes import montar_diagrama
from locais_votacao import carregar_locais_votacao, locais_votacao_disponivel
from mapa_municipal import montar_mapa
from municipios_rj import MUNICIPIOS_RJ, SUBSIDIO_DEPUTADO_ESTADUAL_RJ
from rj_data import CARGOS_RJ
from setores_censitarios import carregar_setores

@st.cache_data(show_spinner="Cruzando setores censitários com os locais de votação...")
def _montar_mapa_areas_influencia_cache(_setores, _locais_votacao, recorte):
    # Argumentos com "_" na frente: Streamlit não tenta gerar hash deles
    # (GeoDataFrame com coluna de geometria não é hasheável). `recorte`,
    # a única coisa que varia entre chamadas nesta página, é a chave do cache.
    return montar_mapa_areas_influencia(_setores, _locais_votacao, recorte=recorte)

st.title("Pleito Municipal")
st.caption("Vereador e prefeito, eleitos juntos, no mesmo pleito municipal")

cargos_municipais_rj = [c for c in CARGOS_RJ if c["pleito"] == "Municipal"]
cargos_municipais = [c for c in CARGOS if c["pleito"] == "Municipal"]

st.subheader("Quantas vagas no RJ")
render_vagas_resumo(cargos_municipais_rj)

st.subheader("Quanto ganha cada cargo")
render_salarios_resumo(cargos_municipais_rj)

st.subheader("Vereadores e teto de subsídio por município")
st.caption(
    "Vereadores: depende da população (Censo 2022), Art. 29, IV da Constituição. "
    f"Teto de subsídio: percentual do subsídio de deputado estadual ({formatar_reais(SUBSIDIO_DEPUTADO_ESTADUAL_RJ)}), "
    "Art. 29, VI. É o valor MÁXIMO permitido, a Câmara de cada município pode fixar "
    "um valor menor por lei própria."
)
tabela = pd.DataFrame(MUNICIPIOS_RJ).rename(
    columns={
        "municipio": "Município",
        "populacao_2022": "População (2022)",
        "vereadores": "Vereadores",
        "teto_vereador": "Teto do subsídio (R$)",
    }
)
st.dataframe(tabela.sort_values("População (2022)", ascending=False), hide_index=True, use_container_width=True)

st.subheader("Mapa")
opcoes_mapa = {
    "População (2022)": "populacao_2022",
    "Vereadores": "vereadores",
    "Teto do subsídio de vereador (R$)": "teto_vereador",
}
escolha = st.selectbox("O que colorir no mapa", options=list(opcoes_mapa.keys()))

locais = None
if locais_votacao_disponivel():
    if st.checkbox("Mostrar locais de votação (eleição de 04/10/2026)"):
        locais = carregar_locais_votacao()
        st.caption(f"{len(locais):,} locais de votação no RJ, cada um pode reunir várias seções.".replace(",", "."))
else:
    st.caption(
        "Locais de votação: rode `python src/restaurar_dados.py` para restaurar esse conjunto de dados do TSE."
    )

fig = montar_mapa(MUNICIPIOS_RJ, opcoes_mapa[escolha], escolha, locais_votacao=locais)
st.pyplot(fig, use_container_width=True)

st.subheader("Área de influência de cada local de votação")
st.caption(
    "O TSE não publica um polígono oficial de abrangência por local de votação. Como "
    "aproximação, cada setor censitário do IBGE (Censo 2022, a menor unidade geográfica "
    "oficial) foi atribuído ao local de votação mais próximo do seu centro, e os setores "
    "de cada local foram unidos numa única área. A borda de cada área acompanha os "
    "limites reais dos setores, não é uma reta artificial."
)
if locais_votacao_disponivel():
    recorte = st.radio(
        "Recorte", options=["Estado inteiro", "Zoom no município do Rio de Janeiro"], horizontal=True
    )
    locais_para_areas = carregar_locais_votacao()
    setores = carregar_setores()
    fig_areas = _montar_mapa_areas_influencia_cache(
        setores, locais_para_areas, "rio" if "Rio de Janeiro" in recorte else "estado"
    )
    st.pyplot(fig_areas, use_container_width=True)
else:
    st.caption("Locais de votação: rode `python src/restaurar_dados.py` para restaurar esse conjunto de dados do TSE.")

st.subheader("Como o poder é organizado no município")
prefeito = next(c for c in cargos_municipais if c["cargo"] == "Prefeito")
vereador = next(c for c in cargos_municipais if c["cargo"] == "Vereador")
fig_diagrama = montar_diagrama(prefeito, vereador)
st.pyplot(fig_diagrama, use_container_width=True)

st.subheader("O que cada cargo faz")
for cargo in cargos_municipais:
    render_cargo_card(cargo)
