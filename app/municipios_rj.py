"""População e número de vereadores dos 92 municípios do RJ.

População: Censo 2022 (IBGE), via "Lista de municípios do Rio de Janeiro
por população" (Wikipédia). É a base oficial usada para definir vagas nas
eleições municipais de 2024 em diante.

Vereadores: calculados pela regra da Constituição Federal (Art. 29, IV),
que define de 9 a 55 vereadores por município conforme faixas de
população.
"""

FAIXAS_VEREADORES = [
    (15_000, 9),
    (30_000, 11),
    (50_000, 13),
    (80_000, 15),
    (120_000, 17),
    (160_000, 19),
    (300_000, 21),
    (450_000, 23),
    (600_000, 25),
    (750_000, 27),
    (900_000, 29),
    (1_050_000, 31),
    (1_200_000, 33),
    (1_350_000, 35),
    (1_500_000, 37),
    (1_800_000, 39),
    (2_400_000, 41),
    (3_000_000, 43),
    (4_000_000, 45),
    (5_000_000, 47),
    (6_000_000, 49),
    (7_000_000, 51),
    (8_000_000, 53),
]


def vereadores_por_populacao(populacao: int) -> int:
    for limite, vereadores in FAIXAS_VEREADORES:
        if populacao <= limite:
            return vereadores
    return 55


MUNICIPIOS_RJ = [
    {"municipio": "Rio de Janeiro", "populacao_2022": 6_211_223},
    {"municipio": "São Gonçalo", "populacao_2022": 896_744},
    {"municipio": "Duque de Caxias", "populacao_2022": 808_161},
    {"municipio": "Nova Iguaçu", "populacao_2022": 785_867},
    {"municipio": "Campos dos Goytacazes", "populacao_2022": 483_540},
    {"municipio": "Belford Roxo", "populacao_2022": 483_087},
    {"municipio": "Niterói", "populacao_2022": 481_749},
    {"municipio": "São João de Meriti", "populacao_2022": 440_962},
    {"municipio": "Petrópolis", "populacao_2022": 278_881},
    {"municipio": "Volta Redonda", "populacao_2022": 261_563},
    {"municipio": "Macaé", "populacao_2022": 246_391},
    {"municipio": "Magé", "populacao_2022": 228_127},
    {"municipio": "Itaboraí", "populacao_2022": 224_267},
    {"municipio": "Cabo Frio", "populacao_2022": 222_161},
    {"municipio": "Maricá", "populacao_2022": 197_277},
    {"municipio": "Nova Friburgo", "populacao_2022": 189_939},
    {"municipio": "Barra Mansa", "populacao_2022": 169_894},
    {"municipio": "Angra dos Reis", "populacao_2022": 167_434},
    {"municipio": "Mesquita", "populacao_2022": 167_127},
    {"municipio": "Teresópolis", "populacao_2022": 165_123},
    {"municipio": "Rio das Ostras", "populacao_2022": 156_491},
    {"municipio": "Nilópolis", "populacao_2022": 146_774},
    {"municipio": "Queimados", "populacao_2022": 140_523},
    {"municipio": "Araruama", "populacao_2022": 129_671},
    {"municipio": "Resende", "populacao_2022": 129_612},
    {"municipio": "Itaguaí", "populacao_2022": 116_841},
    {"municipio": "São Pedro da Aldeia", "populacao_2022": 104_029},
    {"municipio": "Itaperuna", "populacao_2022": 101_041},
    {"municipio": "Japeri", "populacao_2022": 96_289},
    {"municipio": "Barra do Piraí", "populacao_2022": 92_883},
    {"municipio": "Saquarema", "populacao_2022": 89_559},
    {"municipio": "Seropédica", "populacao_2022": 80_596},
    {"municipio": "Três Rios", "populacao_2022": 78_346},
    {"municipio": "Valença", "populacao_2022": 67_753},
    {"municipio": "Cachoeiras de Macacu", "populacao_2022": 56_943},
    {"municipio": "Rio Bonito", "populacao_2022": 56_276},
    {"municipio": "Guapimirim", "populacao_2022": 51_696},
    {"municipio": "Casimiro de Abreu", "populacao_2022": 46_110},
    {"municipio": "São Francisco de Itabapoana", "populacao_2022": 45_059},
    {"municipio": "Paraty", "populacao_2022": 44_872},
    {"municipio": "Santo Antônio de Pádua", "populacao_2022": 41_325},
    {"municipio": "Paracambi", "populacao_2022": 41_375},
    {"municipio": "Mangaratiba", "populacao_2022": 41_220},
    {"municipio": "Paraíba do Sul", "populacao_2022": 42_063},
    {"municipio": "Armação dos Búzios", "populacao_2022": 40_006},
    {"municipio": "São Fidélis", "populacao_2022": 38_939},
    {"municipio": "São João da Barra", "populacao_2022": 36_573},
    {"municipio": "Bom Jesus do Itabapoana", "populacao_2022": 35_173},
    {"municipio": "Vassouras", "populacao_2022": 33_976},
    {"municipio": "Tanguá", "populacao_2022": 31_086},
    {"municipio": "Arraial do Cabo", "populacao_2022": 30_986},
    {"municipio": "Itatiaia", "populacao_2022": 30_908},
    {"municipio": "Paty do Alferes", "populacao_2022": 29_619},
    {"municipio": "Bom Jardim", "populacao_2022": 28_102},
    {"municipio": "Iguaba Grande", "populacao_2022": 27_920},
    {"municipio": "Piraí", "populacao_2022": 27_474},
    {"municipio": "Miracema", "populacao_2022": 26_881},
    {"municipio": "Miguel Pereira", "populacao_2022": 26_578},
    {"municipio": "Pinheiral", "populacao_2022": 24_298},
    {"municipio": "Itaocara", "populacao_2022": 22_919},
    {"municipio": "Quissamã", "populacao_2022": 22_393},
    {"municipio": "São José do Vale do Rio Preto", "populacao_2022": 22_080},
    {"municipio": "Silva Jardim", "populacao_2022": 21_352},
    {"municipio": "Conceição de Macabu", "populacao_2022": 21_104},
    {"municipio": "Cordeiro", "populacao_2022": 20_783},
    {"municipio": "Porto Real", "populacao_2022": 20_373},
    {"municipio": "Cantagalo", "populacao_2022": 19_390},
    {"municipio": "Sapucaia", "populacao_2022": 17_729},
    {"municipio": "Mendes", "populacao_2022": 17_502},
    {"municipio": "Rio Claro", "populacao_2022": 17_401},
    {"municipio": "Porciúncula", "populacao_2022": 17_288},
    {"municipio": "Carmo", "populacao_2022": 17_198},
    {"municipio": "Sumidouro", "populacao_2022": 15_206},
    {"municipio": "Natividade", "populacao_2022": 15_074},
    {"municipio": "Cambuci", "populacao_2022": 14_616},
    {"municipio": "Italva", "populacao_2022": 14_073},
    {"municipio": "Carapebus", "populacao_2022": 13_847},
    {"municipio": "Quatis", "populacao_2022": 13_682},
    {"municipio": "Cardoso Moreira", "populacao_2022": 12_958},
    {"municipio": "Engenheiro Paulo de Frontin", "populacao_2022": 12_242},
    {"municipio": "Areal", "populacao_2022": 11_828},
    {"municipio": "Aperibé", "populacao_2022": 11_034},
    {"municipio": "Duas Barras", "populacao_2022": 10_980},
    {"municipio": "Trajano de Moraes", "populacao_2022": 10_302},
    {"municipio": "Santa Maria Madalena", "populacao_2022": 10_232},
    {"municipio": "Varre-Sai", "populacao_2022": 10_207},
    {"municipio": "Rio das Flores", "populacao_2022": 8_954},
    {"municipio": "Comendador Levy Gasparian", "populacao_2022": 8_741},
    {"municipio": "São Sebastião do Alto", "populacao_2022": 7_750},
    {"municipio": "Laje do Muriaé", "populacao_2022": 7_336},
    {"municipio": "São José de Ubá", "populacao_2022": 7_070},
    {"municipio": "Macuco", "populacao_2022": 5_415},
]

for _m in MUNICIPIOS_RJ:
    _m["vereadores"] = vereadores_por_populacao(_m["populacao_2022"])

VEREADORES_RJ_TOTAL = sum(m["vereadores"] for m in MUNICIPIOS_RJ)
