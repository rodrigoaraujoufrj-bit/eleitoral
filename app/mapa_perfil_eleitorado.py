"""Mapa do perfil do eleitorado por zona, colorido por uma métrica de filtro.

Reaproveita a geometria de zona de `areas_influencia.py` (setor censitário
atribuído ao local de votação mais próximo, dissolvido por zona), mas
colore cada zona por um valor calculado em `perfil_eleitorado.py` (número
ou percentual de eleitores que passam num filtro), não por uma cor
categórica por zona. Pode dar zoom só nas zonas de maior valor.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from areas_influencia import CRS_PROJETADA, calcular_areas_influencia
from mapa_municipal import CORES_MAPA, carregar_geodataframe


def carregar_zonas_geometria(setores: gpd.GeoDataFrame, locais_votacao: pd.DataFrame) -> gpd.GeoDataFrame:
    """Geometria de cada zona eleitoral do RJ, uma linha por zona (165 no total)."""
    pontos = gpd.GeoDataFrame(
        locais_votacao,
        geometry=gpd.points_from_xy(locais_votacao["lon"], locais_votacao["lat"]),
        crs="EPSG:4326",
    )
    _, areas = calcular_areas_influencia(setores, pontos)
    return areas.reset_index()[["zona", "geometry"]]


def montar_mapa_perfil(
    zonas_geometria: gpd.GeoDataFrame,
    valores_por_zona: pd.Series,
    legenda: str,
    zonas_alvo: list[str] | None = None,
):
    """Mapa coroplético por zona. Com `zonas_alvo`, dá zoom só nelas e destaca a borda."""
    municipios = carregar_geodataframe().to_crs(CRS_PROJETADA)
    zonas = zonas_geometria.copy()
    zonas["valor"] = zonas["zona"].map(valores_por_zona).fillna(0)

    fig, ax = plt.subplots(figsize=(7, 8))
    municipios.plot(ax=ax, facecolor="#F1ECF6", edgecolor="#C9A6D9", linewidth=0.5)
    zonas.plot(
        ax=ax,
        column="valor",
        cmap=CORES_MAPA,
        linewidth=0.3,
        edgecolor="#FAF8FB",
        legend=True,
        legend_kwds={"label": legenda, "shrink": 0.6},
    )

    if zonas_alvo:
        destaque = zonas[zonas["zona"].isin(zonas_alvo)]
        destaque.boundary.plot(ax=ax, color="#C9922E", linewidth=1.4)
        minx, miny, maxx, maxy = destaque.total_bounds
        margem_x = max((maxx - minx) * 0.25, 3000)
        margem_y = max((maxy - miny) * 0.25, 3000)
        ax.set_xlim(minx - margem_x, maxx + margem_x)
        ax.set_ylim(miny - margem_y, maxy + margem_y)

    ax.set_axis_off()
    fig.tight_layout()
    return fig
