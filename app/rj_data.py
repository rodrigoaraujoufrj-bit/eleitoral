"""Quantidade de vagas em disputa no Rio de Janeiro, por cargo.

Foco no pleito atual de cada cargo (não trata eleições passadas):
- Pleito Municipal (Vereador e Prefeito): próxima eleição municipal.
- Pleito Estadual e Federal (Governador, Senador, Deputado Estadual,
  Deputado Federal e Presidente): eleição geral de 2026.

Números confirmados por fonte (setembro de 2026):
- Municípios do RJ: 92 (IBGE)
- Deputados federais do RJ: 46 (bancada eleita em 2022, mantida em 2026)
- Deputados estaduais do RJ: 70 (ALERJ)
- Senadores: o RJ tem 3 titulares, mas o mandato é de 8 anos e a renovação
  é alternada a cada eleição (1/3, depois 2/3). Em 2022 o RJ renovou 1
  vaga, então em 2026 é a vez de renovar as outras 2.
- Vereadores: varia por município, conforme a Constituição (Art. 29, IV),
  de 9 (até 15 mil habitantes) a 55 (mais de 8 milhões). Calculado em
  municipios_rj.py a partir da população de cada um dos 92 municípios
  (censo 2022): soma 1.376 vereadores no RJ.
"""

from municipios_rj import MUNICIPIOS_RJ, VEREADORES_RJ_TOTAL

MUNICIPIOS_RJ_TOTAL = len(MUNICIPIOS_RJ)

CARGOS_RJ = [
    {
        "cargo": "Prefeito",
        "pleito": "Municipal",
        "vagas": MUNICIPIOS_RJ_TOTAL,
        "explicacao": "Um prefeito para cada um dos 92 municípios do RJ.",
    },
    {
        "cargo": "Vereador",
        "pleito": "Municipal",
        "vagas": VEREADORES_RJ_TOTAL,
        "explicacao": "Cada município tem de 9 a 55 vereadores, dependendo da população, conforme a Constituição (Art. 29, IV). Some os 92 municípios do RJ e o total é 1.376.",
    },
    {
        "cargo": "Presidente da República",
        "pleito": "Estadual e Federal",
        "vagas": 1,
        "explicacao": "Um cargo só, mas representa o Brasil inteiro, não apenas o RJ. O eleitor do RJ vota nele junto com todo o país.",
    },
    {
        "cargo": "Governador",
        "pleito": "Estadual e Federal",
        "vagas": 1,
        "explicacao": "Um cargo só para todo o estado do Rio de Janeiro.",
    },
    {
        "cargo": "Senador",
        "pleito": "Estadual e Federal",
        "vagas": 2,
        "explicacao": "O RJ tem 3 senadores titulares, mas o mandato é de 8 anos e a renovação é alternada: em 2022 foi renovada 1 vaga, então em 2026 são renovadas as outras 2.",
    },
    {
        "cargo": "Deputado Federal",
        "pleito": "Estadual e Federal",
        "vagas": 46,
        "explicacao": "O número de cadeiras por estado é proporcional à população. O RJ tem a 3ª maior bancada do país, atrás de São Paulo e Minas Gerais.",
    },
    {
        "cargo": "Deputado Estadual",
        "pleito": "Estadual e Federal",
        "vagas": 70,
        "explicacao": "O tamanho da Assembleia Legislativa (ALERJ) é definido por regra própria, ligada ao número de deputados federais do estado.",
    },
]
