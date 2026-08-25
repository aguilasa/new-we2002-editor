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
| [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) | [WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) | O oráculo comportamental está morto e a fase 4 é circular: o gate 22 precisa do `wte.exe` vivo, e entendê-lo é a WTE-TASK-25, que depende do 22 | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-045](/docs/tasks/CORR-WTE-045.md) | [WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) | A seção das seis áreas do `offsets-novos.md` diz `roms/09-areas-com-time`, que é o nome da sessão — a imagem é `japanese-shift-jis.bin` | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-046](/docs/tasks/CORR-WTE-046.md) | [WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) | Três dos 14 vereditos `retomada de fronteira` provam com `case N`, e o `Database.cpp` tem `if(i == N)` — num deles o `case N` existe em outro bloco | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-047](/docs/tasks/CORR-WTE-047.md) | [WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) | As sessões 10 e 11, que deram 18 dos 33 endereçados, não têm o resultado da segunda régua (`cmp`) registrado em lugar nenhum | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-048](/docs/tasks/CORR-WTE-048.md) | [WTE-TASK-20](/docs/tasks/20-round-trip-headless.md) | O `fase-3.md` gerado ainda diz que o `wte.exe` não passa da tela de carga — o sweep da CORR-WTE-044 varreu quatro arquivos e não este | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-049](/docs/tasks/CORR-WTE-049.md) | [WTE-TASK-20](/docs/tasks/20-round-trip-headless.md) | O parágrafo de dependência da WTE-TASK-20 diz que os 36 restantes são "os que o `we2002_core` não tem", e os 50 `ausente` são todos do `Offsets.hpp`; e cita a 19 como bloqueada | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-050](/docs/tasks/CORR-WTE-050.md) | [WTE-TASK-21](/docs/tasks/21-fechamento-fase-3.md) | A razão entrada × saída divide as 3.692 linhas dos dois geradores pelas 2.504 de entrada de um só; as 852 do `gen_tables_pas` ficam fora do denominador | Alta | [x] concluída | 2026-08-10 |
| [CORR-WTE-051](/docs/tasks/CORR-WTE-051.md) | [WTE-TASK-21](/docs/tasks/21-fechamento-fase-3.md) | A fração de 92,5% subtrai 277 linhas úteis de um total de 3.692 que conta linha em branco — 26 linhas em branco de bloco manual entram como "por regra" | Baixa | [x] concluída | 2026-08-10 |
| [CORR-WTE-052](/docs/tasks/CORR-WTE-052.md) | [WTE-TASK-22](/docs/tasks/22-harness-golden.md) | O Log da WTE-TASK-22 diz 15 testes no `golden_veredito.py`, em dois sítios, e são 18 | Alta | [x] concluída | 2026-08-11 |
| [CORR-WTE-053](/docs/tasks/CORR-WTE-053.md) | [WTE-TASK-22](/docs/tasks/22-harness-golden.md) | A seção 2 descreve o controle como uma faixa de 11.952 bytes; o gate declara nove faixas e 11.955, e nenhum dos dois textos diz de qual imagem fala | Baixa | [x] concluída | 2026-08-11 |
| [CORR-WTE-054](/docs/tasks/CORR-WTE-054.md) | [WTE-TASK-24](/docs/tasks/24-ghidra-convencao-borland.md) | O `vmt.md` diz que todo número saiu do `vmt_probe.java`, e os votos da âncora (4 entre ~150) não têm ferramenta que os produza | Alta | [x] concluída | 2026-08-11 |
| [CORR-WTE-055](/docs/tasks/CORR-WTE-055.md) | [WTE-TASK-24](/docs/tasks/24-ghidra-convencao-borland.md) | A seção 4 do enunciado chama de 322 os imports de `rtl60`/`vcl60`; são 267, e o Log da própria task diz 267 | Baixa | [x] concluída | 2026-08-11 |
| [CORR-WTE-056](/docs/tasks/CORR-WTE-056.md) | [WTE-TASK-24](/docs/tasks/24-ghidra-convencao-borland.md) | O `borland_cc.md` e o `run_headless.sh` mandam rodar `apply_names.py`, e o script é `.java` | Baixa | [x] concluída | 2026-08-11 |
| [CORR-WTE-057](/docs/tasks/CORR-WTE-057.md) | [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) | A conferência de tela mede 3 dos 5 grupos de campo que o critério enumera: o recorte de 520×240 exclui os 23 números de camisa e a lista de jogadores, e o estado de habilitação nunca foi confrontado | Alta | [x] concluída | 2026-08-11 |
| [CORR-WTE-058](/docs/tasks/CORR-WTE-058.md) | [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) | O `visual.md` manda rodar o `capture_forms.sh`, removido nesta task, e a árvore do `progresso.md` não tem `src/impl/` nem as ferramentas novas | Baixa | [x] concluída | 2026-08-11 |
| [CORR-WTE-059](/docs/tasks/CORR-WTE-059.md) | [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) | A spec do `lista_equiposChange` justifica o `aberto` com "ainda não conferido contra a tela", e a seção seguinte é a conferência de tela | Baixa | [x] concluída | 2026-08-11 |
| [CORR-WTE-060](/docs/tasks/CORR-WTE-060.md) | [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) | O `iguala_nombres` não acinzenta no port — 0 px de mudança contra 518 do oráculo —, e o defeito atravessou duas tasks sendo encaminhado para uma correção que ninguém abriu | Alta | [x] concluída | 2026-08-18 |
| [CORR-WTE-061](/docs/tasks/CORR-WTE-061.md) | [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) | O `MaxLength` de `edit_nombre1` é o literal 5, lido da tela; qual campo do formato tem 10 bytes continua sem medir | Baixa | [x] concluída | 2026-08-18 |
| [CORR-WTE-062](/docs/tasks/CORR-WTE-062.md) | [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) | O `lista_formacionesClick` é do grupo `carga`, foi encaminhado para a 26 pelo efeito, e continua `REStub` com as duas tasks concluídas | Alta | [x] concluída | 2026-08-18 |
| [CORR-WTE-063](/docs/tasks/CORR-WTE-063.md) | [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) | As três carregadoras de bitmap da ficha não têm dono em nenhuma das 40 tasks, e a 32 não menciona cara, cabelo nem barba | Alta | [x] concluída | 2026-08-18 |
| [CORR-WTE-064](/docs/tasks/CORR-WTE-064.md) | [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) | O lote do `edit_nombre1` está provado e a travessia emulada dá 6 onde o oráculo corta em 5 | Média | [x] concluída | 2026-08-18 |
| [CORR-WTE-065](/docs/tasks/CORR-WTE-065.md) | [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md) | "o maior `b0` medido é 43" está em três sítios e a varredura das duas ROMs dá 111 e 116 | Alta | [x] concluída | 2026-08-19 |
| [CORR-WTE-066](/docs/tasks/CORR-WTE-066.md) | [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md) | A tabela de endereços atropelados lista o 462, que nunca é alcançado, e omite o `0x004335f4`, que é | Alta | [x] concluída | 2026-08-19 |
| [CORR-WTE-067](/docs/tasks/CORR-WTE-067.md) | [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md) | A nota nova da WTE-TASK-27 põe a `AtualizaBlocosLivresDeMl` no `we2002_ml` e promete um mapa de ocupação que a unidade não expõe | Baixa | [x] concluída | 2026-08-19 |
| [CORR-WTE-068](/docs/tasks/CORR-WTE-068.md) | [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) | Três specs de gravação ainda dizem que o gate passa "só as duas faixas do arranque"; medido hoje, os três dão byte-idêntico | Alta | [x] concluída | 2026-08-20 |
| [CORR-WTE-069](/docs/tasks/CORR-WTE-069.md) | [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) | As três funções novas do `we2002_ml` (`IndiceDoBlocoMl`, `ParDoIndiceLinearMl`, `PrimeiroBlocoLivreMl`) entraram no caminho de gravação sem um teste sequer | Baixa | [x] concluída | 2026-08-20 |
| [CORR-WTE-070](/docs/tasks/CORR-WTE-070.md) | [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) | A tabela "Arquivos a criar ou modificar" da 27 aponta para `wte/tools/roteiros/gravacao-*.sh`, que não existe | Baixa | [x] concluída | 2026-08-20 |
| [CORR-WTE-071](/docs/tasks/CORR-WTE-071.md) | [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md) | O mapa do `.mcr` afirma 16 destinos em cinco lugares; o `LAYOUT` do gerador tem 17, e o título gerado o diz logo acima da tabela com as 17 linhas | Alta | [x] concluída | 2026-08-20 |
| [CORR-WTE-072](/docs/tasks/CORR-WTE-072.md) | [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md) | O `gravacao-controle.md` fecha dizendo que o `boton_mcr2isoClick` escreve setor inteiro — premissa que a WTE-TASK-28 mediu e refutou, e que o próprio doc já desmente 30 linhas acima | Alta | [x] concluída | 2026-08-20 |
| [CORR-WTE-073](/docs/tasks/CORR-WTE-073.md) | [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md) | O `check_lcl_combo.py` ficou preso no `:99` em código vivo depois da mudança para o `:98`: pula em silêncio numa máquina só com o `:98` | Alta | [x] concluída | 2026-08-20 |
| [CORR-WTE-074](/docs/tasks/CORR-WTE-074.md) | [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md) | A confrontação Pascal × Python do leitor de `.mcr` aponta para `work/saida.mcr`, que o `golden_check.sh` apaga a cada corrida; a fixture estável tem outro nome | Baixa | [x] concluída | 2026-08-20 |
| [CORR-WTE-075](/docs/tasks/CORR-WTE-075.md) | [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md) | `do_roundtrip()` grava num destino fixo versionado, e o teste sobrescreve a medição de `wte/re/mcr-roundtrip.tsv` e a repõe num `finally` | Baixa | [x] concluída | 2026-08-20 |
| [CORR-WTE-076](/docs/tasks/CORR-WTE-076.md) | [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) | O plano e a task dizem que o `ficha_color` tem 758 linhas de DFM; o extrator versionado dá 866, e nunca deu 758 | Alta | [x] concluída | 2026-08-21 |
| [CORR-WTE-077](/docs/tasks/CORR-WTE-077.md) | [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) | A §5.3 do plano ainda descreve o render 2D como `TBitmap` + varredura de pixel, algoritmo que a WTE-TASK-29 mediu e refutou — é reescrita de paleta | Alta | [x] concluída | 2026-08-21 |
| [CORR-WTE-078](/docs/tasks/CORR-WTE-078.md) | [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) | O Log da sétima passagem conta 7 casos novos no `test_dump_zonas.py`; o commit acrescentou 9 | Baixa | [x] concluída | 2026-08-21 |
| [CORR-WTE-079](/docs/tasks/CORR-WTE-079.md) | [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) | O `compara_tela.sh` ficou com dois blocos de `--malha` mortos — um duplicado no `captura_oraculo` e um aninhado no ramo `cor|grade` do `captura_port`, com `continue` fora de laço | Baixa | [x] concluída | 2026-08-21 |
| [CORR-WTE-080](/docs/tasks/CORR-WTE-080.md) | [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) | O `golden-14-uniforme` falhou por espera de janela em 3 de 4 corridas do modo controle nesta revisão; a 4ª deu byte-idêntico | Alta | [x] concluída | 2026-08-21 |
| [CORR-WTE-081](/docs/tasks/CORR-WTE-081.md) | [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) | Três gravações na imagem sem dono — o `OK` do `ficha_color`, o `Comple.` do `jugador` e o ` Accept` do `estrategia`; a WTE-TASK-27 contava seis gravações e são nove | Alta | [x] concluída | 2026-08-21 |
| [CORR-WTE-082](/docs/tasks/CORR-WTE-082.md) | [CORR-WTE-081](/docs/tasks/CORR-WTE-081.md) | A tela de tática nunca é enchida — a `0x0040A0B4` (1.443 B) não tem port, e sem ela o ` Accept` do `estrategia` gravaria as coordenadas de tempo de projeto do `.lfm` | Alta | [x] concluída | 2026-08-21 |
| [CORR-WTE-083](/docs/tasks/CORR-WTE-083.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | Dez times desenham bandeira preta — os 8 CLASSIC e dois clubes de ML: o `ed.exe` não lê a paleta deles e o editor do Obocaman lê | Alta | [x] concluída | 2026-08-23 |
| [CORR-WTE-084](/docs/tasks/CORR-WTE-084.md) | [CORR-WTE-083](/docs/tasks/CORR-WTE-083.md) | O combo 85 (`ml_teams[22]`) diverge por POSIÇÃO depois de a paleta ser consertada — bandeira 2 px mais abaixo, e a barra `equipe` do oráculo em 76 px, fora da grade `11v+9` | Média | [x] concluída | 2026-08-23 |
| [CORR-WTE-085](/docs/tasks/CORR-WTE-085.md) | [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) | O plano e o `progresso.md` ainda dizem "duas das **seis** gravações" onde o `check_fase4.py` mede **dezessete**; o plano se contradiz a dezesseis linhas de distância | Alta | [x] concluída | 2026-08-23 |
| [CORR-WTE-086](/docs/tasks/CORR-WTE-086.md) | [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) | A WTE-TASK-30 dá o `pabajoClick` como dono da rota de vínculo do `ficha_enlaza`; nenhuma spec nem código liga os dois — quem abre o modal é o `mostrar_jugadorClick`, que segue `aberto` | Baixa | [x] concluída | 2026-08-23 |
| [CORR-WTE-087](/docs/tasks/CORR-WTE-087.md) | [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) | O Log da WTE-TASK-30 conta 12 `.inc` novos e 6 `.uses` tocados; o commit `fb640cd` tem 11 `.inc` novos e 5 `.uses` | Baixa | [x] concluída | 2026-08-23 |
| [CORR-WTE-088](/docs/tasks/CORR-WTE-088.md) | [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) | Nove comentários de ferramenta viva ainda descrevem o gate no `:99` depois da mudança para o `:98` — entre eles a lista de guardas do `golden_check.sh` | Baixa | [x] concluída | 2026-08-23 |
| [CORR-WTE-089](/docs/tasks/CORR-WTE-089.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | Três vereditos `aberto` por "nada exercita o corpo" quando a bateria golden já os exercita — o `lista_jugadores_1Change` dispara em quatro gates verdes | Alta | [x] concluída | 2026-08-24 |
| [CORR-WTE-090](/docs/tasks/CORR-WTE-090.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | Três vereditos `aberto` esperando decisão já tomada ou de outra fase; o `ComboBoxDrawItem` fechava o ciclo 31→37→34→31 | Alta | [x] concluída | 2026-08-24 |
| [CORR-WTE-091](/docs/tasks/CORR-WTE-091.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | O `Original ` da ficha não alcançava a `PreencheFicha` por ciclo de `uses`, e a régua dele precisa ser um par de roteiros que difere por um clique | Alta | [x] concluída | 2026-08-24 |
| [CORR-WTE-092](/docs/tasks/CORR-WTE-092.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | O ramo do reserva e o arrasto de bola não tinham estímulo; o harness não sabia produzir `mousedown` | Alta | [x] concluída | 2026-08-24 |
| [CORR-WTE-093](/docs/tasks/CORR-WTE-093.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | Os quatro laços do maior `FormCreate` não tinham leitura, e o dono do diálogo de textura (WTE-TASK-29) fechou sem ele | Alta | [x] concluída | 2026-08-24 |
| [CORR-WTE-094](/docs/tasks/CORR-WTE-094.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | A WTE-TASK-32 abre dizendo que o `ed.exe` não calcula preço; ele calcula, o que falta é o botão — e a fórmula dele já está transpilada nesta árvore | Média | [x] concluída | 2026-08-24 |
| [CORR-WTE-095](/docs/tasks/CORR-WTE-095.md) | [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) | O editor do Obocaman nunca preça o slot 22 e o `ed.exe` diz que ele tem preço; medido em seis times, e o `je` da terceira coluna já foi descartado como causa | Média | [x] concluída | 2026-08-24 |
| [CORR-WTE-096](/docs/tasks/CORR-WTE-096.md) | [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) | Chave duplicada no `GOLDEN_DE` do `check_fase4.py` apaga o gate do `base_teamClick`: o `fase-4.md` publica **nenhum** para o único escritor que tem golden verde | Alta | [x] concluída | 2026-08-24 |
| [CORR-WTE-097](/docs/tasks/CORR-WTE-097.md) | [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) | O cabeçalho do `base_teamClick.inc` diz "medido em dois times" onde a amostra final tem seis, e é ali que mora o `ULTIMO_SLOT_PRECADO` | Baixa | [x] concluída | 2026-08-24 |
| [CORR-WTE-098](/docs/tasks/CORR-WTE-098.md) | [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) | A §5.1 do plano ainda diz que o preço "não precisa de golden test de imagem" e nomeia só o `etiqprecioClick`; a outra metade grava e tem o `golden-22-precos` | Média | [x] concluída | 2026-08-24 |
| [CORR-WTE-099](/docs/tasks/CORR-WTE-099.md) | [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) | A lista de arquivos da WTE-TASK-32 não menciona as quinze linhas acrescentadas ao `.gitignore` | Baixa | [x] concluída | 2026-08-24 |
| [CORR-WTE-100](/docs/tasks/CORR-WTE-100.md) | [CORR-WTE-095](/docs/tasks/CORR-WTE-095.md) | A citação `` `{$Q-}` `` num comentário do `we2002_preco.pas` abre nível 2: é o único warning do build, e em `{$mode delphi}` seria erro fatal | Baixa | [x] concluída | 2026-08-24 |
| [CORR-WTE-101](/docs/tasks/CORR-WTE-101.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | O contrato da spec diz "seis seções obrigatórias" e a ferramenta cobra cinco; e a frase do `fase-4.md` apresenta as 481 linhas de evidência como se fossem todas, quando 44 outras ficam fora da conta | Média | [x] concluída | 2026-08-24 |
| [CORR-WTE-102](/docs/tasks/CORR-WTE-102.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | Quatro sítios vivos ainda derivam as dezessete gravações "das 94 specs"; o índice conta 96 desde que a WTE-TASK-32 escreveu as duas de preço | Média | [x] concluída | 2026-08-24 |
| [CORR-WTE-103](/docs/tasks/CORR-WTE-103.md) | [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | No estado zero o `check_fase4.py` emite o título `## Os que continuam aberto` colado no parágrafo — a linha em branco mora dentro do `if` que lista os sem spec | Baixa | [x] concluída | 2026-08-24 |
| [CORR-WTE-104](/docs/tasks/CORR-WTE-104.md) | [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md) | O `golden-24-gravacao-dupla` grava no time 2, cujos dois primeiros cobradores são iguais (`[7, 7, …]`): a troca do `Load`+`Save` que ele existe para medir é a identidade ali, e o roteiro passa com vaivém e sem ele | Alta | [x] concluída | 2026-08-25 |
| [CORR-WTE-105](/docs/tasks/CORR-WTE-105.md) | [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md) | A pendência do vaivém dos cobradores foi encaminhada por prosa da WTE-TASK-34 para a 35, e a 35 não a tem em lugar nenhum — zero ocorrências no arquivo dela | Baixa | [x] concluída | 2026-08-25 |
| [CORR-WTE-106](/docs/tasks/CORR-WTE-106.md) | [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) | O `check_divergencias.py` é a única guarda de recusa do repositório sem `test_*.py`; as "três recusas vistas" do critério não deixaram artefato — as quatro foram exercitadas nesta revisão e saem com código 2 | Média | [x] concluída | 2026-08-25 |
| [CORR-WTE-107](/docs/tasks/CORR-WTE-107.md) | [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) | A lista de arquivos da WTE-TASK-35 nomeia oito dos nove do commit; falta justamente o repasse escrito na WTE-TASK-36 | Baixa | [x] concluída | 2026-08-25 |
| [CORR-WTE-108](/docs/tasks/CORR-WTE-108.md) | [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) | A task deixa "o plano é o que falta conferir" sobre o vaivém, e o plano nunca afirmou aquilo — zero ocorrências de `idempot`/`cobrador`/`OFS_KICKER` | Baixa | [x] concluída | 2026-08-25 |
| [CORR-WTE-109](/docs/tasks/CORR-WTE-109.md) | [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) | Quatro sítios do lado WTE dizem que "o editor original não é idempotente", e neste projeto "o original" é o `wte.exe` — a medição da CORR-WTE-104 cobre um caminho e não a afirmação inteira | Média | [x] concluída | 2026-08-25 |
| [CORR-WTE-110](/docs/tasks/CORR-WTE-110.md) | [WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md) | Os quatro casos de borda foram medidos num vetor só (`names`, 20 B) e o critério diz "por campo"; `abbreviations` (4 B, a menor folga), `name` e `kanji_name` não passam pelos grupos 1 e 2 | Média | [x] concluída | 2026-08-25 |
| [CORR-WTE-111](/docs/tasks/CORR-WTE-111.md) | [WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md) | A chave `faixa` do `CAMPOS` não é lida por ninguém, e dois dos quatro valores contradizem o medido — `edit_nombre1` declara (5,19) contra 5..13 | Baixa | [x] concluída | 2026-08-25 |
| [CORR-WTE-112](/docs/tasks/CORR-WTE-112.md) | [WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md) | O `filtro` de caracteres é publicado por campo no `buffers.md` e nunca conferido contra o `KeyPress`, enquanto o `predicado` de faixa ao lado aborta se sumir | Baixa | [x] concluída | 2026-08-25 |
| [CORR-WTE-113](/docs/tasks/CORR-WTE-113.md) | [WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md) | `golden_suite.sh --roteiro` sem `--retomar` trunca o `golden.tsv` inteiro antes de qualquer corrida — 97 linhas viram 1, e foi assim que as 92 corridas da WTE-TASK-34 se perderam | Alta | [x] concluída | 2026-08-25 |
| [CORR-WTE-114](/docs/tasks/CORR-WTE-114.md) | [WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md) | As três divergências que a WTE-TASK-37 mediu foram parqueadas numa task já concluída; o `divergencias.md` não tem nenhuma, e uma delas se declara "ainda sem entrada aqui" | Média | [x] concluída | 2026-08-25 |
| [CORR-WTE-115](/docs/tasks/CORR-WTE-115.md) | [WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md) | O `check_carregado.py` aborta na moldura e não tem `test_*.py`, enquanto o `check_retorno.py`, nascido no mesmo commit, tem | Baixa | [ ] pendente | — |

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
- [x] CORR-WTE-044 — o controle **existe**; o ponteiro global é que é sobrescrito pela carga do time. Desfecho: condição de contorno — a ROM japonesa passa da troca de time com 0 violação de acesso
- [x] CORR-WTE-045 — tirar o nome da imagem da evidência em vez da constante da sessão, e regerar
- [x] CORR-WTE-046 — devolver a construção que casou (`case` ou `if`) junto do gatilho, e imprimir a que casou
- [x] CORR-WTE-047 — versionar o resultado do `cmp` por sessão e gerar o veredito das duas réguas no `offsets-novos.md`
- [x] CORR-WTE-048 — trocar a justificativa aposentada no `compare_dumps.py` (oráculo de comportamento × de formato) e regerar
- [x] CORR-WTE-049 — separar as duas populações de offset no enunciado da 20 e parar de afirmar status da 19
- [x] CORR-WTE-050 — parear entrada e saída por gerador na razão do fechamento da fase 3, e corrigir a §4.5
- [x] CORR-WTE-051 — contar a fração com a mesma régua nos dois lados da subtração, e dizer qual é
- [x] CORR-WTE-052 — trocar 15 por 18 nos dois sítios do Log da 22, com o `grep -c` que remede
- [x] CORR-WTE-053 — reescrever a seção 2 da 22 com as nove faixas, os 11.955 bytes e a imagem de cada medida
- [x] CORR-WTE-054 — pôr a votação da âncora no `vmt_probe.java`, ou dizer no `vmt.md` de onde os votos vieram
- [x] CORR-WTE-055 — trocar 322 por 267 na seção 4 da 24, dizendo que 322 é o total
- [x] CORR-WTE-056 — trocar `apply_names.py` por `.java` nos três sítios do procedimento do Ghidra
- [x] CORR-WTE-057 — levar o recorte da conferência de tela aos 23 dorsais, à lista de jogadores e ao estado de habilitação
- [x] CORR-WTE-058 — tirar do `visual.md` o comando que não existe mais, e pôr na árvore do `progresso.md` o que a 25 criou
- [x] CORR-WTE-059 — trocar a razão escrita do veredito `aberto` pela que sobrou
- [x] CORR-WTE-060 — medir por que o `iguala_nombres` não acinzenta, uma variável por vez
- [x] CORR-WTE-061 — descobrir o que é a coluna 0 da tabela de `0x00433a10` e tirar o literal do port
- [x] CORR-WTE-062 — portar o `lista_formacionesClick` e rever os três vereditos que dependem dele
- [x] CORR-WTE-063 — dar dono a cara, cabelo e barba: estender a 29 ou registrar na 35
- [x] CORR-WTE-064 — fechar a conta do `[0x00433a10]`, que dá um a mais que a tela
- [x] CORR-WTE-065 — medir o maior `b0` em vez de afirmá-lo, e pôr o número dentro do `--check`
- [x] CORR-WTE-066 — gerar a tabela de endereços atropelados do medido, e nomear o quarto DWORD
- [x] CORR-WTE-067 — reescrever a nota de desbloqueio da 27 com a API que ficou
- [x] CORR-WTE-068 — reescrever a régua das três specs com o resultado de hoje
- [x] CORR-WTE-069 — cobrir o inverso do índice linear e o alocador com teste próprio
- [x] CORR-WTE-070 — reconciliar a tabela de arquivos da 27 com a árvore
- [x] CORR-WTE-071 — contar o `LAYOUT` em vez de afirmar 16 destinos
- [x] CORR-WTE-072 — reescrever o fecho do `gravacao-controle.md` com o que a 28 mediu
- [x] CORR-WTE-073 — dar `WTE_DISPLAY` ao `check_lcl_combo.py`, com `:98` de default
- [x] CORR-WTE-074 — resolver a fixture do `.mcr` por ordem, com a estável na frente
- [x] CORR-WTE-075 — parametrizar o destino do `--roundtrip` e tirar o teste de cima do versionado
- [x] CORR-WTE-076 — remedir as linhas do `ficha_color.dfm` no plano e na task
- [x] CORR-WTE-077 — reescrever a §5.3 do plano com o algoritmo de paleta que foi medido
- [x] CORR-WTE-078 — corrigir a contagem de casos novos do `test_dump_zonas.py`
- [x] CORR-WTE-079 — apagar os dois blocos mortos de `--malha` do `compara_tela.sh`
- [x] CORR-WTE-080 — estabilizar o `golden-14-uniforme`, ou tornar a repetição explícita
- [x] CORR-WTE-081 — implementar as três gravações órfãs, uma por vez, com o controle fechando antes de cada golden
- [x] CORR-WTE-082 — portar a `0x0040A0B4` e medir a metade de tática do ` Accept`, antes de a CORR-WTE-081 poder fechar
- [x] CORR-WTE-083 — dar cor à bandeira dos 8 times CLASSIC, pela tabela de offsets do Obocaman, sem mexer no `we2002_core`
- [x] CORR-WTE-084 — decidir de quem é o desvio do combo 85: 2 px na bandeira e uma barra fora da grade no oráculo
- [x] CORR-WTE-085 — acertar a conta de gravações no plano e no `progresso.md`: são dezessete
- [x] CORR-WTE-086 — separar o dono do `ficha_enlaza` do dono do `ficha_movertodos` na WTE-TASK-30
- [x] CORR-WTE-087 — corrigir a contagem de `.inc` e `.uses` do Log da WTE-TASK-30
- [x] CORR-WTE-088 — tirar o `:99` dos comentários que descrevem o comportamento de hoje
- [x] CORR-WTE-089 — medir que handler dispara em que gate golden, e promover os que a régua de byte já cobria
- [x] CORR-WTE-090 — tirar do `aberto` o que espera decisão, e quebrar o ciclo do `ComboBoxDrawItem`
- [x] CORR-WTE-091 — descer a `PreencheFicha` para a `wte_ficha` e julgar o `Original ` por um par diferencial
- [x] CORR-WTE-092 — dar ao harness o verbo `arrasta` e um roteiro que entre pelo botão do reserva
- [x] CORR-WTE-093 — ler os quatro laços do `estrategia.FormCreate` e escrever os dois últimos corpos fora de preço
- [x] CORR-WTE-094 — corrigir a premissa de preço da WTE-TASK-32 e registrar o oráculo B que ela ganha
- [x] CORR-WTE-095 — descobrir por que a `0x00403400` posiciona e não escreve na 23ª volta
- [x] CORR-WTE-096 — tirar a chave duplicada do `GOLDEN_DE` e recusar gate vazio de escritor `implementado`
- [x] CORR-WTE-097 — atualizar o cabeçalho do `base_teamClick.inc` para os seis times medidos
- [x] CORR-WTE-098 — pôr a régua de byte na §5.1 do plano, e nomear as duas metades da feature
- [x] CORR-WTE-099 — acrescentar o `.gitignore` à lista de arquivos da WTE-TASK-32
- [x] CORR-WTE-100 — tirar as chaves da diretiva citada na prosa do `we2002_preco.pas`
- [x] CORR-WTE-101 — trocar "seis seções" por cinco no gabarito e no gerador, e dizer que a conta é só delas
- [x] CORR-WTE-102 — atualizar de 94 para 96 a população de specs de onde saem as dezessete gravações
- [x] CORR-WTE-103 — tirar do `if` a linha em branco que separa o bloco de specs do título seguinte
- [x] CORR-WTE-104 — mover o `golden-24` para um time em que os dois primeiros cobradores diferem, e escrever o resultado do terceiro ponto
- [x] CORR-WTE-105 — dar entrada na WTE-TASK-35 à pendência que a 34 encaminhou para ela
- [x] CORR-WTE-106 — escrever o `test_check_divergencias.py` com as quatro recusas plantadas
- [x] CORR-WTE-107 — acrescentar o repasse da WTE-TASK-36 à lista de arquivos da 35
- [x] CORR-WTE-108 — trocar o "falta conferir" pelo resultado da conferência: o plano não afirmava
- [x] CORR-WTE-109 — medir a segunda gravação em geral e dar sujeito à frase da não-idempotência
- [x] CORR-WTE-110 — medir as bordas nos outros três vetores, ou escrever que a medição é por classe
- [x] CORR-WTE-111 — apagar a `faixa` morta do `CAMPOS`, ou torná-la expectativa conferida
- [x] CORR-WTE-112 — conferir o `filtro` de cada campo contra o `KeyPress`, como já se faz com a faixa
- [x] CORR-WTE-113 — fazer o `--roteiro` preservar o registro, e guardar a preservação com teste
- [x] CORR-WTE-114 — abrir no `divergencias.md` as entradas das três candidatas da reconferência de UI
- [ ] CORR-WTE-115 — escrever o `test_check_carregado.py` com a recusa da moldura plantada

## Detalhes por correção

### CORR-WTE-060

- **Arquivo com problema:** `wte/src/impl/ep2002_mainform.lista_equiposChange.inc`
  (linha 49) e/ou `wte/forms/ep2002_mainform.lfm`
- **Sintoma:** no time-modelo o `nacional` vira falso e o original acinzenta o
  `iguala_nombres`; o port não muda um pixel. A linha `Enabled := nacional`
  existe, e o vizinho `boton_nombres2iso` — mesmo `TSpeedButton`, mesmo `Flat`,
  mesmo `Glyph`, seis linhas abaixo — acinzenta certo
- **Como foi detectado:** medido pela CORR-WTE-057 (0 px contra 518), que
  escreveu no Log que o defeito pede correção própria. Nenhuma foi aberta; a
  WTE-TASK-26 fechou apontando de novo para ela
- **Fix:** reproduzir isolado no `:99`, trocar **uma** variável por vez
  (`ParentFont`, depois a cor de canto do glifo), e corrigir onde a medição
  apontar — no `dfm2lfm.py` se for conversão, nunca no `.lfm` gerado. Se a causa
  for da LCL, vira divergência deliberada com a medição escrita

### CORR-WTE-061

- **Arquivo com problema:** `wte/src/impl/ep2002_mainform.FormShow.inc` e
  `wte/tools/dump_truncamento.py`
- **Sintoma:** duas linhas vizinhas com lastro diferente — `edit_nombre2` sai de
  `SizeOf` do campo de destino e é conferida a cada `make check`;
  `edit_nombre1` é o literal 5, apoiado só numa leitura de tela
- **Como foi detectado:** o `compara_tela.sh --nomes`, na primeira corrida,
  achou o port aceitando 7 caracteres contra 5 do oráculo. A conferência do
  gerador havia aprovado 20 porque `40 div 2` fecha — ela compara a aritmética
  contra um destino escrito à mão
- **Fix:** ler o `0x0040cbc8`, que preenche a tabela de `0x00433a10` a partir de
  `0x004231a0`, e descobrir o que é a coluna 0. Com o destino nomeado, devolver
  a entrada a `DESTINOS` e **conferir que dá 5** — não escolher o campo que dê 5

### CORR-WTE-062

- **Arquivo com problema:** `wte/src/ep2002_estrategia.pas` (o `REStub` da linha
  214) e `wte/re/spec/estrategia.lista_formacionesClick.md`
- **Sintoma:** a spec da WTE-TASK-25 encaminha o handler para a WTE-TASK-26; a
  26 não o tem na lista, porque o grupo dele é `carga`. As duas tasks estão
  concluídas e o corpo é stub. Dois handlers da 26 ficaram `aberto` por
  dependerem dele: o `bolaMouseDown` desenha sempre a zona 0 e o `relojTimer`
  nunca roda
- **Como foi detectado:** ao escrever o `check_edicao.py`, conferindo quem
  preenche o vetor bola→zona
- **Fix:** portar o handler com as duas auxiliares (`0x004097d4`, 474 B e
  `0x004099bc`, 227 B), e **rever os três vereditos na mesma passagem** —
  `lista_formacionesClick`, `bolaMouseDown` e `relojTimer`

### CORR-WTE-063

- **Arquivo com problema:** `docs/tasks/29-camisa-e-bandeira-2d.md` ou
  `docs/tasks/35-divergencias-deliberadas.md`, conforme a decisão
- **Sintoma:** as três carregadoras de bitmap da ficha (`0x00406fe0`,
  `0x00407110`, `0x00407338`) foram excluídas pela WTE-TASK-26 como "sem dono", e
  a WTE-TASK-29 não menciona cara, cabelo nem barba. No port as setas de
  aparência mudam o rótulo e não mudam o desenho
- **Como foi detectado:** `grep -rl` dos três endereços em `docs/tasks/` devolve
  só a task que os excluiu
- **Fix:** decisão do usuário — estender a 29 (as três tabelas de cor já estão
  localizadas) ou registrar a exclusão na 35 com o efeito escrito. O que não
  fecha é o estado de hoje

### CORR-WTE-064

- **Arquivo com problema:** `wte/tools/dump_truncamento.py` (`CONTRADIZ_A_TELA`)
  e `wte/src/impl/ep2002_mainform.aux.inc` (`LimiteDoNome1`)
- **Sintoma:** o lote do `edit_nombre1` está provado — `OFS_TEAM_NAME_KANJI`,
  `0x004231a0`[0][0] — e a travessia do original emulada byte a byte dá largura
  12 para o time 2, logo `div 2` = 6. **O oráculo corta em 5.** O `edit_nombre2`,
  pelo mesmo modelo, fecha exato (7, conferido na tela)
- **Como foi detectado:** `compara_tela.sh --nomes` com o texto novo
  `A B-C.DEFG`, cujo sexto caractere é um `D` visível: o oráculo mostra `A BC.`
  e o port, posto em 6, mostrava `A BC.D`
- **Fix:** reler `0x00403c0c` instrução a instrução, com atenção a onde `esi` é
  incrementado em relação ao `getc`; se não fechar, medir a tela em três times
  de larguras diferentes e ver se a diferença é constante. Cinco hipóteses já
  estão descartadas no arquivo da correção

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
  `docs/tasks/30-handlers-auxiliares.md`, `docs/tasks/32-preco-do-jogador.md`,
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
  o dono errado repetido na task 32, `BitBtn1Click` 3× na task 30 (são 4) e
  cinco handlers de ocorrência única listados como repetidos, dos quais o `.md`
  registra só `botonClick`
- **Como foi detectado:** `grep -rn "FormCreate" docs/PLAN-WTE-LAZARUS.md` não
  devolve o "17"; `grep -rn "17 vezes" docs/` devolve os dois arquivos que o
  têm. As contagens saem do TSV gerado, que a própria seção "Homônimos" do
  `.md` já imprime certas
- **Fix:** no gerador — corrigir a atribuição e derivar as linhas faltantes de
  `count_by_name(m)`, abortando se um nome citado da task 30 não existir entre
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

### CORR-WTE-044

- **Arquivo com problema:** nenhum arquivo, e é isso que a torna diferente das
  43 anteriores — o defeito é de **ordem entre fases**, no
  `docs/PLAN-WTE-LAZARUS.md` §4.2 e no grafo de dependências da fase 4
- **Sintoma:** o `wte.exe` morre ao trocar de time com as duas ROMs daqui, e a
  cadeia para destravá-lo se fecha sobre si mesma: o gate da WTE-TASK-22 precisa
  do oráculo vivo, entender o oráculo é a WTE-TASK-25, e a 25 depende da 22
- **Como foi detectado:** WTE-TASK-19, terceira passagem. `WINEDEBUG=+seh,+loaddll`
  põe a violação de acesso em `Graphics::TFont::SetSize` + 8 do `vcl60.bpl`
  (realocado para `0x005f0000`), com `this` nulo, chamada de `0x0040b1ac` dentro
  de uma rotina que faz `FindComponent("dorsal" + N)`. Os roteiros 07 e 08 são
  iguais até `= ARRANQUE` e dão 0 contra 309 violações — a atribuição é medida.
  Duas hipóteses anteriores caíram antes desta: tamanho da imagem e região vazia
  em `14368636`
- **Fix:** diagnóstico estático, sem implementar nada. Quatro perguntas em ordem
  de custo (o que é `+0x68` nesta VCL, de onde vem o `N`, quem escreve no global
  `0x004335e4`, existe contorno), com o ferramental da WTE-TASK-24 que já está
  concluída. Os dois desfechos são legítimos, e o negativo **muda a WTE-TASK-22**
- **Desfecho: o positivo — condição de contorno, e é a imagem.** Com
  `roms/japanese-shift-jis.bin` o `wte.exe` passa da troca de time com **0**
  violação de acesso, contra 49.749 com a europeia no mesmo roteiro. O controle
  procurado **existe**; o ponteiro global é que é sobrescrito pela carga do
  time. Medição em [`../../wte/re/crash-causa.md`](../../wte/re/crash-causa.md)
- **O "com as duas ROMs daqui" do Sintoma acima era extrapolação.** A japonesa
  nunca tinha sido medida neste caminho — `grep` por `japonesa` na WTE-TASK-19,
  no `offsets-novos.md` e no `crash.md` não devolvia nada antes desta correção.
  A frase não estava errada por descuido de quem mediu: a WTE-TASK-19 mediu a
  europeia e generalizou. Fica como lembrete de que "as duas ROMs" é afirmação
  que custa uma corrida a mais para virar medida

### CORR-WTE-045

- **Arquivo com problema:** `wte/tools/analisar_io.py:478`, e o
  `wte/re/offsets-novos.md` que sai dele
- **Sintoma:** a seção das seis áreas diz ter medido sobre "cópia de
  `roms/09-areas-com-time`" — nome da **sessão**, não da imagem. Esse caminho
  não existe; a imagem é `japanese-shift-jis.bin`, como as 64 linhas dessa
  sessão registram no `io-medido.tsv`. E a frase seguinte, sobre a europeia
  travar, só faz sentido com a japonesa
- **Como foi detectado:** `ls roms/` contra o texto gerado, e a contagem por
  `sessao`/`imagem` do `io-medido.tsv`
- **Fix:** derivar o nome da imagem das linhas da própria sessão em vez de
  interpolar a constante `AREAS`, e regerar

### CORR-WTE-046

- **Arquivo com problema:** `wte/tools/analisar_io.py` — `papel_no_legado()`
  (linhas 430-437) e a montagem da prova (linha 672)
- **Sintoma:** 3 dos 14 vereditos `retomada de fronteira` provam com
  `` `case N` no `Database.cpp` `` onde o fonte tem `if(i == N)`:
  `OFS_FORMATIONS_A` (32), `OFS_TEAM_NAME_5_A` (57) e `OFS_ML_TEAM_NAME_8_A`
  (30). Nos dois primeiros o `case N :` não existe no arquivo; no terceiro
  existe, e em bloco sem relação — a citação leva ao sítio errado
- **Como foi detectado:** cruzando o gatilho devolvido por `papel_no_legado()`
  contra `re.search(r"\bcase\s+N\s*:")` no `src/core/Database.cpp`
- **Fix:** o classificador casa `RE_CASO` **ou** `RE_SE` e descarta qual das
  duas foi; devolver a construção junto do gatilho e imprimir a que casou. O
  veredito e as contagens 33/14/3 não mudam — é rótulo

### CORR-WTE-047

- **Arquivo com problema:** nenhum arquivo tem o dado — é o que falta.
  `wte/tools/diff_dirigido.sh:270` roda a conferência e o resultado morre no
  diretório da sessão
- **Sintoma:** as sessões `10-telas-que-faltavam` e `11-varredura-de-times`,
  que levaram os endereçados de 15 para 33, não têm em lugar nenhum o número da
  segunda régua — o `cmp.tsv` não é versionado, o Log da 5ª passagem não o traz
  (o da 4ª traz) e o `offsets-novos.md` só cita o `cmp` como método
- **Como foi detectado:** `git ls-files wte/re | grep cmp` vazio, e `grep` por
  "réguas" no `offsets-novos.md` sem resultado de sessão
- **Fix:** versionar o resultado do `cmp` por sessão e gerar o veredito das
  duas réguas no `offsets-novos.md`, com teste exigindo a linha para toda
  sessão que escreveu. Não há suspeita de que a conferência não rodou — o
  script tem `set -euo pipefail` e a função devolve 3 quando falha; o que falta
  é o rastro

### CORR-WTE-048

- **Arquivo com problema:** `wte/tools/compare_dumps.py:278`, e o
  `wte/re/fase-3.md` que sai dele
- **Sintoma:** a seção do oráculo abre com "Não é o `wte.exe` — esse **não
  passa da tela de carga**", e linka a CORR-WTE-044 ao lado, que é a correção
  que desfez essa frase. O `dd2f2a9` aposentou a afirmação em quatro arquivos e
  não neste
- **Como foi detectado:** `grep -n "tela de carga" wte/re/fase-3.md` contra o
  `git show --stat dd2f2a9`, que não lista o arquivo — a ordem explica: o
  `e12a999` (WTE-TASK-20) é anterior ao sweep
- **Fix:** trocar a justificativa por uma que sobreviva à CORR-WTE-044 — o
  `wte.exe` é oráculo de **comportamento**, e a pergunta desta task é de
  **formato** —, e regerar

### CORR-WTE-049

- **Arquivo com problema:** `docs/tasks/20-round-trip-headless.md:25-38`
- **Sintoma:** duas populações trocadas. Os "36 restantes" saem dos 50 `OFS_*`
  que a WTE-TASK-06 marcou `ausente`, e esses 50 são **todos** do
  `Offsets.hpp` — há lado C++ para todos, e o texto diz que são "os que o
  `we2002_core` não tem". Quem o core não tem são as faixas sem dono. Além
  disso o parágrafo dá a WTE-TASK-19 como `❌ Bloqueado` (está ✅ desde
  2026-08-10) e repete 28 / 36, que hoje são 33 / 17
- **Como foi detectado:** a tabela de vereditos do `offsets-novos.md` tem
  `Offsets.hpp` como primeira coluna, e `grep` pelos nomes no header confirma;
  o status, contra a linha da 19 no `progresso.md`
- **Fix:** reescrever a seção mantendo o argumento (nenhum critério da 20 toca o
  oráculo A), nomeando as duas populações separadamente e apontando para a nota
  do `progresso.md` em vez de repetir status de outra tarefa

### CORR-WTE-050

- **Arquivo com problema:** `wte/tools/check_fase3.py:303-305`, o
  `wte/re/fase-3-fechamento.md` que sai dele, e a §4.5 do
  `docs/PLAN-WTE-LAZARUS.md` para onde a frase migrou
- **Sintoma:** "2504 linhas de C++ viraram 3692 de Pascal — razão 1.47" divide a
  saída dos **dois** geradores pela entrada de **um**. As 708 linhas de
  `we2002_offsets.pas` + `we2002_tables.pas` vêm do `gen_tables_pas.py`, cuja
  entrada — `Tables.cpp` (704), `Tables.hpp` (53), `Offsets.hpp` (95), 852
  linhas — está em `FORA_DO_TRANSPILADOR` e não entra no denominador. Fechando
  os dois lados a razão é 1.10; só o transpilador, 1.19
- **Como foi detectado:** `DA_CAMADA` nomeia o gerador de cada `.pas` e
  `entrada_do_transpilador()` percorre só `P.UNITS`; `wc -l` nas três entradas
  do `gen_tables_pas` fecha as 852
- **Fix:** parear entrada e saída por gerador — duas razões, ou um denominador
  completo —, com teste que reprove saída contada sem a entrada do seu gerador

### CORR-WTE-051

- **Arquivo com problema:** `wte/tools/check_fase3.py` — `linhas()` contra
  `confere_bloco()`
- **Sintoma:** a coluna **linhas** conta tudo (`len(splitlines())`) e a coluna
  **à mão** só linha útil (`if l.strip()`); a terceira coluna é a subtração das
  duas. As 26 linhas em branco dentro dos blocos manuais entram como "por
  regra". Publicado 92,5%; com a mesma régua nos dois lados, 91,8% (com brancos)
  ou 92,2% (sem). A conclusão da fase não muda em nenhuma das três
- **Como foi detectado:** recontagem por fora com o mesmo dedupe do
  `check_fase3`, medindo os blocos manuais nas duas réguas — 277 contra 303
- **Fix:** contar os dois lados da subtração com a mesma régua, dizer qual é no
  cabeçalho da tabela, e prender isso em teste

### CORR-WTE-052

- **Arquivo com problema:** `docs/tasks/22-harness-golden.md`, linhas 225 e 236
- **Sintoma:** o Log diz **15 testes** no `golden_veredito.py`, em dois sítios, e
  são **18** — o arquivo nasceu com os 18 no próprio commit da task (`e139f46`).
  A frase existe para justificar por que o veredito é Python e não shell, e o
  tamanho da bateria é a evidência do argumento
- **Como foi detectado:** `grep -c "    def test_"` e
  `python3 -m unittest test_golden_veredito` — `Ran 18 tests`
- **Fix:** trocar 15 por 18 nos dois sítios, com o comando que remede ao lado.
  Terceiro caso da mesma família, depois da CORR-WTE-038 (41→47) e da
  CORR-WTE-042 (33→38)

### CORR-WTE-053

- **Arquivo com problema:** `docs/tasks/22-harness-golden.md`, seção 2
- **Sintoma:** a seção que define o que o gate tem de tolerar descreve **uma**
  faixa de 11.952 bytes (`11796..26527`); o roteiro do gate declara **nove**, e
  as duas últimas — `1921862..1921862` e `2012984..2012985` — ficam fora daquele
  intervalo. Medido no modo `golden`: 9 faixas, 11.955 bytes, com as sete de
  setor somando exatamente os 11.952 herdados. Nenhum dos dois textos diz de
  qual imagem fala: a seção veio da WTE-TASK-12 (europeia, 474.784.128 B) e o
  gate fixa a japonesa (307.187.664 B)
- **Como foi detectado:** corrida do gate nesta revisão com `--manter`, e soma
  por faixa do `diff.json`
- **Fix:** reescrever a seção com as nove faixas, os 11.955 bytes, a imagem de
  cada medida e a razão de as duas últimas só aparecerem na japonesa. A decisão
  de declarar em vez de reproduzir não muda

### CORR-WTE-054

- **Arquivo com problema:** `wte/re/vmt.md`, a frase de proveniência do topo
  contra os números da tentativa de âncora
- **Sintoma:** o arquivo afirma que **todo** número saiu do `vmt_probe.java` e
  do `decompile_one.java`. Os "4 votos entre ~150 referências" e o empate a 4
  bytes entre os dois primeiros candidatos não saem de nenhum dos dois — o probe
  imprime a `CAMPOS-POR-HANDLER`, que é a *entrada* do cálculo. E é esse número
  que decide a rota da §8.2
- **Como foi detectado:** `grep -in "voto\|ancora\|anchor" vmt_probe.java` vazio,
  e a lista de `println` do script; o resto dos números foi remedido rodando o
  probe e bate (217 / 189 / 113 slots / dez slots somando 217)
- **Fix:** pôr a votação no `vmt_probe.java` — ele já tem os dois insumos —, ou
  qualificar a frase dizendo que os votos foram calculados fora, com o comando

### CORR-WTE-055

- **Arquivo com problema:** `docs/tasks/24-ghidra-convencao-borland.md`, seção 4
- **Sintoma:** "os 322 imports de `rtl60.bpl`/`vcl60.bpl`" — 322 é o **total**;
  as duas BPLs são 267, e os outros 55 são das DLLs do Windows. O Log da mesma
  task diz 267, então o arquivo se contradiz; a WTE-TASK-09 já tinha corrigido
  essa atribuição no `progresso.md`
- **Como foi detectado:** `run_headless.sh` rodado do zero nesta revisão —
  KERNEL32 51, OLEAUT32 1, RTL60 103, USER32 3, VCL60 164
- **Fix:** 267 nas duas ocorrências da seção 4, com 322 nomeado como total

### CORR-WTE-056

- **Arquivo com problema:** `wte/tools/ghidra/borland_cc.md` (linhas 94 e 107) e
  `wte/tools/ghidra/run_headless.sh` (linha 7)
- **Sintoma:** os três mandam rodar `apply_names.py`; o script é
  `apply_names.java`, e não existe `.py` na árvore. O `borland_cc.md` é o
  documento que permite refazer o projeto Ghidra do zero, e a linha 107 descreve
  a guarda do cspec — que existe e funciona — apontando para o arquivo errado
- **Como foi detectado:** `grep -rn "apply_names\.py" wte/tools/ghidra/`; a
  guarda foi exercitada importando o `.exe` com `-cspec borlanddelphi` e ela
  abortou com a mensagem certa
- **Fix:** trocar por `.java` nos três sítios, e dizer no passo da GUI que o
  `analyzeHeadless` compila GhidraScript em Java sozinho

### CORR-WTE-057

- **Arquivo com problema:** `wte/tools/compara_tela.sh` (`REC_W=520`,
  `REC_H=240`) e o critério de tela da WTE-TASK-25
- **Sintoma:** o critério reduzido enumera cinco grupos de campo — nome nos três
  campos, as cinco barras, **os 23 números de camisa**, **a lista de jogadores**
  e **o estado de habilitação que o `nacional` governa**. O recorte comparado
  cobre os dois primeiros; `lista_jugadores_1` está em y ≈ 392 e os `dorsalN` em
  y ≈ 432, fora dos 240 px de altura. O estado de habilitação nunca foi
  confrontado com o do original — e é exatamente a seção **Saída** da spec, que
  está `nao medido` desde a sexta passagem
- **Como foi detectado:** posições absolutas somadas pela cadeia de pais do
  `MainForm.dfm`; `bash wte/tools/compara_tela.sh 2 9 63` refeito nesta revisão
  (15 larguras batem, 14 exatas contra o dump) e a montagem
  `work/tela/time-63-lado-a-lado.png` termina acima das duas faixas
- **Fix:** estender o recorte (ou usar dois, excluindo por coordenada a caixa
  x 232..312 / y 36..168 da bandeira e do uniforme, que são da WTE-TASK-29) e
  escrever o veredito dos três grupos que faltam, um a um
- **Ela achou dois defeitos do port, e nenhum foi corrigido nela.** Os
  `dorsal1..23` mostram o byte cru onde o original mostra byte + 1, e o
  `iguala_nombres` não é desabilitado no time-modelo. Os dois são comportamento
  do Pascal, estão medidos no Log e na spec, e **pedem correção própria** — o
  escopo desta era o instrumento

### CORR-WTE-058

- **Arquivo com problema:** `wte/re/visual.md` (linhas 12, 19 e 293) e a árvore
  de pastas do `docs/tasks/progresso.md`
- **Sintoma:** o `visual.md` traz `bash wte/tools/capture_forms.sh` como o modo
  de reproduzir o lado port, e a WTE-TASK-25 deletou o script junto com o
  `--show` de que ele dependia. A árvore do `progresso.md` lista quatro
  ferramentas da 25 e não lista `src/impl/`, `src/we2002_estado.pas`,
  `compara_tela.py`/`.sh` nem `check_lcl_combo.py` — e ainda diz que os corpos
  das 25-28 moram nos `ep2002_*.pas`, que é o oposto da decisão da 1ª passagem
- **Como foi detectado:** `ls wte/tools/capture_forms.sh` (não existe) contra
  `grep -n 'capture_forms' wte/re/visual.md`; o `make -C wte check` fica verde
  porque o `visual.md` é **entrada** do `check_fase2.py`, não saída
- **Fix:** reescrever os três sítios no passado, nomeando a task que retirou o
  andaime e preservando as duas armadilhas de captura, que sobrevivem à
  ferramenta; completar a árvore do `progresso.md`

### CORR-WTE-059

- **Arquivo com problema:** `wte/re/spec/MainForm.lista_equiposChange.md`,
  linhas 160-163
- **Sintoma:** "É o custo de ainda não ter conferido contra a tela, e a razão de
  o veredito continuar `aberto`" vem imediatamente antes de
  "## A conferência de tela — três times, e os dois erros que ela achou". A
  frase é da 6ª passagem, a seção é da 8ª. O veredito está certo; a razão
  escrita é que envelheceu, e ela esconde a razão real — a seção **Saída** em
  `nao medido`, por `TControl::SetEnabled` não ter uma única `call rel32`
- **Como foi detectado:** leitura do arquivo em ordem, com
  `bash wte/tools/compara_tela.sh 2 9 63` confirmando que a conferência existe e
  passa
- **Fix:** trocar a frase de fecho pela razão que sobrou, e reescrevê-la de novo
  se a CORR-WTE-057 subir a seção Saída para `observação de tela`

### CORR-WTE-065

- **Arquivo com problema:** `wte/tools/conta_ml.py:185`,
  `wte/src/we2002_ml.pas:129`, `docs/tasks/33-slots-de-master-league.md:179`
- **Sintoma:** os três justificam não modelar `b0 >= 120` com "o maior `b0`
  medido é 43". O 43 é o maior `b0` entre os pares **fora do vetor**; a
  varredura dos 760 pares dá **111** na europeia e **116** na japonesa. A
  conclusão continua de pé, a margem até 120 não é 77, é 4
- **Como foi detectado:** varredura dos 760 pares das duas cópias de `work/`,
  com o mesmo salto de fronteira de setor da `conta_ml.conta()`
- **Fix:** `conta()` devolve o `max_b0`, o `--medir` o grava no
  `ml-slots-medido.tsv` e o `gera_md()` compõe a frase dali; caso novo no
  `test_conta_ml.py`

### CORR-WTE-066

- **Arquivo com problema:** `wte/tools/conta_ml.py` (a tabela literal do
  `gera_md()`), refletida em `wte/re/ml-slots.md`
- **Sintoma:** a tabela dos "endereços alcançados" lista o índice 462, que não
  é alcançado em nenhuma das duas imagens, e omite `0x004335f4` (índices 488 e
  489), que é alcançado na europeia. O `fora_do_vetor = 8` do
  `ml-slots-medido.tsv` não reconcilia com uma tabela de três linhas, e o
  quarto DWORD não aparece em `crash-causa.md` nem em nenhum outro arquivo
- **Como foi detectado:** `conta_ml.conta()` sobre `work/ml-eu.bin`, com os
  índices de `fora` convertidos em endereço por `0x00433224 + 2*i`
- **Fix:** gerar a tabela do medido; registrar a divergência entre modelo
  (quatro DWORDs) e medição ao vivo (três) como pergunta nomeada
- **Pendência resolvida em 2026-08-20:** a sessão foi refeita
  (`sonda_dorsal.py … --vizinhanca`) e o `0x004335f4` muda de `0x0` para
  `0x00010001` no mesmo instante dos outros três. Era falha de transcrição, não
  de comportamento; `CRASH_DWORDS` passou a ter os quatro e o gerador emite a
  concordância em vez da pergunta

### CORR-WTE-067

- **Arquivo com problema:** `docs/tasks/27-handlers-de-gravacao.md`,
  linhas 178-181
- **Sintoma:** a nota diz que o contador é a `AtualizaBlocosLivresDeMl` "do
  `we2002_ml`" — ela é do `ep2002_mainform.aux.inc` — e que "com ele vem o mapa
  de ocupação que diz qual bloco está livre". Não vem: o vetor `ocupacao` é
  local da `ContaBlocosLivresDeMl` e a unidade só devolve a contagem e o número
  de índices fora do vetor
- **Como foi detectado:** leitura da `interface` de `wte/src/we2002_ml.pas` e
  `grep -rn AtualizaBlocosLivresDeMl wte/src`
- **Fix:** reescrever a nota com a API entregue, e dizer qual é o caminho para
  obter o índice livre que a 27 vai precisar

### CORR-WTE-068

- **Arquivo com problema:** `wte/re/spec/MainForm.boton_barras2isoClick.md:119`,
  `MainForm.boton_nombres2isoClick.md:208`, `MainForm.boton_tex2isoClick.md:105`
- **Sintoma:** as seções "a régua desta task" dizem que o `golden_check.sh`
  passa "só as duas faixas do arranque". Desde que a oitava passagem portou os
  dois remendos, os gates são **byte-idênticos** e nenhum roteiro declara faixa
- **Como foi detectado:** `golden_check.sh` sobre `golden-03-barras`,
  `golden-05-nomes`, `golden-06-textura`, `golden-11-descarte-ml` e
  `golden-01-arranque` — todos `PASSOU: byte-identico`; `golden_veredito.py
  --check` diz `21 roteiro(s), 0 declaracao(oes)`
- **Fix:** trocar o resultado nas três, com data, e deixar o histórico numa
  linha. Não mexer no `grabar_memoryClick.md:191`, que fala da sonda contra a
  cópia limpa e continua correto

### CORR-WTE-069

- **Arquivo com problema:** `wte/tests/test_ml.pas`, `wte/tools/test_conta_ml.py`
- **Sintoma:** `IndiceDoBlocoMl`, `ParDoIndiceLinearMl` (o port da `0x0040427c`,
  o inverso do índice linear) e `PrimeiroBlocoLivreMl` entraram na interface do
  `we2002_ml` e só são exercitados pelo `golden-11-descarte-ml`, que aloca **um**
  bloco — o 350. Fronteira nenhuma é tocada
- **Como foi detectado:** `grep` das três na árvore de testes (zero
  ocorrências); `test_ml.pas` reporta `CASOS 7` sem imagem e `CASOS 8` com
- **Fix:** casos de ida e volta, de fronteira e de fora da faixa no
  `test_ml.pas`, com o `CASOS` esperado subindo junto

### CORR-WTE-070

- **Arquivo com problema:** `docs/tasks/27-handlers-de-gravacao.md`, tabela
  "Arquivos a criar ou modificar"
- **Sintoma:** a tabela promete `wte/tools/roteiros/gravacao-*.sh` (4). O
  diretório não existe; o que existe é `wte/tests/roteiros/`, com 21 roteiros de
  gate e 9 sondas, todos `.txt` declarativos. A linha das specs também ficou
  curta (diz 4; são as quatro gravações mais `dorsalClick` e os sete de mover)
- **Como foi detectado:** `ls wte/tools/roteiros/` contra `ls wte/tests/roteiros/`
- **Fix:** reescrever a tabela com o que existe e anotar a mudança de formato
  com data e motivo, como a WTE-TASK-33 fez com o destino do `ml-slots.md`

### CORR-WTE-071

- **Arquivo com problema:** `wte/tools/dump_mcr.py` (linhas 30 e 528),
  `wte/re/mcr.md`, `wte/src/we2002_mcr.pas`, `docs/tasks/28-import-de-mcr.md`
- **Sintoma:** cinco lugares dizem "14 dos **16** destinos"; o `LAYOUT` tem
  **17** (3 no bloco 2, 14 no bloco 3), e o título gerado fica logo acima da
  tabela que lista as 17 linhas
- **Como foi detectado:** `python3 -c "import dump_mcr as m; print(len(m.LAYOUT))"`
  contra o título de `wte/re/mcr.md`; `git show` mostra que o `LAYOUT` nasceu
  com 17 no mesmo commit que escreveu o 16
- **Fix:** computar o número no gerador, como o `min(...)` vizinho já faz, e um
  caso de teste que fixe `len(LAYOUT)`

### CORR-WTE-072

- **Arquivo com problema:** `wte/tools/gravacao_controle.py` (linhas 321-324) e
  o `wte/re/gravacao-controle.md` que ele gera
- **Sintoma:** o parágrafo final diz que a única gravação de setor inteiro do
  projeto é o `boton_mcr2isoClick` e que "é lá que preservar EDC/ECC vira
  decisão". A WTE-TASK-28 mediu o contrário e fechou o critério por refutação;
  o mesmo documento já conta a sessão `27-mcr2iso` entre as 164 faixas limpas
- **Como foi detectado:** leitura do `wte/re/cmp-medido.tsv` — as sete faixas do
  handler vão de 1 a 276 bytes, todas entre 24 e 2071 do setor
- **Fix:** trocar a previsão pelo resultado, com os números computados do
  `cmp-medido.tsv`

### CORR-WTE-073

- **Arquivo com problema:** `wte/tools/check_lcl_combo.py`, linhas 113-144
- **Sintoma:** único resto de `:99` em código executável depois de `601943f`.
  Numa máquina só com o `:98` o gate PULA em silêncio; com um `:99` alheio de
  pé, ele dirige GUI lá — os dois contra a regra do `CLAUDE.md`
- **Como foi detectado:** `make -C wte check` desta revisão imprimiu
  "PULADO (sem Xvfb :99)"; `grep -rn 'WTE_DISPLAY' wte/tools/` mostra que todo
  o resto já migrou
- **Fix:** `ALVO = os.environ.get("WTE_DISPLAY", ":98")` e as três menções em
  código passam a usá-lo

### CORR-WTE-074

- **Arquivo com problema:** `wte/tools/test_dump_mcr.py`,
  `TestPascalConcorda.CARTAO`
- **Sintoma:** a única prova de que os leitores Pascal e Python enxergam o
  mesmo cartão de verdade procura `work/saida.mcr`, que o `golden_check.sh`
  apaga antes de cada lado das corridas com `--artefato saida.mcr`. A fixture
  estável é `work/entrada.mcr`, que fica ao lado
- **Como foi detectado:** `python3 -m unittest test_dump_mcr` reporta
  `OK (skipped=2)`, e `ls work/*.mcr` mostra `entrada.mcr` e `volta.mcr`, sem
  `saida.mcr`
- **Fix:** resolver a fixture por ordem — `WTE_MCR_FIXTURE`, depois
  `work/entrada.mcr`, depois `work/saida.mcr`

### CORR-WTE-075

- **Arquivo com problema:** `wte/tools/dump_mcr.py` (`do_roundtrip`),
  `wte/tools/test_dump_mcr.py` (`test_a_medicao_e_escrita`)
- **Sintoma:** o destino é fixo e versionado, então o teste escreve por cima de
  `wte/re/mcr-roundtrip.tsv` com dado sintético e o repõe num `finally`;
  interrupção que pule o `finally` deixa fixture de teste no lugar da medição.
  O `print` da rotina também vaza para o relatório do `unittest`
- **Como foi detectado:** a saída de `make -C wte check` traz
  "arquivo inteiro: 1 bytes diferentes" depois do `OK`, e a leitura do teste
  mostra o `try/finally`
- **Fix:** `do_roundtrip(antes, depois, destino=IDA_E_VOLTA)`, e o teste
  apontando para o `tempfile` que já cria

### CORR-WTE-076

- **Arquivo com problema:** `docs/PLAN-WTE-LAZARUS.md` §5.3,
  `docs/tasks/29-camisa-e-bandeira-2d.md`
- **Sintoma:** os dois dimensionam o `ficha_color` em **758 linhas de DFM**; o
  artefato versionado tem **866**, e nasceu com 866 no commit que extraiu os 18
- **Como foi detectado:** `wc -l wte/re/dfm/ficha_color.dfm` contra o texto, e
  `git show "7f8fcb0:wte/re/dfm/ficha_color.dfm" | wc -l` para a história
- **Fix:** 758 → 866 nos dois documentos, nomeando a fonte

### CORR-WTE-077

- **Arquivo com problema:** `docs/PLAN-WTE-LAZARUS.md` §5.3, linha 939
- **Sintoma:** o plano manda `TBitmap` + varredura de pixel; a WTE-TASK-29
  mediu que o original não varre pixel nenhum — as três rotinas posicionam o
  `.bmp` em `0x36` e reescrevem entradas de paleta. A task registrou a correção
  nela mesma, e o `progresso.md` manda resolver divergência a favor do plano
- **Como foi detectado:** `wte/re/render2d.tsv` e a seção das três rotinas do
  `wte/re/render2d.md`, os dois com `--check` verde
- **Fix:** reescrever o trecho com o resultado medido, mantendo a hipótese
  antiga como história

### CORR-WTE-078

- **Arquivo com problema:** `docs/tasks/29-camisa-e-bandeira-2d.md`, Log da
  sétima passagem
- **Sintoma:** "7 casos novos, cinco deles recusas". As recusas são cinco de
  fato; os casos novos são **9**
- **Como foi detectado:** `diff` dos `def test_` entre `671a1f9^` e `671a1f9`
- **Fix:** 7 → 9, e anotar o comando que remede

### CORR-WTE-079

- **Arquivo com problema:** `wte/tools/compara_tela.sh`
- **Sintoma:** o bloco `malha` do `captura_oraculo` aparece duas vezes, e o
  primeiro `return 0` deixa o segundo inalcançável; no `captura_port` há um
  `if [ "$MODO" = malha ]` aninhado dentro do ramo `cor|grade` — condição
  impossível — embrulhando uma cópia da chamada ao `compara_tela.py --malha` e
  um `continue` sem laço
- **Como foi detectado:** leitura do script depois de rodar `--malha`, mais
  `grep -n 'compara_tela.py'`, que mostra a chamada duas vezes
- **Fix:** apagar os dois trechos mortos; o `--malha` legítimo já roda pelo
  laço principal e foi reproduzido verde nesta revisão

### CORR-WTE-080

- **Arquivo com problema:** `wte/tests/roteiros/golden-14-uniforme.txt`,
  `wte/tools/roteiro.sh`
- **Sintoma:** quatro corridas de `--modo controle` na mesma árvore: três
  falharam em `espera_janela` (uma no `Extrair Uni do jogo`, duas no `Abre`) e
  uma passou byte-idêntica. Gate que precisa de repetição para ficar verde
  deixa de separar "o port diverge" de "a janela demorou"
- **Como foi detectado:** as quatro corridas desta revisão, com o
  `golden-01-arranque` passando de primeira no meio da série
- **Fix:** subir a espera do passo do diálogo, esperar o `wineserver` do
  prefixo sumir entre os lados, e distinguir na mensagem "app não subiu" de
  "diálogo não veio" — ou tornar a repetição explícita no log

### CORR-WTE-081

- **Arquivo com problema:** `wte/src/impl/` (os três `.inc` que não existem),
  `wte/tests/roteiros/` (os três pares de roteiro que não existem)
- **Sintoma:** `ficha_color.BitBtn3Click` (`0x004069e8`),
  `jugador.BitBtn3Click` (`0x00408548`) e `estrategia.BitBtn3Click`
  (`0x0040a660`) **escrevem na imagem de CD** e ficaram `aberto` sem task dona.
  A WTE-TASK-27 contava seis gravações; medido, são nove. A WTE-TASK-31 exige
  nenhum `aberto` e **não implementa** — ela é fechamento —, então a fase 4 não
  fecha enquanto as três não tiverem dono
- **Como foi detectado:** a leitura dos 17 handlers `auxiliar` na WTE-TASK-30,
  e a varredura de chamadores de `0x004051A4` no `.text`, que devolve
  `['0x4069f9']` — um chamador só, dentro do `BitBtn3Click` do `ficha_color`
- **Fix:** implementar as três na ordem `jugador` → `ficha_color` →
  `estrategia`, cada uma com roteiro golden dos dois lados e o **controle**
  fechando antes. A terceira depende de portar a `0x0040A0B4` (encher a tela de
  tática), que é dívida da WTE-TASK-26 e destrava mais dois `aberto`

### CORR-WTE-082

- **Arquivo com problema:** `wte/src/impl/ep2002_mainform.mostrar_estrategiaClick.inc`
  (a tela abre sem ser enchida) e
  `wte/re/spec/estrategia.BitBtn3Click.md` (a seção *Bytes tocados*)
- **Sintoma:** a `0x0040A0B4`, 1.443 bytes, não tem port. Os componentes
  `bola`, `tirador` e `simbolo` ficam onde o `.lfm` os deixou em tempo de
  projeto, e o ` Accept` (`0x0040a660`) lê a POSIÇÃO DELES para converter em
  célula da malha. A gravação sairia plausível — formato e offset certos,
  conteúdo do formulário — e o diagnóstico apontaria para o escritor.
  Em cima disso, a spec do escritor ainda diz `**Evidência:** não medido` nos
  tamanhos da tática
- **Como foi detectado:** ao executar a terceira parte da CORR-WTE-081, que já
  a previa como pré-requisito fora do escopo. Medido em 2026-08-21 com o
  decodificador do `dump_auxiliares.py`: `0x0040a0b4` tem 1.443 bytes e dois
  chamadores, `estrategia.BitBtn1Click` e `MainForm.mostrar_estrategiaClick`,
  os dois `aberto` pelo mesmo motivo
- **Fix:** medir a segunda metade do `0x0040a660`, portar a `0x0040A0B4` numa
  unidade que nenhum dos dois formulários possua — a forma que a `wte_ficha`
  estreou —, e trocar o veredito dos dois chamadores. A conferência é de TELA
  (`compara_tela.sh`, três times), não de byte: a rotina não grava

### CORR-WTE-083

- **Arquivo com problema:** `wte/src/we2002_database.pas` (o laço de carga, que
  é gerado) e a tela do `MainForm`
- **Sintoma:** **dez** times carregam `flag_colours` como dezesseis zeros e o
  port desenha a bandeira **preta**: os oito CLASSIC (`teams[56..63]`) e dois
  clubes de ML (`ml_teams[5]` HIGHLANDS, `ml_teams[22]` EMILIA). Medido na tela
  em dois deles, um de cada família — 3.840 de 3.840 pixels diferentes do
  oráculo, com as cinco barras e o uniforme batendo em pixel na mesma corrida
- **Como foi detectado:** `compara_tela.sh 2 0 56` na conferência da
  WTE-TASK-31, mais o dump do `dump_estado.pas`, que mostra os oito com paleta
  zerada e `flag_shape` válido (o 56 tem `flag_shape = 4`, e `bandera4.bmp`
  existe)
- **Fix:** o laço nacional para em 55 — `for(i = 0;i < 56;i ++)` no
  `Database.cpp`, transpilado para `for i := 0 to 55` — e o bloco de ML é uma
  lista de índices que pula o 5 e o 22. O `ed.exe` não desenha bandeira e nunca
  precisou da cor; o editor do Obocaman lê, pela tabela de offsets em `.data`.
  Carregar os dez **fora** da camada transpilada, para o `compare_dumps.py`
  continuar idêntico

### CORR-WTE-084

- **Arquivo com problema:** `wte/src/wte_render2d.pas` (a âncora do desenho da
  bandeira) e/ou o próprio `wte.exe` (a largura da barra `equipe`)
- **Sintoma:** depois de a [CORR-WTE-083](/docs/tasks/CORR-WTE-083.md) dar cor
  às dez paletas, nove dos alcançáveis fecham em **0 de 3.840** e o combo 85
  não: a bandeira dele sai **2 px mais abaixo** (alinhada, a diferença cai de
  1.500/3.840 para 92/3.680) e o oráculo desenha a barra `equipe` com **76 px**,
  que não é `11 * v + 9` para nenhum `v` — o port desenha 75, que é o `v = 6`
  da camada de dados
- **Como foi detectado:** ao executar a CORR-WTE-083 e conferir os nove
  alcançáveis com o `compara_tela.sh`, em 2026-08-22. Duas corridas, mesmo
  resultado nas duas
- **Fix:** decidir de quem é cada uma antes de mexer em código. A barra tem
  cara de divergência deliberada — 76 px não é uma largura que o formato
  produza —, e nesse caso o lugar dela é a WTE-TASK-35. O deslocamento da
  bandeira precisa da âncora medida dos dois lados, sem quebrar os nove que já
  fecham em zero

### CORR-WTE-085

- **Arquivo com problema:** `docs/PLAN-WTE-LAZARUS.md:945` e `docs/tasks/progresso.md:122`
- **Sintoma:** as duas linhas dizem "duas das **seis** gravações". A conta subiu
  para nove na WTE-TASK-30 e para **dezessete** na WTE-TASK-31, e o plano diz os
  dois números — 17 na linha 929, 6 na 945
- **Como foi detectado:** `grep -n "seis gravações" docs/PLAN-WTE-LAZARUS.md
  docs/tasks/progresso.md` contra o `São **17**` do `wte/re/fase-4.md`, que é
  gerado pelo `check_fase4.py`
- **Fix:** trocar o número nas duas linhas vivas e, se sair barato, pôr a forma
  `seis|nove gravaç` no perímetro do `check_fase4.py`, como a fase 1 faz com os
  quatro números dela

### CORR-WTE-086

- **Arquivo com problema:** `docs/tasks/30-handlers-auxiliares.md`, seção
  "E a resposta dos dois é a mesma, medida"
- **Sintoma:** a task nomeia o `pabajoClick` como quem toca dados pelo
  `ficha_enlaza`. O `pabajoClick` não menciona vínculo na spec nem no `.inc`, e
  nenhum arquivo de `wte/src/` mostra o `ficha_enlaza`. Quem o alcança, pela
  única spec que o cita, é o `MainForm.mostrar_jugadorClick` — `aberto`. O
  veredito `trivial` dos handlers do `ficha_enlaza` continua certo: o `.dfm` só
  tem `ModalResult = 6/7`
- **Como foi detectado:** `grep -n "enlaza\|vincul" wte/re/spec/MainForm.pabajoClick.md`
  (vazio) e `grep -rn "enlaza" wte/src/impl/*.inc` (vazio), contra
  `wte/re/spec/MainForm.mostrar_jugadorClick.md:42`
- **Fix:** separar as duas metades na task — a do `movertodos` está medida e
  fica — e acrescentar o chamador à spec do `ficha_enlaza.FormShow`

### CORR-WTE-087

- **Arquivo com problema:** `docs/tasks/30-handlers-auxiliares.md`, lista de
  arquivos criados/modificados
- **Sintoma:** "12 `.inc` novos e 6 `.uses` tocados"; o commit `fb640cd` tem 11
  `.inc` novos, 1 `.uses` novo e 4 `.uses` modificados. O `colorearClick.inc`,
  citado na mesma frase, é ampliação — é ele que fecha os doze corpos
- **Como foi detectado:** `git show --diff-filter=A --name-only --format= fb640cd
  -- 'wte/src/impl/*'`, confirmado pela linha "Escrito à mão" do `fase-2.md` no
  mesmo commit: 83 → 94 arquivos
- **Fix:** trocar a contagem na task e desambiguar "doze corpos" na §4.4 do
  plano, sem mexer nos quatro números medidos

### CORR-WTE-088

- **Arquivo com problema:** `wte/tools/{golden_check,roteiro,golden_run_wte,compara_tela,diff_dirigido}.sh`
- **Sintoma:** nove comentários descrevem o ambiente corrente como `:99` — entre
  eles a guarda 2 do `golden_check.sh`, cujo código usa o `$DISPLAY` que a
  `roteiro_display` fixa em `:98`. Quatro outras ocorrências são registro
  histórico e ficam, como manda o CLAUDE.md
- **Como foi detectado:** `grep -n ':99' wte/tools/*.sh` contra
  `grep -n 'WTE_DISPLAY' wte/tools/*.sh`, nesta revisão
- **Fix:** trocar as nove, preservar as quatro históricas, e registrar a regra
  no `wte/tools/README.md`

### CORR-WTE-089

- **Arquivo com problema:** `wte/re/spec/MainForm.lista_jugadores_1Change.md`,
  `MainForm.lista_equipos_2Change.md`, `MainForm.parribaClick.md`
- **Sintoma:** os três estavam `aberto` pela frase "nada exercita o corpo", e os
  três disparam dentro de gates golden verdes — o `lista_jugadores_1Change` em
  **quatro** (`golden-09`, `-10`, `-11`, `-15`), o `lista_equipos_2Change` com
  **64** disparos em dois deles
- **Como foi detectado:** rodando o lado port dos 16 roteiros com par pelo
  `golden_run_laz.sh` e lendo o `port-trace.log` que ele já escreve; a razão
  antiga tinha sido medida só com `compara_tela.sh`, que é régua de pixel e não
  clica a lista de jogadores
- **Fix:** `wte/tools/cobertura_gate.py` mede e versiona a cobertura em
  `wte/re/fase-4-cobertura.tsv`, com quatro guardas — a principal sendo que spec
  que cita o TSV como evidência tem de ter linha nele. Os três passam a
  `implementado`; o `mostrar_jugadorClick` ganha a evidência do ramo titular e
  segue `aberto` pelo do reserva

### CORR-WTE-090

- **Arquivo com problema:** `wte/re/spec/jugador.flechasapaClick.md`,
  `estrategia.ComboBoxDrawItem.md`, `MainForm.boton_dialogo_weClick.md`
- **Sintoma:** os três estavam `aberto` sem pergunta em aberto — o primeiro
  esperando decisão tomada em 2026-08-18 (CORR-WTE-063), o segundo esperando a
  WTE-TASK-37, que é fase 6 e depende da 34, que depende da 31, que exige nenhum
  `aberto`; o terceiro com as duas razões antigas já caídas
- **Como foi detectado:** lendo a razão de cada `aberto` restante contra o
  estado da árvore, na quarta passagem da WTE-TASK-31
- **Fix:** `divergencia deliberada` nos dois que são desvio consciente e
  `nao portado` com justificativa de **escopo** no terceiro. O ciclo fica
  desfeito sem antecipar a decisão da 37. De quebra, a guarda do
  `cobertura_gate.py` virou bidirecional: ela recusou a prosa nova do
  `boton_dialogo_weClick`, que cita o TSV para dizer que dá zero linha, e a
  correção foi conferir também o sentido negativo em vez de afrouxar

### CORR-WTE-091

- **Arquivo com problema:** `wte/src/impl/ep2002_mainform.aux.inc` (a
  `PreencheFicha` presa lá), `wte/re/spec/jugador.BitBtn1Click.md`
- **Sintoma:** o `Original ` da ficha tem seis bytes no original e não tinha
  corpo no port; o `ep2002_jugador` não alcançava a `PreencheFicha`, porque
  `.aux.inc` é incluído na implementação e o `uses` gerado sai na interface
- **Como foi detectado:** lendo a razão de cada `aberto` restante na quarta
  passagem da WTE-TASK-31; a própria spec já nomeava a saída
- **Fix:** a rotina desceu para a `wte_ficha` (unidade neutra, como a
  CORR-WTE-081 e a -082 fizeram antes), o corpo virou uma chamada, e o gate são
  **dois** roteiros que diferem por um clique — sem o par, clicar `Original `
  sem ter editado nada passaria com o corpo vazio. Medido: `golden-18` grava
  `0xc0` no byte de camisa, `golden-19` grava `0x80`, que é o valor da ROM
  intocada. De quebra fechou o `casilla_dorsalKeyPress`, que o mesmo par
  exercita

### CORR-WTE-092

- **Arquivo com problema:** `wte/tools/roteiro.sh` (dialeto sem `mousedown`),
  `wte/re/spec/estrategia.bolaMouseDown.md`, `MainForm.mostrar_jugadorClick.md`
- **Sintoma:** dois handlers sem estímulo nenhum — o ramo do reserva do
  `mostrar_jugadorClick` e o arrasto de bola, que clique não exercita
- **Como foi detectado:** pela cobertura medida na CORR-WTE-089, que mostrou
  zero disparo dos dois em todos os roteiros
- **Fix:** verbo `arrasta` no `roteiro.sh` (com três passos intermediários,
  porque salto único não gera `OnMouseMove` em gtk2) e os roteiros
  `golden-20-ficha-reserva` e `golden-21-arrasto`. **Cada estímulo foi
  confrontado com uma corrida sem estímulo** — sem isso o arrasto teria passado
  duas vezes medindo nada, uma delas com o `bolaMouseDown` disparando e a bola
  voltando ao lugar por ter sido solta fora da própria zona

### CORR-WTE-093

- **Arquivo com problema:** `wte/re/spec/estrategia.FormCreate.md` (quatro laços
  sem leitura), `MainForm.boton_dialogo_texClick.md` (dono fechou sem ele)
- **Sintoma:** os dois últimos `aberto` fora de preço, ambos sem corpo Pascal
- **Como foi detectado:** na quarta passagem da WTE-TASK-31, lendo a razão de
  cada `aberto` restante
- **Fix:** os quatro laços foram lidos por `objdump` e são a montagem da tabela
  de formações — 18 registros de 44 bytes, quatro colunas de 11 intercaladas —,
  que o `dump_formacoes.py` já gera. **A leitura levou a decidir não escrever
  código**, e o corpo faz só o que sobra. O slot virtual `0xcc` do fim foi
  medido no VMT de `TListBox` (`SetItemIndex`), não suposto. O diálogo de
  textura virou `divergencia deliberada` pela troca de `FILE*` por caminho, que
  o `we2002_estado` já documentava

### CORR-WTE-094

- **Arquivo com problema:** `docs/tasks/32-preco-do-jogador.md`
- **Sintoma:** a task abre afirmando que o `ed.exe` não calcula preço, e ele
  calcula — `CalcolaCostoGiocatore` em `legacy/mfc/edDlg.cpp:7703`, com laço de
  time inteiro em `:7948` e handler no message map em `:1286`
- **Como foi detectado:** ao levantar o que a WTE-TASK-32 vai precisar, na
  quarta passagem da WTE-TASK-31
- **Fix:** a premissa vira "o `ed.exe` não **oferece** preço" — `CMD_CALCCOSTI`
  está no `resource.h` e não no `ed.rc`, mesmo caso do `MainForm.Button2Click`.
  E fica registrado que a task ganha oráculo B: `ComputePlayerCost`, já em
  Pascal nesta árvore. Sem presumir fórmula igual — a do `ed.exe` é `double`
  com `ceil`, a do Obocaman é inteira; o valor dele é desenhar a amostragem,
  porque exemplifica os três riscos que a própria task lista

### CORR-WTE-095

- **Arquivo com problema:** `wte/re/spec/MainForm.base_teamClick.md` (o achado
  medido sem causa), `wte/src/impl/ep2002_mainform.base_teamClick.inc`
- **Sintoma:** o `base_teamClick` do oráculo grava preço para 22 dos 23 slots; o
  slot 22 fica com o valor de fábrica em todos os seis times medidos, mesmo
  quando tem a mesma soma e a mesma posição do slot 21
- **Como foi detectado:** ao construir a tabela de verdade da WTE-TASK-32 —
  cada time dava exatamente uma divergência, e era sempre o slot 22
- **Fix:** ainda não. O port reproduz a medida (`ULTIMO_SLOT_PRECADO = 21`) para
  o gate poder ser byte a byte, e esta CORR estabelece a causa. As quatro
  perguntas baratas estão no arquivo, na ordem de responder

### CORR-WTE-096

- **Arquivo com problema:** `wte/tools/check_fase4.py` (o `GOLDEN_DE`) e, por
  tabela, `wte/re/fase-4.md`
- **Sintoma:** `"MainForm.base_teamClick"` aparece duas vezes no literal — uma
  com `("golden-22-precos",)`, outra, resíduo de quando o handler era `aberto`,
  com `()`. Em Python a última vence, então o gate criado pela WTE-TASK-32 é
  inerte e a tabela gerada publica `**nenhum**` para ele. A guarda que deveria
  abortar não abortou porque a chave existe; vazio foi renderizado, não recusado
- **Como foi detectado:** `ast.parse` sobre o fonte nesta revisão — 18 chaves,
  17 únicas —, contra as três corridas do `golden-22-precos` (controle, golden e
  positivo detectando o byte plantado em `OFS_COST_NATIONAL+46`)
- **Fix:** apagar a entrada velha e pôr duas guardas no gerador: recusar chave
  repetida (lendo o próprio fonte com `ast`) e recusar gate vazio para escritor
  `implementado`, cada uma com caso plantado no `test_check_fase4.py`

### CORR-WTE-097

- **Arquivo com problema:** `wte/src/impl/ep2002_mainform.base_teamClick.inc`
- **Sintoma:** o cabeçalho que justifica `ULTIMO_SLOT_PRECADO = 21` diz "medido
  em dois times da ROM japonesa (2 e 9)". A `preco.md`, a spec, o
  `check_preco.py` e a CORR-WTE-095 dizem seis (0, 2, 9, 17, 30, 48), e o
  `preco.tsv` os mostra. É a evidência mais fraca no arquivo onde ela mais pesa
- **Como foi detectado:** `grep -rn "dois times\|seis times"` sobre os quatro
  sítios, e `awk` sobre o `preco.tsv` — seis times medidos, zero linhas de slot
  22 marcadas como medidas
- **Fix:** trocar por seis, com a lista dos índices, mantendo o argumento do
  time 9 (slots 21 e 22 com mesma soma e mesma posição, só o 21 gravado)

### CORR-WTE-098

- **Arquivo com problema:** `docs/PLAN-WTE-LAZARUS.md`, §5.1
- **Sintoma:** o plano descreve a feature de preço como um handler só
  (`etiqprecioClick`) e afirma que ela **não precisa de golden test de imagem**.
  A outra metade (`MainForm.base_teamClick`) grava um byte por jogador e tem o
  `golden-22-precos` registrado como gate; o corpo da WTE-TASK-32 já corrigiu a
  premissa, o plano não
- **Como foi detectado:** leitura da §5.1 contra o `GOLDEN_DE` do
  `check_fase4.py` e o `fase-4-golden.tsv`, mais as três corridas do gate nesta
  revisão — as duas boas mudam 22 bytes em `3067450..3067471` dos dois lados
- **Fix:** nomear as duas metades, trocar a frase pela régua dupla (tabela de
  verdade para a fórmula, byte para o time), e ajustar o "Pronto quando" da
  Fase 5

### CORR-WTE-099

- **Arquivo com problema:** `docs/tasks/32-preco-do-jogador.md`, lista de
  arquivos
- **Sintoma:** o commit `c566455` tocou 31 arquivos e a lista cobre trinta;
  falta o `.gitignore`, que ganhou as regras dos binários compilados de
  `wte/tests/`. A mudança é correta e bem comentada — o que falta é o registro
- **Como foi detectado:** `git show --stat --format= c566455` contra a lista do
  Log, nesta revisão
- **Fix:** acrescentar a linha aos modificados; e, se valer fechar a porta, o
  `01-executar.md` passar a conferir a lista contra `git show --stat` ao fechar
  a task — é a terceira omissão desse tipo (CORR-WTE-078, CORR-WTE-087)

### CORR-WTE-100

- **Arquivo com problema:** `wte/src/we2002_preco.pas:138`
- **Sintoma:** o comentário do `PrecoDaSoma` cita `` `{$Q-}` `` entre crases, e
  crase não é sintaxe de Pascal. O `{` abre nível 2 de comentário — o único
  `Warning` do build — e, pior, a diretiva **é processada**: liga `Q-` antes do
  `{$PUSH}` da linha seguinte, então o `{$POP}` da 149 restaura para um estado
  que já tinha `Q-` e o `PrecoDoJogador` roda sem verificação de overflow
- **Como foi detectado:** ao medir a linha de base do `lazbuild` para a
  CORR-WTE-097, e investigado a pedido do usuário depois da CORR-WTE-095. Três
  medições: `-Co` num programa mínimo mostra que a diretiva citada vale; o
  mesmo com `{$PUSH}`/`{$POP}` mostra que o `POP` não restaura; e os modos
  `objfpc`/`fpc`/`delphi` separam aviso de `Fatal: illegal character`
- **Fix:** `` `$Q-` `` em vez de `` `{$Q-}` ``, dois caracteres. O
  `{$PUSH}{$Q-}{$R-}` da linha 140 fica como está — aquele é o guard de verdade

> **Este registro de abertura afirma duas coisas que a execução refutou** no
> mesmo dia: a diretiva citada **não** é processada, e o `{$POP}` **restaura**
> normalmente. O instrumento que as produziu usava `LongInt`, que em x86-64 não
> distingue `{$Q+}` de `{$Q-}`. O que sobra de real é o warning e a fragilidade
> em `{$mode delphi}` — ver o Log da
> [CORR-WTE-100](/docs/tasks/CORR-WTE-100.md).

### CORR-WTE-101

- **Arquivo com problema:** `wte/re/spec/GABARITO.md`, `wte/tools/check_fase4.py`
  e, por tabela, `wte/re/fase-4.md`
- **Sintoma:** três sítios dizem "seis seções obrigatórias"; o `SECOES` do
  `spec_index.py` tem cinco, e o próprio gabarito lista cinco mais uma `## Notas`
  declarada opcional. A frase gerada erra ainda uma segunda vez: apresenta as
  481 linhas `**Evidência:**` como se fossem todas, e são as das cinco seções
  cobradas — no arquivo há 525, com 44 em `## Notas`, `## Justificativa` e
  `## Como o veredito fechou`
- **Como foi detectado:** `len(S.SECOES)` = 5 contra o `grep` das três frases, e
  um script que separa evidência dentro/fora das seções cobradas: 481 + 44 = 525
- **Fix:** cinco no gabarito e no gerador; a frase do total passa a dizer que
  conta só as seções cobradas, e a guarda amarra a prosa a `len(S.SECOES)` em
  vez de literal

### CORR-WTE-102

- **Arquivo com problema:** `docs/PLAN-WTE-LAZARUS.md:943`,
  `docs/tasks/progresso.md:445`, `wte/tools/check_fase4.py:28` e `:95`
- **Sintoma:** a receita de como as dezessete gravações foram derivadas diz
  "lendo a seção `## Bytes tocados` das **94** specs". Eram 94 na primeira
  passagem da WTE-TASK-31; a WTE-TASK-32 escreveu as duas de preço e o índice
  fecha em 96. O resultado não muda — as duas novas declaram `Nenhum` —, a
  receita é que não confere mais. No plano a frase está quatorze linhas abaixo
  de "96 dos 96"
- **Como foi detectado:** `grep -rn "94 specs"` contra
  `spec_index.py --check` (96 com spec) nesta revisão
- **Fix:** 96 nos quatro sítios vivos, tirando o número da linha 95 do gerador,
  que fala das formas de escrever "não grava" e não da população; o Log da
  primeira passagem fica como está, que é registro histórico

### CORR-WTE-103

- **Arquivo com problema:** `wte/tools/check_fase4.py` (e o gerado `fase-4.md`)
- **Sintoma:** a linha em branco que fecha o bloco "N dos M têm arquivo de spec"
  é emitida dentro do `if m["sem_spec"]`. Com zero — o estado de fechamento — o
  título `## Os que continuam aberto` sai colado no parágrafo, única junção do
  arquivo sem separação
- **Como foi detectado:** `sed -n '38,42p' wte/re/fase-4.md | cat -A` nesta
  revisão; é o terceiro caso da mesma família que a quinta passagem foi caçar
- **Fix:** mover o `a("")` para fora do `if`, e um caso de teste que recuse
  `^## ` logo depois de linha não vazia na saída do gerador — pega os três de
  uma vez

### CORR-WTE-104

- **Arquivo com problema:** `wte/tests/roteiros/golden-24-gravacao-dupla{,.port}.txt`
- **Sintoma:** o roteiro existe para medir se a segunda gravação reproduz a
  troca de `cobrador[0]`/`cobrador[1]`, e grava no **time 2**, onde os seis
  bytes de cobrador são `[7, 7, 8, 7, 7, 8]` — os dois primeiros iguais, a
  troca é a identidade. O roteiro passa exatamente igual com vaivém e sem ele.
  O terceiro ponto (uma gravação × duas), que a task deixou pendente, foi
  rodado nesta revisão e deu **0 bytes de diferença**, com as duas imagens
  mudando 11.966 bytes contra a ROM virgem — mas o zero é indecidível pelo
  motivo acima
- **Como foi detectado:** `golden-17-tatica` e `golden-24-gravacao-dupla` em
  `--modo controle --manter`, `cmp -l` entre as duas imagens, e leitura dos seis
  bytes em 2329068 nas três imagens (virgem, uma gravação, duas)
- **Fix:** trocar para um time com `cobrador[0] != cobrador[1]` — há **41** na
  ROM japonesa, e o 5 (`[9, 5, …]`, em 2329086) custa três `Down` a mais e
  nenhuma coordenada nova —, rodar o par de novo e **escrever o resultado** no
  `golden.md`, seja ele zero ou não. O terceiro ponto do
  `golden-23-multiplas-edicoes` foi conferido na mesma revisão e **passa**: as
  duas edições aparecem, a barra em 2328195 e os dez blocos de nome

### CORR-WTE-105

- **Arquivo com problema:** `docs/tasks/35-divergencias-deliberadas.md`
- **Sintoma:** a WTE-TASK-34 fecha encaminhando a pendência do vaivém *"para a
  WTE-TASK-35, que é quem registra divergência deliberada com evidência"*, e a
  35 não tem a entrada: `grep -c "vaivém|cobrador|OFS_KICKER|idempot"` devolve
  **0** no arquivo dela, cuja seção de candidatas tem nove entradas e nenhuma é
  esta. A 35 está `⬜ Pendente` e é a próxima da fase
- **Como foi detectado:** `grep` cruzado entre as duas tasks nesta revisão
- **Fix:** acrescentar a candidata à 35, dizendo que ela espera **medição** e
  não decisão, com a CORR-WTE-104 como pré-requisito; e, se valer, o
  `01-executar.md` passar a exigir que "encaminhado para a NN" tenha linha na NN

### CORR-WTE-106

- **Arquivo com problema:** `wte/tools/check_divergencias.py` — não tem
  `test_check_divergencias.py`
- **Sintoma:** o critério da task afirma *"mecanizado nos dois sentidos, com as
  três recusas vistas"*, e nada no repositório volta a exercitá-las. É a única
  guarda de **recusa** sem par de teste: os irmãos todos têm
  (`check_fase1/2/3/4`, `check_golden`, `check_preco`, `check_edicao`,
  `check_glifos_disabled`, `cobertura_gate`, `gravacao_controle`,
  `spec_index`), e as nove ferramentas sem teste são medidoras do `.exe`
- **Como foi detectado:** `ls` do arquivo ausente, e as quatro recusas
  plantadas num espelho da árvore em `/tmp` nesta revisão — isenção que some,
  seção que some, retirada que volta, roteiro com `conhecida:` — **as quatro
  saem com código 2**, então o gate funciona e o que falta é mantê-lo assim
- **Fix:** escrever os quatro casos no molde do `test_check_fase4.py`, mais o
  caso do estado de hoje e o do casamento por aspas do `RETIRADAS` (o
  `compara_tela.py` cita `pendente_32` na prosa e passa só porque a citação usa
  crase)

### CORR-WTE-107

- **Arquivo com problema:** `docs/tasks/35-divergencias-deliberadas.md`, lista
  de arquivos
- **Sintoma:** o commit `2e70784` tocou nove arquivos e a lista nomeia oito. O
  que falta é `docs/tasks/36-buffers-e-truncamento.md`, o **repasse** — o único
  dos nove que não é ferramenta, e o que aplica a lição da CORR-WTE-105
- **Como foi detectado:** `git show --stat --format= 2e70784` contra a lista,
  nesta revisão
- **Fix:** acrescentar a linha, dizendo o que o repasse escreve na 36; é a
  quarta omissão desta classe (CORR-WTE-078, -087, -099)

### CORR-WTE-108

- **Arquivo com problema:** `docs/tasks/35-divergencias-deliberadas.md`, linha 260
- **Sintoma:** a candidata do vaivém fecha com *"o plano é o que falta
  conferir"*, e o plano nunca afirmou o vaivém — `grep -c` de
  `idempot|cobrador|OFS_KICKER|vaivém` no `PLAN-WTE-LAZARUS.md` devolve **0**.
  A frase manda procurar texto que não existe, que é o defeito que a própria
  task nomeia ao explicar por que removeu a isenção `pendente_32` em vez de
  registrá-la. O `divergencias.md` está correto
- **Como foi detectado:** `grep` no plano nesta revisão, cruzado com o
  `golden.md` (linha 98, já diz `ed.exe`) e com o enunciado da WTE-TASK-34
- **Fix:** escrever o resultado da conferência no lugar da pendência —
  resultado negativo escrito poupa a próxima busca

### CORR-WTE-110

- **Arquivo com problema:** `wte/tests/test_bordas.pas`
- **Sintoma:** o critério diz *"os quatro casos de borda testados **por
  campo**"*, e os dois grupos que medem borda de campo tocam só `t.names[0]` e
  `t.names[1]`. Ficam de fora `abbreviations` (4 B para limite 3, a menor folga
  do inventário, e vizinho do `kanji_name` no `TTeam`), `Player.name` (11 B) e o
  `kanji_name` como destino. A parte estrutural — o limite caber no vetor — está
  coberta campo a campo pelo gerador; o comportamento, não
- **Como foi detectado:** compilado e rodado o `test_bordas.pas` nesta revisão
  (`10/10 conferencias de borda passaram`) e grepados os vetores que ele toca
- **Fix:** repetir os grupos 1 e 2 nos outros três — o corpo já é
  parametrizável —, começando pelo `abbreviations`; ou escrever no critério que
  a medição é por classe, com a razão

### CORR-WTE-111

- **Arquivo com problema:** `wte/tools/dump_buffers.py`, tabela `CAMPOS`
- **Sintoma:** a chave `faixa` existe nos quatro campos de texto e **nenhum
  código a lê** — os limites publicados saem de `lim_min`/`lim_max`, medidos das
  tabelas por time. E dois valores contradizem o medido: `edit_nombre1` declara
  `(5, 19)` contra **5..13**, `edit_nombre2` declara `(5, 19)` contra **7..19**.
  A mesma chave é **viva** em `NUMERICOS`, o que torna a confusão provável
- **Como foi detectado:** `grep` por consumidores (nenhum) e confronto
  medido × declarado pelo próprio módulo, nesta revisão
- **Fix:** apagar a chave, ou renomeá-la para `esperado` e **conferi-la**,
  corrigindo antes os dois valores; mais um caso que recuse chave que ninguém lê

### CORR-WTE-112

- **Arquivo com problema:** `wte/tools/dump_buffers.py` e o gerado
  `wte/re/buffers.md`
- **Sintoma:** o conjunto de caracteres aceito por campo é declarado à mão e
  publicado num arquivo cujo banner diz *"todo número daqui saiu do script"*,
  sem nunca ser conferido contra o `KeyPress`. O irmão dele na mesma tabela — o
  `predicado` de faixa dos numéricos — é lido do `.inc` e **aborta** se sumir
- **Como foi detectado:** `grep -n "filtro"` no gerador: todas as ocorrências
  são declaração, repasse e impressão; nenhuma abre um `.inc`
- **Fix:** dar ao `filtro` a forma do `predicado` — trecho literal do handler,
  conferido por substring, com a recusa plantada em `test_check_bordas.py`

### CORR-WTE-113

- **Arquivo com problema:** `wte/tools/golden_suite.sh`, o truncamento do TSV
- **Sintoma:** o script reescreve o cabeçalho do `golden.tsv` sempre que
  `--retomar` não é passado, **antes de qualquer corrida** — então `--roteiro`
  não é filtro, é substituição. Aconteceu na WTE-TASK-37: as 92 corridas da
  WTE-TASK-34 (1,8 h de relógio) foram apagadas ao registrar o
  `golden-25-retorno`, recuperadas à mão do `git show HEAD:`, e o Log fechou com
  *"vale um item para quem mexer na bateria de novo"* — item que não foi aberto
- **Como foi detectado:** reproduzido nesta revisão sobre uma **cópia** do TSV,
  com `--saida` apontado para ela e a corrida interrompida em 6 s: **97 linhas
  viraram 1**, o cabeçalho, sem nenhuma corrida ter começado
- **Fix:** truncar só quando a corrida é a bateria inteira (sem `--roteiro` e
  com `--rom ambas`), substituindo a linha do trio `(roteiro, rom, modo)` no
  `registra()`; ou, no mínimo, recusar `--roteiro` sem `--retomar`. Mais o teste
  que exige que as linhas sobrevivam

### CORR-WTE-114

- **Arquivo com problema:** `wte/re/divergencias.md` (ausências) e
  `docs/tasks/35-divergencias-deliberadas.md` (onde as três foram parar)
- **Sintoma:** a WTE-TASK-37 escreveu três candidatas de divergência numa seção
  nova da WTE-TASK-35, que está `concluído` — e o registro que a 35 produziu não
  tem nenhuma das três. A primeira (`ficha_warning` não é levantado pelo port,
  que aplica os remendos de arranque sem perguntar) é **divergência deliberada
  em produção** e se declara *"ainda sem entrada aqui"*. As outras duas são o
  `ficha_enlaza` sem chamador (rota não portada, não divergência escolhida) e o
  `help_team` desabilitado pintando fundo próprio no GTK2
- **Como foi detectado:** `grep -c "ficha_warning\|ficha_enlaza\|help_team"` no
  registro devolve **0**, com o `check_divergencias.py --check` verde — ele
  confere exceção de ferramenta contra entrada, e estas três são comportamento
- **Fix:** abrir as entradas da 1 e da 3 com os seis campos, mandar a 2 para o
  veredito do `mostrar_jugadorClick` e para a seção "O que NÃO entra aqui", e
  transformar a seção da 35 em índice; guarda opcional recusando a frase
  "sem entrada aqui" quando o alvo não tiver seção no registro

### CORR-WTE-115

- **Arquivo com problema:** falta `wte/tools/test_check_carregado.py`
- **Sintoma:** dos dois conferidores criados na mesma passagem, só o
  `check_retorno.py` ganhou par de teste. O `check_carregado.py` implementa a
  recusa mais fácil de quebrar sem ninguém ver — a da moldura 6×32 do Wine, que
  o Log da task registra como achado — e nada volta a exercitá-la
- **Como foi detectado:** `ls` do arquivo ausente, e a recusa plantada num
  espelho em `/tmp` nesta revisão: uma captura encolhida em **um** pixel faz o
  `--check` sair com código 2 e nomear as duas medidas
- **Fix:** escrever o teste no molde do `test_check_retorno.py`, com a captura
  impossível, os dois casos bons (cliente e cliente + moldura, com deslocamento
  `(0,0)` e `(3,29)`) e o formulário sem `ClientWidth` nem `Width`
