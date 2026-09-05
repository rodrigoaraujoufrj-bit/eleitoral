"""Perfil do eleitorado do RJ por bairro, dentro de um único município.

`perfil_secao` (usado em `perfil_eleitorado.py`) não traz bairro, só
`locais_votacao` traz. Este módulo junta os dois pela chave que têm em
comum: município + zona + número do local de votação (`numero_local`).

Só faz sentido dentro de um município: o mesmo nome de bairro (por
exemplo "Centro") se repete em municípios diferentes, então bairro sem
recorte de município misturaria lugares sem relação entre si.
"""

import pandas as pd

from perfil_eleitorado import PERFIL_PATH


def carregar_perfil_com_bairro(locais_votacao: pd.DataFrame) -> pd.DataFrame:
    """Perfil por local de votação (ver `src/tratar_perfil_secao.py`) com o bairro de cada um."""
    perfil = pd.read_parquet(PERFIL_PATH)
    mapa_bairro = locais_votacao[["municipio", "zona", "numero_local", "bairro"]].drop_duplicates()
    return perfil.merge(mapa_bairro, on=["municipio", "zona", "numero_local"], how="left")


def eleitores_por_bairro(
    perfil_com_bairro: pd.DataFrame,
    municipio: str,
    generos: list[str],
    faixas_etarias: list[str],
    escolaridades: list[str],
    racas_cor: list[str],
) -> pd.DataFrame:
    """Eleitores que passam no filtro e total do bairro, por bairro, dentro de um município."""
    perfil = perfil_com_bairro[perfil_com_bairro["municipio"] == municipio]

    totais = (
        perfil.groupby("bairro", as_index=False)["eleitores"].sum().rename(columns={"eleitores": "eleitores_unidade"})
    )

    filtrado = perfil[
        perfil["genero"].isin(generos)
        & perfil["faixa_etaria"].isin(faixas_etarias)
        & perfil["escolaridade"].isin(escolaridades)
        & perfil["raca_cor"].isin(racas_cor)
    ]
    filtrado_bairro = (
        filtrado.groupby("bairro", as_index=False)["eleitores"].sum().rename(columns={"eleitores": "eleitores_filtro"})
    )

    resultado = totais.merge(filtrado_bairro, on="bairro", how="left")
    resultado["eleitores_filtro"] = resultado["eleitores_filtro"].fillna(0).astype(int)
    resultado["percentual"] = (resultado["eleitores_filtro"] / resultado["eleitores_unidade"] * 100).fillna(0)
    return resultado
