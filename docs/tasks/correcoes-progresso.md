# Progresso de Correções — WE2002 Team Editor → Lazarus

Correções abertas pelo `/revisar` ([`../prompts/02-revisar.md`](/docs/prompts/02-revisar.md))
e fechadas pelo `/corrigir`. O andamento das **tarefas** fica em
[`progresso.md`](/docs/tasks/progresso.md); este arquivo só rastreia correção.

**"Concluída em" nasce `—`** e é preenchida por quem executa a correção, com a
data do commit — o `/revisar` abre a correção, não a fecha.

## Resumo executivo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
|---|---|---|---|---|---|
| [CORR-WTE-001](/docs/tasks/CORR-WTE-001.md) | [WTE-TASK-01](/docs/tasks/01-ferramental.md) | Frontmatter da task diz `pendente` numa tarefa concluída | Baixa | [x] concluída | 2026-08-05 |
| [CORR-WTE-002](/docs/tasks/CORR-WTE-002.md) | [WTE-TASK-01](/docs/tasks/01-ferramental.md) | Dois números do `ambiente.md` só são reproduzíveis pelo scratchpad | Baixa | [x] concluída | 2026-08-05 |
| [CORR-WTE-003](/docs/tasks/CORR-WTE-003.md) | [WTE-TASK-02](/docs/tasks/02-esqueleto-do-projeto.md) | A seção `wte/` do `.gitignore` ignora `lib/` e `backup/` no repositório inteiro | Baixa | [x] concluída | 2026-08-05 |
| [CORR-WTE-004](/docs/tasks/CORR-WTE-004.md) | [WTE-TASK-03](/docs/tasks/03-extrator-de-dfm.md) | `--check` fica vermelho num clone limpo, porque `blobs/` é gitignored | Baixa | [x] concluída | 2026-08-05 |
| [CORR-WTE-005](/docs/tasks/CORR-WTE-005.md) | [WTE-TASK-03](/docs/tasks/03-extrator-de-dfm.md) | Os streams sintéticos que sustentam "os 21 `TValueType` exercitados" não são versionados | Baixa | [x] concluída | 2026-08-06 |
| [CORR-WTE-006](/docs/tasks/CORR-WTE-006.md) | [WTE-TASK-04](/docs/tasks/04-mapa-de-handlers.md) | Os fatos medidos pela WTE-TASK-04 não chegaram aos seis documentos que serão executados | Alta | [x] concluída | 2026-08-06 |
| [CORR-WTE-007](/docs/tasks/CORR-WTE-007.md) | [WTE-TASK-04](/docs/tasks/04-mapa-de-handlers.md) | A tabela de envelhecimento do `published_methods.md` erra uma atribuição e omite três divergências | Baixa | [x] concluída | 2026-08-06 |
| [CORR-WTE-008](/docs/tasks/CORR-WTE-008.md) | [WTE-TASK-05](/docs/tasks/05-inventario-de-strings.md) | O decodificador de instrução x86 só foi conferido à mão, e a coluna `handler` inteira depende dele | Baixa | [x] concluída | 2026-08-06 |
| [CORR-WTE-009](/docs/tasks/CORR-WTE-009.md) | [WTE-TASK-05](/docs/tasks/05-inventario-de-strings.md) | A §8.8 e a pendência do `progresso.md` ainda tratam o binário espanhol como única rota para as mensagens decepadas | Baixa | [ ] pendente | — |

## Checklist

- [x] CORR-WTE-001 — sincronizar `status:` do frontmatter, e citá-lo no `01-executar.md`
- [x] CORR-WTE-002 — escrever no `ambiente.md` como remedir os dois números derivados
- [x] CORR-WTE-003 — ancorar `lib/` e `backup/` no `wte/`, onde a seção diz que valem
- [x] CORR-WTE-004 — blob ausente vira aviso; blob divergente continua falha
- [x] CORR-WTE-005 — versionar os streams sintéticos do `dfm_extract.py`
- [x] CORR-WTE-006 — propagar dono e contagem medidos para as tasks 25, 28, 30, o plano §5.1 e o prompt de revisão
- [x] CORR-WTE-007 — corrigir a atribuição e completar a tabela de envelhecimento, no gerador
- [x] CORR-WTE-008 — versionar a conferência do decodificador x86 contra o `objdump`
- [ ] CORR-WTE-009 — dizer na §8.8 que as mensagens decepadas têm cópia dentro do próprio `.exe`

## Detalhes por correção

### CORR-WTE-001

- **Arquivo com problema:** `docs/tasks/01-ferramental.md` (frontmatter), com a
  causa em `docs/prompts/01-executar.md`
- **Sintoma:** `status: pendente` numa tarefa que o `progresso.md` registra como
  `✅ Concluído` em 2026-08-05, com os seis critérios `[x]`
- **Como foi detectado:** `grep '^status:' docs/tasks/*.md` confrontado com a
  tabela de resumo do `progresso.md`
- **Fix:** trocar para `concluído` no arquivo da task e acrescentar o passo à
  seção "4) Atualizar progresso" do `01-executar.md`, para não repetir nas 39
  tarefas restantes

### CORR-WTE-002

- **Arquivo com problema:** `wte/re/ambiente.md`
- **Sintoma:** os dois blocos de "Achado" citam evidência que mora no scratchpad
  da execução (`ShowInfo.java`, `wte-windows.tsv`) e não trazem o comando que a
  regera — os únicos números do arquivo sem a coluna "Como foi medido"
- **Como foi detectado:** `git ls-files wte/` devolve só o `.md`; os números
  foram reproduzidos a partir do scratchpad ainda não limpo, que some no próximo
  boot
- **Fix:** inlinar no `ambiente.md` o `analyzeHeadless` + `ShowInfo.java` e o
  laço `xdotool` do censo de janelas, e remover a referência ao caminho volátil.
  Os valores estão certos; o que falta é a rota de volta

### CORR-WTE-003

- **Arquivo com problema:** `.gitignore`, seção
  `# ---- Projeto Lazarus em wte/ (WTE-TASK-02) ----`
- **Sintoma:** `lib/` e `backup/` entraram sem âncora, então valem para o
  repositório inteiro — inclusive a árvore do `newWe2002`, que a task tinha o
  critério explícito de não tocar. As regras vizinhas da mesma seção
  (`wte/build/`, `wte/assets`) são ancoradas
- **Como foi detectado:** `git check-ignore -v src/lib/x.cpp tools/lib/z.py
  legacy/backup/y.txt` casa nas linhas 69 e 70 do `.gitignore`
- **Fix:** trocar por `wte/lib/` e `wte/backup/`. Impacto atual é zero — nada
  rastreado casa —, o defeito é latente: arquivo que some sem aparecer no
  `git status`. As três regras de extensão (`*.lps`, `*.ppu`, `*.compiled`)
  ficam como estão

### CORR-WTE-004

- **Arquivo com problema:** `wte/tools/dfm_extract.py`, função `do_check()`
- **Sintoma:** os 118 `.bin` de `wte/re/dfm/blobs/` são gitignored e só nascem
  no modo de escrita, mas `--check` exige que existam. Num clone limpo com o
  `.exe` presente e a árvore versionada intacta, `make -C wte check` sai
  vermelho com 118 linhas de `nao existe` — o mesmo código de saída de um `.dfm`
  editado à mão, que é o que o gate existe para pegar
- **Como foi detectado:** `do_check()` rodado contra uma sandbox com a árvore
  versionada correta e `blobs/` ausente (cópia em scratchpad, sem tocar na
  árvore real); e a mesma sandbox com uma linha de `ficha_about.dfm` alterada.
  Os dois estados devolvem 1
- **Fix:** blob ausente vira aviso e sai 0; blob presente e divergente, ou blob
  sobrando, continuam falha. A garantia byte a byte não muda — ela vem do
  SHA-256 dentro do `.dfm` versionado, que a comparação de texto já cobre

### CORR-WTE-005

- **Arquivo com problema:** `wte/tools/` — falta o teste; o Log da WTE-TASK-03 é
  quem afirma a cobertura
- **Sintoma:** o Log diz que os `TValueType` ausentes dos 18 formulários "foram
  exercitados contra streams sintéticos", e o critério "tipo desconhecido aborta
  com offset" está `[x]`. Os streams não estão no repositório. Metade dos
  caminhos afirmados (`vaCollection`, `vaSet`, `vaExtended`, `vaInt64`,
  `vaWString`, as três flags de objeto, as quatro rotas de aborto) não ocorre no
  `.exe`, então `--check` verde não diz nada sobre eles
- **Como foi detectado:** `git ls-files wte | grep -i test` devolve só
  `wte/tests/README.md`, que reserva a pasta para o lado Pascal a partir da
  WTE-TASK-20. Os caminhos foram refeitos à mão nesta revisão e respondem como o
  Log descreve — é esse trabalho que precisa virar arquivo
- **Fix:** `wte/tools/test_dfm_extract.py` em stdlib pura (ou `--selftest` no
  próprio gerador), cobrindo os 21 tipos, as três flags e cada rota de aborto
  com o offset absoluto conferido na mensagem

### CORR-WTE-006

- **Arquivo com problema:** `docs/tasks/25-handlers-de-carga.md`,
  `docs/tasks/28-handlers-auxiliares.md`, `docs/tasks/30-preco-do-jogador.md`,
  `docs/PLAN-WTE-LAZARUS.md` (§5.1), `docs/tasks/04-mapa-de-handlers.md`,
  `docs/prompts/02-revisar.md`
- **Sintoma:** a WTE-TASK-04 mediu e listou sete divergências, mas a lista mora
  só em `wte/re/published_methods.md`. Os documentos que comandam a execução
  continuam dizendo `FormCreate`/`FormShow` em 19 endereços (são 18),
  `malla1MouseDown`/`malla2MouseDown` em `ficha_color`/`ficha_creditos_equipo`
  (são de `estrategia`), `etiqprecioClick` em `ficha_creditos_equipo` (é de
  `jugador`, em dois arquivos) e seis handlers de ocorrência única na lista de
  "repetidos". O prompt de revisão pede `FormCreate` 17 vezes, e reprovaria uma
  fase 2 correta
- **Como foi detectado:** `cut -f2,3 wte/re/published_methods.tsv | sort |
  uniq -c` confrontado com `grep` nos seis arquivos; e o cruzamento
  independente pelo lado do DFM (219 ligações → 95 pares, todos no TSV)
- **Fix:** trocar o texto pelo medido em cada arquivo. Os números do censo da
  §1 ficam de fora — são da WTE-TASK-09

### CORR-WTE-007

- **Arquivo com problema:** `wte/tools/dump_published.py`, `render_md()`
  (a saída `wte/re/published_methods.md` é gerada)
- **Sintoma:** a tabela "Onde o plano e as tarefas envelheceram" atribui à §1.4
  do plano a frase "`FormCreate` aparece 17 vezes", que o plano não contém — ela
  está na task 04 e no `02-revisar.md`. E omite três divergências do mesmo tipo:
  o dono errado repetido na task 30, `BitBtn1Click` 3× na task 28 (são 4) e
  cinco handlers de ocorrência única listados como repetidos, dos quais o `.md`
  registra só `botonClick`
- **Como foi detectado:** `grep -rn "FormCreate" docs/PLAN-WTE-LAZARUS.md` não
  devolve o "17"; `grep -rn "17 vezes" docs/` devolve os dois arquivos que o
  têm. As contagens saem do TSV gerado, que a própria seção "Homônimos" do
  `.md` já imprime certas
- **Fix:** no gerador — corrigir a atribuição e derivar as linhas faltantes de
  `count_by_name(m)`, abortando se um nome citado da task 28 não existir entre
  os 96, como `EXCEPTIONS` e `FORMULA_OWNERS` já fazem

### CORR-WTE-008

- **Arquivo com problema:** `wte/tools/dump_strings.py` — `decode()` e
  `extent()`, o decodificador de comprimento de instrução x86-32
- **Sintoma:** a coluna `handler` das 474 referências, os 122 pares
  string↔handler, a cobertura de 26,8% da `.text` e as tabelas das perguntas 2 e
  3 saem de medir onde cada handler termina. O `strings.md` diz, corretamente,
  que a conferência contra o `objdump` "é manual e não roda no `--check`". A
  convenção que faltava — `wte/tools/test_<gerador>.py` — passou a existir com a
  CORR-WTE-005, depois desta tarefa
- **Como foi detectado:** a conferência foi refeita nesta revisão com harness
  próprio e **reproduz**: 10.416 fronteiras contra 10.416, zero divergência. Mas
  a primeira tentativa deu 48 falsos positivos (linhas de continuação do
  `objdump`, sem mnemônico) — número que só volta assim é número sem rota de
  volta, como o da CORR-WTE-002
- **Fix:** `wte/tools/test_dump_strings.py` com duas metades — comprimento por
  caso sem o `.exe`, e a conferência contra o `objdump` sob `skipUnless`,
  descartando as linhas sem mnemônico

### CORR-WTE-009

- **Arquivo com problema:** `docs/PLAN-WTE-LAZARUS.md` (§8.8) e
  `docs/tasks/progresso.md` (pendências externas)
- **Sintoma:** os dois dizem que conseguir o binário original em espanhol é o
  que devolveria as mensagens que o tradutor decepou. Medido na WTE-TASK-05: o
  bloco de literais aparece três vezes em `.data`, as duas cópias altas não são
  referenciadas por ponteiro nenhum, e nelas o texto está inteiro — inclusive a
  mensagem que a própria §8.8 cita como exemplo (`somente na Mastere`, que na
  cópia morta lê `somente na Master    )`)
- **Como foi detectado:** coluna `copia_de` do `strings.tsv` (371 das 765 com
  gêmea) e as três marcadas `gemea_difere`, confrontadas com o texto da §8.8
- **Fix:** trocar a saída nas duas passagens — o binário espanhol continua bom
  de ter e continua não bloqueante, mas deixa de ser a única rota. O número "70"
  fica onde está: é da WTE-TASK-09
