---
id: CORR-MCR-016
title: "Correção: \"os três últimos nasceram na MCR-TASK-10\" não são os três últimos da lista"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-MCR-016: o ponteiro por posição na §3.2 do plano não casa com os três que a prosa explica

## Problema identificado

A §3.2 do plano ganhou os seis módulos novos e, logo abaixo do bloco, a frase:

> **Os três últimos nasceram na MCR-TASK-10** e não estavam neste esboço.

Os três últimos da lista (fora a pasta `ui/`) são `cli.py`, `selftest.py` e
`ui_check.py`. Os três que a frase então explica são `harness.py`,
`controls.py` e `ui_check.py` — e são estes os que a task criou de fato: o
esboço anterior já trazia `glossary.py`, `cli.py` e `selftest.py`.

A prosa está certa sobre **quais**; o ponteiro por posição está errado, e é ele
que o leitor usa primeiro.

## Evidência

O bloco antes da task (`git show 68e55a2^:docs/PLAN-MCR-PY.md`) termina assim:

```
  mcrio.py        ler, gravar, validar, recusar
  glossary.py     es -> en, e a recusa de espanhol remanescente
  cli.py          argparse: info dump get set roundtrip negative check
  selftest.py     o agregador, com o controle negativo
  ui/             app.py, main_window.py, ...
```

E depois:

```
  mcrio.py        ler, gravar, validar, recusar
  glossary.py     es -> en, e a recusa de espanhol remanescente
  harness.py      ok/attempt/refuses -- e o guard externo do self-check
  controls.py     os controles negativos, como substituicao literal
  cli.py          argparse: info dump get set roundtrip negative check
  selftest.py     o agregador, com o controle negativo
  ui_check.py     o gate mcr_ui: a janela sobe no :98, ou pula com 77
  ui/             app.py, main_window.py, ...
```

Diferença: `harness.py`, `controls.py`, `ui_check.py`. Posições 12, 13 e 16 de
16 — não as três últimas.

```
$ grep -n "três últimos" docs/PLAN-MCR-PY.md
309:**Os três últimos nasceram na MCR-TASK-10** e não estavam neste esboço. O
```

## Causa raiz

Os dois módulos novos foram inseridos no meio da lista para ficar perto do que
se parecem, e a frase que os anuncia continuou apontando por posição.

## Correção

### Arquivo: `docs/PLAN-MCR-PY.md`

Nomear os três em vez de apontá-los por posição — o resto do parágrafo já os
nomeia um a um, então basta a abertura:

```markdown
**O `harness.py`, o `controls.py` e o `ui_check.py` nasceram na MCR-TASK-10** e
não estavam neste esboço.
```

Nome resiste a reordenação da lista; posição não. É a mesma razão pela qual as
tabelas deste ciclo linkam o arquivo em vez de dizer "a linha de cima".

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-MCR-PY.md` | modificar |

## Verificação

- [ ] `grep -n "três últimos" docs/PLAN-MCR-PY.md` sai vazio
- [ ] os três nomes da abertura são os mesmos que o parágrafo explica
- [ ] conferência de forma e de existência de link de `.claude/rules/links.md`
      vazias
- [ ] `python3 tools/check_tasks.py` e `ctest -R tasks` verdes

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
