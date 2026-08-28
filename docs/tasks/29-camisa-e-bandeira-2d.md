---
id: WTE-TASK-29
title: "Camisa e bandeira 2D em tempo real, com colar-cores"
type: implementação
category: features
phase: 4
depends_on: ["WTE-TASK-08", "WTE-TASK-24", "WTE-TASK-27"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md §5.3 e §9"
status: concluído
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

Formulário `ficha_color`: 866 linhas de DFM (`wc -l
wte/re/dfm/ficha_color.dfm`).

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
| `wte/re/render2d.md` | criar — feito (algoritmo e espaço de cor; a tolerância medida está no log da sexta passagem, porque ela é resultado de execução e não saída de gerador) |
| `wte/tools/dump_render2d.py`, `wte/tools/test_dump_render2d.py` | criar — feito |
| `wte/src/we2002_render.pas` | criar — feito (a aritmética de cor) |
| `wte/src/we2002_bmp.pas` | criar — feito (o recipiente de 8 bpp) |
| `wte/src/wte_render2d.pas` | criar — feito (o `TLazIntfImage` e o cache) |
| `wte/src/wte_uniformes.pas` | criar — feito (gerado: as duas tabelas de `.data`) |
| `wte/tests/test_render.pas`, `wte/tests/test_bmp.pas` | criar — feito |
| `wte/tools/compara_tela.py` | estender — feito (a medida dos três `TImage`) |
| `wte/src/impl/ep2002_mainform.grabar_camisetaClick.inc` | criar — feito |
| `wte/tests/roteiros/golden-14-uniforme{,.port}.txt` | criar — feito |
| `wte/src/wte_cor.pas` | criar — feito (o estado do editor de cor) |
| `wte/src/impl/ep2002_color.*.inc`, `ep2002_mainform.colorearClick.inc` | criar — feito (os 11 de edição, mais o `FormCreate`, o `botonClick` e o `aux.inc`; os 4 restantes do formulário são da [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md)) |
| `wte/tools/compara_tela.{sh,py}` | estender — feito (o modo `--grade`, a régua da tolerância) |

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
- [x] **Diff de bitmap sobre grade de cores, com tolerância medida e causa
      nomeada — a tolerância é ZERO, e não há causa a nomear.** As três medidas
      fecharam. As duas primeiras mediam a paleta *como ela veio da imagem*:
      `bandera`, `home1` e `home2` recortados pelo `.lfm` (times 2, 9 e 63:
      **0 de 8.960 px**, 9.800 no clube de ML) e `--cor`, as **16 amostras**
      do editor (**0 de 5.168 px**). A terceira é a grade do enunciado, e ela
      mede depois de **calcular**: `compara_tela.sh --grade` clica três vezes
      em escurecer, uma em clarear e uma no gradiente, nos dois lados, e
      compara as 16 amostras **e** os três `TImage`. Nos mesmos três times:
      **16 de 16 amostras mudaram** dos dois lados, e a divergência é
      **0 de 5.168 px** nas amostras e **0 de 8.960** (9.800 no de ML) no
      bitmap. As recusas foram **vistas**, e são quatro ao todo:
      `PRIMEIRA_UNIFORME = 0` acusa 2.008 de 3.360 px no `home1`; trocar R por
      B no `TColor` da amostra acusa 8 das 16; o `oscurecer` com a faixa
      **aberta** em vez de fechada acusa 12 das 16 amostras e 3.792 de 3.840 px
      da bandeira; e o gradiente escrevendo a partir da ponta em vez do miolo
      acusa 15 das 16
- [x] **`grabar_camisetaClick` byte-idêntico, sem tolerância** — spec em
      [`MainForm.grabar_camisetaClick.md`](../../wte/re/spec/MainForm.grabar_camisetaClick.md),
      golden [`golden-14-uniforme`](../../wte/tests/roteiros/golden-14-uniforme.txt)
      verde com o controle antes. **30.956 bytes idênticos nos dois lados, e a
      imagem intacta nos dois.** O gate é `--artefato`, como o
      [`golden-07-mcr`](../../wte/tests/roteiros/golden-07-mcr.txt): comparar
      só as imagens aprovaria um port inerte, porque nenhum dos dois lados as
      toca. A recusa foi **vista** — tirando o `+ 32` do campo de tamanho o
      artefato sai com 30.924 bytes
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
- [x] **Os dois `malla` do `estrategia`, com veredito** — `malla1MouseDown`
      (`0x00409f4c`) e `malla2MouseDown` (`0x0040a000`), os dois
      `implementado`. Eles estão na tabela de alvos desta task porque o
      `published_methods.tsv` os atribui a ela, e **não são cor**: o X escolhe a
      coluna e o Y a linha, e o marcador daquela coluna desce para
      `malla.Top + (Y div 16)*16 + 3`. Os três números saem do `.text` pelo
      `dump_zonas.py`, que os confere contra o `.lfm` em quatro pontos por
      malha; e o efeito do clique foi medido contra o oráculo pelo
      `compara_tela.sh --malha`: **só a coluna clicada anda, e anda 80 px nos
      dois lados**. Duas recusas vistas — X trocado por Y move o `simbolo4` em
      16 px e deixa o `simbolo2` parado; sem o arredondamento o delta vira 88
- [x] **Os 11 handlers de edição do `ficha_color`, com spec cada** — entraram na
      sexta passagem, com o `botonClick` completado de 2 para 5 movimentos. Os
      outros quatro do formulário (`BitBtn1..3Click`, `SpeedButton1Click`) são
      da [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) pela tabela "o que
      fica de fora" dela, que nomeia exatamente estes 11 como desta task
- [x] Commit no formato conventional, em inglês

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

### Sétima passagem, 2026-08-21 — **fecha**: as duas malhas do campinho

A task passa a `✅ Concluído`. O que faltava era o par `malla` do `estrategia`,
que o `published_methods.tsv` atribui aqui e que não é cor: é geometria.

- **Resumo do que foi feito:**

  **Os dois handlers são 180 bytes cada e a mesma sequência de instruções**, com
  dois imediatos de diferença — a cadeia do prefixo (`"simbolo"` contra
  `"tirador"`) e o campo da `TImage` (`[this+0x384]` contra `[this+0x398]`). O
  original não fatorou; o port fatorou em `MoveMarcadorDaMalha`, e os dois
  números que diferem entram por parâmetro.

  **Os três números não foram digitados.** `24`, `16` e `3` saem do `.text` pelo
  [`dump_zonas.py`](../../wte/tools/dump_zonas.py), que ganhou um decodificador
  de malha, e vão para a `wte_zonas.pas` como `MALHA_PASSO_X`, `MALHA_PASSO_Y` e
  `MALHA_FOLGA`. O que lhes dá valor não é a extração — é a **conferência contra
  o `.lfm`**, que é outra fonte e tem de fechar em quatro pontos por malha:
  `malla.Width div passo` = quantos marcadores existem, `marcador1.Left` =
  `malla.Left + folga`, `marcador1.Top` = `malla.Top + folga`, e o passo de
  `Left` entre marcadores vizinhos. Uma folga errada quebra as duas do meio; um
  passo errado quebra a primeira e a quarta.

  **E o `MALHA_PASSO_Y` não é um imediato:** ele sai do deslocamento do par
  `sar ecx,N` / `shl ecx,N`, e o gerador exige que os dois `N` sejam iguais — um
  arredondamento que descesse e subisse por valores diferentes não seria
  arredondamento.

  **A régua de tela virou modo versionado.** A primeira medição foi um script
  descartável, e o número que ela produziu ia para documento — que é exatamente
  a armadilha 11 do `progresso.md`. Virou `compara_tela.sh --malha`: leva os
  dois lados ao mesmo time, abre o campinho, clica na coluna 2 linha 5 da
  `malla1`, e compara o **delta** de cada um dos quatro marcadores.

- **Duas coisas que a medição de tela ensinou, e nenhuma se via no
  disassembly:**

  1. **A janela do campinho não se acha pelo nome.** O `.dfm` diz
     `Caption = 'Estrategia'`, e o oráculo o reescreve no arranque com o nome do
     time em Shift-JIS — sob Wine o título sai `'   ?????'`. O port mantém o do
     formulário. Achar por nome funcionaria de um lado só, que é pior do que não
     funcionar de nenhum; os dois são achados pelo **tamanho**, como o
     `roteiro.sh` já faz com a janela principal.
  2. **As posições de partida divergem, e comparar posição mediria outra
     task.** O oráculo carrega a posição de cada marcador da imagem (a rotina
     interna `0x0040a0b4`, não portada) e o port deixa os quatro no default do
     `.dfm` — no time 2 o oráculo mostra `316/380/460` e o `simbolo1` nem
     aparece dentro da malha. **O handler não lê a posição corrente**, ele a
     calcula a partir do `Top` da malha, então o delta é comparável mesmo com
     pontos de partida diferentes. A régua compara delta, e só exige presença da
     coluna clicada.

- **A conferência que decidiu qual parâmetro é o X.** Na convenção da Borland o
  `Self`, o `Sender` e o `Button` vão em EAX, EDX e CL, e o `Shift`, o `X` e o
  `Y` sobram na pilha. Quem diz qual é qual não é este handler: é o
  `bolaMouseDown`, que guarda os dois num `TPoint` global (`0x0043434c`) e assim
  fixa `[ebp+0xc]` como X e `[ebp+0x8]` como Y. Trocados, o handler compila,
  roda e move o marcador errado para a altura errada — e foi a primeira das duas
  mutações.

- **Arquivos criados/modificados:**
  - criados: `wte/src/impl/ep2002_estrategia.malla{1,2}MouseDown.inc`,
    `wte/re/spec/estrategia.malla{1,2}MouseDown.md`, `wte/re/malhas.tsv`
    (gerado)
  - modificados: `wte/tools/dump_zonas.py` (o decodificador de malha e as
    quatro conferências), `wte/tools/test_dump_zonas.py` (9 casos novos, cinco
    deles recusas — `diff` dos `def test_` entre `671a1f9^` e `671a1f9`),
    `wte/src/impl/ep2002_estrategia.aux.inc`
    (`MoveMarcadorDaMalha`), `wte/src/wte_zonas.pas` e `wte/re/zonas.md`
    (gerados), `wte/src/ep2002_estrategia.pas` (gerado),
    `wte/tools/compara_tela.{sh,py}` (o modo `--malha`),
    `wte/re/spec/INDICE.md` e `wte/re/fase-2.md` (gerados),
    `wte/tools/README.md`, a §4.4 do plano e o `progresso.md`

- **Gates medidos nesta passagem:**

  | gate | resultado |
  |---|---|
  | `compara_tela.sh --malha` | **só a coluna clicada anda, 80 px nos dois lados** |
  | mutação: X trocado por Y | **recusa vista**: `simbolo4` anda 16, `simbolo2` fica parado |
  | mutação: sem o arredondamento do Y | **recusa vista**: 88 px em vez de 80 |
  | `dump_zonas.py --check` | verde; **cinco recusas** cobertas por teste (passo, folga, prefixo, constantes divergentes, ordem das guardas) |
  | `golden-01-arranque` | controle e golden byte-idênticos |
  | `golden-03-barras` | golden byte-idêntico |
  | `make -C wte check` | exit 0 |
  | `make -C wte test` | 695 testes, OK |
  | `lazbuild wte/wte.lpi` | compila |

  As specs saíram de 75 para **77 de 96**; os `aberto` caíram de 36 para 34.

- **O que fica para outra task, com dono nomeado:** a rotina interna
  `0x0040a0b4`, que carrega a posição dos marcadores da imagem, e o
  `estrategia.BitBtn3Click` (`0x0040a660`), que a lê de volta — as duas metades
  do caminho de dado que este par alimenta. As duas são da
  [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md).

- **Problemas encontrados:** um autoinfligido e caro. `git checkout` num
  `.inc` **não commitado** não desfaz a mutação: apaga o arquivo inteiro de
  volta ao `HEAD`, e o `MoveMarcadorDaMalha` sumiu junto. O sintoma foi o gate
  continuar acusando a mutação já revertida. Para desfazer edição de arquivo
  novo, `cp` da cópia de segurança — nunca `git checkout`.

### Sexta passagem, 2026-08-21 — **parcial**: o editor de cor edita, e a grade fecha

A task **continua `⬜ Pendente`**, e o que sobra agora é de outro formulário.
Os 11 handlers de edição do `ficha_color` entraram, o `botonClick` foi
completado, e com eles o último critério de medida da task fechou.

- **Resumo do que foi feito:**

  **A grade de cores do enunciado existe, e a tolerância dela é zero.** O
  `compara_tela.sh` ganhou o modo `--grade`, e a diferença dele para o `--cor`
  é a única que importa: o `--cor` mede a paleta **como ela veio da imagem** —
  prova que os dois lados leem a mesma fonte e não prova nada sobre a
  aritmética, porque nenhuma cor foi calculada. O `--grade` clica antes de
  medir. Três em escurecer, um em clarear, um no gradiente: as três operações
  da `we2002_render` exercitadas pela tela, com o piso, o teto e o truncamento
  todos mordendo.

  **A escolha dos botões em vez das barras foi medida, e não estética.** Clicar
  na trilha de um `TScrollBar` pagina por `LargeChange`, e o passo do comctl32
  sob Wine não é o do gtk2 — o `--edicao` teve de medir que os dois andavam +2
  antes de poder comparar. Cada clique de botão é uma operação inteira e
  determinística, e não depende de widgetset nenhum.

  **A guarda que o modo precisava ter, e o `--cor` não precisava:** medir
  depois de editar aprova um port inerte se os cliques não chegarem — as duas
  capturas ficam iguais e a comparação sai verde sem ter medido conta nenhuma.
  Então o **antes** entra como pré-condição: a cor do oráculo tem de ter mudado,
  e a do port também, e os dois têm de ter mudado **as mesmas amostras**. Do
  lado do port a mesma coisa é conferida por outro caminho, contando disparo no
  trace, e as duas medidas são independentes de propósito.

  **O `botonClick` tinha dois dos cinco movimentos, e o que faltava doía.** A
  quinta passagem portou a família e o repinte; faltavam a gravação de volta na
  fonte anterior (`0x00405b48`, que o original chama de **quatorze** lugares e
  este port chamava de nenhum), o `conjunto` e a visibilidade dos combos. Sem a
  primeira, editar a bandeira e clicar em "Unifo. 2D" **perdia a edição** — e o
  sintoma só aparece quando o usuário volta, que é o pior tipo.

  **E uma nota de spec que tinha caducado sem ninguém notar.** A spec do
  `MainForm.FormCreate` classificava as três últimas instruções do original —
  que guardam os ponteiros de `bandera`, `home1` e `home2` em globais — como
  "detalhe de implementação em C++ sem efeito observável, porque em Pascal os
  três se alcançam pelo campo do formulário". **Isso valia enquanto só o
  `MainForm` desenhava.** Os handlers do `ficha_color` também redesenham, e dali
  os campos não se alcançam: `ep2002_mainform` já usa `ep2002_color`, então a
  volta fecharia ciclo de `uses` de interface. As globais do original são
  exatamente a indireção que resolve isso, e o port passou a tê-las
  (`RegistraImagensDoEditor`).

- **Três leituras que quase saíram erradas, e as três se corrigiram com uma
  segunda fonte:**

  1. **`barra1` é o início e `barra2` é o fim**, e o `.dfm` os declara na ordem
     inversa. Quem decide não é a ordem de declaração: é a *published field
     table* (`re/campos.tsv`), e ela diz `0x360 = barra2`, `0x364 = barra1`.
     Contar componentes na ordem do `.dfm` dava o mesmo resultado em três dos
     alvos desta passagem e **o oposto** neste — e a faixa do gradiente sairia
     invertida.
  2. **O `lista_col3Change` parecia escrita morta.** Os dois bytes que ele
     escreve (`0x004331d8`/`d9`) têm três referências cada no `.text`, e todas
     as seis estão dentro do próprio handler. A conclusão fácil está errada: o
     par é indexado em outro lugar com passo dois
     (`mov dl,[eax*2+0x004331d6]`), ou seja `d6`/`d7` é o slot 0 e `d8`/`d9` é o
     slot 1 — o mesmo par de slots que o resto do estado visual usa. O slot 0
     é lido da imagem e devolvido a ela pela gravação do `BitBtn3`. **Busca por
     endereço literal não prova ausência de leitura.**
  3. **O `colorMouseDown` testa `boton0` duas vezes na cauda**, e no segundo
     teste redesenha o *uniforme*. É defeito do original, está reproduzido, e a
     spec diz por quê: o gate compara pixel, e "corrigir" produziria divergência
     em vez de fidelidade.

- **A divergência deliberada da passagem anterior fica, e agora com a metade
  portada:** o `lista_col3` continua no default do formulário, porque o par de
  bytes de padrão de camisa não tem campo na camada de dados. O que mudou é que
  a **escrita** passou a existir — o port guarda os dois em
  `wte_cor.PadraoDaCamisa`, e nada os lê ainda. O único consumidor no original
  é a gravação do `BitBtn3`, que é da WTE-TASK-30. Guardá-los agora é o que faz
  aquela gravação ser possível sem reabrir este handler.

  A segunda divergência é a **família 2 (chuteira)**: o `lista_col2Change`
  escreve o `conjunto` como o original, e o preenchimento devolve `False` sem
  pintar em vez de cair no laço com o ponteiro de fonte não inicializado. Entrada
  para a [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md), junto com a
  primeira.

- **Arquivos criados/modificados:**
  - criados: os 11 `wte/src/impl/ep2002_color.<handler>.inc`,
    `wte/src/impl/ep2002_color.aux.inc`, e as 11 specs
    `wte/re/spec/ficha_color.*.md`
  - modificados: `wte/src/wte_cor.pas` (`SalvaPaleta`, `CoresEmVigor`,
    `FormaEmVigor`, `SalvaFormaDaBandeira`, o cola-cores e o padrão de camisa),
    `wte/src/wte_render2d.pas` (`PintaUmaAmostra`, `RepintaAmostras`, o
    registro dos três `TImage` e os dois redesenhos em vigor),
    `wte/src/impl/ep2002_color.{botonClick.inc,uses}`,
    `wte/src/impl/ep2002_mainform.FormCreate.inc`,
    `wte/src/ep2002_{color,mainform}.pas` (gerados),
    `wte/tools/compara_tela.{sh,py}` (o modo `--grade`),
    `wte/tools/test_compara_tela.py` (5 casos novos),
    `wte/re/spec/{ficha_color.botonClick.md,INDICE.md}`,
    `wte/re/fase-2.md` (gerado), `wte/tools/README.md`, a §4.4 do plano e o
    `progresso.md`

- **Gates medidos nesta passagem:**

  | gate | resultado |
  |---|---|
  | `compara_tela.sh --grade 2 9 63` | **0 de 5.168 px** nas amostras e 0 de 8.960 (9.800 no 63) no bitmap; 16/16 amostras mudaram dos dois lados |
  | mutação: `oscurecer` com faixa aberta | **recusa vista**: 12 das 16 amostras, 3.792/3.840 px da bandeira |
  | mutação: gradiente a partir da ponta | **recusa vista**: 15 das 16 amostras |
  | `golden-01-arranque` | controle e golden byte-idênticos |
  | `golden-03-barras` | golden byte-idêntico |
  | `golden-13-roundtrip` | golden byte-idêntico, artefato de 131.072 B igual |
  | `golden-14-uniforme` | controle e golden byte-idênticos, artefato de 30.956 B igual |
  | `make -C wte check` | exit 0 |
  | `make -C wte test` | 686 testes, OK |
  | `lazbuild wte/wte.lpi` | compila |

  As specs saíram de 60 para **75 de 96**; os `aberto` caíram de 47 para 36.

- **O que ficou pendente, e é de outro formulário:** os dois `malla`
  (`malla1MouseDown` em `0x00409f4c` e `malla2MouseDown` em `0x0040a000`), que
  o `published_methods.tsv` atribui a esta task. Eles são do `estrategia`, não
  do `ficha_color`, e **não são cor**: cada um acha `simbolo<Y div 24 + 1>` por
  nome e lhe dá `Top := malla1.Top + (X div 16)*16 + 3` — geometria do campinho
  tático. Fechá-los pede régua de tela para o `estrategia`, que é instrumento
  novo.

  Os quatro handlers restantes do `ficha_color` — `BitBtn1Click`,
  `BitBtn2Click`, `BitBtn3Click` e `SpeedButton1Click` — **não são desta task**:
  a tabela "o que fica de fora" da
  [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) nomeia exatamente os 11
  que entraram aqui e deixa a moldura do formulário para ela. O `BitBtn3` é
  gravação de verdade (`0x004051a4` escreve na imagem) e vai precisar de roteiro
  golden próprio.

- **Problemas encontrados:** os três de leitura descritos acima. Mais um de
  invocação, que custou uma corrida: o `golden_check.sh` **não deriva** o
  `.port.txt` do nome do roteiro — sem `--roteiro-port` ele dirige o lado port
  com o roteiro do oráculo, que procura o diálogo `Abre` e falha em 30 s com
  "janela 'Abre' nao apareceu". O sintoma parece regressão do port e não é.

### Quinta passagem, 2026-08-21 — **parcial**: o editor de cor abre

A task **continua `⬜ Pendente`**. Três dos 17 handlers do `ficha_color`
entraram, e com eles o estado que a spec do `FormCreate` tinha adiado *para
esta task*. Falta variar a cor.

- **Resumo do que foi feito:**

  **A decisão que estava esperando há três tasks foi tomada.** A spec do
  `ficha_color.FormCreate` dizia, com todas as letras, que escrever aquele
  corpo antes de decidir onde os cinco globais do editor moram seria inventar,
  e que a decisão era desta task. Eles moram em
  [`wte_cor.pas`](../../wte/src/wte_cor.pas), e cada um tem nome: `familia`,
  `conjunto`, `entrada`, `faixa_ini`, `faixa_fim`.

  **E o alias que quase passou batido:** o vetor das 16 palavras fica em
  `0x00433dd4`, e o pintor de amostra escreve em `[indice*4 + 0x00433dd0]` com
  `indice` de **1** a 16 — ou seja o `faixa_fim` **é** o elemento zero do
  vetor, e os dois só não colidem porque o pintor começa em 1. As bases
  divergem por isso: `entrada` conta de zero e `faixa_*` contam de um. Um port
  que uniformizasse as bases erraria a faixa do gradiente em um degrau.

  **As quatro famílias foram medidas; duas foram portadas.** O `botonClick` não
  olha o `Sender` como objeto: recorta o sexto caractere do `Name` (`"boton"`
  tem cinco letras) e converte para inteiro — o dígito **é** a família. Duas
  são bandeira e uniforme; as outras duas são chuteira (`0x00433096`) e uma
  quarta paleta sem combo visível (`0x004331b6`), e nenhuma das duas é camisa
  nem bandeira. Ficaram de fora com endereço escrito. O port **não pinta** nesse
  caso; o original pinta, e desenha lixo — com a família fora de 0..3 ele cai
  no laço com o ponteiro de fonte não inicializado, o que é comportamento
  indefinido e não comportamento.

  **O bug da passagem foi da LCL, não do formato:** as 16 amostras não
  apareciam. O `TLabel` da LCL desenha **transparente por default** e ignora o
  próprio `Color`; a VCL de 2002 não tinha a propriedade separada. Uma linha —
  `Transparent := False` antes da cor — e as 16 apareceram. O diagnóstico
  custou mais do que a correção: o `REMark` provou que o preenchimento tinha
  rodado e devolvido `True`, o que descartou de uma vez a família, o time e o
  `FindComponent`, e sobrou o widgetset.

  **A régua nova é `compara_tela.sh --cor`**, e ela captura a janela do
  **modal**, não a principal: o que muda são as amostras, e elas estão lá
  dentro. Ela conta as cores distintas do lado do oráculo e **reprova** se
  forem menos de duas — 16 amostras da mesma cor significa que o editor não
  abriu ou que o recorte caiu fora dele, e sem essa guarda isso passaria por
  verde.

- **A divergência deliberada, e ela é de tela:** o `lista_col3` — o combo de
  padrão de camisa, `NORMAL`/`ROMBOIDAL`/`EXTRA` — fica no default do
  formulário. O original o escolhe por dois bytes que lê da imagem para
  `0x004331d6`/`0x004331d7`, e esses dois bytes **não estão na camada de
  dados**: nem `TTeam` nem `TMlTeam` têm campo de padrão de camisa, e o
  `we2002_core` é o oráculo de formato deste projeto. Inventar de onde saem
  seria pior do que deixar o default. Entrada para a
  [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md).

- **Arquivos criados/modificados:**
  - criados: `wte/src/wte_cor.pas`,
    `wte/src/impl/ep2002_color.{FormCreate,botonClick}.inc`,
    `wte/src/impl/ep2002_color.uses`,
    `wte/src/impl/ep2002_mainform.colorearClick.inc`,
    `wte/re/spec/MainForm.colorearClick.md`,
    `wte/re/spec/ficha_color.botonClick.md`
  - modificados: `wte/src/wte_render2d.pas` (o pintor de amostra),
    `wte/src/{ep2002_color,ep2002_mainform}.pas` (gerados),
    `wte/src/impl/ep2002_mainform.uses`,
    `wte/tools/compara_tela.{sh,py}` (o modo `--cor`),
    `wte/re/spec/ficha_color.FormCreate.md` (veredito e a decisão que ela
    adiava), `wte/re/spec/INDICE.md` e `wte/re/fase-2.md` (gerados), a §4.4 do
    plano e o `progresso.md`

- **Gates medidos nesta passagem:**

  | gate | resultado |
  |---|---|
  | `compara_tela.sh --cor` (2, 9, 63) | **0 de 5.168 px**, 11/9/8 cores distintas |
  | mutação: R e B trocados no `TColor` | **recusa vista**: 8 das 16 amostras |
  | `compara_tela.sh 2` | bandeira e uniforme seguem em 0 de 8.960 px |
  | `make -C wte check` | exit 0 |
  | `make -C wte test` | 681 testes, OK |
  | `lazbuild wte/wte.lpi` | compila |

  **O golden não rodou, e continua certo:** nenhum dos três handlers escreve
  byte de imagem. O último estado medido é o do commit anterior, com
  `golden-01`, `golden-03`, `golden-13` e `golden-14` verdes.

- **O que ficou pendente:** os 14 handlers de edição do `ficha_color` — as três
  barras, o gradiente, o escurecer/clarear, os quatro combos, o
  `colorMouseDown` (que é o **colar-cores** do título da task, com
  Ctrl+Shift) e os três `BitBtn`. Com eles vem a grade de cores.

- **Problemas encontrados:** o `Transparent` da LCL, descrito acima. Mais um
  susto que valeu a lição: `pkill -f "build/wte work/..."` **mata o próprio
  shell** que roda o comando, porque a linha de comando dele contém o padrão. O
  sintoma foi um comando saindo com 144 e nada acontecendo. `pkill -x wte`
  resolve.

### Quarta passagem, 2026-08-21 — **parcial**: a extração do uniforme

A task **continua `⬜ Pendente`**. Fechou o `grabar_camisetaClick`; sobram os 15
handlers do `ficha_color` e, com eles, a grade de cores do diff de bitmap.

- **Resumo do que foi feito:**

  **O handler é o inverso exato do `boton_tex2isoClick`, literal a literal.**
  Os dois calculam o endereço com a mesma expressão — `19756824 + 47040 *
  (indice + 9 * (indice div 95))` —, e o que muda é a direção. A terceira
  passagem tinha lido `0x12d7718` como 19.755.288 e passou um bom tempo
  procurando explicação para uma diferença de 1.536 bytes contra a região que a
  WTE-TASK-27 já media. **A diferença não existia: era aritmética hexadecimal
  feita de cabeça.** Vale a regra — converter imediato com ferramenta, não com
  a cabeça, mesmo quando "dá para ver".

  **O que não é aritmética é o tamanho, e é a única leitura de dado do
  handler:** dois bytes em `offset + 44`, little-endian, **mais 32**. O `+ 32`
  diz que o campo conta o corpo e não o cabeçalho de 32 bytes que o precede.
  Medido no gate: 30.956 bytes para o time 2, que são 15 blocos de payload
  inteiro mais 236 bytes soltos — os **dois** laços exercitados na mesma
  corrida, o que não era garantido e vale registrar.

  **Os dois laços não são estilo, são estrutura.** O primeiro copia payload
  inteiro e salta os 304 bytes de cabeçalho e EDC/ECC de cada setor; o segundo
  copia `tamanho mod 2048` byte a byte e **não tem salto nenhum** — não precisa,
  porque o primeiro deixou o ponteiro no começo do payload seguinte e o resto
  sempre cabe lá.

  **A recusa do diálogo é contra o `dialogo_tex`, não contra o de gravação.**
  Mesma forma do `grabar_memoryClick`, com o outro par: gravar por cima do
  arquivo que o editor tem aberto para importar apagaria a fonte. O laço tem
  duas portas de saída e só uma leva ao aviso — cancelar sai calado.

  **E o `Xvfb` morreu no meio, sem dizer nada.** O `golden_check.sh` saiu com
  rc 1 e **zero linhas** de saída, inclusive sob `bash -x`: sem servidor, o
  `ps -o args= -C Xvfb` falha, o `set -o pipefail` propaga, e o `set -e` mata o
  script na primeira linha da calibração. Diagnóstico de um comando
  (`xdpyinfo`), mas só depois de procurar bug no lugar errado.

- **A afordância nova, e ela é a terceira da mesma família:** `WTE_UNI` semeia
  o destino do lado port, como `WTE_MCR` faz para o `.mcr`. O
  `golden_check.sh` exporta as **duas** quando há `--artefato`, porque ele não
  sabe qual botão o roteiro clica — a que sobra é inerte.

- **Arquivos criados/modificados:**
  - criados: `wte/re/spec/MainForm.grabar_camisetaClick.md`,
    `wte/src/impl/ep2002_mainform.grabar_camisetaClick.inc`,
    `wte/tests/roteiros/golden-14-uniforme.txt` e `.port.txt`
  - modificados: `wte/src/ep2002_mainform.pas` (gerado — o stub virou
    `{$I}`), `wte/src/we2002_estado.pas`,
    `wte/src/impl/ep2002_mainform.FormShow.inc`,
    `wte/tools/golden_check.sh`, `wte/tools/golden_run_laz.sh`,
    `wte/re/spec/INDICE.md` (gerado), `wte/re/fase-2.md` (gerado),
    `wte/tests/README.md`, a §4.4 do plano e o `progresso.md`

- **Gates medidos nesta passagem:**

  | gate | resultado |
  |---|---|
  | `golden-14-uniforme` **controle** | byte-idêntico; artefato de 30.956 B igual nos dois lados |
  | `golden-14-uniforme` **golden** | byte-idêntico; artefato igual; imagem intacta nos dois |
  | mutação: `+ 32` removido | **recusa vista**: 30.956 contra 30.924 bytes |
  | `make -C wte check` | exit 0 |
  | `make -C wte test` | 681 testes, OK |
  | `lazbuild wte/wte.lpi` | compila |

- **O que ficou pendente:** os 15 handlers de `ficha_color`, com spec, e a
  grade de cores do diff de bitmap — que é a metade que falta do critério de
  tolerância e depende deles.

- **Problemas encontrados:** os dois descritos acima — a conversão hexadecimal
  errada e o `Xvfb` morto.

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
