"""Quatro jeitos de mapa específicos do Curral Eleitoral, além do
coroplético contínuo por zona de `mapa_perfil_eleitorado.py`:

- **Dominância**: qual candidato foi o mais votado em cada zona, cor
  categórica (uma por candidato, os menos frequentes agrupados em
  "Outros" pra manter a legenda legível).
- **Comparação**: a vantagem, em pontos percentuais, de um candidato
  sobre outro em cada zona, cor divergente (âmbar de um lado, roxo do
  outro, neutro no meio).
- **Mapa de calor**: densidade de voto suavizada, num mapa interativo de
  verdade (Plotly + CARTO), não presa aos limites de zona como as
  outras duas e com nome de bairro/rua visível no fundo.
- **Hotspot**: ponto quente/frio estatisticamente significativo
  (Getis-Ord Gi*, ver `hotspot.py`), 7 categorias fixas.
"""

import math

import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from matplotlib import pyplot as plt

from areas_influencia import paleta_categorica
from hotspot import CATEGORIAS_EM_ORDEM
from mapa_municipal import CORES_CALOR_HEX, CORES_DIVERGENTE, carregar_geodataframe
from mapa_perfil_eleitorado import CRS_PROJETADA

COR_OUTROS = "#B7AFC2"  # cinza neutro, fora da paleta categórica (só roxo/magenta/âmbar)
COR_SEM_DADO = "#E4DEEA"

# Cores fixas e em ordem pro hotspot (Getis-Ord Gi*): âmbar pro "quente"
# (candidato mais forte ali do que se esperaria por acaso) e roxo pro "frio"
# (mais fraco do que o esperado), mesma convenção de cor da comparação entre
# 2 candidatos (CORES_DIVERGENTE). Reaproveita os tons já usados no resto do
# app (extremos de CORES_MAPA e o âmbar da identidade visual), não inventa
# cor nova. Zipado com CATEGORIAS_EM_ORDEM (de hotspot.py) pra não duplicar
# os nomes das 7 categorias em dois lugares.
CORES_HOTSPOT = dict(
    zip(CATEGORIAS_EM_ORDEM, ["#8C5A12", "#C9922E", "#E0B876", "#E4DEEA", "#C9A6D9", "#8A5FA8", "#2C2140"])
)


def _fundo_municipios(municipios_geometria: gpd.GeoDataFrame | None):
    municipios = municipios_geometria if municipios_geometria is not None else carregar_geodataframe().to_crs(CRS_PROJETADA)
    fig, ax = plt.subplots(figsize=(7, 8))
    municipios.plot(ax=ax, facecolor="#F1ECF6", edgecolor="#C9A6D9", linewidth=0.5)
    return fig, ax, municipios


def _aplicar_zoom(ax, limite_zoom):
    if limite_zoom is None:
        return
    minx, miny, maxx, maxy = limite_zoom
    margem_x = max((maxx - minx) * 0.2, 2500)
    margem_y = max((maxy - miny) * 0.2, 2500)
    ax.set_xlim(minx - margem_x, maxx + margem_x)
    ax.set_ylim(miny - margem_y, maxy + margem_y)


def montar_mapa_dominancia(
    zonas_geometria: gpd.GeoDataFrame,
    dominancia_por_zona: pd.DataFrame,
    municipios_geometria: gpd.GeoDataFrame | None = None,
    coluna_unidade: str = "zona",
):
    """`dominancia_por_zona`: colunas `zona` (ou `coluna_unidade`) e `categoria`
    (nome do candidato mais votado ali, ou "Outros"), uma linha por zona."""
    zonas = zonas_geometria.merge(
        dominancia_por_zona[[coluna_unidade, "categoria"]], on=coluna_unidade, how="left"
    )
    zonas["categoria"] = zonas["categoria"].fillna("Sem dado")
    categorias = sorted(c for c in zonas["categoria"].unique() if c not in ("Outros", "Sem dado"))
    cores = dict(zip(categorias, paleta_categorica(max(len(categorias), 1)).colors))
    cores["Outros"] = COR_OUTROS
    cores["Sem dado"] = COR_SEM_DADO

    fig, ax, municipios = _fundo_municipios(municipios_geometria)
    for categoria, cor in cores.items():
        subset = zonas[zonas["categoria"] == categoria]
        if subset.empty:
            continue
        subset.plot(ax=ax, color=cor, linewidth=0.3, edgecolor="#FAF8FB", label=categoria)
    ax.legend(loc="lower left", fontsize=7, frameon=True, title="Mais votado(a) na zona")

    if municipios_geometria is not None:
        _aplicar_zoom(ax, municipios.total_bounds)
    ax.set_axis_off()
    fig.tight_layout()
    return fig


def montar_mapa_hotspot(
    zonas_geometria: gpd.GeoDataFrame,
    hotspot_por_zona: pd.DataFrame,
    municipios_geometria: gpd.GeoDataFrame | None = None,
    coluna_unidade: str = "zona",
):
    """`hotspot_por_zona`: saída de `hotspot.calcular_hotspot`, colunas
    `zona` (ou `coluna_unidade`) e `classificacao` (uma das 7 categorias
    fixas de `hotspot.CATEGORIAS_EM_ORDEM`)."""
    zonas = zonas_geometria.merge(
        hotspot_por_zona[[coluna_unidade, "classificacao"]], on=coluna_unidade, how="left"
    )
    zonas["classificacao"] = zonas["classificacao"].fillna("Sem padrão significativo")

    fig, ax, municipios = _fundo_municipios(municipios_geometria)
    for categoria, cor in CORES_HOTSPOT.items():
        subset = zonas[zonas["classificacao"] == categoria]
        if subset.empty:
            continue
        subset.plot(ax=ax, color=cor, linewidth=0.3, edgecolor="#FAF8FB", label=categoria)
    ax.legend(loc="lower left", fontsize=6.5, frameon=True, title="Hotspot (Getis-Ord Gi*)")

    if municipios_geometria is not None:
        _aplicar_zoom(ax, municipios.total_bounds)
    ax.set_axis_off()
    fig.tight_layout()
    return fig


# `radius` do Densitymap é em pixel de tela, não em metro: um valor fixo
# fica bom demais num recorte (1 município, poucas dezenas de locais de
# votação espalhados) e ruim demais no outro (RJ inteiro, milhares de
# locais, quase colados uns nos outros na tela). Por isso o raio é
# calculado a partir de uma distância real fixa no chão (calibrada pela
# banda que o KDE antigo, em matplotlib, calculava sozinho pra esses
# mesmos dados: a versão nova busca o mesmo nível de suavização, só que
# com mapa de fundo): bbox estreito (1 município) vira raio grande em
# pixel, bbox largo (RJ inteiro) vira raio pequeno, sempre a mesma
# distância no mundo real.
_BANDA_ALVO_METROS = 1300
_LARGURA_RENDER_PX = 1200  # largura aproximada do gráfico no app; não dá pra saber o valor exato do lado do Python, sem JS reativo ao tamanho do container


def montar_mapa_calor_interativo(pontos: pd.DataFrame):
    """Densidade de voto suavizada, num mapa interativo de verdade (Plotly),
    com bairro/rua visível no fundo (CARTO).

    `pontos`: colunas `lat`, `lon` (WGS84) e `votos_estimados` (ver
    `votos_por_local`, em resultados_eleitorais.py). Diferente do
    coroplético por zona, não fica preso aos limites de zona: mostra onde
    o voto se concentra de fato, suavizado. Ao contrário da versão anterior
    (matplotlib, sem mapa de fundo), dá pra ver em que bairro ou rua o
    voto está de fato concentrado, não só uma mancha sem referência
    espacial nenhuma.
    """
    fig = go.Figure()
    if pontos.empty or pontos["votos_estimados"].sum() <= 0:
        fig.update_layout(map_style="carto-positron")
        return fig

    lon_min, lon_max = pontos["lon"].min(), pontos["lon"].max()
    lat_min, lat_max = pontos["lat"].min(), pontos["lat"].max()
    margem_lon = max((lon_max - lon_min) * 0.1, 0.015)
    margem_lat = max((lat_max - lat_min) * 0.1, 0.015)

    largura_graus = (lon_max + margem_lon) - (lon_min - margem_lon)
    lat_media = (lat_min + lat_max) / 2
    largura_metros = max(largura_graus * 111_320 * math.cos(math.radians(lat_media)), 1)
    raio = _BANDA_ALVO_METROS * _LARGURA_RENDER_PX / largura_metros
    raio = min(max(raio, 10), 90)

    escala = [[i / (len(CORES_CALOR_HEX) - 1), cor] for i, cor in enumerate(CORES_CALOR_HEX)]
    fig.add_trace(
        go.Densitymap(
            lat=pontos["lat"],
            lon=pontos["lon"],
            z=pontos["votos_estimados"],
            radius=raio,
            colorscale=escala,
            colorbar=dict(title=dict(text="Concentração<br>de voto"), tickvals=[]),
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        map=dict(
            style="carto-positron",
            bounds=dict(
                west=lon_min - margem_lon,
                east=lon_max + margem_lon,
                south=lat_min - margem_lat,
                north=lat_max + margem_lat,
            ),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
    )
    return fig


def montar_mapa_comparacao(
    zonas_geometria: gpd.GeoDataFrame,
    vantagem_por_zona: pd.Series,
    legenda: str,
    zonas_alvo: list[str] | None = None,
    municipios_geometria: gpd.GeoDataFrame | None = None,
    coluna_unidade: str = "zona",
):
    """`vantagem_por_zona`: Série indexada por zona (ou `coluna_unidade`) com a
    vantagem em pontos percentuais de um candidato sobre outro (negativo
    quando o segundo vence). A faixa de cor é sempre simétrica em torno de
    0, pra manter a cor neutra sempre no empate técnico."""
    zonas = zonas_geometria.copy()
    zonas["valor"] = zonas[coluna_unidade].map(vantagem_por_zona).fillna(0)
    limite = max(abs(zonas["valor"].min()), abs(zonas["valor"].max()), 1)

    fig, ax, municipios = _fundo_municipios(municipios_geometria)
    zonas.plot(
        ax=ax,
        column="valor",
        cmap=CORES_DIVERGENTE,
        vmin=-limite,
        vmax=limite,
        linewidth=0.3,
        edgecolor="#FAF8FB",
        legend=True,
        legend_kwds={"label": legenda, "shrink": 0.6},
    )

    limite_zoom = None
    if zonas_alvo:
        destaque = zonas[zonas[coluna_unidade].isin(zonas_alvo)]
        destaque.boundary.plot(ax=ax, color="#3A3040", linewidth=1.2)
        limite_zoom = destaque.total_bounds
    elif municipios_geometria is not None:
        limite_zoom = municipios.total_bounds
    _aplicar_zoom(ax, limite_zoom)

    ax.set_axis_off()
    fig.tight_layout()
    return fig
