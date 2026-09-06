import streamlit as st

from components import formatar_numero
from locais_votacao import carregar_locais_votacao, locais_votacao_disponivel
from mapa_municipal import carregar_geodataframe
from mapa_perfil_eleitorado import (
    CRS_PROJETADA,
    carregar_bairros_geometria,
    carregar_zonas_geometria,
    montar_mapa_perfil,
)
from municipios_rj import MUNICIPIOS_RJ
from perfil_eleitorado import (
    ORDEM_ESCOLARIDADE,
    ORDEM_FAIXA_ETARIA,
    ORDEM_GENERO,
    ORDEM_RACA_COR,
    carregar_perfil_eleitorado,
    eleitores_por_zona,
    perfil_eleitorado_disponivel,
)
from perfil_eleitorado_bairro import carregar_perfil_com_bairro, eleitores_por_bairro
from setores_censitarios import carregar_setores

NOMES_MUNICIPIOS = sorted(m["municipio"] for m in MUNICIPIOS_RJ)


@st.cache_data(show_spinner="Calculando a geometria de cada zona eleitoral...")
def _zonas_geometria_cache(_setores, _locais_votacao, municipios: tuple[str, ...]):
    return carregar_zonas_geometria(_setores, _locais_votacao, municipios=list(municipios) or None)


@st.cache_data(show_spinner="Calculando a geometria de cada bairro...")
def _bairros_geometria_cache(_setores, _locais_votacao, municipio: str):
    return carregar_bairros_geometria(_setores, _locais_votacao, municipio)


@st.cache_data(show_spinner="Cruzando o perfil do eleitorado com o bairro de cada local...")
def _perfil_com_bairro_cache(_locais_votacao):
    return carregar_perfil_com_bairro(_locais_votacao)


st.title("Perfil do Eleitorado por Zona")
st.caption(
    "Combine um recorte de município com filtros de gênero, faixa etária, escolaridade e "
    "raça/cor para ver em quais zonas eleitorais (ou bairros, dentro de 1 município) esse "
    "perfil está mais concentrado. Dado real do TSE (eleição de 04/10/2026), agregado a partir "
    "do conjunto perfil_secao. É composição demográfica do eleitorado registrado, não dado de "
    "comportamento, consumo ou intenção de voto."
)

if not perfil_eleitorado_disponivel():
    st.caption("Rode `python src/tratar_perfil_secao.py` para gerar esse conjunto de dados.")
    st.stop()

if not locais_votacao_disponivel():
    st.caption("Locais de votação: rode `python src/restaurar_dados.py` para restaurar esse conjunto de dados do TSE.")
    st.stop()

st.subheader("Onde")
municipios_selecionados = st.multiselect(
    "Município (deixe vazio para o estado inteiro)",
    options=NOMES_MUNICIPIOS,
    default=[],
    help="Um candidato a vereador ou prefeito só disputa no próprio município: escolha um ou "
    "mais para não misturar com áreas de fora.",
)
municipios_filtro = [m.upper() for m in municipios_selecionados]

opcoes_nivel = ["Zona eleitoral"]
if len(municipios_filtro) == 1:
    opcoes_nivel.append("Bairro")
if len(opcoes_nivel) > 1:
    nivel = st.radio("Nível de análise", options=opcoes_nivel, horizontal=True)
else:
    nivel = "Zona eleitoral"
    st.caption(
        "Selecione exatamente 1 município acima para analisar por bairro, uma unidade menor "
        "que zona eleitoral, mais útil para quem disputa vereador."
    )
rotulo_unidade = "Bairro" if nivel == "Bairro" else "Zona"

if len(municipios_filtro) == 1:
    dados_municipio = next(m for m in MUNICIPIOS_RJ if m["municipio"].upper() == municipios_filtro[0])
    locais_municipio = carregar_locais_votacao()
    eleitorado_municipio = locais_municipio.loc[
        locais_municipio["municipio"] == municipios_filtro[0], "eleitores"
    ].sum()
    vagas_vereador = dados_municipio["vereadores"]
    quociente = eleitorado_municipio / vagas_vereador
    st.info(
        f"**Quantos votos um vereador precisa em {dados_municipio['municipio']}?** O município "
        f"tem {vagas_vereador} vagas de vereador e {formatar_numero(eleitorado_municipio, 0)} "
        f"eleitores; dividindo os dois dá **{formatar_numero(quociente, 0)} votos** (o quociente "
        "eleitoral aproximado). Um candidato com essa votação praticamente garante uma vaga "
        "sozinho. Na prática, o sistema proporcional também depende do desempenho do "
        "partido/coligação inteiro, então boa parte dos vereadores eleitos historicamente tem "
        "votação abaixo disso; sem dado de eleição passada (fora do escopo deste projeto), não "
        "dá pra estimar esse número menor com precisão. Trate como teto de referência, não como "
        "meta mínima."
    )

st.subheader("Quem")
coluna_a, coluna_b = st.columns(2)
with coluna_a:
    generos = st.multiselect("Gênero", options=ORDEM_GENERO, default=ORDEM_GENERO)
    escolaridades = st.multiselect("Escolaridade", options=ORDEM_ESCOLARIDADE, default=ORDEM_ESCOLARIDADE)
with coluna_b:
    faixas_etarias = st.multiselect("Faixa etária", options=ORDEM_FAIXA_ETARIA, default=ORDEM_FAIXA_ETARIA)
    racas_cor = st.multiselect("Raça/cor", options=ORDEM_RACA_COR, default=ORDEM_RACA_COR)

if nivel == "Bairro":
    locais = carregar_locais_votacao()
    perfil_com_bairro = _perfil_com_bairro_cache(locais)
    resultado = eleitores_por_bairro(
        perfil_com_bairro, municipios_filtro[0], generos, faixas_etarias, escolaridades, racas_cor
    )
    resultado = resultado.rename(columns={"bairro": "unidade", "eleitores_unidade": "eleitores_total"})
else:
    perfil = carregar_perfil_eleitorado()
    resultado = eleitores_por_zona(
        perfil, generos, faixas_etarias, escolaridades, racas_cor, municipios=municipios_filtro or None
    )
    resultado = resultado.rename(columns={"zona": "unidade", "eleitores_zona": "eleitores_total"})

if resultado.empty:
    st.warning(f"Nenhum(a) {rotulo_unidade.lower()} encontrado(a) para esse recorte.")
    st.stop()

setores = carregar_setores()
if nivel == "Bairro":
    unidade_geometria = _bairros_geometria_cache(setores, carregar_locais_votacao(), municipios_filtro[0])
    coluna_geo = "bairro"
else:
    unidade_geometria = _zonas_geometria_cache(setores, carregar_locais_votacao(), tuple(municipios_filtro))
    coluna_geo = "zona"

area_km2_por_unidade = (unidade_geometria.geometry.area / 1_000_000).set_axis(unidade_geometria[coluna_geo])
resultado["area_km2"] = resultado["unidade"].map(area_km2_por_unidade)
resultado["densidade"] = resultado["eleitores_filtro"] / resultado["area_km2"]

st.subheader(f"{'Bairros' if nivel == 'Bairro' else 'Zonas'} onde esse perfil é mais forte")
metrica = st.radio(
    f"Ordenar {rotulo_unidade.lower()}s por",
    options=["Total de eleitores (número)", "Concentração na zona (%)", "Densidade (eleitores por km²)"],
    horizontal=True,
)
st.caption(
    "Total: quantos eleitores do recorte passam no filtro, em número absoluto. Concentração: "
    "desses eleitores, qual fração é do recorte todo, útil para achar onde um perfil é raro no "
    "resto mas forte ali. Densidade: eleitores do filtro por km², uma referência de onde a "
    "campanha de rua rende mais por área percorrida (não é dado de custo real, que este projeto "
    "não tem). Sem nenhum filtro de gênero/faixa/escolaridade/raça restrito, concentração é "
    "sempre 100%. Com município selecionado, todas já ignoram eleitores de fora dele."
)
coluna_metrica = {
    "Total de eleitores (número)": "eleitores_filtro",
    "Concentração na zona (%)": "percentual",
    "Densidade (eleitores por km²)": "densidade",
}[metrica]

teto = min(30, len(resultado))
piso = min(3, teto)
quantidade_alvo = st.slider(
    f"Quantos(as) {rotulo_unidade.lower()}s destacar", min_value=piso, max_value=teto, value=min(10, teto)
)

ordenado = resultado.sort_values(coluna_metrica, ascending=False)
unidades_alvo = ordenado.head(quantidade_alvo)["unidade"].tolist()

renomear = {
    "municipio": "Município",
    "unidade": rotulo_unidade,
    "eleitores_filtro": "Eleitores no filtro",
    "eleitores_total": f"Total de eleitores no(a) {rotulo_unidade.lower()}",
    "percentual": "Concentração (%)",
    "densidade": "Densidade (eleitores/km²)",
}
tabela = ordenado.head(quantidade_alvo).rename(columns=renomear)
tabela["Concentração (%)"] = tabela["Concentração (%)"].round(1)
tabela["Densidade (eleitores/km²)"] = tabela["Densidade (eleitores/km²)"].round(0)
colunas_tabela = [c for c in renomear.values() if c in tabela.columns]
st.dataframe(tabela[colunas_tabela], hide_index=True, use_container_width=True)

sem_destaque = st.checkbox(f"Ver o recorte inteiro, sem destacar os(as) {rotulo_unidade.lower()}s de cima")

municipios_geometria = None
if municipios_filtro:
    gdf_municipios = carregar_geodataframe().to_crs(CRS_PROJETADA)
    municipios_geometria = gdf_municipios[gdf_municipios["name"].str.upper().isin(municipios_filtro)]

valores_por_unidade = resultado.set_index("unidade")[coluna_metrica]
legenda = {
    "eleitores_filtro": "Eleitores no filtro",
    "percentual": "Concentração (%)",
    "densidade": "Eleitores no filtro por km²",
}[coluna_metrica]
fig = montar_mapa_perfil(
    unidade_geometria,
    valores_por_unidade,
    legenda,
    zonas_alvo=None if sem_destaque else unidades_alvo,
    municipios_geometria=municipios_geometria,
    coluna_unidade=coluna_geo,
)
st.pyplot(fig, use_container_width=True)
