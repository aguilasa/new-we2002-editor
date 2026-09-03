---
id: CORR-PES2-022
title: "Correção: a coluna \"Revisado em\" das PES2-TASK-32 e 33 diz `✅ Concluído`, e nenhuma das duas foi revisada"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-PES2-022: duas tasks saíram da fila de revisão sem terem sido revisadas

## Problema identificado

A tabela de resumo do [`progresso.md`](/docs/tasks/progresso.md) tem a coluna
**"Revisado em"**, e o próprio arquivo declara o que ela aceita:

> - **"Revisado em"** — o commit da revisão. Tarefa concluída e ainda não
>   revisada leva `⬜ pendente`; tarefa que nem começou leva `—`, porque não
>   há o que revisar.

Nas linhas da `PES2-TASK-32` e da `PES2-TASK-33` a célula tem
**`✅ Concluído`** — que não é data, não é `⬜ pendente` e não é `—`. É o
símbolo da coluna **"Status"**, escrito uma coluna adiante.

O efeito não é cosmético. O `/revisar` escolhe *"a `✅ Concluído` de menor ID
com a coluna Revisado em ainda em `⬜ pendente`"*. Com `✅ Concluído` na
célula, as duas tasks **deixaram de estar na fila** — e nenhuma das duas foi
revisada: não existe commit de revisão delas, e nenhuma `CORR-PES2-*` as tem
como origem. A coluna existe exatamente para impedir isso, e aqui ela afirmou
o contrário do que aconteceu.

## Evidência

O estado atual:

```
$ grep -n "PES2-TASK-3[234]\]" docs/tasks/progresso.md | cut -c1-200
77:| [PES2-TASK-32](...) | ... | 0 | — | ✅ Concluído | 2026-09-02 | ✅ Concluído |
78:| [PES2-TASK-33](...) | ... | 0 | 32 | ✅ Concluído | 2026-09-03 | ✅ Concluído |
79:| [PES2-TASK-34](...) | ... | 0 | 33 | ✅ Concluído | 2026-09-03 | ⬜ pendente |
```

Quando entrou — no `65e980a`, que é um commit de **task**, não de revisão:

```
$ git show 4d3a574:docs/tasks/progresso.md | grep "PES2-TASK-33\]" | tail -c 60
 | ✅ Concluído | 2026-09-03 | ⬜ pendente |

$ git show 65e980a:docs/tasks/progresso.md | grep "PES2-TASK-33\]" | tail -c 60
 | ✅ Concluído | 2026-09-03 | ✅ Concluído |
```

Que revisão nenhuma aconteceu:

```
$ git log --oneline --all | grep -i "review"
cce9b46 docs: open CORR-PES2-017..020 from the PES2-TASK-29 review
22c0637 docs: open CORR-PES2-013..016 from the PES2-TASK-27 review
dbbbf3e docs: open CORR-PES2-009..012 from the PES2-TASK-26 review
2852889 docs: open CORR-PES2-005..008 from the PES2-TASK-02 review
d9dfde9 docs: open CORR-PES2-001 and -002 from the PES2-TASK-01 review
(nada de 32 nem de 33)

$ grep -c "PES2-TASK-3" docs/tasks/correcoes-progresso.md
0
```

## Causa raiz

A célula foi preenchida por quem **executou** a task 33, copiando o símbolo
da coluna vizinha, em vez de deixá-la em `⬜ pendente` para o `/revisar`.

## Correção

### Arquivo: `docs/tasks/progresso.md`

Repor `⬜ pendente` nas duas células, devolvendo as duas tasks à fila:

```
| [PES2-TASK-32](/docs/tasks/32-poc-do-mcp-do-duckstation.md) | ... | ✅ Concluído | 2026-09-02 | ⬜ pendente |
| [PES2-TASK-33](/docs/tasks/33-compilar-e-validar-o-mcp.md)  | ... | ✅ Concluído | 2026-09-03 | ⬜ pendente |
```

**A ordem de revisão passa a ser 32, 33 e só então 34** — o `/revisar` toma a
de menor ID. A 34 já foi revisada (esta invocação), e a data dela fica onde
está: repor a fila das duas anteriores não desfaz a revisão que houve.

### Arquivo: `docs/prompts/01-executar.md` (ou onde o rito de fechar task mora)

Se o prompt de execução não disser que a célula **"Revisado em"** nasce
`⬜ pendente` e é escrita **só** pelo `/revisar`, dizer. É a mesma cerca que
o `02-revisar.md` já tem do outro lado ("a única célula do `progresso.md` que
este prompt escreve é a Revisado em").

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/progresso.md` | modificar |
| `docs/prompts/01-executar.md` | modificar |

## Verificação

- [ ] `grep -c '| ✅ Concluído |$' docs/tasks/progresso.md` devolve `0`
- [ ] `python3 tools/check_tasks.py` continua verde
- [ ] o `/revisar` sem argumento escolhe a `PES2-TASK-32`
- [ ] as duas revisões pendentes são feitas, uma invocação por vez

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
