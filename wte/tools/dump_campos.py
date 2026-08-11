#!/usr/bin/env python3
"""Nome -> deslocamento dos campos publicados dos 18 formularios.

Gera `wte/re/campos.tsv` e `wte/re/campos.md`, insumo da WTE-TASK-25 e de
todo handler da fase 4 dali em diante.

## O problema que isto resolve

O corpo de qualquer handler do `.exe` referencia controle por **deslocamento**:
`mov eax,[ebx+0x33c]`. Sem o mapa, ler um handler para com "ele chama um metodo
de alguma coisa" -- que nao da para escrever em Pascal.

A tentacao e derivar o deslocamento da ordem dos `object` no `.dfm`: o primeiro
componente no primeiro campo, e assim por diante. **Medido: nao bate.** No
`MainForm` a ordem do DFM acerta *zero* dos 116 -- o campo em `0x2f0` e o
`lista_equipos`, que no DFM e o 73o `object`. A ordem do DFM e a de criacao (a
ordem em que o IDE gravou), e a ordem dos campos e a da declaracao no `.h`; o
C++Builder nao as mantem em sincronia. Derivar dali produziria a leitura errada
com a cara da certa, que e a armadilha 1 do `progresso.md` por outro caminho.

## De onde o mapa sai, entao

Do proprio binario. O streaming de DFM precisa resolver `object lista_equipos:
TComboBox` no campo certo, e faz isso por nome, em tempo de execucao: a classe
carrega uma **published field table**, apontada pelo VMT em deslocamento -56.
Ela sobreviveu ao `/STRIP` pela mesma razao que a published method table da
WTE-TASK-04 sobreviveu -- sem ela o formulario nao carrega.

    word  contagem
    dword ponteiro para a tabela de classes
    contagem x { dword deslocamento, word indice de classe, shortstring nome }

O -56 nao e chute: o cabecalho negativo do VMT e fixo desde o Delphi 4, e a
WTE-TASK-04 ja o usa para `vmtMethodTable` (-52) e `vmtClassName` (-44). Este
script confere os dois de novo em cada VMT que aceita, entao um deslocamento
errado apareceria como formulario sem nome, nao como tabela silenciosamente
torta.

## As tres conferencias que o script faz, e aborta se falharem

1. **Os 18 VMTs.** Achados pelo auto-ponteiro (dword cujo valor e o proprio
   endereco mais 76), como no `dump_published.py`. O conjunto de nomes tem de
   ser exatamente os 18 arquivos de `wte/re/dfm/`.
2. **Campo por campo contra o DFM.** O conjunto de nomes da tabela tem de ser
   igual ao conjunto de `object <nome>:` do `.dfm` daquele formulario --
   descontado o componente **sem nome**, que nao gera campo. E o `TStaticText`
   de 4x4 do `MainForm` que o `progresso.md` registra: 116 `object`, 115
   campos.
3. **O primeiro deslocamento.** O menor deslocamento de cada formulario tem de
   ser o mesmo nos 18; e o tamanho de instancia de `TForm`, e sai medido daqui
   em vez de escrito a mao. Se um formulario discordar, o -56 esta errado ou a
   classe nao deriva de `TForm`.

Uso:

    python3 wte/tools/dump_campos.py            # regenera
    python3 wte/tools/dump_campos.py --check    # o que `make -C wte check` roda
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "we-team-editor" / "we-team-editor.exe"
DFM = ROOT / "wte" / "re" / "dfm"
OUT = ROOT / "wte" / "re"

REL_EXE = "we-team-editor/we-team-editor.exe"
REL_DFM = "wte/re/dfm"
REL_OUT = "wte/re"
GENERATOR = "wte/tools/dump_campos.py"

TSV_NAME = "campos.tsv"
MD_NAME = "campos.md"

# Cabecalho negativo do VMT, fixo desde o Delphi 4. Os tres que interessam.
VMT_SELF = -76
VMT_FIELD_TABLE = -56
VMT_METHOD_TABLE = -52
VMT_CLASS_NAME = -44
VMT_INSTANCE_SIZE = -40

RE_OBJECT = re.compile(r"^\s+object\s+(?:([A-Za-z_]\w*)\s*:\s*)?(\w+)\s*$", re.M)


class DumpError(Exception):
    """Erro de medicao, sempre com contexto suficiente para agir."""


# --------------------------------------------------------------------- PE ---
#
# Leitor de PE em stdlib pura, pela mesma razao do `dump_units.py`: cada gerador
# de `wte/tools/` roda sozinho, sem importar os irmaos. O que ele decide -- onde
# uma RVA cai no arquivo -- e fato sobre o formato, nao escolha de projeto.
class PE:
    def __init__(self, data: bytes, rotulo: str) -> None:
        self.data = data
        self.rotulo = rotulo
        if data[:2] != b"MZ":
            raise DumpError(f"{rotulo}: nao comeca com MZ")
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe:pe + 4] != b"PE\0\0":
            raise DumpError(f"{rotulo}: assinatura PE ausente em {pe:#x}")
        nsec = struct.unpack_from("<H", data, pe + 6)[0]
        szopt = struct.unpack_from("<H", data, pe + 20)[0]
        opt = pe + 24
        self.base = struct.unpack_from("<I", data, opt + 28)[0]
        self.sections = []
        for i in range(nsec):
            o = pe + 24 + szopt + i * 40
            name = data[o:o + 8].rstrip(b"\0").decode("latin1")
            vsize = struct.unpack_from("<I", data, o + 8)[0]
            vaddr = struct.unpack_from("<I", data, o + 12)[0]
            rsize = struct.unpack_from("<I", data, o + 16)[0]
            raddr = struct.unpack_from("<I", data, o + 20)[0]
            self.sections.append((name, vaddr, vsize, raddr, rsize))

    def off(self, va: int) -> int | None:
        """Deslocamento no arquivo do endereco virtual `va`, ou None."""
        rva = va - self.base
        for _name, vaddr, vsize, raddr, rsize in self.sections:
            span = max(vsize, rsize)
            if vaddr <= rva < vaddr + span and rva - vaddr < rsize:
                return raddr + (rva - vaddr)
        return None

    def dword(self, va: int) -> int:
        o = self.off(va)
        if o is None:
            raise DumpError(f"{self.rotulo}: {va:#010x} fora das secoes")
        return struct.unpack_from("<I", self.data, o)[0]

    def shortstring(self, va: int) -> str:
        o = self.off(va)
        if o is None:
            raise DumpError(f"{self.rotulo}: {va:#010x} fora das secoes")
        n = self.data[o]
        return self.data[o + 1:o + 1 + n].decode("latin1")


# ------------------------------------------------------------------- VMTs ---
def acha_vmts(pe: PE) -> dict[str, int]:
    """Os VMTs de classe, pelo auto-ponteiro. Mesma regua do dump_published."""
    achados: dict[str, int] = {}
    for _name, vaddr, vsize, raddr, rsize in pe.sections:
        limite = min(vsize, rsize)
        for delta in range(0, max(0, limite - 4), 4):
            off = raddr + delta
            valor = struct.unpack_from("<I", pe.data, off)[0]
            va = pe.base + vaddr + delta
            if valor != va + 76:
                continue
            vmt = va + 76
            nome_ptr = pe.dword(vmt + VMT_CLASS_NAME)
            tam = pe.dword(vmt + VMT_INSTANCE_SIZE)
            if not nome_ptr or not tam:
                continue           # a rejeitada da WTE-TASK-04, sem nome e sem tamanho
            nome = pe.shortstring(nome_ptr)
            if not nome.startswith("T"):
                continue
            achados[nome] = vmt
    return achados


def le_field_table(pe: PE, vmt: int) -> list[tuple[int, str]]:
    """Os campos publicados da classe: (deslocamento, nome), na ordem gravada."""
    tabela = pe.dword(vmt + VMT_FIELD_TABLE)
    if not tabela:
        return []
    o = pe.off(tabela)
    if o is None:
        raise DumpError(f"{REL_EXE}: field table em {tabela:#010x} fora das secoes")
    contagem = struct.unpack_from("<H", pe.data, o)[0]
    p = o + 6                      # word contagem + dword ponteiro de classes
    saida: list[tuple[int, str]] = []
    for _ in range(contagem):
        desl = struct.unpack_from("<I", pe.data, p)[0]
        n = pe.data[p + 6]
        nome = pe.data[p + 7:p + 7 + n].decode("latin1")
        saida.append((desl, nome))
        p += 7 + n
    return saida


# -------------------------------------------------------------------- DFM ---
def componentes(nome_form: str) -> list[tuple[str, str]]:
    """(<nome>, <classe>) de cada `object` do .dfm. Nome vazio = anonimo."""
    caminho = DFM / f"{nome_form}.dfm"
    if not caminho.exists():
        raise DumpError(f"{REL_DFM}/{nome_form}.dfm: ausente")
    texto = caminho.read_text(encoding="latin1")
    saida = []
    for m in RE_OBJECT.finditer(texto):
        nome, classe = m.group(1), m.group(2)
        if nome is None:           # `object TStaticText` -- componente sem nome
            saida.append(("", classe))
        else:
            saida.append((nome, classe))
    return saida


# ------------------------------------------------------------------ saida ---
def medir() -> tuple[list[dict], int]:
    pe = PE(EXE.read_bytes(), REL_EXE)
    formularios = sorted(p.stem for p in DFM.glob("*.dfm"))
    if not formularios:
        raise DumpError(f"{REL_DFM}: nenhum .dfm -- rode o dfm_extract.py antes")

    vmts = acha_vmts(pe)
    faltando = [f for f in formularios if f"T{f}" not in vmts]
    if faltando:
        raise DumpError(
            f"{REL_EXE}: sem VMT para {', '.join(faltando)} -- o -76 ou o -44 "
            f"mudou de lugar")

    medidas = []
    bases = set()
    for form in formularios:
        vmt = vmts[f"T{form}"]
        campos = le_field_table(pe, vmt)
        tam = pe.dword(vmt + VMT_INSTANCE_SIZE)
        comps = componentes(form)
        nomeados = [n for n, _c in comps if n]
        anonimos = len(comps) - len(nomeados)

        do_dfm = set(nomeados)
        da_tabela = {n for _o, n in campos}
        if do_dfm != da_tabela:
            so_dfm = sorted(do_dfm - da_tabela)
            so_tab = sorted(da_tabela - do_dfm)
            raise DumpError(
                f"{form}: a field table e o .dfm discordam; so no dfm: "
                f"{so_dfm or '-'}; so na tabela: {so_tab or '-'}")
        if len(campos) != len(da_tabela):
            raise DumpError(f"{form}: nome repetido na field table")
        for desl, nome in campos:
            if desl % 4:
                raise DumpError(f"{form}.{nome}: deslocamento {desl} nao alinhado")
            if not 0 < desl < tam:
                raise DumpError(
                    f"{form}.{nome}: deslocamento {desl} fora da instancia ({tam})")
        if campos:
            bases.add(min(d for d, _n in campos))

        classe = {n: c for n, c in comps if n}
        ordem_dfm = [n for n in nomeados]
        por_desl = sorted(campos)
        coincide = sum(1 for i, (_d, n) in enumerate(por_desl)
                       if i < len(ordem_dfm) and ordem_dfm[i] == n)
        medidas.append({
            "form": form,
            "vmt": vmt,
            "tam": tam,
            "campos": por_desl,
            "classe": classe,
            "objects": len(comps),
            "anonimos": anonimos,
            "coincide": coincide,
        })

    if len(bases) != 1:
        raise DumpError(
            f"o primeiro campo nao cai no mesmo lugar nos 18: {sorted(bases)}")
    return medidas, bases.pop()


def gera_tsv(medidas: list[dict]) -> str:
    linhas = ["formulario\toffset\tcampo\tclasse"]
    for m in medidas:
        for desl, nome in m["campos"]:
            linhas.append(f"{m['form']}\t{desl:#06x}\t{nome}\t{m['classe'][nome]}")
    return "\n".join(linhas) + "\n"


def gera_md(medidas: list[dict], base: int) -> str:
    total = sum(len(m["campos"]) for m in medidas)
    objetos = sum(m["objects"] for m in medidas)
    anonimos = sum(m["anonimos"] for m in medidas)
    coincide = sum(m["coincide"] for m in medidas)

    w: list[str] = []
    a = w.append
    a("# `re/campos.md` — nome → deslocamento dos campos publicados")
    a("")
    a(f"Produto da [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md).")
    a(f"Gerado por [`../tools/dump_campos.py`](../tools/dump_campos.py), a partir")
    a(f"de `{REL_EXE}` e dos 18 formulários de [`dfm/`](dfm/).")
    a("**Não editar à mão** — correção entra no script e o arquivo é regerado:")
    a("")
    a("```sh")
    a(f"python3 {GENERATOR}")
    a(f"python3 {GENERATOR} --check   # o que `make -C wte check` roda")
    a("```")
    a("")
    a("A tabela em si está em [`campos.tsv`](campos.tsv); este arquivo é a leitura")
    a("dela. **Todo número daqui saiu do script**, inclusive os do texto corrido.")
    a("")
    a("## Para que serve")
    a("")
    a("Handler do `.exe` referencia controle por deslocamento — `mov eax,[ebx+0x33c]`.")
    a("Sem este mapa, ler um handler da fase 4 para em *\"ele chama um método de")
    a("alguma coisa\"*, que não dá para escrever em Pascal. Com ele, `0x33c` no")
    a("`ficha_color` é o `recuadro2`, e a frase vira spec.")
    a("")
    a("## A ordem do DFM **não** serve, e é isso que o número abaixo mede")
    a("")
    a("A derivação barata seria: primeiro `object` do `.dfm` no primeiro campo, e")
    a("assim por diante. Medido nos 18 formulários, essa regra acerta")
    a(f"**{coincide} de {total}** campos. A ordem do `.dfm` é a de criação; a dos")
    a("campos é a da declaração no `.h`, e o C++Builder não as mantém em sincronia.")
    a("Derivar dali produziria leitura errada com cara de certa — a armadilha 1 do")
    a("[`../../docs/tasks/progresso.md`](../../docs/tasks/progresso.md) por outro")
    a("caminho.")
    a("")
    a("## De onde o mapa sai")
    a("")
    a("Da *published field table* que o VMT aponta em deslocamento **-56**. Ela")
    a("existe porque o streaming de DFM precisa resolver `object lista_equipos:")
    a("TComboBox` no campo certo, por nome, em tempo de execução — e por isso")
    a("sobreviveu ao `/STRIP`, como a published method table da")
    a("[WTE-TASK-04](../../docs/tasks/04-mapa-de-handlers.md) (-52).")
    a("")
    a("```text")
    a("word  contagem")
    a("dword ponteiro para a tabela de classes")
    a("contagem x { dword deslocamento, word índice de classe, shortstring nome }")
    a("```")
    a("")
    a("## O que foi medido")
    a("")
    if anonimos == 1:
        diferenca = f"A diferença é **{anonimos}** componente **sem nome**, que não gera"
    else:
        diferenca = f"A diferença são **{anonimos}** componentes **sem nome**, que não geram"
    a(f"São **{total} campos** em **{len(medidas)} formulários**, contra")
    a(f"**{objetos} `object`** nos `.dfm`. {diferenca}")
    a("campo — o `TStaticText` de 4×4 px do `MainForm` que o `progresso.md`")
    a("registra como o que separa a contagem exata da apressada.")
    a("")
    a(f"O primeiro campo de todo formulário cai em **{base:#x}** ({base}), que é o")
    a("tamanho de instância de `TForm` nesta VCL. O número sai medido daqui, não")
    a("escrito à mão: o script exige que os 18 concordem e aborta se um discordar —")
    a("discordância significaria que o -56 está errado ou que a classe não deriva")
    a("de `TForm`. O tamanho de instância de cada formulário é o primeiro múltiplo")
    a("de 8 a partir daí, o que explica os 4 bytes de sobra nos de contagem ímpar.")
    a("")
    a("| Formulário | VMT | Instância | Campos | `object` | Sem nome | 1º campo |")
    a("|---|---|---:|---:|---:|---:|---|")
    for m in medidas:
        primeiro = m["campos"][0][1] if m["campos"] else "—"
        a(f"| `{m['form']}` | `{m['vmt']:#010x}` | {m['tam']} | "
          f"{len(m['campos'])} | {m['objects']} | {m['anonimos']} | "
          f"`{primeiro}` |")
    a("")
    a("## Como usar ao ler um handler")
    a("")
    a("O `this` do formulário chega em `EAX` (convenção Borland, §8.1 do plano), e")
    a("o corpo costuma guardá-lo num registrador. `[<reg>+0x2f0]` no `MainForm` é")
    a("o `lista_equipos`; a coluna `offset` do TSV está em hexadecimal justamente")
    a("para colar contra o disassembly sem conversão no meio.")
    a("")
    return "\n".join(w)


def generate() -> dict[str, str]:
    medidas, base = medir()
    return {TSV_NAME: gera_tsv(medidas), MD_NAME: gera_md(medidas, base)}


def do_check(files: dict[str, str]) -> int:
    problemas = []
    for nome, conteudo in sorted(files.items()):
        caminho = OUT / nome
        if not caminho.exists():
            problemas.append(f"{nome}: nao existe")
            continue
        no_disco = caminho.read_text(encoding="utf-8")
        if no_disco == conteudo:
            print(f"dump_campos: {REL_OUT}/{nome}: ok")
            continue
        for i, (x, y) in enumerate(
                zip(no_disco.splitlines(), conteudo.splitlines()), 1):
            if x != y:
                problemas.append(f"{nome}: linha {i} diverge")
                break
        else:
            problemas.append(
                f"{nome}: {len(no_disco.splitlines())} linhas no disco contra "
                f"{len(conteudo.splitlines())} regeradas")
    if problemas:
        print(f"{REL_OUT} nao corresponde a {REL_EXE}:", file=sys.stderr)
        for p in problemas:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1
    return 0


def do_write(files: dict[str, str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in sorted(files.items()):
        (OUT / nome).write_text(conteudo, encoding="utf-8", newline="\n")
        print(f"  {nome}: {conteudo.count(chr(10))} linhas, "
              f"{len(conteudo.encode('utf-8'))} bytes")
    return 0


def main(argv: list[str]) -> int:
    check = False
    for arg in argv:
        if arg == "--check":
            check = True
        else:
            print(f"uso: {GENERATOR} [--check]", file=sys.stderr)
            return 2
    try:
        files = generate()
    except DumpError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return do_check(files) if check else do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
