---
id: KITS-TASK-28
---

# KITS-TASK-28 — Confronto 3: `confront.py --score` com um uniforme que não é o `A4`

## Goal

O confronto por histograma de cor do `looks` refeito com o time da §4.1, titular e suplente, contra o quadro do emulador.

## Arquivos a criar ou modificar

- `tools/kits/confront.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [x] Os escores de titular e suplente colados, com o limiar que o `looks` usa
- [x] Controle: nosso titular contra o quadro do suplente do jogo reprova

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#5).

Da KITS-TASK-10: o `tools/kits/confront.py` já existe e é o confronto 2 (os pares de bandeira, `WE2002_KITS_CORPUS`), sem subcomando — rodar sem opção confronta os pares. O `--score` desta task entra como modo novo dele, sem mudar o que a corrida sem opção faz; o arquivo está na regra da fachada (`FACADE_CLIENTS` do `selftest.py`), então só importa `core.api`.

Da KITS-TASK-27: o "time da §4.1" é a partida **Escócia (`TEX_01`, titular) × Dinamarca (`TEX_13`, suplente)**, no slot 3 do emulador, cópia mestra em `work/kits-states/SLPM-87056_3.sav` (sha256 `5f392a12…`), gravado sobre `work/we2002-english.cue`. O quadro do jogo é de partida, não da `LOOKS SET`: câmera de transmissão, figuras pequenas, e o goleiro da Escócia na paleta de goleiro do conjunto **2** (§4.1) — o titular "inteiro" do nosso 3D não é exatamente o que está em campo.

## Log de Execução

### 2026-10-04

O `--score` entrou no `tools/kits/confront.py` como modo novo; a corrida sem
opção (confronto 2) não mudou, e o arquivo continua só com `core.api` e a
biblioteca padrão — o 3D é desenhado pela janela, lançada com o python do venv
no `:98`, e o PNG é lido por um leitor próprio.

Método: a métrica do `looks` (interseção de histograma a 5 bits por canal, o
quadro restrito às cores que o nosso render desenha). O quadro do jogo é o
`screen.png` que o `oracle.py --slot 3` grava; nele mediram-se seis caixas de
jogador de linha, três por time (`BOXES`), num zoom 2× com grade de 20 px. Os
goleiros ficam fora: não estão no quadro, e o da Escócia veste a paleta de
goleiro do conjunto 2 (§4.1). O nosso lado é a aba 3D de frente e de costas
(`--yaw 180` e `0`), figura de jogador.

O quadro se repete: duas corridas do `oracle.py --slot 3 --cue
work/we2002-english.cue` (a de `work/kits-oracle/match-3/` e outra no
scratchpad) deram o mesmo `screen.png`:

```
ee1bfba6e7dc03af8276130f6f25d8b71493aefdd3635dc4c6069ac009e9d8a6  …/match-again/screen.png
ee1bfba6e7dc03af8276130f6f25d8b71493aefdd3635dc4c6069ac009e9d8a6  work/kits-oracle/match-3/screen.png
```

Por isso o digest está no código (`FRAME_SHA256`), e outro quadro é recusado;
vermelho visto com uma cópia de um pixel trocado: `has sha256 8891e0bdb89a, not
the ee1bfba6e7dc… BOXES were measured on`, exit 1.

Critério 1 — `WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/confront.py --score`, exit 0:

```
  players on the pitch         ours TEX_01 set 1  ours TEX_13 set 2
  TEX_01 Scotland, first kit  0.770 (33.0 % kept)  0.429 (10.8 % kept)
  TEX_13 Denmark, second kit  0.349 (14.9 % kept)  0.759 (29.8 % kept)
confront 3: 2 of 2 team(s) score their own kit 0.05 over the other's
```

O limiar é o `KIT_CONTROL_MARGIN` do `looks`, 0,05. As vantagens, que a
corrida positiva imprime desde a CORR-KITS-051:

```
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/confront.py --score | grep lead
  TEX_01 players: our TEX_01 leads our TEX_13 by 0.342
  TEX_13 players: our TEX_13 leads our TEX_01 by 0.410
```

Critério 2 — `python3 tools/kits/confront.py --score --negative` troca os
renders, e os dois times reprovam (exit 0 só quando reprovam):

```
  red   the TEX_01 players score our TEX_13 0.429, TEX_01 0.770: a lead of -0.342, under 0.05
  red   the TEX_13 players score our TEX_01 0.349, TEX_13 0.759: a lead of -0.410, under 0.05
confront 3 --negative: the swapped renders give 2 failure(s) of 2 -- the control holds
```

Limite assumido: um quadro, uma partida, seis jogadores; a frase diz este
confronto, não toda partida.
- **Closed** — commit `165495d` (2026-10-04): feat(kits): confront.py --score judges the 3D against the match frame
  - Files (`git show --name-status 165495d`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/28-confronto-3.md`
    - `M tools/kits/confront.py`
- **Reviewed** (2026-10-04) at `78b9ea2`: CORR-KITS-051
