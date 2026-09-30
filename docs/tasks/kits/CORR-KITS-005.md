---
id: CORR-KITS-005
title: Add versioned probes for the 105-TEX and tuple-independence claims
origin: KITS-TASK-03
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-005 — Add versioned probes for the 105-TEX and tuple-independence claims

Origin: [KITS-TASK-03](/docs/tasks/kits/03-primitivas-por-retangulo.md)

## Problem

O §4.3 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) afirma que "a contagem é a mesma nos 105 TEX e independe da tupla fora a cabeça". O Log da KITS-TASK-03 diz que o resultado dos 105 TEX saiu de "um laço descartável" e que só a tupla `A-A1-A-A-A` foi medida. O `cli.py prims` tem `--kit`, mas nenhum modo para todos os kits nem opção `--tuple`, então nenhum comando versionado reproduz as duas afirmações. O revisor as refez por uma sonda própria sobre o núcleo e elas se sustentam (105 de 105 kits com um resultado só; 6 tuplas mantendo 237/429 de kit, com o total variando com a cabeça — 598/634 em `A-I3-A-G-A`), mas só por sonda, o que a regra "sonda que produziu um número vira opção de uma ferramenta versionada" proíbe.

## Evidência

```text
$ python tools/kits/cli.py prims --help | grep -cE -- '--all|--tuple'
0
$ sed -n 352,353p docs/PLAN-KITS-PY.md
linha (383) e nenhuma além. A contagem é a mesma nos 105 TEX e independe da
tupla fora a cabeça, que amostra o `DAT2D`. Fica aberta a outra metade: se a
```

Sonda do revisor, sem versão (laço sobre `survey.layout.KIT_TAGS` com `survey.prims_image`, e seis tuplas com `survey.prims_files`):

```text
105 ((0, 593, (('DAT2D', 356), ('kit', 237)), ...), (1, 629, (('DAT2D', 200), ('kit', 429)), ...))
A-I3-A-G-A [(598, (('uniform', 237),), ...), (634, (('uniform', 429),), ...)]
```

## Root cause

Hipótese, pela redação do Log: a varredura rodou como laço descartável e a conclusão foi para o plano sem virar opção do CLI.

## Fix

Adicionar ao `prims` do `tools/kits/cli.py`, sobre `survey.prims_files`, as opções `--all-kits` (junta resultados idênticos e imprime quantos são distintos) e `--tuple T` (ou uma varredura de tuplas). Colar a saída no Log e citar os dois comandos no §4.3. Alternativa: restringir o §4.3 a "medido no `TEX_A4` e na tupla `A-A1-A-A-A`".

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/core/survey.py`
- `docs/PLAN-KITS-PY.md`
- `docs/tasks/kits/03-primitivas-por-retangulo.md`

## Verificação

```text
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --all-kits
```

Hoje falha com `unrecognized arguments`; depois imprime "105 kits, 1 distinct result".

## Log de Execução
