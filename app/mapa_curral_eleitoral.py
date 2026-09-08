"""Três jeitos de mapa específicos do Curral Eleitoral, além do coroplético
contínuo por zona de `mapa_perfil_eleitorado.py`:

- **Dominância**: qual candidato foi o mais votado em cada zona, cor
  categórica (uma por candidato, os menos frequentes agrupados em
  "Outros" pra manter a legenda legível).
- **Comparação**: a vantagem, em pontos percentuais, de um candidato
  sobre outro em cada zona, cor divergente (âmbar de um lado, roxo do
  outro, neutro no meio).
- **Mapa de calor**: densidade de voto suavizada (KDE), não presa aos
  limites de zona como as outras duas.
"""

import geopandas as gpd
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import gaussian_kde
from shapely import contains_xy

from areas_influencia import paleta_categorica
from mapa_municipal import CORES_CALOR, CORES_DIVERGENTE, carregar_geodataframe
from mapa_perfil_eleitorado import CRS_PROJETADA

COR_OUTROS = "#B7AFC2"  # cinza neutro, fora da paleta categórica (só roxo/magenta/âmbar)
COR_SEM_DADO = "#E4DEEA"


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


def montar_mapa_calor(
    pontos: pd.DataFrame,
    municipios_geometria: gpd.GeoDataFrame | None = None,
    resolucao: int = 220,
):
    """Densidade de voto suavizada (KDE), a partir de pontos com peso.

    `pontos`: colunas `lat`, `lon` (WGS84) e `votos_estimados` (ver
    `votos_por_local`, em resultados_eleitorais.py). Diferente do
    coroplético por zona, não fica preso aos limites de zona: mostra onde
    o voto se concentra de fato dentro de cada uma, suavizado. A grade é
    recortada pelo contorno dos municípios (fora dele fica transparente,
    sem inventar voto em área sem gente).
    """
    municipios = municipios_geometria if municipios_geometria is not None else carregar_geodataframe().to_crs(CRS_PROJETADA)
    area = municipios.union_all()

    pontos_proj = gpd.GeoDataFrame(
        pontos, geometry=gpd.points_from_xy(pontos["lon"], pontos["lat"]), crs="EPSG:4326"
    ).to_crs(CRS_PROJETADA)
    xs = pontos_proj.geometry.x.to_numpy()
    ys = pontos_proj.geometry.y.to_numpy()
    pesos = pontos_proj["votos_estimados"].to_numpy()

    fig, ax = plt.subplots(figsize=(7, 8))
    municipios.plot(ax=ax, facecolor="#F1ECF6", edgecolor="#C9A6D9", linewidth=0.5)

    if pesos.sum() <= 0 or len(xs) < 2:
        ax.set_axis_off()
        fig.tight_layout()
        return fig

    kde = gaussian_kde(np.vstack([xs, ys]), weights=pesos)

    xmin, ymin, xmax, ymax = area.bounds
    margem_x, margem_y = (xmax - xmin) * 0.05, (ymax - ymin) * 0.05
    xmin, xmax, ymin, ymax = xmin - margem_x, xmax + margem_x, ymin - margem_y, ymax + margem_y

    grade_x, grade_y = np.mgrid[xmin : xmax : complex(resolucao), ymin : ymax : complex(resolucao)]
    grade_z = kde(np.vstack([grade_x.ravel(), grade_y.ravel()])).reshape(grade_x.shape)
    dentro = contains_xy(area, grade_x, grade_y)
    grade_z = np.where(dentro, grade_z, np.nan)

    valores_validos = grade_z[~np.isnan(grade_z)]
    if valores_validos.size:
        vmin, vmax = float(valores_validos.min()), float(valores_validos.max())
        # Opacidade cresce com a densidade (raiz quadrada pra subir rápido no
        # começo): onde tem pouco voto fica quase transparente, deixando o
        # contorno de fundo aparecer, e só "acende" nas concentrações reais.
        # Um imshow com opacidade fixa aqui ficava ilegível: a cor mais clara
        # da paleta (extremo "menos voto") é quase idêntica ao fundo do mapa,
        # então sem isso a maior parte do estado não mostrava nada.
        normalizado = np.clip((grade_z - vmin) / (vmax - vmin), 0, 1)
        opacidade = np.where(np.isnan(grade_z), 0, normalizado**0.5)

        # zorder explícito: imshow nasce com zorder mais baixo que o
        # preenchimento dos municípios (um Patch), sem isso o calor fica
        # escondido atrás dele, apesar de ser desenhado depois.
        ax.imshow(
            grade_z.T,
            extent=(xmin, xmax, ymin, ymax),
            origin="lower",
            cmap=CORES_CALOR,
            norm=plt.Normalize(vmin=vmin, vmax=vmax),
            alpha=opacidade.T,
            interpolation="bilinear",
            zorder=2,
        )
        sm = plt.cm.ScalarMappable(cmap=CORES_CALOR, norm=plt.Normalize(vmin=vmin, vmax=vmax))
        cbar = fig.colorbar(sm, ax=ax, shrink=0.6)
        cbar.set_label("Concentração de voto")
        cbar.set_ticks([vmin, vmax])
        cbar.set_ticklabels(["Menor", "Maior"])

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_axis_off()
    fig.tight_layout()
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
