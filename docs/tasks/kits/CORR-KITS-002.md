---
id: CORR-KITS-002
title: "Version the survey's negative controls instead of an ad hoc probe"
origin: KITS-TASK-01
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-002 — Version the survey's negative controls instead of an ad hoc probe

Origin: [KITS-TASK-01](/docs/tasks/kits/01-levantamento-do-tex.md)

## Problem

O Log da KITS-TASK-01 mostra resultados de controle negativo (`clean {...}` / `planted {...}`, e o árbitro indo de 1 para 2 variantes), mas o script que os produziu não está no repositório nem no Log. Nenhum selftest nem alvo de `ctest` exercita `survey_files`. A regra do projeto ("sonda que produziu um número vira opção de uma ferramenta versionada"; "verificador sem vermelho visto não é gate") exige que o vermelho seja reproduzível da HEAD.

## Evidência

```text
$ git ls-files tools/kits
tools/kits/cli.py
tools/kits/core/__init__.py
tools/kits/core/survey.py
$ python tools/kits/cli.py survey --negative roms/japanese-shift-jis.bin
cli.py: error: unrecognized arguments: --negative
```

O revisor replantou os mesmos bits de CLUT numa sonda própria e obteve `planted 105 () 103 ('98','A4') () 1` e `ref 2` — o verificador fica vermelho —, mas os 104/102 do Log vêm de uma edição extra de retângulo que não se reconstrói a partir do Log.

## Root cause

Hipótese: o controle rodou como sonda descartável em memória — exatamente o padrão que a task existia para eliminar no §1.1.

## Fix

Adicionar um controle versionado (`tools/kits/selftest.py` ou `cli.py survey --negative <imagem>`) que plante, via `survey_files`, os três defeitos — bit de CLUT no conjunto 2 do `TEX_A4`, bit de CLUT de goleiro no conjunto 1 do `TEX_A4`, e o árbitro do `TEX_00` — e afirme que as contagens se movem. Colar a saída dele no Log no lugar dos dicionários da sonda.

## Arquivos a criar ou modificar

- `tools/kits/cli.py` (ou novo `tools/kits/selftest.py`)
- `docs/tasks/kits/01-levantamento-do-tex.md`

## Verificação

```text
$ python tools/kits/cli.py survey --negative roms/japanese-shift-jis.bin
```

Hoje: erro do argparse. Depois: cada defeito plantado imprime o vermelho, saída 0.

## Log de Execução
