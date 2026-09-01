# Progresso de Correções — mapeamento do Pro Evolution Soccer 2 (PSX)

Correções abertas pelo `/revisar` ([`../prompts/02-revisar.md`](/docs/prompts/02-revisar.md))
e fechadas pelo `/corrigir`. O andamento das **tarefas** fica em
[`progresso.md`](/docs/tasks/progresso.md); este arquivo só rastreia correção.

**"Concluída em" nasce `—`** e é preenchida por quem executa a correção, com a
data do commit — o `/revisar` abre a correção, não a fecha.

**A numeração deste pool começa em `CORR-PES2-001`.** O pool anterior, com a
numeração `CORR-WTE-XXX` contínua de 001 a 143, desceu inteiro para
[`concluidos/`](/docs/tasks/concluidos/correcoes-progresso.md) em 2026-09-01,
junto com as tasks que o geraram — a pasta é um conjunto fechado, e o
`tools/check_tasks.py` confere cada task contra o progresso que mora ao lado
dela. O prefixo muda porque o projeto muda; a convenção de que **o pool é
único dentro do ciclo** continua valendo.

**As duas primeiras entradas vieram da revisão da PES2-TASK-01**, em
2026-09-01 — como devia: de uma medição, não de uma suposição.

## Resumo executivo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
|---|---|---|---|---|---|
| [CORR-PES2-001](/docs/tasks/CORR-PES2-001.md) | [PES2-TASK-01](/docs/tasks/01-ferramental-das-fases-3-e-4.md) | A §3.2 diz que sem `-EL` o `objdump` mente; medido, sem `-EL` a saída é idêntica — quem mente é o `-EB` | Alta | [x] concluída | 2026-09-01 |
| [CORR-PES2-002](/docs/tasks/CORR-PES2-002.md) | [PES2-TASK-01](/docs/tasks/01-ferramental-das-fases-3-e-4.md) | A regra e os cinco prompts mandam abrir `CORR-WTE-XXX`; o pool vivo é `CORR-PES2-XXX` | Média | [x] concluída | 2026-09-01 |
| [CORR-PES2-003](/docs/tasks/CORR-PES2-003.md) | [CORR-PES2-002](/docs/tasks/CORR-PES2-002.md) | Os prompts e os wrappers cravam `WTE-TASK-XX`; o ciclo vivo é `PES2-TASK-XX` | Média | [x] concluída | 2026-09-01 |

<!-- Criticidade: Alta · Média · Baixa.
     Status: `[ ] pendente` · `[x] concluída` · `[x] envelhecida`.
     A coluna de origem aceita uma task **ou outra CORR**, quando a correção
     nasceu de uma correção.

     Modelo de linha, para quando a primeira for aberta -- as duas primeiras
     celulas sao link em `/docs/`, como manda a .claude/rules/links.md; aqui
     estao sem colchete para nao virar link quebrado na conferencia:

| CORR-PES2-001 -> /docs/tasks/CORR-PES2-001.md | PES2-TASK-04 -> a task de origem | <o problema em uma frase, nao o fix> | Alta | [ ] pendente | — |
-->

## Checklist

- [x] CORR-PES2-001 — o `-EL` do `objdump` na §3.2 está anotado no flag errado
- [x] CORR-PES2-002 — prefixo do pool contradito pela regra e pelos prompts
- [x] CORR-PES2-003 — o prefixo de *task* continua cravado nos prompts e nos wrappers

## Detalhes por correção

### CORR-PES2-001

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md` (§3.2) e o Log da
  `docs/tasks/01-ferramental-das-fases-3-e-4.md`, de onde a frase saiu
- **Sintoma:** o plano afirma, como medido, que sem `-EL` o `objdump` decodifica
  big-endian sobre bytes little-endian e "não falha, só mente". Remedido: 1.017
  linhas com e sem `-EL`, **mnemônicos idênticos** — o alvo default do
  `mipsel-linux-gnu-objdump` 2.42 já é `elf32-tradlittlemips`. Quem mente é o
  `-EB`, que o plano não menciona
- **Como foi detectado:** revisão da PES2-TASK-01 — os dois comandos da §3.2
  rodados verbatim sobre `/SLES_039.57` extraído para o scratchpad, mais as
  variantes sem `-EL` e com `-EB`, comparadas por `diff` na coluna de mnemônico
- **Fix:** trocar a frase pela medida, mantendo o `-EL` explícito no comando e
  movendo a lição "não falha, só mente" para o `-EB`

### CORR-PES2-002

- **Arquivo com problema:** `.claude/rules/tasks.md` (linha 68) e os cinco
  prompts de `docs/prompts/` — 43 ocorrências de `CORR-WTE` ao todo
- **Sintoma:** a regra afirma que a numeração é `CORR-WTE-XXX` "qualquer que
  seja o projeto", enquanto o `correcoes-progresso.md` vivo declara
  `CORR-PES2-001`. A mesma regra proíbe cravar prefixo de ID em prompt, e os
  cinco prompts cravam
- **Como foi detectado:** revisão da PES2-TASK-01, ao ter de escolher o nome do
  primeiro arquivo de correção do ciclo. Resolvida a favor do pool, que é o
  texto mais novo (`0bdf350` contra `602218d`)
- **Fix:** a regra passa a dizer que o prefixo é do ciclo e sai do
  `correcoes-progresso.md`; os prompts passam a `CORR-<PREFIXO>-XXX`, como os
  `*.template.md` já fazem. `docs/tasks/concluidos/` não se toca

### CORR-PES2-003

- **Arquivo com problema:** `.claude/rules/tasks.md`, os cinco prompts de
  `docs/prompts/` e os cinco wrappers de `.claude/commands/` — 39 + 11
  ocorrências de `WTE-TASK`
- **Sintoma:** a CORR-PES2-002 tirou dos prompts o prefixo de *correção* e
  deixou o de *task*: eles mandam executar `WTE-TASK-XX`, e o `progresso.md`
  vivo lista `PES2-TASK-01` a `-25`. As três exclusões "nunca execute
  `WTE-TASK-XX` por aqui" não nomeiam nenhuma task existente
- **Como foi detectado:** varredura de discrepância da CORR-PES2-002, ao
  conferir o que mais o mesmo parágrafo da regra proíbe. Dívida independente —
  nem criada nem revelada pelo conserto dela —, aberta em vez de redimensionar
  a correção no meio do lote
- **Fix:** `<PREFIXO>-TASK-XX`, com o prefixo saindo do `progresso.md`, e a
  mesma distinção da 002 entre placeholder prescritivo e citação de task real
  do ciclo fechado. Glob executável fica `docs/tasks/*-TASK-*.md`

<!-- Modelo de bloco, para quando a primeira for aberta:

### CORR-PES2-001

- **Arquivo com problema:** `<caminho>` (linha N) e/ou `<caminho do gerador, se
  o arquivo for gerado — o conserto vai no gerador, nunca na saída>`
- **Sintoma:** <o que se observa, com o número medido dos dois lados>
- **Como foi detectado:** <a régua que acusou, e em que corrida>
- **Fix:** <o gesto, e o que fazer se a medição apontar para outra causa>
-->

---

## O que este projeto tem de diferente, e que muda a forma da CORR

**Não há oráculo** (§4.1 do [plano](/docs/PLAN-PES2-PSX.md)). No `newWe2002` e
no `wte/` a evidência de uma correção era uma faixa de bytes contra um binário
que sabia a resposta; aqui o oráculo é **o jogo rodando**, e a evidência é uma
captura de tela mais o offset que a produziu.

Três consequências para a seção `## Evidência` de qualquer `CORR-PES2-*`:

- **O quadro não entra no git.** É jogo comercial, mesma regra de `roms/` e dos
  FAQs. O que entra é o comando que o produz e o número medido — como o
  `boot_check.sh` já faz com desvio-padrão e contagem de pixels.
- **Divergência fora do esperado vira CORR com a faixa e o marcador**, não com
  o offset absoluto: offset constante não sobrevive à troca de release (§6.6).
- **"Não reproduz" é resultado**, e fecha a correção como `[x] envelhecida`
  quando o sintoma deixou de existir entre a abertura e a execução. O Log dela
  traz as medidas que mostram isso.
