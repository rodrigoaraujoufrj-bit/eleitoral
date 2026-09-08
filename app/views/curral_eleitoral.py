import streamlit as st

from locais_votacao import carregar_locais_votacao, locais_votacao_disponivel
from mapa_municipal import carregar_geodataframe
from mapa_perfil_eleitorado import CRS_PROJETADA, carregar_zonas_geometria, montar_mapa_perfil
from municipios_rj import MUNICIPIOS_RJ
from resultados_eleitorais import (
    candidatos,
    carregar_votacao,
    resultados_disponivel,
    turnos_disponiveis,
    votos_por_zona,
)
from setores_censitarios import carregar_setores

NOMES_MUNICIPIOS = sorted(m["municipio"] for m in MUNICIPIOS_RJ)

# Cada cargo só existe num ano (o app não cruza pleito municipal com
# estadual/federal) e só os municipais (vereador, prefeito) disputam
# dentro de 1 município; os outros têm o mesmo candidato nos 92 do RJ.
CARGOS = {
    "Vereador": {"ano": 2024, "municipal": True},
    "Prefeito": {"ano": 2024, "municipal": True},
    "Governador": {"ano": 2022, "municipal": False},
    "Senador": {"ano": 2022, "municipal": False},
    "Deputado Estadual": {"ano": 2022, "municipal": False},
    "Deputado Federal": {"ano": 2022, "municipal": False},
}
# Proporcional (estadual/federal) passa de mil candidatos no RJ: por padrão
# mostra só quem se elegeu, com opção de ver todo mundo.
CARGOS_MUITOS_CANDIDATOS = {"Deputado Estadual", "Deputado Federal"}


@st.cache_data(show_spinner="Carregando a votação...")
def _votacao_cache(ano: int):
    return carregar_votacao(ano)


@st.cache_data(show_spinner="Calculando a geometria de cada zona eleitoral...")
def _zonas_geometria_cache(_setores, _locais_votacao, municipios: tuple[str, ...]):
    return carregar_zonas_geometria(_setores, _locais_votacao, municipios=list(municipios) or None)


st.title("Curral Eleitoral")
st.caption(
    "Onde um candidato específico teve força de verdade, voto real divulgado pelo TSE. "
    "Diferente da página de Perfil por Zona (que é composição demográfica, uma aproximação "
    "de quem mora onde), isto é resultado de eleição passada de verdade, não suposição. "
    "Vereador e prefeito são da eleição de 2024; governador, senador, deputado estadual e "
    "deputado federal, da de 2022 (presidente ainda não, ver README)."
)

if not locais_votacao_disponivel():
    st.caption("Locais de votação: rode `python src/baixar_dados_tse.py` para restaurar esse conjunto de dados do TSE.")
    st.stop()

st.subheader("Cargo")
cargo_escolhido = st.radio("Cargo", options=list(CARGOS.keys()), horizontal=True)
info_cargo = CARGOS[cargo_escolhido]
ano = info_cargo["ano"]

if not resultados_disponivel(ano):
    st.caption(f"Rode `python src/tratar_resultados.py --ano {ano}` para gerar esse conjunto de dados.")
    st.stop()

votacao = _votacao_cache(ano)

st.subheader("Onde e quem")
if info_cargo["municipal"]:
    municipio_escolhido = st.selectbox("Município", options=NOMES_MUNICIPIOS)
    municipios_filtro = [municipio_escolhido.upper()]
else:
    municipios_selecionados = st.multiselect(
        "Município (deixe vazio para o estado inteiro)",
        options=NOMES_MUNICIPIOS,
        default=[],
        help=f"{cargo_escolhido} tem o(a) mesmo(a) candidato(a) nos 92 municípios do RJ; use isso só "
        "pra focar numa região, não é filtro obrigatório como em vereador/prefeito.",
    )
    municipios_filtro = [m.upper() for m in municipios_selecionados]

turnos = turnos_disponiveis(votacao, cargo_escolhido, municipios_filtro[0] if info_cargo["municipal"] else None)
if not turnos:
    st.warning(f"Sem dados de {cargo_escolhido.lower()} para esse recorte.")
    st.stop()
turno_escolhido = (
    st.radio("Turno", options=turnos, horizontal=True, format_func=lambda t: f"{t}º turno")
    if len(turnos) > 1
    else turnos[0]
)

apenas_eleitos = st.checkbox(
    "Mostrar só quem foi eleito", value=cargo_escolhido in CARGOS_MUITOS_CANDIDATOS
)
lista_candidatos = candidatos(
    votacao, cargo_escolhido, turno_escolhido, municipios=municipios_filtro or None, apenas_eleitos=apenas_eleitos
)
if lista_candidatos.empty:
    st.warning("Nenhum candidato encontrado para esse recorte.")
    st.stop()

opcoes_candidato = {
    f"{linha.candidato} ({linha.partido}), {linha.votos:,} votos, {linha.situacao.lower()}".replace(",", "."): (
        linha.sq_candidato
    )
    for linha in lista_candidatos.itertuples()
}
escolha = st.selectbox(f"Candidato a {cargo_escolhido.lower()}", options=list(opcoes_candidato.keys()))
sq_escolhido = opcoes_candidato[escolha]

st.subheader("Onde estão os votos dele(a)")
por_zona = votos_por_zona(votacao, sq_escolhido, municipios=municipios_filtro or None)
total_votos = int(por_zona["votos"].sum())
concentracao_top3 = round(por_zona.head(3)["percentual"].sum(), 1)

recorte_ativo = bool(municipios_filtro) and not info_cargo["municipal"]
rotulo_total = "Total de votos no recorte" if recorte_ativo else "Total de votos"

coluna_a, coluna_b = st.columns(2)
coluna_a.metric(rotulo_total, f"{total_votos:,}".replace(",", "."))
coluna_b.metric("Concentração nas 3 zonas mais fortes", f"{concentracao_top3}%")
texto_concentracao = (
    "Quanto maior essa concentração, mais o candidato depende de poucas zonas específicas "
    "(um curral eleitoral mais forte); quanto mais baixa, mais espalhado é o voto dele pelo "
    "recorte escolhido."
)
if recorte_ativo:
    texto_concentracao += " Com município selecionado, os dois números acima já valem só pra ele, não pro RJ inteiro."
st.caption(texto_concentracao)

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
zona_geometria = _zonas_geometria_cache(setores, locais, tuple(municipios_filtro))

municipio_geometria = None
if municipios_filtro:
    gdf_municipios = carregar_geodataframe().to_crs(CRS_PROJETADA)
    municipio_geometria = gdf_municipios[gdf_municipios["name"].str.upper().isin(municipios_filtro)]

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
