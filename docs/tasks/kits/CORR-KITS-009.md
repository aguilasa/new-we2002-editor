---
id: CORR-KITS-009
---

# CORR-KITS-009 — Paste the uv --negative transcript whole and give the survey md5

Origin: [KITS-TASK-04](/docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md)

## Problem

A transcrição do `uv --negative` no Log da KITS-TASK-04 mostra 5 linhas de expectativa sob "7 of 7 expectations held". As duas linhas "rects move -2 px in x" (215 de 215 e 429 de 429), que são a conferência do critério "os retângulos acompanham", ficaram de fora. O Log também diz que o `survey` sai "com o mesmo md5 das tasks anteriores" sem dar o valor, e nenhuma task anterior o registra (a 03 diz só "md5 da saída igual"). É a mesma classe da CORR-KITS-006.

## Evidência

```text
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --negative
uniform moved to (577,256) moved 2  figure 0  rects move -2 px in x    237 mapped -> 215 of 215 still mapped moved  held
uniform moved to (577,256) moved 2  figure 1  rects move -2 px in x    429 mapped -> 429 of 429 still mapped moved  held
$ grep -c "rects move -2 px in x" docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md
0
$ python tools/kits/cli.py survey roms/japanese-shift-jis.bin | md5sum
c2ec025a808afd4ffbe4c39fca0d991a *-
$ grep -c c2ec025a docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md
0
```

## Root cause

A transcrição foi aparada à mão ao ser colada, e a comparação de md5 foi feita num shell descartável sem registrar o valor.

## Fix

No Log de `docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md`, colar a saída inteira do `--negative` e escrever o md5 do `survey` (`c2ec025a808afd4ffbe4c39fca0d991a`) com o comando que o produz.

## Arquivos a criar ou modificar

- `docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md`

## Verificação

```text
$ grep -c "rects move -2 px in x" docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md
$ grep -c c2ec025a docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md
```

Hoje os dois dão 0; depois, 2 e pelo menos 1.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `e4f60cd9`)

```text
$ grep -c "rects move -2 px in x" docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md
0
$ python tools/kits/cli.py survey roms/japanese-shift-jis.bin | md5sum
c2ec025a808afd4ffbe4c39fca0d991a *-
$ grep -c c2ec025a docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md
0
```

REPRODUCED. Causa raiz confirmada: transcrição aparada e md5 não registrado.

### O que foi feito

- A transcrição inteira do `uv --negative` entrou no Log da KITS-TASK-04 pela [CORR-KITS-008](/docs/tasks/kits/CORR-KITS-008.md), que rodou antes nesta leva e mexia no mesmo bloco (a saída passou de 7 para 11 expectativas); aqui só se confere que as duas linhas `rects move -2 px in x` estão lá.
- O md5 do `survey` escrito no Log, com o comando. A afirmação "o mesmo das tasks anteriores" foi medida, não copiada: o `cli.py` de `fc5717ae`, `18e7ec61` e `f71b47d6`, extraído por `git archive` para uma pasta temporária, dá o mesmo valor:

```text
$ for c in fc5717ae 18e7ec61 f71b47d6; do git archive $c tools/kits tools/pes2 tools/looks | tar -x -C old; python old/tools/kits/cli.py survey roms/japanese-shift-jis.bin | md5sum; done
fc5717ae c2ec025a808afd4ffbe4c39fca0d991a *-
18e7ec61 c2ec025a808afd4ffbe4c39fca0d991a *-
f71b47d6 c2ec025a808afd4ffbe4c39fca0d991a *-
```

### Verificação

```text
$ grep -c "rects move -2 px in x" docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md
2
$ grep -c c2ec025a docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md
2
```
- **Closed** — commit `4c0c7808` (2026-09-30): docs(kits): give the survey md5 in the KITS-TASK-04 Log, measured per commit
  - Files (`git show --name-status 4c0c7808`):
    - `M docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md`
    - `M docs/tasks/kits/CORR-KITS-009.md`
