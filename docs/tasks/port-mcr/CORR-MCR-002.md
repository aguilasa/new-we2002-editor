---
id: CORR-MCR-002
title: "Correção: a verificação de Fase 0 do perfil pede um `grep` que não tem como sair vazio"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-MCR-002: o perfil ficou com o escopo velho do `grep`

## Problema identificado

O `docs/prompts/perfil-mcr.md`, na seção `## Verificações específicas por
fase`, manda o revisor conferir, para toda task de Fase 0:

```markdown
- **Fase 0** — `grep -rn 'port-mcr' docs/prompts .claude` vazio; …
```

Esse comando **não tem como sair vazio**, e não deve: a MCR-TASK-01 mediu
exatamente isso e concluiu que o critério precisava de escopo — as duas regras
de `.claude/rules/` **citam** `port-mcr` de propósito, como já citam `PES2` e
`WTE`, e o próprio `perfil-mcr.md` mora em `docs/prompts/`.

A task corrigiu o critério **no arquivo dela** (`grep -rn 'port-mcr'
docs/prompts/0*.md docs/prompts/geral.md .claude/commands`) e deixou o perfil
com a forma antiga. Como é o perfil que o `/revisar` lê para saber o que
perguntar de uma fase, a próxima revisão de Fase 0 sai vermelha sobre uma
decisão já tomada e medida.

## Evidência

O escopo da task — o que o rito de fato exige:

```
$ grep -rn 'port-mcr' docs/prompts/0*.md docs/prompts/geral.md .claude/commands
(vazio)
```

O escopo que o perfil pede — 11 acertos, 7 deles dentro do próprio perfil,
incluindo a linha da verificação:

```
$ grep -rn 'port-mcr' docs/prompts .claude | wc -l
11
$ grep -rn 'port-mcr' docs/prompts .claude
docs/prompts/perfil-mcr.md:3:   **Este arquivo é o perfil do ciclo `port-mcr`**…
docs/prompts/perfil-mcr.md:13:  recebem por argumento: `/executar port-mcr`…
docs/prompts/perfil-mcr.md:89:  docs/tasks/port-mcr/  este ciclo
docs/prompts/perfil-mcr.md:110: - `docs/tasks/port-mcr/progresso.md` — toda task escreve nele…
docs/prompts/perfil-mcr.md:130: - **Fase 0** — `grep -rn 'port-mcr' docs/prompts .claude` vazio…
.claude/rules/links.md:103:    — `docs/tasks/port-mcr/`, desde…
.claude/rules/tasks.md:140,141,156
```

E o critério de conclusão da MCR-TASK-01, que é a fonte de verdade dela:

> `grep -rn 'port-mcr' docs/prompts/0*.md docs/prompts/geral.md .claude/commands`
> sai **vazio** — o rito não conhece ciclo pelo nome. As duas regras de
> `.claude/rules/` **podem** citá-lo como exemplo, e citam.

## Causa raiz

O perfil foi escrito antes da execução da MCR-TASK-01, com o escopo que a
execução mediu e descartou; a task não reconciliou o perfil ao mudar o
critério.

## Correção

### Arquivo: `docs/prompts/perfil-mcr.md`

Na seção `## Verificações específicas por fase`, trocar a linha da Fase 0 pelo
escopo medido, dizendo por que ele é esse:

```markdown
- **Fase 0** — `grep -rn 'port-mcr' docs/prompts/0*.md docs/prompts/geral.md
  .claude/commands` vazio: o **rito** não conhece ciclo pelo nome. As duas
  regras de `.claude/rules/` e este perfil **citam** `port-mcr`, e devem —
  convenção sem caso concreto vira prosa, e elas já nomeiam `PES2` e `WTE` do
  mesmo jeito. `/executar` sem argumento escolhe a mesma task de antes;
  `pip freeze` do venv no Log.
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/prompts/perfil-mcr.md` | modificar |

## Verificação

- [ ] o comando escrito na linha da Fase 0 do perfil sai **vazio** quando
      rodado como está escrito
- [ ] o perfil diz explicitamente que `.claude/rules/` e ele mesmo podem citar
      o ciclo
- [ ] `python3 tools/check_tasks.py` verde e `ctest -R tasks` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
