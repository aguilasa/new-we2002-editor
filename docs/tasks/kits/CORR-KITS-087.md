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
