"""Conteúdo de referência sobre os cargos eletivos brasileiros.

Fonte: Constituição Federal de 1988 (Poder Executivo e Legislativo, nas
esferas federal, estadual e municipal). Mantido separado da apresentação
para poder ser reaproveitado depois, por exemplo ao cruzar candidatos com
a abrangência real do cargo que disputam.
"""

CARGOS = [
    {
        "esfera": "Federal",
        "cargo": "Presidente da República",
        "poder": "Executivo",
        "mandato": "4 anos, com direito a uma reeleição para o mandato seguinte",
        "eleicao": "Voto majoritário, com segundo turno se nenhum candidato atingir maioria absoluta no primeiro turno",
        "atribuicoes": [
            "Chefiar o Estado e o governo federal",
            "Comandar as Forças Armadas",
            "Representar o Brasil nas relações internacionais e assinar tratados",
            "Sancionar ou vetar as leis aprovadas pelo Congresso Nacional",
            "Editar medidas provisórias, que dependem de aprovação do Congresso para virarem lei permanente",
            "Nomear ministros de Estado e outros cargos federais previstos na Constituição",
            "Enviar ao Congresso a proposta de orçamento federal",
            "Definir políticas nacionais de saúde (SUS), educação, segurança pública federal e política econômica",
        ],
        "nao_atribuicoes": [
            "Não decide sobre segurança pública dentro dos estados, essa é atribuição do governador",
            "Não executa obras ou serviços municipais",
            "Não define o currículo ou a gestão de escolas municipais",
            "Não legisla sozinho de forma permanente, medida provisória é temporária e depende do Congresso",
        ],
    },
    {
        "esfera": "Federal",
        "cargo": "Senador",
        "poder": "Legislativo",
        "mandato": "8 anos, com renovação alternada de um terço e dois terços das vagas a cada eleição",
        "eleicao": "Voto majoritário, três senadores por estado",
        "atribuicoes": [
            "Elaborar e votar leis federais, em conjunto com a Câmara dos Deputados",
            "Aprovar indicações do presidente para ministros do STF, diretores de agências reguladoras, presidente do Banco Central e embaixadores",
            "Aprovar tratados internacionais assinados pelo presidente",
            "Julgar o presidente e ministros do STF em crimes de responsabilidade, o chamado impeachment",
            "Autorizar operações de crédito externo dos estados e municípios",
        ],
        "nao_atribuicoes": [
            "Não executa políticas públicas nem presta serviços diretamente à população",
            "Não é responsável por obras",
            "Não decide sozinho, depende da aprovação em conjunto com a Câmara e da sanção do presidente",
        ],
    },
    {
        "esfera": "Federal",
        "cargo": "Deputado Federal",
        "poder": "Legislativo",
        "mandato": "4 anos",
        "eleicao": "Voto proporcional, com o número de cadeiras por estado variando conforme a população",
        "atribuicoes": [
            "Elaborar e votar leis federais",
            "Autorizar o início de processos de impeachment contra o presidente",
            "Aprovar o orçamento federal, em conjunto com o Senado",
            "Fiscalizar o governo federal, inclusive por meio de Comissões Parlamentares de Inquérito (CPIs)",
        ],
        "nao_atribuicoes": [
            "Não executa políticas públicas nem obras",
            "Não representa exclusivamente o município onde nasceu ou mora, o mandato é referente ao estado todo",
        ],
    },
    {
        "esfera": "Estadual",
        "cargo": "Governador",
        "poder": "Executivo",
        "mandato": "4 anos, com direito a uma reeleição para o mandato seguinte",
        "eleicao": "Voto majoritário estadual, com segundo turno se nenhum candidato atingir maioria absoluta no primeiro turno",
        "atribuicoes": [
            "Comandar a Polícia Militar e a Polícia Civil do estado",
            "Administrar hospitais e a rede estadual de saúde",
            "Administrar o ensino médio e parte do ensino técnico",
            "Construir e manter rodovias estaduais",
            "Administrar os presídios estaduais",
            "Administrar o Detran e definir tributos estaduais, como ICMS e IPVA",
        ],
        "nao_atribuicoes": [
            "Não comanda a Polícia Federal",
            "Não decide sobre leis federais",
            "Não é responsável pela educação infantil nem pelo ensino fundamental, que são atribuições municipais",
            "Não interfere na administração de outro estado",
        ],
    },
    {
        "esfera": "Estadual",
        "cargo": "Deputado Estadual",
        "poder": "Legislativo",
        "mandato": "4 anos",
        "eleicao": "Voto proporcional dentro do estado",
        "atribuicoes": [
            "Elaborar e votar leis estaduais",
            "Aprovar o orçamento do estado",
            "Fiscalizar o governador",
            "Participar da elaboração da Constituição Estadual",
        ],
        "nao_atribuicoes": [
            "Não executa obras nem presta serviços",
            "Não tem poder sobre leis federais ou municipais",
        ],
    },
    {
        "esfera": "Municipal",
        "cargo": "Prefeito",
        "poder": "Executivo",
        "mandato": "4 anos, com direito a uma reeleição para o mandato seguinte",
        "eleicao": "Voto majoritário municipal, com segundo turno apenas em municípios com mais de 200 mil eleitores",
        "atribuicoes": [
            "Administrar a educação infantil e o ensino fundamental",
            "Administrar a atenção básica de saúde, como postos de saúde, UBS e agentes comunitários",
            "Administrar o transporte público municipal e o trânsito local",
            "Administrar a coleta de lixo e a iluminação pública",
            "Definir o uso do solo urbano, o chamado zoneamento",
            "Definir tributos municipais, como o IPTU",
        ],
        "nao_atribuicoes": [
            "Não comanda policiais, segurança pública é atribuição estadual e federal",
            "Não administra hospitais estaduais nem escolas de ensino médio",
            "Não decide sobre estradas estaduais ou federais",
        ],
    },
    {
        "esfera": "Municipal",
        "cargo": "Vereador",
        "poder": "Legislativo",
        "mandato": "4 anos",
        "eleicao": "Voto proporcional dentro do município",
        "atribuicoes": [
            "Elaborar e votar leis municipais, como uso do solo, posturas e tributos municipais",
            "Aprovar o orçamento da prefeitura",
            "Fiscalizar o prefeito",
            "Autorizar o início de processos de impeachment contra o prefeito",
        ],
        "nao_atribuicoes": [
            "Não executa serviços públicos",
            "Não contrata funcionários",
            "Não decide sozinho sobre obras, aprova o orçamento, mas quem executa é o prefeito",
        ],
    },
]

# No Brasil, vereador e prefeito são eleitos num pleito (municipal) e os
# demais cargos noutro (estadual e federal, no mesmo ano). O app segue essa
# divisão, então cada cargo carrega a que pleito pertence.
for _cargo in CARGOS:
    _cargo["pleito"] = "Municipal" if _cargo["esfera"] == "Municipal" else "Estadual e Federal"
