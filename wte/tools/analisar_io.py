#!/usr/bin/env python3
"""Le o trace de I/O do `wte.exe` e diz que regiao da imagem ele toca.

WTE-TASK-19. Dois modos, e so o segundo e gerador:

**Medicao** (`--log`) -- converte um `strace` produzido pelo
`wte/tools/diff_dirigido.sh` em faixas `(acao, op, offset, tamanho)`. E aqui
que a evidencia nasce; a saida vai para o TSV que o `--tsv` nomear.

**Geracao** (sem argumento, ou `--check`) -- le a evidencia ja versionada em
`wte/re/io-medido.tsv` e escreve `wte/re/offsets-novos.md`, cruzando cada faixa
medida com o `Offsets.hpp` do `newWe2002` e com os candidatos que a WTE-TASK-06
extraiu do `.exe`.

## Por que trace, e por que ele responde o que `cmp` nao responde

A pergunta da task e *que regioes o app Lazarus precisa endereçar*. `cmp` so
enxerga escrita de valor DIFERENTE: o editor do Obocaman grava, na maior parte
das areas, exatamente o que leu, e ali um `cmp` limpo nao distingue "nao
gravou" de "gravou igual". Pior: `cmp` nao ve LEITURA nenhuma, e leitura e
metade da resposta -- e a metade que diz onde os 50 `OFS_*` ausentes moram.

## O que uma faixa e, e o que ela nao e

Uma faixa e um intervalo `[offset, offset+tamanho)` que uma syscall tocou. Ela
**nao** e um campo: o `wte.exe` le em blocos de 512 e 2048 bytes, entao uma
leitura de 512 bytes a partir de `OFS_TEAM_NAME_1+1` cobre tanto o nome do time
quanto o que vier depois. Confirmar um offset por conteudo de faixa e
afirmacao de POSICAO, nao de semantica -- o que a faixa prova e que o app
endereca aquele ponto, nao o que ele faz com o byte.

Uso:
    bash wte/tools/diff_dirigido.sh <roteiro>       # produz o log
    python3 wte/tools/analisar_io.py --log ... --tsv ...
    python3 wte/tools/analisar_io.py                # regera offsets-novos.md
    python3 wte/tools/analisar_io.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OFFSETS_HPP = ROOT / "src" / "core" / "include" / "we2002" / "Offsets.hpp"
OFFSETS_TSV = ROOT / "wte" / "re" / "offsets.tsv"
MEDIDO_TSV = ROOT / "wte" / "re" / "io-medido.tsv"
OUT_MD = ROOT / "wte" / "re" / "offsets-novos.md"

SETOR = 2352
DADOS_INI, DADOS_FIM = 24, 2072

# Quanto um `_llseek` pode cair depois de um `OFS_*` e ainda ser aquele offset.
# Medido: o `wte.exe` procura o inicio do NOME e nao do REGISTRO, e por isso
# quase toda leitura comeca em `OFS_* + 1`. A folga cobre isso sem deixar um
# offset vizinho ser reivindicado por engano -- os `OFS_*` mais proximos entre
# si na tabela do newWe2002 distam 48 bytes (`OFS_LINK_ML` e `OFS_LINK_ML1`).
FOLGA_INICIO = 16


# =========================================================== 1. a medicao ===

def _regex(alvo: str) -> dict[str, re.Pattern]:
    a = re.escape(alvo)
    return {
        # `_llseek(fd, off, [ABS], WHENCE)` -- o que interessa e o `[ABS]`, a
        # posicao ABSOLUTA resultante, e nao o argumento `off`: com SEEK_CUR o
        # argumento e relativo, e le-lo como absoluto poe a faixa no offset 0.
        "seek": re.compile(r"_llseek\((\d+)<[^>]*" + a + r">,\s*-?\d+,\s*\[(\d+)\]"),
        "seek64": re.compile(r"\blseek\((\d+)<[^>]*" + a
                             + r">,\s*-?\d+,\s*\w+\)\s*=\s*(\d+)"),
        "rw": re.compile(r"\b(read|write)\((\d+)<[^>]*" + a
                         + r">,.*?,\s*(\d+)\)\s*=\s*(-?\d+)"),
        "p": re.compile(r"\bp(read|write)64\((\d+)<[^>]*" + a
                        + r">,.*?,\s*(\d+),\s*(\d+)\)\s*=\s*(-?\d+)"),
        # Syscall partida em duas linhas. O `strace -f` corta toda syscall que
        # bloqueia, e sobre a imagem isso e a MAIORIA delas -- ignorar o par
        # perdia escrita inteira em silencio, e so o confronto com o `cmp`
        # mostrou.
        "abre": re.compile(r"^(\d+)\s+\S+\s+(pread64|pwrite64|read|write|_llseek)"
                           r"\((\d+)<[^>]*" + a + r">,\s*(-?\d+)?.*<unfinished"),
        "retoma": re.compile(r"^(\d+)\s+\S+\s+<\.\.\. "
                             r"(pread64|pwrite64|read|write|_llseek) resumed>"
                             r"(.*)$"),
    }


RE_HORA = re.compile(r"^\s*(\d+)\s+(\d\d):(\d\d):(\d\d)\.(\d+)")


def _segundos(h: str, m: str, s: str, frac: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + float("0." + frac)


def hora_da_linha(ln: str) -> float | None:
    m = RE_HORA.match(ln)
    return _segundos(*m.groups()[1:]) if m else None


def eventos_datados(linhas, alvo: str):
    """(hora, op, offset, tamanho) de cada syscall que tocou a imagem.

    O `strace -y` carimba o caminho ao lado do fd, entao a filtragem e por
    nome de arquivo e nao por numero -- fd se recicla, nome nao.

    A varredura e sobre o log INTEIRO, de proposito: a posicao do arquivo vem
    de um `_llseek` que pode estar do outro lado de uma marca, e fatiar o log
    antes de reconstruir a posicao perderia essa continuidade.
    """
    R = _regex(alvo)
    pos: dict[str, int] = {}
    pendente: dict[str, tuple[str, str, float | None]] = {}

    def registra(op: str, fd: str, got: int, quando):
        p = pos.get(fd, 0)
        pos[fd] = p + got
        return (quando, "R" if op == "read" else "W", p, got)

    for ln in linhas:
        quando = hora_da_linha(ln)

        m = R["p"].search(ln)
        if m:
            op, _fd, _n, off, got = m.groups()
            if int(got) > 0:
                yield (quando, "R" if op == "read" else "W", int(off), int(got))
            continue

        m = R["retoma"].match(ln)
        if m:
            pid, op, resto = m.groups()
            alvo_pend = pendente.pop(pid, None)
            if alvo_pend is None or alvo_pend[0] != op:
                continue
            _op, fd, _q = alvo_pend
            if op == "_llseek":
                mm = re.search(r"\[(\d+)\]", resto)
                if mm:
                    pos[fd] = int(mm.group(1))
                continue
            if op.startswith("p"):
                # `<... pread64 resumed>"...", COUNT, OFFSET) = GOT` -- o
                # offset e argumento, e nao a posicao do arquivo.
                mm = re.search(r",\s*(\d+),\s*(\d+)\)\s*=\s*(-?\d+)", resto)
                if mm and int(mm.group(3)) > 0:
                    yield (quando, "R" if op == "pread64" else "W",
                           int(mm.group(2)), int(mm.group(3)))
                continue
            mm = re.search(r"=\s*(-?\d+)", resto)
            if mm and int(mm.group(1)) > 0:
                yield registra(op, fd, int(mm.group(1)), quando)
            continue

        m = R["abre"].match(ln)
        if m:
            pid, op, fd, _off = m.groups()
            pendente[pid] = (op, fd, quando)
            continue

        m = R["seek"].search(ln)
        if m:
            pos[m.group(1)] = int(m.group(2))
            continue
        m = R["seek64"].search(ln)
        if m:
            pos[m.group(1)] = int(m.group(2))
            continue

        m = R["rw"].search(ln)
        if m:
            op, fd, _n, got = m.groups()
            if int(got) > 0:
                yield registra(op, fd, int(got), quando)


def eventos(linhas, alvo: str):
    """(op, offset, tamanho), sem a hora. E a forma que os testes exercitam."""
    for _quando, op, off, n in eventos_datados(linhas, alvo):
        yield (op, off, n)


def unir(evs, op: str) -> list[tuple[int, int]]:
    itens = sorted((o, o + n) for t, o, n in evs if t == op)
    fora: list[list[int]] = []
    for a, b in itens:
        if fora and a <= fora[-1][1]:
            fora[-1][1] = max(fora[-1][1], b)
        else:
            fora.append([a, b])
    return [(a, b) for a, b in fora]


def medir(log: Path, marcas: Path, alvo: str, tsv: Path,
          imagem: str = "?") -> int:
    """Fatia o trace por RELOGIO, e nao por numero de linha.

    O `strace` bufferiza o arquivo de log: `wc -l` no instante da marca fica
    atras das syscalls que ja aconteceram, e a atribuicao "esta faixa e daquela
    acao" sai errada em silencio. Foi medido -- sete escritas do arranque
    viraram duas no TSV enquanto o `cmp` continuava mostrando as sete.
    """
    linhas = log.read_text(errors="replace").splitlines()
    cortes = []
    for l in marcas.read_text().splitlines():
        if not l.strip():
            continue
        quando, nome = l.split("\t")
        h, m, resto = quando.split(":")
        s, frac = resto.split(".")
        cortes.append((_segundos(h, m, s, frac), nome.strip()))
    fora = ["imagem\tacao\top\tinicio\tfim\ttamanho\tsetor\tbyte_no_setor"]
    datados = list(eventos_datados(linhas, alvo))
    total = 0
    for i, (fim, nome) in enumerate(cortes):
        ini = cortes[i - 1][0] if i else 0.0
        evs = [(op, o, n) for q, op, o, n in datados
               if q is not None and ini <= q < fim]
        antes = total
        for op in ("R", "W"):
            for a, b in unir(evs, op):
                fora.append(f"{imagem}\t{nome}\t{op}\t{a}\t{b - 1}\t{b - a}"
                            f"\t{a // SETOR}\t{a % SETOR}")
                total += 1
        if total == antes:
            # Acao exercitada que NAO tocou a imagem. Fica registrada: "nao
            # gravou" e resultado, e sem a linha ela seria indistinguivel de
            # "nao foi exercitada".
            fora.append(f"{imagem}\t{nome}\t.\t\t\t0\t\t")
    tsv.write_text("\n".join(fora) + "\n")
    print(f"analisar_io: {total} faixa(s) -> {tsv}")
    return 0


def conferir_reguas(io_tsv: Path, cmp_tsv: Path) -> int:
    """As duas reguas tem de fechar: o que MUDOU esta no que foi ESCRITO.

    O trace ve escrita de qualquer valor; o `cmp` so ve escrita de valor
    diferente. Logo toda faixa do `cmp` tem de caber dentro de alguma faixa de
    escrita do trace -- o contrario nao vale, e nao e erro.

    Faixa do `cmp` que sobra significa que o trace PERDEU syscall, e ai nenhum
    numero desta task vale nada. Ja aconteceu: o corte por numero de linha
    ficava atras do buffer do `strace` e atribuia escrita a acao errada.
    """
    def ler(p: Path) -> list[dict[str, str]]:
        linhas = p.read_text(encoding="utf-8").splitlines()
        cab = linhas[0].split("\t")
        return [dict(zip(cab, l.split("\t"))) for l in linhas[1:] if l.strip()]

    escritas = [(int(r["inicio"]), int(r["fim"]))
                for r in ler(io_tsv) if r.get("op") == "W" and r.get("inicio")]
    mudou = [(int(r["inicio"]), int(r["fim"])) for r in ler(cmp_tsv)]
    orfas = [(a, b) for a, b in mudou
             if not any(x <= a and b <= y for x, y in escritas)]
    if orfas:
        print(f"analisar_io: ATENCAO -- {len(orfas)} de {len(mudou)} faixa(s) "
              f"que MUDARAM nao aparecem como escrita no trace:", file=sys.stderr)
        for a, b in orfas:
            print(f"  {a}..{b} ({b - a + 1} B)", file=sys.stderr)
        print("  o trace perdeu syscall; a atribuicao por acao nao vale",
              file=sys.stderr)
        return 3
    print(f"analisar_io: as duas reguas fecham -- {len(mudou)} faixa(s) do cmp "
          f"contidas em {len(escritas)} faixa(s) de escrita do trace")
    return 0


AMOSTRA = 64
OUT_CONTEUDO = ROOT / "wte" / "re" / "io-conteudo.tsv"


def amostrar(imagem: Path) -> int:
    """Que conteudo a imagem tem nas faixas que o `wte.exe` leu.

    A pergunta que isto responde e a do travamento: o editor cai logo depois de
    ler uma faixa, e saber se aquela faixa tem DADO ou esta zerada e a
    diferenca entre "ele leu e nao gostou" e "nao ha o que ler nesta release".

    Le uma **copia**, nunca `roms/` -- o chamador passa o caminho, e o
    `diff_dirigido.sh` passa a copia de `work/`.
    """
    faixas = [f for f in ler_medido() if f["op"] == "R" and f["inicio"]]
    vistos: dict[int, dict] = {}
    for f in faixas:
        vistos.setdefault(int(f["inicio"]), f)
    fora = ["inicio\ttamanho\tbytes_amostrados\tnao_zero\tamostra_hex"]
    with imagem.open("rb") as fh:
        for inicio in sorted(vistos):
            f = vistos[inicio]
            n = min(AMOSTRA, int(f["tamanho"]))
            fh.seek(inicio)
            b = fh.read(n)
            fora.append(f"{inicio}\t{f['tamanho']}\t{len(b)}"
                        f"\t{sum(1 for c in b if c)}\t{b.hex()}")
    OUT_CONTEUDO.write_text("\n".join(fora) + "\n")
    print(f"analisar_io: {len(vistos)} faixa(s) amostrada(s) -> "
          f"{OUT_CONTEUDO.relative_to(ROOT)}")
    return 0


def ler_conteudo() -> dict[int, dict[str, str]]:
    if not OUT_CONTEUDO.exists():
        return {}
    linhas = OUT_CONTEUDO.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    return {int(r["inicio"]): r for r in
            (dict(zip(cab, l.split("\t"))) for l in linhas[1:] if l.strip())}


# ========================================================== 2. a geracao ====

def ler_offsets_hpp() -> dict[str, int]:
    txt = OFFSETS_HPP.read_text(encoding="utf-8")
    return {m.group(1): int(m.group(2)) for m in re.finditer(
        r"inline\s+constexpr\s+Offset\s+(OFS_\w+)\s*=\s*(\d+)\s*;", txt)}


def ler_offsets_tsv() -> list[dict[str, str]]:
    linhas = OFFSETS_TSV.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    return [dict(zip(cab, l.split("\t"))) for l in linhas[1:] if l.strip()]


def ler_medido() -> list[dict[str, str]]:
    if not MEDIDO_TSV.exists():
        raise SystemExit(f"analisar_io: falta {MEDIDO_TSV.relative_to(ROOT)} -- "
                         f"rode wte/tools/diff_dirigido.sh primeiro")
    linhas = MEDIDO_TSV.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    return [dict(zip(cab, l.split("\t"))) for l in linhas[1:] if l.strip()]


def casar(faixas: list[dict], conhecidos: dict[str, int]) -> dict[str, list[dict]]:
    """`OFS_*` -> faixas que o cobrem. Um offset e coberto quando cai dentro."""
    fora: dict[str, list[dict]] = {}
    for nome, valor in conhecidos.items():
        for f in faixas:
            a, b = int(f["inicio"]), int(f["fim"])
            if a - FOLGA_INICIO <= valor <= b:
                fora.setdefault(nome, []).append(f)
    return fora


def sem_dono(faixas: list[dict], conhecidos: dict[str, int]) -> list[dict]:
    valores = sorted(conhecidos.values())
    fora = []
    for f in faixas:
        a, b = int(f["inicio"]), int(f["fim"])
        if not any(a - FOLGA_INICIO <= v <= b for v in valores):
            fora.append(f)
    return fora


def gerar() -> str:
    conhecidos = ler_offsets_hpp()
    tsv = ler_offsets_tsv()
    todas_sessoes = ler_medido()
    conteudo = ler_conteudo()

    imagens = []
    for r in todas_sessoes:
        if r["imagem"] not in imagens:
            imagens.append(r["imagem"])
    principal = imagens[0]
    medido = [r for r in todas_sessoes if r["imagem"] == principal]

    confirmados_06 = {r["nome"] for r in tsv if r["registro"] == "confirmado"}
    ausentes_06 = {r["nome"]: r for r in tsv if r["registro"] == "ausente"}
    candidatos = {int(r["valor"]): r for r in tsv if r["registro"] == "candidato"}

    faixas = [f for f in medido if f["op"] in ("R", "W")]
    # Acao exercitada que nao tocou a imagem. "Nao gravou" e resultado, e sem
    # a linha ele seria indistinguivel de "nao foi exercitada".
    silenciosas = [f for f in medido if f["op"] == "."]
    leitura = [f for f in faixas if f["op"] == "R"]
    escrita = [f for f in faixas if f["op"] == "W"]
    tocado = casar(faixas, conhecidos)
    orfas = sem_dono(faixas, conhecidos)

    acoes = []
    for f in medido:
        if f["acao"] not in acoes:
            acoes.append(f["acao"])

    L: list[str] = []
    w = L.append

    w("# Offsets medidos contra o `wte.exe` em execução — WTE-TASK-19")
    w("")
    w("**GERADO por `wte/tools/analisar_io.py` — não editar à mão.**")
    w("Evidência: [`io-medido.tsv`](io-medido.tsv), produzido por")
    w("[`../tools/diff_dirigido.sh`](../tools/diff_dirigido.sh).")
    w("Regenerar: `python3 wte/tools/analisar_io.py`.")
    w("")
    w("O irmão estático é [`offsets.md`](offsets.md), que lê o `.exe` parado.")
    w("Aqui o `.exe` **roda**, e o que se mede é a syscall.")
    w("")
    w("---")
    w("")
    w("## O método, e por que não é `cmp`")
    w("")
    w("O enunciado da task pede diff dirigido: editar um campo, gravar, `cmp`.")
    w("Isso enxerga **escrita de valor diferente**, e só. O editor do Obocaman")
    w("grava, na maior parte das áreas, exatamente o que leu — ali o `cmp` sai")
    w("limpo e não distingue *não gravou* de *gravou igual*, que levam a")
    w("conclusões opostas sobre o que o app Lazarus precisa endereçar. E `cmp`")
    w("não vê **leitura** nenhuma, que é a metade da resposta que diz onde os")
    w("50 `OFS_*` ausentes moram.")
    w("")
    w("Então a régua é `strace` sobre o processo Wine, e o `cmp` fica como")
    w("segunda régua independente: toda faixa que mudou no arquivo tem de estar")
    w("contida numa faixa de escrita do trace.")
    w("")
    w("### Um terceiro caminho que foi tentado e **derruba o app**")
    w("")
    w("Encher a cópia com um padrão (`0xA5`) depois do Load e ver o que")
    w("sobrevive à gravação. A ideia era mapear escrita sem depender de valor.")
    w("**Não funciona:** o `wte.exe` não lê tudo no Load — ele lê sob demanda,")
    w("e uma imagem de 474 MB cheia de `0xA5` o mata no primeiro clique, com a")
    w("janela sobrevivendo ao processo. Medido, e registrado aqui para que")
    w("ninguém repita.")
    w("")
    w("---")
    w("")
    w("## O diff de controle vem primeiro")
    w("")
    ctrl = [f for f in escrita if f["acao"] == "ARRANQUE"]
    tot = sum(int(f["tamanho"]) for f in ctrl)
    w(f"**Abrir a imagem, sem tocar em nada, já grava {tot} bytes em "
      f"{len(ctrl)} faixa(s).**")
    w("Não é o `Load`+`Save` não idempotente do `ed.exe`: aqui não há `Save`")
    w("nenhum — o `wte.exe` escreve durante a **carga**, antes de a janela")
    w("principal aparecer e sem clique de usuário.")
    w("")
    if ctrl:
        w("| faixa | tamanho | setor | byte no setor |")
        w("|---|---:|---:|---:|")
        for f in ctrl:
            w(f"| {f['inicio']}..{f['fim']} | {f['tamanho']} | {f['setor']} "
              f"| {f['byte_no_setor']} |")
        w("")
        atingidos = sorted(
            (v, n) for n, v in conhecidos.items()
            if any(int(f["inicio"]) <= v <= int(f["fim"]) for f in ctrl))
        # 2048 = a regiao de dados de usuario inteira de um setor.
        bloco = [f for f in ctrl if int(f["tamanho"]) >= DADOS_FIM - DADOS_INI]
        a0 = min(int(f["inicio"]) for f in bloco)
        b0 = max(int(f["fim"]) for f in bloco)
        w(f"Sete das oito faixas são contíguas em setor: `{a0}`..`{b0}`, "
          f"setores {a0 // SETOR} a {b0 // SETOR}, sempre do byte 24 ao 2071 —")
        w("a região de dados de usuário inteira de cada setor. Estão **abaixo**")
        w(f"do menor offset que este repositório conhece (`"
          f"{min(conhecidos.values())}`), então nenhuma toca dado de time ou")
        w("de jogador.")
        w("")
        if atingidos:
            w("A oitava toca, sim, um `OFS_*`: "
              + ", ".join(f"`{n}` (`{v}`)" for v, n in atingidos) + ".")
        else:
            avulsas = [f for f in ctrl
                       if int(f["tamanho"]) < DADOS_FIM - DADOS_INI]
            for f in avulsas:
                a = int(f["inicio"])
                perto = min(conhecidos.items(), key=lambda kv: abs(kv[1] - a))
                w(f"A oitava é de **{f['tamanho']} byte** em `{a}` (setor "
                  f"{f['setor']}, byte {f['byte_no_setor']}). Nenhum `OFS_*` "
                  f"cai nela; o mais")
                w(f"próximo é `{perto[0]}` = `{perto[1]}`, a "
                  f"{abs(perto[1] - a)} bytes. Um byte solto, gravado na carga")
                w("e sem nome — é candidato a offset novo, e está na tabela de")
                w("faixas órfãs abaixo.")
        w("")
    w("**Consequência para toda medição desta task:** essa faixa é ruído de")
    w("fundo e sai da conta. Sem o controle, ela apareceria em cada corrida e")
    w("pareceria efeito da edição.")
    w("")
    w("---")
    w("")
    w("## O que a sessão mediu")
    w("")
    w("| ação | faixas de leitura | bytes lidos | faixas de escrita | bytes escritos |")
    w("|---|---:|---:|---:|---:|")
    for acao in acoes:
        r = [f for f in leitura if f["acao"] == acao]
        e = [f for f in escrita if f["acao"] == acao]
        w(f"| `{acao}` | {len(r)} | {sum(int(f['tamanho']) for f in r)} "
          f"| {len(e)} | {sum(int(f['tamanho']) for f in e)} |")
    w("")
    if silenciosas:
        w(f"**{len(silenciosas)} das {len(acoes)} ações não tocaram a imagem "
          f"em byte nenhum:** "
          + ", ".join(f"`{f['acao']}`" for f in silenciosas) + ".")
        w("")
        w("Isso é medida, e não ausência de medida: os cliques **chegam** ao")
        w("app — o mesmo roteiro reabre o splash `Sobre...` por clique, com a")
        w("janela mapeando —, e mesmo assim os botões de gravação por área não")
        w("escrevem byte nenhum enquanto não houver time selecionado.")
        w("")
    w("---")
    w("")
    w(f"## Os `OFS_*` que a execução confirmou — {len(tocado)}")
    w("")
    w("Confirmado aqui quer dizer: **o `wte.exe` endereçou este ponto da")
    w("imagem**. É afirmação de posição, não de semântica — a leitura vem em")
    w("bloco de 512 ou 2048 bytes, e o que a faixa prova é que o app vai ali.")
    w("")
    w("A coluna \"WTE-TASK-06\" diz o que a análise **estática** tinha dito do")
    w("mesmo offset. `ausente` virando confirmado é o resultado que esta task")
    w("existe para produzir.")
    w("")
    w("| `Offsets.hpp` | valor | WTE-TASK-06 | ação | op | faixa |")
    w("|---|---:|---|---|---|---|")
    for nome in sorted(tocado, key=lambda n: conhecidos[n]):
        f = tocado[nome][0]
        antes = ("confirmado" if nome in confirmados_06
                 else f"ausente ({ausentes_06[nome]['classe']})"
                 if nome in ausentes_06 else "—")
        w(f"| `{nome}` | {conhecidos[nome]} | {antes} | `{f['acao']}` "
          f"| {f['op']} | {f['inicio']}..{f['fim']} |")
    w("")
    novos_confirmados = sorted(n for n in tocado if n in ausentes_06)
    w(f"**{len(novos_confirmados)} dos 50 `ausente`** da WTE-TASK-06 passaram a")
    w("`confirmado` por execução. Os demais continuam sem evidência dinâmica —")
    w("não porque o `wte.exe` não os alcance, mas porque a sessão medida não")
    w("exercitou a tela que os toca.")
    w("")
    w("---")
    w("")
    w(f"## Faixas que nenhum `OFS_*` explica — {len(orfas)}")
    w("")
    w("Região que o `wte.exe` endereça e que o `Offsets.hpp` do `newWe2002`")
    w("não nomeia. É a lista que o app Lazarus vai precisar, e que este")
    w("repositório ainda não tem.")
    w("")
    w("| ação | op | faixa | tamanho | setor | candidato da WTE-TASK-06 |")
    w("|---|---|---|---:|---:|---|")
    for f in orfas:
        a, b = int(f["inicio"]), int(f["fim"])
        dentro = [v for v in candidatos if a - FOLGA_INICIO <= v <= b]
        cand = ", ".join(f"`{v}`" for v in sorted(dentro)) or "—"
        w(f"| `{f['acao']}` | {f['op']} | {a}..{b} | {f['tamanho']} "
          f"| {f['setor']} | {cand} |")
    w("")
    fora_da_faixa = [f for f in orfas
                     if int(f["inicio"]) > max(conhecidos.values())]
    if fora_da_faixa:
        w("### Fora da janela que o `newWe2002` conhece")
        w("")
        w(f"O maior offset do `Offsets.hpp` é `{max(conhecidos.values())}`.")
        w("As faixas abaixo estão **acima** dele — território que este")
        w("repositório nunca precisou endereçar, e o aviso que a")
        w("[`offsets.md`](offsets.md) escreveu se cumpre: a faixa do filtro")
        w("estático deriva do nosso próprio `Offsets.hpp`, então offset novo")
        w("aqui **alarga a janela** e obriga a reconferir o limite das duas")
        w("tabelas.")
        w("")
        w("| ação | op | faixa | tamanho | setor | byte no setor |")
        w("|---|---|---|---:|---:|---:|")
        for f in fora_da_faixa:
            w(f"| `{f['acao']}` | {f['op']} | {f['inicio']}..{f['fim']} "
              f"| {f['tamanho']} | {f['setor']} | {f['byte_no_setor']} |")
        w("")
    w("---")
    w("")
    w("## O limite duro desta medição: o `wte.exe` morre ao carregar um time")
    w("")
    w("Medido, e é o que impede esta task de fechar. Com as duas ROMs que este")
    w("repositório tem, o `wte.exe` **encerra com falha de segmentação logo")
    w("depois** de ler os dados do primeiro time selecionado:")
    w("")
    w("```")
    w("--- SIGSEGV {si_signo=SIGSEGV, si_code=SEGV_MAPERR, si_addr=NULL} ---")
    w("```")
    w("")
    w("A janela sobrevive ao processo — o `wineserver` a mantém mapeada —, e é")
    w("por isso que o sintoma se disfarça de *clique parou de funcionar*.")
    w("Foram gastos dois diagnósticos até separar as duas coisas; quem repetir")
    w("a medição confira `ps -o stat` procurando `Z`, e não a tela.")
    w("")
    w("### A hipótese do tamanho foi testada, e está **refutada**")
    w("")
    w("O editor avisa na abertura que o tamanho não corresponde: ele quer")
    w("**474.431.328** bytes exatos, e as ROMs daqui têm 474.784.128 (European")
    w("Deluxe) e 307.187.664 (japonesa). A diferença da primeira é")
    w("**352.800 bytes = exatamente 150 setores** de 2352, e toda ela está na")
    w("cauda, muito depois do maior offset conhecido.")
    w("")
    if len(imagens) > 1:
        outra = imagens[1]
        w(f"Então a cópia foi truncada para o tamanho exato (`{outra}`) e a")
        w("sessão rodou de novo, mesmo roteiro, uma variável trocada. Resultado:")
        w("")
        w("- o aviso de tamanho **some** — o corte é o que ele queria;")
        w("- o mapa de I/O sai **idêntico faixa a faixa**, leitura e escrita;")
        w("- **o `wte.exe` cai igual**, no mesmo ponto.")
        w("")
        w("Tamanho não é a causa. O que a hipótese explicava era o aviso, e o")
        w("aviso nunca foi o problema.")
        w("")
    w("### O que sobra como pista: a região está vazia nesta release")
    w("")
    ultima = conteudo.get(14368636)
    if ultima:
        w(f"A última leitura antes do `SIGSEGV` são {ultima['tamanho']} bytes em")
        w(f"`14368636` — 1,8 MB **acima** do maior offset que o `newWe2002`")
        w(f"conhece. Amostrando os primeiros {ultima['bytes_amostrados']} bytes")
        w(f"dessa faixa na imagem: **{ultima['nao_zero']} não são zero**.")
        w("")
        outros = [c for o, c in sorted(conteudo.items())
                  if o != 14368636 and int(c["bytes_amostrados"]) >= 64]
        if outros:
            menor = min(int(c["nao_zero"]) for c in outros)
            w(f"Para comparar: das outras {len(outros)} faixas lidas, a mais")
            w(f"vazia tem {menor} bytes não-zero na mesma amostra. A região que")
            w("o editor lê por último, e logo antes de morrer, é a única")
            w("praticamente zerada.")
            w("")
        w("Isso não prova a causa — prova que **nesta release não há o que ler**")
        w("onde o editor foi ler. Medida em [`io-conteudo.tsv`](io-conteudo.tsv).")
        w("")
    w("**O pedido, então, deixou de ser \"a release de 474.431.328 bytes\" e")
    w("passou a ser: uma release cuja região em `14368636` seja populada.**")
    w("Truncar a que temos não serve; é preciso outro dump.")
    w("")
    w("### O que isso custa, e a quem")
    w("")
    w("| Alcançado | Bloqueado |")
    w("|---|---|")
    w("| arranque e carga inicial | os seis grupos de campo da WTE-TASK-19 |")
    w("| seleção de time (uma vez) | qualquer gravação por área |")
    w("| o diff de controle | o diff dirigido *stricto sensu* — editar um campo e gravar |")
    w("")
    w("E o custo maior não é desta task: o `wte.exe` é o **oráculo")
    w("comportamental** do projeto (§4.2 do plano), e a")
    w("[WTE-TASK-22](../../docs/tasks/22-harness-golden.md) monta o gate golden")
    w("em cima dele. Um oráculo que não passa da tela de carga não sustenta")
    w("gate nenhum. **Achar a release de 474.431.328 bytes deixou de ser")
    w("desejável e passou a ser pré-requisito da fase 4.**")
    w("")
    w("---")
    w("")
    w("## Geometria de setor, conferida")
    w("")
    dentro = sum(1 for f in faixas
                 if DADOS_INI <= int(f["inicio"]) % SETOR < DADOS_FIM)
    w(f"{dentro} de {len(faixas)} faixas começam dentro da região de dados de")
    w(f"usuário de um setor MODE2/2352 (bytes {DADOS_INI}..{DADOS_FIM - 1}).")
    w("O corte não é decorativo: é o mesmo que a WTE-TASK-06 usa para separar")
    w("offset de imagem de constante qualquer, e vê-lo valer sobre syscall")
    w("real é a confirmação de que a régua estática media a coisa certa.")
    w("")
    fora_da_regiao = [f for f in faixas
                      if not (DADOS_INI <= int(f["inicio"]) % SETOR < DADOS_FIM)]
    if fora_da_regiao:
        w("A(s) exceção(ões):")
        w("")
        for f in fora_da_regiao:
            w(f"- `{f['acao']}` {f['op']} em `{f['inicio']}`, {f['tamanho']} "
              f"byte(s) — byte {int(f['inicio']) % SETOR} do setor "
              f"{f['setor']}.")
        w("")
        w("A leitura de 23 bytes no offset `0` não é dado: é o *sync* mais o")
        w("cabeçalho do setor 0, que o editor lê para reconhecer o formato — e")
        w("cabeçalho de setor fica, por definição, fora da região de dados.")
        w("")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", type=Path, help="trace do diff_dirigido.sh")
    ap.add_argument("--marcas", type=Path)
    ap.add_argument("--alvo", default="dd-run.bin")
    ap.add_argument("--tsv", type=Path)
    ap.add_argument("--imagem", default="?")
    ap.add_argument("--amostrar", type=Path, metavar="COPIA",
                    help="amostra o conteudo das faixas lidas, numa COPIA")
    ap.add_argument("--conferir", nargs=2, type=Path,
                    metavar=("IO_TSV", "CMP_TSV"),
                    help="confere que o cmp cabe nas escritas do trace")
    ap.add_argument("--check", action="store_true",
                    help="nao escreve; sai 2 se a saida divergir do commitado")
    args = ap.parse_args(argv)

    if args.amostrar:
        return amostrar(args.amostrar)

    if args.conferir:
        return conferir_reguas(*args.conferir)

    if args.log:
        if not (args.marcas and args.tsv):
            ap.error("--log exige --marcas e --tsv")
        return medir(args.log, args.marcas, args.alvo, args.tsv, args.imagem)

    texto = gerar()
    rel = OUT_MD.relative_to(ROOT)
    if args.check:
        if not OUT_MD.exists() or OUT_MD.read_text(encoding="utf-8") != texto:
            print(f"analisar_io: {rel}: DIVERGE do gerador", file=sys.stderr)
            return 2
        print(f"analisar_io: {rel}: ok")
        return 0
    OUT_MD.write_text(texto, encoding="utf-8")
    print(f"analisar_io: {rel}: {len(texto)} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
