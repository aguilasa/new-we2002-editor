---
id: CORR-DMCP-031
---

# CORR-DMCP-031 — O check de duas seções numa carga de matriz do looks não afirma nada

Origin: [DMCP-TASK-22](/docs/tasks/duckmcp/22-looks-oracle-session.md)

## Problem

O self-check do `tools/looks/oracle.py` tem o check "two sections pointed at by one matrix load are
refused" (`tools/looks/oracle.py:9675`) escrito como `attempt(nome, OracleError, lambda: …)`. O
`attempt` do `tools/looks/harness.py:73` é `attempt(name, fn, default=None)`: roda `fn()` e só
acusa exceção inesperada. Com essa ordem, quem roda é `OracleError()` — que constrói a exceção e não
a levanta —, e o `lambda` que chama `_drawn_section` vira o `default` e nunca roda. O check passa
sempre, sem medir se `_drawn_section` recusa duas seções. Anterior ao ciclo `duckmcp`; achado na
DMCP-TASK-22.

## Evidência

Numa cópia da árvore (`git archive HEAD tools`), `_drawn_section` plantado para devolver `None` logo
na entrada — nunca recusar —, e o self-check continua verde:

```text
$ T=$(mktemp -d) && git archive HEAD tools | tar -x -C "$T" && python3 - "$T" <<'EOF'
import sys
p = sys.argv[1] + "/tools/looks/oracle.py"; s = open(p).read()
i = s.index("def _drawn_section"); j = s.index(":\n", s.index(")", i)) + 2
open(p, "w").write(s[:j] + "    return None  # planted: never refuses\n" + s[j:])
EOF
$ (cd "$T" && python3 tools/looks/oracle.py --check | tail -1; echo "exit=${pipestatus[1]}")
oracle.py: 0 failure(s)
exit=0
```

## Root cause

Os argumentos de `attempt` estão na ordem de `refuses(name, fn, fragment, kind)` ou de um
`assertRaises(kind, fn)`: a intenção era "exige `OracleError`", e o helper certo para isso é o
`refuses`.

## Fix

Em `tools/looks/oracle.py:9675`: trocar o `attempt` por `refuses(nome, lambda: _drawn_section(…),
<trecho da mensagem>, kind=OracleError)`, com o trecho que identifica a recusa de duas seções.
Varrer o arquivo atrás de outros `attempt(…, <Classe de exceção>, …)` na mesma forma.

## Arquivos a criar ou modificar

- `tools/looks/oracle.py`

## Verificação

- a planta da Evidência deixa `python3 tools/looks/oracle.py --check` vermelho, com a linha do check
  colada;
- sem a planta, `--check` volta a `0 failure(s)`;
- `python3 tools/looks/selftest.py` sai 0.

## Log de Execução

**Reprodução (2026-10-25, HEAD `cdebb44f`, `rite reproduce --all --cycle duckmcp`):** REPRODUCED — com
`_drawn_section` plantado para devolver `None`, o self-check segue verde:

```text
$ (cd "$T" && python3 tools/looks/oracle.py --check | tail -1; echo "exit=${pipestatus[1]}")
oracle.py: 0 failure(s)
```

A causa confere: `attempt(name, fn, default=None)` (`tools/looks/harness.py:73`) recebia `OracleError`
como `fn` e o `lambda` como `default`.

**Conserto:** `tools/looks/oracle.py:9675` passou a `c.refuses(nome, lambda: _drawn_section(…),
"points into 2 sections at once", kind=OracleError)` — o fragmento é o da mensagem de
`_drawn_section`. Varredura de outros `attempt(…, <Classe>, …)` no arquivo e em `tools/`:

```text
$ grep -rnE 'attempt\(\s*"[^"]*",\s*[A-Z][A-Za-z]*(Error|Exception|Mismatch|Disc|Arrived)\b' tools/
$ grep -nE 'attempt\([^,]*,\s*$' tools/looks/oracle.py
9709:                got = attempt("main under a %s" % kind.__name__,
9808:    found = attempt("the chain of a synthetic boot segment",
10056:    counted, codes = attempt("walk one real node",
10104:    inside = attempt("compare with a rewritten primitive",
```

Os quatro multilinha restantes passam um `lambda`/função como segundo argumento (lidos um a um); o da
9675 era o único com classe.

**Controle** — a planta da Evidência sobre uma cópia de `tools/looks` + `tools/duckmcp` + `tools/pes2`
da árvore consertada:

```text
$ (cd "$T" && python3 tools/looks/oracle.py --check | grep -E "two sections|failure"; echo "exit=${pipestatus[1]}")
  FAIL  two sections pointed at by one matrix load are refused: did NOT refuse
oracle.py: 1 failure(s)
exit=1
```

**Verificação** na árvore entregue:

```text
$ python3 tools/looks/oracle.py --check | grep -E "two sections|failure"
  ok    two sections pointed at by one matrix load are refused
oracle.py: 0 failure(s)
$ python3 tools/looks/selftest.py 2>&1 | tail -2; echo "exit=$?"
controls: 0 failure(s)
looks_selftest: 0 failure(s)
exit=0
```
- **Closed** — commit `15e3538f` (2026-10-25): test(looks): the two-sections check refuses through c.refuses instead of asserting nothing
  - Files (`git show --name-status 15e3538f`):
    - `M docs/tasks/duckmcp/CORR-DMCP-031.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/looks/oracle.py`
