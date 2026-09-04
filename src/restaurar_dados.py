"""Restaura os CSVs brutos do TSE a partir dos arquivos versionados em data/raw.

Os CSVs originais somam ~1,8 GB, acima do limite de 100 MiB por arquivo do
GitHub. Por isso eles entram no repositorio comprimidos com gzip e, quando
ainda assim passam de 100 MiB, divididos em partes de 90 MiB.

Uso:
    python src/restaurar_dados.py              # restaura o que estiver faltando
    python src/restaurar_dados.py --forcar     # refaz mesmo se o CSV ja existir
    python src/restaurar_dados.py --verificar  # so confere os hashes, nao escreve

Depois de rodar, cada pasta de data/raw tem o .csv pronto para uso. Os CSVs
ficam fora do controle de versao (veja .gitignore); apenas os .gz e as partes
sao versionados.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA_RAW = RAIZ / "data" / "raw"

# Origem: dados abertos do TSE (https://dadosabertos.tse.jus.br/), eleicao de
# 04/10/2026, recorte RJ. sha256 e linhas referem-se ao CSV descomprimido.
CONJUNTOS = [
    {
        "pasta": "locais_votacao",
        "csv": "eleitorado_local_votacao_2026_RJ.csv",
        "partido": False,
        "bytes": 15_904_464,
        "linhas": 38_739,
        "sha256": "6291fd08e32f2e1b00eb04800bb880e02470436e10d7965b566987fb8cfdca09",
    },
    {
        "pasta": "perfil_deficiencia",
        "csv": "perfil_eleitor_deficiencia_2026_RJ.csv",
        "partido": False,
        "bytes": 38_009_537,
        "linhas": 155_199,
        "sha256": "52ed993fe495c502b0b5bdb0243be87038d19a9e81cd285b3e449edb98738921",
    },
    {
        "pasta": "perfil_secao",
        "csv": "perfil_eleitor_secao_2026_RJ.csv",
        "partido": True,  # dividido em .gz.part00, .part01, ...
        "bytes": 1_786_359_698,
        "linhas": 6_943_094,
        "sha256": "34d824aa9918a764e029eadf2ce0f48d53b658d5927564cb45cc3e0b7d0a0289",
    },
]

TAMANHO_BLOCO = 4 * 1024 * 1024


def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(TAMANHO_BLOCO), b""):
            h.update(bloco)
    return h.hexdigest()


def juntar_partes(destino_gz: Path, partes: list[Path]) -> None:
    """Concatena as partes em um unico .gz temporario."""
    with destino_gz.open("wb") as saida:
        for parte in partes:
            with parte.open("rb") as entrada:
                shutil.copyfileobj(entrada, saida, TAMANHO_BLOCO)


def descomprimir(origem_gz: Path, destino_csv: Path) -> None:
    with gzip.open(origem_gz, "rb") as entrada, destino_csv.open("wb") as saida:
        shutil.copyfileobj(entrada, saida, TAMANHO_BLOCO)


def restaurar(conjunto: dict, forcar: bool, apenas_verificar: bool) -> bool:
    pasta = DATA_RAW / conjunto["pasta"]
    csv = pasta / conjunto["csv"]
    nome = conjunto["csv"]

    if csv.exists() and not forcar:
        tamanho_ok = csv.stat().st_size == conjunto["bytes"]
        if apenas_verificar:
            digest = sha256_arquivo(csv)
            if digest == conjunto["sha256"]:
                print(f"  OK       {nome}  (sha256 confere)")
                return True
            print(f"  FALHOU   {nome}  (sha256 diferente do esperado)")
            return False
        if tamanho_ok:
            print(f"  ja existe {nome}  ({csv.stat().st_size:,} bytes) - pulando")
            return True
        print(f"  {nome} existe com tamanho inesperado, refazendo...")

    if apenas_verificar:
        print(f"  ausente  {nome}  (rode sem --verificar para restaurar)")
        return False

    gz_temporario = None
    if conjunto["partido"]:
        partes = sorted(pasta.glob(f"{nome}.gz.part*"))
        if not partes:
            print(f"  ERRO: nenhuma parte encontrada para {nome} em {pasta}")
            return False
        print(f"  juntando {len(partes)} partes de {nome}.gz ...")
        gz = pasta / f"{nome}.gz"
        juntar_partes(gz, partes)
        gz_temporario = gz
    else:
        gz = pasta / f"{nome}.gz"
        if not gz.exists():
            print(f"  ERRO: {gz} nao encontrado")
            return False

    print(f"  descomprimindo {gz.name} ...")
    descomprimir(gz, csv)

    if gz_temporario is not None:
        gz_temporario.unlink()

    digest = sha256_arquivo(csv)
    if digest != conjunto["sha256"]:
        print(f"  ERRO: sha256 de {nome} nao confere.")
        print(f"        esperado {conjunto['sha256']}")
        print(f"        obtido   {digest}")
        return False

    print(f"  OK       {nome}  ({csv.stat().st_size:,} bytes, {conjunto['linhas']:,} linhas)")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description="Restaura os CSVs brutos do TSE.")
    p.add_argument("--forcar", action="store_true", help="refaz mesmo se o CSV ja existir")
    p.add_argument("--verificar", action="store_true", help="so confere os hashes")
    args = p.parse_args()

    print(f"data/raw em {DATA_RAW}\n")
    resultados = [restaurar(c, args.forcar, args.verificar) for c in CONJUNTOS]

    ok = sum(resultados)
    print(f"\n{ok}/{len(resultados)} conjuntos prontos.")
    return 0 if ok == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
