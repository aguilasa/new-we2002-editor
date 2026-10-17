---
id: KRP-TASK-24
---

# KRP-TASK-24 — A pele do corpo segue a Cor da Pele do painel da cabeça

## Goal

Na figura da aba, trocar a Cor da Pele no painel da cabeça muda também a pele do corpo (braços, pernas, mãos), pela regra que o ciclo `looks` mediu na `LOOKS SET`, como o [§3.3](/docs/PLAN-KITS-REPLAY.md#3.3) decide.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py` (`scene_of` monta a figura com o `skin_colour` do jogador)
  - `tools/kits/ui_check.py` (o `player_judge` exige o corpo diferente entre duas peles, com planta)
  - `tools/kits/selftest.py`
  - `docs/PLAN-KITS-REPLAY.md` (§3.3: a decisão)
- Out:
  - o `match_scene` (a aba não o desenha; §3.3)
  - cabelo e barba: só a cabeça os tem

## Done criteria

- [x] sem a opção, o digest de `cli.py figure` é o de antes da task
- [x] `cli.py figure … --player D-L3-H-A-A` contra `--player A-L3-H-A-A`: toda primitiva fora da cabeça que muda de CLUT desce 3 linhas, e alguma muda, impresso por comando versionado
- [x] o `kits_ui` exige o corpo (abaixo da cabeça) diferente entre as duas peles, e a planta que monta o corpo na pele de referência fica vermelha
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Decisão do usuário (2026-10-16), vendo o painel da KRP-TASK-22: "se mudar a cor da cabeça, tem que mudar a cor do corpo". Revoga, na aba, o "inclusive a pele do corpo" do §3.2.

## Log de Execução

- **done** (2026-10-16): o `scene_of` monta a figura com o `skin_colour` do jogador no lugar do da tupla de referência, e a cabeça entra depois pela regra do §3.1. A pele do corpo segue a regra da `LOOKS SET` (CORR-LOOKS-103). O `match_scene` não muda (§3.3).

Achado ao mexer no `player_judge`: desde a KRP-TASK-22, a comparação "reference × Croatia 11" media o painel aparecendo, não a cabeça. A captura de referência saía sem a caixa marcada (painel oculto, vista de 940 px), e deu 108094 px no Log da 22. Agora a referência é capturada com a caixa marcada e a tupla `A-A1-A-A-A` (`REFERENCE_LOOKS`), e a diferença volta a ser da cabeça: 7449 px. Com isso a planta `Player's head ignored` derruba as três comparações, não só duas.

Sem a opção, o digest é o de antes (HEAD `34763c76` contra a árvore da task):

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22; … --tag 22 --match --set 1   (> digest-before.txt / digest-after.txt)
$ diff work/krp24/digest-before.txt work/krp24/digest-after.txt && echo SAME
SAME
```

O corpo entre peles A e D sai do `kits_image` (`selftest.py --image`, `_player_skin_image_checks`); a planta `the body's skin not moved` derruba o `kits_ui`:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits -V
1/5 Test #18: kits_selftest ....................   Passed  310.73 sec
19:   ..... figure 0, skin A to D: 226 of 575 body primitive(s) move, by [3] row(s)
19:   ..... figure 1, skin A to D: 70 of 611 body primitive(s) move, by [3] row(s)
2/5 Test #19: kits_image .......................   Passed   26.93 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
21:   ok    3D TEX_14: Player's head draws the looks tuple's head, and two players apart only in hair colour are drawn apart (reference against Croatia 11 7449 px, Croatia 11 against Croatia 2 617 px, Croatia 11 against Croatia 11 skin D 4238 px below the head)
21:         plant 'Player's head ignored': reference and Croatia 11 draw the same 3D view; Croatia 11 and Croatia 2 draw the same 3D view; Croatia 11 and Croatia 11 skin D draw the same body: the skin stayed on the head
21:   ok    plant 'Player's head ignored' fails the player head judge
21:         plant 'the body's skin not moved': Croatia 11 and Croatia 11 skin D draw the same body: the skin stayed on the head
21:   ok    plant 'the body's skin not moved' fails the player head judge
21: kits_ui: 0 failure(s)
4/5 Test #21: kits_ui ..........................   Passed  240.25 sec
5/5 Test #22: kits_replay ......................   Passed   11.25 sec
The following tests passed:
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 81 of 81 red
```

A planta do `kits_ui` não tem par no `controls.py`: a regra está no `scene_of`, que só roda com o disco, e o sandbox dos controles corre sem ele (mesma razão do §3.2 para o `head --drawn`).
- **Closed** — commit `a0bec3f8` (2026-10-16): feat(kits): the body's skin follows the player's skin colour
  - Files (`git show --name-status a0bec3f8`):
    - `M docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md`
    - `M tools/kits/core/figure.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui_check.py`
- **Reviewed** (2026-10-17) at `212e579c`: CORR-KRP-027, CORR-KRP-028
