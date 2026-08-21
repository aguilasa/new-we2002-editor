---
id: WTE-TASK-29
title: "Camisa e bandeira 2D em tempo real, com colar-cores"
type: implementação
category: features
phase: 4
depends_on: ["WTE-TASK-08", "WTE-TASK-24", "WTE-TASK-27"]
status: pendente
---

# WTE-TASK-29: Render 2D

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.3 e §9.
- Terceira das quatro, e **a de maior risco do projeto**. A tabela de riscos do
  plano dá probabilidade **média** para "render 2D não bate pixel a pixel", e a
  causa nomeada é arredondamento de gradiente.

É também a feature mais visível: o readme do original a vende como "an
improvement over WE2002 Painter features".

---

## Objetivo

Reproduzir o editor de cor com fidelidade medida.

### Alvos

| Handler | Endereço |
|---|---|
| `colorearClick` | `0x00410ea8` |
| `gradienteClick` | `0x004063b0` |
| `oscurecerClick` | `0x004065fc` |
| `aclararClick` | `0x00406744` |
| `lista_col0Change` … `lista_col3Change` | `0x0040688c` … `0x0040690c` |
| `colorMouseDown` | `0x00406a0c` |
| `barraChange`, `barra1Change`, `barra2Change` | `0x00405e40`, `0x00406358`, `0x00406384` |
| `malla1MouseDown`, `malla2MouseDown` | `0x00409f4c`, `0x0040a000` |
| `grabar_camisetaClick` | `0x0040ee80` |

Formulário `ficha_color`: 758 linhas de DFM.

### A base

Os 105 `image/uniformes2d/*.bmp` e as 53 `image/banderas/*.bmp` são a base, e a
cor é aplicada sobre eles. A convenção de índice vem da WTE-TASK-08.

Em Pascal isso é `TBitmap` mais varredura de pixel; a LCL dá `TLazIntfImage`
para acesso rápido — `Canvas.Pixels` num loop é ordens de grandeza mais lento e
não serve para tempo real.

> **Correção medida em 2026-08-20: não há varredura de pixel — a cor mora na
> paleta.** O parágrafo acima supõe o algoritmo que a pergunta 2 de "Onde a
> fidelidade some" manda descobrir *antes* de escrever código, e a resposta é a
> outra. O `TLazIntfImage` continua sendo o certo, e por outro motivo: o port
> precisa do **índice** de cada pixel, e o leitor de BMP da LCL entrega o
> bitmap já convertido para 32 bpp, com a paleta consumida e jogada fora. Daí a
> [`we2002_bmp.pas`](../../wte/src/we2002_bmp.pas), que decodifica o arquivo
> ela mesma.

### Onde a fidelidade some

1. **Arredondamento de gradiente.** Se o original faz aritmética inteira com
   truncamento e o Pascal faz com arredondamento, o degradê inteiro desloca de 1.
   É o risco nomeado.
2. **Paleta.** BMP de 8 bits tem paleta; aplicar cor pode ser troca de entrada de
   paleta, não varredura de pixel. Descobrir qual antes de escrever código —
   muda o algoritmo inteiro.
3. **Espaço de cor.** "Escurecer" e "clarear" podem ser multiplicação em RGB ou
   ajuste em HSL. Resultado parecido, valores diferentes.

### Verificação

**Diff de bitmap contra captura do original**, não inspeção. Para uma grade de
cores de entrada, capturar a camisa renderizada dos dois lados e comparar pixel
a pixel.

**Aceitar tolerância documentada** se a igualdade exata não sair — a §9 já prevê
isso. O que não é aceitável é tolerância não medida: se houver diferença, ela
tem de ter máximo conhecido e causa nomeada.

### A gravação é outra coisa, e desde 2026-08-19 ela mora aqui

`grabar_camisetaClick` (`0x0040ee80`) tem critério byte-idêntico, sem
tolerância. Render é tela; gravação é dado. Não confundir os dois critérios.

> **Correção medida em 2026-08-20: ele não grava na imagem — ele exporta.** O
> enunciado dizia "grava na imagem", e o `.text` diz outra coisa: o handler abre
> o destino em `"wb"`, **lê** da imagem e escreve num arquivo, terminando com
> `O uni foi salvo!!!.`. A ROM sai intacta. O critério byte-idêntico continua
> valendo, mas sobre o **artefato** — é a mesma forma do
> [`golden-07-mcr`](../../wte/tests/roteiros/golden-07-mcr.txt), com
> `--artefato`. Quem grava textura **na** imagem é o `boton_tex2isoClick`, que
> já tem veredito `implementado`. Detalhe em
> [`wte/re/render2d.md`](../../wte/re/render2d.md).

*(decisão do usuário, 2026-08-19)* Até essa data o handler era da
[WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) — a gravação lá, o render
aqui. A divisão criava **ciclo**: a 27 não fechava sem esta task, e esta
declarava `depends_on` a 27. Agora a task que produz os pixels é a mesma que os
grava, e por isso esta subiu para a fase 4.

Com a gravação vieram as regras, e nenhuma delas é sobre o handler — são sobre
gravar **nesta imagem**:

- **Nunca recalcular EDC/ECC.** O original não recalcula; preservar é o correto.
- **Fronteira de setor.** `2352 = 24 + 2048 + 280`, com os saltos à mão.
- **Cópia, sempre**; `roms/` nunca é alvo.
- **O diff de controle** já medido em
  [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md) vale aqui
  igual: gravar sem editar **muda** 22 bytes nesta ROM.
- **O clique não grava; quem grava é o `fseek` seguinte.** Saída bufferizada do
  runtime C — roteiro que termina numa gravação mede um oráculo truncado, porque
  o harness encerra com `wineserver -k`. Todo roteiro de gravação termina com
  uma troca de time e só então a marca de corte. Medido com o par
  [`27-descarga-sem.txt`](../../wte/tests/roteiros/27-descarga-sem.txt) /
  [`27-descarga-com.txt`](../../wte/tests/roteiros/27-descarga-com.txt).

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar |
| `wte/re/render2d.md` | criar — algoritmo e espaço de cor **feitos**; tolerância ainda não |
| `wte/tools/dump_render2d.py`, `wte/tools/test_dump_render2d.py` | criar — feito |
| `wte/src/we2002_render.pas` | criar — feito (a aritmética de cor) |
| `wte/src/we2002_bmp.pas` | criar — feito (o recipiente de 8 bpp) |
| `wte/src/wte_render2d.pas` | criar — feito (o `TLazIntfImage` e o cache) |
| `wte/src/wte_uniformes.pas` | criar — feito (gerado: as duas tabelas de `.data`) |
| `wte/tests/test_render.pas`, `wte/tests/test_bmp.pas` | criar — feito |
| `wte/tools/compara_tela.py` | estender — feito (a medida dos três `TImage`) |

---

## Critério de conclusão

- [x] **Decidido paleta vs. varredura de pixel, com evidência: é paleta.** As
      três rotinas de desenho posicionam o `.bmp` em `0x36` — o fim do
      cabeçalho de 54 bytes, a primeira entrada — e reescrevem as primeiras
      entradas; nenhuma toca um pixel. **E não reescrevem o mesmo tanto:** a
      bandeira faz 16 e o uniforme faz 15, duas vezes, uma por arquivo. A
      seção 6 do [`assets.md`](../../wte/re/assets.md) dizia "idem, 16" para o
      uniforme; foi corrigida, e o número passou a sair de ferramenta
- [x] **Espaço de cor de escurecer/clarear identificado: nenhum.** Não é RGB
      de 8 bits nem HSL — a conta acontece na palavra BGR555 **empacotada**.
      Escurecer subtrai `1`, `0x20` e `0x400`; clarear soma os mesmos três. O
      limite é testado no byte já expandido, com piso `> 0` e teto `< 0xF8` — e
      `0xF8` é `31 << 3`, o que prova de quebra que a expansão de 5 para 8 bits
      é **deslocamento**, saturando em 248 e não em 255
- [x] **`TLazIntfImage` usado; render em tempo real sem travar a janela.** A
      [`wte_render2d.pas`](../../wte/src/wte_render2d.pas) monta um
      `TLazIntfImage` a partir do índice de paleta de cada pixel e o atribui ao
      `TImage`. O custo está medido, não afirmado: o maior bitmap que este
      render toca tem **51 × 42 = 2.142 px** (o `dump_render2d.py` mede a
      pasta), uma troca de time redesenha três arquivos, e a troca de paleta em
      si são 45 bytes. O `.bmp` é lido do disco **uma vez** e fica em memória —
      o original o relê a cada redesenho, porque para ele o arquivo *é* o
      estado
- [ ] Diff de bitmap sobre grade de cores, com tolerância **medida** e causa
      nomeada — **metade fechou, e a tolerância é zero.** O
      `compara_tela.py` ganhou a medida: `bandera`, `home1` e `home2`
      recortados pelo `.lfm` e comparados pixel a pixel, com a calibração que
      já existia. Times 2, 9 e 63: **0 de 8.960 px** (9.800 no clube de ML),
      maior desvio de canal 0. A refusa foi **vista** — com
      `PRIMEIRA_UNIFORME = 0` o mesmo teste acusa 2.008 de 3.360 px no `home1`.
      Falta variar a cor pelo `ficha_color`, que é a "grade" do enunciado e
      depende dos 15 handlers daquele formulário
- [ ] `grabar_camisetaClick` byte-idêntico, sem tolerância, com spec em
      `wte/re/spec/MainForm.grabar_camisetaClick.md` e golden verde. **O
      formato do gate já está decidido:** ele emite arquivo e deixa a ROM
      intacta, então é `--artefato`, como o
      [`golden-07-mcr`](../../wte/tests/roteiros/golden-07-mcr.txt) — comparar
      só as imagens aprovaria um port inerte
- [x] **Determinado se `grabar_camisetaClick` escreve setor inteiro ou só
      payload — e a pergunta tinha uma premissa errada embutida.** Ele não
      escreve na imagem de forma nenhuma: **lê** dela e escreve num arquivo. O
      laço é `fread` de 2048, `fwrite` de 2048, `fseek(+304)` — payload puro, e
      `2048 + 304 = 2352` é o setor MODE2 inteiro, ou seja ele **salta**
      cabeçalho e EDC/ECC em vez de copiá-los. Logo EDC/ECC não se aplica, pelo
      mesmo tipo de refutação que fechou o critério irmão da
      [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md). Medido pelo
      `dump_render2d.py`, que recusa se os três `push` mudarem
- [x] **Bandeira e uniforme conferidos na tela contra o original, para os
      mesmos 3 times da [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md)** —
      times 2, 9 e 63, ROM japonesa, por `wte/tools/compara_tela.sh`, em
      2026-08-21. E não por olho: os três `TImage` são **medidos**, porque ali
      não há fonte no meio — é o mesmo bitmap com a mesma paleta dos dois lados.
      Zero divergência nos três
- [ ] Commit no formato conventional, em inglês

### O critério de tela que veio da WTE-TASK-25

*(2026-08-11)*

A 25 pedia comparar a janela carregada contra o original para 3 times. A janela
carregada tem bandeira e uniforme, que são desta task — e esta task depende da
27, que depende da 26, que depende da 25. Ciclo. A 25 cortou o nó restringindo
a conferência dela aos campos que o grupo de carga produz (nomes, barras,
números de camisa, lista de jogadores, habilitação), e **a metade excluída caiu
aqui**.

O ciclo que restava — esta task esperando a gravação da 27, e a 27 esperando o
render daqui — morreu em 2026-08-19, quando `grabar_camisetaClick` passou a ser
desta task. `depends_on` continua `[08, 24, 27]`, e agora todos apontam para
número **menor**: a ordem numérica virou a ordem de execução.

Sem esta linha a exclusão de lá viraria buraco: os dois lados diriam "é da
outra" e ninguém conferiria. As três rotinas envolvidas são `0x00405270`
(bandeira do titular), `0x00405468` (bandeira do reserva) e `0x004056c8`
(uniforme); as duas primeiras estão inventariadas em
[`auxiliares.md`](../../wte/re/auxiliares.md), com tamanho e chamadores.

## Log de Execução

### Terceira passagem, 2026-08-21 — **parcial**: os assets chegam à tela

A task **continua `⬜ Pendente`**. Fecharam três critérios; sobram o
`grabar_camisetaClick`, a grade de cores do `ficha_color` e as specs dos 15
handlers daquele formulário.

- **Resumo do que foi feito:**

  **A cor chegou na tela, e a medida contra o oráculo deu zero.** Três unidades
  novas, com a mesma separação das duas passagens anteriores: a
  `we2002_bmp` cuida do recipiente de 8 bpp (sem LCL, testável headless), a
  `wte_render2d` é a única que precisa de janela, e a `wte_uniformes` é gerada.
  Os handlers `lista_equiposChange` e `lista_equipos_2Change` deixaram de só
  acertar a visibilidade.

  **E apareceu um bug de verdade, do tipo que a task previu.** A primeira
  versão desenhava a camisa com `home_kit[0..14]`; o oráculo usa
  `[1..15]`. **A assimetria bandeira × uniforme não é só de contagem — é de
  início**, e essa metade não se vê olhando o laço: os dois somam 2 ao ponteiro
  a cada volta, e o que muda é onde ele começa. O resultado não era tela em
  branco: era uma camisa colorida, com as cores certas nos lugares errados, que
  passaria por decisão de design para quem não tivesse o original ao lado.

  **A medição não precisou de decompilador, e o original entregou a resposta de
  graça:** ele grava a paleta *dentro* do `.bmp`, então o arquivo que o oráculo
  deixou em disco **é** o resultado. Três pares (arquivo, time) independentes
  casaram com `home_kit[1..15]`; nenhum com `[0..14]`. O `.text` depois
  explicou o porquê — o carregador enche o **slot 0** (`0x432f16` e
  `0x432f36`), copia os 64 bytes para o **slot 1**, e o desenhista lê de
  `0x432f56`, que é exatamente `0x432f16 + 64`. E o dado fecha a conta: nos 190
  conjuntos de uniforme das duas ROMs a palavra 0 é zero — não é cor, é
  enchimento.

  **A régua virou ferramenta, e a recusa foi vista.** O `compara_tela.py`
  ganhou a medida dos três `TImage`: retângulo lido do `.lfm`, calibração que
  já existia, e comparação pixel a pixel. Ali não há fonte no meio — é o mesmo
  bitmap com a mesma paleta dos dois lados —, então divergência é cor errada e
  o veredito é tolerância zero. Com `PRIMEIRA_UNIFORME = 0` de volta, o mesmo
  teste acusa 2.008 de 3.360 px no `home1`.

  **E o golden vermelho era meu, não do port.** O `golden-13-roundtrip` falhou
  com 443 bytes de diferença no `.mcr`, e a suspeita óbvia era regressão desta
  passagem. Não era, e nem era falha pré-existente: o roteiro do lado port
  espera o cartão de entrada em `WTE_MCR_ENTRADA`, que o `golden_check.sh` não
  semeia — quem semeia é o invocador. Sem a variável o import não acontece, o
  `port-trace.log` não traz `boton_mcr2isoClick`, e o port exporta o time como
  estava. Com `WTE_MCR_ENTRADA=$PWD/work/entrada.mcr` passa byte-idêntico. O
  trace foi o que resolveu em um minuto o que o diff de bytes não resolvia.

- **A divergência deliberada, e ela é antiga:** o port **não** grava a paleta
  no `.bmp` do usuário. Recolorir em memória é a recomendação da seção 6.2 do
  `assets.md`, e a razão é concreta — a pasta de assets aqui é um symlink para
  a pasta do Obocaman. A segunda, menor, é o cache: o original relê o arquivo a
  cada redesenho porque para ele o arquivo *é* o estado; aqui ele é só a forma.

- **Arquivos criados/modificados:**
  - criados: `wte/src/we2002_bmp.pas`, `wte/src/wte_render2d.pas`,
    `wte/src/wte_uniformes.pas` (gerado), `wte/tests/test_bmp.pas`
  - modificados: `wte/src/we2002_render.pas` (o tipo do bloco de cores e as
    duas constantes de início), `wte/src/impl/ep2002_mainform.aux.inc` (os três
    auxiliares de dado), os dois `.inc` de troca de time,
    `wte/src/impl/ep2002_mainform.uses`, `wte/src/ep2002_mainform.pas`
    (gerado), `wte/tools/dump_render2d.py`, `wte/tools/test_dump_render2d.py`,
    `wte/tools/compara_tela.py`, `wte/re/render2d.{md,tsv}` (gerados), as duas
    specs de troca de time, `wte/re/fase-2.md` (gerado), os dois `README.md`,
    a §4.4 do plano e o `progresso.md`

- **Gates medidos nesta passagem:**

  | gate | resultado |
  |---|---|
  | `make -C wte check` | exit 0 |
  | `make -C wte test` | 681 testes, OK |
  | `lazbuild wte/wte.lpi` | compila |
  | `test_bmp.pas` | 27 casos sintéticos, 31 com um `.bmp` real |
  | `compara_tela.sh 2 9 63` | 0 de 8.960 px (9.800 no time 63), desvio de canal 0 |
  | mutação `PRIMEIRA_UNIFORME = 0` | **recusa vista**: 2.008/3.360 px no `home1` |
  | `golden-01-arranque` | controle e golden byte-idênticos |
  | `golden-03-barras` | controle e golden byte-idênticos |
  | `golden-13-roundtrip` | controle e golden byte-idênticos, artefato incluído |

  Três roteiros, não os treze: esta passagem não toca byte de imagem, e os três
  escolhidos cobrem arranque, gravação com troca de time e o par
  import/export — todos passam pelos handlers que mudaram.

- **O que ficou pendente:**
  - os 15 handlers de `ficha_color`, com spec, e com eles a **grade de cores**
    do diff de bitmap;
  - o golden `--artefato` do `grabar_camisetaClick`.

- **Problemas encontrados:** os dois descritos acima — o `home_kit[1..15]` e o
  `WTE_MCR_ENTRADA`. Mais um terceiro, pequeno e caro: um parâmetro chamado
  `jogo` **sombreia** a global `Jogo`, porque Pascal é insensível a caixa, e o
  compilador reclama `Illegal qualifier` na linha do `Jogo.teams` — que é onde
  o erro não está. O parâmetro passou a se chamar `qual`, como no
  `BarraDoTime`.

### Segunda passagem, 2026-08-20 — **parcial**: o Pascal da aritmética

A task **continua `⬜ Pendente`**. Nenhum critério fechou inteiro nesta
passagem; o que ela entrega é a metade da cor que dá para provar sem janela.

- **Resumo do que foi feito:**

  **`we2002_render.pas`, e ele não desenha.** A unidade não usa LCL, não abre
  arquivo e não sabe o que é um `TBitmap` — só decodifica, escurece, clareia e
  interpola. A separação é a do `src/core/` do `newWe2002`, e a razão é
  prática: teste de cor que precise de janela é teste que não roda no gate.

  **O guard fecha o círculo, e ele extrai em vez de reafirmar.** O
  `dump_render2d.py --check` já conferia que certos padrões de instrução
  existem; agora ele **lê o operando** de cada um e o compara com a constante
  correspondente da unidade. A diferença importa: um `shl` que virasse `shl 4`
  continuaria casando com um padrão escrito frouxo e sairia como 4. Sete
  constantes vêm assim; a oitava — `BMP_CABECALHO` — é a única que não se
  extrai, porque um `push imm8` sozinho não diz para que serve, e a
  conferência dela vai na direção contrária: o Pascal afirma 54 e o `.exe` tem
  de conter `push 54` dentro das três rotinas de desenho.

  **E um guard que não é sobre número:** a unidade não pode conter
  `Round(acumulado`. É grep, é barato, e é exatamente o risco da §9 acontecendo
  em silêncio.

  **A `Rampa` tinha um off-by-one, e o disassembly o pegou antes do teste.** A
  primeira versão preenchia `n` entradas com a última igual à ponta final; o
  laço do original vai de `ini + 1` até `fim - 1` (`cmp ebx,[0x433dd0]` com
  `jl`) e preenche só o **miolo**. Escrever `n` entradas apagaria a cor que o
  usuário escolheu na ponta.

  **O confronto Pascal × Python precisou de `Single` emulado.** O `float` do
  Python é duplo, e a referência divergiria do Pascal por um motivo que não
  existe no binário — então a referência passa cada operação por
  `struct.pack("<f", …)`. E o caso de teste é escolhido para que truncar
  **morda**: uma rampa que divida certinho não distingue `Trunc` de `Round`, e
  o confronto passaria com o port errado. O próprio teste verifica isso antes
  de confrontar.

- **Arquivos criados/modificados:**
  - criados: `wte/src/we2002_render.pas`, `wte/tests/test_render.pas`
  - modificados: `wte/tools/dump_render2d.py` (o guard do Pascal e a seção nova
    do markdown), `wte/tools/test_dump_render2d.py`, `wte/re/render2d.md`
    (gerado), `wte/re/fase-2.md` (gerado — a unidade nova entra na lista de
    fora-da-casca), `wte/tools/README.md`, `wte/tests/README.md`

- **Gates medidos nesta passagem:**

  | gate | resultado |
  |---|---|
  | `dump_render2d.py --check` | verde; **três recusas vistas** (constante trocada, passo trocado, `Round` no lugar de `Trunc`) |
  | `test_dump_render2d.py` | 25 testes, verde |
  | `test_render.pas` | 31 casos, verde |
  | `make -C wte check` | exit 0 |
  | `make -C wte test` | 670 testes, OK |
  | `lazbuild wte/wte.lpi` | compila |

  **O golden continua sem rodar, e continua certo:** a unidade nova ainda não
  tem chamador — nenhum handler mudou, e nenhum byte que o gate mede passa por
  ela.

- **O que ficou pendente:**
  - ligar a unidade aos handlers de `ficha_color` e às três rotinas de desenho,
    com `TLazIntfImage`;
  - o diff de bitmap sobre grade de cores, com tolerância medida;
  - as specs dos 15 handlers;
  - o golden `--artefato` do `grabar_camisetaClick`;
  - a conferência de tela dos 3 times herdada da WTE-TASK-25.

- **Problemas encontrados:** o off-by-one da `Rampa`, descrito acima. Achado ao
  reler o laço do original para escrever o cabeçalho da função — que é o
  argumento para escrever o cabeçalho antes do corpo.

### Primeira passagem, 2026-08-20 — **parcial**: o algoritmo, medido

A task **continua `⬜ Pendente`**. Fecharam os três critérios que o próprio
enunciado manda fechar *antes* de escrever código; o que falta é Pascal e gate.

- **Executado em:** 2026-08-20

- **Resumo do que foi feito:**

  **As três perguntas do enunciado tinham resposta no `.text`, e nenhuma
  precisou de decompilador.** São padrões de instrução curtos e inequívocos, e
  o [`dump_render2d.py`](../../wte/tools/dump_render2d.py) os lê e **recusa**
  emitir markdown se algum deixar de aparecer — 17 assinaturas, com as duas
  recusas vistas.

  **É paleta, e não varredura de pixel.** As três rotinas de desenho
  posicionam o `.bmp` em `0x36` — o fim do cabeçalho de 54 bytes — e reescrevem
  as primeiras entradas. Isso já estava na seção 6 do `assets.md`; o que é novo
  é a **assimetria**: a bandeira reescreve 16 entradas e o uniforme reescreve
  **15**, duas vezes, uma por arquivo. O `assets.md` dizia "idem, 16 entradas,
  por arquivo" para o uniforme, e foi corrigido. É o erro fácil desta task: as
  três rotinas se parecem o bastante para alguém escrever um laço só.

  **Não há espaço de cor.** Escurecer e clarear decodificam a palavra só para
  testar o limite e depois somam ou subtraem direto no `DWORD` BGR555
  empacotado: `1`, `0x20`, `0x400`. O teto do clarear é `0xF8`, e `0xF8` é
  `31 << 3` — o que prova de quebra que a expansão de 5 para 8 bits é
  **deslocamento**, saturando em 248 e não em 255. Um port que expandisse com
  `v * 255 / 31` teria branco diferente em toda camisa clara.

  **O risco nomeado da §9 tem duas causas, não uma.** O passo do gradiente é
  guardado em `Single` (`fstp DWORD`), e a conversão para inteiro **trunca para
  zero** — o arredondador da RTL põe `0xc01` no control word do 387 antes do
  `fistp`, e os bits 10–11 em `11` são *round toward zero*. E a soma final não
  recompõe a palavra canal a canal: soma os deslocamentos truncados **sobre a
  palavra de partida**. O teste executa as duas formas e mostra que divergem de
  um degrau — o risco provado em vez de afirmado.

  **E o enunciado tinha uma premissa errada.** Ele dizia que
  `grabar_camisetaClick` grava na imagem, e por isso seria a segunda gravação a
  provar EDC/ECC. Medido, não é: ele abre o destino em `"wb"`, **lê** da imagem
  e escreve num arquivo, terminando com `O uni foi salvo!!!.`. O laço é payload
  puro — `fread` 2048, `fwrite` 2048, `fseek(+304)` —, e `2048 + 304 = 2352`,
  o setor inteiro: ele **salta** cabeçalho e EDC/ECC em vez de copiá-los. Logo
  o critério de EDC/ECC não se aplica, e o golden deste handler é do formato
  `--artefato`, como o do `grabar_memory`. É a segunda vez seguida que um
  critério de EDC/ECC fecha por refutação; a primeira foi na WTE-TASK-28.

- **Arquivos criados/modificados:**
  - criados: `wte/tools/dump_render2d.py`, `wte/tools/test_dump_render2d.py`,
    `wte/re/render2d.md` (gerado), `wte/re/render2d.tsv` (gerado)
  - modificados: `wte/re/assets.md` (a correção do 16 → 15),
    `wte/tools/README.md`, este arquivo

- **Gates medidos nesta passagem:**

  | gate | resultado |
  |---|---|
  | `dump_render2d.py --check` | verde, 17 assinaturas conferidas |
  | `test_dump_render2d.py` | 17 testes, verde; as duas recusas vistas |
  | `make -C wte check` | exit 0 |
  | `make -C wte test` | 662 testes, OK |
  | `lazbuild wte/wte.lpi` | compila |

  **O golden não foi rodado, e não deveria ser:** esta passagem não tocou uma
  linha de Pascal. O último estado medido é o do commit da WTE-TASK-28, com
  `golden-12` e `golden-13` verdes.

- **O que ficou pendente, e é o grosso:**
  - `we2002_render.pas` e `test_render.pas` — o Pascal do formato;
  - o diff de bitmap sobre grade de cores, com tolerância medida;
  - as specs dos 15 handlers de `ficha_color`;
  - o golden do `grabar_camisetaClick`, que agora se sabe ser `--artefato`;
  - a conferência de tela de bandeira e uniforme para os 3 times herdados da
    WTE-TASK-25.

- **Problemas encontrados:** o descrito acima — dois documentos afirmavam coisa
  que o binário não sustenta (o "16 entradas" do `assets.md` e o "grava na
  imagem" do enunciado desta task). Os dois eram generalização plausível, e os
  dois agora têm ferramenta que recusa se o número mudar.
