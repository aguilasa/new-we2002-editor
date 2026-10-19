---
id: CORR-KRP-026
---

# CORR-KRP-026 — Logs de fechamento trazem $ sh rite check, que não roda; a forma é sh "$RITE_HOME/bin/rite"

Origin: [KRP-TASK-23](/docs/tasks/concluidos/kits-replay/23-fechamento-da-fase-3a.md)

## Problem

A linha de evidência `$ sh rite check --cycle kits-replay` do Log não roda como está escrita: não há
arquivo `rite` na raiz do repositório, então `sh rite` falha. A forma exigida é
`sh "$RITE_HOME/bin/rite"`. A mesma linha está copiada nas tasks de fechamento das fases 2 e 3.

A saída colada está certa; só o texto do comando está errado.

## Evidência

```text
$ ls rite
ls: cannot access 'rite': No such file or directory
$ git grep -n '\$ sh rite\b' -- docs/tasks/kits-replay
docs/tasks/kits-replay/08-fechamento-da-fase-2.md:48:$ sh rite check --cycle kits-replay
docs/tasks/kits-replay/11-fechamento-da-fase-3.md:43:$ sh rite check --cycle kits-replay
docs/tasks/kits-replay/23-fechamento-da-fase-3a.md:43:$ sh rite check --cycle kits-replay
$ sh "$RITE_HOME/bin/rite" check --cycle kits-replay
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

## Root cause

(Hipótese.) O comando foi abreviado à mão ao ser colado no Log.

## Fix

No bloco de Log das tasks 08, 11 e 23, trocar `$ sh rite check` por `$ sh "$RITE_HOME/bin/rite" check`.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/08-fechamento-da-fase-2.md`
- `docs/tasks/kits-replay/11-fechamento-da-fase-3.md`
- `docs/tasks/kits-replay/23-fechamento-da-fase-3a.md`

## Verificação

```sh
git grep -n '\$ sh rite\b' -- docs/tasks/kits-replay
```

Hoje lista 3 linhas. Depois do conserto não pode listar nenhuma.

## Log de Execução

### 2026-10-16

Reprodução (`rite reproduce`, HEAD `22c48f71`): `ls rite` sai 2 (não há `rite` na raiz), e as
linhas 48 da task 08 e 43 das tasks 11 e 23 traziam `$ sh rite check --cycle kits-replay`.

Conserto: nas três, a linha virou `$ sh "$RITE_HOME/bin/rite" check --cycle kits-replay`. A saída
colada abaixo delas não muda.

O `git grep` da Verificação, sobre a pasta inteira, também acha esta correção e a tabela de correções,
que citam o texto velho de propósito; conferido nos três arquivos da task:

```text
$ git grep -n '\$ sh rite\b' -- docs/tasks/kits-replay/08-fechamento-da-fase-2.md docs/tasks/kits-replay/11-fechamento-da-fase-3.md docs/tasks/kits-replay/23-fechamento-da-fase-3a.md
$ git grep -n 'RITE_HOME/bin/rite" check --cycle' -- docs/tasks/kits-replay/08-fechamento-da-fase-2.md docs/tasks/kits-replay/11-fechamento-da-fase-3.md docs/tasks/kits-replay/23-fechamento-da-fase-3a.md
docs/tasks/kits-replay/08-fechamento-da-fase-2.md:48:$ sh "$RITE_HOME/bin/rite" check --cycle kits-replay
docs/tasks/kits-replay/11-fechamento-da-fase-3.md:43:$ sh "$RITE_HOME/bin/rite" check --cycle kits-replay
docs/tasks/kits-replay/23-fechamento-da-fase-3a.md:43:$ sh "$RITE_HOME/bin/rite" check --cycle kits-replay
```

O primeiro não imprime nada (sai 1).
- **Closed** — commit `e92e6353` (2026-10-16): docs(kits): closing Logs call rite check by its runnable path
  - Files (`git show --name-status e92e6353`):
    - `M docs/tasks/kits-replay/08-fechamento-da-fase-2.md`
    - `M docs/tasks/kits-replay/11-fechamento-da-fase-3.md`
    - `M docs/tasks/kits-replay/23-fechamento-da-fase-3a.md`
    - `M docs/tasks/kits-replay/CORR-KRP-026.md`
