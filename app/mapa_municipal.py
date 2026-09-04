from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

GEOJSON_PATH = Path(__file__).resolve().parent / "geo" / "rj_municipios.geojson"

# Mesma paleta do tema do app (lilás claro -> roxo ardósia), para o mapa
# combinar visualmente com o resto do site.
CORES_MAPA = LinearSegmentedColormap.from_list("eleitoral", ["#F1ECF6", "#C9A6D9", "#8A5FA8", "#2C2140"])


def carregar_geodataframe() -> gpd.GeoDataFrame:
    return gpd.read_file(GEOJSON_PATH)


def montar_mapa(municipios_rj: list, coluna: str, legenda: str):
    """Mapa coroplético estático do RJ, colorindo cada município por `coluna`.

    Usa geopandas/matplotlib (sem depender de internet para tiles ou JS),
    já que este ambiente bloqueia os CDNs que um mapa interativo precisaria.
    """
    gdf = carregar_geodataframe()
    dados = {m["municipio"]: m[coluna] for m in municipios_rj}
    gdf[coluna] = gdf["name"].map(dados)

    fig, ax = plt.subplots(figsize=(7, 8))
    gdf.plot(
        column=coluna,
        cmap=CORES_MAPA,
        linewidth=0.4,
        edgecolor="#FAF8FB",
        legend=True,
        legend_kwds={"label": legenda, "shrink": 0.6},
        ax=ax,
    )
    ax.set_axis_off()
    fig.tight_layout()
    return fig
