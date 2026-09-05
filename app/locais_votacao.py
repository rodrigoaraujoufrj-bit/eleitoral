"""Locais de votação do RJ, eleição de 04/10/2026.

Fonte: dados abertos do TSE, conjunto "Local de votação" (ver
data/raw/locais_votacao/leiame.pdf). O CSV bruto tem uma linha por seção
eleitoral; aqui ele é agregado para uma linha por local físico (uma escola
pode ter várias seções).

A chave do agrupamento é município + zona + NR_LOCAL_VOTACAO, não só
NR_LOCAL_VOTACAO: esse número se repete em zonas diferentes do mesmo
município, então agrupar sem a zona funde locais físicos distintos (dava
2.919 "locais únicos" em vez dos 5.040 corretos). O total oficial do TSE
para o RJ é 5.183 (autoatendimento eleitoral, tse.jus.br); a diferença de
~2,8% é provavelmente só a data de geração deste extrato.

O número original (`numero_local`) é mantido no resultado porque é a
mesma chave usada em `perfil_secao` (município + zona + NR_LOCAL_VOTACAO):
é assim que `perfil_eleitorado_bairro.py` cruza o perfil demográfico, que
não tem bairro, com o bairro de cada local, que só existe aqui.

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
        bruto.groupby(["NM_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO"], as_index=False)
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
    agrupado = agrupado.drop(columns=["NM_MUNICIPIO", "NR_ZONA"])
    agrupado = agrupado.rename(columns={"NR_LOCAL_VOTACAO": "numero_local"})
    agrupado.insert(0, "id_local", agrupado.index)
    return agrupado
