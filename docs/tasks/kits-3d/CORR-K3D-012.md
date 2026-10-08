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

- 2026-10-08 — triagem inline: **REPRODUCED**. O G3 afirmava "As duas figuras posam cada peça de
  braço igual" sem ressalva; `oracle.py:2448-2449` monta `shared` a partir de `scene.pose`, que pose
  por nome.
- Escolhido o primeiro caminho da CORR: dizer o que a conferência é. Medir a matriz do GTE por peça,
  lida do jogo, fica para quem precisar dela.
  - `oracle.py`: a saída diz `posed alike by name`; docstring do módulo e comentário no laço dizem
    que a comparação é por construção e não pode dar "posed apart".
  - `selftest.py`: o caso sintético virou "the judge refuses an arm reported posed apart", com
    comentário de que só o juiz é exercitado.
  - G3: o item diz "por construção, não por medição", cita o `scene.pose` e a origem da suposição
    (ciclo `looks`). A transcrição do G3 foi refeita: `diff` contra a saída de
    `oracle.py --edt-arms` vazio.
- Verificação: o `grep` agora devolve `posed alike by name` nas quatro linhas da transcrição e o item
  150 com a ressalva. `selftest.py`: `kits_selftest: 0 failure(s)`; `selftest.py --image`:
  `figure: 0 failure(s)`, rc=0; `controls.py`: `controls: 34 of 34 red`.
- **Closed** — commit `c568724` (2026-10-08): docs(kits): say the arm pose check is by name, not measured
  - Files (`git show --name-status c568724`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/CORR-K3D-012.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
