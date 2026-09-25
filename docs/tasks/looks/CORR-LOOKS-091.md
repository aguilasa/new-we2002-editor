---
id: CORR-LOOKS-091
title: "O bloco de evidência mistura prosa à transcrição do comando"
origin: LOOKS-TASK-40
severity: low
files: [docs/tasks/looks/40-a-camera-do-close-up.md]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-091 — O bloco de evidência mistura prosa à transcrição do comando

Origin: [LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md)

## Problema identificado

O bloco `### Evidência` apresenta duas transcrições `$ python ...`, e nenhuma
das duas é o que o comando imprime:

- a do `--closeups` tira `NAT`, `BODY` e `AGE` das doze linhas sem reticência,
  e tira a corrida do slot 1 inteira;
- a do `--silhouette-closeups` elide o meio de cada linha com `...` e troca a
  tabela do slot 1 por uma glosa em português — `-- slot 1 (goalkeeper) --  (o
  pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)` — que a
  ferramenta nunca emite.

Todo número da glosa está certo, então nada está errado. O que se perde é o
leitor conseguir separar saída de ferramenta de comentário, num bloco que
existe para ser evidência.

## Evidência

```text
$ sed -n '118,126p' docs/tasks/looks/40-a-camera-do-close-up.md
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) ...,  1005 (3.9x)
  -- slot 1 (goalkeeper) --  (o pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)

$ WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... python tools/looks/confront.py --silhouette-closeups
  FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) with its own camera, 1005 with the full figure's (3.9x)
  -- slot 1 (goalkeeper), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
  SKIN      walk frame 12; band from row 35:  402 of 1922 ( 21%) with its own camera,  997 with the full figure's (2.5x)
```

## Causa raiz

A transcrição foi encurtada para leitura, e a frase de resumo foi escrita
**dentro** da cerca em vez de ao lado dela.

## Correção

Colar as seis linhas do slot 1 verbatim (são doze ao todo) e tirar a frase do
"pior caso" de dentro da cerca para a prosa acima. É o mesmo princípio da regra
do ciclo sobre transcrição em `CORR-*`: reescrever é falsificar a evidência.

## Arquivos

- docs/tasks/looks/40-a-camera-do-close-up.md

## Verificação

Toda linha dentro das duas cercas aparece verbatim na saída do comando nomeado
no topo do bloco — `diff` entre o trecho do arquivo e a saída filtrada do
`confront.py --silhouette-closeups` sai vazio.

## Log de Execução

### 2026-09-25 — triagem inline (`/rite:fix-all looks --plan`, Rite 0.8.0)

**REPRODUCED**, decidido inline por `rite reproduce --all --cycle looks --json` na HEAD `de066fd5`.

O `sed` devolve a mesma cerca com a frase do "pior caso" dentro dela: o sintoma. O `confront` não roda aqui pelo mesmo motivo da CORR-LOOKS-088 e não decide.

```text
$ sed -n '118,126p' docs/tasks/looks/40-a-camera-do-close-up.md
  -- slot 2 (outfield player), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3:  160 of 2682 (  6%) with its own camera, 2452 with the full figure's (15.3x)
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) ...,  1005 (3.9x)
    H.COL     walk frame 12; band from row 35:  299 of 2373 ( 13%) ...,   899 (3.0x)
    H.F.COL.  walk frame 12; band from row 35:  266 of 2516 ( 11%) ...,  1016 (3.8x)
    HAIR      walk frame 12; band from row 35:  286 of 1972 ( 15%) ...,   716 (2.5x)
    SKIN      walk frame 12; band from row 35:  297 of 1897 ( 16%) ...,   915 (3.1x)
  -- slot 1 (goalkeeper) --  (o pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)
$ WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... python tools/looks/confront.py --silhouette-closeups
confront FAILED: SLPM-87056_1.sav was recorded on 'C:\\games\\ps1\\work\\we2002-english.cue', and this cycle drives '...'.  The file name cannot tell you this: both releases boot the serial SLPM-87056, so a state made on the Japanese disc carries the same name and brings unreadable menus with it.
[exit 1]
```
