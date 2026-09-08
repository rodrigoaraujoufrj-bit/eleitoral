"""Votação real por candidato, resultado de eleição passada (TSE).

Diferente de `perfil_eleitorado.py` (composição demográfica, uma
aproximação de quem mora onde), isto é voto de verdade: onde um candidato
específico teve força na eleição anterior, o "curral eleitoral" dele. Ver
`src/tratar_resultados.py` para como os parquets em `data/processed/` são
gerados a partir de `data/raw/resultados/`.
"""

from pathlib import Path

import pandas as pd

DATA_PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"


def resultados_disponivel(ano: int) -> bool:
    return (DATA_PROCESSED / f"votacao_{ano}.parquet").exists()


def carregar_votacao(ano: int) -> pd.DataFrame:
    return pd.read_parquet(DATA_PROCESSED / f"votacao_{ano}.parquet")


def turnos_disponiveis(votacao: pd.DataFrame, municipio: str, cargo: str) -> list[str]:
    filtro = votacao[(votacao["municipio"] == municipio) & (votacao["cargo"] == cargo)]
    return sorted(filtro["turno"].unique())


def candidatos_do_municipio(votacao: pd.DataFrame, municipio: str, cargo: str, turno: str) -> pd.DataFrame:
    """Um candidato por linha, com total de votos e situação, do mais votado pro menos."""
    filtro = votacao[
        (votacao["municipio"] == municipio) & (votacao["cargo"] == cargo) & (votacao["turno"] == turno)
    ]
    return (
        filtro.groupby(["sq_candidato", "candidato", "partido", "situacao"], as_index=False)["votos"]
        .sum()
        .sort_values("votos", ascending=False)
    )


def votos_por_zona(votacao: pd.DataFrame, sq_candidato: str) -> pd.DataFrame:
    """Votos de um candidato específico, por zona, com o percentual do total dele em cada uma."""
    do_candidato = votacao[votacao["sq_candidato"] == sq_candidato]
    por_zona = do_candidato.groupby("zona", as_index=False)["votos"].sum()
    total = por_zona["votos"].sum()
    por_zona["percentual"] = (por_zona["votos"] / total * 100) if total else 0
    return por_zona.sort_values("votos", ascending=False)
