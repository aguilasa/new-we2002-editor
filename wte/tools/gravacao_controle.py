#!/usr/bin/env python3
"""Escreve `wte/re/gravacao-controle.md` -- o diff de CONTROLE da gravacao.

WTE-TASK-27. O enunciado da task manda medir, antes de qualquer implementacao,
**o que muda de graca**: carregar um time e mandar gravar sem tocar em campo
nenhum. Sem essa linha de base toda divergencia medida depois vem contaminada,
porque nem o formato nem o editor original sao idempotentes.

## Por que isto e gerador, e nao prosa

Os offsets desta medicao sao a secao `Bytes tocados` das seis specs do grupo, e
seriam copiados a mao de dois TSV. Numero copiado a mao envelhece calado -- e a
regra deste repositorio e que todo numero em doc venha de ferramenta. Aqui a
fonte e a evidencia ja versionada:

- [`wte/re/io-medido.tsv`](../re/io-medido.tsv) -- o trace de syscall, que diz
  o que o app **enderecou**;
- [`wte/re/cmp-medido.tsv`](../re/cmp-medido.tsv) -- o `cmp`, que diz o que
  efetivamente **mudou**.

As duas nao medem a mesma coisa, e a diferenca entre elas e o achado principal
desta corrida: o editor grava 51 bytes e so 21 sao diferentes do que ja estava
la. `cmp` sozinho nao distingue "nao gravou" de "gravou igual".

Uso:
    python3 wte/tools/gravacao_controle.py
    python3 wte/tools/gravacao_controle.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IO_TSV = ROOT / "wte" / "re" / "io-medido.tsv"
CMP_TSV = ROOT / "wte" / "re" / "cmp-medido.tsv"
OFFSETS_HPP = ROOT / "src" / "core" / "include" / "we2002" / "Offsets.hpp"
OUT_MD = ROOT / "wte" / "re" / "gravacao-controle.md"

SESSAO = "27-gravacao-controle"
SONDA_SEM = "27-descarga-sem"      # clica as barras e morre  -> zero byte
SONDA_COM = "27-descarga-com"      # clica e troca de time    -> 5 bytes
SESSAO_MCR2ISO = "27-mcr2iso"      # o import de .mcr da WTE-TASK-28
SETOR = 2352

# As acoes do roteiro que sao GRAVACAO. O arranque e a troca de time entram no
# quadro tambem, mas como linha de base -- elas nao sao do grupo da task, e o
# que elas gravam ja tem dono na WTE-TASK-25.
GRAVACOES = ("GRAVA_BARRAS", "GRAVA_NOMES")

# A NAO-IDEMPOTENCIA, E DE QUEM ELA E -- medido pela CORR-WTE-109 em 2026-08-25.
#
# TABELA A MAO, E COM GUARDA, pela mesma razao do `TERCEIRO_PONTO` do
# `check_golden.py`: o numero sai de corrida de golden, que precisa do `:98`, do
# Wine e de ~600 MB de temporario, e nao se remede em `--check`. O que o
# `test_gravacao_controle.py` cobra e a COERENCIA -- que a prosa gerada nao
# volte a atribuir ao `wte.exe` um comportamento que a tabela diz ser do outro
# binario.
#
# A frase que estava aqui -- *"o `Load`+`Save` do editor original nao e
# idempotente"* -- e verdadeira no `newWe2002`, onde o oraculo E o `ed.exe`.
# Migrada para este projeto ela trocou de sujeito sem trocar de palavras: aqui
# "o original" e o `wte.exe` do Obocaman.
#
# E o `wte.exe` nao tem um ciclo `Load`+`Save` de banco inteiro -- ele grava por
# area. Dos 17 caminhos de gravacao, DOIS tocam `OFS_KICKER`, e os dois foram
# medidos gravando duas vezes seguidas: nenhum troca o par.
IDEMPOTENCIA = {
    "data": "2026-08-25",
    "caminhos_que_tocam_kicker": 2,
    # o ` Accept` da tela de tatica -- CORR-WTE-104, time 5
    "tatica_uma_x_duas": 0,
    "tatica_virgem_x_uma": 11962,
    # o import de `.mcr` -- CORR-WTE-109, time 3, duas importacoes encadeadas
    "mcr2iso_uma_x_duas": 0,
    "mcr2iso_virgem_x_uma": 12419,
    # onde a troca SERIA visivel, depois da importacao
    "times_com_par_desigual": 41,
    "times_que_trocaram": 0,
}


def _curto(caminho: Path) -> Path:
    # `is_relative_to` porque o teste aponta as fontes para um diretorio
    # temporario; fora dele, o caminho relativo e o que se quer ler.
    return caminho.relative_to(ROOT) if caminho.is_relative_to(ROOT) else caminho


def ler_tsv(caminho: Path) -> list[dict[str, str]]:
    if not caminho.exists():
        raise SystemExit(f"gravacao_controle: falta {_curto(caminho)}")
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    return [dict(zip(cab, l.split("\t"))) for l in linhas[1:] if l.strip()]


def ler_offsets() -> dict[str, int]:
    txt = OFFSETS_HPP.read_text(encoding="utf-8")
    return {m.group(1): int(m.group(2)) for m in re.finditer(
        r"inline\s+constexpr\s+Offset\s+(OFS_\w+)\s*=\s*(\d+)\s*;", txt)}


def rotulo(pos: int, conhecidos: dict[str, int]) -> str:
    """`OFS_*` imediatamente anterior, com o deslocamento.

    E o mesmo criterio do `golden_compare.py` do newWe2002: nomear a regiao
    pelo offset conhecido que a precede. Nao afirma semantica -- afirma
    POSICAO, que e o que uma faixa prova.
    """
    antes = [(v, k) for k, v in conhecidos.items() if v <= pos]
    if not antes:
        return "antes do primeiro offset"
    v, k = max(antes)
    return f"{k}+{pos - v}" if pos != v else k


def faixas_da_sessao() -> tuple[list[dict], list[dict]]:
    io = [r for r in ler_tsv(IO_TSV) if r["sessao"] == SESSAO]
    cmp_ = [r for r in ler_tsv(CMP_TSV) if r["sessao"] == SESSAO]
    if not io:
        raise SystemExit(
            f"gravacao_controle: a sessao `{SESSAO}` nao esta em "
            f"{_curto(IO_TSV)} -- rode o diff_dirigido.sh sobre "
            f"wte/tests/roteiros/golden-02-gravacao.txt")
    return io, cmp_


PAYLOAD_INICIO = 24
PAYLOAD_FIM = 24 + 2048 - 1          # 2071 -- o SETOR ja mora acima


def sessoes_da_task() -> list[str]:
    """As sessoes do `cmp-medido.tsv` que sao desta task.

    O prefixo `27-` e a convencao de nome das sondas e do controle. Deduzir
    dali em vez de listar a mao e o que faz uma sonda nova entrar sozinha na
    conferencia -- listar a mao seria a forma conhecida de a conta envelhecer
    calada."""
    vistas = [r["sessao"] for r in ler_tsv(CMP_TSV) if r["sessao"].startswith("27-")]
    return sorted(set(vistas))


def fora_do_payload() -> list[tuple[str, int, int]]:
    """Faixas medidas que tocam byte de EDC/ECC ou de cabecalho de setor.

    Setor MODE2/2352 = 24 de cabecalho + 2048 de dados + 280 de EDC/ECC. O
    editor original NAO recalcula EDC/ECC, entao preservar e o comportamento
    correto -- e preservar acontece de graca enquanto toda escrita cair dentro
    dos 2048. Esta e a conta que transforma "presumido" em "medido", e ela nao
    precisa de corrida nova: sai do TSV que as corridas ja versionaram.

    Devolve (sessao, inicio, fim) de cada faixa que sai do payload."""
    ruim: list[tuple[str, int, int]] = []
    alvo = set(sessoes_da_task())
    for r in ler_tsv(CMP_TSV):
        if r["sessao"] not in alvo:
            continue
        ini, fim = int(r["inicio"]), int(r["fim"])
        for pos in (ini, fim):
            if not (PAYLOAD_INICIO <= pos % SETOR <= PAYLOAD_FIM):
                ruim.append((r["sessao"], ini, fim))
                break
    return ruim


def faixas_comuns() -> set[tuple[str, str]]:
    """As faixas que aparecem em TODAS as sessoes da task.

    Sao a injecao da abertura da imagem: sete setores que o app reescreve na
    carga, mais dois bytes soltos. Elas nao pertencem a acao nenhuma do
    roteiro, e por isso sao descontadas antes de se falar do que um handler
    especifico grava."""
    sess = sessoes_da_task()
    linhas = ler_tsv(CMP_TSV)
    por = {s: {(r["inicio"], r["fim"]) for r in linhas if r["sessao"] == s}
           for s in sess}
    return set.intersection(*por.values()) if por else set()


def faixas_proprias(sessao: str) -> list[dict[str, str]]:
    """As faixas de `sessao` descontada a injecao da abertura."""
    comuns = faixas_comuns()
    return [r for r in ler_tsv(CMP_TSV)
            if r["sessao"] == sessao and (r["inicio"], r["fim"]) not in comuns]


def payload_inteiro(sessao: str) -> list[dict[str, str]]:
    """As faixas de `sessao` que sao o payload INTEIRO de um setor.

    2048 bytes comecando no 24: de borda a borda da regiao de dados, sem tocar
    os 24 de cabecalho nem os 280 de EDC/ECC."""
    return [r for r in ler_tsv(CMP_TSV)
            if r["sessao"] == sessao
            and int(r["tamanho"]) == 2048
            and int(r["byte_no_setor"]) == PAYLOAD_INICIO]


def gerar() -> str:
    io, cmp_ = faixas_da_sessao()
    conhecidos = ler_offsets()
    imagem = io[0]["imagem"]
    mudou = [(int(r["inicio"]), int(r["fim"])) for r in cmp_]

    L: list[str] = []
    w = L.append
    w("# Diff de controle da gravação — gravar sem editar nada")
    w("")
    w("**Arquivo gerado.** Não edite à mão: mexa em")
    w("[`../tools/gravacao_controle.py`](../tools/gravacao_controle.py) e")
    w("reexecute. `make -C wte check` roda o `--check`.")
    w("")
    w("Produto da [WTE-TASK-27](../../docs/tasks/concluidos/27-handlers-de-gravacao.md).")
    w("A medição é a sessão `" + SESSAO + "` de")
    w("[`../tools/diff_dirigido.sh`](../tools/diff_dirigido.sh) sobre")
    w(f"`roms/{imagem}`, com o roteiro")
    w("[`../tests/roteiros/golden-02-gravacao.txt`]"
      "(../tests/roteiros/golden-02-gravacao.txt).")
    w("")
    w("## Por que ele vem antes de implementar qualquer coisa")
    w("")
    w("Carregar um time e mandar gravar **sem tocar em campo nenhum** já muda")
    w("bytes. Sem essa linha de base, toda divergência medida depois vem")
    w("contaminada: o `Save` do formato reconstrói dado a partir de link.")
    w("")
    i = IDEMPOTENCIA
    w("**A segunda armadilha que este parágrafo citava não é deste editor.**")
    w("Ele dizia que o `Load`+`Save` *\"do editor original\"* não é idempotente")
    w("— troca os dois primeiros cobradores de cada clube de ML. A frase é")
    w("verdadeira no [`newWe2002`](../../docs/PLAN-LINUX.md), onde o oráculo é")
    w("o **`ed.exe`**; migrada para cá ela trocou de sujeito sem trocar de")
    w("palavras, porque neste projeto *\"o original\"* é o `wte.exe` do")
    w("Obocaman.")
    w("")
    w(f"Medido em {i['data']} ([CORR-WTE-109](../../docs/tasks/concluidos/CORR-WTE-109.md)):")
    w("o `wte.exe` **não tem** ciclo `Load`+`Save` de banco inteiro — ele grava")
    w("por área. Dos 17 caminhos de gravação,")
    w(f"**{i['caminhos_que_tocam_kicker']}** tocam `OFS_KICKER`, e os dois")
    w("gravam duas vezes seguidas sem trocar o par:")
    w("")
    w("| Caminho | uma × duas gravações | a gravação aconteceu |")
    w("|---|---:|---:|")
    w(f"| ` Accept` da tática | **{i['tatica_uma_x_duas']}** B "
      f"| {i['tatica_virgem_x_uma']} B contra a ROM virgem |")
    w(f"| import de `.mcr` | **{i['mcr2iso_uma_x_duas']}** B "
      f"| {i['mcr2iso_virgem_x_uma']} B contra a ROM virgem |")
    w("")
    w("**E o zero não é cego.** Depois da importação,")
    w(f"**{i['times_com_par_desigual']}** dos 96 times têm")
    w("`cobrador[0] != cobrador[1]` — é neles que uma troca apareceria. Na")
    w(f"segunda gravação, **{i['times_que_trocaram']}** trocaram.")
    w("")
    w("## O que cada ação endereçou, e o que de fato mudou")
    w("")
    w("As duas colunas de contagem não medem a mesma coisa. `escreveu` é")
    w("syscall — o que o app mandou para o arquivo. `mudou` é `cmp` — o que")
    w("ficou diferente do que já estava lá. A diferença entre elas é gravação")
    w("de valor igual, que nenhum `cmp` enxerga.")
    w("")
    w("| ação | faixas de escrita | bytes escritos | bytes que mudaram |")
    w("| --- | ---: | ---: | ---: |")
    for acao in dict.fromkeys(r["acao"] for r in io):
        escritas = [r for r in io if r["acao"] == acao and r["op"] == "W"]
        n_bytes = sum(int(r["tamanho"]) for r in escritas)
        dentro = 0
        for r in escritas:
            a, b = int(r["inicio"]), int(r["fim"])
            for i, j in mudou:
                if i >= a and j <= b:
                    dentro += j - i + 1
        w(f"| `{acao}` | {len(escritas)} | {n_bytes} | {dentro} |")
    w("")

    for acao in GRAVACOES:
        escritas = [r for r in io if r["acao"] == acao and r["op"] == "W"]
        w(f"### `{acao}`")
        w("")
        if not escritas:
            w("**Não tocou a imagem.** Nenhuma syscall de escrita entre esta")
            w("marca e a seguinte. Isso é resultado, não ausência de medida: a")
            w("linha existe no TSV com `op` = `.` justamente para distinguir")
            w("\"não gravou\" de \"não foi exercitado\".")
            w("")
            continue
        w("| offset | tamanho | setor | região | mudou |")
        w("| ---: | ---: | ---: | --- | ---: |")
        for r in sorted(escritas, key=lambda x: int(x["inicio"])):
            a, b = int(r["inicio"]), int(r["fim"])
            d = sum(j - i + 1 for i, j in mudou if i >= a and j <= b)
            w(f"| {a} | {r['tamanho']} | {a // SETOR} | "
              f"`{rotulo(a, conhecidos)}` | {d} |")
        w("")

    w("## O clique não grava: quem grava é o `fseek` seguinte")
    w("")
    w("O `wte.exe` escreve pela saída **bufferizada** do runtime C. Clicar o")
    w("botão não produz syscall nenhuma: os bytes ficam no buffer, e só vão ao")
    w("arquivo quando algo depois procura noutro ponto do mesmo arquivo —")
    w("`fseek` esvazia a saída pendente antes de mover.")
    w("")
    w("O par de sondas abaixo mede isso com **uma** variável de diferença. Os")
    w("dois roteiros são iguais linha a linha; o `-com` tem quatro linhas a")
    w("mais, que trocam de time depois do clique.")
    w("")
    w("| sonda | roteiro | escritas na imagem |")
    w("| --- | --- | ---: |")
    for nome, arq in ((SONDA_SEM, "27-descarga-sem.txt"),
                      (SONDA_COM, "27-descarga-com.txt")):
        n = len([r for r in ler_tsv(IO_TSV)
                 if r["sessao"] == nome and r["op"] == "W"
                 and r["acao"] == "GRAVA_BARRAS"])
        w(f"| `{nome}` | [`../tests/roteiros/{arq}`]"
          f"(../tests/roteiros/{arq}) | {n} |")
    w("")
    w("Duas consequências, e as duas doem:")
    w("")
    w("- **roteiro que termina numa gravação mede um oráculo truncado.** O")
    w("  harness encerra com `wineserver -k`, e o que estiver no buffer se")
    w("  perde. Se o port gravar direto, o gate acusaria o *port* por bytes")
    w("  que o oráculo nunca chegou a escrever;")
    w("- **a marca de corte tem de vir depois da descarga.** Na primeira")
    w("  medição desta passagem ela não vinha, e os 5 bytes das barras")
    w("  apareceram creditados à ação seguinte, a dos nomes — atribuição")
    w("  errada, em silêncio, num TSV que parecia medido.")
    w("")
    w("Por isso cada bloco do roteiro termina com uma troca de time, e só")
    w("então a marca.")
    w("")
    w("## A gravação sem edição **não** é neutra")
    w("")
    w("Ela é destrutiva nesta imagem, e o motivo é o alfabeto. A ROM japonesa")
    w("guarda o nome do time em duas escritas: latina no primeiro bloco e")
    w("katakana de meia largura nos demais. O editor lê o campo da tela — que")
    w("veio do bloco latino — e o grava em **todos** os blocos. Os três")
    w("trechos que mudam de graça são katakana sendo substituído por ASCII.")
    w("")
    w("Consequência para o port: reproduzir isso é obrigação, não escolha. Um")
    w("port que \"preservasse\" o katakana passaria a divergir do oráculo em")
    w("toda gravação de nomes, e o golden acusaria a gravação por um defeito")
    w("que seria de fidelidade.")
    w("")
    w("## O mesmo ordinal em blocos de ordenação diferente")
    w("")
    w("Os blocos de nome não estão todos na mesma ordem, e o editor escreve o")
    w("time selecionado no **mesmo ordinal** de todos. Medido nesta corrida,")
    w("com dois ordinais consecutivos:")
    w("")
    w("| bloco | ordinal *k* | ordinal *k*+1 |")
    w("| --- | --- | --- |")
    w("| `OFS_TEAM_NAME_1_A` (12 B) | `SCOTLAND` | `IRELAND` |")
    w("| `OFS_TEAM_NAME_6_B` (8 B) | `ｶﾒﾙｰﾝ` | `ﾆｲｼﾞｪﾘｱ` |")
    w("")
    w("Gravar \"Scotland\" substituiu, no último bloco, o registro que")
    w("guardava \"Camarões\". Isso é o comportamento do original e o port o")
    w("reproduz — o que **não** se pode é descobrir isso depois, olhando um")
    w("diff, e chamar de bug do port.")
    w("")
    w("## A ROM europeia não hospeda este controle")
    w("")
    w("Rodado nesta mesma passagem, o roteiro acima sobre")
    w("`roms/golden-european-deluxe.bin` morre na troca de time: a caixa de")
    w("confirmação da gravação nunca aparece, e o log do Wine traz **49.749**")
    w("violações de acesso — o mesmo número que a")
    w("[CORR-WTE-044](../../docs/tasks/concluidos/CORR-WTE-044.md) já tinha medido, e")
    w("reproduzido aqui com")
    w("`grep -cE 'code=c0000005' <log>`. O `golden_run_wte.sh` reprova com")
    w("código 4 exatamente por isso: oráculo que morreu no meio grava menos,")
    w("e o diff sairia menor.")
    w("")
    w("O critério \"nas duas ROMs\" da task herda esse limite. Ele não é")
    w("omissão desta passagem — é a mesma restrição que já vale para o gate")
    w("desde a WTE-TASK-22.")
    w("")
    w("## EDC/ECC preservado, e a conta que prova isso")
    w("")
    w("Setor MODE2/2352 são 24 bytes de cabeçalho, 2048 de dados e 280 de")
    w("EDC/ECC. O editor original **não recalcula** EDC/ECC, então preservar")
    w("é o comportamento correto — e preservar sai de graça enquanto toda")
    w("escrita cair dentro dos 2048. O que transforma isso de presumido em")
    w("medido não é corrida nova: é uma conta sobre as faixas que as corridas")
    w("já versionaram.")
    w("")
    sess = sessoes_da_task()
    ruim = fora_do_payload()
    total = sum(1 for r in ler_tsv(CMP_TSV) if r["sessao"] in set(sess))
    w(f"Conferidas **{total}** faixas do `cmp`, em {len(sess)} sessões desta")
    w("task:")
    w("")
    for nome in sess:
        n_faixas = sum(1 for r in ler_tsv(CMP_TSV) if r["sessao"] == nome)
        w(f"- `{nome}` — {n_faixas} faixa(s)")
    w("")
    if ruim:
        w("**Faixa fora do payload — EDC/ECC ALCANÇADO:**")
        w("")
        for nome, ini, fim in ruim:
            w(f"- `{nome}`: {ini}..{fim}")
    else:
        w(f"**Nenhuma toca byte de EDC/ECC nem de cabeçalho.** Cada extremo cai")
        w(f"entre {PAYLOAD_INICIO} e {PAYLOAD_FIM} do próprio setor, que é a")
        w("região de dados de usuário. Os 280 bytes de correção saem intactos")
        w("das quatro gravações desta task.")
    w("")
    w("A conta enumera as sessões pelo prefixo `27-` em vez de listá-las: sonda")
    w("nova entra sozinha, e listar à mão seria a forma conhecida de o número")
    w("envelhecer calado.")
    w("")
    mcr2iso = faixas_proprias(SESSAO_MCR2ISO)
    inteiras = payload_inteiro(SESSAO_MCR2ISO)
    if not mcr2iso:
        # Sem a sessao no TSV nao ha o que contar, e afirmar assim mesmo e o
        # defeito que a CORR-WTE-072 fechou.
        w("**O alcance da conta fora desta task não foi medido nesta rodada:**")
        w(f"a sessão `{SESSAO_MCR2ISO}` não está no `cmp-medido.tsv` lido aqui.")
        return "\n".join(L) + "\n"
    w("**A conta alcança o projeto inteiro, e isso foi medido depois.** O")
    w("enunciado da [WTE-TASK-28](../../docs/tasks/concluidos/28-import-de-mcr.md)")
    w("previa que o `boton_mcr2isoClick` escreveria **setor inteiro**, e que")
    w("ali preservar EDC/ECC deixaria de ser consequência e viraria decisão.")
    w(f"Medido, não é: a sessão `{SESSAO_MCR2ISO}` já está entre as contadas")
    w(f"acima, e as {len(mcr2iso)} faixas próprias do handler cabem no payload")
    w(f"— a maior tem {max(int(r['tamanho']) for r in mcr2iso)} bytes.")
    w("")
    w("Escrita de payload **inteiro** existe e já está contada, mas não é do")
    w(f"handler: são as {len(inteiras)} faixas de 2048 bytes que a injeção da")
    w(f"abertura deixa, de {PAYLOAD_INICIO} a {PAYLOAD_FIM}, borda a borda.")
    w("Elas também não tocam os 280 — o payload inteiro ainda é payload.")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="nao escreve; sai 2 se a saida divergir do commitado")
    args = ap.parse_args(argv)
    texto = gerar()
    rel = OUT_MD.relative_to(ROOT)
    if args.check:
        if not OUT_MD.exists() or OUT_MD.read_text(encoding="utf-8") != texto:
            print(f"gravacao_controle: {rel}: DIVERGE do gerador", file=sys.stderr)
            return 2
        print(f"gravacao_controle: {rel}: ok")
        return 0
    OUT_MD.write_text(texto, encoding="utf-8")
    print(f"gravacao_controle: {rel}: {len(texto)} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
