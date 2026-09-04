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


def montar_mapa(municipios_rj: list, coluna: str, legenda: str, locais_votacao=None):
    """Mapa coroplético estático do RJ, colorindo cada município por `coluna`.

    Usa geopandas/matplotlib (sem depender de internet para tiles ou JS),
    já que este ambiente bloqueia os CDNs que um mapa interativo precisaria.

    `locais_votacao`, se passado, é um DataFrame com colunas "lat"/"lon"
    (ver app/locais_votacao.py) plotado como pontos por cima do mapa.
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

    if locais_votacao is not None and len(locais_votacao):
        ax.scatter(
            locais_votacao["lon"],
            locais_votacao["lat"],
            s=4,
            color="#C9922E",
            alpha=0.55,
            linewidths=0,
            label="Local de votação",
        )
        ax.legend(loc="lower left", fontsize=8, frameon=False)

    ax.set_axis_off()
    fig.tight_layout()
    return fig
