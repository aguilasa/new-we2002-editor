#!/usr/bin/env python3
"""Le, do `wte.exe` VIVO, o ponteiro global que a rotina de realce usa.

Produto da CORR-WTE-044. O `analisar_crash.py` chega ate *qual instrucao
faltou* -- `Graphics::TFont::SetSize` com `this` nulo, chamada de
`0x0040b1ac`. Dali nao sai a causa: saber que o objeto e nulo nao diz **por
que**, e a diferenca entre "o controle nao existe" e "o ponteiro foi
sobrescrito" muda o desfecho inteiro. Esta ferramenta le a memoria do processo
enquanto ele roda e separa as duas.

O que ela mede, por amostragem de 20 ms:

- o global `0x004335e4` -- o ponteiro do "controle realcado agora";
- `[global + 0x68]`, o `TControl.FFont` desse objeto;
- a classe do objeto, resolvida pelo VMT (`[obj]`, nome em `[vmt - 0x2c]`);
- o censo dos componentes do `MainForm` cujo nome comeca com `dorsal`;
- a vizinhanca de `.data` em volta do global, para separar escrita pontual de
  escrita em massa.

**ptrace_scope=1 nesta maquina.** So da para ler `/proc/<pid>/mem` de
descendente, entao esta ferramenta **lanca** o `diff_dirigido.sh` como filho em
vez de se anexar a um processo ja rodando. E a mesma razao pela qual o
`diff_dirigido.sh` lanca o `strace` em vez de anexar.

    python3 wte/tools/sonda_dorsal.py wte/tests/roteiros/08-so-troca-de-time.txt
    python3 wte/tools/sonda_dorsal.py <roteiro> --imagem roms/japanese-shift-jis.bin

`--check` **nao roda o Wine**: confere os quatro deslocamentos hardcoded acima
contra o codigo dos `.bpl`, decodificando os prologos que os usam. E o mesmo
contrato do `check_lcl_props.py` (CORR-WTE-020) -- numero que a ferramenta le
do disco, nao numero de memoria. Sem os `.bpl` presentes ele avisa e sai 0,
como o `dfm_extract.py` faz com os blobs (CORR-WTE-004): a pasta
`we-team-editor/` e do usuario e nao e versionada.
"""

from __future__ import annotations

import argparse
import os
import struct
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXE_DIR = ROOT / "we-team-editor"
VCL = EXE_DIR / "vcl60.bpl"
RTL = EXE_DIR / "rtl60.bpl"

# Os dois globais do `.exe`, que carrega na base preferida 0x00400000.
GLOBAL = 0x004335E4   # o "controle realcado agora" -- lido em 0x0040b19e
MAINFORM = 0x00434360  # a instancia do TMainForm -- lida em 0x0040b235

# A vizinhanca despejada por --vizinhanca. Cobre a tabela que a troca de time
# preenche (0x00433580..0x004335bf), o contador (0x004335c0) e o global.
VIZ_INI = 0x00433580
VIZ_TAM = 0xC0

# Deslocamentos de campo, todos conferidos por --check contra os .bpl.
OFF_FFONT = 0x68        # TControl.FFont          -- vcl60 TControl::SetFont
OFF_FNAME = 0x08        # TComponent.FName        -- rtl60 TComponent::FindComponent
OFF_FCOMPONENTS = 0x10  # TComponent.FComponents  -- idem
OFF_TLIST_ITEMS = 0x04  # TList.FList             -- rtl60 TList::Get
OFF_TLIST_COUNT = 0x08  # TList.FCount            -- rtl60 TComponent::GetComponentCount
OFF_VMT_NOME = 0x2C     # vmtClassName, em vmt - 0x2c


class SondaError(Exception):
    pass


# --------------------------------------------------------------- --check ----

def _pe(caminho: Path):
    """Reusa o leitor de PE do analisar_crash.py -- um so na arvore."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import analisar_crash as ac
    return ac.Pe(caminho.read_bytes(), caminho.name)


def _exportacao(pe, nome_parcial: str) -> int:
    for rva, nome in pe.exportacoes():
        if nome_parcial in nome:
            return rva
    raise SondaError(f"exportacao com '{nome_parcial}' nao existe")


def _bytes_do_rva(caminho: Path, pe, rva: int, n: int) -> bytes:
    off = pe.rva_para_offset(rva)
    if off is None:
        raise SondaError(f"RVA {rva:#x} fora do arquivo")
    return caminho.read_bytes()[off:off + n]


def _desloc_mod_rm_8(codigo: bytes, opcode: int) -> list[int]:
    """Deslocamentos de 1 byte em `mov reg,[reg+disp8]` (0x8b, mod=01).

    Decodificador minimo de proposito unico: nao e um desmontador. Ele existe
    para que os quatro numeros acima venham do disco, e nao da memoria de quem
    escreveu o documento.
    """
    saida = []
    i = 0
    while i < len(codigo) - 2:
        if codigo[i] == opcode and (codigo[i + 1] >> 6) == 0b01:
            saida.append(codigo[i + 2])
            i += 3
            continue
        i += 1
    return saida


def conferir_layout() -> int:
    faltando = [p.name for p in (VCL, RTL) if not p.exists()]
    if faltando:
        print(f"sonda_dorsal: {', '.join(faltando)} ausente(s) -- "
              "we-team-editor/ e do usuario e nao e versionada; "
              "conferencia de layout pulada")
        return 0

    pe_v, pe_r = _pe(VCL), _pe(RTL)
    esperado = [
        (VCL, pe_v, "@Controls@TControl@SetFont", 0x10, OFF_FFONT,
         "TControl.FFont"),
        (RTL, pe_r, "@Classes@TComponent@FindComponent", 0x30, OFF_FCOMPONENTS,
         "TComponent.FComponents"),
        (RTL, pe_r, "@Classes@TComponent@FindComponent", 0x30, OFF_FNAME,
         "TComponent.FName"),
        (RTL, pe_r, "@Classes@TComponent@GetComponentCount", 0x10,
         OFF_TLIST_COUNT, "TList.FCount"),
        (RTL, pe_r, "@Classes@TList@Get$", 0x28, OFF_TLIST_ITEMS,
         "TList.FList"),
    ]
    ruim = 0
    for caminho, pe, simbolo, tam, desloc, rotulo in esperado:
        rva = _exportacao(pe, simbolo)
        codigo = _bytes_do_rva(caminho, pe, rva, tam)
        vistos = _desloc_mod_rm_8(codigo, 0x8B)
        if desloc in vistos:
            print(f"sonda_dorsal: {rotulo} = {desloc:#04x}: ok "
                  f"({caminho.name} {simbolo} RVA {rva:#x})")
        else:
            ruim += 1
            print(f"sonda_dorsal: {rotulo} = {desloc:#04x}: DIVERGE -- "
                  f"{caminho.name} {simbolo} usa "
                  f"{[hex(v) for v in vistos]}", file=sys.stderr)
    return 2 if ruim else 0


# ---------------------------------------------------------------- medicao ----

def acha_pid() -> int | None:
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / "cmdline").read_bytes()
        except OSError:
            continue
        if b"we-team-editor.exe" in cmd and b"strace" not in cmd:
            return int(p.name)
    return None


class Mem:
    def __init__(self, pid: int) -> None:
        self.f = open(f"/proc/{pid}/mem", "rb", 0)

    def ler(self, addr: int, n: int) -> bytes | None:
        try:
            self.f.seek(addr)
            return self.f.read(n)
        except OSError:
            return None

    def dw(self, addr: int) -> int | None:
        b = self.ler(addr, 4)
        return None if not b or len(b) < 4 else struct.unpack("<I", b)[0]

    def ansistr(self, p: int | None) -> str:
        if not p:
            return ""
        n = self.dw(p - 4)
        if n is None or not 0 <= n < 256:
            return "?"
        b = self.ler(p, n)
        return "" if b is None else b.decode("latin-1", "replace")

    def classe(self, obj: int | None) -> str | None:
        vmt = self.dw(obj) if obj else None
        if not vmt:
            return None
        p = self.dw(vmt - OFF_VMT_NOME)
        if not p:
            return None
        b = self.ler(p, 64)
        return None if b is None else b[1:1 + b[0]].decode("latin-1", "replace")


def censo_dorsais(mem: Mem, form: int):
    lista = mem.dw(form + OFF_FCOMPONENTS)
    if not lista:
        return 0, []
    n = mem.dw(lista + OFF_TLIST_COUNT) or 0
    arr = mem.dw(lista + OFF_TLIST_ITEMS)
    if not arr:
        return n, []
    saida = []
    for i in range(min(n, 4000)):
        c = mem.dw(arr + 4 * i)
        if not c:
            continue
        nome = mem.ansistr(mem.dw(c + OFF_FNAME))
        if nome.lower().startswith("dorsal"):
            saida.append((nome, c, mem.classe(c), mem.dw(c + OFF_FFONT)))
    return n, saida


def medir(roteiro: Path, saida: Path, imagem: Path | None,
          vizinhanca: bool) -> int:
    cmd = ["bash", str(ROOT / "wte/tools/diff_dirigido.sh"), str(roteiro),
           "--saida", str(saida)]
    if imagem:
        cmd += ["--imagem", str(imagem)]
    env = dict(os.environ, WINEDEBUG=os.environ.get("WINEDEBUG", "+seh"))
    proc = subprocess.Popen(cmd, cwd=ROOT, env=env,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)

    pid, t0 = None, time.time()
    while pid is None and time.time() - t0 < 180 and proc.poll() is None:
        pid = acha_pid()
        time.sleep(0.05)
    if pid is None:
        proc.wait()
        print("sonda_dorsal: nao achei o processo do wte.exe", file=sys.stderr)
        return 1
    print(f"sonda_dorsal: wte.exe = pid {pid}  (saida em {saida})", flush=True)

    mem = Mem(pid)
    log = saida / "wine.log"
    ultimo_global: object = object()
    ultimo_censo: object = object()
    ultima_viz: bytes | None = None
    excecao_vista = False

    while proc.poll() is None:
        v = mem.dw(GLOBAL)
        if v is not None and v != ultimo_global:
            ultimo_global = v
            print(f"{time.time() - t0:7.2f}s  [{GLOBAL:#010x}]={v:#010x}"
                  f"  classe={mem.classe(v)}"
                  f"  [+{OFF_FFONT:#04x}]="
                  f"{mem.dw(v + OFF_FFONT) if v else None}", flush=True)

        form = mem.dw(MAINFORM)
        if form:
            n, ds = censo_dorsais(mem, form)
            chave = (n, len(ds), tuple(d[3] for d in ds))
            if chave != ultimo_censo:
                ultimo_censo = chave
                sem_font = [d[0] for d in ds if not d[3]]
                print(f"{time.time() - t0:7.2f}s  MainForm={form:#010x}"
                      f"  componentes={n}  dorsal*={len(ds)}"
                      f"  sem_Font={sem_font}", flush=True)

        if vizinhanca:
            bloco = mem.ler(VIZ_INI, VIZ_TAM)
            if bloco is not None and bloco != ultima_viz:
                velho, ultima_viz = ultima_viz, bloco
                print(f"{time.time() - t0:7.2f}s  .data mudou:", flush=True)
                for i in range(0, len(bloco), 4):
                    novo = struct.unpack_from("<I", bloco, i)[0]
                    ant = (struct.unpack_from("<I", velho, i)[0]
                           if velho else None)
                    if velho is None or novo != ant:
                        a = VIZ_INI + i
                        marca = "  <== o global" if a == GLOBAL else ""
                        print(f"    {a:#010x}  "
                              f"{'-' if ant is None else hex(ant)} -> "
                              f"{novo:#010x}{marca}", flush=True)

        if not excecao_vista and log.exists():
            try:
                if b"code=c0000005" in log.read_bytes()[:8_000_000]:
                    excecao_vista = True
                    print(f"{time.time() - t0:7.2f}s  <<< primeira c0000005 "
                          "no wine.log", flush=True)
            except OSError:
                pass
        time.sleep(0.02)

    proc.wait()
    if log.exists():
        n = log.read_bytes().count(b"code=c0000005")
        print(f"sonda_dorsal: {n} violacao(oes) de acesso no wine.log")
        print("sonda_dorsal: a CONTAGEM nao e propriedade do defeito -- o "
              "manipulador do app reentra em laco, entao ela mede quanto "
              "tempo o processo ficou vivo. O que separa as sessoes e zero "
              "contra nao-zero.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("roteiro", nargs="?", type=Path,
                    help="roteiro de wte/tests/roteiros/")
    ap.add_argument("--imagem", type=Path,
                    help="imagem a medir (padrao: a do diff_dirigido.sh)")
    ap.add_argument("--saida", type=Path,
                    default=Path("/tmp/sonda-dorsal"),
                    help="diretorio da corrida")
    ap.add_argument("--vizinhanca", action="store_true",
                    help="despeja tambem a vizinhanca de .data do global")
    ap.add_argument("--check", action="store_true",
                    help="nao roda o Wine; confere os deslocamentos nos .bpl")
    args = ap.parse_args(argv)

    try:
        if args.check or args.roteiro is None:
            return conferir_layout()
        args.saida.mkdir(parents=True, exist_ok=True)
        return medir(args.roteiro, args.saida, args.imagem, args.vizinhanca)
    except SondaError as e:
        print(f"sonda_dorsal: ERRO: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
