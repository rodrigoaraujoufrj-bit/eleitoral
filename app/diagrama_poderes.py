import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from cargos_data import DEFINICOES_PODER

COR_EXECUTIVO = "#8A5FA8"
COR_LEGISLATIVO = "#C9922E"
COR_TEXTO_CLARO = "#FAF8FB"
COR_CAIXA_ORGAOS = "#F1ECF6"
COR_TEXTO_ESCURO = "#241B33"


def _caixa(ax, x, y, largura, altura, cor_fundo, cor_texto, titulo, corpo, tamanho_titulo=13, tamanho_corpo=10):
    caixa = FancyBboxPatch(
        (x, y),
        largura,
        altura,
        boxstyle="round,pad=0.12,rounding_size=0.15",
        linewidth=0,
        facecolor=cor_fundo,
    )
    ax.add_patch(caixa)

    centro_x = x + largura / 2
    y_titulo = y + altura - 0.35
    ax.text(
        centro_x, y_titulo, titulo,
        ha="center", va="top", fontsize=tamanho_titulo, fontweight="bold", color=cor_texto,
    )
    if corpo:
        ax.text(
            centro_x, y_titulo - 0.45, corpo,
            ha="center", va="top", fontsize=tamanho_corpo, color=cor_texto, linespacing=1.6,
        )


def _seta(ax, x, y_topo, y_base, cor):
    ax.annotate(
        "",
        xy=(x, y_base), xytext=(x, y_topo),
        arrowprops=dict(arrowstyle="-|>", color=cor, linewidth=1.6, mutation_scale=16),
    )


def montar_diagrama(cargo_executivo: dict, cargo_legislativo: dict):
    """Diagrama Executivo x Legislativo: definição, cargo e órgãos subordinados."""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10.5)
    ax.set_axis_off()

    colunas = [
        (0.4, "Executivo", COR_EXECUTIVO, cargo_executivo),
        (5.1, "Legislativo", COR_LEGISLATIVO, cargo_legislativo),
    ]
    largura = 4.5

    for x, poder, cor, cargo in colunas:
        definicao = textwrap.fill(DEFINICOES_PODER[poder], width=42)
        _caixa(
            ax, x, 7.6, largura, 2.9, cor, COR_TEXTO_CLARO,
            f"PODER {poder.upper()}", definicao, tamanho_titulo=14, tamanho_corpo=9.5,
        )
        _seta(ax, x + largura / 2, 7.55, 6.9, cor)

        _caixa(
            ax, x, 5.7, largura, 1.2, cor, COR_TEXTO_CLARO,
            cargo["cargo"], None, tamanho_titulo=13,
        )
        _seta(ax, x + largura / 2, 5.65, 5.0, cor)

        orgaos = "\n".join(f"•  {item}" for item in cargo["orgaos_subordinados"])
        orgaos_quebrado = "\n".join(
            textwrap.fill(linha, width=48, subsequent_indent="    ") for linha in orgaos.split("\n")
        )
        _caixa(
            ax, x, 0.3, largura, 4.6, COR_CAIXA_ORGAOS, COR_TEXTO_ESCURO,
            "Órgãos subordinados", None, tamanho_titulo=12,
        )
        ax.text(
            x + 0.3, 4.1, orgaos_quebrado,
            ha="left", va="top", fontsize=9.5, color=COR_TEXTO_ESCURO, linespacing=1.9,
        )

    fig.tight_layout()
    return fig
