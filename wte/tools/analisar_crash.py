#!/usr/bin/env python3
"""Localiza o travamento do `wte.exe` a partir do log de excecao do Wine.

Produto da WTE-TASK-19. Responde uma pergunta que o `analisar_io.py` nao
alcanca: **onde**, no codigo, o editor morre ao trocar de time.

O `analisar_io.py` mede I/O -- que regioes da imagem o editor le e grava. Isso
disse que a ultima leitura antes do `SIGSEGV` e em 14368636 e que ali esta
release esta praticamente zerada, e essa correlacao virou hipotese de causa.
**Correlacao nao e causa**, e esta ferramenta e a que separa as duas: o Wine
sabe exatamente qual instrucao faltou, e sabe em que endereco cada modulo foi
carregado. Com os dois, o endereco de falha vira nome de funcao.

Duas modos, como o `analisar_io.py`:

**Medicao** (`--log wine.log --sessao NOME`) -- le o log de uma corrida feita com
`WINEDEBUG=+seh,+loaddll` e acrescenta a evidencia versionada:

    WINEDEBUG=+seh,+loaddll bash wte/tools/diff_dirigido.sh <roteiro> --saida DIR
    python3 wte/tools/analisar_crash.py --log DIR/wine.log \\
        --sessao com-time --roteiro 06-diff-dirigido.txt --seleciona-time sim

**Geracao** (sem argumento, ou `--check`) -- le a evidencia versionada mais o
`we-team-editor.exe` e o `vcl60.bpl`, resolve o endereco de falha contra a
tabela de exportacao do modulo, acha os sitios de chamada no `.exe` e escreve
`wte/re/crash.md`:

    python3 wte/tools/analisar_crash.py
    python3 wte/tools/analisar_crash.py --check

O `.exe` e os dois `.bpl` **nao sao versionados** (binario de terceiro sem
licenca -- secao 2 do plano). Sem eles a geracao falha dizendo isso, como a do
`dump_offsets.py`.
"""

from __future__ import annotations

import argparse
import csv
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RE_DIR = ROOT / "wte" / "re"
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
BPL = ROOT / "we-team-editor"
PUBLICADOS = RE_DIR / "published_methods.tsv"

TSV_SESSOES = RE_DIR / "crash-sessoes.tsv"
TSV_SEH = RE_DIR / "crash-seh.tsv"
TSV_MODULOS = RE_DIR / "crash-modulos.tsv"
OUT_MD = RE_DIR / "crash.md"

REL_EXE = "we-team-editor/we-team-editor.exe"

COLS_SESSOES = ["sessao", "roteiro", "seleciona_time", "excecoes"]
COLS_SEH = ["sessao", "ordem", "code", "addr", "info0", "info1",
            "eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp"]
COLS_MODULOS = ["sessao", "modulo", "base", "tipo"]


class CrashError(Exception):
    pass


# ------------------------------------------------------------------- PE ----
#
# Um leitor de PE32 minimo, e deliberadamente separado do `dump_offsets.py`:
# aquele resolve realocacao e a tabela de offsets do autor; este so precisa de
# secoes, exportacao e importacao. Fundir os dois acoplaria duas tasks.


class Pe:
    def __init__(self, dados: bytes, nome: str) -> None:
        self.d = dados
        self.nome = nome
        if dados[:2] != b"MZ":
            raise CrashError(f"{nome}: nao comeca com 'MZ'")
        pe = struct.unpack_from("<I", dados, 0x3C)[0]
        if dados[pe:pe + 4] != b"PE\0\0":
            raise CrashError(f"{nome}: assinatura PE ausente em {pe:#x}")
        self.opt = pe + 0x18
        self.base = struct.unpack_from("<I", dados, pe + 0x34)[0]
        nsec = struct.unpack_from("<H", dados, pe + 6)[0]
        off = self.opt + struct.unpack_from("<H", dados, pe + 0x14)[0]
        self.secoes = []
        for i in range(nsec):
            s = dados[off + i * 40:off + i * 40 + 40]
            nome_s = s[:8].rstrip(b"\0").decode("latin-1")
            vs, va, rs, ra = struct.unpack_from("<IIII", s, 8)
            self.secoes.append((nome_s, va, vs, ra, rs))

    def rva_para_offset(self, rva: int) -> int | None:
        for _, va, vs, ra, rs in self.secoes:
            # `rs` e o tamanho no arquivo e `vs` o tamanho em memoria. A cauda
            # de .data e maior em memoria (BSS zerado); endereco que cai la nao
            # tem byte no arquivo, e devolver ra+delta leria lixo de outra
            # secao. Por isso o corte e por `rs`.
            if va <= rva < va + rs:
                return ra + (rva - va)
        return None

    def secao_de(self, rva: int) -> str | None:
        for nome, va, vs, ra, rs in self.secoes:
            if va <= rva < va + max(vs, rs):
                return nome
        return None

    def bytes_da_secao(self, nome: str) -> tuple[int, bytes]:
        for n, va, vs, ra, rs in self.secoes:
            if n == nome:
                return va, self.d[ra:ra + max(vs, rs)]
        raise CrashError(f"{self.nome}: secao {nome} ausente")

    def exportacoes(self) -> list[tuple[int, str]]:
        rva = struct.unpack_from("<I", self.d, self.opt + 0x60)[0]
        o = self.rva_para_offset(rva)
        if o is None:
            return []
        nfun, nnam = struct.unpack_from("<II", self.d, o + 0x14)
        afun, anam, aord = struct.unpack_from("<III", self.d, o + 0x1C)
        pf = self.rva_para_offset(afun)
        pn = self.rva_para_offset(anam)
        po = self.rva_para_offset(aord)
        nomes: dict[int, str] = {}
        for i in range(nnam):
            nr = struct.unpack_from("<I", self.d, pn + 4 * i)[0]
            oo = struct.unpack_from("<H", self.d, po + 2 * i)[0]
            p = self.rva_para_offset(nr)
            nomes[oo] = self.d[p:self.d.index(b"\0", p)].decode("latin-1")
        saida = []
        for i in range(nfun):
            f = struct.unpack_from("<I", self.d, pf + 4 * i)[0]
            if f:
                saida.append((f, nomes.get(i, f"<ordinal {i}>")))
        return sorted(saida)

    def importacoes(self) -> dict[int, tuple[str, str]]:
        """VA da entrada da IAT -> (dll, simbolo)."""
        rva = struct.unpack_from("<I", self.d, self.opt + 0x68)[0]
        o = self.rva_para_offset(rva)
        saida: dict[int, tuple[str, str]] = {}
        while o is not None:
            olt, _ts, _fc, nrva, fthunk = struct.unpack_from("<IIIII", self.d, o)
            if not nrva:
                break
            p = self.rva_para_offset(nrva)
            dll = self.d[p:self.d.index(b"\0", p)].decode("latin-1")
            t = self.rva_para_offset(olt or fthunk)
            k = 0
            while True:
                v = struct.unpack_from("<I", self.d, t + 4 * k)[0]
                if not v:
                    break
                if not v & 0x80000000:
                    q = self.rva_para_offset(v)
                    nome = self.d[q + 2:self.d.index(b"\0", q + 2)]
                    saida[self.base + fthunk + 4 * k] = (
                        dll, nome.decode("latin-1"))
                k += 1
            o += 20
        return saida

    def texto_em(self, va: int, limite: int = 64) -> str | None:
        o = self.rva_para_offset(va - self.base)
        if o is None:
            return None
        fim = self.d.find(b"\0", o, o + limite)
        if fim < 0:
            return None
        bruto = self.d[o:fim]
        if len(bruto) < 3 or not all(0x20 <= c < 0x7F for c in bruto):
            return None
        return bruto.decode("latin-1")


def exportacao_que_contem(pe: Pe, rva: int) -> tuple[int, str] | None:
    anteriores = [e for e in pe.exportacoes() if e[0] <= rva]
    return anteriores[-1] if anteriores else None


# ------------------------------------------------------- leitura do log ----

RE_MODULO = re.compile(
    r'loaddll:build_module Loaded L"(.+?)" at ([0-9A-Fa-f]{8}): (\w+)')
RE_EXC = re.compile(
    r'seh:dispatch_exception code=([0-9a-f]+) flags=\S+ '
    r'addr=([0-9A-Fa-f]+) ip=')
RE_INFO = re.compile(r'seh:dispatch_exception\s+info\[(\d)\]=([0-9A-Fa-f]+)')
RE_REGS1 = re.compile(
    r'seh:dispatch_exception\s+eax=([0-9A-Fa-f]+) ebx=([0-9A-Fa-f]+) '
    r'ecx=([0-9A-Fa-f]+) edx=([0-9A-Fa-f]+) esi=([0-9A-Fa-f]+) '
    r'edi=([0-9A-Fa-f]+)')
RE_REGS2 = re.compile(
    r'seh:dispatch_exception\s+ebp=([0-9A-Fa-f]+) esp=([0-9A-Fa-f]+)')

CODE_ALVO = "c0000005"

# Quantas excecoes vao para o TSV. A contagem TOTAL fica em crash-sessoes.tsv;
# aqui entram so as primeiras, porque a falha e uma so e o resto e cascata --
# o manipulador de excecao do proprio app cai em seguida e reentra, e foram
# 309 registros na primeira medicao. Versionar 309 linhas identicas nao mede
# nada que a coluna `excecoes` ja nao meca.
MAX_SEH = 5


def ler_log(linhas) -> tuple[list[dict], list[dict]]:
    """Devolve (excecoes, modulos) de um wine.log com +seh e +loaddll.

    So `c0000005` (violacao de acesso) entra. As outras que o Wine dispara na
    subida -- `6ba` (RPC_S_SERVER_UNAVAILABLE) do `wineboot`, por exemplo --
    sao ruido de inicializacao e apareceriam em qualquer corrida.
    """
    excecoes: list[dict] = []
    modulos: list[dict] = []
    atual: dict | None = None
    vistos: set[tuple[str, str]] = set()
    for ln in linhas:
        m = RE_MODULO.search(ln)
        if m:
            caminho, base, tipo = m.groups()
            nome = caminho.replace("\\\\", "\\").split("\\")[-1]
            chave = (nome, base.lower())
            if tipo == "native" and chave not in vistos:
                vistos.add(chave)
                modulos.append({"modulo": nome, "base": f"0x{base.lower()}",
                                "tipo": tipo})
            continue
        m = RE_EXC.search(ln)
        if m:
            code, addr = m.groups()
            atual = ({"code": code, "addr": f"0x{addr.lower()}"}
                     if code == CODE_ALVO else None)
            if atual is not None:
                excecoes.append(atual)
            continue
        if atual is None:
            continue
        m = RE_INFO.search(ln)
        if m:
            atual[f"info{m.group(1)}"] = f"0x{m.group(2).lower()}"
            continue
        m = RE_REGS1.search(ln)
        if m:
            for nome, v in zip(("eax", "ebx", "ecx", "edx", "esi", "edi"),
                               m.groups()):
                atual[nome] = f"0x{v.lower()}"
            continue
        m = RE_REGS2.search(ln)
        if m:
            atual["ebp"] = f"0x{m.group(1).lower()}"
            atual["esp"] = f"0x{m.group(2).lower()}"
            atual = None
    return excecoes, modulos


def _ler_tsv(p: Path) -> list[dict[str, str]]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _grava_tsv(p: Path, cols: list[str], linhas: list[dict]) -> None:
    with p.open("w", encoding="utf-8", newline="") as f:
        # `lineterminator` explicito: o default do csv e CRLF, e o resto de
        # wte/re/ e LF. Sem isto o git normaliza na entrada e o arquivo
        # commitado deixa de ser byte a byte o que a ferramenta escreve.
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t",
                           lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for ln in linhas:
            w.writerow(ln)


def medir(log: Path, sessao: str, roteiro: str, seleciona: str) -> int:
    excecoes, modulos = ler_log(log.read_text(errors="replace").splitlines())
    total = len(excecoes)
    for i, e in enumerate(excecoes, 1):
        e["sessao"] = sessao
        e["ordem"] = str(i)
    excecoes = excecoes[:MAX_SEH]
    for m in modulos:
        m["sessao"] = sessao

    def substitui(p: Path, cols: list[str], novas: list[dict]) -> None:
        antigas = [r for r in _ler_tsv(p) if r.get("sessao") != sessao]
        _grava_tsv(p, cols, antigas + novas)

    substitui(TSV_SEH, COLS_SEH, excecoes)
    substitui(TSV_MODULOS, COLS_MODULOS, modulos)
    substitui(TSV_SESSOES, COLS_SESSOES, [{
        "sessao": sessao, "roteiro": roteiro,
        "seleciona_time": seleciona, "excecoes": str(total)}])
    print(f"analisar_crash: {sessao}: {total} excecao(oes) {CODE_ALVO} "
          f"({len(excecoes)} no TSV), {len(modulos)} modulo(s) nativo(s)")
    return 0


# -------------------------------------------------------------- analise ----


def _prologo(codigo: bytes, ini_va: int, alvo: int) -> int | None:
    """Inicio da rotina que contem `alvo`, pelo prologo `push ebp; mov ebp,esp`.

    Heuristica, e assumida como tal no texto gerado: e o prologo que o
    C++Builder 6 emite em toda funcao com quadro. Varre para tras a partir do
    sitio de chamada e para no primeiro que aparecer.
    """
    i = alvo - ini_va
    while i >= 2:
        if codigo[i:i + 3] == b"\x55\x8b\xec":
            return ini_va + i
        i -= 1
    return None


def _chamadas_para(codigo: bytes, ini_va: int, alvo: int) -> list[int]:
    saida = []
    for i in range(len(codigo) - 5):
        if codigo[i] == 0xE8:
            rel = struct.unpack_from("<i", codigo, i + 1)[0]
            if ini_va + i + 5 + rel == alvo:
                saida.append(ini_va + i)
    return saida


def _thunks_para(pe: Pe, iat: int) -> list[int]:
    """Enderecos de `jmp dword ptr [iat]`.

    O C++Builder nao chama a IAT direto: emite um `jmp [IAT]` por simbolo e
    chama esse thunk com `call rel32`. Procurar `call [IAT]` nao acha nada --
    ja custou uma busca vazia.
    """
    saida = []
    padrao = b"\xff\x25" + struct.pack("<I", iat)
    for nome, va, vs, ra, rs in pe.secoes:
        blob = pe.d[ra:ra + max(vs, rs)]
        pos = blob.find(padrao)
        while pos >= 0:
            saida.append(pe.base + va + pos)
            pos = blob.find(padrao, pos + 1)
    return saida


def _literais(pe: Pe, ini: int, fim: int) -> list[tuple[int, str]]:
    """`mov eax, imm32` na rotina, quando imm32 aponta para texto no arquivo."""
    va, codigo = pe.bytes_da_secao(".text")
    ini_va = pe.base + va
    saida = []
    for i in range(ini - ini_va, min(fim - ini_va, len(codigo) - 5)):
        if codigo[i] == 0xB8:
            imm = struct.unpack_from("<I", codigo, i + 1)[0]
            t = pe.texto_em(imm)
            if t:
                saida.append((imm, t))
    return saida


def ler_publicados() -> list[tuple[int, dict]]:
    if not PUBLICADOS.is_file():
        raise CrashError(f"{PUBLICADOS.relative_to(ROOT)} nao existe")
    linhas = _ler_tsv(PUBLICADOS)
    return sorted((int(x["endereco"], 16), x) for x in linhas)


def dono(publicados: list[tuple[int, dict]], va: int) -> tuple[int, dict] | None:
    anteriores = [p for p in publicados if p[0] <= va]
    return anteriores[-1] if anteriores else None


# --------------------------------------------------------------- gerar -----


def gerar() -> str:
    if not EXE.is_file():
        raise CrashError(
            f"{REL_EXE} nao existe.\n"
            "       A pasta we-team-editor/ nao e versionada (binario de "
            "terceiro sem\n"
            "       licenca -- ver a secao 2 do plano). Coloque-a na raiz do "
            "repositorio.")
    sessoes = _ler_tsv(TSV_SESSOES)
    seh = _ler_tsv(TSV_SEH)
    modulos = _ler_tsv(TSV_MODULOS)
    if not sessoes or not seh:
        raise CrashError("sem evidencia: rode com --log antes")

    exe = Pe(EXE.read_bytes(), REL_EXE)
    publicados = ler_publicados()

    # A primeira excecao da sessao que seleciona time e a que interessa. As
    # seguintes sao consequencia: o proprio manipulador de excecao do app cai
    # depois, e ip=0 nao localiza nada.
    com = [s for s in sessoes if s["seleciona_time"] == "sim"]
    if not com:
        raise CrashError("nenhuma sessao com selecao de time")
    sessao = com[0]["sessao"]
    falhas = [e for e in seh if e["sessao"] == sessao]
    if not falhas:
        raise CrashError(f"sessao {sessao} sem excecao registrada")
    primeira = falhas[0]
    addr = int(primeira["addr"], 16)

    mods = [m for m in modulos if m["sessao"] == sessao]
    alvo = None
    for m in sorted(mods, key=lambda x: int(x["base"], 16)):
        b = int(m["base"], 16)
        if b <= addr and (alvo is None or b > int(alvo["base"], 16)):
            alvo = m
    if alvo is None:
        raise CrashError(f"nenhum modulo nativo abaixo de {addr:#x}")
    caminho = BPL / alvo["modulo"]
    if not caminho.is_file():
        raise CrashError(f"we-team-editor/{alvo['modulo']} nao existe")
    mod = Pe(caminho.read_bytes(), alvo["modulo"])
    rva = addr - int(alvo["base"], 16)
    exp = exportacao_que_contem(mod, rva)
    if exp is None:
        raise CrashError(f"{alvo['modulo']}: nada exportado antes de {rva:#x}")
    exp_rva, exp_nome = exp

    # Do simbolo de volta para o `.exe`: IAT -> thunk -> sitios de chamada.
    iat = [va for va, (_d, n) in exe.importacoes().items() if n == exp_nome]
    sitios: list[int] = []
    va_txt, codigo = exe.bytes_da_secao(".text")
    ini_va = exe.base + va_txt
    for entrada in iat:
        for t in _thunks_para(exe, entrada):
            sitios += _chamadas_para(codigo, ini_va, t)
    sitios.sort()

    # O sitio que casa com o valor do parametro no momento da falha. O
    # C++Builder passa o 1o argumento em EDX (convencao __fastcall da Borland,
    # §8.1 do plano), entao `mov edx, imm` logo antes do `call` identifica qual
    # dos sitios disparou.
    edx = int(primeira.get("edx", "0x0"), 16)
    culpado = None
    for s in sitios:
        i = s - ini_va
        if codigo[i - 5] == 0xBA and \
                struct.unpack_from("<I", codigo, i - 4)[0] == edx:
            culpado = s
            break

    rotina = _prologo(codigo, ini_va, culpado or sitios[0])
    chamadores = _chamadas_para(codigo, ini_va, rotina) if rotina else []
    fim_rotina = min([s for s in sitios if s > (rotina or 0)] + [len(codigo)])
    lits = _literais(exe, rotina, rotina + 0x200) if rotina else []

    L: list[str] = []
    def w(s: str = "") -> None:
        L.append(s)

    w("# `re/crash.md` — onde o `wte.exe` morre ao trocar de time")
    w()
    w("**Gerado por [`wte/tools/analisar_crash.py`](../tools/analisar_crash.py)")
    w("— não editar à mão.** Evidência em [`crash-seh.tsv`](crash-seh.tsv),")
    w("[`crash-modulos.tsv`](crash-modulos.tsv) e")
    w("[`crash-sessoes.tsv`](crash-sessoes.tsv).")
    w()
    w("Produto da WTE-TASK-19. O [`offsets-novos.md`](offsets-novos.md) mede")
    w("**I/O** e chegou até *a última leitura antes do `SIGSEGV`*; daí a causa")
    w("não sai — leitura vizinha de uma falha é correlação. Este documento")
    w("pergunta ao Wine **qual instrução faltou**, e responde com nome de")
    w("função.")
    w()
    w("## O que separa as duas sessões")
    w()
    w("| sessão | roteiro | seleciona time? | violações de acesso |")
    w("|---|---|:---:|---:|")
    for s in sessoes:
        marca = "sim" if s["seleciona_time"] == "sim" else "não"
        w(f"| `{s['sessao']}` | `{s['roteiro']}` | {marca} "
          f"| {s['excecoes']} |")
    w()
    w("Os dois roteiros são **iguais linha a linha até a marca `ARRANQUE`**;")
    w("o segundo tem duas linhas a mais, que trocam o time pelo teclado. Mesmo")
    w("binário, mesma imagem, uma variável de diferença — e ela separa nenhuma")
    w("violação de acesso de todas elas. **A atribuição é medida, não inferida")
    w("do que aparece na tela** — e a tela, aqui, engana: a janela sobrevive ao")
    w("processo porque o `wineserver` a mantém mapeada.")
    w()
    w("## A exceção")
    w()
    w("| # | code | addr | info[1] (endereço que faltou) | eax | edx |")
    w("|---:|---|---|---|---|---|")
    for e in falhas:
        w(f"| {e['ordem']} | `{e['code']}` | `{e['addr']}` | "
          f"`{e.get('info1', '—')}` | `{e.get('eax', '—')}` | "
          f"`{e.get('edx', '—')}` |")
    w()
    w("A primeira é a que localiza. As seguintes falham no **endereço zero**")
    w("e não localizam nada: o manipulador de exceção do próprio app cai em")
    w("seguida e reentra — daí a contagem alta na tabela acima.")
    w()
    w("## Onde ela cai")
    w()
    w("| | |")
    w("|---|---|")
    w(f"| endereço da falha | `{primeira['addr']}` |")
    w(f"| módulo carregado ali | `{alvo['modulo']}` em `{alvo['base']}` |")
    w(f"| RVA no módulo | `{rva:#x}` |")
    w(f"| exportação que o contém | `{exp_nome}` (`{exp_rva:#x}`, "
      f"+{rva - exp_rva:#x}) |")
    w(f"| endereço que faltou | `{primeira.get('info1', '—')}` |")
    w()
    base_pref = f"{mod.base:#010x}"
    w(f"O `{alvo['modulo']}` prefere `{base_pref}` e foi **realocado** para")
    w(f"`{alvo['base']}`; sem a linha do `+loaddll` o endereço de falha não")
    w("cai em módulo nenhum e a pista morre ali. É por isso que a medição")
    w("pede `WINEDEBUG=+seh,+loaddll`, e não só `+seh`.")
    w()
    if primeira.get("eax") == "0x00000000":
        w("`eax` é zero e o endereço que faltou é o deslocamento de um campo")
        w("do objeto: o `this` chegou **nulo**. Não é ponteiro solto nem")
        w("índice fora de faixa — é um objeto que deveria existir e não")
        w("existe.")
        w()
    w("## Quem chama")
    w()
    w(f"O `.exe` importa `{exp_nome}` e a chama")
    w("por thunk (`jmp dword ptr [IAT]`), que é a forma do C++Builder —")
    w("procurar `call [IAT]` não acha nada. Sítios de chamada no `.text`:")
    w()
    w("| sítio | é o da falha? |")
    w("|---|:---:|")
    for s in sitios:
        w(f"| `{s:#010x}` | {'sim' if s == culpado else '—'} |")
    w()
    if culpado:
        w(f"O sítio é identificado pelo argumento: o C++Builder passa o")
        w(f"primeiro parâmetro em `EDX` (convenção Borland, §8.1 do plano), e")
        w(f"no instante da falha `EDX` valia `{primeira['edx']}` — o mesmo")
        w("imediato que só um dos sítios carrega.")
        w()
    if rotina:
        w(f"Os dois sítios estão dentro da mesma rotina privada, que começa em")
        w(f"`{rotina:#010x}` (prólogo `push ebp; mov ebp,esp`). Ela não é")
        w("publicada — não é manipulador de evento —, então não tem nome no")
        w("[`published_methods.tsv`](published_methods.tsv). Quem a chama, sim:")
        w()
        w("| chamada em | manipulador que a contém | formulário | deslocamento |")
        w("|---|---|---|---:|")
        for c in chamadores:
            d = dono(publicados, c)
            if d:
                a, x = d
                w(f"| `{c:#010x}` | `{x['handler']}` | `{x['formulario']}` "
                  f"| +{c - a:#x} |")
        w()
        if lits:
            w("Literais que a rotina referencia (`mov eax, imm32` apontando")
            w("para texto no arquivo):")
            w()
            for va_l, t in lits:
                w(f"- `{va_l:#010x}` → `{t!r}`")
            w()
    w("## O que isto muda")
    w()
    w("**A falha é de estado de interface, não de leitura da imagem.** A")
    w("cadeia medida vai do manipulador de troca de time até uma rotina que")
    w("procura um controle pelo nome e mexe na fonte dele; o que falta é o")
    w("objeto, não o byte.")
    w()
    w("**A causa foi medida depois, e está em [`crash-causa.md`]"
      "(crash-causa.md)** (CORR-WTE-044). O resumo, porque ele aposenta duas")
    w("frases que este documento carregou até 2026-08-10:")
    w()
    w("- **o controle existe.** Os 23 `dorsalN` estão vivos no `MainForm`,")
    w("  todos `TStaticText`, todos com `Font` não nula. Quem não presta é o")
    w("  ponteiro guardado em `0x004335e4`, que a carga do time sobrescreve")
    w("  com dado de uma tabela vizinha (`0x00010001`) — valor que passa no")
    w("  `if (obj != nil)` da rotina e cujo `+0x68` lê zero;")
    w("- **a região vazia em `14368636` não é a causa, nem a causa da")
    w("  causa.** As duas imagens leem essa mesma faixa ao trocar de time, e")
    w("  só uma delas trava. O [`offsets-novos.md`](offsets-novos.md)")
    w("  continua medindo um fato; ele só não explica este.")
    w()
    w("E **desbloqueia** a WTE-TASK-19, com ressalva: o oráculo é dirigível")
    w("com `roms/japanese-shift-jis.bin` — mesmo roteiro, zero violações de")
    w("acesso —, e não com a `golden-european-deluxe.bin`. As três ressalvas")
    w("que acompanham o contorno estão no `crash-causa.md`.")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", type=Path, help="wine.log com +seh,+loaddll")
    ap.add_argument("--sessao", help="nome da sessao no TSV de evidencia")
    ap.add_argument("--roteiro", default="?")
    ap.add_argument("--seleciona-time", choices=("sim", "nao"), default="sim")
    ap.add_argument("--check", action="store_true",
                    help="nao escreve; sai 2 se a saida divergir do commitado")
    args = ap.parse_args(argv)

    try:
        if args.log:
            if not args.sessao:
                ap.error("--log exige --sessao")
            return medir(args.log, args.sessao, args.roteiro,
                         args.seleciona_time)
        texto = gerar()
    except CrashError as e:
        print(f"analisar_crash: ERRO: {e}", file=sys.stderr)
        return 1

    rel = OUT_MD.relative_to(ROOT)
    if args.check:
        if not OUT_MD.exists() or OUT_MD.read_text(encoding="utf-8") != texto:
            print(f"analisar_crash: {rel}: DIVERGE do gerador", file=sys.stderr)
            return 2
        print(f"analisar_crash: {rel}: ok")
        return 0
    OUT_MD.write_text(texto, encoding="utf-8")
    print(f"analisar_crash: {rel}: {len(texto)} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
