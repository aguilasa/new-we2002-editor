---
id: CORR-KITS-008
title: Plant a red for the outside-256x128 count in uv --negative
origin: KITS-TASK-04
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
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

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `e4f60cd9`)

```text
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --negative | grep -c "outside"
0
```

REPRODUCED. Causa raiz confirmada: as sete expectativas de `uv_negative` olhavam digest, deslocamento, união e contagem mapeada; nenhuma lia `FigureUv.outside`.

### O que foi feito

`tools/kits/core/survey.py`, `uv_negative`, quatro expectativas novas, uma para cada veredito de fora:

- `UV_OUTSIDE_SPLIT`: sob o `UV_SHIFT` já existente, a figura 0 vai de 0 a 18 "corners in two images".
- `UV_OUTSIDE_ROLE`: o registro do uniforme, sem mover, chamado de `banner` (`UV_RENAMED`) — as duas figuras vão de 0 ao número mapeado (237 e 429).
- `UV_OUTSIDE_EDGE`: o uniforme movido para (560,256) e alargado para 96 halfwords (`UV_WIDE`, `_widen_images`) — a figura 1 vai de 0 a 236 "rect leaves 256x128". Era o ramo nunca exercitado: um registro de 64 halfwords a 8 bits tem exatamente 128 pixels e não sai; só alargando o registro a coluna passa de 127.

O `cli.py` não precisou mudar: o `print_uv_controls` já imprime o que o núcleo devolve. O Log da KITS-TASK-04 recebeu a transcrição nova inteira.

### Verificação

```text
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --negative; echo "exit $?"
  uniform moved to (577,256) moved 2  both      digest changes           2360a921f7cee6f6 -> 39883f850ca73f5d  held
  uniform moved to (577,256) moved 2  figure 0  rects move -2 px in x    237 mapped -> 215 of 215 still mapped moved  held
  uniform moved to (577,256) moved 2  figure 0  union x1 moves -2 px     (0, 0, 63, 103) -> (0, 0, 61, 103)  held
  uniform moved to (577,256) moved 2  figure 1  rects move -2 px in x    429 mapped -> 429 of 429 still mapped moved  held
  uniform moved to (577,256) moved 2  figure 1  union x1 moves -2 px     (48, 0, 127, 127) -> (46, 0, 125, 127)  held
  uniform moved to (577,256) moved 2  figure 0  outside: split rises     0 outside -> 18 corners in two images  held
  uniform named banner       moved 0  figure 0  outside: role = mapped   0 outside -> 237 not uniform or sleeves  held
  uniform named banner       moved 0  figure 1  outside: role = mapped   0 outside -> 429 not uniform or sleeves  held
  uniform at (560,256) w 96  moved 2  figure 1  outside: edge rises      0 outside -> 236 rect leaves 256x128  held
  uniform moved to (0,0)     moved 2  figure 0  mapped count drops to 0  237 -> 0  held
  uniform moved to (0,0)     moved 2  figure 1  mapped count drops to 0  429 -> 0  held
11 of 11 expectations held
exit 0
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --negative | grep -c "outside"
4
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin | tail -1
sha256 of the canonical JSON: 2360a921f7cee6f69dcbc1bb3ad2633c306a720c86399a04b918fbdf9448fb84
$ grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py
(sem saída, exit 1)
```

O digest do `uv` sem controle é o mesmo do Log da KITS-TASK-04: a saída publicada não mudou.
