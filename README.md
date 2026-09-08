# Eleitoral

Projeto de análise geoespacial e dashboard interativo sobre a política eletiva do estado do Rio de Janeiro (RJ), a partir de dados abertos do TSE (Tribunal Superior Eleitoral) e do IBGE.

## Escopo

- **Recorte geográfico**: estado do Rio de Janeiro e seus 92 municípios (sem outros estados)
- **Pouco dado histórico, e só quando ele responde algo que o pleito atual sozinho não responde**: o foco principal é o pleito atual/próximo de cada cargo, não série histórica de eleições passadas. A exceção é a votação real da eleição anterior de cada cargo (ver "Curral eleitoral" abaixo), usada só pra mostrar onde um candidato teve força de verdade, algo que nenhum dado do pleito atual consegue mostrar
- **Dois pleitos**, porque no Brasil eles acontecem em anos diferentes:
  - **Pleito Municipal**: vereador e prefeito
  - **Pleito Estadual e Federal**: deputado estadual, deputado federal, senador, governador e presidente (eleição geral de 2026)

## Ideia geral

- Explicar de forma clara o que cada cargo eletivo faz de fato, para direcionar melhor a cobrança política e o voto
- Mostrar quantas vagas de cada cargo estão em disputa no RJ (por município, quando for o caso)
- Mostrar quanto cada cargo ganha (subsídio), incluindo o teto de vereador por município
- Análise geoespacial e dashboard interativo com mapas e indicadores, navegável pelo navegador

## Páginas do app

- **Home**: apresentação do projeto
- **Pleito Municipal**: vereador e prefeito, quantas vagas no RJ, o que cada cargo faz, mapa por município e área de influência de cada zona eleitoral
- **Pleito Estadual e Federal**: deputado estadual, deputado federal, senador, governador e presidente, quantas vagas no RJ, o que cada cargo faz e mapa do eleitorado real por município
- **Análise do Eleitorado**: duas páginas
  - **Perfil por Zona**: perfil do eleitorado por zona ou, dentro de 1 município, por bairro (gênero, faixa etária, escolaridade, raça/cor), com recorte opcional por município e mapa que dá zoom onde o perfil filtrado é mais forte
  - **Curral Eleitoral**: votação real (não estimativa) de um candidato específico, por zona. Cobre vereador e prefeito (2024, dentro do município do candidato) e governador, senador, deputado estadual e deputado federal (2022, no RJ inteiro)

## Stack

- **Python** para tratamento de dados (pandas, geopandas)
- **geopandas** / **matplotlib** para os mapas coropléticos (estáticos, sem depender de internet em tempo de execução) e **plotly** para outros gráficos
- **Streamlit** para o webapp/dashboard, com navegação em seções (`st.navigation`) separando os dois pleitos

## Identidade visual

Paleta roxo ardósia (base) e âmbar (destaque), com cinza neutro, escolhida entre 4 direções para evitar qualquer associação partidária (nada de vermelho, azul saturado ou verde-amarelo). Tom moderno e acessível, fonte Manrope. Configurada em `.streamlit/config.toml` (tema principal e tema da barra lateral) e aplicada em todas as páginas via `app/theme.py`.

## Estrutura

```
eleitoral/
├── .streamlit/
│   └── config.toml               # tema visual (cores, fonte, cantos)
├── app/
│   ├── app.py                    # roteador (st.navigation entre os pleitos)
│   ├── theme.py                  # marca do app, aplicada em cada página
│   ├── components.py             # cards e resumo de vagas, reutilizados nas páginas
│   ├── cargos_data.py            # funções e deveres de cada cargo, com o pleito a que pertence
│   ├── rj_data.py                # quantidade de vagas de cada cargo no RJ
│   ├── municipios_rj.py          # população e vereadores dos 92 municípios do RJ
│   ├── mapa_municipal.py         # mapa coroplético dos municípios do RJ
│   ├── locais_votacao.py         # locais de votação do RJ (TSE), um ponto por local
│   ├── setores_censitarios.py    # setores censitários do RJ (IBGE, Censo 2022)
│   ├── areas_influencia.py       # área de influência de cada zona eleitoral (setor + Voronoi)
│   ├── perfil_eleitorado.py      # perfil do eleitorado por zona, com filtros combináveis
│   ├── perfil_eleitorado_bairro.py # o mesmo, por bairro, dentro de 1 município
│   ├── mapa_perfil_eleitorado.py # mapa coroplético por zona ou bairro, com zoom no filtrado
│   ├── resultados_eleitorais.py  # votação real por candidato (curral eleitoral)
│   ├── mapa_curral_eleitoral.py  # mapa de dominância (categórico) e de comparação (divergente)
│   ├── diagrama_poderes.py       # diagrama Executivo x Legislativo e órgãos subordinados
│   ├── geo/
│   │   ├── rj_municipios.geojson          # contorno dos 92 municípios (fonte: GitHub, tbrugz/geodata-br)
│   │   └── rj_setores_censitarios.parquet # setores censitários do RJ (fonte: GitHub, ipea/geobr_prep_data)
│   └── views/
│       ├── home.py
│       ├── pleito_municipal.py
│       ├── pleito_estadual_federal.py
│       ├── perfil_eleitorado.py
│       └── curral_eleitoral.py
├── src/
│   ├── baixar_dados_tse.py       # baixa os brutos do TSE (primeiro passo após clonar)
│   ├── restaurar_dados.py        # legado, ver "Dados brutos do TSE"
│   ├── tratar_perfil_secao.py    # agrega o perfil do eleitorado por local de votação
│   └── tratar_resultados.py      # trata a votação por candidato/município/zona
├── data/
│   ├── raw/        # brutos do TSE, NÃO versionados (ver abaixo)
│   │   ├── resultados/           # votação por candidato/município/zona (RJ), 2022 e 2024
│   │   ├── locais_votacao/       # eleitorado por local de votação (RJ)
│   │   ├── perfil_secao/         # perfil do eleitorado por seção (RJ)
│   │   └── perfil_deficiencia/   # eleitores com deficiência (RJ)
│   └── processed/  # dados já tratados (não versionados), ver `perfil_eleitorado_local.parquet` e `votacao_<ano>.parquet`
├── notebooks/      # exploração e prototipagem
├── requirements.txt
└── README.md
```

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/baixar_dados_tse.py     # baixa os dados brutos do TSE (~2,3 GB)
python src/tratar_perfil_secao.py  # gera o perfil do eleitorado por local de votação
python src/tratar_resultados.py --ano 2024  # gera a votação por candidato (curral eleitoral, vereador/prefeito)
python src/tratar_resultados.py --ano 2022  # o mesmo, governador/senador/deputados
streamlit run app/app.py
```

O download é o primeiro passo depois de clonar: os dados brutos **não são
versionados**, então um clone novo vem sem eles. Detalhes na seção seguinte.
Os `tratar_*` geram o que fica em `data/processed/`, também não
versionado; sem eles, as páginas de Análise do Eleitorado mostram uma
mensagem pedindo pra rodar o script certo, em vez de dar erro.

## Dados brutos do TSE

Os dados brutos do TSE **não são versionados**. Eles somam ~2,3 GB (um deles,
sozinho, 1,7 GB), muito acima do limite de 100 MiB por arquivo do GitHub. Em
vez de carregar os dados, o repositório carrega o **script que os baixa**:

```bash
python src/baixar_dados_tse.py                 # baixa o que estiver faltando
python src/baixar_dados_tse.py --listar        # só mostra o que falta
python src/baixar_dados_tse.py --conjunto resultados_2024
python src/baixar_dados_tse.py --forcar        # rebaixa mesmo se o CSV existir
```

É **idempotente**: um conjunto cujo CSV já está em `data/raw/` é pulado, então
rodar de novo depois de uma interrupção só completa o que falta. Mostra
progresso durante o download e apaga o `.zip` depois de extrair (use
`--manter-zip` para guardá-lo).

| Chave | Pasta | Arquivo extraído | Linhas | CSV | Zip baixado |
|---|---|---|---:|---:|---:|
| `resultados_2022` | `resultados` | `votacao_candidato_munzona_2022_RJ.csv` | 476.349 | 211 MB | 553 MB |
| `resultados_2024` | `resultados` | `votacao_candidato_munzona_2024_RJ.csv` | 80.711 | 35,6 MB | 47 MB |
| `locais_votacao_2026` | `locais_votacao` | `eleitorado_local_votacao_2026_RJ.csv` | 38.739 | 15,2 MB | 83,5 MB |
| `perfil_secao_2026` | `perfil_secao` | `perfil_eleitor_secao_2026_RJ.csv` | 6.943.094 | 1,66 GB | 202 MB |
| `perfil_deficiencia_2026` | `perfil_deficiencia` | `perfil_eleitor_deficiencia_2026_RJ.csv` | 155.199 | 36,2 MB | 88,3 MB |

Quase todos os zips do TSE são **nacionais**: trazem um CSV por UF, mais um
`BRASIL`, além do `leiame.pdf` do conjunto. O script extrai **só o CSV do RJ e
o `leiame.pdf`**, descartando as outras UFs sem gravá-las em disco. A exceção é
`perfil_eleitor_secao`, que o TSE já publica por UF. Cada pasta fica com o
`leiame.pdf` do seu conjunto, são documentos **diferentes** entre si (em
`resultados/`, onde caem dois anos, viram `leiame_2022.pdf` e
`leiame_2024.pdf`).

Uma pegadinha do CDN: no conjunto de eleitores com deficiência a **pasta** se
chama `perfil_eleitor_deficiente` e o **arquivo**
`perfil_eleitor_deficiencia_2026.zip`. Trocar um nome pelo outro dá 404.

### Por que o download passa pelo PowerShell

O CDN do TSE (`cdn.tse.jus.br`) fica atrás da Akamai, que barra clientes de
linha de comando por **fingerprint TLS**: `curl`, `requests` e `urllib` levam
403 Forbidden mesmo enviando cabeçalhos de navegador, porque o bloqueio não
olha o User-Agent, e sim a assinatura do handshake TLS. O que passa, no
Windows, é o **BITS** (`Start-BitsTransfer`), que baixa pela pilha WinHTTP do
sistema; por isso o script delega o download ao PowerShell.

Fora do Windows não há BITS. O script tenta `urllib` e, se a Akamai barrar,
explica o caminho manual: baixar os zips pelo navegador e rodar
`python src/baixar_dados_tse.py --zips-em <pasta>`, que extrai a partir deles
sem baixar nada.

### Lendo os CSVs

**Ao ler os CSVs**: são `ISO-8859-1` (Latin-1), sem BOM, separador `;`, campos de
texto entre aspas duplas. As coordenadas de `locais_votacao` usam **vírgula
decimal**, e `-1` é o código de ausência de valor (não um valor real).

```python
pd.read_csv(caminho, sep=";", encoding="latin-1", decimal=",")
```

A chave de junção entre os três conjuntos é `CD_MUNICIPIO` + `NR_ZONA` + `NR_SECAO`.
Atenção: `perfil_deficiencia` é **microdado individual** (uma linha por eleitor,
com `SQ_ELEITOR`), enquanto os outros dois são agregados, por isso este
repositório é privado.

`locais_votacao` tem cobertura de coordenada praticamente total: 5.038 dos
5.040 locais de votação únicos do RJ têm latitude/longitude válida (bate com
o total oficial do TSE, 5.183, a diferença de ~2,8% é provavelmente a data
de geração deste extrato). A mesma escola pode reunir várias seções, por
isso `app/locais_votacao.py` agrupa por local antes de plotar. Atenção:
o agrupamento tem que ser por **município + zona + NR_LOCAL_VOTACAO**, esse
número sozinho se repete em zonas diferentes do mesmo município (agrupar só
por local dava 2.919, fundindo locais físicos distintos). É a camada de
pontos que aparece no mapa do Pleito Municipal, opcional via checkbox.

Origem: <https://dadosabertos.tse.jus.br/>, servida pelo CDN `cdn.tse.jus.br`
(sobre o bloqueio dele, veja "Por que o download passa pelo PowerShell" acima).

### Legado ainda no repositório

Antes desta abordagem, os brutos entravam versionados comprimidos com gzip (o
maior dividido em partes de 90 MiB), remontados por `src/restaurar_dados.py`.
Esses `.gz` e `.gz.part*` **ainda estão rastreados** em `data/raw/`, ~211 MB:
acrescentar `data/raw/` ao `.gitignore` não desrastreia o que já estava
rastreado. Removê-los do rastreamento (`git rm --cached`), junto com
`src/restaurar_dados.py`, é uma limpeza pendente. Ela encolhe o clone
futuro, não o histórico, que continuaria carregando os blobs.

## Área de influência de cada zona eleitoral

O TSE não publica um polígono oficial de abrangência por zona eleitoral
(a suspeita, investigada e não confirmada, é que só existe uma ferramenta
de consulta ponto a ponto em cada TRE, sem tabela para download em lote).
Como aproximação, `app/areas_influencia.py` faz o seguinte:

1. Parte dos 5.038 pontos de `locais_votacao.py` e calcula, para cada
   setor censitário do IBGE (a menor unidade geográfica oficial, 42.270
   no RJ), qual é o local de votação mais próximo do seu centro, a mesma
   lógica de um diagrama de Voronoi, mas decidida setor por setor, não com
   geometria pura.
2. A hierarquia eleitoral, da maior unidade para a menor, é zona, depois
   local de votação, depois seção: uma zona reúne vários locais, e cada
   local reúne várias seções. Atribuir cada setor direto ao local mais
   próximo (5.038 no RJ) gerava áreas pequenas e picotadas nas regiões
   mais densas. Por isso os setores são dissolvidos por zona (165 no RJ):
   bem menos fragmentado, ainda seguindo os limites reais dos setores, não
   retas artificiais.

Mesmo por zona, dentro do município do Rio (49 zonas) as áreas ficam
espalhadas e intercaladas pelo território, não formam blocos únicos e
contíguos como um bairro: é assim mesmo que a divisão em zonas eleitorais
foi desenhada lá, não é erro de cálculo. Por isso o mapa usa preenchimento
colorido por zona, não só contorno (que vira uma malha ilegível quando há
muitas áreas pequenas lado a lado), com uma paleta categórica só dentro da
família roxo/magenta/âmbar do app (nada de vermelho, verde ou azul
saturado, pelo mesmo motivo da identidade visual: nenhuma associação
partidária).

Essa é uma aproximação territorial, não o zoneamento eleitoral real (que
também considera outros critérios, não só distância).

Fonte dos setores censitários: pacote `geobr` (Ipea), que espelha os dados
oficiais do IBGE em releases do GitHub
(`github.com/ipea/geobr_prep_data`), já que o servidor do próprio IBGE
(`geoftp.ibge.gov.br`) está bloqueado nesta sessão, assim como o TSE. Usada
a versão "simplified" (simplificação topológica), no mesmo nível de
detalhe já usado no contorno dos municípios. O arquivo nacional (~473 mil
setores) foi filtrado para o RJ e salvo em `app/geo/rj_setores_censitarios.parquet`
(GeoParquet, 8,5 MB, bem mais compacto que GeoJSON para 42 mil polígonos).

## Perfil do eleitorado por zona ou por bairro

`src/tratar_perfil_secao.py` agrega `perfil_secao` (6,9 milhões de linhas,
uma por combinação de seção e categoria) por **local de votação**
(município + zona + número do local), somando `QT_ELEITORES` em quatro
dimensões publicadas pelo TSE: gênero, faixa etária, grau de escolaridade
e raça/cor. Mantém a combinação completa dessas quatro dimensões (não
cada uma separada), porque é isso que permite depois filtrar por mais de
uma dimensão ao mesmo tempo (por exemplo "mulheres jovens com ensino
médio incompleto") sem perder a relação entre elas. Roda em pouco mais de
um minuto (lê o CSV em pedaços de 500 mil linhas, já agregando cada
pedaço antes de somar, para não estourar memória com um arquivo de 1,7 GB)
e gera `data/processed/perfil_eleitorado_local.parquet` (1,9 milhão de
linhas, 3,5 MB), não versionado:

```bash
python src/tratar_perfil_secao.py
```

A granularidade é por local, não por zona, porque `perfil_secao` não traz
bairro (só `locais_votacao` traz), e local de votação é a única chave em
comum entre os dois conjuntos do TSE para juntar os dois depois. Quem só
precisa de zona (`app/perfil_eleitorado.py`) soma esse resultado por
município + zona, sem perder nada.

Validado: as 165 zonas batem exatamente com as de `locais_votacao.py`, o
total de eleitores do RJ (12,86 milhões) é compatível com o esperado para
o estado, sem nenhum filtro aplicado cada zona soma exatamente 100% do
seu próprio eleitorado (garantindo que a agregação não perde nem duplica
ninguém), e ao juntar com bairro (`app/perfil_eleitorado_bairro.py`) só
0,016% dos eleitores ficam sem bairro (os poucos locais sem coordenada,
já excluídos de `locais_votacao.py`).

A página **Análise do Eleitorado > Perfil por Zona** usa isso em três
etapas. Primeiro "Onde": um recorte opcional de um ou mais municípios,
porque um candidato a vereador ou prefeito só disputa no próprio
município, não faz sentido misturar com área de fora. Com **exatamente
um** município selecionado, aparece um segundo controle, "Nível de
análise": zona eleitoral (o padrão) ou **bairro**, uma unidade bem menor,
mais parecida com o que um candidato a vereador realmente enxerga ao
planejar campanha (bairro não faz sentido sem recorte de município, o
mesmo nome, como "Centro", se repete em vários). Depois "Quem": os
filtros de gênero, faixa etária, escolaridade e raça/cor. O usuário
escolhe ordenar pelo número absoluto ou pelo percentual de concentração,
e o mapa dá zoom automaticamente nas zonas ou bairros de maior valor
dentro do recorte, com a borda destacada em âmbar.

Uma zona pode abranger mais de um município (18 das 165 no RJ). Sem
recorte, a tabela mostra os nomes separados por "/", do que tem mais
eleitores na zona para o que tem menos. Com um município selecionado, o
recorte já ignora eleitores de fora dele nessa zona (tanto no total quanto
no mapa, que mostra só a fatia de setores censitários cujo local de
votação mais próximo é desse município, não a zona inteira). A mesma
lógica de "local mais próximo" (ver `app/areas_influencia.py`) é reusada
para desenhar os bairros: cada setor censitário vira parte do bairro do
seu local de votação mais próximo.

É composição demográfica do eleitorado registrado (dado real do TSE), não
dado de comportamento, consumo ou intenção de voto, e a página deixa isso
explícito para quem for usar a ferramenta.

Com exatamente 1 município selecionado, a página também responde "quantos
votos um vereador precisa": divide o eleitorado do município (real, de
`locais_votacao.py`) pelas vagas de vereador dele (`municipios_rj.py`,
Art. 29 IV da Constituição), o quociente eleitoral aproximado. É referência
de teto (quem tira essa votação garante vaga sozinho), não piso: o sistema
proporcional também depende do desempenho do partido/coligação, então boa
parte dos vereadores eleitos tem votação abaixo disso (ver quantos, de
verdade, na página **Curral Eleitoral**, com a votação real de 2024).

Uma terceira métrica, junto com total e concentração, é **densidade**
(eleitores do filtro por km², área da própria zona ou bairro): uma
referência geográfica de onde uma campanha de porta em porta rende mais
gente por área percorrida, não um dado real de custo de campanha (que
este projeto não tem e não fabrica).

## Curral eleitoral

Diferente de tudo até aqui, isto é resultado real de eleição passada, não
composição demográfica nem aproximação nenhuma: onde um candidato
específico teve força de verdade. É a exceção ao "pouco dado histórico"
do escopo, porque nenhum outro dado do projeto responde essa pergunta.

Fonte: TSE, conjunto "Votação nominal por candidato, por município e
zona" (`votacao_candidato_munzona`), baixado por `src/baixar_dados_tse.py`
e tratado por `src/tratar_resultados.py`:

```bash
python src/tratar_resultados.py --ano 2024
python src/tratar_resultados.py --ano 2022
```

Cada linha do CSV bruto já é um candidato numa zona (RJ inteiro em 2024
são só ~80 mil linhas, não precisa processar em pedaços como
`perfil_secao`). O tratamento filtra fora eleições que não são a
principal do ano (o arquivo de 2024, por exemplo, trazia junto uma
eleição suplementar de Três Rios de outubro/2025, por causa de uma
decisão judicial específica daquele município) e grava
`data/processed/votacao_<ano>.parquet`.

A página **Análise do Eleitorado > Curral Eleitoral** escolhe primeiro um
**cargo**, que decide o resto do fluxo:

- **Vereador e prefeito** (2024) só disputam dentro do próprio município,
  então o próximo passo é escolher um. Prefeito também tem turno (só
  relevante pra ele: em 2024 só Niterói e Petrópolis foram pro 2º turno
  no RJ).
- **Governador, senador, deputado estadual e deputado federal** (2022) têm
  o mesmo candidato nos 92 municípios do RJ, então município vira um
  filtro opcional pra focar numa região (o padrão é o estado inteiro), não
  um passo obrigatório. Deputado estadual e deputado federal passam de mil
  candidatos cada um no RJ; por padrão a lista mostra só quem se elegeu,
  com uma caixa pra revelar todo mundo.

Depois de escolher o cargo e o recorte, a página oferece 3 jeitos de olhar
pro mesmo dado (`app/mapa_curral_eleitoral.py`), todos reaproveitando a
mesma geometria de zona da página de Perfil por Zona:

- **Um candidato**: o fluxo original. Mostra o total de votos dele, a
  situação (eleito por quociente partidário, por média, não eleito etc.) e
  quanto vem das 3 zonas mais fortes (o indicador de "quão forte é o
  curral"). O mapa colore por votos absolutos ou por **densidade** (votos
  por km², opção nova): densidade evita que uma zona rural grande pareça
  "mais forte" só por ter mais área, é votos por km² mesmo, não voto
  total.
- **Quem venceu em cada zona**: mapa de dominância, cor categórica em vez
  de gradiente. Olha todo mundo que concorreu (não só quem passou num
  filtro), e mostra o candidato mais votado em cada zona. Como um cargo
  proporcional (deputado) pode ter mais de mil candidatos, só os que mais
  "vencem" zona ganham cor própria (até 8); o resto entra em "Outros"
  (cinza), senão a legenda vira ilegível. A tabela de apoio (zonas
  vencidas por candidato) não tem esse limite, lista todo mundo que
  venceu ao menos 1 zona.
- **Comparar 2 candidatos**: mapa divergente (roxo de um lado, âmbar do
  outro, neutro no empate técnico), pela vantagem em pontos percentuais
  de A sobre B em cada zona. Bom pra rivalidade direta (ex.: Castro x
  Freixo no governo de 2022, ainda que Castro tenha vencido só no 1º
  turno).

**Cobertura de hoje**: vereador e prefeito (2024, com os dois turnos) e
governador, senador, deputado estadual e deputado federal (2022, só 1º
turno). Falta só **presidente**: não vem no arquivo do RJ porque o TSE
publica o resultado dele só no arquivo nacional ("BR"), já que o
candidato é o mesmo em todo o país, não teria sentido duplicar por UF.

Sobre o 2022 só ter 1º turno: não é um dado faltando, é o resultado real.
O governador Cláudio Castro (PL) se reelegeu já no 1º turno, em
02/10/2022, com 58,67% dos votos válidos contra 27,38% de Marcelo Freixo
(PSB), o primeiro governador reeleito no 1º turno desde Sérgio Cabral em
2010 (fonte: [TSE](https://www.tse.jus.br/comunicacao/noticias/2022/Outubro/claudio-castro-pl-e-releito-governador-do-rj)).
Senador e deputado (estadual e federal) no Brasil nunca têm 2º turno,
então o arquivo de 2022 do RJ está completo do jeito que é: nenhum desses
4 cargos teve um 2º turno pra faltar.

Também não temos o nível de seção eleitoral (só município e zona), TSE
publica isso num conjunto à parte ("Votação por seção eleitoral"), mais
pesado; se um dia for atrás, dá pra descer a granularidade do curral
eleitoral no mesmo nível de bairro que já existe no Perfil por Zona.

## Pontos de interesse (transporte, comércio) via OpenStreetMap

Investigado como possível camada adicional (transporte público, shopping
centers etc., úteis para cruzar com a área de influência de cada zona). O
OSM tem as tags certas para isso: `highway=bus_stop` (ponto de ônibus),
`railway=station` combinado com `station=subway` ou `station=light_rail`
(metrô e VLT), `railway=station` sozinho (trem, SuperVia),
`amenity=bus_station` (terminal), `shop=mall` (shopping),
`amenity=place_of_worship` (igrejas, relevante para o perfil eleitoral no
Brasil).

Mas, assim como TSE e IBGE, nenhuma fonte testada de dados do OSM é
acessível nesta sessão: a Overpass API (`overpass-api.de`,
`overpass.kumi.systems`), o Geofabrik e o extrato regional do
OpenStreetMap France (`download.openstreetmap.fr`) devolveram bloqueio de
rede, assim como os serviços ArcGIS da própria prefeitura do Rio
(`pgeo3.rio.rj.gov.br`, que tem uma camada de transporte público). Ao
contrário dos setores censitários, ainda não foi encontrado um espelho
desses dados no GitHub. Para usar essa camada, vai precisar da mesma ponte
usada para os dados do TSE: alguém com acesso de rede baixa o extrato
(Overpass Turbo ou Geofabrik, recorte RJ) e sobe pro repositório.

## Dados pendentes

Esta sessão roda num ambiente sem acesso de rede a sites externos (TSE, IBGE, Wikipédia bloqueados). A população dos municípios e os salários foram obtidos por busca (com fonte) ou colados manualmente a partir da Wikipédia, não baixados de um arquivo oficial.

- **Salário de prefeito por município**: não existe fórmula constitucional (é fixado por lei de cada Câmara Municipal). Hoje o app mostra só o exemplo da capital.
- **Salário efetivo de vereador por município**: o app mostra o teto legal (máximo permitido), não o valor que cada Câmara efetivamente paga, que pode ser menor.

O contorno geográfico dos municípios (para o mapa) veio de um repositório público no GitHub (`raw.githubusercontent.com`, não bloqueado aqui), então esse item não teve o mesmo problema.

**Correção importante em `app/geo/rj_municipios.geojson`**: 6 municípios com litoral complexo
(Rio de Janeiro, Macaé, Paraty, Angra dos Reis, Mangaratiba, Itaguaí) tinham a
geometria corrompida na fonte original: cada ilha virou um "anel" a mais dentro
de um único `Polygon`, em vez de cada uma virar seu próprio polígono num
`MultiPolygon`. O GeoJSON tratava o primeiro anel como área externa e todo o
resto como buraco a subtrair, dando geometria inválida (área negativa,
`is_valid=False`) e, no caso do Rio, um polígono efetivamente de ~200 metros
de largura. Corrigido reconstruindo cada um como a união de seus anéis como
polígonos independentes; as áreas resultantes batem com os valores reais
conhecidos (Rio: 1.186,6 km², Macaé: 1.217,6 km², Paraty: 926,7 km² etc.) e a
cobertura de pontos do TSE dentro do próprio contorno subiu de 66% para 99,8%
do estado inteiro. Não é possível garantir que os mapas mostrados antes dessa
correção estivessem exibindo o Rio de Janeiro corretamente.

Sobre o mapa em si: a primeira versão usava Leaflet (via `folium`), mas a biblioteca e as camadas de mapa (tiles) vêm de CDNs externos (jsdelivr, CartoDB, OpenStreetMap), todos bloqueados nesta sessão. Trocado por um mapa estático com `geopandas`/`matplotlib`, que não depende de nada externo em tempo de execução, nem aqui nem para quem for rodar o app.

Os dados do TSE não têm mais esse problema: quem roda o projeto numa máquina com
acesso de rede normal (Windows, por causa do BITS) baixa tudo com
`python src/baixar_dados_tse.py`, sem depender do GitHub como ponte. A ponte
continua necessária só para as fontes que seguem inacessíveis, como o OSM.

## Próximos passos

- [x] Página de funções e deveres dos cargos eletivos
- [x] Identidade visual (tema roxo ardósia + âmbar)
- [x] Definir recorte geográfico (RJ, 92 municípios)
- [x] Definir pleitos e separar o app em duas seções (municipal / estadual e federal)
- [x] Quantidade de vagas por cargo no RJ
- [x] Vereadores por município (1.376 no total), com base na população do Censo 2022
- [x] Salário de presidente, governador, senador, deputado federal e deputado estadual
- [x] Teto legal de subsídio de vereador por município
- [x] Primeiro mapa coroplético (população, vereadores ou teto de subsídio por município)
- [x] Diagrama Executivo x Legislativo, com definição de cada poder e órgãos subordinados no estado e no município
- [x] Baixar os dados de eleitorado do TSE para o RJ (locais de votação, perfil por seção, eleitores com deficiência)
- [x] Locais de votação no mapa (5.038 pontos, camada opcional)
- [x] Área de influência de cada zona eleitoral (setor censitário + local mais próximo, dissolvido por zona), estado inteiro e zoom no Rio
- [x] Tratar `perfil_secao` e gerar agregado por zona em `data/processed/`
- [x] Página de perfil do eleitorado por zona, com filtros combináveis e mapa com zoom automático
- [x] Recorte espacial por município, e perfil do eleitorado por bairro dentro de 1 município
- [x] Mapa para o Pleito Estadual e Federal (eleitorado real por município, já que esses cargos não têm vaga municipal)
- [x] Quociente eleitoral aproximado (votos que garantem vaga de vereador) e densidade (eleitores por km²) na Análise do Eleitorado
- [x] Script único para baixar os brutos do TSE (`src/baixar_dados_tse.py`), com os brutos fora do versionamento
- [ ] Desrastrear os `.gz`/`.gz.part*` legados de `data/raw/` e remover `src/restaurar_dados.py`
- [ ] Tratar `perfil_deficiencia` e gerar agregado em `data/processed/`
- [ ] Pontos de interesse (transporte público, comércio) via OpenStreetMap, quando achar uma fonte acessível
- [ ] Renda por setor censitário (IBGE), para cruzar com o perfil do eleitorado
- [ ] Salário efetivo de prefeito e vereador por município (além do teto/exemplo)
- [x] Curral eleitoral: votação real por candidato, município e zona (vereador e prefeito, 2024)
- [x] Curral eleitoral pra governador, senador, deputado estadual e deputado federal (2022)
- [x] 3 jeitos de visualizar o curral eleitoral no mapa: 1 candidato (votos ou densidade), dominância por zona e comparação entre 2 candidatos
- [ ] Curral eleitoral pra presidente (falta achar o arquivo nacional "BR" do TSE, ver "Curral eleitoral" acima)
- [ ] Curral eleitoral no nível de seção/bairro, se um dia buscarmos "Votação por seção eleitoral" do TSE
- [ ] Cruzar com dados eleitorais de fato (candidatos, votação) quando o pleito de 2026 tiver dados
