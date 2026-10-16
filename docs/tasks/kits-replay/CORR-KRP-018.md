---
id: CORR-KRP-018
---

# CORR-KRP-018 — Coluna de barba, match_scene com player e head --drawn sem controle plantado

Origin: [KRP-TASK-10](/docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md)

## Problem

A K2 da §9 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#9) pede que toda asserção nova venha
com um plant que a derrube, e que o Log mostre esse vermelho. Três veredictos ou caminhos de código
novos não têm controle no catálogo:

1. A asserção do selftest "the player's beard column moves to his beard colour". Ela fica vermelha
   quando plantada (abaixo), mas o `controls.py` não tem entrada para ela, então esse vermelho nunca
   apareceu no catálogo. A asserção "off the skin records … is the disc's" também não tem controle.
2. O caminho de jogador do `match_scene` (troca de seção mais `player_head_clut` no `order[0]`).
   Nenhum selftest, `kits_ui` ou checagem do oracle chama `match_figure` com `player=`, então quebrá-lo
   não deixa nenhum gate vermelho.
3. O `replay.py head --drawn` sai 1 quando há divergência, mas não tem plant, e nenhum gate nem o
   `check` o roda. O vermelho dele só foi visto na corrida ad hoc do revisor.

## Evidência

```text
$ python3 tools/kits/controls.py --list | grep player_head_clut
  figure-player-hair-unmoved   kits/core/figure.py :: player_head_clut
  figure-player-skin-unmoved   kits/core/figure.py :: player_head_clut
$ grep -n "player=" tools/kits/selftest.py tools/kits/oracle.py tools/kits/ui_check.py
(sem saída)
$ grep -n "drawn_head\|--drawn" tools/kits/*.py tools/kits/core/*.py
tools/kits/replay.py:18 / 1135   (só o uso e o argparse; nenhum gate chama)
```

Não há controle de coluna de barba.

Plants ad hoc, numa cópia de rascunho montada a partir da HEAD (`git archive HEAD tools | tar -x -C <tmp>`).

Trocando `        column += values["beard_colour"]\n` por `        column += 0\n` em
`tools/kits/core/figure.py`, dentro de `<tmp>/tools/kits`:

```text
$ python3 -c "import selftest
class C:
    def ok(self,n,c,d=''): print('PASS' if c else 'FAIL',n)
selftest._player_head_checks(C())"
FAIL figure.py: the player's beard column moves to his beard colour
```

Pelo mesmo método, trocando `        column += values["hair_colour"]\n` por `        column += 0\n`:

```text
$ WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head <repo>/work/kits-oracle/replay-10-2.json --drawn
... 17 differ: [[1, [32, 480], [16, 480]], ...]
0 of 1 drawn head(s) sample the game's CLUT on every primitive
```

## Root cause

A task catalogou plants só para a coluna de cabelo, a linha de pele e o gêmeo redirecionado; os
outros caminhos novos ficaram sem controle.

## Fix

Em `CONTROLS`, no `tools/kits/controls.py`:

- `figure-player-beard-unmoved`, plantando a linha de barba de `player_head_clut`;
- uma asserção de selftest ou de `kits_image` de que `match_figure(..., player="A-L3-B-A-B")` desenha
  a seção 46 com as CLUTs (32,480)/(160,480), mais um controle que plante a troca de CLUT de
  `number == order[0][0]` no `match_scene`;
- para o `head --drawn`, uma de duas: ligá-lo ao `replay.py check` (o gate `kits_replay`) com um
  controle em `drawn_head`, ou dizer na §3.2 que ele é relatório, não gate.

## Arquivos a criar ou modificar

- `tools/kits/controls.py`
- `tools/kits/selftest.py`
- `tools/kits/core/figure.py` (alvo dos plants)
- `tools/kits/replay.py`

## Verificação

```sh
python3 tools/kits/controls.py --list | grep -c "figure-player-beard-unmoved"
```

Hoje dá 0. Depois do conserto tem de dar 1, e `python3 tools/kits/controls.py` tem de continuar
terminando em `controls: N of N red`.

## Log de Execução
