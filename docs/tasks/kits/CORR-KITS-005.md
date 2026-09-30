---
id: CORR-KITS-005
title: Add versioned probes for the 105-TEX and tuple-independence claims
origin: KITS-TASK-03
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
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

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `7c6c8309`)

```text
$ python tools/kits/cli.py prims --help | grep -cE -- '--all|--tuple'
0
```

REPRODUCED. Causa raiz confirmada: o `prims` só aceitava `--kit` e `--negative`; nada versionado varria kits nem tuplas.

### O que foi feito

- `tools/kits/core/survey.py`: `prims_all_kits` (agrupa os kits de resultado idêntico, `KitsSweep`), `prims_tuples` e `kit_roles_of` (o que a varredura de tuplas compara: os papéis do kit pelas duas contagens, por figura), `prims_all_kits_negative` (`SweepControl`: tira o uniforme do `TEX_A4` para (0,0) e exige o agrupamento partido em 104 + `TEX_A4` e os papéis do kit diferentes), e `read_prims_all_kits`, que lê tudo numa abertura de disco. `prims_image` ganhou a tupla.
- `tools/kits/cli.py prims --all-kits`, `--tuple T` (repetível) e `--all-kits --negative`.
- §4.3 do plano cita os comandos; o Log da KITS-TASK-03 troca o "laço descartável" pelas três saídas.

### Verificação

```text
$ python tools/kits/cli.py prims --help | grep -cE -- '--all|--tuple'
3
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --all-kits; echo "exit $?"
Primitives per kit record, every kit: roms/japanese-shift-jis.bin
  tuple A-A1-A-A-A: 105 kits, 1 distinct result(s)
  105 kit(s)
    figure 0: 593 primitive(s); kit role uniform 237
    figure 1: 629 primitive(s); kit role uniform 429
exit 0
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --tuple A-A1-A-A-A --tuple D-A1-A-A-A --tuple A-P1-A-A-A --tuple A-I3-A-A-A --tuple A-A1-H-A-A --tuple A-A1-A-G-A --tuple A-A1-A-A-G --tuple A-I3-A-G-A | tail -1
  kit roles identical in all 8 tuples: yes (1 distinct)
```

O verificador visto falhando:

```text
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --all-kits --negative; echo "exit $?"
Planted: 2 image record(s) of TEX_A4 moved from (576,256) to (0,0)
  clean    105 kits, 1 distinct result(s): 105
  planted  105 kits, 2 distinct result(s): 104, 1  [TEX_A4]
  kit roles of TEX_A4, clean vs planted: 2 distinct
red
exit 0
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --negative | tail -1
14 of 14 expectations held
$ grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py
(sem saída, exit 1)
```
