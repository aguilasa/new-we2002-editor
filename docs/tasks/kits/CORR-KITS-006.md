---
id: CORR-KITS-006
---

# CORR-KITS-006 — Paste prims transcripts in the Log whole, not trimmed

Origin: [KITS-TASK-03](/docs/tasks/kits/03-primitivas-por-retangulo.md)

## Problem

O primeiro critério da KITS-TASK-03 é a saída "colada no Log", mas o que está lá não é o que a ferramenta imprime. Na transcrição do `prims` faltam o cabeçalho `Primitives per kit record: ...` e duas linhas por figura (`a corner in a DAT2D image record` 356/200 e `a corner in no record of either file` 0). Na do `--negative` aparecem 4 das 14 linhas, e o texto "(exit 0; sai 1 se alguma falhar)" entrou dentro do bloco de código como se fosse saída da ferramenta.

## Evidência

```text
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin | grep -nE 'Primitives per|a corner in'
1:Primitives per kit record: roms/japanese-shift-jis.bin
6:  a corner in a DAT2D image record         356
7:  a corner in no record of either file     0
15:  a corner in a DAT2D image record         200
16:  a corner in no record of either file     0
$ grep -c 'a corner in' docs/tasks/kits/03-primitivas-por-retangulo.md
0
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --negative | wc -l
15
```

## Root cause

Hipótese: a saída foi aparada à mão quando o Log foi escrito.

## Fix

Colar as duas saídas inteiras na seção de evidência da task e pôr a nota de código de saída fora do bloco de código.

## Arquivos a criar ou modificar

- `docs/tasks/kits/03-primitivas-por-retangulo.md`

## Verificação

```text
$ grep -c 'a corner in' docs/tasks/kits/03-primitivas-por-retangulo.md
```

Hoje dá 0; depois, 4.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `7c6c8309`)

```text
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin | grep -nE 'Primitives per|a corner in'
1:Primitives per kit record: roms/japanese-shift-jis.bin
7:  a corner in a DAT2D image record         356
8:  a corner in no record of either file     0
16:  a corner in a DAT2D image record         200
17:  a corner in no record of either file     0
$ grep -c 'a corner in' docs/tasks/kits/03-primitivas-por-retangulo.md
0
```

REPRODUCED (os números de linha andaram um desde a revisão; o conteúdo é o mesmo). Causa raiz confirmada: as duas transcrições não são a saída do comando.

### O que foi feito

Os blocos de `prims` e de `prims --negative` do Log da KITS-TASK-03 trocados pela saída inteira dos mesmos comandos na HEAD `c58061c6` (os dois saem 0), gerada por script e não digitada. A nota "(exit 0; sai 1 se alguma falhar)" saiu do bloco: o `# exit 0` fica no comentário da linha `$`, e "sai 1 se alguma expectativa falhar" vai para o texto logo abaixo.

### Verificação

```text
$ grep -c 'a corner in' docs/tasks/kits/03-primitivas-por-retangulo.md
4
$ grep -n 'sai 1 se alguma falhar' docs/tasks/kits/03-primitivas-por-retangulo.md
(sem saída, exit 1)
```
- **Closed** — commit `0f48d058` (2026-09-30): docs(kits): paste the prims transcripts of KITS-TASK-03 whole
  - Files (`git show --name-status 0f48d058`):
    - `M docs/tasks/kits/03-primitivas-por-retangulo.md`
    - `M docs/tasks/kits/CORR-KITS-006.md`
