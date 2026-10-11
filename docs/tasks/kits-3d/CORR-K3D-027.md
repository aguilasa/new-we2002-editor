---
id: CORR-K3D-027
---

# CORR-K3D-027 — G8 diz que a K3D-TASK-18 repete os itens 3 a 5, mas o item 4 não é medido

Origin: [K3D-TASK-18](/docs/tasks/kits-3d/18-medir-os-22-replay.md)

## Problem

O parágrafo do G8 sobre a [K3D-TASK-18](/docs/tasks/kits-3d/18-medir-os-22-replay.md) diz que ela repete no focado os itens 3 a 5 da K3D-TASK-17.
O item 4 pede a braçadeira e os quatro braços na lista do jogo — xy de tela, página, CLUT,
zona e cor por vértice. O `--replay-field` não imprime dado de primitiva nenhum, e as
conclusões "Medido (K3D-TASK-18)" do G8 nada dizem do item 4. O objetivo da própria task
lista só as colunas da tabela: plano e entrega discordam.

## Evidência

```text
$ grep -n 'repete os itens 3 a 5' docs/KITS-AJUSTES-3D.md
727: ... repete os itens 3 a 5 da 17 no ...
$ git show 27f2565 -- tools/kits/oracle.py | grep -c 'shading_of\|section_samples\|zone'
0
```

## Root cause

Hipótese: a task restringiu o escopo à tabela e deixou o dado de primitiva de perto para a
K3D-TASK-19, e o G8 não foi atualizado para combinar.

## Fix

No parágrafo da K3D-TASK-18 no G8 de `docs/KITS-AJUSTES-3D.md`, dizer "itens 3 e 5" e
apontar o item 4 para a K3D-TASK-19. Ou acrescentar ao `--replay-field` as colunas do item 4.

## Arquivos a criar ou modificar

- docs/KITS-AJUSTES-3D.md (ou tools/kits/oracle.py)

## Verificação

```sh
grep -n 'repete os itens 3 a 5' docs/KITS-AJUSTES-3D.md
```

Hoje imprime a linha 727; depois, nada — ou a saída do `--replay-field` traz dado do item 4
por foco.

## Log de Execução

### 2026-10-11 — G8 diz itens 3 e 5, e o 4 vai para a K3D-TASK-19

Triagem inline (`rite reproduce --all --cycle kits-3d`): **REPRODUCED**. Na HEAD `75ae037`,
`grep -n 'repete os itens 3 a 5' docs/KITS-AJUSTES-3D.md` imprime a linha 727, e
`git show 27f2565 -- tools/kits/oracle.py | grep -c 'shading_of\|section_samples\|zone'` imprime `0`.

Caminho escolhido: o primeiro da CORR. O parágrafo da K3D-TASK-18 no G8 diz agora "itens 3 e 5" e
passa o item 4 à K3D-TASK-19, cujo parágrafo no mesmo G8 já pede "os itens 4 a 7 da 17" no Bokšić.
Acrescentar o item 4 ao `--replay-field` mediria primitivas de 22 figuras de costas e longe, o que a 19
mede de perto.

Verificação: `grep -n 'repete os itens 3 a 5' docs/KITS-AJUSTES-3D.md` não imprime nada (saída 1).
Varredura: `grep -rn 'itens 3 a 5\|3 a 5 da' docs/ tools/kits/` só acha o título desta CORR no
`fixes.json`.
