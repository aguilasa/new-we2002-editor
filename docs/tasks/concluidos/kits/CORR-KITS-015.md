---
id: CORR-KITS-015
---

# CORR-KITS-015 — Update NOTICE.md kits rows to name tex.py as the CARP importer

Origin: [KITS-TASK-07](/docs/tasks/concluidos/kits/07-tex-e-guarda-de-forma.md)

## Problem

A linha de linhagem do kits no `NOTICE.md` diz que `lzss`/`bin_archive` chegam pelo `tools/kits/core/survey.py`, "which ... imports to read every kit container". Desde a KITS-TASK-07 quem lê todo contêiner de kit é o `tex.py`: ele importa `bin_archive` e `lzss` e põe `tools/pes2` no `sys.path`, e o `survey.py` passou a depender dele para isso. O crédito existe, mas a rota descrita está velha. A regra do repositório é que a linha do NOTICE muda no mesmo commit que traz o código.

## Evidência

```text
$ grep -n "tools/kits/core/survey.py\` imports to read every kit" NOTICE.md
220:| **Maximiliano Ducoli (CARP)** | ... Through `tools/pes2/lzss.py` and `tools/pes2/bin_archive.py`, which `tools/kits/core/survey.py` imports to read every kit container. ...
$ grep -n "^import bin_archive\|^import lzss" tools/kits/core/tex.py
38:import bin_archive  # noqa: E402  (tools/pes2, after the path insert)
39:import lzss  # noqa: E402
$ grep -c "tools/kits/core/tex.py" NOTICE.md
0
```

## Root cause

O `NOTICE.md` não estava na lista `files:` da task, então o commit não o tocou.

## Fix

Na linha 220 do `NOTICE.md`, nomear `tools/kits/core/tex.py` (a guarda de forma) como quem importa, ao lado do `survey.py`.

## Arquivos a criar ou modificar

- `NOTICE.md`

## Verificação

```text
$ grep -c "tools/kits/core/tex.py" NOTICE.md
```

Hoje dá 0; depois, pelo menos 1.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `bc81d3ab`)

```text
$ grep -n "^import bin_archive\|^import lzss" tools/kits/core/tex.py
37:import bin_archive  # noqa: E402  (tools/pes2, after the path insert)
38:import lzss  # noqa: E402
$ grep -c "tools/kits/core/tex.py" NOTICE.md
0
```

REPRODUCED.

### O que foi feito

Linha do CARP na seção do `tools/kits/` do `NOTICE.md`: a rota passa a nomear o `tex.py` (a guarda de forma, que lê todo contêiner de kit) e mantém o `survey.py`, que continua importando os dois (`grep -n "^import bin_archive\|^import lzss" tools/kits/core/survey.py` → linhas 32 e 34) para o levantamento e os retângulos de VRAM.

### Verificação

```text
$ grep -c "tools/kits/core/tex.py" NOTICE.md
1
```
- **Closed** — commit `5c544533` (2026-10-01): docs(notice): name tex.py as the kits route to the CARP LZSS and BIN format
  - Files (`git show --name-status 5c544533`):
    - `M NOTICE.md`
    - `M docs/tasks/kits/CORR-KITS-015.md`
