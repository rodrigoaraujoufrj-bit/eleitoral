"""Baixa os dados brutos do TSE usados pelo projeto, direto do CDN oficial.

Os brutos não são versionados (veja `.gitignore`): somam ~2,3 GB, e um deles
sozinho tem 1,7 GB, muito acima do limite de 100 MiB por arquivo do GitHub.
Este script é o primeiro passo depois de clonar o repositório.

    python src/baixar_dados_tse.py                  # baixa o que estiver faltando
    python src/baixar_dados_tse.py --listar         # só mostra o que falta, não baixa
    python src/baixar_dados_tse.py --conjunto resultados_2024 perfil_secao_2026
    python src/baixar_dados_tse.py --forcar         # rebaixa mesmo se o CSV existir
    python src/baixar_dados_tse.py --manter-zip     # não apaga o .zip após extrair

É idempotente: um conjunto cujo CSV já existe é pulado, então rodar de novo
depois de uma interrupção só completa o que falta.

## Por que PowerShell/BITS no Windows

O CDN do TSE (`cdn.tse.jus.br`) fica atrás da Akamai, que barra clientes de
linha de comando por *fingerprint* TLS: `curl`, `requests` e `urllib` levam
**403 Forbidden** mesmo enviando cabeçalhos de navegador, porque o bloqueio
não olha o User-Agent, e sim a assinatura do handshake TLS. O que funciona no
Windows é o **BITS** (`Start-BitsTransfer`), que baixa pela pilha WinHTTP do
sistema e passa. Por isso, no Windows, o download é delegado ao PowerShell.

Fora do Windows não há BITS; o script cai para `urllib` e, se a Akamai barrar,
explica o que fazer (baixar pelo navegador e apontar --zips-em).

## Os zips do TSE

Quase todos os zips são **nacionais**: trazem um CSV por UF mais um
`BRASIL`, além do `leiame.pdf` do conjunto. Só extraímos o CSV do RJ e o
`leiame.pdf`, o resto é descartado sem nunca tocar o disco. A exceção é
`perfil_eleitor_secao`, que o TSE já publica por UF.

## Lendo os CSVs depois

São `ISO-8859-1` (Latin-1), separador `;`, campos de texto entre aspas duplas
e **vírgula decimal**:

    pd.read_csv(caminho, sep=";", encoding="latin-1", decimal=",")

Nos campos numéricos, `-1` é código de **ausência de dado** (`#NULO` nos
campos de texto), e `-3` significa que naquele ano o dado nem era registrado
(`#NE`). Nenhum dos dois é valor real: filtre antes de somar ou tirar média.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA_RAW = RAIZ / "data" / "raw"
BASE = "https://cdn.tse.jus.br/estatistica/sead/odsele"

# Cada conjunto: de onde baixa, em que pasta de data/raw/ cai, e qual arquivo
# de dentro do zip interessa. `zip_aprox` é só para avisar o tamanho antes de
# começar (conferido em 08/09/2026); o valor real vem do próprio servidor.
CONJUNTOS = [
    {
        "chave": "resultados_2022",
        "pasta": "resultados",
        "url": f"{BASE}/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip",
        "csv": "votacao_candidato_munzona_2022_RJ.csv",
        "leiame": "leiame_2022.pdf",
        "zip_aprox": 580_343_288,
        "descricao": "Votação por candidato, município e zona - eleição 2022",
    },
    {
        "chave": "resultados_2024",
        "pasta": "resultados",
        "url": f"{BASE}/votacao_candidato_munzona/votacao_candidato_munzona_2024.zip",
        "csv": "votacao_candidato_munzona_2024_RJ.csv",
        "leiame": "leiame_2024.pdf",
        "zip_aprox": 49_612_998,
        "descricao": "Votação por candidato, município e zona - eleição 2024",
    },
    {
        "chave": "locais_votacao_2026",
        "pasta": "locais_votacao",
        "url": f"{BASE}/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip",
        "csv": "eleitorado_local_votacao_2026_RJ.csv",
        "leiame": "leiame.pdf",
        "zip_aprox": 87_570_807,
        "descricao": "Eleitorado por local de votação (traz lat/lon) - 2026",
    },
    {
        "chave": "perfil_secao_2026",
        "pasta": "perfil_secao",
        # Único já publicado por UF: o zip nacional não existe para este conjunto.
        "url": f"{BASE}/perfil_eleitor_secao/perfil_eleitor_secao_2026_RJ.zip",
        "csv": "perfil_eleitor_secao_2026_RJ.csv",
        "leiame": "leiame.pdf",
        "zip_aprox": 211_731_916,
        "descricao": "Perfil do eleitorado por seção (1,7 GB depois de extrair) - 2026",
    },
    {
        "chave": "perfil_deficiencia_2026",
        "pasta": "perfil_deficiencia",
        # Atenção ao nome misturado: a pasta no CDN é "deficiente", o arquivo é
        # "deficiencia". Trocar um pelo outro dá 404.
        "url": f"{BASE}/perfil_eleitor_deficiente/perfil_eleitor_deficiencia_2026.zip",
        "csv": "perfil_eleitor_deficiencia_2026_RJ.csv",
        "leiame": "leiame.pdf",
        "zip_aprox": 92_591_610,
        "descricao": "Eleitores com deficiência, microdado individual - 2026",
    },
]

BLOCO = 4 * 1024 * 1024

# Roda um Start-BitsTransfer assíncrono e reporta o progresso em linhas
# simples, para o Python ir imprimindo enquanto baixa. Enquanto o BITS
# negocia a conexão, BytesTotal vem como UInt64.MaxValue (= desconhecido).
PS_BAIXAR = r"""
param([Parameter(Mandatory=$true)][string]$Url,
      [Parameter(Mandatory=$true)][string]$Destino)

$ErrorActionPreference = 'Stop'
$DESCONHECIDO = [uint64]::MaxValue

try {
    $job = Start-BitsTransfer -Source $Url -Destination $Destino `
                              -Asynchronous -DisplayName 'tse-download'
} catch {
    Write-Output ("ERRO " + $_.Exception.Message)
    exit 1
}

while ($true) {
    Start-Sleep -Milliseconds 500
    $job = Get-BitsTransfer -JobId $job.JobId
    if ($null -eq $job) { Write-Output "ERRO job do BITS sumiu"; exit 1 }

    if ($job.JobState -eq 'Transferred') {
        Complete-BitsTransfer -BitsJob $job
        Write-Output "FIM"
        exit 0
    }
    if ($job.JobState -eq 'Error' -or $job.JobState -eq 'TransientError') {
        $msg = $job.ErrorDescription
        if (-not $msg) { $msg = "estado " + $job.JobState }
        Remove-BitsTransfer -BitsJob $job -ErrorAction SilentlyContinue
        Write-Output ("ERRO " + ($msg -replace '\s+', ' ').Trim())
        exit 1
    }
    $total = $job.BytesTotal
    if ($total -eq $DESCONHECIDO) { $total = 0 }
    Write-Output ("PROG {0} {1}" -f $job.BytesTransferred, $total)
}
"""


def humano(n: float) -> str:
    for unidade in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unidade == "GB":
            return f"{n:,.1f} {unidade}".replace(",", "@").replace(".", ",").replace("@", ".")
        n /= 1024
    return f"{n} B"


def _powershell() -> str | None:
    """Windows PowerShell primeiro: o módulo BitsTransfer é nativo lá."""
    for exe in ("powershell.exe", "pwsh.exe", "pwsh"):
        caminho = shutil.which(exe)
        if caminho:
            return caminho
    return None


def _progresso(baixado: int, total: int) -> None:
    if total:
        pct = 100 * baixado / total
        linha = f"    {humano(baixado)} / {humano(total)}  ({pct:5.1f}%)"
    else:
        linha = f"    {humano(baixado)}  (conectando...)"
    print(linha.ljust(60), end="\r", flush=True)


def baixar_bits(url: str, destino: Path) -> None:
    """Baixa via BITS (Windows). Levanta RuntimeError se falhar."""
    exe = _powershell()
    if not exe:
        raise RuntimeError("PowerShell não encontrado no PATH")

    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as f:
        f.write(PS_BAIXAR)
        script = Path(f.name)

    try:
        proc = subprocess.Popen(
            [exe, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(script), "-Url", url, "-Destino", str(destino)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        erro = None
        assert proc.stdout is not None
        for linha in proc.stdout:
            linha = linha.strip()
            if linha.startswith("PROG "):
                _, baixado, total = linha.split()
                _progresso(int(baixado), int(total))
            elif linha.startswith("ERRO "):
                erro = linha[5:]
            elif linha == "FIM":
                pass
            elif linha:
                erro = linha
        proc.wait()
        print(" " * 60, end="\r")
        if proc.returncode != 0:
            raise RuntimeError(erro or f"BITS terminou com código {proc.returncode}")
    finally:
        script.unlink(missing_ok=True)


def baixar_urllib(url: str, destino: Path) -> None:
    """Fallback fora do Windows. A Akamai costuma barrar; a mensagem explica."""
    import urllib.error
    import urllib.request

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            total = int(resp.headers.get("Content-Length") or 0)
            baixado = 0
            with destino.open("wb") as saida:
                while bloco := resp.read(BLOCO):
                    saida.write(bloco)
                    baixado += len(bloco)
                    _progresso(baixado, total)
            print(" " * 60, end="\r")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            raise RuntimeError(
                "403 Forbidden: o CDN do TSE barra clientes que não sejam navegador "
                "(fingerprint TLS). Fora do Windows não há BITS. Baixe os zips pelo "
                "navegador e rode de novo com --zips-em <pasta>."
            ) from e
        raise RuntimeError(f"HTTP {e.code} ao baixar {url}") from e


def baixar(url: str, destino: Path) -> None:
    if destino.exists():
        destino.unlink()  # BITS recusa destino já existente
    destino.parent.mkdir(parents=True, exist_ok=True)
    if platform.system() == "Windows":
        baixar_bits(url, destino)
    else:
        baixar_urllib(url, destino)


def extrair(zip_path: Path, conjunto: dict, pasta: Path) -> bool:
    """Extrai só o CSV do RJ e o leiame.pdf. Ignora as outras UFs e o BRASIL."""
    alvo_csv = conjunto["csv"].lower()
    with zipfile.ZipFile(zip_path) as zf:
        info_csv = None
        info_leiame = None
        for info in zf.infolist():
            if info.is_dir():
                continue
            nome = Path(info.filename).name.lower()
            if nome == alvo_csv:
                info_csv = info
            elif nome == "leiame.pdf":
                info_leiame = info

        if info_csv is None:
            dentro = sorted(Path(i.filename).name for i in zf.infolist() if not i.is_dir())
            print(f"    ERRO: {conjunto['csv']} não está no zip. Contém: {dentro[:6]}...")
            return False

        destino_csv = pasta / conjunto["csv"]
        print(f"    extraindo {conjunto['csv']} ({humano(info_csv.file_size)})...")
        with zf.open(info_csv) as entrada, destino_csv.open("wb") as saida:
            shutil.copyfileobj(entrada, saida, BLOCO)

        if destino_csv.stat().st_size != info_csv.file_size:
            print(f"    ERRO: {conjunto['csv']} saiu com tamanho diferente do declarado no zip")
            return False

        if info_leiame is not None:
            with zf.open(info_leiame) as entrada, (pasta / conjunto["leiame"]).open("wb") as saida:
                shutil.copyfileobj(entrada, saida, BLOCO)
        else:
            print("    aviso: este zip não trouxe leiame.pdf")

    return True


def processar(conjunto: dict, forcar: bool, manter_zip: bool, zips_em: Path | None) -> bool:
    pasta = DATA_RAW / conjunto["pasta"]
    destino_csv = pasta / conjunto["csv"]
    print(f"[{conjunto['chave']}] {conjunto['descricao']}")

    if destino_csv.exists() and not forcar:
        print(f"    já existe {conjunto['csv']} ({humano(destino_csv.stat().st_size)}) - pulando\n")
        return True

    pasta.mkdir(parents=True, exist_ok=True)
    nome_zip = conjunto["url"].rsplit("/", 1)[-1]

    if zips_em is not None:
        zip_path = zips_em / nome_zip
        if not zip_path.exists():
            print(f"    ERRO: {zip_path} não encontrado (--zips-em)\n")
            return False
        apagar_zip = False
    else:
        zip_path = pasta / nome_zip
        apagar_zip = not manter_zip
        print(f"    baixando {nome_zip} (~{humano(conjunto['zip_aprox'])})...")
        try:
            baixar(conjunto["url"], zip_path)
        except RuntimeError as e:
            print(f"    ERRO no download: {e}\n")
            return False

    try:
        ok = extrair(zip_path, conjunto, pasta)
    except zipfile.BadZipFile:
        print("    ERRO: o arquivo baixado não é um zip válido (download incompleto?)\n")
        return False
    finally:
        if apagar_zip and zip_path.exists():
            zip_path.unlink()

    if ok:
        print(f"    OK  {destino_csv.relative_to(RAIZ)} ({humano(destino_csv.stat().st_size)})\n")
    else:
        print()
    return ok


def main() -> int:
    p = argparse.ArgumentParser(
        description="Baixa os dados brutos do TSE (recorte RJ) para data/raw/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--conjunto", nargs="+", metavar="CHAVE",
                   choices=[c["chave"] for c in CONJUNTOS],
                   help="baixa só os conjuntos indicados (padrão: todos)")
    p.add_argument("--forcar", action="store_true", help="rebaixa mesmo se o CSV já existir")
    p.add_argument("--manter-zip", action="store_true", help="não apaga o .zip depois de extrair")
    p.add_argument("--listar", action="store_true", help="mostra o que falta e sai, sem baixar")
    p.add_argument("--zips-em", metavar="PASTA", type=Path,
                   help="usa zips já baixados nessa pasta em vez de baixar do TSE")
    args = p.parse_args()

    escolhidos = CONJUNTOS
    if args.conjunto:
        escolhidos = [c for c in CONJUNTOS if c["chave"] in args.conjunto]

    print(f"data/raw em {DATA_RAW}\n")

    if args.listar:
        for c in CONJUNTOS:
            csv = DATA_RAW / c["pasta"] / c["csv"]
            estado = f"presente ({humano(csv.stat().st_size)})" if csv.exists() else "FALTANDO"
            print(f"  {c['chave']:<24} {estado:<22} zip ~{humano(c['zip_aprox'])}")
        return 0

    if args.zips_em is not None and not args.zips_em.is_dir():
        print(f"ERRO: --zips-em {args.zips_em} não é uma pasta")
        return 1

    if platform.system() != "Windows" and args.zips_em is None:
        print("Aviso: fora do Windows não há BITS, e o CDN do TSE costuma responder\n"
              "403 a clientes que não sejam navegador. Se falhar, baixe os zips no\n"
              "navegador e rode com --zips-em <pasta>.\n")

    resultados = [processar(c, args.forcar, args.manter_zip, args.zips_em) for c in escolhidos]
    ok = sum(resultados)
    print(f"{ok}/{len(resultados)} conjuntos prontos.")
    return 0 if ok == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
