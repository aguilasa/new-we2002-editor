#!/usr/bin/env python3
"""A bateria golden completa: operacao x ROM x resultado.

Gera `wte/re/golden.md` -- o produto da WTE-TASK-34, a partir do
`wte/re/golden.tsv` que o `golden_suite.sh` escreve enquanto roda. Irmao dos
`check_fase1/2/3/4.py`, e pela mesma razao: numero em doc que nao saiu de
ferramenta ja se propagou neste repositorio (CORR-WTE-012, -014, -023).

    python3 wte/tools/check_golden.py           # regera
    python3 wte/tools/check_golden.py --check   # o que `make -C wte check` roda

## A divisao de trabalho com o `check_fase4.py`

O `check_fase4.py` pergunta *os 96 handlers tem veredito?* e usa a bateria como
UMA das suas medidas. Este pergunta *a bateria cobre o que a fase 6 exige?*, e
o eixo dele e outro: ROM x operacao, nao handler x veredito. Os dois leem TSVs
diferentes, escritos por corridas diferentes, e nenhum reescreve o do outro.

## Os cinco vereditos, e por que `SEM_ORACULO` nao e `REPROVOU`

| veredito | o que aconteceu |
|---|---|
| `PASSOU` | os dois lados produziram a mesma imagem (e o mesmo artefato) |
| `REPROVOU` | divergiram -- e a unica que acusa o port |
| `SEM_ORACULO` | o `wte.exe` morreu com `c0000005` e gravou menos |
| `NAO_APLICAVEL` | o `controle` daquele par nao passou, entao o `golden` seria ilegivel |
| `ESTOUROU_TEMPO` | 900 s sem terminar |

**A distincao entre `REPROVOU` e `SEM_ORACULO` e a task inteira.** O criterio
da WTE-TASK-34 diz "nas duas ROMs", e a europeia mata o oraculo ao trocar de
time (`wte/re/crash-causa.md`). Oraculo que morre no meio grava MENOS: um verde
ali seria mentira, e um vermelho acusaria o port por bytes que o original nunca
chegou a escrever. Nenhuma das duas palavras serve, e por isso ha uma terceira.

## As duas guardas

1. **`golden` sem `controle` na mesma ROM aborta.** O controle vem antes do
   teste, e sem ele verde e vermelho nao significam nada. A bateria ja recusa
   rodar nessa ordem; esta guarda impede que um TSV editado a mao publique o
   que a bateria nao produziria.
2. **Roteiro em disco e ausente do TSV aborta.** Bateria que cresce e tabela
   que nao acompanha e como a conta de gravacoes ficava antes da WTE-TASK-31:
   o numero envelhece sozinho e ninguem repara.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WTE = ROOT / "wte"
TSV = WTE / "re" / "golden.tsv"
OUT = WTE / "re" / "golden.md"
ROTEIROS = WTE / "tests" / "roteiros"

ROMS = ("japonesa", "europeia")
VEREDITOS = ("PASSOU", "REPROVOU", "SEM_ORACULO", "NAO_APLICAVEL",
             "ESTOUROU_TEMPO")

# As duas combinacoes que a fase 6 acrescenta, e a task que as nomeia. Um
# roteiro so entra aqui quando existe em disco; a guarda 2 cuida do resto.
CATEGORIA = {
    "golden-23-multiplas-edicoes": "edicao multipla antes de gravar",
    "golden-24-gravacao-dupla": "gravar duas vezes seguidas",
}


class CheckError(Exception):
    pass


def le_tsv() -> list[dict]:
    if not TSV.exists():
        raise CheckError(f"falta {TSV.relative_to(ROOT)} -- rode o golden_suite.sh")
    linhas = TSV.read_text(encoding="utf-8").splitlines()
    if not linhas:
        raise CheckError(f"{TSV.relative_to(ROOT)} vazio")
    cab = linhas[0].split("\t")
    esperado = ["roteiro", "rom", "modo", "veredito", "segundos", "data"]
    if cab != esperado:
        raise CheckError(f"cabecalho inesperado no TSV: {cab}")
    fora = []
    linhas_lidas = []
    for n, l in enumerate(linhas[1:], start=2):
        if not l.strip():
            continue
        c = l.split("\t")
        if len(c) != 6:
            raise CheckError(f"{TSV.name}:{n}: {len(c)} colunas, esperava 6")
        d = dict(zip(cab, c))
        if d["veredito"] not in VEREDITOS:
            fora.append(f"{TSV.name}:{n}: {d['veredito']}")
        linhas_lidas.append(d)
    if fora:
        raise CheckError("veredito fora do vocabulario: " + "; ".join(fora))
    return linhas_lidas


def mede() -> dict:
    corridas = le_tsv()

    # o que existe em disco
    disco = sorted(
        p.stem for p in ROTEIROS.glob("golden-*.txt")
        if not p.name.endswith(".port.txt")
        and (ROTEIROS / f"{p.stem}.port.txt").exists())

    por = {}          # (roteiro, rom, modo) -> dict
    for c in corridas:
        por[(c["roteiro"], c["rom"], c["modo"])] = c

    roms_medidas = sorted({c["rom"] for c in corridas}, key=ROMS.index)

    # guarda 1: golden sem controle na mesma ROM
    orfaos = sorted(
        f"{r}/{rom}" for (r, rom, m) in por
        if m == "golden" and (r, rom, "controle") not in por)
    if orfaos:
        raise CheckError(
            "golden registrado sem o controle da mesma ROM: "
            + ", ".join(orfaos)
            + ". O controle vem ANTES do teste -- sem ele, verde e vermelho "
              "nao significam nada.")

    # guarda 2: roteiro em disco e ausente do TSV
    medidos = {c["roteiro"] for c in corridas}
    faltando = [r for r in disco if r not in medidos]
    if faltando:
        raise CheckError(
            "roteiro com par em disco e ausente da bateria: "
            + ", ".join(faltando)
            + ". Rode o golden_suite.sh de novo -- tabela que nao acompanha a "
              "bateria envelhece sozinha.")

    # e o inverso: TSV citando roteiro que nao existe mais
    sobrando = sorted(medidos - set(disco))
    if sobrando:
        raise CheckError(
            "TSV cita roteiro sem par em disco: " + ", ".join(sobrando))

    conta = {v: 0 for v in VEREDITOS}
    for c in corridas:
        conta[c["veredito"]] += 1

    segundos = sum(int(c["segundos"]) for c in corridas)

    return {
        "corridas": corridas,
        "por": por,
        "disco": disco,
        "roms": roms_medidas,
        "conta": conta,
        "segundos": segundos,
        "data": max(c["data"] for c in corridas),
    }


def gera(m: dict) -> str:
    L: list[str] = []
    a = L.append
    por, disco, roms = m["por"], m["disco"], m["roms"]

    a("# `re/golden.md` — a bateria golden completa")
    a("")
    a("**GERADO — não editar à mão.** A correção entra no gerador, ou na")
    a("bateria que escreve o TSV, e o arquivo é regerado:")
    a("")
    a("```sh")
    a("bash wte/tools/golden_suite.sh          # roda e escreve o re/golden.tsv")
    a("python3 wte/tools/check_golden.py       # regera este arquivo")
    a("python3 wte/tools/check_golden.py --check")
    a("```")
    a("")
    a("Produto da [WTE-TASK-34](../../docs/tasks/34-bateria-golden-completa.md).")
    a(f"Fonte: [`golden.tsv`](golden.tsv), {len(m['corridas'])} corrida(s)")
    a(f"registrada(s), a mais recente de {m['data']}.")
    a("**Todo número daqui saiu do script.**")
    a("")

    a("## O critério, e o que ele custou para virar mensurável")
    a("")
    a("> Para cada operação que grava, `wte.exe` sob Wine e o app Lazarus")
    a("> produzem **imagem byte-idêntica** a partir da mesma imagem de")
    a("> entrada, nas duas ROMs.")
    a("")
    japo = [c for c in m["corridas"] if c["rom"] == "japonesa"]
    euro = [c for c in m["corridas"] if c["rom"] == "europeia"]
    jp_ok = sum(1 for c in japo if c["veredito"] == "PASSOU")
    eu_sem = sum(1 for c in euro if c["veredito"] == "SEM_ORACULO")
    a(f"**{jp_ok} de {len(japo)} corridas verdes na japonesa.** Na europeia,")
    a(f"{eu_sem} de {len(euro)} não têm oráculo — ver a seção das duas ROMs.")
    a("")

    a("## Operação × ROM × resultado")
    a("")
    a("Cada roteiro roda **duas vezes por ROM**: `controle` (oráculo contra")
    a("oráculo, que prova que o par roteiro+imagem é determinístico) e")
    a("`golden` (oráculo contra o app Lazarus). A célula traz os dois, nessa")
    a("ordem, porque é nessa ordem que eles valem.")
    a("")
    cab = "| Roteiro |" + "".join(f" {r} |" for r in roms)
    a(cab)
    a("|---|" + "---|" * len(roms))
    for r in disco:
        cel = []
        for rom in roms:
            c = por.get((r, rom, "controle"), {}).get("veredito", "—")
            g = por.get((r, rom, "golden"), {}).get("veredito", "—")
            cel.append(f" {c} / {g} |")
        a(f"| [{r}](../tests/roteiros/{r}.txt) |" + "".join(cel))
    a("")
    a("**Nenhuma célula vazia** — era o quarto critério da task, e a guarda 2")
    a("do gerador o mecaniza: roteiro com par em disco e ausente do TSV")
    a("**aborta** a geração.")
    a("")

    a("## Distribuição dos vereditos")
    a("")
    a("| Veredito | Corridas |")
    a("|---|---:|")
    for v in VEREDITOS:
        a(f"| `{v}` | {m['conta'][v]} |")
    a(f"| **total** | **{len(m['corridas'])}** |")
    a("")
    a("`REPROVOU` é a única que acusa o port. `SEM_ORACULO` diz que o")
    a("`wte.exe` morreu com `c0000005` e gravou menos; `NAO_APLICAVEL` diz que")
    a("o `controle` daquele par não passou, e um `golden` ali seria ilegível.")
    a("")

    a("## As duas combinações que só aparecem nesta fase")
    a("")
    a("As tasks 27, 31 e 32 rodaram golden **por operação**, isoladas. Estas")
    a("duas exercitam o que teste isolado não alcança, e as duas nasceram")
    a("aqui:")
    a("")
    a("| Roteiro | O que só ele exercita | Japonesa |")
    a("|---|---|---|")
    for r, desc in CATEGORIA.items():
        if r not in disco:
            continue
        g = por.get((r, "japonesa", "golden"), {}).get("veredito", "—")
        c = por.get((r, "japonesa", "controle"), {}).get("veredito", "—")
        a(f"| [{r}](../tests/roteiros/{r}.txt) | {desc} | {c} / {g} |")
    a("")
    a("**A edição múltipla** põe duas edições de naturezas diferentes na mesma")
    a("sessão — uma barra num `TTrackBar` e os três nomes em `TEdit` — e grava")
    a("pelos dois botões sem recarregar o time. É a classe de bug que teste")
    a("isolado não pega: se o original recalculasse algo ao trocar de contexto")
    a("de edição, a segunda gravação sairia de um estado que nenhum gate da")
    a("fase 4 chegou a produzir.")
    a("")
    a("**A gravação dupla** grava a tática duas vezes no mesmo time, com")
    a("recarga entre elas. A tática é a escolha certa porque é a gravação que")
    a("carrega `OFS_KICKER`: o `newWe2002` registra que o editor original")
    a("**não é idempotente** — `Load`+`Save` troca os dois primeiros cobradores")
    a("de cada clube de Master League, e gravar duas vezes volta ao início. Se")
    a("o app Lazarus não reproduzisse o vaivém, a segunda gravação divergiria")
    a("mesmo com a primeira byte-idêntica.")
    a("")
    a("**E nenhum dos dois prova sozinho que o estímulo aconteceu.** É a lição")
    a("1 da quarta passagem da")
    a("[WTE-TASK-31](../../docs/tasks/31-fechamento-fase-4.md): se os dois")
    a("lados não fizerem nada, os dois concordam. O terceiro ponto de cada um")
    a("é o par que grava **uma** vez pelo mesmo caminho —")
    a("`golden-04-barras-editada` e `golden-05-nomes` para o primeiro,")
    a("`golden-17-tatica` para o segundo.")
    a("")

    a("## As duas ROMs, e por que a resposta não é simétrica")
    a("")
    a("O critério diz \"nas duas ROMs\", e esta bateria **rodou as duas** em vez")
    a("de decidir por prosa que uma não valia. O resultado da europeia é")
    a("medida, não suposição:")
    a("")
    a("| ROM | Corridas | `PASSOU` | `SEM_ORACULO` | `NAO_APLICAVEL` | `REPROVOU` |")
    a("|---|---:|---:|---:|---:|---:|")
    for rom in roms:
        cs = [c for c in m["corridas"] if c["rom"] == rom]
        def n(v: str) -> int:
            return sum(1 for c in cs if c["veredito"] == v)
        a(f"| {rom} | {len(cs)} | {n('PASSOU')} | {n('SEM_ORACULO')} "
          f"| {n('NAO_APLICAVEL')} | {n('REPROVOU')} |")
    a("")
    a("Com a europeia o `wte.exe` morre ao trocar de time: a carga do time")
    a("escreve além do fim da tabela de `0x00433580` e deixa `0x00010001` onde")
    a("estaria o ponteiro de `dorsal1`, que passa no teste de `nil` e não é")
    a("objeto nenhum ([`crash-causa.md`](crash-causa.md)). **Oráculo que morre")
    a("no meio grava menos**, e nenhuma das duas palavras usuais serve: verde")
    a("seria mentira, e vermelho acusaria o port por bytes que o original nunca")
    a("chegou a escrever. Por isso o vocabulário tem `SEM_ORACULO`.")
    a("")
    a("**O que isso fecha, e o que não fecha.** Fecha a pergunta que a")
    a("WTE-TASK-31 deixou nomeada — *a europeia é da 34* —, e a resposta é que")
    a("ela foi medida, roteiro a roteiro, em vez de dispensada em bloco por uma")
    a("medição de 2026-08-18 feita sobre um roteiro só. Não fecha a paridade na")
    a("europeia, que **continua sem oráculo**: enquanto o `wte.exe` cair ali,")
    a("nenhuma bateria pode julgar o port contra ele naquela imagem.")
    a("")

    a("## Custo")
    a("")
    horas = m["segundos"] / 3600
    a(f"**{m['segundos']} segundos de relógio** ({horas:.1f} h) nas")
    a(f"{len(m['corridas'])} corridas. Cada uma faz duas cópias da imagem e as")
    a("apaga no fim: ~586 MB de temporário com a japonesa, ~950 MB com a")
    a("europeia. **`roms/` nunca é alvo** — a guarda 4 do `golden_check.sh`.")
    a("")
    a("Não roda em CI, e o plano já registra isso: precisa de Wine, do `:98` e")
    a("do binário do Obocaman, que é gitignored.")
    a("")
    return "\n".join(L) + "\n"


def main(argv: list[str]) -> int:
    checando = "--check" in argv
    try:
        texto = gera(mede())
    except CheckError as e:
        print(f"check_golden: {e}", file=sys.stderr)
        return 2
    rel = OUT.relative_to(ROOT)
    if checando:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texto:
            print(f"check_golden: {rel}: DIVERGE do gerador", file=sys.stderr)
            return 2
        print(f"check_golden: {rel}: ok")
        return 0
    OUT.write_text(texto, encoding="utf-8")
    print(f"check_golden: {rel}: {len(texto)} B")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
