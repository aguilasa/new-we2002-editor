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
- Out: os checkboxes (KITS-TASK-40)

## Done criteria

- [ ] `cli.py figure --match` com o `TEX_14` desenha a figura de partida. A silhueta dela, contra a do quadro do jogo no slot 5 na mesma pose e câmera, fica dentro de um limite medido, com o comando
- [ ] Com a braçadeira, a figura troca a 97 pela 93, e a captura difere da sem braçadeira dentro do braço
- [ ] A janela mostra a figura de partida na aba 3D, com o texto novo no catálogo nas duas línguas
- [ ] Um vermelho visto no `kits_ui`: a planta que desenha a 97 com a braçadeira ligada
- [ ] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Aberta em 2026-10-06 por decisão do usuário. Depende, pela `order` do ciclo, das KITS-TASK-45 (pose) e 46 (manga curta). O CLI não grava `depends_on` depois da criação. Sem a 46, a figura de partida só tem manga longa.

Da KITS-TASK-46 (2026-10-06, §4.3): a manga curta foi medida no slot 6. As peças de braço trocam por posição na ordem de desenho: 95 96 97 98 viram 3 5 4 6, a braçadeira 93 vira 90, e no goleiro 99 101 100 102 viram 57 58 59 60. A tabela está em `oracle.SLEEVE_LENGTHS`. A figura de partida pode, então, sair de manga curta ou longa.

Da KITS-TASK-45 (2026-10-06, §4.3): a pose de duas figuras do slot 5 está em `work/kits-pose/slot5-30.json` (capitão) e `slot5-24.json` (linha), refeita por `oracle.py --match-pose 5`. Ali estão a projeção (`H` 1376, `OFX`/`OFY` 0) e, por peça, a seção, a rotação 4.12 e a translação. Ao desenhar, o texel de cada canto segue `Primitive.indices`, a ordem gravada, e não `corners`; pareado por `corners`, a peça erra de 2 a 4 px.

## Log de Execução
