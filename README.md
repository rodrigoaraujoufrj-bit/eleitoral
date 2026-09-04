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
- **Pleito Municipal**: vereador e prefeito — quantas vagas no RJ e o que cada cargo faz
- **Pleito Estadual e Federal**: deputado estadual, deputado federal, senador, governador e presidente — quantas vagas no RJ e o que cada cargo faz

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
│   ├── diagrama_poderes.py       # diagrama Executivo x Legislativo e órgãos subordinados
│   ├── geo/
│   │   └── rj_municipios.geojson # contorno dos 92 municípios (fonte: GitHub, tbrugz/geodata-br)
│   └── views/
│       ├── home.py
│       ├── pleito_municipal.py
│       └── pleito_estadual_federal.py
├── src/
│   └── restaurar_dados.py        # remonta e descomprime os brutos do TSE
├── data/
│   ├── raw/        # brutos do TSE, versionados comprimidos (ver abaixo)
│   │   ├── locais_votacao/       # eleitorado por local de votação (RJ)
│   │   ├── perfil_secao/         # perfil do eleitorado por seção (RJ)
│   │   └── perfil_deficiencia/   # eleitores com deficiência (RJ)
│   └── processed/  # dados já tratados (não versionados)
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

Cada pasta traz o `leiame.pdf` original do respectivo conjunto — são documentos
**diferentes** entre si, um por conjunto.

**Ao ler os CSVs**: são `ISO-8859-1` (Latin-1), sem BOM, separador `;`, campos de
texto entre aspas duplas. As coordenadas de `locais_votacao` usam **vírgula
decimal**, e `-1` é o código de ausência de valor (não um valor real).

```python
pd.read_csv(caminho, sep=";", encoding="latin-1", decimal=",")
```

A chave de junção entre os três conjuntos é `CD_MUNICIPIO` + `NR_ZONA` + `NR_SECAO`.
Atenção: `perfil_deficiencia` é **microdado individual** (uma linha por eleitor,
com `SQ_ELEITOR`), enquanto os outros dois são agregados — por isso este
repositório é privado.

`locais_votacao` tem cobertura de coordenada praticamente total: 2.918 dos
2.919 locais de votação únicos do RJ têm latitude/longitude válida (a mesma
escola pode reunir várias seções, por isso `app/locais_votacao.py` agrupa por
local antes de plotar). É a camada de pontos que aparece no mapa do Pleito
Municipal, opcional via checkbox.

Origem: <https://dadosabertos.tse.jus.br/>. O CDN do TSE (`cdn.tse.jus.br`) fica
atrás de Akamai e bloqueia clientes de linha de comando por fingerprint TLS —
`curl` e `Invoke-WebRequest` levam 403 mesmo com cabeçalhos de navegador. O
download funcionou via `Start-BitsTransfer` (WinHTTP).

## Dados pendentes

Esta sessão roda num ambiente sem acesso de rede a sites externos (TSE, IBGE, Wikipédia bloqueados). A população dos municípios e os salários foram obtidos por busca (com fonte) ou colados manualmente a partir da Wikipédia, não baixados de um arquivo oficial.

- **Salário de prefeito por município**: não existe fórmula constitucional (é fixado por lei de cada Câmara Municipal). Hoje o app mostra só o exemplo da capital.
- **Salário efetivo de vereador por município**: o app mostra o teto legal (máximo permitido), não o valor que cada Câmara efetivamente paga, que pode ser menor.

O contorno geográfico dos municípios (para o mapa) veio de um repositório público no GitHub (`raw.githubusercontent.com`, não bloqueado aqui), então esse item não teve o mesmo problema.

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
- [x] Locais de votação no mapa (2.918 pontos, camada opcional)
- [ ] Tratar `perfil_secao` e `perfil_deficiencia` e gerar agregados em `data/processed/`
- [ ] Salário efetivo de prefeito e vereador por município (além do teto/exemplo)
- [ ] Mapas para o Pleito Estadual e Federal
- [ ] Cruzar com dados eleitorais de fato (candidatos, votação) quando o pleito de 2026 tiver dados
