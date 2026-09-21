# Progresso de Correções — mapeamento do Pro Evolution Soccer 2 (PSX)

Correções abertas pelo `/rite:review` (até a migração para o Rite, pelo `/revisar` — [prompt da época](https://github.com/aguilasa/new-we2002-editor/blob/bcb5aee473527ace5d5bc24ef29c9a36d26a2874/docs/prompts/02-revisar.md))
e fechadas pelo `/rite:fix`. O andamento das **tarefas** fica em
[`progresso.md`](/docs/tasks/progresso.md); este arquivo só rastreia correção.

**"Done on" nasce `—`** e é escrita pelo `rite close` com a data do commit que
corrigiu — a revisão abre a correção, não a fecha.

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

<!-- rite:begin fixes -->
| ID | Title | Origin | Severity | Status | Done on |
| --- | --- | --- | --- | --- | --- |
| [CORR-PES2-001](/docs/tasks/CORR-PES2-001.md) | Correção: o -EL do objdump não é o que a §3.2 diz que é — quem mente é o -EB | PES2-TASK-01 | high | done | 2026-09-01 |
| [CORR-PES2-002](/docs/tasks/CORR-PES2-002.md) | Correção: as regras e os prompts dizem CORR-WTE, o pool vivo é CORR-PES2 | PES2-TASK-01 | medium | done | 2026-09-01 |
| [CORR-PES2-003](/docs/tasks/CORR-PES2-003.md) | Correção: os prompts e os wrappers cravam WTE-TASK-XX; o ciclo vivo é PES2-TASK-XX | CORR-PES2-002 | medium | done | 2026-09-01 |
| [CORR-PES2-004](/docs/tasks/CORR-PES2-004.md) | Correção: os prompts ficaram agnósticos de plano e de prefixo, e continuam cheios de corpo WTE-específico | CORR-PES2-003 | medium | done | 2026-09-01 |
| [CORR-PES2-005](/docs/tasks/CORR-PES2-005.md) | Correção: duas das cinco recusas do `--self-check` do `poke.py` medem a mesma coisa; a regra de fim e o último registro nunca são exercitados | PES2-TASK-02 | high | done | 2026-09-01 |
| [CORR-PES2-006](/docs/tasks/CORR-PES2-006.md) | Correção: o `poke.py` mede oito listas e continua dizendo cinco — inclusive no que imprime | PES2-TASK-02 | high | done | 2026-09-01 |
| [CORR-PES2-007](/docs/tasks/CORR-PES2-007.md) | Correção: três textos vivos ainda dizem cinco listas, e a tabela de testes do plano não conhece o `poke` | PES2-TASK-02 | medium | done | 2026-09-01 |
| [CORR-PES2-008](/docs/tasks/CORR-PES2-008.md) | Correção: a varredura do `poke.py` só enxerga registro delimitado por NUL, e o disco tem tabela de largura fixa | PES2-TASK-02 | low | done | 2026-09-01 |
| [CORR-PES2-009](/docs/tasks/CORR-PES2-009.md) | Correção: o `--check` do `lzss.py` não sabe ficar vermelho — o bug de porte que a própria task nomeia passa verde | PES2-TASK-26 | high | done | 2026-09-01 |
| [CORR-PES2-010](/docs/tasks/CORR-PES2-010.md) | Correção: as duas constantes do `scan` do `lzss.py` — uma decide todo verdicto com 128 B de margem, a outra é justificada por um número errado | PES2-TASK-26 | medium | done | 2026-09-01 |
| [CORR-PES2-011](/docs/tasks/CORR-PES2-011.md) | Correção: o prefixo de registro citado na §1.14(e) é o do quarto registro, não a forma deles | PES2-TASK-26 | low | done | 2026-09-01 |
| [CORR-PES2-012](/docs/tasks/CORR-PES2-012.md) | Correção: o estado medido diz 208 contêineres no PES2 e 195 no WE2002; os quatro discos medem 208, 210, 177 e 195 | PES2-TASK-26 | low | done | 2026-09-01 |
| [CORR-PES2-013](/docs/tasks/CORR-PES2-013.md) | Correção: o `check` do `bin_archive.py` sai vermelho na imagem golden, e nenhum documento diz isso | PES2-TASK-27 | high | done | 2026-09-01 |
| [CORR-PES2-014](/docs/tasks/CORR-PES2-014.md) | Correção: não são os 105 `TEX_*.BIN` da European Deluxe que são Form 2 — são 18 | PES2-TASK-27 | high | done | 2026-09-01 |
| [CORR-PES2-015](/docs/tasks/CORR-PES2-015.md) | Correção: um dos quatro offsets de bandeira citados é de forma, e mora noutro arquivo; o quarto de cor é 75776 | PES2-TASK-27 | high | done | 2026-09-01 |
| [CORR-PES2-016](/docs/tasks/CORR-PES2-016.md) | Correção: a profundidade é decidida por contêiner, e o `DAT2D.BIN` do PES2 tem 261 paletas de 16 contra 5 de 256 | PES2-TASK-27 | high | done | 2026-09-01 |
| [CORR-PES2-017](/docs/tasks/CORR-PES2-017.md) | Correção: o perfil do ciclo não tem seção de Fase 7, e a Fase 7 já teve quatro tasks executadas | PES2-TASK-29 | medium | done | 2026-09-01 |
| [CORR-PES2-018](/docs/tasks/CORR-PES2-018.md) | Correção: são 9 de 13 entradas que recomprimem no orçamento, não 10 de 3, e a folga vai a 3 bytes, não 4 | PES2-TASK-29 | high | done | 2026-09-01 |
| [CORR-PES2-019](/docs/tasks/CORR-PES2-019.md) | Correção: o import não valida profundidade nem paleta, e grava um PNG de 4 bpp num slot de 8 bpp em silêncio | PES2-TASK-29 | high | done | 2026-09-01 |
| [CORR-PES2-020](/docs/tasks/CORR-PES2-020.md) | Correção: a conferência antes da gravação nunca foi vista ficando vermelha | PES2-TASK-29 | low | done | 2026-09-01 |
| [CORR-PES2-021](/docs/tasks/CORR-PES2-021.md) | Correção: o `boot_check.sh` justifica nomear o binário com um 0,019 que a própria task mediu e desmentiu | PES2-TASK-34 | high | done | 2026-09-03 |
| [CORR-PES2-022](/docs/tasks/CORR-PES2-022.md) | Correção: a coluna "Revisado em" das PES2-TASK-32 e 33 diz `✅ Concluído`, e nenhuma das duas foi revisada | PES2-TASK-34 | high | done | 2026-09-03 |
| [CORR-PES2-023](/docs/tasks/CORR-PES2-023.md) | Correção: o perfil não tem verificações de Fase 0, diz que ela não tem task de trabalho, e conta seis fases onde há oito | PES2-TASK-34 | medium | done | 2026-09-03 |
| [CORR-PES2-024](/docs/tasks/CORR-PES2-024.md) | Correção: o `--measure-menu` é gate, não confere se está no menu, e nenhum comando versionado o coloca lá | PES2-TASK-34 | medium | done | 2026-09-03 |
| [CORR-PES2-025](/docs/tasks/CORR-PES2-025.md) | Correção: a §3.2 do plano ainda chama a morada do fork de "item aberto da PES2-TASK-34" | PES2-TASK-34 | low | done | 2026-09-03 |
| [CORR-PES2-026](/docs/tasks/CORR-PES2-026.md) | Correção: o offset da RAM no fluxo inflado ficou em 6799; o leitor corrigido mede 6754 | PES2-TASK-32 | high | done | 2026-09-03 |
| [CORR-PES2-027](/docs/tasks/CORR-PES2-027.md) | Correção: o `pes2_boot` nunca roda pela receita documentada — ele quer `PES2_IMAGE`, e os docs só dão `WE2002_PES2_*` | PES2-TASK-32 | high | done | 2026-09-03 |
| [CORR-PES2-028](/docs/tasks/CORR-PES2-028.md) | Correção: o fork publica binário próprio, e o AppImage dele traz o servidor MCP | PES2-TASK-32 | high | done | 2026-09-03 |
| [CORR-PES2-029](/docs/tasks/CORR-PES2-029.md) | Correção: estado ausente despeja traceback no `savestate.py`, e o `except` do `selftest.py` vira NameError | PES2-TASK-32 | low | done | 2026-09-03 |
| [CORR-PES2-030](/docs/tasks/CORR-PES2-030.md) | Correção: o `pes2_boot` prova vida exigindo que dois quadros difiram, e falha na tela de intro que não anima | CORR-PES2-027 | high | done | 2026-09-03 |
| [CORR-PES2-031](/docs/tasks/CORR-PES2-031.md) | Correção: o fluxo A, que é a razão de o fork existir, não tem ferramenta versionada | PES2-TASK-33 | medium | done | 2026-09-04 |
| [CORR-PES2-032](/docs/tasks/CORR-PES2-032.md) | Correção: o fork morre calado durante execução livre, e toda ferramenta relata isso como "não está rodando" | PES2-TASK-33 | high | done | 2026-09-03 |
<!-- rite:end -->

**A tabela acima é gerada** pelo `rite.py sync` a partir do frontmatter de cada correção — não
edite dentro dela. **Status:** `pending` · `in-progress` · `done` · `stale`. **Severidade:**
`critical` · `high` · `medium` · `low`. A origem (`origin`) aceita uma task **ou outra CORR**, quando a correção nasceu
de uma correção. Correção nova sai do `rite new-fix`, que aloca o ID.

## Checklist

- [x] CORR-PES2-001 — o `-EL` do `objdump` na §3.2 está anotado no flag errado
- [x] CORR-PES2-002 — prefixo do pool contradito pela regra e pelos prompts
- [x] CORR-PES2-003 — o prefixo de *task* continua cravado nos prompts e nos wrappers
- [x] CORR-PES2-004 — corpo WTE-específico nos prompts que se dizem agnósticos
- [x] CORR-PES2-005 — o `--self-check` do `poke.py` não exercita duas guardas
- [x] CORR-PES2-006 — `poke.py` diz cinco listas e trabalha com oito
- [x] CORR-PES2-007 — três textos vivos ainda dizem cinco listas
- [x] CORR-PES2-008 — a varredura do `poke.py` assume um esquema de registro
- [x] CORR-PES2-009 — o `--check` do `lzss.py` não sabe ficar vermelho
- [x] CORR-PES2-010 — os dois limiares do `scan`, um deles com 128 B de margem
- [x] CORR-PES2-011 — prefixo de registro citado é uma instância, não a forma
- [x] CORR-PES2-012 — contagem de contêineres afirmada por jogo, medida por disco
- [x] CORR-PES2-013 — gate vermelho na imagem golden, sem veredito escrito
- [x] CORR-PES2-014 — 18 dos 105 `TEX_*` são Form 2, não os 105
- [x] CORR-PES2-015 — offset de forma citado como cor, e noutro arquivo
- [x] CORR-PES2-016 — profundidade decidida por contêiner, não por paleta
- [x] CORR-PES2-017 — a Fase 7 não tem verificações escritas no perfil
- [x] CORR-PES2-018 — dois números da §1.14(g) não batem com a ferramenta
- [x] CORR-PES2-019 — o `import` aceita a profundidade errada
- [x] CORR-PES2-020 — a conferência antes do disco não é exercitada
- [x] CORR-PES2-021 — o 0,019 entre binários foi desmentido pela própria task
- [x] CORR-PES2-022 — duas tasks saíram da fila de revisão sem terem sido revisadas
- [x] CORR-PES2-023 — a Fase 0 não tem verificações escritas no perfil
- [x] CORR-PES2-024 — o caso vermelho não confere a tela nem tem caminho versionado
- [x] CORR-PES2-025 — a §3.2 descreve como aberto um item que a 34 fechou
- [x] CORR-PES2-026 — o offset da RAM ficou no valor de antes do conserto de 45 bytes
- [x] CORR-PES2-027 — o gate de boot se reporta *skipped* na única receita escrita
- [x] CORR-PES2-028 — o fork publica binário próprio, e ele tem o MCP
- [x] CORR-PES2-029 — dois caminhos de falha saem como traceback em vez de recusa
- [x] CORR-PES2-030 — o gate de boot falha na tela parada, e diz que o emulador morreu
- [x] CORR-PES2-031 — o fluxo A não virou ferramenta, como o fluxo C virou
- [x] CORR-PES2-032 — a queda intermitente do emulador não está escrita em lugar nenhum

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

### CORR-PES2-009

- **Arquivo com problema:** `tools/pes2/lzss.py`, o `--check`; e por herança o
  `pes2_image` do `ctest`, que o roda
- **Sintoma:** com `count = b - 0xB9` (o bug do `k3` assinado que a própria
  task nomeia), `(EsIt)` cai de 172 inteiros / 2.153 blocos para 41 / 812, e o
  `--check` imprime `CHECK OK` e sai 0. O laço de estabilidade compara
  `decompress` consigo mesmo; o `--roundtrip` é cego ao mesmo bug porque o
  `compress` daqui nunca emite `0xC0..0xFE`
- **Como foi detectado:** revisão da PES2-TASK-26 — cópia da ferramenta no
  scratchpad com o bug reintroduzido
- **Fix:** assertar valor medido por disco (as quatro linhas que a §1.14(e) já
  publica), ou digest do primeiro bloco de `TEX_00.BIN`; e corrigir o `--help`

### CORR-PES2-010

- **Arquivo com problema:** `tools/pes2/lzss.py`, `scan()` e `PROBE_CAP`; e a
  definição do verdicto `none` na §1.14(e) do plano
- **Sintoma:** `minimum=1024` é o que separa `none` de `partial` — com 64 todo
  arquivo `none` produz blocos —, o menor bloco real do disco tem 1.152 B, e a
  margem de 128 B nunca foi escrita. O comentário do `PROBE_CAP` diz que o
  maior bloco é 16 KiB; são 16.676, com cinco acima de 16 KiB em `(EsIt)`
- **Como foi detectado:** revisão da PES2-TASK-26 — varredura com
  `minimum=64` sobre os 36 não-`whole`, e distribuição de tamanho dos 2.153
  blocos
- **Fix:** nomear o limiar com o número que o justifica, publicar a
  distribuição, e a §1.14(e) dizer "não decodifica para 1 KiB ou mais"

### CORR-PES2-011

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md` §1.14(e)
- **Sintoma:** o prefixo `0f 80 0a 00 20 02 80 01`, apresentado como a forma
  dos registros de 16 B da cauda, é o do **quarto**: o primeiro é
  `00 00 0a 00 00 02 00 01`, e o literal só aparece em 53066. Os 15.538 bytes,
  esses, conferem exatamente
- **Como foi detectado:** revisão da PES2-TASK-26 — dump da cauda de
  `DAT2D.BIN` a partir do fim do último bloco
- **Fix:** citar o primeiro registro e o que é comum aos quatro (`0a 00` nos
  bytes 2-3, `20 00 80 00` nos 8-11, os quatro últimos crescendo)

### CORR-PES2-012

- **Arquivo com problema:** `docs/tasks/progresso.md` (estado medido e
  checklist da Fase 7) e `docs/tasks/26-codec-lzss.md` (Contexto e critério)
- **Sintoma:** "208 no PES2, 195 no WE2002" e "os 208 contêineres de cada
  release"; medido, são 208, 210, 177 e 195 — a contagem é do disco, não do
  jogo, e os "13 de diferença" comparam duas pontas de uma faixa de quatro
- **Como foi detectado:** revisão da PES2-TASK-26 — `lzss.py --check` nos
  quatro discos, cujo cabeçalho imprime a contagem de cada um
- **Fix:** dar os quatro números por disco e tirar o número do item de
  checklist, que quer garantir os três verdictos, não a contagem

### CORR-PES2-013

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md` §1.14(f), e o gate
  `bin_archive.py check` na imagem golden European Deluxe
- **Sintoma:** a §1.14(f) diz que as falhas são "todas em `GDC_*` … nenhuma
  fora dos estádios, nos quatro discos"; na golden há uma fora — o registro em
  18052 de `/BIN/TEX_70.BIN`, que não é estádio nem Form 2 —, e é ela mais os
  cinco *outros* que fazem o `check` sair **1** com `CHECK FAILED` naquele
  disco. Nenhum documento registra que o gate é vermelho ali
- **Como foi detectado:** revisão da PES2-TASK-27 — `bin_archive.py check` nos
  quatro discos, com o código de saída
- **Fix:** escrever o veredito (esperado, seis registros, disco hackeado) ou
  contá-los à parte, como já se fez com os estádios da §1.14(d)

### CORR-PES2-014

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md` §1.14(e),
  `docs/PLAN-FEATURES.md` §5c, e o Log da PES2-TASK-26 e o Contexto da
  PES2-TASK-27
- **Sintoma:** "na imagem golden European Deluxe os **105** `TEX_*.BIN` são
  Form 2". Medido: **18**; os outros 87 são Form 1 e o `bin_archive.py` desta
  mesma task os lê — `TEX_03`, `TEX_06`, `TEX_28`, `TEX_70` e `TEX_84`
  aparecem no relatório dele
- **Como foi detectado:** revisão da PES2-TASK-27 — `is_form1()` sobre os 105
  nos três discos
- **Fix:** "18 dos 105", com o comando; a explicação do `TEX_00` continua
  valendo, porque ele é um dos 18

### CORR-PES2-015

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md` §1.14(f) e o repasse em
  `docs/tasks/14-bandeiras.md`
- **Sintoma:** "os quatro `OFS_FLAG_*` caem em `/BIN/DAT2D.BIN` nos offsets
  69798, 72400, 73254 e 73728". O **72400** é `OFS_FLAG_SHAPE_COPY_4` —
  forma, não cor — e mora em **`/SELFORM.BIN`**; o quarto de cor,
  `OFS_FLAG_COLOURS_B`, está em **75776** e ficou de fora
- **Como foi detectado:** revisão da PES2-TASK-27 — `ofs_map.locate()` sobre
  os nove `OFS_FLAG_*`; o resumo do `ofs_map.py` corta em três por arquivo, o
  que escondeu o quarto de `DAT2D.BIN`
- **Fix:** 69798, 73254, 73728, 75776; e uma linha dizendo onde moram os cinco
  `OFS_FLAG_SHAPE_COPY_*`

### CORR-PES2-016

- **Arquivo com problema:** `tools/pes2/bin_archive.py`, `depth_of()`; e a
  regra como enunciada na §1.14(f)
- **Sintoma:** a profundidade é decidida por contêiner com `max(widths)`, e o
  `/BIN/DAT2D.BIN` das duas releases de PES2 tem **261 CLUTs de 16 cores e 5
  de 256** — o arquivo inteiro é lido a 8 bpp por causa dos cinco. Silencioso:
  a contagem de bytes não muda com a profundidade, então o `check` fica verde
  e o `export` escreve PNG errado. É o arquivo para o qual a §1.14(f) manda a
  PES2-TASK-14 olhar
- **Como foi detectado:** revisão da PES2-TASK-27 — larguras de CLUT por
  contêiner nos três discos originais
- **Fix:** profundidade do **par imagem-paleta**, saindo do CLUT em uso; o
  `check` conta os contêineres de largura mista em vez de escondê-los

### CORR-PES2-017

- **Arquivo com problema:** `docs/prompts/perfil-pes2.md`
- **Sintoma:** a seção "Verificações específicas por fase" vai da Fase 2 à 6 e pula a 7, que já teve as tasks 26, 27, 28 e 29 executadas.
- **Como foi detectado:** `sed -n '/Verificações específicas por fase/,$p' docs/prompts/perfil-pes2.md | grep '^\*\*Fase'` — a Fase 7 não aparece.
- **Fix:** acrescentar a seção da Fase 7, com as perguntas que as quatro tasks já executadas mostraram valer.

### CORR-PES2-018

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md` §1.14(g) e `docs/tasks/29-gravacao-de-asset.md`
- **Sintoma:** afirmam "10 de 13 recomprimem dentro do orçamento" e "folga de 0 a 4 bytes"; a medição completa dá **9 de 13** e **0 a 3**.
- **Como foi detectado:** rodando o laço sem o filtro `if i < 4 or ok`, que escondia a entrada 8 do `LOGO.BIN` — 1.081 B contra 1.076 de folga.
- **Fix:** um subcomando `budget` no `asset_write.py` que imprime a conta, e os dois números corrigidos a partir dele.

### CORR-PES2-019

- **Arquivo com problema:** `tools/pes2/asset_write.py`, `cmd_import`
- **Sintoma:** um PNG de 4 bpp exportado do `LOGO.BIN` é aceito e gravado no `TITLE.BIN`, que é 8 bpp. A dimensão em pixels é a mesma nos dois e a contagem de bytes também, então nenhuma das três validações existentes dispara.
- **Como foi detectado:** `export` do `/BIN/LOGO.BIN` entrada 2 seguido de `import` no `/BIN/TITLE.BIN` entrada 2, sobre cópia: `written, and verified before it went`, exit 0.
- **Fix:** derivar a profundidade do PNG do tamanho da `PLTE`, recusar quando não for a do destino, comparar a paleta com o CLUT do slot, e exercitar a recusa no `check`.

### CORR-PES2-020

- **Arquivo com problema:** `tools/pes2/asset_write.py`, `rewrite_image`
- **Sintoma:** a conferência `decompress(compress(x)) == x` roda antes de toda gravação e nunca foi vista recusando; o `check` só a atravessa em verde.
- **Como foi detectado:** lendo o que o `check` exercita — a guarda de orçamento aparece em vermelho, esta não aparece.
- **Fix:** ponto de injeção privado para um codec defeituoso, e um caso no `check` que exige o `Refused`.

### CORR-PES2-030

- **Arquivo com problema:** `tools/pes2/boot_check.sh`, a asserção de vida
  (linhas 178-182)
- **Sintoma:** o gate tira dois quadros em relógio fixo — 45 s e mais 12 s — e
  exige que difiram. Numa tela de abertura estática os dois saem **byte a
  byte iguais** e ele imprime `FAIL: the two frames are the same -- it is not
  running` sobre um emulador vivo: `sd=0,13657` é conteúdo desenhado, a janela
  existia e o MCP respondeu. Medido em três corridas seguidas do mesmo
  comando: 0 de 524.000 pixels na primeira, 260.000 nas duas seguintes
- **Como foi detectado:** a verificação final da [CORR-PES2-027](/docs/tasks/CORR-PES2-027.md),
  que é o que fez o `pes2_boot` correr pela receita pela primeira vez — o gate
  passou a ser exercitado, e a intermitência apareceu na segunda corrida
- **Fix:** a prova de vida não pode depender de o jogo animar naquele
  instante. Amostrar N vezes ao longo do `PES2_GAP` e exigir que alguma difira;
  ou perguntar a contagem de quadros ao MCP do fork, degradando para a tela
  quando o binário é o AppImage. E a mensagem tem de dizer o que foi medido —
  "estas duas amostras são idênticas" — e não a conclusão

### CORR-PES2-021

- **Arquivo com problema:** `tools/pes2/boot_check.sh`, linha 38
- **Sintoma:** o cabeçalho justifica o gate nomear o binário dizendo que "the title screen's standard deviation differs by 0.019 between them"; a tabela da §6.14, escrita no mesmo commit, mede 0,359942..0,360497 (fork) contra 0,358742 (AppImage) — ~0,0015 — e descarta explicitamente o binário como causa dos 0,019.
- **Como foi detectado:** `grep -rn "0\.019"` na árvore, e a rota `main-menu` remedida nesta revisão: `sd=0.359966` no fork.
- **Fix:** reescrever o parágrafo com o que a §6.14 sustenta — as médias sobrevivem, o desvio não se reproduz nem no mesmo binário, e é por isso que o gate precisa dizer qual binário correu.

### CORR-PES2-022

- **Arquivo com problema:** `docs/tasks/progresso.md`, linhas das PES2-TASK-32 e 33
- **Sintoma:** a célula "Revisado em" das duas tem `✅ Concluído`, que é o símbolo da coluna vizinha. Nenhuma das duas foi revisada — não há commit de revisão nem CORR de origem —, e o valor as tirou da fila do `/revisar`.
- **Como foi detectado:** `git show 65e980a:docs/tasks/progresso.md` contra `4d3a574`, mais `git log --oneline --all | grep review` e `grep -c "PES2-TASK-3" correcoes-progresso.md`.
- **Fix:** repor `⬜ pendente` nas duas células e cercar o rito no `01-executar.md`.

### CORR-PES2-023

- **Arquivo com problema:** `docs/prompts/perfil-pes2.md`, "Verificações específicas por fase"
- **Sintoma:** não há entrada de Fase 0; o parágrafo diz "Não há task de trabalho nelas" com quatro tasks de Fase 0 no quadro e três delas entregando ferramenta; e diz "As seis fases" onde a §5 tem oito.
- **Como foi detectado:** `grep "^\*\*Fase" perfil-pes2.md` contra `grep "^### Fase" PLAN-PES2-PSX.md`, e a contagem da coluna Fase do `progresso.md`.
- **Fix:** separar a Fase 1 (fechada) da Fase 0, escrever a lista de Fase 0, e corrigir a contagem.

### CORR-PES2-024

- **Arquivo com problema:** `tools/pes2/mcp_drive.py`, `measure_menu`
- **Sintoma:** o caso vermelho que o perfil promove a gate não confere estar no menu principal antes de medir, e nenhum comando versionado deixa o emulador parado lá — toda rota o mata no `__exit__`. O que salvou a corrida foi um save state não versionado que sobrou da task.
- **Como foi detectado:** `--screen main-menu` seguido de `--measure-menu` devolve `skipping: no MCP server`; a corrida só fechou com `fork.py launch` + `mcp.py --call load_state slot=1`.
- **Fix:** verificar `MAIN_MENU_MEAN ± MAIN_MENU_TOL` antes de medir, e dar um caminho versionado até o estado (`--keep-alive` ou `--measure-menu <imagem>`).

### CORR-PES2-025

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md`, §3.2, linha 1004
- **Sintoma:** a tabela do emulador diz que onde o fork mora "é item aberto da PES2-TASK-34"; a task fechou o item e a §6.14, o `CLAUDE.md` e o perfil já dizem `~/Applications/duckstation-mcp/`.
- **Como foi detectado:** `grep -n "item aberto" docs/PLAN-PES2-PSX.md`, contra `python3 tools/pes2/fork.py which`.
- **Fix:** trocar a oração pelo caminho, com a nota de licença.

### CORR-PES2-026

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md` §6.14 e o Log da PES2-TASK-32
- **Sintoma:** os dois dizem que a RAM começa no offset 6799 do fluxo inflado; o `savestate.py` mede 6754 em oito estados, inclusive um de hoje. A diferença são os 45 bytes que a PES2-TASK-33 corrigiu — ela reescreveu os dois endereços (+45) e não o deslocamento (−45).
- **Como foi detectado:** `savestate.py info` nos oito estados da POC contra `grep -rn "6799" docs/`.
- **Fix:** trocar para 6754 e escrever de onde ele vem, para o próximo conserto de base não deixar o número para trás.

### CORR-PES2-027

- **Arquivo com problema:** `CLAUDE.md`, `docs/prompts/perfil-pes2.md`, `tools/pes2/boot_check.sh`
- **Sintoma:** a receita de `ctest -R pes2` documentada só define `WE2002_PES2_*`, e o `boot_check.sh` pula sem `PES2_IMAGE`. O único gate que põe o jogo na tela nunca corre, e o skip é igual ao de uma máquina sem emulador.
- **Como foi detectado:** `WE2002_PES2_IMAGE=… ctest -R pes2_boot` → `***Skipped 0.01 sec`; a mesma corrida com `PES2_IMAGE=<copia>.cue` fecha `BOOT OK`.
- **Fix:** pôr `PES2_IMAGE` (o `.cue`) na receita dos dois docs, e fazer o skip distinguir variável trocada de máquina sem emulador.

### CORR-PES2-028

- **Arquivo com problema:** `docs/PLAN-PES2-PSX.md` §6.14, critério da PES2-TASK-32, `tools/pes2/fork.py recipe`
- **Sintoma:** os dois docs afirmam que o fork "não publica binário próprio". Ele publica quatorze na release `latest`, de 2026-08-29, e o `DuckStation-x64.AppImage` dela traz `EnableMCPServer`, `MCPServerPort` e `duckstation-mcp`. O custo de ter um binário com MCP é um download, não 107 s de compilação — e a receita só conhece o caminho longo.
- **Como foi detectado:** `gh api repos/sadnescity/duckstation/releases`, download do AppImage, `--appimage-extract` e `strings -a … | grep -x EnableMCPServer` → 1.
- **Fix:** corrigir a frase nos dois lugares, pôr o download como primeiro caminho da receita com a conferência por `strings`, e registrar que o engano veio de ler o README (que é o do upstream) em vez da aba de releases.

### CORR-PES2-029

- **Arquivo com problema:** `tools/pes2/savestate.py`, `tools/pes2/selftest.py`
- **Sintoma:** arquivo que não é save state recebe `error: … not DUCC`; arquivo que não existe recebe `FileNotFoundError` cru. E o `except savestate.Skip` do `selftest.py`, com o import dentro do mesmo `try`, vira `NameError` se o import falhar — que o `except Exception` irmão não pega.
- **Como foi detectado:** `savestate.py info /nao/existe.sav` contra `savestate.py info CLAUDE.md`; o padrão do `except` reproduzido isolado.
- **Fix:** recusar `OSError` com a forma `error: …` em todos os subcomandos, tirar o import do `try` no `selftest.py`, e um caso vermelho de estado ausente no `self_check`.

### CORR-PES2-031

- **Arquivo com problema:** `tools/pes2/` — nenhuma ferramenta arma breakpoint
- **Sintoma:** o fluxo A é a justificativa inteira do fork depois que a PES2-TASK-32 entregou C e D em Python puro, e ele não virou comando: `grep -rn "breakpoint" tools/pes2/*.py` devolve só um comentário dizendo que ele é preciso. O fluxo C virou `savestate.py scan`, com selftest e casos vermelhos; o A virou um parágrafo de Log.
- **Como foi detectado:** ao tentar reproduzir o disparo desta revisão foi preciso escrever a sequência MCP à mão — e foi nesse caminho que a queda da CORR-PES2-030 apareceu.
- **Fix:** `who_writes.py <endereço>`, com espera que distingue queda de servidor ausente, `--self-check` no `pes2_selftest`, e uma linha na tabela de gates.

### CORR-PES2-032

- **Arquivo com problema:** o binário do fork, mais `tools/pes2/mcp.py`, `tools/pes2/fork.py` e a §6.11 do plano
- **Sintoma:** o emulador de trabalho cai sozinho durante execução livre — quatro mortes em seis corridas, de 15 s a 90 s —, sem log, sem core dump e sem journal; um controle de 75 s sem chamada MCP sobreviveu. Nada avisa, e a mensagem de servidor ausente diz "the fork is not running. Start it with fork.py launch", que descreve esquecimento e não queda.
- **Como foi detectado:** seis corridas nesta revisão, com `pgrep -x duckstation-qt` mostrando o processo sumido; o log do `fork.py` tem três linhas de Qt depois de todas elas.
- **Fix:** armadilha 35 na §6.11 com a contagem recontada, mensagem que distingue "caiu" de "nunca subiu", e log que acumula em vez de truncar.

