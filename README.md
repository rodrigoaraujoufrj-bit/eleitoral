# Eleitoral

Projeto de análise geoespacial e dashboard interativo sobre a política eletiva do estado do Rio de Janeiro (RJ), a partir de dados abertos do TSE (Tribunal Superior Eleitoral) e do IBGE.

## Escopo

- **Recorte geográfico**: estado do Rio de Janeiro e seus 92 municípios (sem outros estados)
- **Sem dados históricos**: o foco é o pleito atual/próximo de cada cargo, não série histórica de eleições passadas
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
- **Pleito Estadual e Federal**: deputado estadual, deputado federal, senador, governador e presidente, quantas vagas no RJ e o que cada cargo faz
- **Análise do Eleitorado**: perfil do eleitorado por zona (gênero, faixa etária, escolaridade, raça/cor), com filtros combináveis e mapa que dá zoom nas zonas onde o perfil filtrado é mais forte

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
│   ├── mapa_perfil_eleitorado.py # mapa coroplético por zona, com zoom nas zonas filtradas
│   ├── diagrama_poderes.py       # diagrama Executivo x Legislativo e órgãos subordinados
│   ├── geo/
│   │   ├── rj_municipios.geojson          # contorno dos 92 municípios (fonte: GitHub, tbrugz/geodata-br)
│   │   └── rj_setores_censitarios.parquet # setores censitários do RJ (fonte: GitHub, ipea/geobr_prep_data)
│   └── views/
│       ├── home.py
│       ├── pleito_municipal.py
│       ├── pleito_estadual_federal.py
│       └── perfil_eleitorado.py
├── src/
│   ├── restaurar_dados.py        # remonta e descomprime os brutos do TSE
│   └── tratar_perfil_secao.py    # agrega o perfil do eleitorado por zona
├── data/
│   ├── raw/        # brutos do TSE, versionados comprimidos (ver abaixo)
│   │   ├── locais_votacao/       # eleitorado por local de votação (RJ)
│   │   ├── perfil_secao/         # perfil do eleitorado por seção (RJ)
│   │   └── perfil_deficiencia/   # eleitores com deficiência (RJ)
│   └── processed/  # dados já tratados (não versionados), ver `perfil_eleitorado_zona.parquet`
├── notebooks/      # exploração e prototipagem
├── requirements.txt
└── README.md
```

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

## Dados brutos do TSE

Três conjuntos de dados abertos do TSE, todos com recorte **RJ** e referentes à
eleição de **04/10/2026**, estão versionados em `data/raw/`. Como os CSVs
originais somam ~1,8 GB e o GitHub rejeita arquivos acima de 100 MiB, eles
entram no repositório **comprimidos com gzip**; o maior deles é ainda dividido
em partes de 90 MiB.

Para gerar os `.csv` a partir do que está versionado:

```bash
python src/restaurar_dados.py              # restaura o que estiver faltando
python src/restaurar_dados.py --verificar  # só confere os sha256
```

O script remonta as partes, descomprime e valida o SHA-256 de cada arquivo. Os
`.csv` resultantes ficam fora do versionamento (`.gitignore`), então rodá-lo é o
primeiro passo depois de clonar.

| Conjunto | Arquivo | Linhas | CSV | No repo |
|---|---|---:|---:|---:|
| `locais_votacao` | `eleitorado_local_votacao_2026_RJ.csv` | 38.739 | 15,2 MB | 2,9 MB |
| `perfil_secao` | `perfil_eleitor_secao_2026_RJ.csv` | 6.943.094 | 1,66 GB | 202 MB (3 partes) |
| `perfil_deficiencia` | `perfil_eleitor_deficiencia_2026_RJ.csv` | 155.199 | 36,2 MB | 2,6 MB |

Cada pasta traz o `leiame.pdf` original do respectivo conjunto, são documentos
**diferentes** entre si, um por conjunto.

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

Origem: <https://dadosabertos.tse.jus.br/>. O CDN do TSE (`cdn.tse.jus.br`) fica
atrás de Akamai e bloqueia clientes de linha de comando por fingerprint TLS,
`curl` e `Invoke-WebRequest` levam 403 mesmo com cabeçalhos de navegador. O
download funcionou via `Start-BitsTransfer` (WinHTTP).

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

## Perfil do eleitorado por zona

`src/tratar_perfil_secao.py` agrega `perfil_secao` (6,9 milhões de linhas,
uma por combinação de seção e categoria) por zona eleitoral, somando
`QT_ELEITORES` em quatro dimensões publicadas pelo TSE: gênero, faixa
etária, grau de escolaridade e raça/cor. Mantém a combinação completa
dessas quatro dimensões por zona (não cada uma separada), porque é isso
que permite depois filtrar por mais de uma dimensão ao mesmo tempo (por
exemplo "mulheres jovens com ensino médio incompleto") sem perder a
relação entre elas. Roda em menos de 30 segundos (lê o CSV em pedaços de
500 mil linhas, já agregando cada pedaço antes de somar, para não
estourar memória com um arquivo de 1,7 GB) e gera
`data/processed/perfil_eleitorado_zona.parquet` (182 mil linhas, bem
abaixo do teto teórico de combinações possíveis), não versionado:

```bash
python src/tratar_perfil_secao.py
```

Validado: as 165 zonas batem exatamente com as de `locais_votacao.py`, o
total de eleitores do RJ (12,86 milhões) é compatível com o esperado para
o estado, e sem nenhum filtro aplicado cada zona soma exatamente 100% do
seu próprio eleitorado (garantindo que a agregação não perde nem duplica
ninguém).

A página **Análise do Eleitorado > Perfil por Zona** usa isso: o usuário
combina filtros de gênero, faixa etária, escolaridade e raça/cor
(`app/perfil_eleitorado.py` calcula, por zona, quantos eleitores passam no
filtro e qual fração é da zona toda), escolhe se quer ordenar pelo número
absoluto ou pelo percentual de concentração, e o mapa
(`app/mapa_perfil_eleitorado.py`) dá zoom automaticamente nas zonas de
maior valor, com a borda destacada em âmbar. Uma zona pode abranger mais
de um município (18 das 165 no RJ); nesses casos a tabela mostra os nomes
separados por "/", do que tem mais eleitores na zona para o que tem menos.

É composição demográfica do eleitorado registrado (dado real do TSE), não
dado de comportamento, consumo ou intenção de voto, e a página deixa isso
explícito para quem for usar a ferramenta.

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

Os locais de votação vieram assim: outra sessão do Claude Code, rodando localmente (sem essa restrição de rede), baixou os três conjuntos do TSE e subiu pro GitHub comprimidos, seguindo o padrão de "usar o GitHub como ponte" descrito acima.

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
- [ ] Tratar `perfil_deficiencia` e gerar agregado em `data/processed/`
- [ ] Pontos de interesse (transporte público, comércio) via OpenStreetMap, quando achar uma fonte acessível
- [ ] Renda por setor censitário (IBGE), para cruzar com o perfil do eleitorado
- [ ] Salário efetivo de prefeito e vereador por município (além do teto/exemplo)
- [ ] Mapas para o Pleito Estadual e Federal
- [ ] Cruzar com dados eleitorais de fato (candidatos, votação) quando o pleito de 2026 tiver dados
