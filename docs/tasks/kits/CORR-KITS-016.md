---
id: CORR-KITS-016
title: "Use layout.kit_path in RomSource.kits, restoring the lost line break"
origin: KITS-TASK-07
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-016 — Use layout.kit_path in RomSource.kits, restoring the lost line break

Origin: [KITS-TASK-07](/docs/tasks/kits/07-tex-e-guarda-de-forma.md)

## Problem

A linha 101 de `tools/kits/core/source.py` junta duas linhas de código com uns 20 espaços no meio, o que parece uma quebra de linha perdida. Ela também remonta o caminho do kit à mão, quando `survey.layout.kit_path(tag)` já existe e o mesmo módulo o usa em `build_open_fixtures`.

## Evidência

```text
$ grep -n "KIT_PREFIX + tag  " tools/kits/core/source.py
101:                path = survey.layout.KIT_DIR + survey.layout.KIT_PREFIX + tag                     + survey.layout.KIT_SUFFIX
$ grep -n "layout.kit_path" tools/kits/core/source.py
378:    kit_path = survey.layout.kit_path(CONTROL_KIT_TAG)
```

## Root cause

Hipótese: uma continuação de linha se perdeu na edição.

## Fix

Em `tools/kits/core/source.py:101`, usar `path = survey.layout.kit_path(tag)`.

## Arquivos a criar ou modificar

- `tools/kits/core/source.py`

## Verificação

```text
$ grep -c "KIT_PREFIX + tag  " tools/kits/core/source.py
```

Hoje dá 1; depois, 0, com `cli.py tex` dando a mesma saída de antes nas duas imagens.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `bc81d3ab`)

```text
$ grep -n "KIT_PREFIX + tag  " tools/kits/core/source.py
101:                path = survey.layout.KIT_DIR + survey.layout.KIT_PREFIX + tag                     + survey.layout.KIT_SUFFIX
```

REPRODUCED.

### O que foi feito

`tools/kits/core/source.py:101` passa a `path = survey.layout.kit_path(tag)`.

### Verificação

```text
$ grep -c "KIT_PREFIX + tag  " tools/kits/core/source.py
0
$ python tools/kits/cli.py tex roms/japanese-shift-jis.bin | md5sum          # antes e depois, exit 0 nos dois
78df4860c3d0e2ff1a65a215e4412d08 *-
$ python tools/kits/cli.py tex roms/golden-european-deluxe.bin | md5sum      # antes e depois, exit 1 nos dois (8 recusados)
f5cc3872f6a2a6a066b23b05272ed73c *-
```

`cmp` das saídas de antes e depois: idênticas nas duas imagens.
