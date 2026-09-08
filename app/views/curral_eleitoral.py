import streamlit as st

from locais_votacao import carregar_locais_votacao, locais_votacao_disponivel
from mapa_municipal import carregar_geodataframe
from mapa_perfil_eleitorado import CRS_PROJETADA, carregar_zonas_geometria, montar_mapa_perfil
from municipios_rj import MUNICIPIOS_RJ
from resultados_eleitorais import (
    candidatos_do_municipio,
    carregar_votacao,
    resultados_disponivel,
    turnos_disponiveis,
    votos_por_zona,
)
from setores_censitarios import carregar_setores

ANO = 2024
NOMES_MUNICIPIOS = sorted(m["municipio"] for m in MUNICIPIOS_RJ)


@st.cache_data(show_spinner="Calculando a geometria de cada zona eleitoral...")
def _zonas_geometria_cache(_setores, _locais_votacao, municipio: str):
    return carregar_zonas_geometria(_setores, _locais_votacao, municipios=[municipio])


st.title("Curral Eleitoral")
st.caption(
    "Onde um candidato específico teve força de verdade, voto real da eleição de 2024 "
    "divulgado pelo TSE. Diferente da página de Perfil por Zona (que é composição "
    "demográfica, uma aproximação de quem mora onde), isto é resultado de eleição passada "
    "de verdade, não suposição. Hoje só cobre vereador e prefeito (2024); governador, "
    "senador, deputados e presidente ainda não estão disponíveis (ver README)."
)

if not resultados_disponivel(ANO):
    st.caption(f"Rode `python src/tratar_resultados.py --ano {ANO}` para gerar esse conjunto de dados.")
    st.stop()

if not locais_votacao_disponivel():
    st.caption("Locais de votação: rode `python src/baixar_dados_tse.py` para restaurar esse conjunto de dados do TSE.")
    st.stop()

votacao = carregar_votacao(ANO)

st.subheader("Onde e quem")
municipio_escolhido = st.selectbox("Município", options=NOMES_MUNICIPIOS)
municipio_upper = municipio_escolhido.upper()

cargo_escolhido = st.radio("Cargo", options=["Vereador", "Prefeito"], horizontal=True)

turnos = turnos_disponiveis(votacao, municipio_upper, cargo_escolhido)
if not turnos:
    st.warning(f"Sem dados de {cargo_escolhido.lower()} para {municipio_escolhido}.")
    st.stop()
turno_escolhido = (
    st.radio("Turno", options=turnos, horizontal=True, format_func=lambda t: f"{t}º turno")
    if len(turnos) > 1
    else turnos[0]
)

candidatos = candidatos_do_municipio(votacao, municipio_upper, cargo_escolhido, turno_escolhido)
if candidatos.empty:
    st.warning("Nenhum candidato encontrado para esse recorte.")
    st.stop()

opcoes_candidato = {
    f"{linha.candidato} ({linha.partido}), {linha.votos:,} votos, {linha.situacao.lower()}".replace(",", "."): (
        linha.sq_candidato
    )
    for linha in candidatos.itertuples()
}
escolha = st.selectbox(f"Candidato a {cargo_escolhido.lower()}", options=list(opcoes_candidato.keys()))
sq_escolhido = opcoes_candidato[escolha]

st.subheader("Onde estão os votos dele(a)")
por_zona = votos_por_zona(votacao, sq_escolhido)
total_votos = int(por_zona["votos"].sum())
concentracao_top3 = round(por_zona.head(3)["percentual"].sum(), 1)

coluna_a, coluna_b = st.columns(2)
coluna_a.metric("Total de votos", f"{total_votos:,}".replace(",", "."))
coluna_b.metric("Concentração nas 3 zonas mais fortes", f"{concentracao_top3}%")
st.caption(
    "Quanto maior essa concentração, mais o candidato depende de poucas zonas específicas "
    "(um curral eleitoral mais forte); quanto mais baixa, mais espalhado é o voto dele pelo "
    "município."
)

teto = min(15, len(por_zona))
piso = min(3, teto)
if teto > piso:
    quantidade_alvo = st.slider("Quantas zonas destacar", min_value=piso, max_value=teto, value=min(5, teto))
else:
    # Poucas zonas no total (candidato com votos em 1 ou 2 zonas só): nada
    # pra escolher, mostra todas sem controle deslizante.
    quantidade_alvo = teto
zonas_alvo = por_zona.head(quantidade_alvo)["zona"].tolist()

tabela = por_zona.rename(columns={"zona": "Zona", "votos": "Votos", "percentual": "% do total do candidato"})
tabela["% do total do candidato"] = tabela["% do total do candidato"].round(1)
st.dataframe(tabela, hide_index=True, use_container_width=True)

setores = carregar_setores()
locais = carregar_locais_votacao()
zona_geometria = _zonas_geometria_cache(setores, locais, municipio_upper)

gdf_municipios = carregar_geodataframe().to_crs(CRS_PROJETADA)
municipio_geometria = gdf_municipios[gdf_municipios["name"].str.upper() == municipio_upper]

valores_por_zona = por_zona.set_index("zona")["votos"]
fig = montar_mapa_perfil(
    zona_geometria,
    valores_por_zona,
    "Votos",
    zonas_alvo=zonas_alvo,
    municipios_geometria=municipio_geometria,
    coluna_unidade="zona",
)
st.pyplot(fig, use_container_width=True)
