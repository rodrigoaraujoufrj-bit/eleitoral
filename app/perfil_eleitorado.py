"""Perfil do eleitorado do RJ por zona eleitoral (TSE, perfil_secao agregado).

Ver `src/tratar_perfil_secao.py` para como
`data/processed/perfil_eleitorado_zona.parquet` é gerado: uma linha por
zona e combinação de gênero, faixa etária, grau de escolaridade e
raça/cor, com o total de eleitores naquela combinação. A combinação é
preservada (não cada dimensão separada) para permitir filtrar por mais de
uma dimensão ao mesmo tempo sem perder a relação entre elas.
"""

from pathlib import Path

import pandas as pd

PERFIL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "perfil_eleitorado_zona.parquet"

ORDEM_GENERO = ["FEMININO", "MASCULINO", "NÃO INFORMADO"]

ORDEM_FAIXA_ETARIA = [
    "16 anos",
    "17 anos",
    "18 anos",
    "19 anos",
    "20 anos",
    "21 a 24 anos",
    "25 a 29 anos",
    "30 a 34 anos",
    "35 a 39 anos",
    "40 a 44 anos",
    "45 a 49 anos",
    "50 a 54 anos",
    "55 a 59 anos",
    "60 a 64 anos",
    "65 a 69 anos",
    "70 a 74 anos",
    "75 a 79 anos",
    "80 a 84 anos",
    "85 a 89 anos",
    "90 a 94 anos",
    "95 a 99 anos",
    "100 anos ou mais",
    "Inválida",
]

ORDEM_ESCOLARIDADE = [
    "ANALFABETO",
    "LÊ E ESCREVE",
    "ENSINO FUNDAMENTAL INCOMPLETO",
    "ENSINO FUNDAMENTAL COMPLETO",
    "ENSINO MÉDIO INCOMPLETO",
    "ENSINO MÉDIO COMPLETO",
    "SUPERIOR INCOMPLETO",
    "SUPERIOR COMPLETO",
    "NÃO INFORMADO",
]

ORDEM_RACA_COR = ["Branca", "Parda", "Preta", "Amarela", "Indígena", "NÃO INFORMADO"]


def perfil_eleitorado_disponivel() -> bool:
    return PERFIL_PATH.exists()


def carregar_perfil_eleitorado() -> pd.DataFrame:
    return pd.read_parquet(PERFIL_PATH)


def eleitores_por_zona(
    perfil: pd.DataFrame,
    generos: list[str],
    faixas_etarias: list[str],
    escolaridades: list[str],
    racas_cor: list[str],
) -> pd.DataFrame:
    """Eleitores que passam no filtro e total da zona, por zona.

    Devolve todas as 165 zonas, mesmo as com zero eleitores no filtro. Uma
    zona pode abranger mais de um município (183 combinações de município
    e zona para 165 zonas no RJ); nesse caso "municipio" traz os nomes
    separados por "/", do que tem mais eleitores na zona para o que tem
    menos.
    """
    totais = perfil.groupby("zona", as_index=False)["eleitores"].sum().rename(columns={"eleitores": "eleitores_zona"})
    municipios_por_zona = (
        perfil.groupby(["zona", "municipio"], as_index=False)["eleitores"]
        .sum()
        .sort_values("eleitores", ascending=False)
        .groupby("zona")["municipio"]
        .apply(" / ".join)
    )
    totais["municipio"] = totais["zona"].map(municipios_por_zona)

    filtrado = perfil[
        perfil["genero"].isin(generos)
        & perfil["faixa_etaria"].isin(faixas_etarias)
        & perfil["escolaridade"].isin(escolaridades)
        & perfil["raca_cor"].isin(racas_cor)
    ]
    filtrado_zona = (
        filtrado.groupby("zona", as_index=False)["eleitores"].sum().rename(columns={"eleitores": "eleitores_filtro"})
    )

    resultado = totais.merge(filtrado_zona, on="zona", how="left")
    resultado["eleitores_filtro"] = resultado["eleitores_filtro"].fillna(0).astype(int)
    resultado["percentual"] = (resultado["eleitores_filtro"] / resultado["eleitores_zona"] * 100).fillna(0)
    return resultado
