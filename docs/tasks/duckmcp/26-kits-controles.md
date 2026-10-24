---
id: DMCP-TASK-26
---

# DMCP-TASK-26 — `kits`: controles, `COPIED` e monkeypatch reapontados

## Goal

`fork-joystick-let-through`, `looks-oracle-joystick-unasked` e `replay-capture-joystick-late` plantam no arquivo onde o código mora agora; `COPIED` inclui `tools/duckmcp`; o monkeypatch de `kits/selftest.py` troca `duckmcp.fork.joysticks` e `duckmcp.fork.launch`; um controle novo cobre a guarda de joystick do `dump_slot`.

## Arquivos a criar ou modificar

- In:
  - os três arquivos
  - `tools/duckmcp/selftest.py`: encolher no mesmo commit as entradas do `PENDING` da regra (b) que esta task remove; sem isso o check de entrada velha fica vermelho (CORR-DMCP-023)
- Out:
  - —

## Done criteria

- [x] `python3 tools/kits/controls.py` sai 0, com a contagem antes e depois no Log
- [x] o controle novo do `dump_slot` aparece vermelho, visto no Log
- [x] `grep -n 'pes2/fork.py' tools/kits/*.py` não acha nada
- [x] `ctest --test-dir build -R kits_selftest` passa

## Notes

## Log de Execução

Estado encontrado: três dos quatro pontos já estavam feitos por tasks anteriores. `fork-joystick-let-through` já plantava em `duckmcp/fork.py` (DMCP-TASK-12), `looks-oracle-joystick-unasked` em `looks/oracle.py` e `replay-capture-joystick-late` em `kits/replay.py`, os dois sobre `fork.refuse_joysticks()` do `duckmcp`. `COPIED` já trazia `tools/duckmcp` em `kits/controls.py` e em `kits/ui_check.py`, e o monkeypatch já trocava `duckmcp.fork.joysticks`/`launch`. Faltavam duas coisas.

- `kits/selftest.py` `_live_guard_checks`: o `import fork` do shim de `tools/pes2` (a entrada DMCP-TASK-26 do `PENDING` da regra (b)) virou `from duckmcp import fork`. A entrada saiu do `PENDING` em `tools/duckmcp/selftest.py`.
- A check nova `oracle.py dump_slot refuses a plugged-in controller before it boots the fork`: com `duckmcp.fork.joysticks` devolvendo `js0` e `launch` levantando erro, `kits/oracle.py` `dump_slot` tem que sair por `fork.Fail`. O controle `oracle-dump-joystick-unasked` tira o `fork.refuse_joysticks()` do `dump_slot`.
- Fora disso, só docstrings: as de `kits/controls.py` e `kits/ui_check.py` diziam que o `duckmcp` era copiado por causa do shim `pes2/mcp.py`.

Controles, antes (árvore da HEAD extraída por `git archive` num diretório à parte) e depois:

```
$ python3 <HEAD>/tools/kits/controls.py
controls: 87 of 87 red
$ python3 tools/kits/controls.py; echo exit $?
controls: 88 of 88 red
exit 0
```

O controle novo, vermelho:

```
$ python3 tools/kits/controls.py --only oracle-dump-joystick-unasked
  base   unplanted sandbox            selftest exit 0
  RED    oracle-dump-joystick-unasked kits/oracle.py :: dump_slot
controls: 1 of 1 red
```

Regra (b), antes e depois:

```
antes:  ok    rule (b): PENDING lists 8 site(s) in 8 entries, audit.py counts 8
        audit: 8 raw site(s) in 8 file(s)
depois: ok    rule (b): PENDING lists 7 site(s) in 7 entries, audit.py counts 7
        by category: import 0, client 0, sys.path 7
        audit: 7 raw site(s) in 7 file(s)
```

`grep -n 'pes2/fork.py' tools/kits/*.py` não acha nada (exit 1). `ctest --test-dir build -R kits_selftest`: `100% tests passed, 0 tests failed out of 1`.

Repassado da DMCP-TASK-25, fora dos arquivos desta task: o `main` do `kits/oracle.py` não converte `Fail` em código de saída, então a corrida que chama `dump_slot` (com `--cue` ou a variável do `.cue`) termina, com controle plugado, em traceback em vez de sair 1.
