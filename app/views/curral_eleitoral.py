import streamlit as st

from hotspot import calcular_hotspot, hotspot_disponivel
from locais_votacao import carregar_locais_votacao, locais_votacao_disponivel
from mapa_curral_eleitoral import (
    montar_mapa_calor,
    montar_mapa_comparacao,
    montar_mapa_dominancia,
    montar_mapa_hotspot,
)
from mapa_municipal import carregar_geodataframe
from mapa_perfil_eleitorado import CRS_PROJETADA, carregar_zonas_geometria, montar_mapa_perfil
from municipios_rj import MUNICIPIOS_RJ
from resultados_eleitorais import (
    candidatos,
    carregar_votacao,
    comparar_candidatos_por_zona,
    dominancia_por_zona,
    participacao_por_zona,
    resultados_disponivel,
    turnos_disponiveis,
    votos_por_local,
    votos_por_zona,
)
from setores_censitarios import carregar_setores

NOMES_MUNICIPIOS = sorted(m["municipio"] for m in MUNICIPIOS_RJ)
CANONICO = {m["municipio"].upper(): m["municipio"] for m in MUNICIPIOS_RJ}

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


def _slider_quantidade(rotulo: str, total: int, teto_padrao: int, valor_padrao: int) -> int:
    """Slider "quantas unidades destacar", só quando há de fato o que escolher.

    `st.slider` quebra se min_value == max_value (recorte pequeno, tipo um
    candidato com voto em só 1 ou 2 zonas): nesse caso mostra tudo, sem
    controle nenhum.
    """
    teto = min(teto_padrao, total)
    piso = min(3, teto)
    if teto > piso:
        return st.slider(rotulo, min_value=piso, max_value=teto, value=min(valor_padrao, teto))
    return teto


def _selectbox_candidato(lista_candidatos, rotulo: str, excluir_sq: str | None = None):
    candidatos_disponiveis = lista_candidatos if excluir_sq is None else lista_candidatos[
        lista_candidatos["sq_candidato"] != excluir_sq
    ]
    opcoes = {
        f"{linha.candidato} ({linha.partido}), {linha.votos:,} votos, {linha.situacao.lower()}".replace(",", "."): (
            linha.sq_candidato
        )
        for linha in candidatos_disponiveis.itertuples()
    }
    escolha = st.selectbox(rotulo, options=list(opcoes.keys()))
    return opcoes[escolha]


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

st.subheader("Onde")
if info_cargo["municipal"]:
    # Turno primeiro, não depois: só prefeito tem 2º turno, e só nalguns
    # municípios (Niterói e Petrópolis em 2024). Perguntar o turno antes
    # filtra o dropdown de município pra só quem de fato teve esse turno,
    # em vez de deixar escolher qualquer um dos 92 e só descobrir depois
    # que não tem 2º turno pra ele.
    turnos_do_cargo = turnos_disponiveis(votacao, cargo_escolhido)
    turno_escolhido = (
        st.radio("Turno", options=turnos_do_cargo, horizontal=True, format_func=lambda t: f"{t}º turno")
        if len(turnos_do_cargo) > 1
        else turnos_do_cargo[0]
    )
    municipios_do_turno = sorted(
        CANONICO.get(m, m)
        for m in votacao.loc[
            (votacao["cargo"] == cargo_escolhido) & (votacao["turno"] == turno_escolhido), "municipio"
        ].unique()
    )
    if len(municipios_do_turno) < len(NOMES_MUNICIPIOS):
        st.caption(
            f"Só {len(municipios_do_turno)} município(s) foram pro {turno_escolhido}º turno de "
            f"{cargo_escolhido.lower()} em {ano}: {', '.join(municipios_do_turno)}."
        )
    municipio_escolhido = st.selectbox("Município", options=municipios_do_turno)
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

    turnos = turnos_disponiveis(votacao, cargo_escolhido)
    if not turnos:
        st.warning(f"Sem dados de {cargo_escolhido.lower()} para esse recorte.")
        st.stop()
    turno_escolhido = (
        st.radio("Turno", options=turnos, horizontal=True, format_func=lambda t: f"{t}º turno")
        if len(turnos) > 1
        else turnos[0]
    )

recorte_ativo = bool(municipios_filtro) and not info_cargo["municipal"]

setores = carregar_setores()
locais = carregar_locais_votacao()
zona_geometria = _zonas_geometria_cache(setores, locais, tuple(municipios_filtro))
area_km2_por_zona = (zona_geometria.geometry.area / 1_000_000).set_axis(zona_geometria["zona"])

municipio_geometria = None
if municipios_filtro:
    gdf_municipios = carregar_geodataframe().to_crs(CRS_PROJETADA)
    municipio_geometria = gdf_municipios[gdf_municipios["name"].str.upper().isin(municipios_filtro)]

st.subheader("Visualização")
visualizacao = st.radio(
    "Visualização",
    options=["Um candidato", "Quem venceu em cada zona", "Comparar 2 candidatos"],
    horizontal=True,
)

if visualizacao == "Um candidato":
    apenas_eleitos = st.checkbox("Mostrar só quem foi eleito", value=cargo_escolhido in CARGOS_MUITOS_CANDIDATOS)
    lista_candidatos = candidatos(
        votacao, cargo_escolhido, turno_escolhido, municipios=municipios_filtro or None, apenas_eleitos=apenas_eleitos
    )
    if lista_candidatos.empty:
        st.warning("Nenhum candidato encontrado para esse recorte.")
        st.stop()
    sq_escolhido = _selectbox_candidato(lista_candidatos, f"Candidato a {cargo_escolhido.lower()}")

    st.subheader("Onde estão os votos dele(a)")
    por_zona = votos_por_zona(votacao, sq_escolhido, turno_escolhido, municipios=municipios_filtro or None)
    por_zona["area_km2"] = por_zona["zona"].map(area_km2_por_zona)
    por_zona["densidade"] = por_zona["votos"] / por_zona["area_km2"]
    total_votos = int(por_zona["votos"].sum())
    concentracao_top3 = round(por_zona.head(3)["percentual"].sum(), 1)

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

    opcoes_metrica = ["Votos absolutos", "Densidade (votos por km²)", "Mapa de calor"]
    if hotspot_disponivel(zona_geometria):
        opcoes_metrica.append("Hotspot (Getis-Ord Gi*)")
    metrica = st.radio(
        "Colorir o mapa por",
        options=opcoes_metrica,
        horizontal=True,
        help="Densidade evita que uma zona rural grande pareça 'mais forte' só por ter mais área "
        "(mostra votos por km², não voto total). Mapa de calor é uma densidade suavizada, sem "
        "ficar presa ao limite de cada zona: espalha o voto dela pelos locais de votação, "
        "proporcional ao eleitorado de cada um (o TSE não publica voto por local, então é mais "
        "uma aproximação, só pra esse mapa). Hotspot é diferente dos outros 3: um teste "
        "estatístico (Getis-Ord Gi*) que aponta onde o candidato é desproporcionalmente forte ou "
        "fraco comparado às zonas vizinhas, não só onde ele tem mais voto ou mais gente votando "
        "(some quando o recorte tem poucas zonas demais pra fazer sentido).",
    )
    if metrica in ("Mapa de calor", "Hotspot (Getis-Ord Gi*)"):
        coluna_metrica, legenda_mapa = "votos", "Votos"
    else:
        coluna_metrica, legenda_mapa = (
            ("votos", "Votos") if metrica == "Votos absolutos" else ("densidade", "Votos por km²")
        )

    quantidade_alvo = _slider_quantidade("Quantas zonas destacar", len(por_zona), teto_padrao=15, valor_padrao=5)
    zonas_alvo = por_zona.sort_values(coluna_metrica, ascending=False).head(quantidade_alvo)["zona"].tolist()

    tabela = por_zona.rename(
        columns={
            "zona": "Zona",
            "votos": "Votos",
            "percentual": "% do total do candidato",
            "densidade": "Votos por km²",
        }
    )
    tabela["% do total do candidato"] = tabela["% do total do candidato"].round(1)
    tabela["Votos por km²"] = tabela["Votos por km²"].round(1)
    st.dataframe(
        tabela[["Zona", "Votos", "% do total do candidato", "Votos por km²"]], hide_index=True, use_container_width=True
    )

    if metrica == "Mapa de calor":
        pontos = votos_por_local(votacao, sq_escolhido, turno_escolhido, locais, municipios=municipios_filtro or None)
        fig = montar_mapa_calor(pontos, municipios_geometria=municipio_geometria)
    elif metrica == "Hotspot (Getis-Ord Gi*)":
        participacao = participacao_por_zona(
            votacao, sq_escolhido, cargo_escolhido, turno_escolhido, municipios=municipios_filtro or None
        )
        valores_participacao = participacao.set_index("zona")["percentual_local"]
        hotspot_resultado = calcular_hotspot(zona_geometria, valores_participacao, coluna_unidade="zona")
        st.caption(
            "Compara o percentual de voto do candidato em cada zona (sobre o total de votos "
            "válidos dela, não sobre o total dele) com o das 6 zonas mais próximas, e testa se "
            "esse padrão é forte o bastante pra não ser só acaso. \"Ponto quente\" é onde ele é "
            "desproporcionalmente forte; \"ponto frio\", onde é desproporcionalmente fraco; a "
            "maioria das zonas fica \"sem padrão significativo\", o que é esperado (nem toda "
            "zona é um extremo estatístico)."
        )
        significativas = hotspot_resultado[hotspot_resultado["classificacao"] != "Sem padrão significativo"]
        if significativas.empty:
            st.caption("Nenhuma zona formou um padrão estatisticamente significativo pra esse candidato.")
        else:
            tabela_hotspot = (
                significativas.sort_values("z_score", key=abs, ascending=False)
                .rename(columns={"zona": "Zona", "valor": "% local", "z_score": "Z-score", "classificacao": "Classificação"})
            )
            tabela_hotspot["% local"] = tabela_hotspot["% local"].round(1)
            tabela_hotspot["Z-score"] = tabela_hotspot["Z-score"].round(2)
            st.dataframe(tabela_hotspot, hide_index=True, use_container_width=True)
        fig = montar_mapa_hotspot(zona_geometria, hotspot_resultado, municipios_geometria=municipio_geometria, coluna_unidade="zona")
    else:
        valores_por_zona = por_zona.set_index("zona")[coluna_metrica]
        fig = montar_mapa_perfil(
            zona_geometria,
            valores_por_zona,
            legenda_mapa,
            zonas_alvo=zonas_alvo,
            municipios_geometria=municipio_geometria,
            coluna_unidade="zona",
        )
    st.pyplot(fig, use_container_width=True)

elif visualizacao == "Quem venceu em cada zona":
    st.subheader("Quem foi o(a) mais votado(a) em cada zona")
    st.caption(
        "Dominância real: olha todo mundo que concorreu, não só um recorte. Os candidatos que "
        "mais vencem zonas ganham cor própria; o resto entra em \"Outros\" (cinza), senão a "
        "legenda vira uma sopa de cores num cargo com muitos candidatos."
    )
    dominancia = dominancia_por_zona(votacao, cargo_escolhido, turno_escolhido, municipios=municipios_filtro or None)

    ranking = (
        dominancia.groupby("candidato", as_index=False)
        .agg(zonas_vencidas=("zona", "count"))
        .sort_values("zonas_vencidas", ascending=False)
        .rename(columns={"candidato": "Candidato(a)", "zonas_vencidas": "Zonas vencidas"})
    )
    st.dataframe(ranking, hide_index=True, use_container_width=True)

    fig = montar_mapa_dominancia(
        zona_geometria, dominancia, municipios_geometria=municipio_geometria, coluna_unidade="zona"
    )
    st.pyplot(fig, use_container_width=True)

else:
    apenas_eleitos = st.checkbox("Mostrar só quem foi eleito", value=cargo_escolhido in CARGOS_MUITOS_CANDIDATOS)
    lista_candidatos = candidatos(
        votacao, cargo_escolhido, turno_escolhido, municipios=municipios_filtro or None, apenas_eleitos=apenas_eleitos
    )
    if len(lista_candidatos) < 2:
        st.warning("Esse recorte não tem 2 candidatos pra comparar.")
        st.stop()

    coluna_a, coluna_b = st.columns(2)
    with coluna_a:
        sq_a = _selectbox_candidato(lista_candidatos, "Candidato(a) A")
    with coluna_b:
        sq_b = _selectbox_candidato(lista_candidatos, "Candidato(a) B", excluir_sq=sq_a)

    comparacao = comparar_candidatos_por_zona(votacao, sq_a, sq_b, turno_escolhido, municipios=municipios_filtro or None)
    nome_a = lista_candidatos.loc[lista_candidatos["sq_candidato"] == sq_a, "candidato"].iloc[0]
    nome_b = lista_candidatos.loc[lista_candidatos["sq_candidato"] == sq_b, "candidato"].iloc[0]

    st.subheader(f"{nome_a} x {nome_b}, zona a zona")
    coluna_a, coluna_b = st.columns(2)
    coluna_a.metric(f"Zonas onde {nome_a} vence", int((comparacao["vantagem_pct"] > 0).sum()))
    coluna_b.metric(f"Zonas onde {nome_b} vence", int((comparacao["vantagem_pct"] < 0).sum()))
    st.caption(
        "Vantagem em pontos percentuais dos votos dos dois candidatos somados em cada zona: "
        "positivo é vantagem do A (roxo no mapa), negativo é vantagem do B (âmbar)."
    )

    comparacao_ordenada = comparacao.reindex(comparacao["vantagem_pct"].abs().sort_values(ascending=False).index)
    quantidade_alvo = _slider_quantidade(
        "Quantas zonas mais disputadas destacar", len(comparacao_ordenada), teto_padrao=15, valor_padrao=5
    )
    zonas_alvo = comparacao_ordenada.head(quantidade_alvo)["zona"].tolist()

    tabela = comparacao_ordenada.rename(
        columns={"zona": "Zona", "votos_a": f"Votos de {nome_a}", "votos_b": f"Votos de {nome_b}", "vantagem_pct": "Vantagem (p.p.)"}
    )
    tabela["Vantagem (p.p.)"] = tabela["Vantagem (p.p.)"].round(1)
    st.dataframe(tabela, hide_index=True, use_container_width=True)

    vantagem_por_zona = comparacao.set_index("zona")["vantagem_pct"]
    fig = montar_mapa_comparacao(
        zona_geometria,
        vantagem_por_zona,
        f"Vantagem de {nome_a} (roxo) x {nome_b} (âmbar), em p.p.",
        zonas_alvo=zonas_alvo,
        municipios_geometria=municipio_geometria,
        coluna_unidade="zona",
    )
    st.pyplot(fig, use_container_width=True)
