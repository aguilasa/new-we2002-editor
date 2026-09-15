# Correções — visualizador 3D da aparência do jogador

Correções abertas pelo `/revisar` sobre as tasks deste ciclo. O andamento das
**tarefas** fica em [`progresso.md`](/docs/tasks/looks/progresso.md).

**O prefixo deste pool é `CORR-LOOKS-`**, com numeração contínua a partir de
`001`. O pool é único dentro do ciclo, e não se cruza com o de nenhuma outra
pasta — o ciclo de PES2 tem o seu em
[`/docs/tasks/correcoes-progresso.md`](/docs/tasks/correcoes-progresso.md), o
do port do `.mcr` em
[`/docs/tasks/port-mcr/correcoes-progresso.md`](/docs/tasks/port-mcr/correcoes-progresso.md),
e o ciclo arquivado, o dele em
[`/docs/tasks/concluidos/correcoes-progresso.md`](/docs/tasks/concluidos/correcoes-progresso.md).

## Resumo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
| -- | -------------- | ------ | ----------- | ------ | ------------ |
| [CORR-LOOKS-001](/docs/tasks/looks/CORR-LOOKS-001.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | A raiz do Superpack tem treze pastas de jogo, não catorze | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-002](/docs/tasks/looks/CORR-LOOKS-002.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | O comentário do `.gitignore` guarda o número que a própria task derrubou | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-003](/docs/tasks/looks/CORR-LOOKS-003.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | `superpack_count.py` descarta entrada ilegível em silêncio | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-004](/docs/tasks/looks/CORR-LOOKS-004.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | A LOOKS-TASK-18 se contradiz sobre as 50 tuplas em dois bullets seguidos | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-005](/docs/tasks/looks/CORR-LOOKS-005.md) | [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | A guarda dos dois discos não tem quem a chame, e nada obriga a 03 a chamá-la | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-006](/docs/tasks/looks/CORR-LOOKS-006.md) | [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | A recusa do `/SELECT.BIN` sai como `digest mismatch` pelado | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-007](/docs/tasks/looks/CORR-LOOKS-007.md) | [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | O `layout.py` diz que não faz I/O, e faz | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-008](/docs/tasks/looks/CORR-LOOKS-008.md) | [LOOKS-TASK-03](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) | O `BASE` é derivável e nunca é derivado — `require_base()` não tem chamador nenhum | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-009](/docs/tasks/looks/CORR-LOOKS-009.md) | [LOOKS-TASK-03](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) | A varredura da regra 1 não tem caso vermelho, e nada diz quanto ela varreu | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-010](/docs/tasks/looks/CORR-LOOKS-010.md) | [LOOKS-TASK-04](/docs/tasks/looks/04-formato-de-secao.md) | O `EDT_MOD.BIN` tem 20 seções e duas listas de onze — a varredura começou a 15.704 | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-011](/docs/tasks/looks/CORR-LOOKS-011.md) | [LOOKS-TASK-04](/docs/tasks/looks/04-formato-de-secao.md) | O `sweep_addresses()` guarda duas regex mortas com o nome das vivas | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-012](/docs/tasks/looks/CORR-LOOKS-012.md) | [LOOKS-TASK-05](/docs/tasks/looks/05-arquivos-de-modelo.md) | O perfil promete o `looks_image` desde a 05, e `ctest -R looks` sai 0 sem achar teste | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-013](/docs/tasks/looks/CORR-LOOKS-013.md) | [LOOKS-TASK-05](/docs/tasks/looks/05-arquivos-de-modelo.md) | O cabeçalho do `MODEL.BIN` foi descrito por metade — duas corridas, e a lista 0 declara o 1816 | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-014](/docs/tasks/looks/CORR-LOOKS-014.md) | [LOOKS-TASK-05](/docs/tasks/looks/05-arquivos-de-modelo.md) | O título da LOOKS-TASK-05 ainda diz onze seções; a tabela já diz vinte | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-015](/docs/tasks/looks/CORR-LOOKS-015.md) | [LOOKS-TASK-06](/docs/tasks/looks/06-harness-controles-e-selftest.md) | O gate obrigatório não é alcançável por `ctest` nesta máquina, e pedir por ele sai 0 | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-016](/docs/tasks/looks/CORR-LOOKS-016.md) | [LOOKS-TASK-06](/docs/tasks/looks/06-harness-controles-e-selftest.md) | Os dois alvos de `looks` ficaram fora do `if(Python3_FOUND)` que guarda os outros oito | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-017](/docs/tasks/looks/CORR-LOOKS-017.md) | [LOOKS-TASK-07](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md) | Sem `WE2002_LOOKS_IMAGE` o `--check-live` sobe o emulador e morre num traceback, em vez de pular com 77 | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-018](/docs/tasks/looks/CORR-LOOKS-018.md) | [LOOKS-TASK-08](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) | A palavra de página declara a profundidade da CLUT, e 1.039 das 2.841 primitivas dizem 8 bits | Alta | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-019](/docs/tasks/looks/CORR-LOOKS-019.md) | [LOOKS-TASK-08](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) | O `--tmds` promete dizer se algum campo move um TMD e não pergunta: a metade negativa do veredito não sai de comando | Média | [ ] pendente | — |

**Legenda de status:** `[ ] pendente` · `[~] em andamento` · `[x] concluída`

**Criticidade** é sobre o efeito, não sobre o tamanho do conserto:

- **Alta** — a task entregou algo que mede errado, ou um gate que passa sem
  medir. Neste ciclo isso inclui qualquer guarda que fique verde lendo o disco
  errado, porque esse erro não tem sintoma.
- **Média** — o resultado está certo mas a evidência não sustenta, ou o código
  viola uma das três regras de desenho.
- **Baixa** — documentação, número que não reproduz, link ou nome.

## Checklist

- [x] CORR-LOOKS-001 — treze pastas na raiz do Superpack, não catorze
- [x] CORR-LOOKS-002 — o `.gitignore` ainda descreve a raiz com o número da subpasta
- [x] CORR-LOOKS-003 — `superpack_count.py` tem de falhar alto no que não conseguiu ler
- [x] CORR-LOOKS-004 — o primeiro bullet da LOOKS-TASK-18 desmente o terceiro
- [x] CORR-LOOKS-005 — nada obriga o `iso_source.py` a passar pela guarda
- [x] CORR-LOOKS-006 — o `/SELECT.BIN` recusa sem dizer que o disco é o inglês
- [x] CORR-LOOKS-007 — o docstring do `layout.py` promete o que a dívida da 03 ainda deve
- [x] CORR-LOOKS-008 — nenhum comando redeixa o `BASE` a partir dos arquivos reais
- [x] CORR-LOOKS-009 — o `--sweep` só foi visto verde, e não diz quanto varreu
- [x] CORR-LOOKS-010 — a varredura do `EDT_MOD.BIN` leu 11 de 20 seções
- [x] CORR-LOOKS-011 — duas regex mortas no `sweep_addresses()`, com o nome das vivas
- [x] CORR-LOOKS-012 — não existe alvo `looks_image`, e pedir por ele sai verde
- [x] CORR-LOOKS-013 — 12 listas miram 104 e 4 miram 232; a lista de 72 declara o 1816
- [x] CORR-LOOKS-014 — título da 05 no frontmatter diz 11, a tabela diz 20
- [x] CORR-LOOKS-015 — `ctest -R looks` não acha os alvos em build nenhum, e sai 0
- [x] CORR-LOOKS-016 — os dois alvos de `looks` estão fora da guarda de Python
- [x] CORR-LOOKS-017 — o quarto pré-requisito do `--check-live` não tem caminho de skip
- [x] CORR-LOOKS-018 — 1.039 de 2.841 primitivas amostram em CLUT de 8 bits, e o plano só diz 4
- [ ] CORR-LOOKS-019 — nenhum comando cruza o resíduo do `--fields` com o mapa de TMDs

## Detalhes por correção

### CORR-LOOKS-001

- **Arquivo com problema:** `NOTICE.md`, `docs/PLAN-LOOKS-PY.md` §2 e o Log da
  `01-base-legal-e-linhagem.md`
- **Sintoma:** os três dizem "catorze pastas de jogo" na raiz do Superpack; são
  treze, e a frase do plano lista treze nomes logo em seguida
- **Como foi detectado:** `python tools/looks/superpack_count.py
  "C:/games/we2002/Superpackv6"` imprime catorze **linhas**, das quais uma é o
  `Cronologia We-Pes-IssPro.htm`; um `os.listdir` separando por tipo dá 13 e 1
- **Fix:** trocar o número nos três, dizendo "pastas" e não "jogos" — as três
  `We2000 *` são um jogo só

### CORR-LOOKS-002

- **Arquivo com problema:** `.gitignore`, comentário da entrada `/Superpackv6/`
- **Sintoma:** o comentário descreve a coletânea inteira como "4,2 GB, 28.720
  arquivos", que é a subpasta `We2002\` — exatamente o erro que esta task
  corrigiu no plano e no `NOTICE.md`, no mesmo commit
- **Como foi detectado:** confronto das três descrições do Superpack no
  repositório contra a saída do `superpack_count.py` (4,50 GiB, 31.790)
- **Fix:** `4,5 GiB, 31.790 arquivos` no comentário, com meia linha dizendo que
  28.720 deles estão em `We2002\`

### CORR-LOOKS-003

- **Arquivo com problema:** `tools/looks/superpack_count.py`
- **Sintoma:** arquivo ilegível some da conta (`except OSError: continue`),
  entrada de topo ilegível some da repartição (`except OSError: pass`) e
  subpasta sem permissão some inteira, porque `os.walk` roda com o
  `onerror=None` de default. A saída sai somada e com cara de completa
- **Como foi detectado:** leitura dirigida pela pergunta que o `02-revisar.md`
  faz de toda ferramenta — falha alto ou emite parcial? — e por
  `os.walk` sobre raiz ilegível devolver zero entrada sem erro. O número de
  hoje está certo: a revisão o reproduziu byte a byte
- **Fix:** contar o que foi pulado, imprimir `skipped: N`, sair != 0 quando
  `N > 0`, e um caso vermelho no `self_check()` exigindo `skipped == 1`

### CORR-LOOKS-004

- **Arquivo com problema:** `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md`
- **Sintoma:** o primeiro bullet do Contexto diz que os 50 JPGs são "nomeados
  pela tupla exata" e o terceiro diz que são 49 — o achado entrou por bullet
  novo sem corrigir a frase que ele desmente
- **Como foi detectado:** leitura do arquivo contra a §5.4 do plano, que a
  mesma execução corrigiu certo, mais a contagem da pasta (50 `.jpg`, o
  primeiro em ordem sendo `0.jpg`)
- **Fix:** reescrever o primeiro bullet na forma da §5.4

### CORR-LOOKS-005

- **Arquivo com problema:** `docs/tasks/looks/03-fonte-de-disco-e-layout.md` e
  a §4.5 do plano
- **Sintoma:** `layout.require()` recusa certo, mas o único chamador é o
  `_check_discs()` — que a 03 tem por critério **mover**. Nenhum critério da 03
  manda o `iso_source.py` passar pela guarda, e fechada ao pé da letra o ciclo
  fica com uma guarda testada e inalcançável
- **Como foi detectado:** `grep -rn "require(" tools/ --include=*.py` acha três
  ocorrências, todas dentro do próprio `layout.py`, mais a leitura do critério
  da 03
- **Fix:** item de critério na 03 exigindo que toda leitura passe por
  `layout.require()`, com caso vermelho vivo pelo `iso_source.py`, e a §4.5
  dizendo quem chama a guarda e não só que ela existe

### CORR-LOOKS-006

- **Arquivo com problema:** `tools/looks/layout.py`, ramo de dica do `require()`
- **Sintoma:** `/SELECT.BIN` não está em `TEXTURE_FILES` nem em
  `GEOMETRY_FILES`, então recusa com `digest mismatch` pelado — a mensagem que
  o docstring do módulo diz ser a errada. É um dos dois arquivos que diferem
  entre os discos, e a causa provável da recusa é a mesma do `DAT2D.BIN`
- **Como foi detectado:** `require(layout.SELECT, …)` direto, comparado com o
  mesmo estímulo no `DAT2D.BIN`; e os digests dos dois discos remedidos
  (`86d14a66…` × `c9e1eaf8…`)
- **Fix:** dica própria para o `/SELECT.BIN` e um `assert` no `self_check()` de
  que **todo** caminho de `DIGEST` produz dica não vazia

### CORR-LOOKS-007

- **Arquivo com problema:** `tools/looks/layout.py`, docstring de topo
- **Sintoma:** diz "It also does no I/O" e o `_check_discs()` do mesmo arquivo
  abre duas imagens de CD. A dívida é conhecida e está na 03; o que está errado
  é afirmar hoje a propriedade que só vale depois dela
- **Como foi detectado:** leitura do módulo contra ele mesmo — `grep -n
  "iso.Image\|import iso" tools/looks/layout.py` dá três linhas
- **Fix:** ressalva no docstring, com a data e o destino, e a linha da 03
  mandando removê-la junto com a função

### CORR-LOOKS-008

- **Arquivo com problema:** `tools/looks/iso_source.py` (o `_check_discs()`), e
  a §4.5 do plano
- **Sintoma:** `derive_base()` e `require_base()` só rodam sobre vetores
  sintéticos dentro do `self_check()`. O único comando que abre os discos reais
  confere digest e não deriva base nenhuma, então as duas constantes de `BASE`
  ficam cravadas na prática, contra o que o critério da task pede. Os números do
  Log (2/18 palavras, 642/1.703, 24/240, alvos 8..112 e 72..1.712) vieram de
  script descartado, e reconferi-los exigiu escrever outro
- **Como foi detectado:** `grep -rn "require_base\|derive_base" tools/
  --include=*.py | grep -v layout.py` sai vazio; a derivação reproduzida à mão
  bate com o Log nos dois arquivos
- **Fix:** o `--check-discs` chama `require_base()` nos dois arquivos de
  geometria, nos dois discos, imprime cabeçalho/base/constante e sai != 0 em
  `WrongBase`

### CORR-LOOKS-009

- **Arquivo com problema:** `tools/looks/layout.py` (`sweep_addresses()`) e o
  critério da `06-harness-controles-e-selftest.md`
- **Sintoma:** a varredura que faz cumprir a regra 1 é a única peça do módulo
  sem caso vermelho, e nunca foi observada achando nada. Filtro quebrado, raiz
  errada ou blanqueamento demais imprimem a mesma frase verde, porque a saída
  não diz quantos arquivos varreu. E nenhum alvo a roda: o critério da 06 não
  nomeia o `sweep_addresses()`, então autoriza um segundo varredor
- **Como foi detectado:** `grep -n sweep tools/looks/layout.py` não acha
  ocorrência dentro do `self_check()`; árvore sintética em `tempfile` mostra
  que a varredura funciona — teste que esta revisão teve de escrever e que não
  fica
- **Fix:** caso vermelho no `self_check()` com os cinco sub-casos (hex,
  subpasta, escape na linha, escape na linha de cima, `layout.py` sintético),
  contagem de arquivos e linhas na saída, isenção do dono por caminho e não por
  nome, e a 06 obrigada a reusar a função

### CORR-LOOKS-010

- **Arquivo com problema:** a §1.5 do plano, o critério da
  `05-arquivos-de-modelo.md`, e o Log da `04-formato-de-secao.md`
- **Sintoma:** a varredura do `EDT_MOD.BIN` começa no offset 15.704 — a 43% do
  arquivo — e o Log a reporta como "11 seções … termina em 36.072 EXATO", sem
  dizer de onde partiu. Do offset 216, que é o primeiro alvo da **segunda** lista
  de ponteiros do cabeçalho, a mesma ferramenta acha **20 seções, 1.218
  vértices, 1.074 primitivas**. São dois modelos de onze peças, compartilhando
  15.704 e 17.572. A região que a §1.5 chama de "material de textura" é
  geometria, e o "cabeçalho TIM em 3.228" cai dentro da seção 2.608–3.432
- **Como foi detectado:** `section.scan(edt, 216)` contra `section.scan(edt,
  15704)`, mais o dump das duas listas e dos bytes em 3.228
- **Fix:** §1.5 reescrita no lugar; o critério da 05 pede 20/1.218/1.074 a
  partir de 216 e modelo **por lista**; a 08 ganha a linha de que são três
  candidatos e não dois; e o início do `EDT_MOD.BIN` passa a ser derivado ou
  constante do `layout.py`

### CORR-LOOKS-011

- **Arquivo com problema:** `tools/looks/layout.py`, topo do `sweep_addresses()`
- **Sintoma:** a reescrita para `tokenize` deixou `hex_literal` e `big_decimal`
  compiladas e sem uso na função do comando, enquanto as que decidem vivem no
  `_address_lines()` **com os mesmos nomes** e padrões ancorados. Quem for
  mudar o que conta como endereço edita as de cima e não muda nada
- **Como foi detectado:** `awk '/^def sweep_addresses/,/^def _address_lines/'
  tools/looks/layout.py | grep hex_literal` — duas atribuições, nenhuma leitura
- **Fix:** apagar as duas linhas mortas, ou promover as vivas a constante de
  módulo com nome próprio; um nome, uma definição

### CORR-LOOKS-012

- **Arquivo com problema:** `tests/CMakeLists.txt` (o alvo que falta) e a tabela
  de gates de `docs/prompts/perfil-looks.md`
- **Sintoma:** o perfil dá o `looks_image` como existente desde a LOOKS-TASK-05
  e não há linha nenhuma sobre `looks` no `tests/CMakeLists.txt`.
  `ctest --test-dir build -R looks` imprime `No tests were found!!!` e **sai
  0** — ausência indistinguível de verde, que é o que o próprio perfil proíbe
  ("mediu e passou, ou pulou com 77"). A verificação existe e é o
  `modelfile.py --check-image`, que ninguém roda sem se lembrar dele. E a
  LOOKS-TASK-19 diz criar "os três alvos", o que contradiz a tabela
- **Como foi detectado:** `grep -rn looks tests/CMakeLists.txt` vazio, e
  `ctest --test-dir build -R looks` com `echo $?`
- **Fix:** registrar o `looks_image` (77 sem `WE2002_LOOKS_IMAGE`), e alinhar a
  tabela de gates do perfil com a 19 sobre quem cria cada alvo

### CORR-LOOKS-013

- **Arquivo com problema:** o docstring de `layout.geometry_start()`, o último
  item do critério da `05-arquivos-de-modelo.md`, a §1.5 do plano e a linha
  encaminhada à `08-de-onde-vem-o-boneco.md`
- **Sintoma:** "16 das 18 listas abrem com tag `0x80` mirando o offset 104" —
  16 abrem com `0x80`, mas só **12** miram 104; **4** miram **232**, uma
  **segunda** corrida de ponteiros (32 contra 64). E "1816 é fato que as listas
  não declaram" — a lista de 72 tem uma entrada só, tag `0x02`, mirando
  exatamente 1816; a de 88 mira 4792. A decisão de não derivar o início do
  `MODEL.BIN` continua certa (`min` de todos os alvos é 104), mas a evidência
  escrita não a sustenta, e a segunda corrida não está registrada em lugar
  nenhum
- **Como foi detectado:** `layout.read_pointer_entries()` sobre as 18 listas,
  mais um parser independente que concorda, e `section.read_section()` em 104,
  232, 1816 e 4792
- **Fix:** corrigir os quatro textos com os números medidos, registrar as duas
  corridas e as duas listas de uma entrada, e dizer o motivo verdadeiro de a
  constante ficar

### CORR-LOOKS-014

- **Arquivo com problema:** `docs/tasks/looks/05-arquivos-de-modelo.md`,
  frontmatter
- **Sintoma:** o `title:` ainda diz "as 11 do `EDT_MOD.BIN`" e a célula da
  tabela do `progresso.md` já diz "as 20" — a CORR-LOOKS-010 atualizou um dos
  dois lugares onde o título mora. O `check_tasks.py` não confere título e fica
  verde
- **Como foi detectado:** `grep -n "^title:"` na task contra a linha 41 do
  `progresso.md`
- **Fix:** frontmatter passa a dizer 20, e um laço confere as vinte tasks de uma
  vez

### CORR-LOOKS-015

- **Arquivo com problema:** `docs/prompts/perfil-looks.md` (a tabela de gates) e
  a `19-alvos-de-ctest-e-cli.md`
- **Sintoma:** o `looks_selftest` está registrado no `tests/CMakeLists.txt` e
  **nenhum** dos três diretórios de build deste worktree o conhece:
  `ctest -R looks` responde `No tests were found!!!` e sai **0** nos três. O
  remédio que o Log da task propõe — reconfigurar o build — não funciona aqui:
  `cmake -S . -B <novo>` morre em `Could NOT find CURL`
  (`src/core/CMakeLists.txt:1`), e o `tools/looks/` não precisa de curl, de Qt
  nem de compilador. É o mesmo sintoma da CORR-LOOKS-012, que foi fechada sem
  que o `ctest` desta máquina jamais tivesse listado o alvo
- **Como foi detectado:** `ctest --test-dir {build,build-mingw,
  build-windows-release} -R looks` com `echo $?`; `grep -rl looks --include=
  CTestTestfile.cmake .` vazio; `CMAKE_HOME_DIRECTORY` do `build/` apontando
  para `/home/ingmar/...`; e uma configuração nova falhando em CURL
- **Fix:** o perfil passa a dizer, por alvo, o comando que roda **nesta**
  máquina (`python tools/looks/selftest.py`), a armadilha do `ctest -R` vazio
  saindo 0 entra na lista, e a 19 fecha a conta com o comando que existe.
  Tornar os alvos de `looks` configuráveis sem o `src/core` é decisão do dono
  do repositório, não de execução

### CORR-LOOKS-016

- **Arquivo com problema:** `tests/CMakeLists.txt`, linhas 205 e 210
- **Sintoma:** os oito testes Python do arquivo estão dentro de
  `if(Python3_FOUND)`; os dois de `looks` ficaram em `depth=0`. Sem Python
  detectado, `${Python3_EXECUTABLE}` expande para nada e o `looks_selftest` —
  o gate que "nunca pula" — aparece como **Failed** por executável inexistente,
  mandando quem o vir procurar defeito em `tools/looks/`
- **Como foi detectado:** mapa de `if`/`endif` do arquivo com a profundidade de
  cada `add_test`
- **Fix:** envolver os dois em `if(Python3_FOUND)`, e de passagem pôr cada
  comentário imediatamente acima do `add_test` que ele explica — hoje eles estão
  na ordem inversa

### CORR-LOOKS-017

- **Arquivo com problema:** `tools/looks/oracle.py`, a preflight do
  `check_live()`
- **Sintoma:** o `--check-live` precisa de **quatro** coisas e confere três.
  Sem `WE2002_LOOKS_IMAGE` ele sobe o emulador, esconde a janela, roda cinco
  verificações e então morre com `RuntimeError` e traceback (rc=1) dentro do
  `verify_load()` — nem mediu nem pulou com 77, que é o contrato do perfil. A
  mensagem certa já existe no `iso_source.image_from_env()`, e o módulo irmão
  (`modelfile.py --check-image`) já converte esse mesmo erro em skip 77
- **Como foi detectado:** rodando `--check-live` só com
  `WE2002_LOOKS_DRIVE_IMAGE` posta; os outros três caminhos de skip foram
  reproduzidos e saem 77 corretamente. Com as duas variáveis, o comando fecha
  verde e **todos** os números do Log reproduzem
- **Fix:** conferir a imagem japonesa na preflight, antes de qualquer `launch`,
  convertendo o `RuntimeError` em skip 77; e listar os pré-requisitos num só
  lugar, para o quinto não repetir a história

### CORR-LOOKS-018

- **Arquivo com problema:** `tools/looks/section.py` (`Primitive.tpage_vram`),
  `docs/PLAN-LOOKS-PY.md` §1.6 e §1.7
- **Sintoma:** a releitura da primitiva registrou **onde** a página de textura
  está e não **como** ela é amostrada. Os bits 7-8 do `tpage` são a
  profundidade, e os três valores do disco não concordam: `0x18` e `0x1A` são
  4 bits, `0x99` é **8 bits** — e ele é **1.039 das 2.841** primitivas, 666
  de 1.074 no `EDT_MOD.BIN`. O plano só tem a frase `4-bit CLUT`, de uma
  amostra do `get_gpu_state`, e a §1.7 diz "128×128 a 4 bpp cada". CLUT de 4
  bits tem 16 entradas, a de 8 tem 256: a LOOKS-TASK-10 caça a lista de
  paletas por marcador e erra em silêncio com a largura errada. De quebra,
  **duas das três páginas não têm entrada no `DAT2D.BIN`**
- **Como foi detectado:** remedindo os 2.841 `tpage` do disco japês com o
  `section.py` commitado e decodificando os bits do campo — as contagens por
  arquivo e por página estão na CORR
- **Fix:** `Primitive` expondo profundidade e semitransparência, com
  `self_check()` afirmando as duas páginas; §1.6 com a contagem por página e a
  profundidade de cada uma; §1.7 sem o "4 bpp" generalizado; e o critério da
  LOOKS-TASK-10 exigindo as duas larguras

### CORR-LOOKS-019

- **Arquivo com problema:** `tools/looks/oracle.py` — `check_tmds()` e
  `report_field()`
- **Sintoma:** o docstring do `check_tmds()` pergunta *"and does any field move
  one?"* e a função nunca aperta tecla; o `--fields`, que move campo, não
  conhece TMD e joga tudo que não cai nos dois arquivos de modelo num contador
  único (`in no model file: 202 byte(s)`). "Fora dos arquivos de modelo" e
  "fora dos TMDs" são afirmações diferentes, e a segunda — que é a metade
  negativa do veredito da incógnita (a) — não sai de comando nenhum
- **Como foi detectado:** rodando `--tmds` e `--fields` e procurando a linha que
  cruza os dois. Ela não existe; o cruzamento foi feito nesta revisão com
  script descartável sobre a mesma API, e dá **0 de 202** (`SKIN` no slot 2) e
  **0 de 124** (`HAIR` no slot 1) dentro de `0x800c1678..0x800c4948`+4 KiB — a
  conclusão está certa, a evidência é que não está versionada
- **Fix:** `_tmd_headers()` devolvendo extensão, um `tmd_spans()` no feitio do
  `spans()`, o `report_field()` com **três** baldes (modelo, TMD, resto) e um
  controle negativo que estrague o mapa de TMD e exija vermelho
