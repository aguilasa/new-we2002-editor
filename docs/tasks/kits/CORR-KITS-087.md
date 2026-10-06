---
id: CORR-KITS-087
---

# CORR-KITS-087 — Fazer o juiz de partida afirmar que a mudança da braçadeira fica no braço

Origin: [KITS-TASK-47](/docs/tasks/kits/47-figura-partida-aba-3d.md)

## Problem

O critério 2 da KITS-TASK-47 exige que a captura difira "dentro do braço". O juiz de partida do `kits_ui` só confere três coisas: que algo mudou, que a mudança cabe em até 40 px em cada direção (`ARMBAND_BOX`) e que cobre no máximo 5 % da figura (`ARMBAND_SHARE`). Nunca confere onde a mudança está — e mesmo assim a linha `ok` sempre imprime "changes only a box on its arm". Uma braçadeira desenhada no antebraço, na cabeça ou numa perna, numa caixa pequena o bastante, passaria. O critério só vale hoje porque o revisor olhou a captura: a caixa da diferença (423,279)-(448,297) está no braço de uma figura com caixa (421,174)-(558,542).

## Evidência

```text
$ grep -n 'on its arm\|ARMBAND_BOX\|ARMBAND_SHARE\|if max(span)\|if pct' tools/kits/ui_check.py
835:             "only a box on its arm (%s)" % (MATCH_TAG, seen), bad)
    if max(span) > ARMBAND_BOX: ...
    if pct > ARMBAND_SHARE: ...      (nenhum teste da posição de `changed`)
$ ctest --test-dir build -R kits   (com WE2002_LOOKS_IMAGE e afins absolutos, DISPLAY=:98)
ok 3D TEX_14: ... changes only a box on its arm (337 px (1.3 % of the figure) in a 25x18 box)
```

## Root cause

O juiz foi escrito para separar "a braçadeira não muda nada" (a planta) de "a braçadeira muda algo pequeno"; a parte de localização do critério virou texto impresso, não asserção.

## Fix

No `match_judge` de `tools/kits/ui_check.py`, afirmar que a caixa mudada cai dentro de uma região de braço medida — derivada do core (a caixa projetada da seção 97/93 na vista do torso, por `api.match_figure`/`scene.parts`) ou guardada como constante medida com margem. Plantar a 93 numa posição que não é braço (a cabeça, ou o lugar da 98) e mostrar o juiz vermelho. Se não, tirar "on its arm" do texto `ok` e da afirmação do critério.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`

## Verificação

Numa cópia de rascunho, plantar em `tools/kits/core/figure.py` a braçadeira na posição da cabeça (em `match_order`: `if armband and section in (24, 30): section = rule["armband"]` no lugar da regra da 97) e rodar `DISPLAY=:98 XAUTHORITY= python tools/kits/ui_check.py`. Hoje o juiz de partida continua `ok`; depois do conserto tem de dar FAIL.

## Log de Execução

Reproduzido em 2026-10-06 sobre `9673ca0`, em parte.

- **O problema reproduz:** o `match_judge` não testava a posição de `changed`, e o texto `ok`
  dizia "on its arm" sem afirmar isso.
- **A Verificação não reproduz como escrita.** A planta da braçadeira na cabeça já ficava
  vermelha antes do conserto, pelo tamanho, e não pelo lugar. Pôr a 93 fora do braço muda o
  contorno da figura, a câmera reenquadra e a imagem inteira muda. A cabeça dá `spans 142x369,
  over 40` e 75,9 % da figura; o lugar da 98 dá `spans 135x363`.

Conserto em `tools/kits/ui_check.py`:

- O `match_judge` mede a caixa da mudança em fração da caixa da figura e afirma que ela cai num
  braço. `ARM_SIDE` diz que ela fica no terço externo de um dos lados (0,35). `ARM_ROWS` diz que
  fica entre 0,15 e 0,55 da altura, do ombro à cintura. Os dois têm margem sobre o medido, x
  0,01–0,20 e y 0,28–0,33.
- Planta nova `armband drawn on the head` em `core/figure.py` (`match_order`): a braçadeira no
  lugar da primeira peça, a cabeça.
- A docstring do módulo e a do juiz dizem isso.

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep -E "TEX_14|armband|kits_ui:"
  ok    3D TEX_14: the match player is drawn, and the captain's armband changes only a box on its arm (337 px (1.3 % of the figure) in a 25x18 box, x 0.01-0.20 y 0.28-0.33 of the figure's box)
        plant 'armband drawn as section 97': the armband changes nothing
  ok    plant 'armband drawn as section 97' fails the match judge
        plant 'armband drawn on the head': the armband's change spans 142x369, over 40; the armband's change is at x -0.01-1.01 y 0.00-1.00 of the figure's box, not on an arm (outer 0.35, rows 0.15-0.55); the armband changes 75.9 % of the figure, over 5.0
  ok    plant 'armband drawn on the head' fails the match judge
kits_ui: 0 failure(s)
$ … ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py | tail -1
controls: 28 of 28 red
```

Limite: a asserção de lugar não foi vista vermelha **sozinha**. Na planta da cabeça ela falha
junto com a de tamanho e a de fração. Achar uma braçadeira fora do braço que não mude o contorno
da figura pediria uma geometria que o jogo não desenha.
