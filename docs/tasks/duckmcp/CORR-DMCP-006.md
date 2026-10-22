---
id: CORR-DMCP-006
---

# CORR-DMCP-006 — Restringir o grep 'Pro Evolution' da Fase 2 aos arquivos fora dos juízes

Origin: [DMCP-TASK-08](/docs/tasks/duckmcp/08-fork.md) — achado também nas revisões de
[DMCP-TASK-09](/docs/tasks/duckmcp/09-cli-fork-e-lancadores.md) e
[DMCP-TASK-10](/docs/tasks/duckmcp/10-duckmcp-live.md).

## Problem

A verificação da Fase 2 do perfil diz que `grep -rn 'Pro Evolution' tools/duckmcp` não acha nada. Na
HEAD ela acha duas linhas, e as duas são do próprio gate que impõe a agnosticidade: o `TITLE_RE` do
`selftest.py` e o controle `c-game-window-title` do `controls.py`, ambos entrados no `e9ac6f57`
(DMCP-TASK-08). Como está escrita, a verificação nunca passa; as tasks 09 e 10 da fase fecharam com ela
vermelha sem dizer.

## Evidência

```text
$ grep -rn 'Pro Evolution' tools/duckmcp
tools/duckmcp/controls.py:106:        "\nGAME_WINDOW = \"^Pro Evolution Soccer 2$\"\nDIALOGS = (",
tools/duckmcp/selftest.py:97:TITLE_RE = re.compile(r"Pro Evolution Soccer|Winning Eleven|World Soccer",
$ git log --oneline -S'Pro Evolution Soccer' -- tools/duckmcp/controls.py tools/duckmcp/selftest.py
e9ac6f57 feat(duckmcp): game-agnostic fork launcher, …
$ git show e9ac6f57 --stat -- docs/prompts/perfil-duckmcp.md
docs/prompts/perfil-duckmcp.md |  10 +-   (só o bloco da Fase 1 mudou)
```

## Root cause

Hipótese: os juízes isentos da regra (c) (`JUDGES = ("selftest.py", "controls.py")`) não foram levados
para o grep literal da fase quando entraram. Faltou varrer quem repetia o veredito anterior.

## Fix

Em `docs/prompts/perfil-duckmcp.md`, Fase 2, trocar por
`grep -rn 'Pro Evolution' tools/duckmcp --exclude=selftest.py --exclude=controls.py`, ou remeter à
checagem `rule (c)` do selftest que já impõe isso. Alternativa: montar a string nos juízes de modo que
o grep literal não a ache.

## Arquivos a criar ou modificar

- `docs/prompts/perfil-duckmcp.md`

## Verificação

`grep -rn 'Pro Evolution' tools/duckmcp --exclude=selftest.py --exclude=controls.py; echo $?` imprime 1,
e esse (ou o equivalente) é o comando que o perfil cita na Fase 2. O grep literal de hoje sai 0 com 2
linhas.

## Log de Execução
