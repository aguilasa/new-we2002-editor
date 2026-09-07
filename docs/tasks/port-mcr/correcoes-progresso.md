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
| [CORR-MCR-001](/docs/tasks/port-mcr/CORR-MCR-001.md) | [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | `.claude/rules/tasks.md` afirma que os prompts apontam para `docs/tasks/progresso.md`, o que deixou de ser verdade em 2026-09-07 | Alta | [x] concluída | 2026-09-07 |
| [CORR-MCR-002](/docs/tasks/port-mcr/CORR-MCR-002.md) | [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | a verificação de Fase 0 do `perfil-mcr.md` pede um `grep` de escopo que não tem como sair vazio | Alta | [x] concluída | 2026-09-07 |
| [CORR-MCR-003](/docs/tasks/port-mcr/CORR-MCR-003.md) | [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | o link do `progresso.md` no `correcoes-progresso.template.md` aponta para o ciclo raso, contra a própria frase ao lado | Baixa | [x] concluída | 2026-09-07 |
| [CORR-MCR-004](/docs/tasks/port-mcr/CORR-MCR-004.md) | [MCR-TASK-02](/docs/tasks/port-mcr/02-base-legal-e-linhagem.md) | o inventário atribui todo o cache do WebView2 a `bin/`/`obj/`, e 164 arquivos dele são a linha `packages/` | Alta | [ ] pendente | — |
| [CORR-MCR-005](/docs/tasks/port-mcr/CORR-MCR-005.md) | [MCR-TASK-02](/docs/tasks/port-mcr/02-base-legal-e-linhagem.md) | os três `PlayerStatsSkills.dll` são declarados fora da conta e estão dentro da linha "o fonte que importa" | Baixa | [ ] pendente | — |

**Criticidade:** 🔴 Alta · 🟡 Média · 🟢 Baixa
**Status:** `[ ]` pendente · `[x]` concluída · `[x]` envelhecida

---

## Checklist

- [x] CORR-MCR-001 — reconciliar as duas afirmações de `.claude/rules/tasks.md` sobre para onde os prompts apontam
- [x] CORR-MCR-002 — pôr o escopo medido no `grep` de Fase 0 do `perfil-mcr.md`
- [x] CORR-MCR-003 — levar o link do cabeçalho do `correcoes-progresso.template.md` para `<CICLO>/`
- [ ] CORR-MCR-004 — corrigir a atribuição do WebView2 e declarar a profundidade do prefixo na tabela do inventário
- [ ] CORR-MCR-005 — separar o que está fora da conta do que está dentro dela e não é fonte

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

### CORR-MCR-004

- **Arquivo com problema:** `docs/tasks/port-mcr/02-base-legal-e-linhagem.md`
  (tabela "O que não entra, e por quê", célula de razão de `bin/` e `obj/`)
- **Sintoma:** a célula diz que ali mora **todo** o cache do WebView2, "1820
  arquivos e 319.637.837 B". Medido: só **1.656 / 218.698.891** estão sob
  `bin/`+`obj/`; os outros **164 / 100.938.946** são, byte a byte, a linha
  `packages/` da mesma tabela — as categorias são disjuntas, então a
  atribuição contradiz a tabela que ela anota. Junto: a legenda não diz que o
  prefixo casa em qualquer profundidade, e sem isso `.vs/` (20 contra 13 no
  topo) e `packages/` (164 contra 82) não reproduzem.
- **Como foi detectado:** dois `awk` sobre `git ls-tree -r -l HEAD` contra o
  SHA fixado, na revisão da MCR-TASK-02. Todo o resto do inventário remediu
  exato.
- **Fix:** pôr na célula os números medidos de `bin/`+`obj/`, e dizer na
  legenda que o WebView2 **atravessa** duas linhas e que o prefixo casa em
  qualquer profundidade. `NOTICE.md` não precisa de conserto — lá o WebView2
  aparece numa lista de naturezas, sem atribuição a diretório.

### CORR-MCR-005

- **Arquivo com problema:** `docs/tasks/port-mcr/02-base-legal-e-linhagem.md`
  (linha `resto (o fonte que importa)` e a nota logo abaixo dela)
- **Sintoma:** a nota diz que as três cópias de `PlayerStatsSkills.dll` estão
  "fora da conta por não ser arquivo". São arquivo, e estão dentro: 3 dos 72,
  35.328 dos 4.751.336 B. A mesma linha ainda carrega 6 `.jpg` e 2 `.ico`
  (195.476 B) sob a etiqueta "o fonte que importa".
- **Como foi detectado:** decomposição do resto por extensão, com a mesma
  classificação disjunta da tabela; ela fecha em 72 / 4.751.336.
- **Fix:** separar as duas naturezas — o raspador de fato não é arquivo; os
  `.dll` e a arte estão contados e não são fonte — e publicar a decomposição
  por extensão, que é o que torna a linha auditável.
