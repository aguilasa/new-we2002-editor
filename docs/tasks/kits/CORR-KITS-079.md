---
id: CORR-KITS-079
---

# CORR-KITS-079 — Rodar o --attach no slot de manga curta e sustentar a frase da imagem de uniforme

Origin: [KITS-TASK-46](/docs/tasks/kits/46-manga-curta-partida.md)

## Problem

O Escopo da KITS-TASK-46 diz que o `--attach` roda no slot novo, de manga curta. Ele só rodou sobre o save antigo do slot 6, de manga longa, antes de o usuário regravá-lo: o `work/kits-oracle/attach-6.json` que o `--frame-json` leu era esse quadro velho, que mostra `93 95 96 98` e passa. O julgamento do `--attach` só conhece a seção 93, então uma corrida ao vivo sobre o estado de manga curta de verdade sai 1. E a §4.3 afirma "Os braços curtos amostram a imagem de uniforme", mas nada que a task rodou atribui primitivas das páginas de kit às seções de braço curto. Medido: só as seções 3 e 4 (e as 57 e 59 do goleiro) aparecem nas páginas de kit; as 5 e 6 não aparecem.

## Evidência

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue python3 tools/kits/oracle.py --attach 6
  player  0 ( 34 prims, CLUT (0,487)): 2 3 7 8 9 10
  player  2 ( 31 prims, CLUT (0,486)): 2 3 4 7 8 9 10
  player  5 ( 23 prims, CLUT (0,486)): 56 57 59 61 62 63 64
  4 primitive(s) whose texels sections 3 57 all hold: left out
  3 primitive(s) whose texels sections 4 90 all hold: left out
  FAIL  no player draws section 93
(exit 1)
$ grep -n 'Os braços curtos amostram' docs/PLAN-KITS-PY.md
690:...
```

## Root cause

Provavelmente, depois de desbloqueada a task, só `--attach-matrix` e `--sleeves` foram refeitos; o julgamento do `--attach` (`attach_judge`, com `ARMBAND_SECTION`/`REPLACED_SECTION`) não recebeu a tabela `SLEEVE_LENGTHS`.

## Fix

Em `tools/kits/oracle.py`, dar `--sleeve-length` ao `--attach` e fazer o `attach_judge` usar `SLEEVE_LENGTHS[length]` (braçadeira 90 no lugar da 4); refazer no slot 6. Na §4.3 de `docs/PLAN-KITS-PY.md`, trocar a frase pelo que foi medido: que seções de braço curto amostram a imagem de uniforme (3 e 4 vistas; 5 e 6 não vistas nas páginas de kit).

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/PLAN-KITS-PY.md`

## Verificação

`python3 tools/kits/oracle.py --attach 6 --sleeve-length short` (com o ambiente acima) sai 0. Hoje a opção não existe, e `--attach 6` sai 1.

## Log de Execução

Reproduzido em 2026-10-06. A opção `--sleeve-length` não existia no `--attach`, e com ela
acrescentada a corrida ao vivo no slot 6 (manga curta, regravado pelo usuário) sai 1:

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue python3 tools/kits/oracle.py --attach 6 --sleeve-length short
  frame kept at work/kits-oracle/attach-6.json (--frame-json reads it back)
  180 figure primitive(s); by the file their texels are in: MODEL.BIN only 174, EDT_MOD.BIN only 0, both 0, neither 6
  4 primitive(s) whose texels sections 90 91 all hold: left out
  3 primitive(s) whose texels sections 4 90 all hold: left out
    player  0 ( 34 prims, CLUT (0,487)): 2 3 7 8 9 10
    player  1 ( 31 prims, CLUT (0,486)): 2 3 7 8 9 10
    player  2 ( 31 prims, CLUT (0,486)): 2 3 4 7 8 9 10
    player  3 ( 31 prims, CLUT (0,487)): 2 3 4 7 8 9 10
    player  4 ( 30 prims, CLUT (0,487)): 2 3 4 7 8 9 10
    player  5 ( 23 prims, CLUT (0,486)): 56 57 59 61 62 63 64
  short sleeves: the armband is 90, in place of 4
  FAIL  no player draws section 90
```

A causa vai além da tabela. A seção 90 tem 5 quads no disco e só 1 deles é dela (os outros estão
também na 4 ou na 91), e esse único não é desenhado neste quadro. Nenhum jogador pode então ser
nomeado pela 90 por texel. Os capitães aparecem só como jogadores de linha sem a 4 (os jogadores
0 e 1, um de cada CLUT).

Decisão do dono do repositório, nesta sessão: **julgar só o que os texels decidem**.

Conserto em `tools/kits/oracle.py`:

- `--attach` aceita `--sleeve-length`, e o `attach_judge` recebe a seção substituída de
  `SLEEVE_LENGTHS`.
- `own_quads` conta os quads próprios da braçadeira, e o `run_attach` imprime quantos estão no
  quadro.
- Sem quad próprio no quadro, o julgamento exige duas coisas: a braçadeira em quads
  compartilhados, e alguns jogadores de linha sem a peça substituída enquanto outros a desenham.
  A troca fica para o `--attach-matrix`, que a julga pelos ponteiros.
- O `--plant-attach` passou a dar 94 como braçadeira no lugar do vizinho do comprimento (`98`,
  `6`).

`tools/kits/selftest.py` ganhou três casos do caminho curto. A §4.3 troca a frase "Os braços
curtos amostram a imagem de uniforme" pelo que o `--attach` vê: 3 e 4, e 57 e 59 do goleiro.

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --attach 6 --sleeve-length short --frame-json work/kits-oracle/attach-6.json
  section 90 on the disc: 5 quad(s), 1 of them its own; 0 own quad(s) in this frame
  no quad of its own in the frame: no player is named by it alone, and the swap is --attach-matrix's to judge (by the pointers)
  ok    the figure is MODEL.BIN's; section 90 is drawn in shared quads, and the outfield players without 4 are the captains
(exit 0)
$ … --attach 6 --sleeve-length short --plant-attach --frame-json work/kits-oracle/attach-6.json
  PLANT  section 94 named the armband, in place of 6
  FAIL  of 5 outfield player(s), 0 draw section 6: no captain is seen by its absence
(exit 1)
$ … --attach 5 --frame-json work/kits-oracle/attach-5.json
  section 93 on the disc: 9 quad(s), 8 of them its own; 6 own quad(s) in this frame
  ok    the figure is MODEL.BIN's, and section 93 takes the place of 97
$ … --attach 5 --plant-attach --frame-json work/kits-oracle/attach-5.json
  FAIL  of 5 outfield player(s), 5 draw section 98: no captain is seen by its absence
(exit 1)
$ python3 tools/kits/selftest.py | grep "short sleeves"
  ok    oracle --attach: short sleeves, 90 only in shared quads and a captain without 4, holds
  ok    oracle --attach: short sleeves where every outfield player draws 4 fail
  ok    oracle --attach: short sleeves with 90 nowhere in the frame fail
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py | tail -1
controls: 28 of 28 red
```

O `work/kits-oracle/attach-6.json` antigo era o quadro de manga longa de antes da regravação.
Ficou copiado no scratchpad, e a corrida ao vivo acima o substituiu pelo quadro de manga curta.
