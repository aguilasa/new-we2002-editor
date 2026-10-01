---
id: CORR-KITS-014
title: Add a planted control for the Form 2 and extent refusals
origin: KITS-TASK-07
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-014 — Add a planted control for the Form 2 and extent refusals

Origin: [KITS-TASK-07](/docs/tasks/kits/07-tex-e-guarda-de-forma.md)

## Problem

Duas asserções novas da KITS-TASK-07 não têm controle versionado nem vermelho no Log. Uma é o `source._sector_data`, que lança `KitUnreadable` quando um setor marcado como Form 2 tem dados nos bytes 2072–2347. A outra é a regra da extensão do cabeçalho: ler além do tamanho ISO só até o arquivo seguinte. O único controle é o do byte do LZSS (`tex --negative`), e nada em `tools/kits` exercita o `KitUnreadable`. Vale a regra "verificador sem vermelho visto não é gate". O caminho funciona, mas só se viu vermelho por sonda descartável.

## Evidência

```text
$ python tools/kits/cli.py tex --negative roms/golden-european-deluxe.bin | grep -c KitUnreadable
0
$ grep -rn "KitUnreadable" tools/kits --include=*.py | grep -v "errors.py\|api.py"
tools/kits/core/source.py:34:from .errors import (KitMissing, KitUnreadable, NotASource, SourceEmpty,
tools/kits/core/source.py:80:        no such tag, `KitUnreadable` if a sector of it is Form 2 for real.
tools/kits/core/source.py:150:        raise KitUnreadable(
tools/kits/core/source.py:176:        raise KitUnreadable("%s on %s runs past the end of the data track."
```

Sonda do revisor, sem versão (leitor de setor em memória que põe `0x55` no byte 2100 do setor 8675 do `TEX_13`):

```text
KitUnreadable /BIN/TEX_13.BIN on ../../roms/golden-european-deluxe.bin: sector 8675 (16 of 16) is Form 2 with data past byte 2048, so it is not a Form 1 sector with a wrong bit.
```

## Root cause

Hipótese: a lista de controles da task saiu do item 4 do §5 do plano, que é anterior às decisões sobre Form 2 e extensão, e as recusas novas nunca entraram nela.

## Fix

Acrescentar a `tools/kits` um controle plantado (no `cli.py tex --negative` ou no futuro `controls.py`) que ponha um byte não nulo nos bytes 2072–2347 de um setor marcado e espere `KitUnreadable`, usando um leitor de setor em memória como o da sonda, não uma cópia de 474 MB. Opcionalmente, um segundo plantio que limite o espaço abaixo da extensão e espere o `TEX_13` recusado. Nomear o controle no §5 do plano.

## Arquivos a criar ou modificar

- `tools/kits/core/source.py`
- `tools/kits/cli.py` ou `tools/kits/controls.py`
- `docs/PLAN-KITS-PY.md` (§5)

## Verificação

```text
$ python tools/kits/cli.py tex --negative roms/golden-european-deluxe.bin | grep -c KitUnreadable
```

Hoje dá 0; depois, pelo menos 1.

## Log de Execução
