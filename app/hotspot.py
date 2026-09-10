"""Getis-Ord Gi*: ponto quente/frio estatisticamente significativo, zona a
zona, pra achar onde um candidato é desproporcionalmente forte (ou fraco)
comparado às zonas vizinhas, não só onde tem mais voto em número absoluto.

Diferente do mapa de calor (`mapa_curral_eleitoral.montar_mapa_calor_interativo`, uma
densidade bruta suavizada), a pergunta aqui é outra: dado o valor de cada
zona, ela forma um aglomerado com as vizinhas que é estatisticamente
diferente do que se esperaria por acaso, ou é só ruído? Usa
`libpysal`/`esda` (PySAL), a biblioteca de referência pra análise
espacial em Python: sem hotspot caseiro, sem reinventar a estatística.
"""

import geopandas as gpd
import pandas as pd
from esda.getisord import G_Local
from libpysal.weights import KNN, fill_diagonal

# Gi* precisa de uma amostra espacial mínima pra fazer sentido; com poucas
# zonas (um município pequeno) o resultado vira ruído, não estatística.
ZONAS_MINIMAS = 8

# Limiares padrão de significância do Gi* (equivalentes ao "Hot Spot
# Analysis" do ArcGIS): 90/95/99% de confiança dos dois lados.
_LIMIARES = [
    (2.58, "Ponto quente (99%)"),
    (1.96, "Ponto quente (95%)"),
    (1.65, "Ponto quente (90%)"),
    (-1.65, "Sem padrão significativo"),
    (-1.96, "Ponto frio (90%)"),
    (-2.58, "Ponto frio (95%)"),
]
CATEGORIAS_EM_ORDEM = [nome for _, nome in _LIMIARES] + ["Ponto frio (99%)"]


def _classificar(z: float) -> str:
    for limiar, nome in _LIMIARES:
        if z >= limiar:
            return nome
    return "Ponto frio (99%)"


def hotspot_disponivel(zonas_geometria: gpd.GeoDataFrame) -> bool:
    return len(zonas_geometria) >= ZONAS_MINIMAS


def calcular_hotspot(
    zonas_geometria: gpd.GeoDataFrame,
    valores_por_zona: pd.Series,
    coluna_unidade: str = "zona",
    k: int = 6,
) -> pd.DataFrame:
    """Getis-Ord Gi* por zona.

    `valores_por_zona`: Série indexada por zona (mesma chave de
    `coluna_unidade`), com valor não negativo (Gi* pressupõe isso; aqui é
    sempre percentual ou contagem de voto, nunca diferença que pode ser
    negativa). Vizinhança por k-vizinhos-mais-próximos do centroide, não
    por fronteira compartilhada (Queen): as zonas do RJ, em especial
    dentro do município do Rio, ficam espalhadas e intercaladas pelo
    território (ver "Área de influência de cada zona eleitoral" no
    README), então adjacência por fronteira deixaria zonas sem vizinho de
    verdade; k-vizinhos é mais robusto a esse formato picotado.

    Retorna uma linha por zona, com `valor`, `z_score` e `classificacao`
    (7 categorias, de "Ponto frio (99%)" a "Ponto quente (99%)").
    """
    zonas = zonas_geometria.reset_index(drop=True).copy()
    zonas["valor"] = zonas[coluna_unidade].map(valores_por_zona).fillna(0)

    k_efetivo = min(k, len(zonas) - 1)
    pesos = KNN.from_dataframe(zonas, k=k_efetivo)
    # Gi* conta a própria zona como vizinha dela mesma, com o mesmo peso dos
    # outros k vizinhos (a matriz do KNN é binária, sem isso a diagonal fica
    # zerada). Preenchido explícito (em vez de deixar o esda inferir) pra não
    # depender de um valor "adivinhado" pro autopeso.
    pesos = fill_diagonal(pesos, 1)

    gi = G_Local(zonas["valor"].to_numpy(), pesos, star=None, permutations=999, seed=42)

    resultado = zonas[[coluna_unidade, "valor"]].copy()
    resultado["z_score"] = gi.Zs
    resultado["classificacao"] = [_classificar(z) for z in gi.Zs]
    return resultado
