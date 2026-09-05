"""Mapa do perfil do eleitorado por zona ou por bairro, colorido por uma métrica de filtro.

Reaproveita a geometria de `areas_influencia.py` (setor censitário
atribuído ao local de votação mais próximo), mas colore cada zona ou
bairro por um valor calculado em `perfil_eleitorado.py`/
`perfil_eleitorado_bairro.py` (número ou percentual de eleitores que
passam num filtro), não por uma cor categórica. Pode restringir a um
recorte de município (um candidato a vereador só disputa no próprio
município, não faz sentido mostrar área de outros) e/ou dar zoom só nas
zonas ou bairros de maior valor dentro desse recorte.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from areas_influencia import CRS_PROJETADA, calcular_areas_influencia
from mapa_municipal import CORES_MAPA, carregar_geodataframe


def carregar_zonas_geometria(
    setores: gpd.GeoDataFrame, locais_votacao: pd.DataFrame, municipios: list[str] | None = None
) -> gpd.GeoDataFrame:
    """Geometria de cada zona eleitoral do RJ, uma linha por zona (165 no total).

    Com `municipios` (nomes em maiúsculas, como em `locais_votacao["municipio"]`),
    cada zona é recortada só na parte cujo local de votação mais próximo é
    de um desses municípios: uma zona que cruza divisa aparece só com a
    fatia relevante, não inteira.
    """
    pontos = gpd.GeoDataFrame(
        locais_votacao,
        geometry=gpd.points_from_xy(locais_votacao["lon"], locais_votacao["lat"]),
        crs="EPSG:4326",
    )
    setores_com_local, areas = calcular_areas_influencia(setores, pontos)
    if municipios:
        setores_com_local = setores_com_local[setores_com_local["municipio"].isin(municipios)]
        areas = setores_com_local.dissolve(by="zona")
    return areas.reset_index()[["zona", "geometry"]]


def carregar_bairros_geometria(
    setores: gpd.GeoDataFrame, locais_votacao: pd.DataFrame, municipio: str
) -> gpd.GeoDataFrame:
    """Geometria de cada bairro de um único município (nome em maiúsculas).

    Mesma lógica de `carregar_zonas_geometria`, só que dissolvida por
    bairro em vez de por zona, e sempre restrita a um município (nome de
    bairro se repete entre municípios, então não faz sentido dissolver
    sem esse recorte).
    """
    pontos = gpd.GeoDataFrame(
        locais_votacao,
        geometry=gpd.points_from_xy(locais_votacao["lon"], locais_votacao["lat"]),
        crs="EPSG:4326",
    )
    setores_com_local, _ = calcular_areas_influencia(setores, pontos)
    setores_do_municipio = setores_com_local[setores_com_local["municipio"] == municipio]
    bairros = setores_do_municipio.dissolve(by="bairro")
    return bairros.reset_index()[["bairro", "geometry"]]


def montar_mapa_perfil(
    zonas_geometria: gpd.GeoDataFrame,
    valores_por_zona: pd.Series,
    legenda: str,
    zonas_alvo: list[str] | None = None,
    municipios_geometria: gpd.GeoDataFrame | None = None,
    coluna_unidade: str = "zona",
):
    """Mapa coroplético por zona (ou por bairro, com `coluna_unidade="bairro"`).

    `municipios_geometria`, se passado, troca o contorno de fundo (estado
    inteiro) pelos municípios selecionados e já enquadra a vista neles.
    `zonas_alvo` (nomes de zona ou de bairro, conforme `coluna_unidade`)
    desenha a borda em âmbar nessas unidades e tem prioridade sobre
    `municipios_geometria` para o enquadramento, se as duas forem passadas
    juntas.
    """
    municipios = municipios_geometria if municipios_geometria is not None else carregar_geodataframe().to_crs(CRS_PROJETADA)
    zonas = zonas_geometria.copy()
    zonas["valor"] = zonas[coluna_unidade].map(valores_por_zona).fillna(0)

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

    limite_zoom = None
    if zonas_alvo:
        destaque = zonas[zonas[coluna_unidade].isin(zonas_alvo)]
        destaque.boundary.plot(ax=ax, color="#C9922E", linewidth=1.4)
        limite_zoom = destaque.total_bounds
    elif municipios_geometria is not None:
        limite_zoom = municipios.total_bounds

    if limite_zoom is not None:
        minx, miny, maxx, maxy = limite_zoom
        margem_x = max((maxx - minx) * 0.2, 2500)
        margem_y = max((maxy - miny) * 0.2, 2500)
        ax.set_xlim(minx - margem_x, maxx + margem_x)
        ax.set_ylim(miny - margem_y, maxy + margem_y)

    ax.set_axis_off()
    fig.tight_layout()
    return fig
