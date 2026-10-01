---
id: CORR-KITS-025
---

# CORR-KITS-025 — Correct the club 63 empty in both fields claim in the task Notes

Origin: [KITS-TASK-13](/docs/tasks/kits/13-nomes-dos-times.md)

## Problem

As Notas da KITS-TASK-13 dizem que, no disco japonês, "o clube 63 vem vazio nos dois campos — `we2002_golden_tool names roms/japanese-shift-jis.bin` mostra `63` seguido de dois campos vazios". Na HEAD esse dump não tem campo vazio em nenhuma das 95 linhas, e a linha do 63 traz katakana e `ARAGON`. A frase é parte da justificativa para usar a tabela no disco japonês.

## Evidência

```text
$ grep -n "clube 63 vem vazio" docs/tasks/kits/13-nomes-dos-times.md
34:- **Por que a tabela no japonês:** lá o `mixed_case_name` é katakana de meia largura em todo time, e o clube 63 vem vazio nos dois campos — ...
$ PATH="<mingw64/bin>:$PATH" $TEMP/build-kits08/tests/we2002_golden_tool.exe names roms/japanese-shift-jis.bin | awk -F'\t' '$2=="" || $3=="" {n++} END{print "empty-field lines:", n+0, "total:", NR}'
empty-field lines: 0 total: 95
$ sed -n '64p' $TEMP/jp_core.tsv | od -c
... 6 3 \t 261 327 272 336 335 \t A R A G O N \n
```

O build estava em dia (`cmake --build $TEMP/build-kits08 --target we2002_golden_tool` → "ninja: no work to do.").

## Root cause

Hipótese: a frase foi escrita a partir da primeira versão do verbo `names`, a de 64 vagas que as próprias Notas dizem ter sido corrigida — nela o índice 63 era a vaga sobrando —, e não foi remedida depois do conserto.

## Fix

Em `docs/tasks/kits/13-nomes-dos-times.md` (Notas, "Por que a tabela no japonês"), tirar a cláusula do "clube 63 vazio" ou trocá-la por uma medição feita na HEAD. A outra metade se reproduz: 0 dos 95 nomes em caixa mista são só ASCII.

## Arquivos a criar ou modificar

- `docs/tasks/kits/13-nomes-dos-times.md`

## Verificação

```text
$ grep -n "clube 63 vem vazio" docs/tasks/kits/13-nomes-dos-times.md
```

Hoje imprime a linha 34; depois do conserto, nada.

## Log de Execução

### Reprodução (HEAD `eee0e6fd`)

O `rite reproduce` rodou o `golden_tool` com o `PATH` de placeholder da Evidência e ele não imprimiu nada (`total: 0`); refeito com o `bin` do MinGW no `PATH` (`$M` = `.../BrechtSanders.WinLibs.POSIX.UCRT_.../mingw64/bin`):

```text
$ PATH="$M:$PATH" $TEMP/build-kits08/tests/we2002_golden_tool.exe names roms/japanese-shift-jis.bin > jp.tsv; echo exit $?
exit 0
$ awk -F'\t' '$2=="" || $3=="" {n++} END{print "empty-field lines:", n+0, "total:", NR}' jp.tsv
empty-field lines: 0 total: 95
$ sed -n 64p jp.tsv | od -c | head -1
0000000   6   3  \t 261 327 272 336 335  \t   A   R   A   G   O   N  \n
```

REPRODUCED: nenhum campo vazio, e o 63 é `ARAGON`.

### O que foi feito

Notas da KITS-TASK-13, "Por que a tabela no japonês": a cláusula do clube 63 saiu, e no lugar ficou o que a mesma corrida mede — 0 dos 95 nomes em caixa mista são só ASCII, nenhum campo vazio —, com a nota do que a frase dizia antes e de onde veio.

```text
$ python -c "...rows=[l.split('\t') for l in jp.tsv]; print(len(rows), sum(all(ord(c)<128 for c in r[1]) for r in rows), sum(r[1]=='' for r in rows))"
rows 95 col2 ascii-only 0 col2 empty 0
```

### Verificação

```text
$ grep -n "clube 63 vem vazio" docs/tasks/kits/13-nomes-dos-times.md
(sem saída, exit 1)
```
