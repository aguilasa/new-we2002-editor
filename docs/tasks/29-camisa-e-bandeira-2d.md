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
| `wte/re/render2d.md` | criar — algoritmo, espaço de cor, tolerância medida |
| `wte/src/we2002_render.pas` | criar |
| `wte/tests/test_render.pas` | criar |

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
- [ ] `TLazIntfImage` usado; render em tempo real sem travar a janela
- [ ] Diff de bitmap sobre grade de cores, com tolerância **medida** e causa nomeada
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
- [ ] **Bandeira e uniforme conferidos na tela contra o original, para os mesmos
      3 times da [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md)** — herdado
      dela em 2026-08-11, ver abaixo
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
