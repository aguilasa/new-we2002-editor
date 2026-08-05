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
| [CORR-WTE-005](/docs/tasks/CORR-WTE-005.md) | [WTE-TASK-03](/docs/tasks/03-extrator-de-dfm.md) | Os streams sintéticos que sustentam "os 21 `TValueType` exercitados" não são versionados | Baixa | [ ] pendente | — |

## Checklist

- [x] CORR-WTE-001 — sincronizar `status:` do frontmatter, e citá-lo no `01-executar.md`
- [x] CORR-WTE-002 — escrever no `ambiente.md` como remedir os dois números derivados
- [x] CORR-WTE-003 — ancorar `lib/` e `backup/` no `wte/`, onde a seção diz que valem
- [x] CORR-WTE-004 — blob ausente vira aviso; blob divergente continua falha
- [ ] CORR-WTE-005 — versionar os streams sintéticos do `dfm_extract.py`

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
