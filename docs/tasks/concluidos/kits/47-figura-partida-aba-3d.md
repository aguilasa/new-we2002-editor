---
id: KITS-TASK-47
---

# KITS-TASK-47 — Figura de partida na aba 3D

## Goal

A aba 3D passa a desenhar também a figura de partida: as seções do `MODEL.BIN` na ordem medida, com a pose da KITS-TASK-45 e o uniforme do TEX aberto. A braçadeira entra trocando a 97 pela 93, e a manga longa ou curta sai da regra da KITS-TASK-46. Isso é o que dá aos checkboxes **Captain armband** e **Long sleeves** da KITS-TASK-40 algo para ligar. A figura da `LOOKS SET` (`EDT_MOD.BIN`) continua como está.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py` e `tools/kits/core/api.py`: a figura de partida, montada a partir das seções e da pose medidas, sem geometria inventada (§0)
  - `tools/kits/cli.py`: o `figure` desenha a figura de partida também, para a CLI fazer o que a janela faz
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py`: a escolha entre a figura da `LOOKS SET` e a de partida, nas duas línguas
  - `tools/kits/ui_check.py`: a verificação e a planta
  - `docs/PLAN-KITS-PY.md`: §3.4 e §4.3
  - `tools/kits/oracle.py`: `--match-silhouette`, `--plant-silhouette` e `--match-pose --write/--check`, o comando do critério 1; o `SLEEVE_LENGTHS` desceu daqui para o core (declarado pela CORR-KITS-086)
  - `tools/kits/selftest.py`: as verificações puras do confronto e da pose gravada (CORR-KITS-086)
  - `tools/kits/core/match_pose.json`: a pose medida, gerada por `oracle.py --match-pose --write` (CORR-KITS-086)
  - `docs/prompts/perfil-kits.md`: a entrada do artefato gerado (CORR-KITS-086)
- Out: os checkboxes (KITS-TASK-40)

## Done criteria

- [x] `cli.py figure --match` com o `TEX_14` desenha a figura de partida. A silhueta dela, contra a do quadro do jogo no slot 5 na mesma pose e câmera, fica dentro de um limite medido, com o comando
- [x] Com a braçadeira, a figura troca a 97 pela 93, e a captura difere da sem braçadeira dentro do braço
- [x] A janela mostra a figura de partida na aba 3D, com o texto novo no catálogo nas duas línguas
- [x] Um vermelho visto no `kits_ui`: a planta que desenha a 97 com a braçadeira ligada
- [x] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Aberta em 2026-10-06 por decisão do usuário. Depende, pela `order` do ciclo, das KITS-TASK-45 (pose) e 46 (manga curta). O CLI não grava `depends_on` depois da criação. Sem a 46, a figura de partida só tem manga longa.

Da KITS-TASK-46 (2026-10-06, §4.3): a manga curta foi medida no slot 6. As peças de braço trocam por posição na ordem de desenho: 95 96 97 98 viram 3 5 4 6, a braçadeira 93 vira 90, e no goleiro 99 101 100 102 viram 57 58 59 60. A tabela está em `oracle.SLEEVE_LENGTHS`. A figura de partida pode, então, sair de manga curta ou longa.

Da KITS-TASK-45 (2026-10-06, §4.3): a pose de duas figuras do slot 5 está em `work/kits-pose/slot5-30.json` (capitão) e `slot5-24.json` (linha), refeita por `oracle.py --match-pose 5`. Ali estão a projeção (`H` 1376, `OFX`/`OFY` 0) e, por peça, a seção, a rotação 4.12 e a translação. Ao desenhar, o texel de cada canto segue `Primitive.indices`, a ordem gravada, e não `corners`; pareado por `corners`, as peças erram de 1,48 a 4,05 px, 21 das 24 acima do limite (`--pair-by corners`, CORR-KITS-083).

## Log de Execução

### 2026-10-06 — execução

A pose virou arquivo versionado, `tools/kits/core/match_pose.json`, escrito por `oracle.py --match-pose 5 --write` e conferido por `--check` (entrada nova em "Generated artifacts" do perfil). Isso deixa a aba 3D e o `kits_ui` independentes de `work/`. O núcleo ganhou `api.match_figure` (`core/figure.py`, `match_scene`): seções do `MODEL.BIN` na ordem da pose, cada uma pela própria matriz, texturizadas como o `assembly.draw_list` resolve (DAT2D primeiro, o TEX depois). A braçadeira e a manga curta trocam a seção por posição e mantêm a matriz da posição. A 93 e a 97 têm a mesma caixa de vértices no disco. A tabela `SLEEVE_LENGTHS` mudou do `oracle.py` para o núcleo, e o `oracle.py` a importa de lá.

```
$ python tools/kits/cli.py figure --match [--armband] --tag 14 --set 1 $WE2002_LOOKS_IMAGE
set 1 match figure, long sleeves: order 24 2 95 96 97 98 7 9 11 8 10 12  140 parts, 140 textured, 7 surfaces  da5cd013c08f5763334e3772bfebe704082b61847bbf5dbb0a30bcfb6410e5d4
set 1 match figure, long sleeves, armband: order 24 2 95 96 93 98 7 9 11 8 10 12  140 parts, 140 textured, 7 surfaces  fc520bb5852e9c515dde15c587bb583d307bc5cd6630d85a88a2d3e9a983bd2d
$ python tools/kits/oracle.py --match-silhouette 5 --tag 14 --frame-json work/kits-oracle/pose-5.json   # exit 0
  capture read from work/kits-oracle/pose-5.json, no emulator
  outfield TEX_14, order 24 2 95 96 97 98 7 9 11 8 10 12: game 6044 cell(s), ours 6079, both 5389; IoU 0.800
  captain  TEX_14, order 30 2 95 96 93 98 7 9 11 8 10 12: game 6966 cell(s), ours 7062, both 6323; IoU 0.821
  ok    both figures within IoU 0.700 of the game's (worst 0.800; cells of 1/4 px)
$ ... --plant-silhouette   # exit 1
  capture read from work/kits-oracle/pose-5.json, no emulator
  PLANT  every piece drawn with its figure's body matrix
  outfield TEX_14, order 24 2 95 96 97 98 7 9 11 8 10 12: game 6044 cell(s), ours 2392, both 2053; IoU 0.322
  captain  TEX_14, order 30 2 95 96 93 98 7 9 11 8 10 12: game 6966 cell(s), ours 2103, both 2007; IoU 0.284
  FAIL  outfield: IoU 0.322 under 0.700
  FAIL  captain: IoU 0.284 under 0.700
```

Limite de IoU 0,70 (`oracle.SILHOUETTE_LIMIT`), entre o real (0,800 e 0,821) e a planta (0,322 e 0,284). Arredondar nossos cantos ao pixel inteiro deu 0,793 e 0,787, sem ganho; ficou o ponto flutuante.

`kits_ui` (`python tools/kits/ui_check.py`, `:98`), juiz novo e planta:

```
  ok    3D TEX_14: the match player is drawn, and the captain's armband changes only a box on its arm (337 px (1.3 % of the figure) in a 25x18 box)
        plant 'armband drawn as section 97': the armband changes nothing
  ok    plant 'armband drawn as section 97' fails the match judge
kits_ui: 0 failure(s)
```

A janela tem o terceiro item **match player** / **jogador em partida** no seletor de figura (`i18n.py`, chave `figure_match`). `ui/app.py --figure 2 --armband` liga a braçadeira até o checkbox da KITS-TASK-40 existir. A planta antiga "3D set ignored" foi reescrita para o texto novo da chamada, e continua vermelha.

Outros vermelhos vistos:

- **`--check`:** com a translação de uma peça somada de 1 no arquivo, sai `FAIL  tools/kits/core/match_pose.json is not what this run measures: rerun with --write` e exit 1. Restaurado, exit 0.
- **Selftest:** com a braçadeira ignorada em `match_order`, saem `FAIL  match order, long sleeves, armband True: section 93 where 97 was, with 97's matrix` e mais 4 falhas. Restaurado, `kits_selftest: 0 failure(s)`.


`ctest --test-dir build -R kits` (com `WE2002_LOOKS_IMAGE`, `WE2002_LOOKS_DRIVE_IMAGE`, `WE2002_KITS_ED_IMAGE`, `:98`): `100% tests passed, 0 tests failed out of 4`.
- **Closed** — commit `f060945` (2026-10-06): feat(kits): draw the match figure in the 3D tab, from the measured pose
  - Files (`git show --name-status f060945`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/prompts/perfil-kits.md`
    - `M docs/tasks/kits/47-figura-partida-aba-3d.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/figure.py`
    - `A tools/kits/core/match_pose.json`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
- **Reviewed** (2026-10-06) at `c8dfdbe`: CORR-KITS-086, CORR-KITS-087, CORR-KITS-088
