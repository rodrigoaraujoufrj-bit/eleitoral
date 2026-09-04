"""Setores censitários do RJ, Censo 2022 (IBGE).

Fonte: pacote `geobr` (Ipea), que espelha os dados oficiais do IBGE em
releases do GitHub (`github.com/ipea/geobr_prep_data`), já que o servidor
do próprio IBGE (geoftp.ibge.gov.br) está bloqueado nesta sessão. Usada a
versão "simplified" (geometria com simplificação topológica), consistente
com o nível de detalhe já usado no contorno dos municípios.

O arquivo nacional (42.270 setores do RJ dentro de ~473 mil do Brasil
inteiro) foi filtrado para `abbrev_state == "RJ"` e salvo em parquet
(GeoParquet), bem mais compacto que GeoJSON para essa quantidade de
polígonos.
"""

from pathlib import Path

import geopandas as gpd

SETORES_PATH = Path(__file__).resolve().parent / "geo" / "rj_setores_censitarios.parquet"


def carregar_setores() -> gpd.GeoDataFrame:
    return gpd.read_parquet(SETORES_PATH)
