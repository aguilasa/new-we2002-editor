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
| [CORR-PES2-004](/docs/tasks/CORR-PES2-004.md) | [CORR-PES2-003](/docs/tasks/CORR-PES2-003.md) | Os prompts ficaram agnósticos de plano e de prefixo, e continuam com o corpo operacional inteiro do ciclo `wte/` | Média | [x] concluída | 2026-09-01 |
| [CORR-PES2-005](/docs/tasks/CORR-PES2-005.md) | [PES2-TASK-02](/docs/tasks/02-poke-por-conjunto-de-copias.md) | Duas das cinco recusas do `--self-check` do `poke.py` medem a mesma guarda; a regra de fim e o último registro nunca são exercitados | Alta | [x] concluída | 2026-09-01 |
| [CORR-PES2-006](/docs/tasks/CORR-PES2-006.md) | [PES2-TASK-02](/docs/tasks/02-poke-por-conjunto-de-copias.md) | O `poke.py` trabalha com oito listas e continua dizendo cinco em nove lugares, dois deles impressos na tela | Alta | [x] concluída | 2026-09-01 |
| [CORR-PES2-007](/docs/tasks/CORR-PES2-007.md) | [PES2-TASK-02](/docs/tasks/02-poke-por-conjunto-de-copias.md) | A tabela de testes do plano, o estado da Fase 2 e a verificação de Fase 2 do perfil ainda dizem cinco listas | Média | [x] concluída | 2026-09-01 |
| [CORR-PES2-008](/docs/tasks/CORR-PES2-008.md) | [PES2-TASK-02](/docs/tasks/02-poke-por-conjunto-de-copias.md) | A varredura do `poke.py` só reconhece registro delimitado por NUL, e o disco tem três tabelas de largura fixa | Baixa | [x] concluída | 2026-09-01 |

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
- [x] CORR-PES2-004 — corpo WTE-específico nos prompts que se dizem agnósticos
- [x] CORR-PES2-005 — o `--self-check` do `poke.py` não exercita duas guardas
- [x] CORR-PES2-006 — `poke.py` diz cinco listas e trabalha com oito
- [x] CORR-PES2-007 — três textos vivos ainda dizem cinco listas
- [x] CORR-PES2-008 — a varredura do `poke.py` assume um esquema de registro

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

### CORR-PES2-004

- **Arquivo com problema:** os cinco prompts de `docs/prompts/` — 64 caminhos
  `wte/` cravados, e as 73 linhas da Etapa 3 do `02-revisar.md` indexadas por
  faixa de task de um ciclo fechado
- **Sintoma:** três correções tiraram dos prompts o plano e os dois prefixos, e
  o corpo operacional do `wte/` ficou: checklist de `.dfm`/`.lfm`/stubs, gates
  datados por task que não existe no ciclo vivo, tabela de geradores de
  `wte/tools/`, e o `04-corrigir-tudo.md` abrindo com "Você vai trabalhar no
  projeto WE2002 Team Editor → Lazarus" — o arquivo que executa as correções de
  PES2. As seis fases do `PLAN-PES2-PSX.md` não têm entrada nenhuma
- **Como foi detectado:** varredura da CORR-PES2-003, ao decidir que os cinco
  cabeçalhos de fase **não** deviam virar `<PREFIXO>-TASK`: trocar afirmaria que
  um checklist de `.dfm` vale para PES2. O caso que separa "prefixo mal escrito"
  de "conteúdo do ciclo errado"
- **Fix:** separação, não substituição — o rito fica no prompt, o que é do ciclo
  sai para um perfil que o `progresso.md` nomeia. **A forma é decisão do
  usuário** e a CORR não a toma sozinha

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

### CORR-PES2-005

- **Arquivo com problema:** `tools/pes2/poke.py`, o `self_check()`; e o Log da
  `docs/tasks/02-poke-por-conjunto-de-copias.md`, que afirma cinco recusas
  exercitadas
- **Sintoma:** o caso da regra de fim (`team=96`, `IRELAND`) é interceptado
  pela guarda de time ausente, porque o 96 não está em `team-names-select2`.
  As duas linhas da saída medem a **mesma** guarda, e a de último registro da
  tabela não tem caso nenhum
- **Como foi detectado:** revisão da PES2-TASK-02 — `--self-check` nas duas
  releases, e `plan(..., allow_partial=True)` mostrando que as duas guardas
  funcionam quando alcançadas
- **Fix:** `_expect_refusal` passa a conferir o **texto** da recusa; o caso da
  regra de fim leva `allow_partial=True`; entra o caso do último registro

### CORR-PES2-006

- **Arquivo com problema:** `tools/pes2/poke.py`, nove ocorrências de "five"
- **Sintoma:** o `--self-check` imprime `in all five lists` e, três linhas
  adiante, `the tightest of the 8 slots` / `8 copy/copies`. O docstring do
  módulo repete a lista de cinco contagens que a §6.1 já corrigiu para oito
- **Como foi detectado:** revisão da PES2-TASK-02 — `grep -n five
  tools/pes2/poke.py` contra `team_map.py --check` e `check_image.py`
- **Fix:** as duas strings derivam de `len(KEYS)`; comentários e docstring
  passam a dizer oito, menos o de `leftovers`, que narra o achado

### CORR-PES2-007

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md` (§5.1 linha 1048 e o
  estado da Fase 2, linhas 1140-1141) e `docs/prompts/perfil-pes2.md`
  (linha 197)
- **Sintoma:** os três dizem "cinco listas/cópias"; a linha 1048 ainda
  descreve o `pes2_image` sem o `poke`, que a task acrescentou ao mesmo teste.
  O perfil se contradiz: a armadilha nº 2 dele já diz oito
- **Como foi detectado:** revisão da PES2-TASK-02 —
  `grep -rn "cinco listas\|cinco cópias" docs/ CLAUDE.md`
- **Fix:** trocar por oito nos três, e citar o `poke` na célula do
  `pes2_image`. `PES2-AJUSTES.md` e as frases datadas ficam como estão

### CORR-PES2-008

- **Arquivo com problema:** `tools/pes2/poke.py`, `leftovers()`
- **Sintoma:** a varredura conta um casamento como registro só com NUL antes e
  depois. `SELECT.BIN` @5320 e o executável guardam registros de 10 B **sem
  terminador quando o nome enche a largura** — nesse caso a varredura não vê a
  cópia e **cala**, e silêncio se lê como "não sobrou"
- **Como foi detectado:** revisão da PES2-TASK-02 — leitura do teste `whole`
  contra o docstring de `_read_fixed` em `tables.py`, que diz que
  "termina em NUL" não é o teste
- **Fix:** aceitar também a forma de largura fixa, usando as tabelas fixas que
  `T.TABLES` já descreve para o arquivo; ou, no mínimo, **recusar** em vez de
  calar quando o nome tem exatamente a largura de uma delas
