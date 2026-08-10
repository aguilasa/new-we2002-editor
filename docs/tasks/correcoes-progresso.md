# Progresso de Correções — WE2002 Team Editor → Lazarus

Correções abertas pelo `/revisar` ([`../prompts/02-revisar.md`](/docs/prompts/02-revisar.md))
e fechadas pelo `/corrigir`. O andamento das **tarefas** fica em
[`progresso.md`](/docs/tasks/progresso.md); este arquivo só rastreia correção.

**"Concluída em" nasce `—`** e é preenchida por quem executa a correção, com a
data do commit — o `/revisar` abre a correção, não a fecha.

**Números não usados:** o **CORR-WTE-033** foi pulado na numeração — a revisão
da WTE-TASK-15 (commit `f50d263`) abriu 030, 032, 034 e 035, e nenhuma 033 foi
escrita. Não há correção perdida; o número simplesmente não existe. Registrado
aqui para que a lacuna não seja lida como arquivo sumido.

**Correção envelhecida:** a **CORR-WTE-037** aparece `[x] envelhecida`. Não
houve conserto de código — o sintoma deixou de existir entre a abertura e a
execução, e o Log dela traz as três medidas que mostram isso. `[x]` ali quer
dizer "fechada e fora do backlog", não "corrigida".

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
| [CORR-WTE-009](/docs/tasks/CORR-WTE-009.md) | [WTE-TASK-05](/docs/tasks/05-inventario-de-strings.md) | A §8.8 e a pendência do `progresso.md` ainda tratam o binário espanhol como única rota para as mensagens decepadas | Baixa | [x] concluída | 2026-08-06 |
| [CORR-WTE-010](/docs/tasks/CORR-WTE-010.md) | [WTE-TASK-06](/docs/tasks/06-mapa-de-offsets.md) | A §8.7 do plano aponta o lado errado da tabela, e o ASCII citado não é o do binário | Alta | [x] concluída | 2026-08-06 |
| [CORR-WTE-011](/docs/tasks/CORR-WTE-011.md) | [WTE-TASK-06](/docs/tasks/06-mapa-de-offsets.md) | O critério de limite do `dump_offsets.py` aborta num sentido só, e a janela de plausibilidade sai do nosso `Offsets.hpp` | Baixa | [x] concluída | 2026-08-06 |
| [CORR-WTE-012](/docs/tasks/CORR-WTE-012.md) | [WTE-TASK-07](/docs/tasks/07-unidades-duvidosas.md) | A §1 do plano diz 300 imports de `rtl60`/`vcl60` (são 267) e chama o `TBrowseURL` de componente de terceiro | Alta | [x] concluída | 2026-08-06 |
| [CORR-WTE-013](/docs/tasks/CORR-WTE-013.md) | [WTE-TASK-07](/docs/tasks/07-unidades-duvidosas.md) | O decodificador x86 do `dump_units.py` é cópia verbatim do `dump_strings.py` e nenhum teste o alcança | Baixa | [x] concluída | 2026-08-06 |
| [CORR-WTE-014](/docs/tasks/CORR-WTE-014.md) | [WTE-TASK-08](/docs/tasks/08-convencao-dos-assets.md) | O "197 bitmaps" (são 198) não está no quadro de reconciliação da WTE-TASK-09 e sobrevive em nove lugares | Alta | [x] concluída | 2026-08-06 |
| [CORR-WTE-015](/docs/tasks/CORR-WTE-015.md) | [WTE-TASK-08](/docs/tasks/08-convencao-dos-assets.md) | Duas transcrições de evidência do `assets.md` não batem: o ano dos 195 `.bmp` e o endereço do `fread` | Baixa | [x] concluída | 2026-08-06 |
| [CORR-WTE-016](/docs/tasks/CORR-WTE-016.md) | [WTE-TASK-09](/docs/tasks/09-fechamento-fase-1.md) | A varredura de sítios para em `docs/` e `wte/re/`, e o `wte/README.md` ainda diz que a §1 do plano registra 197 bitmaps | Baixa | [x] concluída | 2026-08-06 |
| [CORR-WTE-017](/docs/tasks/CORR-WTE-017.md) | [WTE-TASK-09](/docs/tasks/09-fechamento-fase-1.md) | O `fase-1.md` separa offset de tabela de offset em `.text` por substring do endereço, e a igualdade que a prosa afirma não é conferida | Baixa | [x] concluída | 2026-08-06 |
| [CORR-WTE-018](/docs/tasks/CORR-WTE-018.md) | [WTE-TASK-09](/docs/tasks/09-fechamento-fase-1.md) | O `02-revisar.md` cita `~430`, `70` e `197` como "o que já está no plano", e o plano não diz mais isso | Baixa | [x] concluída | 2026-08-09 |
| [CORR-WTE-019](/docs/tasks/CORR-WTE-019.md) | [WTE-TASK-10](/docs/tasks/10-conversor-dfm-para-lfm.md) | A reversão que versionou 816.880 bytes de arte do Obocaman só está registrada num README derivado | Alta | [x] concluída | 2026-08-09 |
| [CORR-WTE-020](/docs/tasks/CORR-WTE-020.md) | [WTE-TASK-10](/docs/tasks/10-conversor-dfm-para-lfm.md) | A tabela `ACEITA`/`DESCARTA` diz ter sido medida na LCL 3.0 e nada remede; `LCL_VERSAO` é código morto | Alta | [x] concluída | 2026-08-09 |
| [CORR-WTE-021](/docs/tasks/CORR-WTE-021.md) | [WTE-TASK-10](/docs/tasks/10-conversor-dfm-para-lfm.md) | O critério "blobs visíveis na janela" foi adiado para a WTE-TASK-11, que não o tem | Baixa | [x] concluída | 2026-08-09 |
| [CORR-WTE-022](/docs/tasks/CORR-WTE-022.md) | [WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md) | O comando publicado da ordem de auto-create devolve 17 das 18 classes, e perde justamente `TMainForm` | Alta | [x] concluída | 2026-08-09 |
| [CORR-WTE-023](/docs/tasks/CORR-WTE-023.md) | [WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md) | O critério de build diz 2.482 linhas (são 2.562) e atribui os 2 hints ao Lazarus (são do `/etc/fpc.cfg`) | Alta | [x] concluída | 2026-08-09 |
| [CORR-WTE-024](/docs/tasks/CORR-WTE-024.md) | [WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md) | O sufixo ` [Lazarus]` não chegou à WTE-TASK-35 e o `--show` não chegou à WTE-TASK-12 | Baixa | [x] concluída | 2026-08-09 |
| [CORR-WTE-025](/docs/tasks/CORR-WTE-025.md) | [WTE-TASK-12](/docs/tasks/12-comparacao-visual.md) | A faixa `11797..26528` é posição do `cmp -l`, e a WTE-TASK-22 vai declará-la como offset | Alta | [x] concluída | 2026-08-09 |
| [CORR-WTE-026](/docs/tasks/CORR-WTE-026.md) | [WTE-TASK-13](/docs/tasks/13-trace-de-eventos.md) | A tabela do achado 2 se anuncia medida, e a coluna VCL não foi medida | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-027](/docs/tasks/CORR-WTE-027.md) | [WTE-TASK-14](/docs/tasks/14-fechamento-fase-2.md) | O `fase-2.md` emite link `/docs/...` de dentro de `wte/re/`, fora do perímetro da regra | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-028](/docs/tasks/CORR-WTE-028.md) | [WTE-TASK-14](/docs/tasks/14-fechamento-fase-2.md) | `conferir_vereditos()` guarda a coluna `Original`, não o veredito | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-029](/docs/tasks/CORR-WTE-029.md) | [WTE-TASK-16](/docs/tasks/16-gerador-de-tabelas.md) | O Log diz que a reconciliação do `fase-2.md` saiu em commit próprio, e ela saiu no mesmo | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-030](/docs/tasks/CORR-WTE-030.md) | [WTE-TASK-15](/docs/tasks/15-mapeamento-de-tipo.md) | O `tipos.md` conta 38 `strcpy`, e o `Database.cpp` tem 40 — os dois que faltam são `std::strcpy` | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-031](/docs/tasks/CORR-WTE-031.md) | [WTE-TASK-16](/docs/tasks/16-gerador-de-tabelas.md) | O `wte/tests/README.md` diz que a pasta está vazia e é só Pascal; tem dois arquivos, um em C++ | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-032](/docs/tasks/CORR-WTE-032.md) | [WTE-TASK-15](/docs/tasks/15-mapeamento-de-tipo.md) | A "regra zero" do `tipos.md` proíbe `LongInt` e `SizeInt` em campo de registro, e a tabela usa os dois | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-034](/docs/tasks/CORR-WTE-034.md) | [WTE-TASK-15](/docs/tasks/15-mapeamento-de-tipo.md) | A "entrada real medida" do `tipos.md` omite os cabeçalhos que declaram os campos que a tabela mapeia | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-035](/docs/tasks/CORR-WTE-035.md) | [WTE-TASK-15](/docs/tasks/15-mapeamento-de-tipo.md) | A decisão 5 do `tipos.md` não tem o "teste que prova", e o critério que o exige está marcado | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-036](/docs/tasks/CORR-WTE-036.md) | [WTE-TASK-17](/docs/tasks/17-transpilador-da-camada-de-dados.md) | A regra `!` → `not` do `SUBS` atravessa a quebra de linha e engole seis statements para dentro de comentário | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-037](/docs/tasks/CORR-WTE-037.md) | [WTE-TASK-17](/docs/tasks/17-transpilador-da-camada-de-dados.md) | A linha das recusas medidas na saída está deslocada, e o worklist da WTE-TASK-18 aponta para a linha errada | Alta | [x] envelhecida | 2026-08-10 |
| [CORR-WTE-038](/docs/tasks/CORR-WTE-038.md) | [WTE-TASK-17](/docs/tasks/17-transpilador-da-camada-de-dados.md) | O Log da WTE-TASK-17 diz 41 regras de substituição, e o gerador tem 47 | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-039](/docs/tasks/CORR-WTE-039.md) | [WTE-TASK-23](/docs/tasks/23-formato-da-spec.md) | O `GABARITO.md` diz que o gerador recusa `(int)*(int *)`, e ele aceita | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-040](/docs/tasks/CORR-WTE-040.md) | [WTE-TASK-23](/docs/tasks/23-formato-da-spec.md) | O `GABARITO.md` diz quatro famílias de `BitBtnNClick`, e o TSV tem três nomes | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-041](/docs/tasks/CORR-WTE-041.md) | [WTE-TASK-23](/docs/tasks/23-formato-da-spec.md) | Quatro das 15 rotas de recusa do `spec_index.py` não têm teste, e o README chama as onze testadas de "as" rotas | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-042](/docs/tasks/CORR-WTE-042.md) | [WTE-TASK-18](/docs/tasks/18-camada-de-dados-gerada.md) | O Log da WTE-TASK-18 diz que os testes do transpilador eram 33, e eram 38 | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-043](/docs/tasks/CORR-WTE-043.md) | [WTE-TASK-18](/docs/tasks/18-camada-de-dados-gerada.md) | `players[i].cost := Ord(buf1[0])` perde o sinal que o `char` do C++ tem | Baixa | [x] concluída | 2026-08-10 |

## Checklist

- [x] CORR-WTE-001 — sincronizar `status:` do frontmatter, e citá-lo no `01-executar.md`
- [x] CORR-WTE-002 — escrever no `ambiente.md` como remedir os dois números derivados
- [x] CORR-WTE-003 — ancorar `lib/` e `backup/` no `wte/`, onde a seção diz que valem
- [x] CORR-WTE-004 — blob ausente vira aviso; blob divergente continua falha
- [x] CORR-WTE-005 — versionar os streams sintéticos do `dfm_extract.py`
- [x] CORR-WTE-006 — propagar dono e contagem medidos para as tasks 25, 28, 30, o plano §5.1 e o prompt de revisão
- [x] CORR-WTE-007 — corrigir a atribuição e completar a tabela de envelhecimento, no gerador
- [x] CORR-WTE-008 — versionar a conferência do decodificador x86 contra o `objdump`
- [x] CORR-WTE-009 — dizer na §8.8 que as mensagens decepadas têm cópia dentro do próprio `.exe`
- [x] CORR-WTE-010 — corrigir lado e ASCII na §8.7 do plano e no enunciado da 06
- [x] CORR-WTE-011 — dizer a regra de aborto que existe, avisar no outro sentido, fixar em teste
- [x] CORR-WTE-012 — corrigir a §1.6 e dar dono ao número de imports da §1.2
- [x] CORR-WTE-013 — cobrir a segunda cópia do decodificador e fixar a identidade entre elas
- [x] CORR-WTE-014 — dar dono ao número de bitmaps e fechar o buraco do quadro da 09
- [x] CORR-WTE-015 — colar da saída as duas evidências transcritas à mão
- [x] CORR-WTE-016 — alargar o perímetro da varredura para `wte/` e fechar o sítio do `wte/README.md`
- [x] CORR-WTE-017 — cortar por faixa de endereço, e fazer a igualdade da §3 abortar
- [x] CORR-WTE-018 — trocar os três números aposentados do `02-revisar.md` e decidir o perímetro de `docs/prompts/`
- [x] CORR-WTE-019 — levar a exceção dos 118 blobs ao plano §2, ao `.gitignore` e ao `progresso.md`
- [x] CORR-WTE-020 — `check_lcl_props.py` remede a tabela contra a LCL instalada, e o `LCL_VERSAO` passa a pinar
- [x] CORR-WTE-021 — apontar o critério dos blobs para a WTE-TASK-12 e acrescentá-lo lá
- [x] CORR-WTE-022 — começar a faixa do `sed` em `401a22`, e dizer por que ela não é a da chamada
- [x] CORR-WTE-023 — colar da saída as três medidas do critério de build da WTE-TASK-11
- [x] CORR-WTE-024 — levar o sufixo ` [Lazarus]` à 35 e o `--show` à 12 e à 25
- [x] CORR-WTE-025 — corrigir a faixa para `11796..26527` nos três sítios, dizendo a base
- [x] CORR-WTE-026 — dizer, por coluna, o que foi medido no achado 2 e dar rota à divergência de `ComboBox.Text`
- [x] CORR-WTE-027 — trocar os seis `/docs/` do `montar()` por `../../docs/`, como o `fase-1.md` já faz
- [x] CORR-WTE-028 — guardar o grupo 3 (veredito) e transformar a coluna `Original` em contagem medida
- [x] CORR-WTE-029 — dizer no Log que a reconciliação entrou no mesmo commit, e por quê
- [x] CORR-WTE-030 — contar 40 `strcpy` no `Database.cpp` e mandar a regra de cópia casar `std::strcpy`
- [x] CORR-WTE-031 — reescrever o `wte/tests/README.md` para a pasta que existe hoje
- [x] CORR-WTE-032 — tirar `LongInt` da lista de proibidos e escrever a exceção de `SizeInt` onde ela é enunciada
- [x] CORR-WTE-034 — remedir a entrada do transpilador com os cabeçalhos, e dar destino ao `Team.hpp`
- [x] CORR-WTE-035 — nomear o teste da decisão 5, em bytes: 1.911 `#10`, sem `#13` e sem BOM
- [x] CORR-WTE-036 — ancorar a regra `!` → `not` na linha, e fazer o guard de quebra valer para `\s`, `[\s\S]` e `.`
- [x] CORR-WTE-037 — **envelhecida**: o `7b642f7` fechou as 498 recusas e mudou a varredura da saída para reportar coordenadas do `.pas`; o invariante de numeração veio pela CORR-WTE-036
- [x] CORR-WTE-038 — trocar 41 por 47 no Log da 17 e desfazer a contradição sobre a CORR-WTE-034
- [x] CORR-WTE-039 — implementar a marca de cast do Ghidra no `spec_index.py`, com teste de falso positivo
- [x] CORR-WTE-040 — medir as famílias de `BitBtnNClick` no `published_methods.tsv` e reescrever a frase
- [x] CORR-WTE-041 — testar as quatro rotas de recusa sem cobertura e contar `raise SpecError` no README
- [x] CORR-WTE-042 — trocar 33 por 38 no Log da 18, com o `git show` que remede
- [x] CORR-WTE-043 — estender o sinal ao converter `AnsiChar` para campo inteiro largo, e testar os dois sentidos

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

### CORR-WTE-010

- **Arquivo com problema:** `docs/PLAN-WTE-LAZARUS.md` (§8.7) e
  `docs/tasks/06-mapa-de-offsets.md` (enunciado, linha 45)
- **Sintoma:** a §8.7 diz que a tabela de `0x004231a0` "é **seguido** de dados
  que não são offsets" e cita `1869507948` como ASCII `l,km`. Medido: esse dword
  está em `0x00423190`, **16 bytes abaixo** da tabela, e é `lmno`. Quem obriga a
  medir é o limite *inferior*; o superior fecha por conteúdo e por referência,
  que concordam. A §8.7 é o que o executor da WTE-TASK-19 lê antes de mexer em
  offset
- **Como foi detectado:** leitura do dword em `0x00423190` pelo leitor de PE do
  `dump_offsets.py` (`= 1869507948 = b'lmno'`), confrontada com o texto da §8.7
- **Fix:** manter a armadilha e trocar a evidência de lado nos dois arquivos; o
  título "O 32º byte da tabela não é offset" também não descreve o medido — são
  72 bytes com 7 buracos internos

### CORR-WTE-011

- **Arquivo com problema:** `wte/tools/dump_offsets.py` —
  `check_table_bounds()` e o texto de `render_md()` (a saída `wte/re/offsets.md`
  é gerada)
- **Sintoma:** o `offsets.md` promete que "o script aborta se os dois limites não
  coincidirem". Ele aborta só quando o código referencia endereço **antes** do
  fim medido pelo conteúdo; no sentido oposto marca `agrees=False` e segue em
  silêncio. E a janela de plausibilidade é o `[min, max]` dos 69 valores do
  nosso `Offsets.hpp`, o que torna tautológica a guarda "o filtro aceita 100% do
  que já se sabe" na parte de faixa — e acopla o limite medido da tabela do
  Obocaman a um arquivo que a WTE-TASK-19 vai mexer
- **Como foi detectado:** três faltas plantadas em memória — referência dentro
  da tabela (aborta), referências removidas para o fim ficar antes da próxima
  (não aborta, `agrees=False`), e `OFS_PLANTADO = 999999999` no header, que
  alargou a faixa e empurrou o fim da tabela de `0x4231e8` para `0x4231ec`
- **Fix:** no gerador — dizer a regra que existe, emitir aviso no sentido que
  não aborta, escrever a acoplagem com o `Offsets.hpp`, e fixar os três casos
  num `wte/tools/test_dump_offsets.py`, no molde do `test_dump_strings.py`

### CORR-WTE-012

- **Arquivo com problema:** `docs/PLAN-WTE-LAZARUS.md` (§1.2 linha 117, §1.6
  linha 251) e `docs/tasks/09-fechamento-fase-1.md` (quadro de reconciliação)
- **Sintoma:** a §1.2 diz "322 imports, sendo **300** de `rtl60.bpl`/`vcl60.bpl`"
  — são **267** (103 + 164), e o número não está no quadro que a WTE-TASK-09
  remede, então não tem dono. A §1.6 chama o `TBrowseURL` de "componente de
  terceiro", enquanto a §5 do mesmo arquivo, já corrigida pela WTE-TASK-07, diz
  que é ação padrão da VCL (`Extactns`) — o plano se contradiz internamente
- **Como foi detectado:** `objdump -x` contando imports por DLL (KERNEL32 51,
  USER32 3, OLEAUT32 1, rtl60 103, vcl60 164, total 322), confrontado com a
  §1.2; e `grep -n "TBrowseURL" docs/PLAN-WTE-LAZARUS.md`, que devolve as duas
  passagens discordantes
- **Fix:** corrigir a frase da §1.6 e acrescentar a linha dos imports ao quadro
  da WTE-TASK-09, apontando para `dump_units.py` — que é quem mede e já publica
  o valor certo

### CORR-WTE-013

- **Arquivo com problema:** `wte/tools/dump_units.py` (cópia de `_fill`,
  `decode`, `extent`) e `wte/tools/test_dump_strings.py` (que só alcança o
  original)
- **Sintoma:** as três funções são byte a byte idênticas às do
  `dump_strings.py`, e a CORR-WTE-008 fixou em teste apenas as do
  `dump_strings.py`. Divergência entre as cópias passa com a bateria verde — e é
  a cópia do `dump_units.py` que delimita os 96 corpos de handler, fronteira de
  que depende o veredito "a chamada do `Comobj` está fora de todo handler"
- **Como foi detectado:** hash do texto-fonte das três funções nos dois
  arquivos (iguais), mais `grep "^import dump" wte/tools/test_dump_strings.py`,
  que devolve só `dump_strings`
- **Fix:** parametrizar a tabela de comprimento sobre os dois módulos e
  acrescentar um teste de identidade entre as cópias, que falhe nomeando a que
  divergiu. A decisão de cada gerador rodar sozinho não é reaberta

### CORR-WTE-014

- **Arquivo com problema:** `docs/tasks/09-fechamento-fase-1.md` (quadro de
  reconciliação) e `docs/prompts/01-executar.md`
- **Sintoma:** a WTE-TASK-08 mediu 198 bitmaps, registrou que a §1.8 do plano
  erra a soma na prosa ("197") e encaminhou para a WTE-TASK-09 — mas o quadro que
  a 09 executa não tem linha de assets. É a segunda vez que isso acontece: a
  CORR-WTE-012 acrescentou a linha dos imports pela mesma razão. O número errado
  está em nove lugares, dois deles no plano e dois em tarefas da fase 7 ainda por
  executar
- **Como foi detectado:** `find we-team-editor -iname '*.bmp' | wc -l` = 198,
  contra as cinco linhas da §1.8 que somam 198 e a prosa que diz 197;
  `grep -rn "197" docs/` lista os nove sítios; o quadro da 09 lido em seguida
- **Fix:** acrescentar a linha dos bitmaps ao quadro da 09 (a rota é comando
  inline, não gerador — a WTE-TASK-08 decidiu assim), mandar a 09 varrer os
  sítios além da §1, e pôr no `01-executar.md` a regra que impede a terceira
  ocorrência

### CORR-WTE-015

- **Arquivo com problema:** `wte/re/assets.md`, §6.1 e §8.1
- **Sintoma:** duas evidências transcritas à mão não batem com a medida. §6.1
  diz que "os outros 195 mantêm o `mtime` de 2006" — são 176 de 2002 e 19 de
  2006. §8.1 rotula o `fread` do molde de memory card como `0x0040f80c`, onde
  está um `push 0x1`; a chamada é em `0x0040f81a`. Nenhuma conclusão muda
- **Como foi detectado:** `find … -printf '%TY\n' | sort | uniq -c` para o ano,
  e o próprio comando `objdump` que o `.md` traz ao lado do bloco. Os demais
  números do arquivo foram rodados verbatim nesta revisão e reproduzem
- **Fix:** colar da saída as duas linhas, e acrescentar ao `.md` o comando da
  quebra por ano. A rota inline da WTE-TASK-08 não é reaberta — o que a correção
  fixa é que evidência transcrita tem de vir colada

### CORR-WTE-016

- **Arquivo com problema:** `wte/tools/check_fase1.py` (`_markdowns()`), com o
  sítio vivo em `wte/README.md:95`
- **Sintoma:** a guarda de número velho enumera só `docs/` e `wte/re/`, que é o
  que o enunciado da 09 pediu — e ali ela fecha em zero, remedido. Fora dali, o
  `wte/README.md` continua afirmando "A §1 do plano registra 197 `.bmp`" (a §1
  registra 198 desde a 09), atribuindo a diferença ao `careto_base.bmp` (era erro
  de soma na prosa, não de inventário) e encaminhando a reconciliação para a
  WTE-TASK-08 e a 09, ambas concluídas. Quatro linhas acima, no mesmo arquivo, o
  alvo `assets` já diz 198
- **Como foi detectado:** `grep -n '197' wte/README.md` com o
  `check_fase1.py --check` verde ao lado; o "18 → 0" da §6 foi remedido
  reextraindo a árvore anterior (`git archive 65cc4be docs wte/re`) e rodando o
  `varrer()` atual sobre ela — devolve 8/4/2/4, batendo com a tabela `SITIOS`
- **Fix:** `rglob` sobre `wte` inteiro (que já cobre `wte/re/`), `wte/tools/README.md`
  para `NARRACAO` (cita `430` para explicar o corte por contexto), dois testes de
  perímetro, e o bloco do `wte/README.md` reescrito como história com destino

### CORR-WTE-017

- **Arquivo com problema:** `wte/tools/check_fase1.py:363-367`, publicado na §3
  do `wte/re/fase-1.md`
- **Sintoma:** a partição "16 na tabela × 3 imediato de `.text`" sai de
  `"0x0042" not in r["va"]` — teste de faixa de endereço escrito como teste de
  substring. `.text` vai até `0x00423000`, então qualquer imediato em
  `0x00422000..0x00422fff` casaria o prefixo e seria contado como morando numa
  tabela de `.data`. Hoje acerta por coincidência de dígito. E a igualdade que a
  prosa afirma logo abaixo — "os outros são exatamente os slots preenchidos",
  `19 − 3 = 16` — não é asserção nenhuma no script
- **Como foi detectado:** cabeçalho de seção do `.exe` lido em Python
  (`.text VA 0x00401000..0x00423000`, `.data VA 0x00423000..`) confrontado com a
  coluna `va` dos 19 `confirmado` do `offsets.tsv`
- **Fix:** comparar `int(a, 16) >= DATA_VA` em vez de substring, levantar
  `CheckError` quando `confirmados − fora_da_tabela ≠ slots_com_nome`, e plantar
  um `va = 0x00422abc` no teste para exercitar a guarda

### CORR-WTE-018

- **Arquivo com problema:** `docs/prompts/02-revisar.md` (linha 88), com a
  decisão de perímetro em `wte/tools/check_fase1.py`
- **Sintoma:** a linha promete "o que já está no plano" e lista sete contagens;
  três estão aposentadas desde a WTE-TASK-09 — componentes `~430` (são 441),
  strings com enchimento `70` (são 13) e bitmaps `197` (são 198). Quem revisa lê
  o número como referência e reprova task correta, que é o modo de falha que a
  CORR-WTE-006 já registrou neste mesmo arquivo
- **Como foi detectado:** `sed -n '86,88p' docs/prompts/02-revisar.md`
  confrontado com a §5 do `wte/re/fase-1.md`, com o `check_fase1.py --check`
  verde ao lado — `docs/prompts/` está fora do perímetro por decisão
- **Fix:** trocar a lista por ponteiro para a §5 gerada, citando os três velhos
  ao lado dos novos como história; e decidir se `docs/prompts/` entra no
  perímetro (a exclusão foi escrita para **destino de link** placeholder, não
  para número de referência). Se entrar, a coluna `antes` de `SITIOS` é remedida
  de novo

### CORR-WTE-019

- **Arquivo com problema:** `docs/PLAN-WTE-LAZARUS.md` §2, `.gitignore` (bloco
  `wte/re/dfm/blobs/`) e `docs/tasks/progresso.md` ("Pendências externas")
- **Sintoma:** os 118 blobs do Obocaman — 816.880 bytes — foram versionados em
  hex inline nos 18 `wte/forms/*.lfm`, por **decisão do usuário registrada** em
  `wte/re/dfm/README.md`. A decisão está certa e não muda. O que não aconteceu
  foi o registro chegar aos três documentos que declaram a política: o plano
  (fonte de verdade) continua dizendo "binário de terceiro sem fonte e sem
  licença não entra no repositório", o `.gitignore` continua afirmando que "hex
  inline seria a mesma coisa numa codificação diferente", e o `progresso.md`
  continua listando os assets como não redistribuídos, sem ressalva. Nenhum dos
  três aponta para o README que os reverte
- **Como foi detectado:** `git ls-files wte/forms/*.lfm` (18 rastreados,
  1.960.767 B, dos quais 1.818.756 B — 92,8% — são linhas de hex) confrontado
  com `sed -n '339,343p' docs/PLAN-WTE-LAZARUS.md`, `sed -n '89,97p'
  .gitignore` e `sed -n '305,306p' docs/tasks/progresso.md`
- **Fix:** acrescentar a exceção com o número e o ponteiro nos três, sem mexer
  em nenhum `.lfm`

### CORR-WTE-020

- **Arquivo com problema:** `wte/tools/dfm2lfm.py` (cabeçalho, `ACEITA`,
  `DESCARTA`, `LCL_VERSAO` na linha 159)
- **Sintoma:** o cabeçalho afirma que a tabela "não é palpite: saiu das fontes
  da LCL 3.0 [...] varrendo as seções `published`". A varredura foi descartável:
  nada em `make -C wte check` toca `/usr/lib/lazarus`, nenhum dos 64 testes
  menciona a LCL, e `LCL_VERSAO = "3.0"` — o pino de versão — nunca é lido.
  Entrada errada em `ACEITA` sai verbatim para o `.lfm`, o `--check` fica verde
  (compara a saída consigo mesma), o `lazbuild` compila, e a janela explode ao
  abrir
- **Como foi detectado:** `grep -rn LCL_VERSAO wte/` devolve só a declaração;
  a remedição desta revisão varreu as seções `published` da LCL 3.0 subindo a
  cadeia de ancestrais e achou **zero** divergência além das oito `Left`/`Top`
  que o cabeçalho já justifica — a tabela está certa, e essa certeza não é
  reproduzível por comando versionado nenhum
- **Fix:** `wte/tools/check_lcl_props.py`, com `--check`, na bateria do
  `wte/Makefile`, exercitado com entrada plantada nos três sentidos (`ACEITA`
  inventada, `DESCARTA` que existe, `LCL_VERSAO` divergindo do disco)

### CORR-WTE-021

- **Arquivo com problema:** `docs/tasks/10-conversor-dfm-para-lfm.md` (critério
  dos blobs) e `docs/tasks/12-comparacao-visual.md`
- **Sintoma:** o único critério aberto da WTE-TASK-10 adia "blobs visíveis na
  janela" para a WTE-TASK-11, que está concluída e nunca teve o item — "blob",
  "bitmap" e "visível" não ocorrem no arquivo dela. O dono real é a
  WTE-TASK-12, que já tem "bitmap não aparece" na tabela de achados e não sabe
  que herdou critério de fora
- **Como foi detectado:** `grep -n -i "blob\|bitmap\|visív" docs/tasks/11-*.md`
  sem saída, contra `grep -n "bitmap" docs/tasks/12-*.md:48`. A metade
  "preservados" foi remedida e passa: 118 blobs conferidos contra o SHA-256 do
  `.dfm` **e** contra `wte/re/dfm/blobs/*.bin`, zero divergentes
- **Fix:** apontar o adiamento para a WTE-TASK-12 e acrescentar o critério
  herdado lá

### CORR-WTE-022

- **Arquivo com problema:** `wte/src/wtemain.pas` (cabeçalho, linhas 21-22) e
  `docs/tasks/11-app-com-a-casca-completa.md` (Log, linhas 115-118) — o mesmo
  comando nos dois
- **Sintoma:** a receita publicada de "reproduzir a medida" da ordem de
  auto-create devolve **17** classes, não 18, e a que falta é `TMainForm`. A
  faixa do `sed` começa em `0x401a2e`, que é a **chamada** do primeiro
  `CreateForm`; os dois `mov` que carregam os operandos daquele sítio estão em
  `0x401a22`/`0x401a28`, antes dela. A ordem escrita em `CriaFormularios` está
  certa — as 17 são exatamente os itens 2 a 18 —, o que não reproduz é a receita
- **Como foi detectado:** rodando o comando do Log verbatim (17 pares de `edx`)
  e resolvendo cada endereço pelo `vmtClassName` (`-44`); `ds:0x427d88`, o sítio
  cortado, resolve para `TMainForm`. Com a faixa em `/401a22:/,/401bc6:/` saem
  18. A contagem de chamadas que a prosa afirma confere: `grep -c 'call
  0x4226c0'` na faixa original dá 18
- **Fix:** faixa a partir de `401a22` nos dois arquivos, com a linha que explica
  por que o endereço da faixa não é o da chamada

### CORR-WTE-023

- **Arquivo com problema:** `docs/tasks/11-app-com-a-casca-completa.md`,
  critério de conclusão 1
- **Sintoma:** "2.482 linhas, 0 warning, 2 hints (ambos do Lazarus sobre
  diretório de pacote do sistema)". São **2.562** linhas; e os 2 hints que o
  contador `(1022)` soma são do FPC — `11030`/`11031`, abrir e fechar
  `/etc/fpc.cfg`. Os hints do Lazarus sobre diretório de pacote existem, mas são
  **sete** e não entram nessa conta. "0 warning" está certo
- **Como foi detectado:** `rm -rf wte/build && lazbuild wte/wte.lpi` e
  `lazbuild -B` dão 2.562 nos dois modos; e compilar o **próprio commit
  `af424c0`** num worktree separado dá 2.562 também, o que descarta deriva —
  `git log af424c0..HEAD -- wte/src wte/wte.lpr wte/wte.lpi wte/forms` é vazio.
  Os hints saem de `lazbuild -B 2>&1 | grep -E '^Hint'`
- **Fix:** colar as três medidas da saída, dizendo qual contador é de quem
- **Escrito no critério: 2.567.** As 2.562 acima valiam quando esta correção
  foi aberta; a [CORR-WTE-022](/docs/tasks/CORR-WTE-022.md), executada no mesmo
  lote e antes desta, acrescentou 5 linhas ao cabeçalho de `wtemain.pas` —
  comentário conta em `lines compiled`

### CORR-WTE-024

- **Arquivo com problema:** `docs/tasks/35-divergencias-deliberadas.md`,
  `docs/tasks/12-comparacao-visual.md` e `docs/tasks/25-handlers-de-carga.md`
- **Sintoma:** a WTE-TASK-11 delegou duas coisas e nenhum destinatário foi
  avisado. O sufixo ` [Lazarus]` no `Caption` dos 18 — mandado explicitamente
  para a WTE-TASK-35 pelo Log e pelo comentário de `MarcaOsTitulos` — não está
  entre as quatro candidatas da 35, e é a **única** divergência do projeto que já
  está no código rodando. E o andaime `--show`, feito para a captura da
  WTE-TASK-12, não é citado por ela: o método diz "mesmo formulário, mesma
  captura" num app que não navega. Ninguém é dono de remover o andaime quando a
  navegação chegar (WTE-TASK-25)
- **Como foi detectado:** `grep -rn "Lazarus\]" docs/ --include='*.md'` e
  `grep -rn -- "--show" docs/` só acham `11-app-com-a-casca-completa.md`. O
  `--show all` foi exercitado no `:99` nesta revisão e funciona: 18 janelas
  visíveis, zero depois do `kill`
- **Fix:** entrada na 35 com os seis campos que a tabela dela exige; passo 2 do
  método da 12 dizendo que se abre com `--show`; e uma linha na 25 dando dono à
  remoção do andaime

### CORR-WTE-025

- **Arquivo com problema:** `wte/re/visual.md:98`,
  `docs/tasks/12-comparacao-visual.md:151` e
  `docs/tasks/22-harness-golden.md:100,145`
- **Sintoma:** o achado 2 da WTE-TASK-12 registra a gravação do aviso de tamanho
  na faixa `11797..26528`. Esses são os índices **1-based do `cmp -l`**, não
  offsets; os offsets são `11796..26527`. A contagem (11.952) e os setores (5 a
  11) estão certos. O critério da linha 145 da WTE-TASK-22 manda essa faixa
  **virar exceção declarada** no gate golden, e a convenção do repositório é
  offset 0-based (`tools/golden_check.sh:84-85`, `405724` =
  `OFS_SQUAD_NUMBERS_NATIONAL + 1008`). Implementada como está, a exceção
  mascara um byte que não diverge e acusa um que diverge
- **Como foi detectado:** reproduzido no `:99` sobre cópia recém-tirada de
  `roms/`: `cmp -l | wc -l` dá 11952 e primeiro/último `11797`/`26528`; a mesma
  comparação por índice 0-based dá `11796..26527`, mesmos setores
- **Fix:** faixa `11796..26527` nos três arquivos, **com a base dita** (offset
  0-based, inclusivo), e o critério da 22 apontando a convenção do
  `golden_check.sh` do `newWe2002`

### CORR-WTE-026

- **Arquivo com problema:** `wte/re/eventos.md`, achado 2 (tabela nas linhas
  89-96 e o item 2 de "O que a fase 4 leva daqui"), e o Log da
  `docs/tasks/13-trace-de-eventos.md`
- **Sintoma:** a tabela abre com "Medido no fonte da LCL 3.0 instalada" e tem
  três colunas. A coluna `LCL/GTK2 3.0` tem arquivo e rotina por linha, e a
  revisão reconferiu todas no disco; a coluna `VCL/Win32 (2002)` **não tem
  fonte nenhuma**, e a coluna `Diverge?` é a comparação das duas. A única
  divergência declarada (`ComboBox.Text := s`) vira instrução para os 12
  handlers de `OnChange` da fase 4, apoiada no lado não medido — o mesmo terreno
  em que a premissa original da task já se mostrou invertida
- **Como foi detectado:** as seis linhas do lado LCL foram remedidas
  (`ChangeLock` em `SetItemIndex`/`SetText`/`SetPosition`, `change-value` no
  `TScrollBar`, `TCustomEdit.TextChanged`); do lado VCL não há o que citar no
  repositório — o `vcl60.bpl` não é lido por nada
- **Fix:** rotular a coluna VCL como não medida, com a origem da afirmação, e
  dar rota de confirmação à divergência de `ComboBox.Text` (disassembly de um
  dos 12 handlers, ou observação do `wte.exe`, que é VCL rodando)

### CORR-WTE-027

- **Arquivo com problema:** `wte/tools/check_fase2.py`, o `montar()` (linha 274
  e a tabela de pendências, 430-440), e a saída dele, `wte/re/fase-2.md`
- **Sintoma:** seis links para `docs/` na forma `/docs/tasks/...`, que
  `.claude/rules/links.md` reserva a markdown **dentro** de `docs/`. O vizinho
  que o `fase-2.md` toma por modelo, o `fase-1.md`, usa `../../docs/`. O mesmo
  erro já foi cometido e corrigido no gerador irmão — ver o Log da
  [CORR-WTE-007](/docs/tasks/CORR-WTE-007.md)
- **Como foi detectado:** `grep -rnoE '\]\((/docs/[^)]*|[^)]*docs/[^)]*)\)'
  wte/re/*.md` — `fase-1.md:3` sai `../../docs/tasks/09-…`, `fase-2.md:3` sai
  `/docs/tasks/14-…`
- **Fix:** `../../docs/` nos seis links do `montar()` e regerar. `eventos.md`
  (186, 214) e `tipos.md` (10), escritos à mão, têm o mesmo defeito e cabem na
  mesma passada

### CORR-WTE-028

- **Arquivo com problema:** `wte/tools/check_fase2.py:216-241`,
  `conferir_vereditos()`
- **Sintoma:** o dicionário anunciado como veredito por formulário guarda
  `m.group(2)` — a coluna `Original` do `visual.md`, que vale `sim` ou `DFM` —,
  e descarta o veredito, que é o grupo 3. Não é falso-verde hoje, porque só
  `len()` é lido e a regex de três colunas já exige veredito não vazio; é dado
  morto errado, que vira falso-verde no dia em que alguém olhar o texto
- **Como foi detectado:** leitura da regex contra o cabeçalho real da tabela
  (`| Formulário | Original | Veredito |`); o teste que cobre a rota
  (`test_check_fase2.py:113-116`) só assere contagem, nunca o valor
- **Fix:** guardar o grupo 3, manter a coluna `Original` como contagem
  (`capturado / só DFM`) publicada no `fase-2.md` — vira número medido o item 3
  de "O que a fase 2 não prova" —, e um assert sobre o valor no teste

### CORR-WTE-029

- **Arquivo com problema:** `docs/tasks/16-gerador-de-tabelas.md`, o Log de
  Execução (Arquivos criados/modificados e o item 2 de Problemas encontrados)
- **Sintoma:** o Log afirma duas vezes que a mudança do `check_fase2.py` e do
  `wte/re/fase-2.md` saiu «em commit próprio (ver abaixo)». Não há esse commit:
  os dois arquivos entraram no `6dab6bb`, o commit da própria task, e o corpo
  dele diz explicitamente o contrário — separá-los deixaria um commit com
  `make -C wte check` vermelho. O «(ver abaixo)» também não tem destino
- **Como foi detectado:**
  `git log --oneline -- wte/tools/check_fase2.py wte/re/fase-2.md` devolve só
  `6dab6bb` e o `6848208` da WTE-TASK-14; `git show --stat 6dab6bb` lista os
  dois arquivos entre os dez do commit
- **Fix:** reescrever as duas afirmações para o que o commit registra,
  preservando a razão da escolha, e remover o «(ver abaixo)». Nenhum código
  muda — a decisão está certa, o desatualizado é o Log

### CORR-WTE-031

- **Arquivo com problema:** `wte/tests/README.md`
- **Sintoma:** o README continua com o texto da fase 0 — «Vazio na fase 0. O
  primeiro conteúdo real é da WTE-TASK-20» e «Esta pasta é só Pascal» —, e a
  WTE-TASK-16 pôs ali `test_offsets.pas` e `test_offsets.cpp`, este último em
  C++ por necessidade: a conferência só vale se cada lado vier de um compilador
  diferente. Falta ainda dizer que os dois são gerados e quem os compila
- **Como foi detectado:** `ls wte/tests` contra o `head -4` do próprio README;
  `head -1 wte/tests/test_offsets.cpp` traz a marca `GERADO por
  wte/tools/gen_tables_pas.py`
- **Fix:** reescrever a abertura para o inventário corrente (os dois dumpers
  gerados e o `roteiros/` da WTE-TASK-13), trocar «só Pascal» pela razão de a
  pasta ser bilíngue, nomear `make -C wte test` como quem constrói e compara, e
  manter a WTE-TASK-20 como o que ainda vai chegar

### CORR-WTE-030

- **Arquivo com problema:** `wte/re/tipos.md`
- **Sintoma:** a decisão 1 afirma "38 `strcpy` e 10 `strcat` em `Database.cpp`";
  o arquivo tem 40 `strcpy`. Os dois que faltam estão escritos `std::strcpy`,
  nas linhas 98 e 100, dentro de `CopyAllStarNames()` — que o `Load()` chama na
  linha 778. 38 é a contagem de dentro do corpo do `Load()`, não a do arquivo
- **Como foi detectado:** `grep -c strcpy src/core/Database.cpp` dá 40 contra
  `grep -o '[^:]strcpy' … | wc -l` = 38; a diferença é exatamente
  `grep -c 'std::strcpy'` = 2
- **Fix:** afirmar 40, dizer as duas grafias e onde cada grupo mora, e estender
  a exigência do gerador à grafia qualificada — uma substituição ancorada em
  `strcpy(` atravessa as duas de `CopyAllStarNames` sem tocá-las

### CORR-WTE-032

- **Arquivo com problema:** `wte/re/tipos.md`
- **Sintoma:** a "regra zero" (linha 23) lista `Integer`, `Cardinal`, `PtrInt`,
  `PtrUInt`, `NativeInt`, `SizeInt` **e `LongInt`** e conclui "Nenhum deles
  entra em campo de registro nem em variável que toque a imagem"; a tabela
  mapeia `int` → `LongInt` para os 30 atributos de `Player` (campos de registro
  gravados na imagem) e `std::size_t` → `SizeInt` na fronteira do `CdImage`. O
  resumo do fim do arquivo (linha 216) já lista só três proibidos
- **Como foi detectado:** `grep -n 'LongInt\|SizeInt' wte/re/tipos.md` põe as
  linhas 23, 30, 41, 46 e 216 lado a lado; a 25 proíbe o que a 41 prescreve
- **Fix:** separar "não são equivalentes" de "são proibidos" — deixar
  `Integer`/`Cardinal`/`PtrInt`/`PtrUInt`/`NativeInt` como proibidos, escrever a
  exceção de `SizeInt` na própria regra, e tirar `LongInt` da lista

### CORR-WTE-034

- **Arquivo com problema:** `wte/re/tipos.md`, e o `UNITS` do
  `wte/tools/port_database_pas.py`
- **Sintoma:** o parágrafo "Entrada real medida" lista cinco arquivos (2.147
  linhas, número que confere), mas a tabela mapeia campos declarados em
  `Player.hpp`, `Team.hpp`, `CdImage.hpp` e `Database.hpp`, nenhum na lista.
  O transpilador já commitado reincorporou cinco cabeçalhos por conta própria e
  deixou o `Team.hpp` de fora — justamente o que declara `Team`, `MlTeam` e
  `Formation`, usados como campo em `Database.hpp:44-48`. Junto: três linhas da
  tabela lideram com grafias (`std::uint8_t`, `std::uint16_t`, `std::int32_t`)
  que não ocorrem em nenhum ponto de `src/core/`
- **Como foi detectado:** `wc -l` dos cinco contra os cabeçalhos;
  `grep -n 'raw_formation\|flag_colours\|link\[46\]' Team.hpp`;
  `grep -rnoE '\b(std::)?u?int(8|16|32|64)_t\b' src/core` só devolve `uint32_t`
  (31×) e `int64_t` (1×)
- **Fix:** reescrever o inventário separando implementação de declaração,
  nomear `Team.hpp`, e dar a ele destino escrito no `UNITS` ou recusa em
  `wte/re/recusas.md`; nas três linhas, deixar a grafia que ocorre

### CORR-WTE-035

- **Arquivo com problema:** `wte/re/tipos.md`
- **Sintoma:** cinco decisões, quatro blocos "Teste que prova" — a decisão 5 (o
  sidecar `_url.txt` por `TFileStream` com `#10`) não tem o seu, e o critério
  "Cada decisão com o teste que a prova nomeado" está marcado como cumprido
- **Como foi detectado:** `grep -c '^## Decisão' wte/re/tipos.md` = 5 contra
  `grep -c 'Teste que prova'` = 4
- **Fix:** acrescentar o bloco à decisão 5, em bytes e não em linhas — 1.911
  `#10`, nenhum `#13`, nenhum BOM, e `cmp` contra o sidecar que o
  `we2002_core` grava para a mesma base

### CORR-WTE-036

- **Arquivo com problema:** `wte/tools/port_database_pas.py`, regra 7 do `SUBS`
- **Sintoma:** `!\s*(?=\w|\()` → `not ` atravessa a quebra de linha. Nos seis
  sítios do `Database.cpp` a linha que termina em `!` é comentário `//`, e o
  statement de baixo entra dentro dele — inclusive dois
  `image_file.Seek(OFS_KIT_PREVIEW)`, que em Pascal desapareceriam. O
  `check_seeks()` não vê (o texto continua tendo `Seek`, só que comentado) e o
  guard de quebra de linha só reconhece a forma `[^x]`
- **Como foi detectado:** aplicar o `SUBS` em ordem sobre `Database.cpp` — a
  regra 7 leva o arquivo de 1.704 para 1.698 linhas; os seis sítios e o que cada
  um engole saem do `re.finditer` do padrão com `\n` no casamento
- **Fix:** ancorar na linha (`!(?=[^\S\n]*[\w(])`), alargar o teste de quebra
  para `\s`, `[\s\S]` e `.` sob `DOTALL`, e fixar o invariante de contagem de
  linhas sobre as seis unidades reais

### CORR-WTE-037

- **Arquivo com problema:** `wte/tools/port_database_pas.py` (o relatório de
  recusa) e a saída dele, `wte/re/transpilador.md`
- **Sintoma:** 493 das 498 recusas vêm da varredura do texto **traduzido** e
  publicam a linha dele como se fosse a do fonte. `Database.cpp` sai da tradução
  com 6 linhas a menos, então a tabela publica `Database.cpp:1256` para o
  `[[fallthrough]]` que está em `1258` — a linha 1256 do fonte é `case 52:`. As
  duas varreduras também listam o mesmo sítio como dois itens, sem dizer que uma
  é da entrada e a outra da saída
- **Como foi detectado:** `len(aplicar_subs(Database.cpp).splitlines())` = 1.698
  contra 1.704 da entrada, confrontado com as duas linhas de `fallthrough` da
  tabela do `--check`; e `test_a_linha_reportada_e_a_real`, que exercita só o
  caminho da entrada
- **Fix:** invariante de numeração em `aplicar_subs` (ou mapa de volta para a
  linha do fonte), rótulo de entrada/saída por recusa, e o teste da linha real
  cobrindo o caminho da saída

### CORR-WTE-038

- **Arquivo com problema:** `docs/tasks/17-transpilador-da-camada-de-dados.md`
  (Log de Execução e a nota do enunciado)
- **Sintoma:** o Log diz "tabela de substituição (**41** regras)" na mesma frase
  em que afirma "nenhum número digitado à mão"; são **47**, e o
  `transpilador.md` gerado já dizia 47 no mesmo commit (`8ae9170`). E a nota do
  enunciado encaminha a reconciliação do `tipos.md` como trabalho da
  CORR-WTE-034, enquanto o item 4 dos "Problemas encontrados" do mesmo arquivo
  registra que ela foi feita em 2026-08-10
- **Como foi detectado:** `len(SUBS)` = 47 por leitura do AST, contra
  `grep 'regras, aplicadas'` nos dois arquivos; `git show 8ae9170` mostra que a
  divergência nasceu com eles. Os demais números do Log (38 testes, 498 recusas
  em 13 motivos, 2.504 linhas) foram remedidos e batem
- **Fix:** 47 no Log, com a rota de remedição ao lado, e a nota do enunciado
  reescrita para o estado corrente

### CORR-WTE-039

- **Arquivo com problema:** `wte/re/spec/GABARITO.md` (linha 133) e
  `wte/tools/spec_index.py` (`MARCAS_DE_DECOMPILADO`)
- **Sintoma:** o gabarito lista nove marcas de decompilado que o gerador
  "recusa"; a tupla do gerador tem sete padrões e não cobre `(int)*(int *)`, a
  marca que sobrevive a quem renomeia `uVar1` antes de colar
- **Como foi detectado:** as nove marcas plantadas contra
  `MARCAS_DE_DECOMPILADO`; sete recusadas, o cast aceito nas duas formas
  (`(param + 8)` e `(this + 8)`)
- **Fix:** implementar o padrão no gerador, com teste da recusa **e** teste de
  falso positivo em prosa portuguesa — ou tirar a marca do gabarito, uma coisa
  ou outra

### CORR-WTE-040

- **Arquivo com problema:** `wte/re/spec/GABARITO.md` (linhas 12-14)
- **Sintoma:** "quatro famílias de `BitBtnNClick`" na frase que justifica o
  nome `<formulario>.<handler>.md`; o TSV tem três nomes (`BitBtn1Click` ×4,
  `BitBtn3Click` ×3, `BitBtn2Click` ×2) e nenhum `BitBtn4Click`. Os outros dois
  números da mesma frase (16 `FormCreate`, 2 `FormShow`) batem
- **Como foi detectado:** `collections.Counter` sobre a coluna `handler` do
  `wte/re/published_methods.tsv`
- **Fix:** frase medida, nomeando as três famílias — e `SpeedButton1Click` ×3,
  se a intenção era contar botão repetido em geral

### CORR-WTE-041

- **Arquivo com problema:** `wte/tools/test_spec_index.py` e
  `wte/tools/README.md` (linha 49)
- **Sintoma:** "as onze rotas de recusa" são onze testes, mas o gerador tem 15
  sítios de `raise SpecError`; ficam sem regressão o TSV ausente, o TSV vazio,
  o frontmatter não fechado, a linha sem `:` e a chave obrigatória ausente — a
  última é a que a primeira spec de verdade vai encontrar
- **Como foi detectado:** `grep -c "raise SpecError"` = 15 contra os onze
  `test_recusa_*`; as rotas foram exercitadas à mão e funcionam, então é falta
  de teste, não bug
- **Fix:** testes para as rotas que faltam e, no README, o número atrelado ao
  `grep -c` para a próxima revisão poder remedir

### CORR-WTE-042

- **Arquivo com problema:** `docs/tasks/18-camada-de-dados-gerada.md` (Log de
  Execução, tabela de arquivos)
- **Sintoma:** "58 testes (eram 33)"; eram **38** no commit anterior à task
  (`d8af56a`) e 35 no commit que fechou a WTE-TASK-17. O próprio enunciado da 18
  diz 38 na linha 29, então o arquivo se contradiz
- **Como foi detectado:** `git show <commit>:wte/tools/test_port_database_pas.py
  | grep -cE '^[[:space:]]+def test_'` nos três commits; 58 no HEAD confere
- **Fix:** 38 no lugar de 33, com o comando de remedição ao lado. Irmão da
  CORR-WTE-038, que é o mesmo defeito no Log da WTE-TASK-17

### CORR-WTE-043

- **Arquivo com problema:** `wte/tools/port_database_pas.py` (tabela
  `CHAR_LOCAL` e a conversão que ela governa), saída em
  `wte/src/we2002_database.pas:962`
- **Sintoma:** `players[i].cost = buf1[0]` do C++ estende sinal (`0xC8` → -56,
  `char` do x86 com `int` de destino); o Pascal gerado emite `Ord(buf1[0])` e
  entrega 200. É a decisão 4 do `tipos.md` não aplicada à conversão
  local→campo largo
- **Como foi detectado:** varredura dos `:= Ord(` do `we2002_database.pas`
  cruzada com o tipo do campo de destino — 34 vão para `ShortInt`/`Byte` e
  coincidem, um vai para `LongInt` e diverge. As duas ROMs foram lidas
  (só leitura): 0 byte ≥ 128 nos 462 custos NC, máximo 36, então a divergência
  é **latente**
- **Fix:** conversão com sinal quando o destino é inteiro largo, `Ord` quando é
  `Byte`, teste nos dois sentidos e um caso em `test_camada_dados.pas`. O
  round-trip da WTE-TASK-20 não pegaria isto: o `Save` grava só o byte baixo e a
  imagem sai idêntica
