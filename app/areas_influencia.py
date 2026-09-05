"""Área de influência de cada zona eleitoral, usando setor censitário como referência.

Ideia: um Voronoi "puro" (feito só com os pontos dos locais de votação)
corta o espaço com linhas retas artificiais, que não respeitam nada do
território real. Aqui, cada setor censitário (a menor unidade geográfica
real do IBGE) é atribuído ao local de votação mais próximo do seu
centroide, a mesma lógica do Voronoi, mas decidida setor por setor.

A hierarquia eleitoral, da maior unidade para a menor, é zona, depois
local de votação, depois seção: uma zona reúne vários locais, e cada
local reúne várias seções. Atribuir cada setor ao local mais próximo (a
unidade do meio, 5.038 no RJ) gera áreas pequenas e picotadas nas regiões
mais densas, onde os locais ficam a poucas quadras uns dos outros. Por
isso os setores são dissolvidos por zona (a unidade de cima, 165 no RJ).

Mesmo por zona, dentro do município do Rio (49 zonas) as áreas ficam
espalhadas e intercaladas pelo território, não formam blocos únicos e
contíguos como um bairro: é assim mesmo que a divisão em zonas eleitorais
foi desenhada lá, não é erro de cálculo. Por isso o mapa usa preenchimento
colorido por zona (cada uma com uma cor), não só contorno: contorno vira
uma malha ilegível quando há muitas áreas pequenas lado a lado.
"""

import colorsys

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from mapa_municipal import carregar_geodataframe

CRS_PROJETADA = "EPSG:31983"  # SIRGAS 2000 / UTM 23S, adequada para o RJ

# Mesma paleta do resto do app: fundo/borda do município como no mapa
# coroplético.
CORES = {
    "fundo_municipio": "#F1ECF6",
    "borda_municipio": "#C9A6D9",
    "ponto": "#C9922E",
}


def _paleta_categorica(quantidade: int) -> ListedColormap:
    """Uma cor distinta por zona, sem sair da família roxo/magenta/âmbar do app.

    Evita vermelho, verde e azul saturados de propósito (mesmo motivo da
    identidade visual do app: nenhuma associação partidária). O matiz varia
    de roxo a âmbar passando por magenta e laranja, com luminosidade
    alternada para diferenciar zonas vizinhas.
    """
    cores = []
    for i in range(quantidade):
        matiz = (265 + i * 135 / quantidade) % 360 / 360
        luminosidade = 0.48 + 0.12 * (i % 3)
        cores.append(colorsys.hls_to_rgb(matiz, luminosidade, 0.45))
    return ListedColormap(cores)


def calcular_areas_influencia(
    setores: gpd.GeoDataFrame, locais_votacao: gpd.GeoDataFrame
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Retorna (setores com o local mais próximo, zona, município e bairro atribuídos, áreas dissolvidas por zona).

    `locais_votacao` precisa ter as colunas "id_local", "zona", "municipio",
    "bairro" e "geometry" (pontos). O "município" e o "bairro" de um setor
    são os do local de votação mais próximo (a mesma referência eleitoral
    usada em toda essa página), não necessariamente os geográficos do
    setor: nas poucas zonas que cruzam divisa (ver módulo
    `perfil_eleitorado`), um setor pode ficar mais perto de um local do
    município vizinho. Ambos os retornos usam `CRS_PROJETADA`.
    """
    setores = setores.to_crs(CRS_PROJETADA)
    pontos = locais_votacao.to_crs(CRS_PROJETADA)

    centroides = setores.copy()
    centroides["geometry"] = centroides.geometry.centroid

    juncao = gpd.sjoin_nearest(
        centroides, pontos[["id_local", "zona", "municipio", "bairro", "geometry"]], how="left", distance_col="dist_m"
    )
    # Em empate (mesma distância a dois locais), sjoin_nearest devolve as duas
    # linhas; fica só a primeira, escolha arbitrária mas sem efeito visível.
    juncao = juncao[~juncao.index.duplicated(keep="first")]

    setores = setores.copy()
    setores["id_local"] = juncao["id_local"].values
    setores["zona"] = juncao["zona"].values
    setores["municipio"] = juncao["municipio"].values
    setores["bairro"] = juncao["bairro"].values

    areas = setores.dissolve(by="zona")
    return setores, areas


def montar_mapa_areas_influencia(setores: gpd.GeoDataFrame, locais_votacao, recorte: str = "estado"):
    """Mapa da área de influência de cada zona eleitoral.

    `locais_votacao` é o DataFrame de `locais_votacao.carregar_locais_votacao()`
    (colunas "id_local", "zona", "lat", "lon"). `recorte`: "estado" (RJ
    inteiro) ou "rio" (zoom no município do Rio de Janeiro).
    """
    municipios = carregar_geodataframe().to_crs(CRS_PROJETADA)
    pontos_wgs84 = gpd.GeoDataFrame(
        locais_votacao,
        geometry=gpd.points_from_xy(locais_votacao["lon"], locais_votacao["lat"]),
        crs="EPSG:4326",
    )
    setores_com_local, areas = calcular_areas_influencia(setores, pontos_wgs84)
    pontos = pontos_wgs84.to_crs(CRS_PROJETADA)

    if recorte == "rio":
        rio = municipios[municipios["name"] == "Rio de Janeiro"]
        limite = rio.union_all().buffer(500)
        setores_com_local = setores_com_local[setores_com_local.geometry.centroid.within(limite)]
        areas = setores_com_local.dissolve(by="zona")
        pontos = pontos[pontos.geometry.within(limite)]
        municipios = rio
        titulo = "Município do Rio de Janeiro"
        tamanho_ponto, largura_borda_municipio = 6, 1.0
    else:
        titulo = "Estado do Rio de Janeiro"
        tamanho_ponto, largura_borda_municipio = 2, 0.5

    areas = areas.reset_index()

    fig, ax = plt.subplots(figsize=(7, 8))
    municipios.plot(
        ax=ax, facecolor=CORES["fundo_municipio"], edgecolor=CORES["borda_municipio"], linewidth=largura_borda_municipio
    )
    areas.plot(ax=ax, column="zona", cmap=_paleta_categorica(len(areas)), categorical=True, linewidth=0, alpha=0.9)
    pontos.plot(
        ax=ax,
        color=CORES["ponto"],
        markersize=tamanho_ponto,
        alpha=0.85,
        linewidths=0.2,
        edgecolor="white",
        label="Local de votação",
    )

    ax.set_axis_off()
    ax.set_title(titulo, fontsize=12, color="#241B33")
    ax.legend(loc="lower left", fontsize=8, frameon=False)
    fig.tight_layout()
    return fig
