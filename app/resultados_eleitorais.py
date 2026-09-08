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


def votos_por_zona(votacao: pd.DataFrame, sq_candidato: str, municipios: list[str] | None = None) -> pd.DataFrame:
    """Votos de um candidato específico, por zona, com o percentual do total dele em cada uma.

    `municipios` restringe tanto a votação somada quanto o total usado no
    percentual ao recorte escolhido (mesma lógica de `eleitores_por_zona`
    em `perfil_eleitorado.py`): com um recorte ativo, os números passam a
    valer só dentro dele, não do estado inteiro.
    """
    do_candidato = votacao[votacao["sq_candidato"] == sq_candidato]
    if municipios:
        do_candidato = do_candidato[do_candidato["municipio"].isin(municipios)]
    por_zona = do_candidato.groupby("zona", as_index=False)["votos"].sum()
    total = por_zona["votos"].sum()
    por_zona["percentual"] = (por_zona["votos"] / total * 100) if total else 0
    return por_zona.sort_values("votos", ascending=False)
