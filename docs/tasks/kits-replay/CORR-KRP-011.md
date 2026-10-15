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

**2026-10-15.** Reproduzido na HEAD antes do conserto: a lista `args` de `confront_tab` não tinha
`--kit-set`, e o `app.py` cai no default, set 1.

```text
$ grep -c -- '"--kit-set"' tools/kits/replay.py
0
$ grep -n -- '--kit-set' tools/kits/replay.py tools/kits/ui/app.py
tools/kits/ui/app.py:935:    parser.add_argument("--kit-set", type=int, choices=(1, 2), default=1,
```

Conserto: em `confront_tab` (`tools/kits/replay.py`) a lista de argumentos do `app.py` passa a levar
`--kit-set` com o `set` que `tab_args` devolveu, quando ele não é `None` — o mesmo set que o JSON
declara em `tab.set`. Com `None` o argumento fica de fora e o `app.py` segue no default, como antes.

```text
$ grep -q -- '"--kit-set"' tools/kits/replay.py; echo $?
0
$ grep -n -A3 -- '"--kit-set"' tools/kits/replay.py
427:        args += ["--kit-set", str(asked["set"])] if asked["set"] is not None else []
428-        args += ["--armband"] if asked["armband"] else []
429-        args += ["--long-sleeves"] if asked["long_sleeves"] else []
430-        args += ["--number", str(asked["number"])] if asked["number"] is not None else []
```

O `confront --tab` não foi rodado aqui: ele sobe o `app.py` no `:98`. Nas cinco capturas da task o
`set` é 1 ou `None`, então os números do Log da KRP-TASK-06 não mudam.
- **Closed** — commit `8a0ffc09` (2026-10-15): fix(kits): confront --tab passes the measured --kit-set to app.py
  - Files (`git show --name-status 8a0ffc09`):
    - `M docs/tasks/kits-replay/CORR-KRP-011.md`
    - `M tools/kits/replay.py`
