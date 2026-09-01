# Progresso de Correções — <título do projeto>

Correções abertas pelo `/revisar` ([`../prompts/02-revisar.md`](/docs/prompts/02-revisar.md))
e fechadas pelo `/corrigir`. O andamento das **tarefas** fica em
[`progresso.md`](/docs/tasks/progresso.md); este arquivo só rastreia correção.

**"Concluída em" nasce `—`** e é preenchida por quem executa a correção, com a
data do commit — o `/revisar` abre a correção, não a fecha.

<!-- Notas de exceção da numeração e do vocabulário. Escreva só as que
     existirem; cada uma evita que uma lacuna seja lida como arquivo sumido.

**Números não usados:** o **CORR-<PREFIXO>-NNN** foi pulado na numeração —
<qual revisão abriu quais IDs, e por que este não chegou a ser escrito>. Não há
correção perdida; o número simplesmente não existe.

**Correção envelhecida:** a **CORR-<PREFIXO>-NNN** aparece `[x] envelhecida`.
Não houve conserto de código — o sintoma deixou de existir entre a abertura e a
execução, e o Log dela traz as medidas que mostram isso. `[x]` ali quer dizer
"fechada e fora do backlog", não "corrigida".
-->

## Resumo executivo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
|---|---|---|---|---|---|
| [CORR-<PREFIXO>-001](/docs/tasks/CORR-<PREFIXO>-001.md) | [<PREFIXO>-TASK-01](/docs/tasks/01-<nome-do-arquivo>.md) | <o problema em uma frase, não o fix> | Alta | [ ] pendente | — |
| [CORR-<PREFIXO>-002](/docs/tasks/CORR-<PREFIXO>-002.md) | [<PREFIXO>-TASK-01](/docs/tasks/01-<nome-do-arquivo>.md) | <o problema em uma frase, não o fix> | Baixa | [ ] pendente | — |

<!-- Criticidade: Alta · Média · Baixa.
     Status: `[ ] pendente` · `[x] concluída` · `[x] envelhecida`.
     A coluna de origem aceita uma task **ou outra CORR**, quando a correção
     nasceu de uma correção. -->

## Checklist

- [ ] CORR-<PREFIXO>-001 — <o gesto do conserto, no imperativo: o que fazer, onde>
- [ ] CORR-<PREFIXO>-002 — <o gesto do conserto, no imperativo: o que fazer, onde>

## Detalhes por correção

### CORR-<PREFIXO>-001

- **Arquivo com problema:** `<caminho>` (linha N) e/ou `<caminho do gerador, se
  o arquivo for gerado — o conserto vai no gerador, nunca na saída>`
- **Sintoma:** <o que se observa, com o número medido dos dois lados>
- **Como foi detectado:** <a régua que acusou, e em que corrida>
- **Fix:** <o gesto, e o que fazer se a medição apontar para outra causa>

### CORR-<PREFIXO>-002

- **Arquivo com problema:** `<caminho>`
- **Sintoma:** <o que se observa, com o número medido dos dois lados>
- **Como foi detectado:** <a régua que acusou, e em que corrida>
- **Fix:** <o gesto, e o que fazer se a medição apontar para outra causa>
