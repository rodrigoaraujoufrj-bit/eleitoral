"""Votação real por candidato, resultado de eleição passada (TSE).

Diferente de `perfil_eleitorado.py` (composição demográfica, uma
aproximação de quem mora onde), isto é voto de verdade: onde um candidato
específico teve força na eleição anterior, o "curral eleitoral" dele. Ver
`src/tratar_resultados.py` para como os parquets em `data/processed/` são
gerados a partir de `data/raw/resultados/`.

Cobre dois grupos de cargo, cada um num ano diferente (ver README, seção
"Curral eleitoral"): vereador e prefeito (2024, um município só disputa
dentro de si mesmo) e governador, senador, deputado estadual e deputado
federal (2022, mesmo candidato em todos os 92 municípios do RJ).
"""

from pathlib import Path

import pandas as pd

DATA_PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"

# Situações do TSE que significam "ganhou a vaga" (o resto, como SUPLENTE ou
# NÃO ELEITO, não). Usado só pra filtro opcional de "mostrar só eleitos",
# necessário nos cargos proporcionais (deputado estadual/federal), que têm
# mais de mil candidatos no RJ.
SITUACOES_ELEITO = {"ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA"}


def resultados_disponivel(ano: int) -> bool:
    return (DATA_PROCESSED / f"votacao_{ano}.parquet").exists()


def carregar_votacao(ano: int) -> pd.DataFrame:
    return pd.read_parquet(DATA_PROCESSED / f"votacao_{ano}.parquet")


def turnos_disponiveis(votacao: pd.DataFrame, cargo: str, municipio: str | None = None) -> list[str]:
    filtro = votacao[votacao["cargo"] == cargo]
    if municipio is not None:
        filtro = filtro[filtro["municipio"] == municipio]
    return sorted(filtro["turno"].unique())


def candidatos(
    votacao: pd.DataFrame,
    cargo: str,
    turno: str,
    municipios: list[str] | None = None,
    apenas_eleitos: bool = False,
) -> pd.DataFrame:
    """Um candidato por linha, com total de votos e situação, do mais votado pro menos.

    `municipios=None` é o RJ inteiro (o único jeito de ver cargos estaduais/
    federais, que não têm disputa por município); uma lista restringe a esses
    municípios, útil pra achar quem teve voto numa região específica mesmo
    num cargo com candidatos demais pra listar todos.
    """
    filtro = votacao[(votacao["cargo"] == cargo) & (votacao["turno"] == turno)]
    if municipios:
        filtro = filtro[filtro["municipio"].isin(municipios)]
    agrupado = (
        filtro.groupby(["sq_candidato", "candidato", "partido", "situacao"], as_index=False)["votos"]
        .sum()
        .sort_values("votos", ascending=False)
    )
    if apenas_eleitos:
        agrupado = agrupado[agrupado["situacao"].isin(SITUACOES_ELEITO)]
    return agrupado


def votos_por_zona(votacao: pd.DataFrame, sq_candidato: str, turno: str, municipios: list[str] | None = None) -> pd.DataFrame:
    """Votos de um candidato específico, por zona, com o percentual do total dele em cada uma.

    `turno` é obrigatório: `sq_candidato` não muda entre turnos (é a mesma
    candidatura), então sem esse filtro um candidato que foi pro 2º turno
    (Niterói e Petrópolis, prefeito, 2024) apareceria com o voto dos dois
    turnos somado, dado sem sentido (são disputas diferentes, com
    concorrentes diferentes). `municipios` restringe tanto a votação
    somada quanto o total usado no percentual ao recorte escolhido (mesma
    lógica de `eleitores_por_zona` em `perfil_eleitorado.py`): com um
    recorte ativo, os números passam a valer só dentro dele, não do
    estado inteiro.
    """
    do_candidato = votacao[(votacao["sq_candidato"] == sq_candidato) & (votacao["turno"] == turno)]
    if municipios:
        do_candidato = do_candidato[do_candidato["municipio"].isin(municipios)]
    por_zona = do_candidato.groupby("zona", as_index=False)["votos"].sum()
    total = por_zona["votos"].sum()
    por_zona["percentual"] = (por_zona["votos"] / total * 100) if total else 0
    return por_zona.sort_values("votos", ascending=False)


def votos_por_local(
    votacao: pd.DataFrame,
    sq_candidato: str,
    turno: str,
    locais_votacao: pd.DataFrame,
    municipios: list[str] | None = None,
) -> pd.DataFrame:
    """Votos de um candidato específico, espalhados por local de votação (lat/lon).

    O TSE não publica voto por local, só por município e zona (ver README).
    Aqui, o voto de cada zona é distribuído entre os locais dela
    proporcional ao eleitorado de cada um, não ao voto real (que a gente
    não tem nesse nível): é uma aproximação, útil só pra alimentar o mapa
    de calor (`montar_mapa_calor`, em mapa_curral_eleitoral.py), que
    precisa de pontos, não de polígono de zona. Não confundir com dado
    real de local de votação.
    """
    por_zona = votos_por_zona(votacao, sq_candidato, turno, municipios)[["zona", "votos"]]
    locais = locais_votacao
    if municipios:
        locais = locais[locais["municipio"].isin(municipios)]
    locais = locais.merge(por_zona, on="zona", how="inner")
    eleitores_por_zona = locais["zona"].map(locais.groupby("zona")["eleitores"].sum())
    fracao = (locais["eleitores"] / eleitores_por_zona).where(eleitores_por_zona > 0, 0)
    locais["votos_estimados"] = locais["votos"] * fracao
    return locais[["lat", "lon", "votos_estimados"]]


def dominancia_por_zona(
    votacao: pd.DataFrame, cargo: str, turno: str, municipios: list[str] | None = None, top_n: int = 8
) -> pd.DataFrame:
    """Pra cada zona, o candidato mais votado ali (dominância real, olhando
    todo mundo que concorreu, não só quem foi filtrado na tela).

    Só os `top_n` que mais "ganham" zona viram categoria própria; o resto
    entra em "Outros", porque um cargo como deputado (mais de mil
    candidatos no RJ) deixaria a legenda do mapa ilegível sem agrupar.
    Retorna uma linha por zona, com `zona`, `candidato` (quem venceu de
    fato) e `categoria` (igual a `candidato`, exceto quando ele caiu no
    agrupamento "Outros").
    """
    filtro = votacao[(votacao["cargo"] == cargo) & (votacao["turno"] == turno)]
    if municipios:
        filtro = filtro[filtro["municipio"].isin(municipios)]
    por_candidato_zona = filtro.groupby(["zona", "sq_candidato", "candidato"], as_index=False)["votos"].sum()
    indice_vencedor = por_candidato_zona.groupby("zona")["votos"].idxmax()
    vencedor = por_candidato_zona.loc[indice_vencedor].reset_index(drop=True)

    mais_frequentes = vencedor["candidato"].value_counts().head(top_n).index
    vencedor["categoria"] = vencedor["candidato"].where(vencedor["candidato"].isin(mais_frequentes), "Outros")
    return vencedor


def comparar_candidatos_por_zona(
    votacao: pd.DataFrame, sq_candidato_a: str, sq_candidato_b: str, turno: str, municipios: list[str] | None = None
) -> pd.DataFrame:
    """Votos dos dois candidatos em cada zona, lado a lado, com a vantagem
    de A sobre B em pontos percentuais (negativa quando B vence ali)."""
    votos_a = votos_por_zona(votacao, sq_candidato_a, turno, municipios).set_index("zona")["votos"]
    votos_b = votos_por_zona(votacao, sq_candidato_b, turno, municipios).set_index("zona")["votos"]
    combinado = pd.concat([votos_a.rename("votos_a"), votos_b.rename("votos_b")], axis=1).fillna(0).reset_index()
    total = combinado["votos_a"] + combinado["votos_b"]
    combinado["vantagem_pct"] = ((combinado["votos_a"] - combinado["votos_b"]) / total.where(total > 0) * 100).fillna(0)
    return combinado
