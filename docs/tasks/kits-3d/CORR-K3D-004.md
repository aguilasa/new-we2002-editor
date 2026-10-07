---
id: CORR-K3D-004
---

# CORR-K3D-004 — Log da K3D-TASK-06 corta a saída do grep de chamadores

Origin: [K3D-TASK-06](/docs/tasks/kits-3d/06-fechamento-fase-2.md)

## Problem

No item 2 do Log da [K3D-TASK-06](/docs/tasks/kits-3d/06-fechamento-fase-2.md), a saída
do `grep -rn "planted_gap\|numbered_scene(\|numbered_indices("` aparece com quatro
linhas; as outras cinco (`api.py:124`, `api.py:140`, `ui_check.py:229`,
`selftest.py:1056`, `selftest.py:1063`) foram trocadas por uma nota, "(e os de
selftest/ui_check/api, que são teste, planta e fachada)". A transcrição não é a saída
da ferramenta, contra a regra de que número e saída no Log são colados dela.

## Evidência

```text
$ grep -rn "planted_gap\|numbered_scene(\|numbered_indices(" tools/kits/*.py tools/kits/ui/*.py tools/kits/core/*.py | grep -v "def " | wc -l
9
$ sed -n '/numbered_indices(/,/selftest\/ui_check/p' docs/tasks/kits-3d/06-fechamento-fase-2.md | grep -c '^tools/'
4
```

## Root cause

Hipótese: a saída foi aparada à mão para ficar legível, em vez de colada inteira.

## Fix

Em `docs/tasks/kits-3d/06-fechamento-fase-2.md`, colar a saída inteira de nove linhas e
pôr a nota sobre os cinco chamadores de teste, planta e fachada depois dela, em prosa;
ou estreitar o `grep` a `tools/kits/core/figure.py tools/kits/cli.py`, para que a saída
seja de fato as quatro linhas mostradas.

## Arquivos a criar ou modificar

- docs/tasks/kits-3d/06-fechamento-fase-2.md

## Verificação

O número de linhas `tools/` sob esse comando no Log tem de ser igual ao que o comando
imprime de fato:

```sh
grep -rn "planted_gap\|numbered_scene(\|numbered_indices(" tools/kits/*.py tools/kits/ui/*.py tools/kits/core/*.py | grep -v "def " | wc -l
sed -n '/numbered_indices(/,/selftest\/ui_check/p' docs/tasks/kits-3d/06-fechamento-fase-2.md | grep -c '^tools/'
```

Hoje dá 9 e 4; depois, os dois números iguais (ou o comando do Log estreitado).

## Log de Execução

- 2026-10-07 — triagem inline: **REPRODUCED**. Os dois comandos da Evidência davam `9` e `4`.
- Item 2 do Log da K3D-TASK-06 com a saída do `grep` colada inteira (nove linhas), e a nota
  sobre os cinco chamadores de teste, planta e fachada movida para prosa depois do bloco.
- Verificação: os dois comandos dão `9` e `9`.
