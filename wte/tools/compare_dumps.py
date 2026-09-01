#!/usr/bin/env python3
"""Confronta a camada de dados Pascal com o `we2002_core`, nas duas ROMs.

Produto da WTE-TASK-20 -- o aceite da fase 3, e o primeiro momento em que o
projeto afirma algo **verificado** sobre dados.

O oraculo aqui nao e o `wte.exe` (esse esta morto -- CORR-WTE-044): e o
`we2002_core`, cujo `Load`/`Save` ja e byte-identico ao `ed.exe` nas duas ROMs.
Duas metades:

1. **leitura** -- `wte/tests/dump_estado.pas` e `dump_estado.cpp` despejam o
   mesmo formato, e o criterio e `diff` **vazio**. Aqui nao ha comportamento
   indefinido para preservar, entao zero divergencia e o unico resultado
   aceitavel;
2. **gravacao** -- `--roundtrip` dos dois faz Load+Save sobre copias limpas, e
   as duas imagens tem de sair **byte a byte iguais**. Aqui vale a ressalva
   conhecida: `Load`+`Save` sem editar nada NAO devolve a imagem intacta, e nao
   deveria -- o `Save` reconstroi as all-star a partir dos links e o original
   troca os dois primeiros cobradores de cada clube de ML. Isso e medido e
   registrado, nao escondido.

O par ser bilingue e o ponto, e e a razao dos dois `test_offsets.*` tambem: o
`fpc` le o Pascal gerado, o `g++` le o C++ original. Dois dumpers na mesma
linguagem esconderiam erro de leitura de literal.

**Medicao** (`--medir`) -- compila os dois, copia as ROMs para `work/`, roda,
compara, e escreve a evidencia em `wte/re/fase-3.tsv`:

    python3 wte/tools/compare_dumps.py --medir

**Geracao** (sem argumento, ou `--check`) -- le a evidencia versionada e
escreve `wte/re/fase-3.md`:

    python3 wte/tools/compare_dumps.py --check

A medicao NAO roda no `make check`: sao ~1,9 GB de copia e uns dois minutos.
Quem quiser refazer chama `--medir` a mao, ou roda o
`test_compare_dumps.py` com `WTE_ROUNDTRIP=1`. O `--check` confere o texto
gerado contra a evidencia, que e o que o resto da bateria faz.

**`roms/` nunca e alvo.** Copia em `work/`, sempre -- os tres editores gravam
in-place e cada imagem tem ~474 MB. `WTE_WORK` move o diretorio de copias para
fora da arvore, que e o que se quer quando o repositorio mora dentro de uma
pasta sincronizada.

**A MEDICAO DE REFERENCIA E A DO LINUX.** O `--medir` roda no Windows e da o
mesmo resultado no que importa -- 0 divergencia no dump e 0 byte no round-trip,
nas duas ROMs, medido em 2026-08-26 --, mas duas colunas mudam sem que nada
tenha regredido: o sidecar `_url.txt` sai com CRLF do lado C++ ali (3822 bytes
contra 1911), porque o `ofstream` dele e aberto em modo texto. E diferenca de
plataforma REGISTRADA DE PROPOSITO na §11 do `docs/PLAN-WINDOWS.md`, nao
defeito; o lado Pascal grava LF nas duas plataformas, por decisao propria. Nao
commite o `fase-3.tsv` de uma corrida Windows: ver a §6 de
`docs/PLAN-WTE-WINDOWS.md`.
"""

from __future__ import annotations

import argparse
import csv
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RE_DIR = ROOT / "wte" / "re"
TESTES = ROOT / "wte" / "tests"
NUCLEO = ROOT / "src" / "core"
# O diretorio das copias de trabalho. `work/` na raiz e o default, e e o que o
# `Makefile` da raiz ja usa.
#
# `WTE_WORK` existe por uma razao de maquina, nao de projeto: a medicao copia
# ~1,9 GB, e uma arvore dentro de uma pasta sincronizada -- OneDrive, Dropbox,
# Drive -- manda esse 1,9 GB para a nuvem antes de alguem apagar. Apontar para
# fora dela resolve sem mudar nada do que se mede.
WORK = Path(os.environ.get("WTE_WORK", "")) or ROOT / "work"

OUT_TSV = RE_DIR / "fase-3.tsv"
OUT_MD = RE_DIR / "fase-3.md"

# `Sofifa.cpp` fica de fora: e o unico que puxa libcurl, e nada do estado
# despejado vem dele.
FONTES_CPP = ["CdImage.cpp", "Database.cpp", "Player.cpp", "Tables.cpp",
              "Team.cpp", "TextCodec.cpp"]

# A descricao NAO e a do enunciado da task, e a divergencia e achado: a WTE-
# TASK-20 supunha a japonesa como "o unico teste real do codec". Medido, quem
# exercita os ramos de mapeamento do KanjiToAscii e a EUROPEIA -- a japonesa
# guarda katakana (`0x83`), que o codec nao conhece e transforma em espaco.
ROMS = [
    ("european-deluxe", "golden-european-deluxe.bin",
     "offsets, nomes latinos e os ramos de mapeamento do codec"),
    ("japanese", "japanese-shift-jis.bin",
     "o ramo padrao do codec: katakana vira espaco"),
    ("ptbr-remaster", "ptbr-remaster.bin",
     "os mesmos ramos do codec que a europeia, com oráculo vivo no wte/"),
]

COLS = ["rom", "arquivo", "o_que_valida", "linhas_dump", "divergencias_dump",
        "bytes_imagem", "faixas_rt_vs_original", "bytes_rt_vs_original",
        "divergencias_rt_pascal_vs_cpp", "sidecar_bytes", "sidecar_igual",
        "kanji_duplo", "kanji_decodificado", "squad_numbers_nao_zero"]


class CompareError(Exception):
    pass


# ------------------------------------------------------------- medicao -----


def compilar(tmp: Path) -> tuple[Path, Path]:
    fpc = shutil.which("fpc")
    gpp = shutil.which("g++")
    if not fpc or not gpp:
        raise CompareError(
            "sem fpc e/ou g++ -- o confronto e entre DOIS compiladores, e com "
            "um so\n       ele nao mede o que promete")
    unidades = tmp / "units"
    unidades.mkdir(parents=True, exist_ok=True)
    pas = tmp / "dump_pas"
    cpp = tmp / "dump_cpp"
    subprocess.run(
        [fpc, f"-Fu{ROOT / 'wte/src'}", f"-FU{unidades}", f"-o{pas}",
         str(TESTES / "dump_estado.pas")],
        check=True, capture_output=True, text=True)
    subprocess.run(
        [gpp, "-std=c++17", "-O1", f"-I{NUCLEO / 'include'}"]
        + [str(NUCLEO / f) for f in FONTES_CPP]
        + [str(TESTES / "dump_estado.cpp"), "-o", str(cpp)],
        check=True, capture_output=True, text=True)
    return pas, cpp


def faixas_diferentes(a: Path, b: Path) -> tuple[int, int]:
    """(numero de faixas, numero de bytes) em que os dois arquivos diferem.

    Faixa e corrida de bytes divergentes com folga de 16 -- mesmo criterio do
    `diff_dirigido.sh`, para que os dois numeros sejam comparaveis.
    """
    BLOCO = 1 << 22
    faixas = 0
    bytes_dif = 0
    ultimo = None
    pos = 0
    with a.open("rb") as fa, b.open("rb") as fb:
        while True:
            x, y = fa.read(BLOCO), fb.read(BLOCO)
            if not x and not y:
                break
            if x != y:
                for i in range(min(len(x), len(y))):
                    if x[i] != y[i]:
                        p = pos + i
                        bytes_dif += 1
                        if ultimo is None or p > ultimo + 16:
                            faixas += 1
                        ultimo = p
            pos += len(x)
    return faixas, bytes_dif


def medir_uma(nome: str, arquivo: str, valida: str, pas: Path, cpp: Path,
              tmp: Path) -> dict:
    origem = ROOT / "roms" / arquivo
    if not origem.is_file():
        raise CompareError(f"roms/{arquivo} nao existe")
    WORK.mkdir(exist_ok=True)

    # -- leitura: os dois dumps, sobre copias proprias.
    copias = {}
    for lado in ("pas", "cpp"):
        c = WORK / f"cmp-{nome}-{lado}.bin"
        shutil.copyfile(origem, c)
        copias[lado] = c
    saidas = {}
    for lado, exe in (("pas", pas), ("cpp", cpp)):
        r = subprocess.run([str(exe), str(copias[lado])],
                           check=True, capture_output=True, text=True)
        saidas[lado] = r.stdout
        (tmp / f"{nome}-{lado}.txt").write_text(r.stdout)

    linhas_pas = saidas["pas"].splitlines()
    linhas_cpp = saidas["cpp"].splitlines()
    divergencias = sum(1 for a, b in zip(linhas_pas, linhas_cpp) if a != b)
    divergencias += abs(len(linhas_pas) - len(linhas_cpp))

    # Medidas de cobertura, tiradas do proprio dump: sem elas, "codec
    # exercitado" e "bitfield conferido" seriam afirmacao sobre codigo que
    # pode nunca ter visto dado nao-zero.
    #
    # `kanji_duplo` conta o campo CRU com pelo menos um byte >= 0x80, que e o
    # que caracteriza Shift-JIS de dois bytes; `kanji_decodificado` conta a
    # saida do KanjiToAscii que nao e vazia nem so espaco. Os dois, e nao um:
    # contar so o campo nao-vazio dava 97 nas duas ROMs por coincidencia -- os
    # 97 registros existem em ambas -- e nao separava release nenhuma.
    def _hex(l: str) -> bytes:
        corpo = l.split(" = ", 1)[1]
        return bytes.fromhex(corpo.split(":", 1)[1])

    kanji_duplo = sum(1 for l in linhas_cpp
                      if ".raw_kanji_name = " in l
                      and any(b >= 0x80 for b in _hex(l)))
    kanji_dec = sum(1 for l in linhas_cpp
                    if ".kanji_name = " in l
                    and _hex(l).strip(b" \0"))
    squad = sum(1 for l in linhas_cpp
                if ".squad_numbers = " in l
                and set(l.split(" = ")[1].split(",")) != {"0"})

    # -- gravacao: Load+Save dos dois lados, sobre copias limpas.
    rt = {}
    for lado, exe in (("pas", pas), ("cpp", cpp)):
        c = WORK / f"rt-{nome}-{lado}.bin"
        shutil.copyfile(origem, c)
        subprocess.run([str(exe), "--roundtrip", str(c)],
                       check=True, capture_output=True, text=True)
        rt[lado] = c

    faixas_orig, bytes_orig = faixas_diferentes(origem, rt["cpp"])
    _, bytes_rt = faixas_diferentes(rt["pas"], rt["cpp"])

    side_pas = rt["pas"].with_name(rt["pas"].stem + "_url.txt")
    side_cpp = rt["cpp"].with_name(rt["cpp"].stem + "_url.txt")
    tem_sidecar = side_pas.is_file() and side_cpp.is_file()
    sidecar_igual = tem_sidecar and filecmp.cmp(side_pas, side_cpp, shallow=False)

    linha = {
        "rom": nome, "arquivo": arquivo, "o_que_valida": valida,
        "linhas_dump": len(linhas_cpp), "divergencias_dump": divergencias,
        "bytes_imagem": origem.stat().st_size,
        "faixas_rt_vs_original": faixas_orig,
        "bytes_rt_vs_original": bytes_orig,
        "divergencias_rt_pascal_vs_cpp": bytes_rt,
        "sidecar_bytes": side_cpp.stat().st_size if tem_sidecar else 0,
        "sidecar_igual": "sim" if sidecar_igual else "nao",
        "kanji_duplo": kanji_duplo,
        "kanji_decodificado": kanji_dec,
        "squad_numbers_nao_zero": squad,
    }
    for c in list(copias.values()) + list(rt.values()):
        c.unlink(missing_ok=True)
    for s in (side_pas, side_cpp):
        s.unlink(missing_ok=True)
    return linha


def medir(tmp: Path) -> int:
    pas, cpp = compilar(tmp)
    linhas = []
    for nome, arquivo, valida in ROMS:
        print(f">> {nome}")
        linha = medir_uma(nome, arquivo, valida, pas, cpp, tmp)
        print(f"   dump: {linha['linhas_dump']} linhas, "
              f"{linha['divergencias_dump']} divergencia(s)")
        print(f"   round-trip Pascal x C++: "
              f"{linha['divergencias_rt_pascal_vs_cpp']} byte(s)")
        linhas.append(linha)
    with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        for l in linhas:
            w.writerow(l)
    print(f"compare_dumps: {OUT_TSV.relative_to(ROOT)}: {len(linhas)} ROM(s)")

    # O AVISO SO EXISTE PORQUE ESTA MEDICAO PASSOU A RODAR EM DUAS PLATAFORMAS.
    #
    # O `fase-3.tsv` versionado e a evidencia do Linux. Uma corrida no Windows
    # o reescreve inteiro, e duas colunas mudam sem que nada tenha regredido --
    # o sidecar `_url.txt` sai com CRLF do lado C++ ali (`ofstream` em modo
    # texto, diferenca de plataforma registrada de proposito na §11 do
    # `docs/PLAN-WINDOWS.md`), enquanto o Pascal grava LF nas duas.
    #
    # Commitar isso trocaria uma medicao por outra, feita noutra maquina e com
    # outro compilador, e o `sidecar_igual = nao` viraria a evidencia oficial.
    if os.name != "posix":
        print()
        print("AVISO: esta corrida NAO e a de referencia.")
        print(f"       O {OUT_TSV.relative_to(ROOT).as_posix()} versionado e a "
              "medicao do Linux; nao commite este.")
        print("       Duas colunas divergem la sem regressao nenhuma -- o "
              "sidecar `_url.txt`")
        print("       sai com CRLF do lado C++ no Windows. Ver a §6 de "
              "docs/PLAN-WTE-WINDOWS.md.")
    return 0


# -------------------------------------------------------------- geracao ----


def ler_tsv() -> list[dict[str, str]]:
    if not OUT_TSV.exists():
        raise CompareError("sem evidencia: rode com --medir antes")
    with OUT_TSV.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def gerar() -> str:
    linhas = ler_tsv()
    L: list[str] = []

    def w(s: str = "") -> None:
        L.append(s)

    w("# `re/fase-3.md` — o aceite da camada de dados")
    w()
    w("**Gerado por [`wte/tools/compare_dumps.py`](../tools/compare_dumps.py)")
    w("— não editar à mão.** Evidência em [`fase-3.tsv`](fase-3.tsv).")
    w()
    w("Produto da [WTE-TASK-20](../../docs/tasks/concluidos/20-round-trip-headless.md). É")
    w("o primeiro momento em que o projeto afirma algo **verificado** sobre")
    w("dados, e não sobre forma.")
    w()
    w("O irmão é [`fase-3-fechamento.md`](fase-3-fechamento.md), da")
    w("WTE-TASK-21: aqui se mede se **os valores batem**; lá, **quem escreveu**")
    w("**o código que os produz** e **quem o consome**. Dois arquivos porque")
    w("são dois geradores — o mesmo arquivo escrito por dois seria duplicação")
    w("sem guarda.")
    w()
    w("## O oráculo aqui é o de formato")
    w()
    w("Não é o `wte.exe` — ele é o oráculo de **comportamento**, e a pergunta")
    w("desta task é de **formato**. Ele é dirigível desde a")
    w("[CORR-WTE-044](../../docs/tasks/concluidos/CORR-WTE-044.md), com")
    w("`roms/japanese-shift-jis.bin`, e mesmo assim não sabe dizer o que os")
    w("bytes significam: mostra o que o editor **faz**, não o que o campo **é**")
    w("([`crash-causa.md`](crash-causa.md) explica por que a ROM é essa).")
    w()
    w("O oráculo daqui é o **`we2002_core`** deste repositório, cujo")
    w("`Load`/`Save` já é byte-idêntico ao `ed.exe` nas duas ROMs. A pergunta")
    w("que ele responde é *o que significam estes bytes*, e é exatamente a")
    w("desta task.")
    w()
    w("**O par é bilíngue de propósito:** o `fpc` lê o Pascal gerado, o `g++`")
    w("lê o C++ original. Dois dumpers na mesma linguagem esconderiam erro de")
    w("leitura de literal — ele apareceria idêntico dos dois lados. É a mesma")
    w("razão dos dois `test_offsets.*` da WTE-TASK-16.")
    w()
    w("## Leitura: `diff` dos dois dumps")
    w()
    w("| ROM | o que valida | linhas | divergências |")
    w("|---|---|---:|---:|")
    for r in linhas:
        w(f"| `{r['arquivo']}` | {r['o_que_valida']} | {r['linhas_dump']} "
          f"| **{r['divergencias_dump']}** |")
    w()
    total = sum(int(r["divergencias_dump"]) for r in linhas)
    if total == 0:
        w("**Zero divergência nas duas ROMs.** O critério aqui não admite")
        w("faixa conhecida, diferente do golden test de imagem do `newWe2002`:")
        w("isto é leitura pura, não há comportamento indefinido para")
        w("preservar, e qualquer byte diferente seria defeito do transpilador.")
    else:
        w(f"**{total} divergência(s).** A fase 3 não fecha assim.")
    w()
    w("O formato do dump é `chave = valor`, uma por linha, com vetor de bytes")
    w("em `<n>:<hex>` cortado no último byte não-zero — forma sem perda, já")
    w("que o resto é zero por definição, e que não gasta 500 caracteres por")
    w("URL vazia.")
    w()
    w("### As duas medidas de cobertura")
    w()
    w("Dump igual dos dois lados não prova nada se o dado for todo zero. Por")
    w("isso o TSV conta, por ROM, quanto do dado exercitado é não-trivial:")
    w()
    w("| ROM | `raw_kanji_name` com byte ≥ `0x80` | `kanji_name` decodificado "
      "não-vazio | `squad_numbers` não zerados |")
    w("|---|---:|---:|---:|")
    for r in linhas:
        w(f"| `{r['rom']}` | {r['kanji_duplo']} | {r['kanji_decodificado']} "
          f"| {r['squad_numbers_nao_zero']} |")
    w()
    w("A primeira coluna conta o campo **cru** com pelo menos um byte alto,")
    w("que é o que caracteriza Shift-JIS de dois bytes; a segunda conta a")
    w("saída do `KanjiToAscii` que não é vazia nem só espaço. As duas, e não")
    w("uma: contar simplesmente \"campo não vazio\" dava 97 nas duas ROMs por")
    w("coincidência — os 97 registros existem em ambas — e não separava")
    w("release nenhuma.")
    w()
    w("O **bitfield de `SquadNumbers`** é o caso que mais precisa disso. O")
    w("Pascal não tem o bitfield do C++: tem um layout escrito à mão")
    w("([`tipos.md`](tipos.md), decisão 2), quatro palavras de 32 bits com")
    w("campos de 5 bits alocados do bit menos significativo para cima. O dump")
    w("emite as **duas** formas — os 23 números desempacotados e as quatro")
    w("palavras cruas —, então um erro de deslocamento não tem por onde")
    w("passar despercebido.")
    w()
    w("### O codec: a premissa da task estava trocada")
    w()
    eu = next((r for r in linhas if r["rom"] == "european-deluxe"), None)
    jp = next((r for r in linhas if r["rom"] == "japanese"), None)
    if eu and jp:
        w("O enunciado da WTE-TASK-20 diz que a ROM japonesa é *o único teste")
        w("real do codec de texto*. **Medido, é o contrário.**")
        w()
        w(f"As duas ROMs têm {eu['kanji_duplo']} campos crus com byte alto, e")
        w("o que sai do `KanjiToAscii` é oposto: "
          f"**{eu['kanji_decodificado']} de {eu['kanji_duplo']}**")
        w("decodificam para texto na European Deluxe, contra "
          f"**{jp['kanji_decodificado']} de {jp['kanji_duplo']}**")
        w("na japonesa.")
        w()
        w("A razão está no próprio codec, portado verbatim de")
        w("`edDlg.cpp:732-809`: ele só conhece o byte de chefe **130**")
        w("(`0x82` — latino de largura dupla e dígitos) e **129** (`0x81`, o")
        w("ponto). Tudo o mais cai no ramo padrão e vira espaço.")
        w()
        w("- a European Deluxe guarda `82 68 82 8e ...` → `Inter`, `Juventu`;")
        w("- a japonesa guarda `83 41 83 43 ...`, que é **katakana** — e vira")
        w("  espaço.")
        w()
        w("Ou seja: quem exercita os ramos de mapeamento é a **europeia**; a")
        w("japonesa exercita o **ramo padrão**. As duas são necessárias, por")
        w("motivos trocados em relação ao que a task supunha, e nenhuma das")
        w("duas sozinha cobre o codec. Isso não é defeito do port: os dois")
        w("lados concordam byte a byte, e o `ed.exe` mostra os mesmos espaços.")
        w()
    w("## Gravação: round-trip byte a byte")
    w()
    w("| ROM | Pascal × C++ | Load+Save × original |")
    w("|---|---:|---|")
    for r in linhas:
        w(f"| `{r['rom']}` | **{r['divergencias_rt_pascal_vs_cpp']}** bytes "
          f"| {r['bytes_rt_vs_original']} bytes em "
          f"{r['faixas_rt_vs_original']} faixa(s) |")
    w()
    rt = sum(int(r["divergencias_rt_pascal_vs_cpp"]) for r in linhas)
    if rt == 0:
        w("**As duas gravações são byte a byte idênticas.**")
    else:
        w(f"**{rt} byte(s) de divergência.** A fase 3 não fecha assim.")
    w()
    w("A segunda coluna **não é defeito, e é a ressalva que a task manda")
    w("registrar**: `Load`+`Save` sem editar nada não devolve a imagem")
    w("intacta, e não deveria. O `Save` reconstrói as squads all-star a partir")
    w("dos links (`OFS_PLAYER_ATTR_8`), e o original troca os dois primeiros")
    w("cobradores de cada clube de ML — o `Load` lê o par trocado e o `Save`")
    w("grava na ordem declarada. O `ed.exe` faz o mesmo; gravar duas vezes")
    w("volta ao início. O que esta linha mede é que os **dois lados fazem")
    w("isso igual**.")
    w()
    w("| ROM | sidecar `_url.txt` | igual dos dois lados |")
    w("|---|---:|:---:|")
    for r in linhas:
        w(f"| `{r['rom']}` | {r['sidecar_bytes']} B | {r['sidecar_igual']} |")
    w()
    w("O sidecar entra porque o `Save` o escreve — herdado do `OnWriteCD`")
    w("original — e porque ele é a decisão 5 do [`tipos.md`](tipos.md): 1.911")
    w("linhas terminadas em `#10`, sem `#13` e sem BOM. Um `\\r\\n` de um dos")
    w("lados apareceria aqui.")
    w()
    w("## O que isto não mede")
    w()
    w("- **As faixas que nenhum `OFS_*` explica.** Não são os `OFS_*` da")
    w("  [WTE-TASK-19](../../docs/tasks/concluidos/19-os-50-offsets-restantes.md) — esses")
    w("  moram todos no `Offsets.hpp`, têm lado C++ e estão dentro deste diff.")
    w("  São as regiões que o `wte.exe` endereça e que este repositório nunca")
    w("  nomeou, a maior delas a do uniforme. Sem lado C++, nenhum diff")
    w("  Pascal × C++ as alcança; nomeá-las é fase 4 e 5.")
    w("- **Comportamento.** Isto é a camada de dados, não os 96 handlers. O")
    w("  gate deles é a WTE-TASK-22, e o oráculo em que ele se apoia é")
    w("  dirigível desde a CORR-WTE-044, com a ROM japonesa.")
    w("- **O `Load` do sidecar.** Nenhum dos dois lados lê `_url.txt` no")
    w("  `Load` — isso é do app —, então `players[].url` sai zerado dos dois e")
    w("  o dump concorda por vacuidade nesse campo.")
    w()
    w("## Refazer")
    w()
    w("```sh")
    w("python3 wte/tools/compare_dumps.py --medir   # ~1,9 GB de cópia")
    w("python3 wte/tools/compare_dumps.py --check   # confere este arquivo")
    w("```")
    w()
    w("A medição **não** roda no `make -C wte check`: são quatro cópias de")
    w("~474 MB e uns dois minutos. O `--check` confere o texto contra o TSV,")
    w("que é o que o resto da bateria faz. Para reexecutar de dentro da")
    w("bateria: `WTE_ROUNDTRIP=1 make -C wte test`.")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--medir", action="store_true",
                    help="compila os dois lados e mede as duas ROMs")
    ap.add_argument("--tmp", type=Path, help="onde compilar (padrao: temporario)")
    ap.add_argument("--check", action="store_true",
                    help="nao escreve; sai 2 se a saida divergir do commitado")
    args = ap.parse_args(argv)

    try:
        if args.medir:
            import tempfile
            if args.tmp:
                args.tmp.mkdir(parents=True, exist_ok=True)
                return medir(args.tmp)
            with tempfile.TemporaryDirectory() as d:
                return medir(Path(d))
        texto = gerar()
    except CompareError as e:
        print(f"compare_dumps: ERRO: {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"compare_dumps: ERRO ao compilar:\n{e.stderr}", file=sys.stderr)
        return 1

    rel = OUT_MD.relative_to(ROOT)
    if args.check:
        if not OUT_MD.exists() or OUT_MD.read_text(encoding="utf-8") != texto:
            print(f"compare_dumps: {rel}: DIVERGE do gerador", file=sys.stderr)
            return 2
        print(f"compare_dumps: {rel}: ok")
        return 0
    OUT_MD.write_text(texto, encoding="utf-8")
    print(f"compare_dumps: {rel}: {len(texto)} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
