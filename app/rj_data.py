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
- Salários (subsídios): presidente e deputado federal/senador ganham o
  mesmo valor, R$ 46.366,19. Deputado estadual (ALERJ) ganha 75% disso,
  R$ 34.774,64. Governador do RJ, R$ 21.868,14. Prefeito e vereador
  variam por município (sem valor único), ver municipios_rj.py.
"""

from municipios_rj import MUNICIPIOS_RJ, VEREADORES_RJ_TOTAL

MUNICIPIOS_RJ_TOTAL = len(MUNICIPIOS_RJ)

CARGOS_RJ = [
    {
        "cargo": "Prefeito",
        "pleito": "Municipal",
        "vagas": MUNICIPIOS_RJ_TOTAL,
        "explicacao": "Um prefeito para cada um dos 92 municípios do RJ.",
        "salario": None,
        "salario_nota": "Fixado por lei de cada Câmara Municipal, varia bastante. Exemplo: o prefeito da capital (Rio de Janeiro) recebe R$ 35.608,27 de subsídio bruto.",
    },
    {
        "cargo": "Vereador",
        "pleito": "Municipal",
        "vagas": VEREADORES_RJ_TOTAL,
        "explicacao": "Cada município tem de 9 a 55 vereadores, dependendo da população, conforme a Constituição (Art. 29, IV). Some os 92 municípios do RJ e o total é 1.376.",
        "salario": None,
        "salario_nota": "Tem teto de 20% a 75% do subsídio do deputado estadual, dependendo da população do município (Art. 29, VI da Constituição). Veja o teto de cada município na tabela abaixo.",
    },
    {
        "cargo": "Presidente da República",
        "pleito": "Estadual e Federal",
        "vagas": 1,
        "explicacao": "Um cargo só, mas representa o Brasil inteiro, não apenas o RJ. O eleitor do RJ vota nele junto com todo o país.",
        "salario": 46_366.19,
        "salario_nota": "É o teto do funcionalismo público, o mesmo valor do subsídio dos ministros do STF.",
    },
    {
        "cargo": "Governador",
        "pleito": "Estadual e Federal",
        "vagas": 1,
        "explicacao": "Um cargo só para todo o estado do Rio de Janeiro.",
        "salario": 21_868.14,
        "salario_nota": "Fixado pela ALERJ. É um dos menores salários de governador entre os estados do Sudeste.",
    },
    {
        "cargo": "Senador",
        "pleito": "Estadual e Federal",
        "vagas": 2,
        "explicacao": "O RJ tem 3 senadores titulares, mas o mandato é de 8 anos e a renovação é alternada: em 2022 foi renovada 1 vaga, então em 2026 são renovadas as outras 2.",
        "salario": 46_366.19,
        "salario_nota": "Mesmo valor do deputado federal, por regra constitucional.",
    },
    {
        "cargo": "Deputado Federal",
        "pleito": "Estadual e Federal",
        "vagas": 46,
        "explicacao": "O número de cadeiras por estado é proporcional à população. O RJ tem a 3ª maior bancada do país, atrás de São Paulo e Minas Gerais.",
        "salario": 46_366.19,
        "salario_nota": None,
    },
    {
        "cargo": "Deputado Estadual",
        "pleito": "Estadual e Federal",
        "vagas": 70,
        "explicacao": "O tamanho da Assembleia Legislativa (ALERJ) é definido por regra própria, ligada ao número de deputados federais do estado.",
        "salario": 34_774.64,
        "salario_nota": "Limitado a 75% do subsídio do deputado federal (Art. 27 da Constituição).",
    },
]
