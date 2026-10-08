---
id: CORR-K3D-012
---

# CORR-K3D-012 — "Posed alike" do G3 é verdade por construção, não medição

Origin: [K3D-TASK-07](/docs/tasks/kits-3d/07-medir-geometria-edt-mod.md)

## Problem

`run_edt_arms`, da [K3D-TASK-07](/docs/tasks/kits-3d/07-medir-geometria-edt-mod.md), preenche `shared[name]` a partir de `scene.pose`. Só que
`scene.pose` dá a cada seção a transformação do nome da peça dela
(`out[where] = by_name[name]`). As seções 1/12, 2/13, 3/14 e 4/15 têm o mesmo nome por
construção, então a conferência nunca imprime "posed apart" com as duas seções posadas.
O G3 mesmo assim afirma "As duas figuras posam cada peça de braço igual" como resultado.
O caso do selftest "an arm the two figures pose apart fails" injeta
`{"upper arm a": False}` no juiz, e portanto nunca exercita a medição.

## Evidência

```text
$ grep -n "posed alike\|posam cada peça" docs/KITS-AJUSTES-3D.md
110:  upper arm a EDT_MOD.BIN sections 1 12, posed alike
...
146:- **As duas figuras posam cada peça de braço igual** ("posed alike"). As seções 1 e 12, 2 e 13, 3 e
$ sed -n 802,813p tools/looks/scene.py
    by_name = {piece["piece"]: piece ...}
    for where, name in piece_names(disc).items():
        ...
        out[where] = (matrix, place)
$ grep -n "placed = \|shared\[name\]" tools/kits/oracle.py
    placed = {repr(pose.get((layout.EDT_MOD, at))) for at, n in arms if n == name}
    shared[name] = len(placed) == 1
```

## Root cause

A conferência compara uma tabela de consulta com ela mesma. Que o jogo pose a seção 12
do goleiro como a seção 1 do jogador é suposição que `piece_names`/`scene.pose` herdam do
ciclo `looks`; esta task não a mediu (inferido do código, não testado no emulador).

## Fix

No G3 de `docs/KITS-AJUSTES-3D.md`, dizer que isso decorre de `scene.pose` atribuir por
nome e citar a origem da suposição. Ou trocar `shared` em `tools/kits/oracle.py` por uma
comparação que possa divergir — a matriz de GTE por peça de cada figura, lida do jogo — e
plantar um controle contra ela.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- docs/KITS-AJUSTES-3D.md
- tools/kits/selftest.py

## Verificação

```sh
grep -n "posed alike\|posam cada peça" docs/KITS-AJUSTES-3D.md
```

Hoje devolve a afirmação sem ressalva; depois, uma com ressalva — ou o oráculo tem de
tirar `shared` de outra fonte que não `scene.pose`.

## Log de Execução
