---
id: CORR-KITS-018
---

# CORR-KITS-018 — Make cli.py import only core.api, and gate that rule

Origin: [KITS-TASK-08](/docs/tasks/concluidos/kits/08-selftest-e-ctest.md)

## Problem

A verificação de fase 1 do perfil, "cli.py só importa core.api e stdlib (§3.1)", falha na HEAD: o `cli.py` importa `core.survey` direto e o usa nas linhas 53-54, 95-97, 135-136 e 150-152. A KITS-TASK-08 montou a varredura de regras do §3.1 (`core_rule_breaks`), mas ela só cobre o `core/` (sem `print`, `exit` nem Qt) e não confere a regra de só-fachada no `cli.py`, então o gate fica verde. O import veio do fc5717ae, não desta task, e já está registrado como exceção na CORR-KITS-001, passada para a KITS-TASK-09. O que é novo aqui é a falta de gate para a regra.

## Evidência

```text
$ grep -n "^from core" tools/kits/cli.py
27:from core import api  # noqa: E402
28:from core import survey as survey_mod  # noqa: E402
$ git log -L28,28:tools/kits/cli.py --oneline -s | head -1
fc5717ae feat(kits): survey the TEX containers in core, print it from cli.py survey
$ env -u WE2002_LOOKS_IMAGE python tools/kits/selftest.py --quiet | grep rules
rules: 0 failure(s)
```

## Root cause

As entradas do survey nunca foram para o `core/api.py`, e a varredura do §3.1 no selftest não confere o que o `cli.py` importa.

## Fix

Expor as funções do survey pelo `tools/kits/core/api.py` e tirar o import de `core.survey` do `tools/kits/cli.py`. Acrescentar ao `_rule_checks` de `tools/kits/selftest.py` uma conferência de que o `cli.py` (e depois o `ui/`) importa só `core.api` e stdlib, mais um controle em `controls.py` que plante `from core import survey` e espere essa linha FAIL. Coordenar com a KITS-TASK-09, que é dona do `cli.py`.

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/core/api.py`
- `tools/kits/selftest.py`
- `tools/kits/controls.py`

## Verificação

```text
$ grep -n "^from core import" tools/kits/cli.py | grep -v "import api"
```

Hoje imprime a linha 28; depois, nada. `python tools/kits/controls.py` tem de mostrar o controle novo vermelho.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `201c7915`)

```text
$ grep -n "^from core" tools/kits/cli.py
27:from core import api  # noqa: E402
28:from core import survey as survey_mod  # noqa: E402
$ env -u WE2002_LOOKS_IMAGE python tools/kits/selftest.py --quiet | grep rules
rules self-check
rules: 0 failure(s)
```

REPRODUCED (o `git log -L` da Evidência falhou só porque o `--scratch` rodou fora do repositório).

### O que foi feito

- `tools/kits/core/api.py`: `api.measure` é o módulo de medição da fase 0 (`survey`, `rects`, `prims`, `uv` e os controles deles), alcançado pela fachada e dito assim no comentário — dar contrato próprio às sondas não é o que elas são.
- `tools/kits/cli.py`: sem `from core import survey`; `survey_mod = api.measure`, e o resto do arquivo não mudou.
- `tools/kits/selftest.py`: `facade_breaks()` lê os imports do `cli.py` por `ast` (lista `FACADE_CLIENTS`, onde o `ui/` entra quando existir) e aceita só `core.api`, a biblioteca padrão e `__future__`; regra nova no `rules`.
- `tools/kits/controls.py`: controle `cli-imports-survey`, que planta `from core import survey` no `cli.py`.

### Verificação

```text
$ grep -n "^from core import" tools/kits/cli.py | grep -v "import api"
(sem saída, exit 1)
$ env -u WE2002_LOOKS_IMAGE python tools/kits/selftest.py --no-plant | grep "cli.py imports"
  ok    cli.py imports only core.api and the standard library (section 3.1)
```

A regra contra o `cli.py` da HEAD de antes (`git show HEAD:tools/kits/cli.py` posto no lugar e devolvido):

```text
HEAD cli.py: [('cli.py', 28, 'core.survey')]
now: []
```

```text
$ python tools/kits/controls.py | tail -2
  RED    cli-imports-survey           kits/cli.py :: the imports
controls: 11 of 11 red
```

Saídas do CLI iguais: `survey | md5sum` → `c2ec025a808afd4ffbe4c39fca0d991a`; `uv` → `2360a921…48fb84`; `prims --negative` 14 de 14, `rects --negative` 1 de 1, `survey --negative` 4 de 4, `uv --negative` 11 de 11.
- **Closed** — commit `8217b130` (2026-10-01): fix(kits): keep cli.py behind the facade and gate the rule
  - Files (`git show --name-status 8217b130`):
    - `M docs/tasks/kits/CORR-KITS-018.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/selftest.py`
