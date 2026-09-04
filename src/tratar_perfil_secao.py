"""Agrega o perfil do eleitorado (TSE, perfil_secao) por zona eleitoral do RJ.

Lê data/raw/perfil_secao/perfil_eleitor_secao_2026_RJ.csv em pedaços (6,9
milhões de linhas, 1,7 GB) e soma QT_ELEITORES por zona e categoria, num
formato longo (município, zona, dimensão, categoria, eleitores), para as
quatro dimensões publicadas pelo TSE: gênero, faixa etária, grau de
escolaridade e raça/cor. Estado civil, identidade de gênero, quilombola e
intérprete de libras existem no CSV mas não entram aqui por enquanto.

Gera data/processed/perfil_eleitorado_zona.parquet. Não versionado (como o
resto de data/processed/), rode antes de usar algo que dependa dele:

    python src/tratar_perfil_secao.py
"""

from pathlib import Path

import pandas as pd

CSV_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "perfil_secao" / "perfil_eleitor_secao_2026_RJ.csv"
)
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "perfil_eleitorado_zona.parquet"

DIMENSOES = {
    "genero": "DS_GENERO",
    "faixa_etaria": "DS_FAIXA_ETARIA",
    "escolaridade": "DS_GRAU_ESCOLARIDADE",
    "raca_cor": "DS_RACA_COR",
}

COLUNAS_USO = ["CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "QT_ELEITORES", *DIMENSOES.values()]

CHAVE = ["CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "dimensao", "categoria"]


def processar(tamanho_pedaco: int = 500_000) -> pd.DataFrame:
    """Soma QT_ELEITORES por zona/dimensão/categoria, lendo o CSV em pedaços.

    Cada pedaço já é agregado (de ~500 mil linhas para algumas centenas)
    antes de acumular, então a soma final cabe em memória mesmo num CSV
    de 1,7 GB.
    """
    partes = []
    leitor = pd.read_csv(
        CSV_PATH, sep=";", encoding="latin-1", usecols=COLUNAS_USO, dtype=str, chunksize=tamanho_pedaco
    )
    for pedaco in leitor:
        pedaco["QT_ELEITORES"] = pd.to_numeric(pedaco["QT_ELEITORES"], errors="coerce").fillna(0)
        for dimensao, coluna in DIMENSOES.items():
            agrupado = (
                pedaco.groupby(["CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", coluna], as_index=False)["QT_ELEITORES"]
                .sum()
                .rename(columns={coluna: "categoria"})
            )
            agrupado.insert(3, "dimensao", dimensao)
            partes.append(agrupado)

    bruto = pd.concat(partes, ignore_index=True)
    return bruto.groupby(CHAVE, as_index=False)["QT_ELEITORES"].sum().rename(columns={"QT_ELEITORES": "eleitores"})


def main():
    final = processar()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    final.to_parquet(OUT_PATH, index=False)
    print(f"Gravado {OUT_PATH} com {len(final)} linhas.")


if __name__ == "__main__":
    main()
