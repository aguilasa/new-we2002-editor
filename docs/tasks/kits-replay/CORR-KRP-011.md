---
id: CORR-KRP-011
---

# CORR-KRP-011 — confront --tab não passa --kit-set ao app.py e o JSON declara um set que a aba não desenhou

Origin: [KRP-TASK-06](/docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md)

## Problem

`tab_args` tira `kit_set` de `replay.figure_tag`, que pode devolver o set 2, e o reporta no JSON como
`tab.set`, o que "a aba é pedida para desenhar". Mas `confront_tab` nunca passa `--kit-set`, então o
`app.py` desenha sempre o default, set 1 (`default=1`, `ui/app.py:935`).

Para uma figura que amostra a paleta do set 2, o JSON diz set 2, a aba desenhou o set 1, e o
histograma é comparado contra o uniforme errado. Nas cinco capturas da task `set` é 1 ou `None`, então
os números do Log não são afetados.

## Evidência

```text
$ grep -n -- '--kit-set' tools/kits/replay.py tools/kits/ui/app.py
tools/kits/ui/app.py:935:    parser.add_argument("--kit-set", type=int, choices=(1, 2), default=1,
$ grep -n "for kit_set, record in PLAYER_PALETTE.items()" -A2 tools/kits/core/replay.py
1011:        for kit_set, record in PLAYER_PALETTE.items():
1013:                return tag, kit_set
$ grep -c -- '"--kit-set"' tools/kits/replay.py
0
```

No `confront --tab --json` sobre `replay-9-3-R1.json` sai `"tab": {..., "set": 1, "tag": "22"}`, e o
`set` nunca vira argumento.

## Root cause

A lista `args` de `confront_tab` foi copiada das flags de figura, faixa, manga e número; o `set`
ficou de fora (o `confront.render` passa `--kit-set`).

## Fix

Em `confront_tab` (`tools/kits/replay.py`), acrescentar `["--kit-set", str(asked["set"])]` quando
`asked["set"]` não for `None`.

## Arquivos a criar ou modificar

- `tools/kits/replay.py`

## Verificação

```sh
grep -q -- '"--kit-set"' tools/kits/replay.py
```

Hoje sai 1. Depois do conserto tem de sair 0.

## Log de Execução
