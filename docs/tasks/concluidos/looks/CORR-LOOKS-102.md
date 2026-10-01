---
id: CORR-LOOKS-102
---

# CORR-LOOKS-102 — Os limiares do oracle.py dependem da largura de janela salva no DuckStation de cada máquina

Origin: [LOOKS-TASK-08](/docs/tasks/concluidos/looks/08-de-onde-vem-o-boneco.md)

## Problem

No Linux, com os states aceitos (CORR-LOOKS-101), o `--check-live` recusa a
própria tela `LOOKS SET`: a média do quadro sai fora da faixa, embora a tela
seja a certa.

## Evidência

```text
$ python3 tools/looks/oracle.py --check-live
  shot slot1-goalkeeper  mean=0.168752 sd=0.187698  .../work/looks-shots/slot1-goalkeeper.png
oracle FAILED: the frame's mean is 0.168752, not the 0.182800 (+-0.006000) of the LOOKS SET screen
```

A captura do Linux tem 800×655, e a do Windows do mesmo slot tem 864×655 e média
0,182425. Os `settings.ini` das duas máquinas diferem, fora de caminhos, só em
`[UI]`: `MainWindowWidth = 864` no Windows e `800` no Linux. Com a janela do
jogo levada a 864×655 por `xdotool windowsize`, a mesma tela deu 0,183844.

## Root cause

O `take_screenshot` do fork sai do tamanho da janela do jogo
(`ScreenshotMode = ScreenResolution`). A janela é portanto instrumento de
medida, mas o tamanho dela vinha da configuração salva de cada máquina, que
nada conferia. `SCREEN_MEAN` e as caixas de região foram medidos no Windows,
a 864 de largura, e só valiam lá.

## Fix

Em `tools/looks/oracle.py`:

- `SHOT_SIZE = (864, 655)`, o tamanho em que os limiares foram medidos.
- `size_window()` leva a janela do jogo a esse tamanho no X, logo depois de a
  sessão subir, e espera a geometria assentar. No Windows não mexe: lá o
  `SetWindowPos` dimensiona a moldura e não a área cliente, e nenhuma corrida
  mediu a diferença; ele continua valendo a largura salva de 864.
- `Session.capture` recusa quadro de qualquer outro tamanho, dizendo o que
  ajustar. Numa máquina Windows com outra largura, o gate falha alto em vez de
  medir errado.

## Arquivos a criar ou modificar

- [tools/looks/oracle.py](/tools/looks/oracle.py)

## Verificação

```text
$ python3 tools/looks/oracle.py --check-live
  window sized 864x655, the measured frame
  shot slot1-goalkeeper  mean=0.182425 ...
  shot slot2-outfield  mean=0.183158 ...
oracle --check-live: 0 failure(s)
```

As duas médias são as que o docstring de `SCREEN_MEAN` registra do Windows,
ao dígito.

Controle negativo, `size_window` trocado por um que não faz nada:

```text
oracle FAILED: the emulator's frame is 800x655 and every threshold here was measured on 864x655 -- the screenshot takes the game window's size, so set the fork's [UI] MainWindowWidth to 864
```

`python3 tools/looks/selftest.py`: `looks_selftest: 0 failure(s)`.

## Log de Execução

- 2026-09-28 — diagnosticado pelo diff dos dois `settings.ini`; medido que
  864×655 devolve a média; corrigido; `--check-live` verde no Linux; controle
  negativo vermelho.
- **Closed** — commit `1843180` (2026-09-28): fix(looks): pin the game window to the frame the thresholds were measured on
  - Files (`git show --name-status 1843180`):
    - `A docs/tasks/looks/CORR-LOOKS-102.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/oracle.py`
