"""Trata a votação por candidato, município e zona (TSE, resultados de eleição).

Lê data/raw/resultados/votacao_candidato_munzona_<ano>_RJ.csv, seleciona só
as colunas relevantes pra achar "curral eleitoral" (onde um candidato
específico teve força de verdade, dado real de eleição passada, diferente
do perfil demográfico) e grava um parquet por ano em data/processed/.

Cada linha do CSV bruto já é um candidato numa zona (não precisa agregar
pedaço a pedaço como perfil_secao: RJ inteiro em 2024 são só ~80 mil
linhas). A exceção é filtrar fora eleições que não são a principal do ano
(ex.: uma eleição suplementar de Três Rios caiu junto no arquivo de 2024,
por causa de uma decisão judicial específica daquele município).

Uso:
    python src/tratar_resultados.py --ano 2024
    python src/tratar_resultados.py --ano 2022
"""

import argparse
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DATA_RAW = RAIZ / "data" / "raw" / "resultados"
DATA_PROCESSED = RAIZ / "data" / "processed"

# A eleição "principal" de cada ano, pra descartar eleições suplementares
# (de município específico, fora do calendário normal) que às vezes vêm
# junto no mesmo arquivo do TSE.
ELEICAO_PRINCIPAL = {
    2024: "ELEIÇÕES MUNICIPAIS 2024",
    2022: "ELEIÇÕES GERAIS ESTADUAIS 2022",
}

COLUNAS = {
    "NR_TURNO": "turno",
    "CD_MUNICIPIO": "cd_municipio",
    "NM_MUNICIPIO": "municipio",
    "NR_ZONA": "zona",
    "DS_CARGO": "cargo",
    "SQ_CANDIDATO": "sq_candidato",
    "NR_CANDIDATO": "nr_candidato",
    "NM_URNA_CANDIDATO": "candidato",
    "SG_PARTIDO": "partido",
    "NM_PARTIDO": "nome_partido",
    "QT_VOTOS_NOMINAIS": "votos",
    "DS_SIT_TOT_TURNO": "situacao",
}


def processar(ano: int) -> pd.DataFrame:
    csv_path = DATA_RAW / f"votacao_candidato_munzona_{ano}_RJ.csv"
    bruto = pd.read_csv(csv_path, sep=";", encoding="latin-1", dtype=str)
    bruto = bruto[bruto["DS_ELEICAO"] == ELEICAO_PRINCIPAL[ano]]

    tratado = bruto[list(COLUNAS)].rename(columns=COLUNAS)
    tratado["votos"] = pd.to_numeric(tratado["votos"], errors="coerce").fillna(0).astype(int)
    return tratado


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ano", type=int, required=True, choices=sorted(ELEICAO_PRINCIPAL))
    args = parser.parse_args()

    tratado = processar(args.ano)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    saida = DATA_PROCESSED / f"votacao_{args.ano}.parquet"
    tratado.to_parquet(saida, index=False)
    print(f"Gravado {saida} com {len(tratado)} linhas.")


if __name__ == "__main__":
    main()
