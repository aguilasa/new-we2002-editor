---
id: CORR-K3D-034
---

# CORR-K3D-034 — Item 7 do G8 generaliza "texel puro em toda seção" e chama de frente a comparação com as costas

Origin: [K3D-TASK-19](/docs/tasks/concluidos/kits-3d/19-medir-capitao-linha-replay.md)

## Problem

O item 7(a) do G8, da [K3D-TASK-19](/docs/tasks/concluidos/kits-3d/19-medir-capitao-linha-replay.md), diz que a distância ao texel puro é menor que ao texel modulado
"em toda seção com pixel próprio". Na captura do Balaban, a seção 96 tem `far` 8,07 contra
7,67 do modulado — ali o modulado está mais perto —, e a 95 é quase empate (3,08 contra
3,10). Além disso, as notas de histograma "de frente" (0,37/0,39/0,38) comparam a frente da
aba com a primeira captura do jogo, que é as costas do jogador, porque nenhuma frente do
jogo é comparada. O texto se lê como frente contra frente.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 10 --focus 2 --frame-json work/kits-oracle/replay-10-2.json | grep -E '^ +9[56]: +[0-9]+ px'
     95:   30 px; game (6.4 7.4 12.2), texel (8.7 9.5 14.3) (far 3.08), texel x colour/128 (7.7 8.5 13.3) (far 3.10)
     96:    9 px; game (6.1 7.2 12.0), texel (13.4 13.8 16.6) (far 8.07), texel x colour/128 (12.4 12.8 15.6) (far 7.67)
$ grep -n 'em toda seção com pixel próprio' docs/KITS-AJUSTES-3D.md
1385:   texel modulado em toda seção com pixel próprio ...
```

Pelo revisor, `--replay-confront 9 --focus 3` no `:98` termina com `the game's frame (the
first capture, the player's back): work/kits-oracle/replay-9-3-frame.png`.

## Root cause

Hipótese: a conclusão foi generalizada das seções do Bokšić para as três capturas.

## Fix

No item 7 do G8 em `docs/KITS-AJUSTES-3D.md`, restringir a afirmação às seções em que ela
vale e nomear a 96 do Balaban (9 px, `far` 8,07/7,67) como exceção. Dizer que as duas notas
da aba são contra as costas do jogo.

## Arquivos a criar ou modificar

- docs/KITS-AJUSTES-3D.md

## Verificação

```sh
grep -n 'em toda seção com pixel próprio' docs/KITS-AJUSTES-3D.md
```

Depois, ou não imprime nada, ou a frase vem seguida da exceção da 96.

## Log de Execução

### 2026-10-12 — a afirmação do texel puro restrita, e as costas do jogo nomeadas

Triagem inline (`rite reproduce --all --cycle kits-3d`): **REPRODUCED** na HEAD `d348951`. Saíram as
linhas `95:` (`far 3.08`, `3.10`) e `96:` (`far 8.07`, `7.67`), e o `grep` achou a linha 1385.

Medido, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin` e as linhas `far` de
`--replay <slot> --focus <K> --frame-json work/kits-oracle/replay-<slot>-<K>.json`:
- Bokšić, slot 9 e slot 10: o texel puro fica mais perto do pixel do jogo em todas as seções com
  pixel próprio (slot 9: 2, 3, 90, 7, 9, 8, 10; slot 10: 2, 95, 96, 93, 98, 7, 9, 8, 10).
- Balaban: o texel puro também fica mais perto, menos em duas seções.
  - A 95 empata (30 px, 3,08 contra 3,10).
  - A 96 vira (9 px, 8,07 contra 7,67).

Conserto, no item 7 do G8:
- (a) Restrito ao que vale, com a 95 e a 96 do Balaban nomeadas como exceção. São as seções de menos
  pixel da captura.
- (b) Diz que a aba de costas e a de frente são as duas comparadas contra **as costas** do jogo, a
  primeira captura. É a linha `the game's frame (the first capture, the player's back)` que o
  `--replay-confront … --focus` imprime, no bloco colado do G8. As notas não mudaram.

Verificação: `grep -n 'em toda seção com pixel próprio' docs/KITS-AJUSTES-3D.md` imprime a linha
1397, agora seguida da exceção da 96.

Varredura: `grep -n 'texel puro\|0,37 de frente'` no G8 e na task 19. A linha 933 é o goleiro da
K3D-TASK-17, outra medição, e a 959 é sobre o `core/raster.py`. Nenhuma muda.
- **Closed** — commit `6fafdf41` (2026-10-12): docs(kits): restrict the pure-texel claim in G8 and say the tab is held against the game's back
  - Files (`git show --name-status 6fafdf41`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/CORR-K3D-034.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
