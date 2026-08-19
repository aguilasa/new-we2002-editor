---
id: WTE-TASK-27
title: "Handlers de gravação — escrever na imagem de CD"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-26"]
status: pendente
---

# WTE-TASK-27: Handlers de gravação

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4 e §6.
- **O grupo mais arriscado do projeto.** É onde o app toca 474 MB de imagem
  in-place, e é o único grupo que o golden test mede diretamente e sem
  ambiguidade.

Vêm por último de propósito: dependem de carga e edição estarem certas.

---

## Objetivo

Implementar as seis gravações, cada uma com golden verde antes de passar para a
seguinte.

### Alvos

| Handler | Endereço | O que grava |
|---|---|---|
| `boton_nombres2isoClick` | `0x0040d534` | nomes na imagem |
| `boton_barras2isoClick` | `0x0040cab8` | barras/atributos |
| `boton_tex2isoClick` | `0x0040de18` | textura |
| `boton_mcr2isoClick` | `0x0040c46c` | dados vindos de `.mcr` — **ver WTE-TASK-31** |
| `grabar_camisetaClick` | `0x0040ee80` | camisa — **ver WTE-TASK-32** |
| `grabar_memoryClick` | `0x0040f69c` | escreve `.mcr` (saída, não a imagem) |

Dois deles são **compartilhados com a Fase 5**: `boton_mcr2isoClick` depende do
parser de `.mcr` e `grabar_camisetaClick` do render 2D. Aqui se implementa a
**gravação** — onde e como os bytes vão para a imagem; a *origem* dos bytes é
das tasks 31 e 32. Se a ordem incomodar, inverta: nada impede fazer a 31/32
antes, desde que o golden desta task rode depois.

### Regras que não podem ser violadas

- **Nunca recalcular EDC/ECC.** O editor original não recalcula; preservar é o
  comportamento correto.
- **Fronteira de setor.** Os offsets pulam cabeçalho de setor manualmente
  (2352 = 24 + 2048 + 280). Se um round-trip falhar, é a primeira suspeita.
- **Cópia, sempre.** Cada rodada de golden usa duas cópias de ~474 MB.

### O diff de controle vem antes

Como na WTE-TASK-19: gravar **sem editar nada** nos dois lados e registrar o que
muda de graça. O `Save` reconstrói as all-star a partir dos links, e o
`Load`+`Save` do original não é idempotente (troca os dois primeiros cobradores
de cada clube de ML). Sem esse controle, toda medição vem contaminada.

### Critério

**Byte-idêntico** entre `wte.exe` e o app Lazarus, nas duas ROMs, para cada
operação. Divergência que sobreviver à análise vira **divergência deliberada**
com registro (WTE-TASK-35) — nunca "aceita e esquecida".

### A metade da WTE-TASK-26 que esta task herdou

*(decisão do usuário, 2026-08-12)*

A [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) edita **em memória** e não
grava; o critério dela dizia "editar pela tela nos dois lados, então gravar nos
dois, e o golden compara". O segundo verbo é desta task — as barras editadas lá
só chegam à imagem pelo `boton_barras2isoClick`, os nomes pelo
`boton_nombres2isoClick` —, e a 27 `depends_on` a 26. Circularidade da mesma
forma que a [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez para o gate.

**A 26 passou a fechar por conferência de tela e esta task herdou o byte.** Na
prática: cada uma das seis gravações roda o golden **duas** vezes —

1. **gravar sem editar** (o diff de controle da seção acima);
2. **editar pela tela, com um handler do grupo da 26, e então gravar.**

A segunda é a que julga a edição e a gravação juntas. Sem ela, a edição fica
verificada só por pixel, e pixel igual dos dois lados não prova que os dois
escreveram o **mesmo byte do modelo** — os dois poderiam desenhar a mesma
largura a partir de campos diferentes. É a lição da terceira ponta da
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md).

Par mínimo por gravação, quando existir handler de edição correspondente:

| gravação | edição que a exercita (WTE-TASK-26) |
|---|---|
| `boton_barras2isoClick` | `sel_barraClick` + `track_barraChange` |
| `boton_nombres2isoClick` | `edit_nombre1/2/3KeyPress`, `iguala_nombresClick` |
| `grabar_memoryClick` | os de número (`dorsalClick`, `scroll_dorsalChange`) |

`boton_tex2isoClick`, `boton_mcr2isoClick` e `grabar_camisetaClick` não têm par
na 26 — a origem dos bytes deles é das tasks 31 e 32, como já diz a seção de
alvos.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar (6) |
| `wte/src/ep2002_*.pas` | modificar |
| `wte/tools/roteiros/gravacao-*.sh` | criar (6) |

---

## Critério de conclusão

- [x] Diff de controle medido e registrado antes de qualquer edição
      — 2026-08-18, em [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md),
      gerado. Gravar sem editar **muda** 22 bytes: katakana virando ASCII
- [ ] As seis com spec e com golden verde nas duas ROMs
- [ ] **Cada gravação que tem par na WTE-TASK-26 rodada também com uma edição
      de tela antes** — herdado da 26 em 2026-08-12; ver a seção acima. É o
      único critério do projeto que julga edição e gravação juntas
- [ ] EDC/ECC preservados — provado, não presumido
- [ ] Nenhuma divergência sem veredito escrito
- [x] `roms/` intocada em todas as rodadas — vale por passagem, e a de
      2026-08-18 rodou toda sobre cópia em `work/`
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-18 — **primeira passagem, parcial.** A tarefa
  continua `⬜ Pendente`: nenhuma das seis gravações foi implementada. O que
  fechou foi a primeira linha do critério, o **diff de controle** — e ele
  mudou o desenho de todo roteiro de gravação que vier depois.

- **Resumo do que foi feito:**

  Três coisas, e a segunda vale mais que as outras duas juntas.

  **O diff de controle está medido e registrado.** Carregar um time e mandar
  gravar sem tocar em campo nenhum **não** é neutro nesta imagem: a ROM
  japonesa guarda o nome do time em latino no primeiro bloco e em katakana de
  meia largura nos demais, e o editor lê o campo da tela — que veio do bloco
  latino — e o grava em **todos**. Vinte e dois bytes mudam de graça, em três
  trechos, e são katakana virando ASCII. Reproduzir isso é obrigação: um port
  que "preservasse" o katakana divergiria do oráculo em toda gravação de nomes,
  e o golden acusaria a gravação por um defeito que seria de fidelidade.

  A medição é a sessão `27-gravacao-controle` do `diff_dirigido.sh`, e o
  registro é gerado — [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md),
  do novo [`gravacao_controle.py`](../../wte/tools/gravacao_controle.py), que
  **não mede nada sozinho**: cruza as duas réguas já versionadas. Os offsets
  desta medição são a seção `Bytes tocados` das seis specs que vêm, e
  copiá-los à mão de dois TSV seria a forma conhecida de o número envelhecer
  calado.

  **O clique não grava — quem grava é o `fseek` seguinte.** O `wte.exe` escreve
  pela saída bufferizada do runtime C. A primeira medição desta passagem disse
  que o `boton_barras2iso` **não tocava a imagem**, e o TSV de uma sessão
  anterior (`09-areas-com-time`) dizia o mesmo desde 2026-08-10. Estava errado
  nos dois: ele grava 5 bytes, que ficam no buffer até algo depois procurar
  noutro ponto do mesmo arquivo.

  Medido com um par de sondas de **uma** variável de diferença, agora
  versionadas — [`27-descarga-sem.txt`](../../wte/tests/roteiros/27-descarga-sem.txt)
  e [`27-descarga-com.txt`](../../wte/tests/roteiros/27-descarga-com.txt),
  iguais linha a linha, e o `-com` troca de time depois do clique: **zero**
  escrita no `-sem`, os 5 bytes em 2328184 no `-com`. O
  `test_gravacao_controle.py` compara os dois corpos e exige que o resultado
  medido continue oposto, como o `test_analisar_crash.py` faz com o par 07/08.

  Duas consequências, e as duas são armadilha de gate:

  1. **roteiro que termina numa gravação mede um oráculo truncado** — o harness
     encerra com `wineserver -k` e o buffer se perde. Se o port gravar direto,
     o golden acusaria o *port* por bytes que o oráculo nunca escreveu;
  2. **marca de corte antes da descarga credita a faixa à ação seguinte.** Na
     primeira corrida os 5 bytes das barras apareceram como se fossem dos
     nomes — atribuição errada, em silêncio, num TSV que parecia medido.

  Por isso cada bloco do `golden-02-gravacao.txt` termina com uma troca de time
  e só então a marca. Refeita a corrida, a atribuição fecha: barras 5 bytes,
  nomes 8 faixas.

  **A primeira régua não tinha porta automática, e ninguém tinha notado.** A
  [CORR-WTE-047](/docs/tasks/CORR-WTE-047.md) deu ao `cmp` um `--fundir-cmp`
  porque o `cmp.tsv` morria em `/tmp`; o **trace** tinha a mesma doença e
  chegava ao `io-medido.tsv` a mão, o que é indistinguível de não chegar quando
  alguém esquece. As 75 faixas desta sessão não entrariam sozinhas. Entrou
  `--fundir-io`, simétrico, chamado pelo `diff_dirigido.sh`.

- **O que a passagem NÃO fez, e é o resto da task:**
  - as seis gravações continuam sem spec e sem Pascal. O
    `boton_nombres2isoClick` foi lido até o ponto de se saber que ele valida os
    três campos de nome antes de gravar (vazio em 1 e 2, menos de 3 letras em
    3) e que endereça oito faixas; isso ainda **não** é spec;
  - o par edição+gravação (o critério herdado da WTE-TASK-26) não rodou: sem
    gravação implementada não há o que comparar;
  - EDC/ECC preservados continua **presumido**, não provado.

- **A ROM europeia não hospeda este grupo, e agora está medido aqui.** O mesmo
  roteiro sobre `roms/golden-european-deluxe.bin` morre na troca de time —
  49.749 violações de acesso, o número que a
  [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) já tinha medido — e a caixa de
  confirmação da gravação nunca aparece. O critério "nas duas ROMs" da task
  herda esse limite; ele não é omissão desta passagem.

- **Arquivos criados/modificados:**
  - `wte/tests/roteiros/golden-02-gravacao.txt` — o roteiro do controle
  - `wte/tests/roteiros/27-descarga-{sem,com}.txt` — o par de sondas
  - `wte/tools/gravacao_controle.py`, `wte/tools/test_gravacao_controle.py`
  - `wte/re/gravacao-controle.md` — gerado
  - `wte/tools/analisar_io.py` (`--fundir-io`), `wte/tools/test_analisar_io.py`
  - `wte/tools/diff_dirigido.sh` — funde as duas réguas
  - `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv`, `wte/re/offsets-novos.md`
  - `wte/tools/README.md`, `wte/tests/roteiros/README.md`
  - `docs/tasks/progresso.md`, e esta task

- **Gates medidos:** `golden_check.sh --modo controle` **PASSOU: byte-idêntico**
  e `--modo positivo` **detectou** o byte plantado em 405228, os dois sobre o
  roteiro final; `make -C wte check` rc 0, com **590 testes** OK; `lazbuild`
  rc 0. As duas réguas do `diff_dirigido.sh` fecham nas três sessões novas
  (12/12, 9/9, 9/9). `roms/` intocada — todas as corridas sobre cópia em
  `work/`.

- **Problemas encontrados:** o descrito acima — a leitura de que o
  `boton_barras2iso` "não grava" era artefato de buffer, e sobreviveu por oito
  dias num TSV versionado porque nada exercia a descarga. Foi preciso desmontar
  a atribuição do próprio instrumento antes de confiar em qualquer número desta
  task.

---

- **Executado em:** 2026-08-18 — **segunda passagem, ainda parcial.** A
  primeira das seis gravações fechou: `boton_barras2isoClick`, com spec, Pascal
  e golden verde. Cinco continuam abertas.

- **Resumo do que foi feito:**

  **`boton_barras2isoClick` está `implementado`.** É o menor do grupo — 272
  bytes, do `0x0040cab8` ao `0x0040cbc7` — e coube inteiro numa leitura. Ele
  grava cinco bytes do **buffer de edição** (`0x00434592`), não do modelo, o
  que é exatamente a distinção que a WTE-TASK-26 mediu e guardou como
  `BarrasEmEdicao`; sem ela a gravação levaria o valor velho e o gate acusaria
  a gravação por um defeito da edição.

  **O endereço não sai de um `OFS_*` mais um passo — sai da aritmética do
  original, e as duas fontes foram confrontadas.** O Obocaman calcula
  `0x45FF0 + 5·idx` como índice de byte no fluxo de dados a partir do setor
  850 e converte para offset absoluto na hora. O `we2002_core` chega aos
  mesmos endereços por outro caminho: lê em sequência e **salta** na fronteira
  de setor, com `OFS_TEAM_BARS_A` para o time 3. As duas concordam onde
  poderiam divergir — 2328199 para `idx = 3`, 2328508 para `idx = 4`. É a
  conferência que a §4.2 do plano manda fazer antes de acreditar em fórmula.

  **O gate agora julga edição e gravação juntas, e precisou de DOIS roteiros
  para isso.** O `golden-03-barras` grava sem editar e passa — mas passaria
  igual com um port que não gravasse nada, porque sem edição os dois lados
  escrevem os bytes que já estavam lá. O `golden-04-barras-editada` edita
  `bar_defence` do time 2 pela tela antes de mandar gravar: medido no lado
  oráculo, `0x04` vira `0x06` em 2328195, e o port produziu o mesmo arquivo. É
  o critério que a WTE-TASK-26 passou para cá em 2026-08-12, e é a primeira vez
  que ele roda.

  O estímulo do `golden-04` não é novo: as três coordenadas (3 `Down`,
  `sel_barra1` em (30,112), trilha em (190,200)) são as que o
  `compara_tela.sh` mediu nos dois lados em 2026-08-12, inclusive o passo de
  `+2` por clique na trilha, que é código diferente nos dois widgetsets.

  **EDC/ECC preservados deixou de ser presumido, para esta gravação.** O
  `cmp` da corrida editada muda **um** byte, em 2328195; os 280 bytes de
  EDC/ECC do setor 989 (2328200..2328479) saem idênticos. Medido, não
  presumido — mas vale para a gravação medida, não para o grupo, então o
  critério continua aberto.

- **A assimetria de coordenada entre os lados tem causa medida.** O `Ok` do
  `ficha_info3` fica em (142,80) no oráculo e em (140,56) no port: sob Wine sem
  gerenciador de janela a moldura é desenhada **dentro** da janela X (3 px de
  borda, 29 de título), e a janela mede 282×113; sob gtk2 a janela **é** o
  cliente, e mede os 276×81 do DFM. Por isso cada `golden-0*` tem `.port.txt`
  próprio.

- **Uma divergência de arquitetura, e ela não aparece no gate.** O port também
  atualiza `Jogo.teams[].bar_*` ao gravar. O `wte.exe` relê a imagem a cada
  troca de time, então o disco é a fonte dele; o port carrega uma vez e desenha
  a partir de `Jogo`. Gravar só no disco faria a tela do próprio port discordar
  do próprio arquivo na volta ao time. Mesmo byte, mesmo offset — está escrito
  na spec.

- **Um número do plano mudou, e o `check_fase2.py` não deixou passar.** Escrever
  Pascal à mão move a fração de código gerado: 74,0% → **73,6%** (9.323 geradas
  contra 3.345 à mão). A §4.4 do `PLAN-WTE-LAZARUS.md` afirma esse número
  literalmente e o `--check` reprovou até ela ser corrigida. Isso vai se repetir
  a cada handler desta fase.

- **O que esta passagem NÃO fez:**
  - `boton_nombres2iso`, `boton_tex2iso`, `boton_mcr2iso`, `grabar_camiseta` e
    `grabar_memory` continuam sem spec e sem Pascal;
  - EDC/ECC preservados continua critério aberto — provado para uma gravação,
    não para as seis;
  - os nove handlers que a WTE-TASK-26 deixou em `aberto` pela opção A
    continuam lá: só o par das barras (`sel_barraClick` + `track_barraChange`)
    ganhou julgamento por byte nesta passagem.

- **Arquivos criados/modificados:**
  - `wte/re/spec/MainForm.boton_barras2isoClick.md` — veredito `implementado`
  - `wte/src/impl/ep2002_mainform.boton_barras2isoClick.inc`
  - `wte/src/impl/ep2002_mainform.aux.inc` — a aritmética de endereço e o
    `GuardaBarrasNoModelo`
  - `wte/src/we2002_estado.pas` — `EnderecoDeDados` e `GravaNaImagem`, a porta
    de escrita do port
  - `wte/tests/roteiros/golden-03-barras{,.port}.txt`,
    `golden-04-barras-editada{,.port}.txt`
  - `wte/re/spec/INDICE.md`, `wte/re/fase-2.md`, `wte/re/offsets-novos.md`,
    `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv` — gerados/evidência
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — a fração remedida
  - `wte/tests/roteiros/README.md`, e esta task

- **Gates medidos:** `golden_check.sh` sobre `golden-03-barras` **PASSOU** e
  sobre `golden-04-barras-editada` **PASSOU** (nos dois, só as duas faixas
  declaradas do arranque divergem); `make -C wte check` rc 0 com **590 testes**
  OK; `lazbuild` rc 0; `spec_index.py` 19 `implementado`. `roms/` intocada.

- **Problemas encontrados:** nenhum que tenha sobrado. Um `pkill -f 'build/wte'`
  numa medição exploratória casou com a própria linha de comando do shell e o
  matou junto — sem consequência para o repositório, e a lição é a de sempre
  neste projeto: filtro por nome alcança quem está segurando o nome.

---

- **Executado em:** 2026-08-19 — **terceira passagem, ainda parcial.** Abertura
  do `boton_nombres2isoClick`: a spec está escrita e o mapa de bytes medido, e
  o Pascal **não**. O veredito ficou `aberto` de propósito.

- **Resumo do que foi feito:**

  **A estrutura do maior handler do grupo está recuperada.** 2.268 bytes, e ele
  não grava sozinho: apoia-se em duas tabelas e três rotinas internas.

  | endereço | papel |
  |---|---|
  | `0x004231a0` | 3 linhas × 6 `DWORD` — quais blocos cada campo tem; zero quer dizer "não tem" |
  | `0x00433a0c` | 3 × 6 registros de 52 B, preenchidos por time: `{offset, comprimento, modo, buffer 40 B}` |
  | `0x00403a68` | codifica o texto da tela no buffer, em **duas** codificações |
  | `0x00403dcc` | resolve o registro `(campo, bloco)` |
  | `0x00403400` | `fseek` + `fputc` byte a byte — não conhece nome nenhum |

  O `+4` da tabela de registros é o `0x00433a10` que a
  [CORR-WTE-061](/docs/tasks/CORR-WTE-061.md) já tinha medido como largura por
  time; agora ele tem vizinhos com nome.

  **O trace não separa bloco de bloco, e isso obrigou uma régua nova.** As oito
  faixas que o `27-gravacao-controle` registrou são fronteiras de **descarga**
  do buffer do runtime C, não gravações lógicas: duas gravações vizinhas caem
  na mesma faixa. A sonda
  [`27-nomes-editados.txt`](../../wte/tests/roteiros/27-nomes-editados.txt)
  digita texto distinto nos três campos antes de gravar, e aí o `cmp` atribui
  cada bloco ao seu campo. Resultado: **dez** blocos, com offset, tamanho e
  conteúdo — 2 de `edit_nombre1`, 5 de `edit_nombre2` e 3 de `edit_nombre3`.

  O estímulo não é novo: texto `A B-C.DEFG` e time 2, os mesmos do
  `compara_tela.sh --nomes`, já medidos nos dois lados em 2026-08-12.

  **Duas codificações, e o campo `modo` do registro escolhe.** Modo 1 é dois
  bytes por caractere (`0x00403448` devolve o par em `0x00432eb4`/`0x00432eb8`;
  caractere não reconhecido vira um espaço simples) — é o
  `OFS_TEAM_NAME_KANJI_A`, onde `A BC.` ocupa 10 bytes. Modo 2 é um byte por
  caractere. Nos dois o resto do comprimento vai a `0x00`, e o laço para no
  comprimento do **registro**, nunca no fim do texto.

  **Três exclusões dentro do laço, e nenhuma é validação de entrada.** Bloco
  ausente na tabela; `edit_nombre1` começando com `?` pula **todos** os blocos
  daquele campo (o `?` é o que a carga mostra quando não soube decodificar, e
  regravá-lo destruiria o nome); e `edit_nombre2` bloco 3 com `ItemIndex >= 63`,
  que é clube de Master League. É por isso que a tabela promete onze blocos e
  a medição vê dez.

  **Ele também mexe na tela, e não só na imagem:** remonta o rótulo do combo
  (`IntToStr(idx)` alinhado à direita em três colunas, mais o texto de
  `edit_nombre1`) e o escreve em `Items[idx]` de `lista_equipos_1` e
  `lista_equipos_2`, guardando e repondo o `ItemIndex` — porque atribuir a
  `Items[]` zera a seleção.

- **O que esta passagem NÃO fez, e por quê:** o Pascal. A spec responde *o que*
  e *onde* para o time medido; falta a regra geral que a carga usa para
  preencher os 18 registros — offset e comprimento **por time** —, e o port
  precisa reproduzi-la ou derivá-la do `we2002_core`. Isso está escrito na
  própria spec, na seção "O que falta para escrever o Pascal": pelo gabarito,
  spec que não basta para escrever o código está incompleta, e dizer isso é a
  informação que ela existe para dar.

- **Arquivos criados/modificados:**
  - `wte/re/spec/MainForm.boton_nombres2isoClick.md` — veredito `aberto`
  - `wte/tests/roteiros/27-nomes-editados.txt` — a sonda de atribuição
  - `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv` — a evidência da sessão
  - `wte/re/offsets-novos.md`, `wte/re/spec/INDICE.md` — gerados
  - `wte/tests/roteiros/README.md`, e esta task

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` rc 0;
  `spec_index.py` 58 com spec, 19 `implementado`. Nenhuma corrida de golden
  nesta passagem — não há Pascal novo para julgar, e rodar o gate sobre código
  inalterado mediria a passagem anterior. `roms/` intocada.

- **Problemas encontrados:** nenhum.

---

- **Executado em:** 2026-08-19 — **quarta passagem.** `boton_nombres2isoClick`
  está `implementado`, com golden verde e controle fechando antes. **Duas das
  seis** gravações prontas; a task continua `⬜ Pendente`.

- **Resumo do que foi feito:**

  **A peça que faltava era `0x00403c0c`, e ela não é tabela — é varredura.** A
  terceira passagem parou dizendo que faltava "a regra geral que enche os 18
  registros, offset e comprimento por time". A regra é: partir do offset do
  bloco, andar `94 − índice` registros terminados em NUL (com o enchimento que
  vier depois) e medir o slot que sobrou. Sem tabela de offset por time e sem
  tabela de comprimento.

  Duas coisas caem de graça daí, e nenhuma tabela as diria: **os blocos guardam
  os times em ordem inversa** — o offset da tabela é o slot do time 94, e o
  `we2002_core` conhece a mesma inversão pelo outro lado (`ml_teams[31-i]` no
  `Save`) — e **o comprimento é a largura do slot medida na imagem**, não uma
  constante, que é por que o mesmo campo grava 7 bytes num bloco e 3 noutro.

  **O salto de setor é do fluxo, não do endereço.** `0x00403388` testa
  `posição mod 2352 = 2072` depois de **cada** byte e pula 304. É o que torna o
  MODE2/2352 invisível para o resto do código do original — e é obrigatório no
  port: sem ele, nome que atravessa fronteira de setor escreveria por cima do
  EDC/ECC. Entrou como `SaltaFronteiraDeSetor` / `LeDoFluxo` / `GravaNoFluxo`
  no `we2002_estado`.

  **O espaço é codificado diferente do `ed.exe`, e isso mudou uma decisão de
  reuso.** No modo de dois bytes o `wte.exe` escreve **um** `0x20` para o
  espaço; o `AsciiToKanji` do `we2002_core` escreve o par `0x82 0x80`. Medido
  no byte gravado: `A BC.` sai com nove bytes, não dez. Como o alvo deste
  projeto é o editor do Obocaman, o port **não** reusa o codec do core aqui —
  reusar teria dado um golden vermelho com cara de bug de offset.

  **Um erro da passagem anterior foi corrigido pela medição.** A spec dizia que
  o bloco 3 do campo 2 é pulado para `ItemIndex >= 63`; é o contrário —
  `cmp eax,0x3f` / `jl` pula quando o índice é **menor** que 63, porque o bloco
  é `OFS_ML_TEAM_NAME_7` e só clube de Master League o tem. A tabela promete
  onze blocos e o `cmp` viu dez com o time 2, que é o que denunciou.

- **A passagem do golden não é vazia, e isso foi medido separado.** Verde entre
  dois lados poderia significar "nenhum dos dois gravou". Rodado o lado port
  sozinho contra a ROM limpa, ele grava **os dez blocos**, nos mesmos offsets e
  tamanhos que a sonda `27-nomes-editados` mediu no oráculo.

- **O `:99` caiu no meio da passagem, e o sintoma é o da memória do projeto:
  saída vazia e código 1, sem uma linha de erro.** O `roteiro_display` resolve
  o `XAUTHORITY` do `ps` e, com o servidor morto, o `set -e` derruba o script
  antes de qualquer mensagem. Foi religado com a geometria documentada no
  `CLAUDE.md` (`Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp`) — não houve
  queda para o `:1`.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.boton_nombres2isoClick.inc`
  - `wte/src/impl/ep2002_mainform.aux.inc` — a tabela `NOME_BLOCOS`, a
    varredura `LocalizaBlocoDeNome` e o codificador `CodificaNomeDoBloco`
  - `wte/src/we2002_estado.pas` — o fluxo com salto de setor
  - `wte/tests/roteiros/golden-05-nomes{,.port}.txt`
  - `wte/re/spec/MainForm.boton_nombres2isoClick.md` — veredito `implementado`,
    mais a regra recuperada e a correção do sentido da exclusão
  - `docs/PLAN-WTE-LAZARUS.md` §4.4, `wte/re/fase-2.md`, `wte/re/spec/INDICE.md`
  - `wte/tests/roteiros/README.md`, e esta task

- **Gates medidos:** `golden_check.sh --modo controle` sobre `golden-05-nomes`
  **PASSOU: byte-idêntico** — e num roteiro que digita isso não é formalidade,
  é a única régua onde o não-determinismo do teclado apareceria; o `golden`
  contra o port **PASSOU**, só as duas faixas do arranque. `make -C wte check`
  rc 0; `lazbuild` rc 0; `spec_index.py` **20 `implementado`**. A fração de
  código gerado caiu de 73,6% para **72,0%** e o `check_fase2.py` reprovou até
  a §4.4 do plano ser corrigida — de novo. `roms/` intocada.

- **Problemas encontrados:** o `:99` morto, acima. Nada mais.

---

- **Executado em:** 2026-08-19 — **quinta passagem.** `boton_tex2isoClick`
  está `implementado`, com controle e golden verdes. **Três das seis**
  gravações prontas; a task continua `⬜ Pendente`.

- **Resumo do que foi feito:**

  **A textura é aritmética pura — nem varredura, nem tabela.**

  ```
  offset = 19756824 + 47040 * (indice + 9 * (indice div 95))
  ```

  `19756824` = `8400 * 2352 + 24` e `47040` = `20 * 2352`: **vinte setores por
  time**, contíguos. Medido com o time 2 e uma fonte de 5000 bytes — setores
  8440..8459, a partir de 19850904, que é exatamente `19756824 + 47040 * 2`.

  **São sempre os vinte, e é aí que um port erraria.** O original copia
  enquanto a fonte durar; quando ela acaba no meio de um bloco ele enche o resto
  com zero, e um **segundo** laço escreve de zero os blocos que sobraram. Uma
  textura menor que a anterior não deixa rabo. Um port que gravasse só o que
  leu passaria com uma fonte de 40960 bytes e falharia com qualquer outra — por
  isso a sonda usa 5000, que não é múltiplo de 2048.

  **O botão não estava habilitado, e achar quem o habilita foi metade da
  passagem.** O primeiro golden falhou com o port sem mostrar o modal, e o
  trace não tinha o handler: `boton_tex2iso` nasce `Enabled = False` no DFM.
  Quem o liga no original é o `boton_dialogo_texClick`, em `0x0040e17d` —
  `SetEnabled(True)` pela VMT[0x64] sobre o campo `0x0474`, que o
  `wte/re/campos.tsv` resolve nesse botão. Faz sentido: sem fonte escolhida não
  há o que gravar.

  **A textura entra no port por `WTE_TEXTURA`, e isso é afordância de harness.**
  O lado port do gate não consegue escolher arquivo — o `TOpenDialog` do gtk2
  não se dirige por coordenada fixa sem gerenciador de janela. A variável semeia
  `TexturaEscolhida` no `FormShow` e liga o botão, exatamente como o argumento
  posicional semeia a imagem desde a WTE-TASK-25. Não muda byte nenhum: muda por
  onde o caminho entra, e os dois lados terminam com o mesmo arquivo.

- **O `boton_dialogo_texClick` continua `aberto`, de propósito.** Portá-lo pela
  metade — só o `Execute` e o caminho — daria um veredito que afirma mais do que
  se fez, e o formato `.tex` é da
  [WTE-TASK-32](/docs/tasks/32-camisa-e-bandeira-2d.md). Na janela do port o
  botão de diálogo segue inerte, e está escrito na spec dele e na do
  `boton_tex2iso`.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.boton_tex2isoClick.inc`
  - `wte/src/impl/ep2002_mainform.aux.inc` — as três constantes da região
  - `wte/src/impl/ep2002_mainform.FormShow.inc` — a semeadura e o `Enabled`
  - `wte/src/we2002_estado.pas` — `TexturaEscolhida`, `TexturaTamanho`,
    `TamanhoDoArquivo`
  - `wte/tools/golden_run_laz.sh` — repassa `WTE_TEXTURA`
  - `wte/tests/roteiros/27-textura.txt` — a sonda
  - `wte/tests/roteiros/golden-06-textura{,.port}.txt` — o gate
  - `wte/re/spec/MainForm.boton_tex2isoClick.md` — veredito `implementado`
  - `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv`, `wte/re/offsets-novos.md`,
    `wte/re/spec/INDICE.md`, `wte/re/fase-2.md`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4, `wte/tests/roteiros/README.md`, e esta task

- **Gates medidos:** `golden_check.sh --modo controle` **PASSOU: byte-idêntico**
  e o `golden` contra o port **PASSOU**, só as duas faixas do arranque.
  Verificado à parte que a passagem não é vazia: o port sozinho contra a ROM
  limpa grava os **vinte** setores, a partir do mesmo 19850904. `make -C wte
  check` rc 0; `lazbuild` rc 0; `spec_index.py` **21 `implementado`**. A fração
  de código gerado caiu para **71,4%** e a §4.4 do plano foi corrigida de novo.
  `roms/` intocada.

- **Problemas encontrados:** o botão desabilitado, acima — e o sintoma dele é
  instrutivo: o gate falhou dizendo "a janela `W11 TE PT` não apareceu", que
  parece problema de roteiro. O que respondeu foi o `port-trace.log`, onde o
  handler simplesmente não constava.
