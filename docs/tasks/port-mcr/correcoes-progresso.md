# Correções — port em Python do editor de `.mcr` do WE2002

Correções abertas pelo `/revisar` sobre as tasks deste ciclo. O andamento das
**tarefas** fica em [`progresso.md`](/docs/tasks/port-mcr/progresso.md).

**O prefixo deste pool é `CORR-MCR-`**, com numeração contínua a partir de
`001`. O pool é único dentro do ciclo, e não se cruza com o de nenhuma outra
pasta — o ciclo de PES2 tem o seu em
[`/docs/tasks/correcoes-progresso.md`](/docs/tasks/correcoes-progresso.md), e o
ciclo arquivado, o dele em
[`/docs/tasks/concluidos/correcoes-progresso.md`](/docs/tasks/concluidos/correcoes-progresso.md).

## Resumo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
| -- | -------------- | ------ | ----------- | ------ | ------------ |
| [CORR-MCR-001](/docs/tasks/port-mcr/CORR-MCR-001.md) | [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | `.claude/rules/tasks.md` afirma que os prompts apontam para `docs/tasks/progresso.md`, o que deixou de ser verdade em 2026-09-07 | Alta | [ ] pendente | — |
| [CORR-MCR-002](/docs/tasks/port-mcr/CORR-MCR-002.md) | [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | a verificação de Fase 0 do `perfil-mcr.md` pede um `grep` de escopo que não tem como sair vazio | Alta | [ ] pendente | — |
| [CORR-MCR-003](/docs/tasks/port-mcr/CORR-MCR-003.md) | [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | o link do `progresso.md` no `correcoes-progresso.template.md` aponta para o ciclo raso, contra a própria frase ao lado | Baixa | [ ] pendente | — |

**Criticidade:** 🔴 Alta · 🟡 Média · 🟢 Baixa
**Status:** `[ ]` pendente · `[x]` concluída · `[x]` envelhecida

---

## Checklist

- [ ] CORR-MCR-001 — reconciliar as duas afirmações de `.claude/rules/tasks.md` sobre para onde os prompts apontam
- [ ] CORR-MCR-002 — pôr o escopo medido no `grep` de Fase 0 do `perfil-mcr.md`
- [ ] CORR-MCR-003 — levar o link do cabeçalho do `correcoes-progresso.template.md` para `<CICLO>/`

---

## Detalhes por correção

### CORR-MCR-001

- **Arquivo com problema:** `.claude/rules/tasks.md` (linhas 29 e 176)
- **Sintoma:** a regra afirma, em tempo presente, que os prompts leem
  `docs/tasks/progresso.md`; desde a MCR-TASK-01 os cinco resolvem `<CICLO>` no
  Passo 0. O gêmeo dessa frase no `CLAUDE.md` foi atualizado no mesmo commit.
- **Como foi detectado:** `grep -n 'docs/tasks/progresso.md'
  .claude/rules/tasks.md`, contra o bloco `Passo 0` dos cinco prompts
  (md5 `aa2ef72d…`, idêntico nos cinco), na revisão da MCR-TASK-01.
- **Fix:** trocar o caminho cravado pela pasta resolvida na linha 29, e
  reescrever a linha 176 no espírito do `CLAUDE.md` — a intenção do parágrafo
  (`concluidos/` é história) continua valendo; só o caminho envelheceu.

### CORR-MCR-002

- **Arquivo com problema:** `docs/prompts/perfil-mcr.md` (linha 130)
- **Sintoma:** `grep -rn 'port-mcr' docs/prompts .claude` devolve **11**
  acertos, 7 deles dentro do próprio perfil — inclusive a linha que pede que
  ele saia vazio. O escopo medido pela MCR-TASK-01 devolve **0**.
- **Como foi detectado:** os dois `grep` rodados lado a lado na revisão da
  MCR-TASK-01, contra o critério de conclusão da própria task.
- **Fix:** escrever na linha da Fase 0 o escopo medido
  (`docs/prompts/0*.md docs/prompts/geral.md .claude/commands`) e dizer por que
  `.claude/rules/` e o perfil podem citar o ciclo.

### CORR-MCR-003

- **Arquivo com problema:** `docs/tasks/correcoes-progresso.template.md`
  (linha 3)
- **Sintoma:** o link diz `/docs/tasks/progresso.md` — o ciclo raso — enquanto
  a frase ao lado dele diz "o que mora **ao lado deste arquivo**". O
  instanciado deste ciclo escreve `/docs/tasks/port-mcr/progresso.md`; só o
  molde ficou para trás.
- **Como foi detectado:** leitura do template contra o item do critério da
  MCR-TASK-01; a conferência de existência de link não alcança
  `*.template.md`, e o destino existe de qualquer forma — só é o arquivo
  errado.
- **Fix:** apontar o link do cabeçalho para
  `/docs/tasks/<CICLO>/progresso.md`, como os demais links do mesmo arquivo.
