---
id: KITS-TASK-04
---

# KITS-TASK-04 — Levantar as UV que o boneco amostra no bitmap de 256×128

## Goal

A entrada da §4.6: o conjunto de retângulos do bitmap de trabalho 256×128 que as primitivas das duas figuras amostram, por comando versionado, pronto para a fase 3 cruzar com o mapa de zonas.

## Arquivos a criar ou modificar

- `tools/kits/core/survey.py`
- `tools/kits/cli.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [x] Subcomando versionado imprime, por figura, os retângulos UV amostrados no espaço 256×128; a saída (ou o digest dela, se longa) está no Log
- [x] A §4.6 do plano diz onde a saída mora e quantas primitivas caem fora do 256×128 (número da ferramenta)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.6).

## Log de Execução

### O que foi feito

- `core/survey.py`: `figure_uv`/`uv_files`/`uv_image`, `bitmap_pixel()` (coluna = `(page_x - record.x) * texels_per_unit + u`, linha = `page_y + v - record.y`, em pixel e não em halfword, para não perder a coluna ímpar). O laço do `draw_list` saiu de `figure_prims` para `_drawn()` e passou a servir aos dois; a saída do `prims` não mudou.
- `cli.py uv <imagem> [--kit TAG] [--json] [--negative]`.
- §4.6 do plano: onde a saída mora (o comando, com o digest) e a tabela.

### Evidência

```
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin      # exit 0
figure 0 (outfield): 237 kit primitive(s), 237 mapped
  mapped per image                             uniform 237
  union box, bitmap px (inclusive)             (0,0)..(63,103)
  distinct px in the rects (bounding-rect)     4117
  outside 256x128: 0
figure 1 (goalkeeper): 429 kit primitive(s), 429 mapped
  mapped per image                             uniform 429
  union box, bitmap px (inclusive)             (48,0)..(127,127)
  distinct px in the rects (bounding-rect)     3825
  outside 256x128: 0
sha256 of the canonical JSON: 2360a921f7cee6f69dcbc1bb3ad2633c306a720c86399a04b918fbdf9448fb84

$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --kit 00 | tail -1
sha256 of the canonical JSON: 2360a921f7cee6f69dcbc1bb3ad2633c306a720c86399a04b918fbdf9448fb84
```

Contra a KITS-TASK-03 (caixas em halfword de VRAM): figura 0, (576,256)..(607,359) → x 2·0 .. 2·31+1 = 0..63, y 0..103; figura 1, (600,256)..(639,383) → x 48..127, y 0..127. As mesmas caixas, e 237/429 primitivas nos dois comandos.

```
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --negative     # exit 0
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
```

O comando sai 1 se alguma expectativa falhar. As quatro linhas `outside:` entraram pela [CORR-KITS-008](/docs/tasks/kits/CORR-KITS-008.md): cada veredito de fora do 256×128 (duas imagens, papel sem lugar, borda) visto saindo do zero.

`grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py` → sem saída; `prims --negative` → `14 of 14 expectations held`; `survey` → saída com o mesmo md5 das tasks anteriores, medido pela [CORR-KITS-009](/docs/tasks/kits/CORR-KITS-009.md) rodando o `cli.py` de cada commit (`git archive <commit> tools/kits tools/pes2 tools/looks` numa pasta temporária):

```
$ python tools/kits/cli.py survey roms/japanese-shift-jis.bin | md5sum
c2ec025a808afd4ffbe4c39fca0d991a *-
```

O mesmo `c2ec025a808afd4ffbe4c39fca0d991a` em `fc5717ae` (KITS-TASK-01), `18e7ec61` (02), `f71b47d6` (03) e na HEAD desta correção.

### Problemas encontrados

- A primeira corrida do `--negative` falhou 4 de 7: o papel sai da origem do registro, e o uniforme deslocado para (577,256) deixava de se chamar "uniforme". O controle passa agora um `roles=` que nomeia a origem deslocada; o comportamento padrão não mudou.
- Com o deslocamento, 22 primitivas da figura 0 saem do registro (a coluna de halfword 576) em vez de mover; o controle exige que as que continuam mapeadas movam (215 de 215).
- **Closed** — commit `63dde69c` (2026-09-30): feat(kits): map each kit primitive's UV rect into the 256x128 work bitmap (uv)
  - Files (`git show --name-status 63dde69c`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/survey.py`
- **Reviewed** (2026-09-30) at `2a63d8ac`: CORR-KITS-008, CORR-KITS-009
