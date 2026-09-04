"""Área de influência de cada local de votação, usando setor censitário como referência.

Ideia: um Voronoi "puro" (feito só com os pontos dos locais de votação)
corta o espaço com linhas retas artificiais, que não respeitam nada do
território real. Aqui, cada setor censitário (a menor unidade geográfica
real do IBGE) é atribuído ao local de votação mais próximo do seu
centroide — a mesma lógica do Voronoi, mas decidida setor por setor. Os
setores atribuídos ao mesmo local são então dissolvidos numa única área,
cuja borda segue os limites reais dos setores, não retas.

Nem todo local de votação forma uma área própria: se vários locais ficam
muito perto um do outro (o mesmo bairro, por exemplo), pode não sobrar
nenhum setor mais próximo de um deles do que dos vizinhos.
"""

import geopandas as gpd
import matplotlib.pyplot as plt

from mapa_municipal import carregar_geodataframe

CRS_PROJETADA = "EPSG:31983"  # SIRGAS 2000 / UTM 23S, adequada para o RJ

# Mesma paleta do resto do app: fundo/borda do município como no mapa
# coroplético, borda da área de influência em roxo mais forte, setor
# censitário individual num roxo bem claro (só aparece no zoom).
CORES = {
    "fundo_municipio": "#F1ECF6",
    "borda_municipio": "#C9A6D9",
    "borda_setor": "#D9C7E8",
    "borda_area": "#8A5FA8",
    "ponto": "#C9922E",
}


def calcular_areas_influencia(
    setores: gpd.GeoDataFrame, locais_votacao: gpd.GeoDataFrame
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Retorna (setores com o local mais próximo atribuído, áreas dissolvidas por local).

    `locais_votacao` precisa ter as colunas "id_local" e "geometry" (pontos).
    Ambos os retornos usam `CRS_PROJETADA`.
    """
    setores = setores.to_crs(CRS_PROJETADA)
    pontos = locais_votacao.to_crs(CRS_PROJETADA)

    centroides = setores.copy()
    centroides["geometry"] = centroides.geometry.centroid

    juncao = gpd.sjoin_nearest(centroides, pontos[["id_local", "geometry"]], how="left", distance_col="dist_m")
    # Em empate (mesma distância a dois locais), sjoin_nearest devolve as duas
    # linhas; fica só a primeira, escolha arbitrária mas sem efeito visível.
    juncao = juncao[~juncao.index.duplicated(keep="first")]

    setores = setores.copy()
    setores["id_local"] = juncao["id_local"].values

    areas = setores.dissolve(by="id_local")
    return setores, areas


def montar_mapa_areas_influencia(setores: gpd.GeoDataFrame, locais_votacao, recorte: str = "estado"):
    """Mapa da área de influência de cada local de votação.

    `locais_votacao` é o DataFrame de `locais_votacao.carregar_locais_votacao()`
    (colunas "id_local", "lat", "lon"). `recorte`: "estado" (RJ inteiro, só a
    borda de cada área) ou "rio" (zoom no município do Rio de Janeiro, com os
    setores individuais visíveis por baixo da área dissolvida).
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
        areas = setores_com_local.dissolve(by="id_local")
        pontos = pontos[pontos.geometry.within(limite)]
        municipios = rio
        titulo = "Município do Rio de Janeiro"
        tamanho_ponto, largura_borda_municipio = 6, 1.0
    else:
        titulo = "Estado do Rio de Janeiro"
        tamanho_ponto, largura_borda_municipio = 2, 0.5

    fig, ax = plt.subplots(figsize=(7, 8))
    municipios.plot(
        ax=ax, facecolor=CORES["fundo_municipio"], edgecolor=CORES["borda_municipio"], linewidth=largura_borda_municipio
    )
    if recorte == "rio":
        setores_com_local.boundary.plot(ax=ax, color=CORES["borda_setor"], linewidth=0.25)
    areas.boundary.plot(ax=ax, color=CORES["borda_area"], linewidth=0.9 if recorte == "rio" else 0.5)
    pontos.plot(ax=ax, color=CORES["ponto"], markersize=tamanho_ponto, alpha=0.7, linewidths=0, label="Local de votação")

    ax.set_axis_off()
    ax.set_title(titulo, fontsize=12, color="#241B33")
    ax.legend(loc="lower left", fontsize=8, frameon=False)
    fig.tight_layout()
    return fig
