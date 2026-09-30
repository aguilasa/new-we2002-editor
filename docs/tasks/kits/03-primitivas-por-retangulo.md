---
id: KITS-TASK-03
title: "Contar primitivas de cada figura por retângulo do TEX"
type: "investigação"
phase: 0
depends_on: []
source_of_truth: "/docs/PLAN-KITS-PY.md#4.3"
files: ["tools/kits/core/survey.py", "tools/kits/cli.py", "docs/PLAN-KITS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
done_on: 2026-09-30
done_commit: f71b47d6
reviewed_on: pending
review_commit: null
---

# KITS-TASK-03 — Contar primitivas de cada figura por retângulo do TEX

## Goal

A primeira metade da §4.3 medida no disco: para a figura 0 (linha) e a 1 (goleiro), quantas primitivas amostram cada um dos retângulos do TEX (uniforme, mangas, bandeira, árbitro), lido pela geometria do `looks`.

## Arquivos a criar ou modificar

- `tools/kits/core/survey.py`
- `tools/kits/cli.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [x] Subcomando versionado imprime a contagem por figura e por retângulo; colada no Log
- [x] A §4.3 do plano registra se a imagem de mangas (576,384) é amostrada por alguma primitiva do `EDT_MOD.BIN` — sim ou não, com o número
- [x] Controle: a contagem total por figura bate com o número de primitivas que o `tools/looks` já desenha (comando e número no Log)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3). Nada de remapear UV à mão (§4.3). Se a manga longa for outra geometria, esta task só registra isso.

## Log de Execução

### O que foi feito

- `core/survey.py`: `prims_files()` conta, por figura, quantas primitivas caem em cada registro do TEX — pela resolução do `assembly.draw_list` (primeiro canto, primeiro registro) **e** pelos quatro cantos contra todo registro, porque o §1.2 avisa que o `draw_list` fica com o primeiro. Papéis (uniforme, mangas, bandeira, árbitro) pela origem do registro, em `KIT_ROLES`.
- `cli.py prims <imagem> [--kit TAG] [--negative]`; o `--negative` é o controle versionado.
- §4.3 do plano: veredito da primeira metade, com a tabela.

### Evidência

```
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin     # exit 0
  kit TEX_A4, tuple A-A1-A-A-A, geometry and resolution by tools/looks draw_list
figure 0 (outfield): 593 primitive(s) over 12 section(s)
  container (draw list, first corner)      DAT2D 356, kit 237
  kit role (draw list, first corner)       uniform 237
  kit role (any of four corners)           uniform 237
  corners touch a kit role first missed    0
  VRAM box of the corners in kit records   (576,256)..(607,359)
  sleeves (576,384): 0 primitive(s)
figure 1 (goalkeeper): 629 primitive(s) over 12 section(s)
  container (draw list, first corner)      DAT2D 200, kit 429
  kit role (draw list, first corner)       uniform 429
  kit role (any of four corners)           uniform 429
  corners touch a kit role first missed    0
  VRAM box of the corners in kit records   (600,256)..(639,383)
  sleeves (576,384): 0 primitive(s)
```

Com `--kit 00` a saída só difere na linha do cabeçalho (`diff`); num laço descartável sobre os 105 TEX o resultado por papel foi um só.

Controle de totais — o `looks` já imprime o mesmo número por figura:

```
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python tools/looks/assembly.py --check-image
  figure 0: 593 primitive(s) over 12 section(s); 237 with no palette in this file, 237 sampling outside it
  figure 1: 629 primitive(s) over 12 section(s); 429 with no palette in this file, 429 sampling outside it
assembly --check-image: ok
```

593/629 = o nosso total; 237/429 "sampling outside" `DAT2D` = a nossa contagem no TEX.

Controles negativos:

```
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --negative
    uniform moved to (0,0)       moved 2  figure 0  uniform first            237 ->   0  drops to zero     held
    uniform moved to (0,0)       moved 2  figure 1  uniform first            429 ->   0  drops to zero     held
    sleeves moved to (560,256)   moved 2  figure 0  disagree                   0 -> 238  rises above zero  held
    sleeves moved to (560,256)   moved 2  figure 1  disagree                   0 -> 194  rises above zero  held
  14 of 14 expectations held                          (exit 0; sai 1 se alguma falhar)
```

O das mangas em (560, 256) prova que a contagem por quatro cantos enxerga registro que o primeiro-encontrado esconde (238 no lugar de 237: uma primitiva do `DAT2D` tem canto na faixa plantada).

`grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py` → sem saída; `cli.py survey` → mesmas linhas da KITS-TASK-01 (md5 da saída igual antes e depois).

### Problemas encontrados

- O primeiro desenho do controle positivo pôs as mangas em (576, 256) e deu `FAILED 0 -> 0`: o papel é lido pela origem, e um registro ali se chama "uniforme". Refeito em (560, 256).
- Só a tupla `A-A1-A-A-A` foi medida por figura; a tupla só troca a cabeça, que amostra o `DAT2D`.
- **Closed** — commit `f71b47d6` (2026-09-30): feat(kits): count each figure's primitives per kit record (prims)
  - Files (`git show --name-status f71b47d6`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/03-primitivas-por-retangulo.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/survey.py`
