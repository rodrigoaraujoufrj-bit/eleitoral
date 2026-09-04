"""Locais de votação do RJ, eleição de 04/10/2026.

Fonte: dados abertos do TSE, conjunto "Local de votação" (ver
data/raw/locais_votacao/leiame.pdf). O CSV bruto tem uma linha por seção
eleitoral; aqui ele é agregado para uma linha por local físico (uma escola
pode ter várias seções).

Requer que data/raw/locais_votacao/eleitorado_local_votacao_2026_RJ.csv já
tenha sido restaurado (python src/restaurar_dados.py).
"""

from pathlib import Path

import pandas as pd

CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "locais_votacao"
    / "eleitorado_local_votacao_2026_RJ.csv"
)

COLUNAS = {
    "NM_MUNICIPIO": "municipio",
    "NR_ZONA": "zona",
    "NM_LOCAL_VOTACAO": "local",
    "DS_ENDERECO": "endereco",
    "NM_BAIRRO": "bairro",
    "NR_LATITUDE": "lat",
    "NR_LONGITUDE": "lon",
    "DS_SITU_SECAO_ACESSIBILIDADE": "acessibilidade",
}


def locais_votacao_disponivel() -> bool:
    return CSV_PATH.exists()


def carregar_locais_votacao() -> pd.DataFrame:
    """Um local de votação por linha, só os que têm coordenada válida."""
    bruto = pd.read_csv(CSV_PATH, sep=";", encoding="latin-1", dtype=str)
    bruto = bruto[bruto["NR_LATITUDE"] != "-1"].copy()

    bruto["lat"] = bruto["NR_LATITUDE"].str.replace(",", ".").astype(float)
    bruto["lon"] = bruto["NR_LONGITUDE"].str.replace(",", ".").astype(float)
    bruto["eleitores_secao"] = pd.to_numeric(bruto["QT_ELEITOR_SECAO"], errors="coerce").fillna(0)

    agrupado = (
        bruto.groupby(["NM_MUNICIPIO", "NR_LOCAL_VOTACAO"], as_index=False)
        .agg(
            municipio=("NM_MUNICIPIO", "first"),
            zona=("NR_ZONA", "first"),
            local=("NM_LOCAL_VOTACAO", "first"),
            endereco=("DS_ENDERECO", "first"),
            bairro=("NM_BAIRRO", "first"),
            lat=("lat", "first"),
            lon=("lon", "first"),
            secoes=("NR_SECAO", "nunique"),
            eleitores=("eleitores_secao", "sum"),
        )
    )
    return agrupado.drop(columns=["NM_MUNICIPIO", "NR_LOCAL_VOTACAO"])
