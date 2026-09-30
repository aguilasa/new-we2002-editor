---
id: CORR-KITS-008
title: Plant a red for the outside-256x128 count in uv --negative
origin: KITS-TASK-04
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-008 — Plant a red for the outside-256x128 count in uv --negative

Origin: [KITS-TASK-04](/docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md)

## Problem

O §4.6 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) afirma "fora do 256×128: **0**" para as duas figuras, como pede o critério 2 da KITS-TASK-04. Nenhuma das 7 expectativas do `uv --negative` confere que esse contador de fora pode sair do zero: elas conferem só o digest, o deslocamento de -2 px, o x1 da união e a contagem mapeada. O contador fica vermelho quando se planta um defeito — com o uniforme deslocado meia palavra, 18 primitivas da figura 0 viram "corners in two images" —, mas o controle versionado não mostra nem afirma isso. Pela regra "verificador sem vermelho visto não é gate", o 0 fica sem gate, e o ramo `UV_OUTSIDE_EDGE` nunca é exercitado.

## Evidência

```text
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --negative | grep -c "outside"
0
```

Sonda do revisor, sem versão (`_move_images` com `UV_SHIFT` no `TEX_A4` e `uv_files` com o papel `uniform` no registro deslocado):

```text
0 233 215 Counter({'corners in two images': 18})
1 429 429 Counter()
```

## Root cause

Hipótese: o controle foi desenhado em torno do movimento dos retângulos, não do veredito que o plano publica.

## Fix

Em `tools/kits/core/survey.py`, no `uv_negative`, acrescentar uma expectativa de que o `len(outside)` da figura 0 vai de 0 a mais de 0 sob `UV_SHIFT` (os 18 "corners in two images"). Acrescentar também um papel plantado que não seja `uniform` nem de manga (por exemplo, o registro deslocado chamado de "banner"), que precisa dar `UV_OUTSIDE_ROLE` > 0. Colar a transcrição nova inteira no Log da task.

## Arquivos a criar ou modificar

- `tools/kits/core/survey.py`
- `tools/kits/cli.py`
- `docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md`

## Verificação

```text
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --negative | grep -c "outside"
```

Hoje dá 0; depois, pelo menos 1, com a linha dizendo "held".

## Log de Execução
