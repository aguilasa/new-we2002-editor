---
id: LOOKS-TASK-12
title: "Incógnita (d) — pele é troca de paleta ou de cor de vértice?"
type: engenharia-reversa
category: textura
phase: 3
depends_on: ["LOOKS-TASK-11"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §6"
status: concluído
---

# LOOKS-TASK-12: Pele — paleta ou cor de vértice

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §6,
  incógnita (d), e §1.6.
- **Este bullet dizia** que a GPU responde 4-bit CLUT enquanto a primitiva
  carrega *"cor por vértice e nenhum UV"*, e que os dois não podiam valer para
  a mesma geometria. As duas metades caíram, e o bloco no fim deste Contexto
  diz por quê: a primitiva **tem** UV (§1.6, LOOKS-TASK-08), e a profundidade
  **não é sempre 4 bits** — `0x0099` amostra em CLUT de **8 bits**, e são 1.039
  das 2.841 primitivas
  ([`CORR-LOOKS-018`](/docs/tasks/looks/CORR-LOOKS-018.md)). O `4-bit CLUT` do
  `get_gpu_state` é amostra de um desenho, não propriedade do arquivo. **A
  paleta que esta task tem de ler pode ter 16 ou 256 entradas**, e qual delas
  sai da palavra de página da primitiva que a usa.
- Na tela, `SKIN` de `A` para `D` mudou o tom **sem mexer em vértice nenhum** —
  o que é compatível com as duas hipóteses.
- **Decidir isto decide metade da Fase 3**, e a resposta depende da
  LOOKS-TASK-08.
- **Comece por `load_state`.** Os dois states de 2026-09-14 põem o jogo na tela
  de edição: **slot 1 goleiro, slot 2 jogador de linha**, os dois no disco
  inglês. Recarregar entre medições dá baseline byte a byte idêntico, e é o que
  faz o diff medir só o que você mudou.
- **A RAM se lê por MCP vivo.** O `savestate.py` não alcança a RAM nesta
  máquina: sem CLI `zstd` e sem o módulo `zstandard`, ele lê cabeçalho e para.


- **O terceiro controle negativo da §5.5 já existia quando esta task abriu.**
  Este bullet dizia que ele estava em aberto, e **a
  [`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md) o plantou
  em 2026-09-15**, com o nome `texture-clut-any-record`: ignorado o intervalo do
  registro, toda peça resolve para a primeira paleta do arquivo e as chuteiras
  saem da cor da pele. Corrigido 2026-09-15. O que esta task acrescentou foi o
  **segundo** jeito de trocar uma paleta por outra, que o primeiro não alcança:
  `skin-matrix-at-the-record`, a matriz de cabelo começando no registro em vez
  de uma janela adiante — que é o erro escrito no critério abaixo.

---

- **A resposta já foi medida, e esta task começa com ela na mão.** Em
  2026-09-14 a [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md)
  mediu, por `python tools/looks/oracle.py --fields SKIN`, que **cada passo de
  `SKIN` soma `0x40` ao byte baixo do CLUT id** das primitivas da pele — quatro
  valores ao todo, que são as quatro peles do `kSkin[4]`. **É paleta.** Não há
  cor de vértice em jogo: a pergunta desta task nasceu da leitura errada da
  primitiva, que dizia "quatro cores, sem UV" e foi corrigida na §1.6.
- **O que continua sendo desta task** é o outro lado do critério: dizer o que o
  renderizador tem de implementar, com a paleta **lida do disco** e não
  deduzida, e o controle da §5.5 — trocar uma paleta por outra e exigir
  vermelho — que a
  [`LOOKS-TASK-06`](/docs/tasks/looks/06-harness-controles-e-selftest.md)
  encaminhou para cá por não ter o que derrubar ainda. O veredito adianta a
  direção; não substitui a medição da paleta.

---

- **As quatro peles estão localizadas no disco desde 2026-09-15**, pela
  [`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md): são os
  quatro registros de **256 entradas** em VRAM (0, 480), (0, 481), (0, 482) e
  (0, 483), nos offsets **65.892 / 66.404 / 66.916 / 67.428** do `DAT2D.BIN`. O
  `+0x40` que a LOOKS-TASK-08 mediu no CLUT id é **exatamente uma linha de
  VRAM**, o que amarra a medição de RAM ao arquivo.
- **Lê-las é uma chamada:** `texture.palette_for(data, primitive)` devolve as
  entradas que aquela primitiva amostra, na largura que a página dela declara.
  A parte que continua sendo desta task é dizer **o que o renderizador faz com
  elas** — e que a pele nua amostra 16 entradas de dentro de uma paleta de 256,
  o que um renderizador ingênuo lê como paleta inteira.

---

- **Uma testemunha de fora concorda com as quatro peles, e dá a grade de
  dentro delas.** Medido em 2026-09-15 pela
  [`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md), lendo o
  tutorial do `zeta` em vez de resumi-lo: a tabela dele tem quatro colunas
  chamadas *blanca, amarilla, canela, negra*, nos offsets **65.892 / 66.404 /
  66.916 / 67.428** — as quatro "Pieles" que a LOOKS-TASK-10 mediu —, e os
  **oito tipos de cabelo** andam **32 bytes** dentro de cada uma.
- **32 bytes são 16 halfwords de VRAM, que é um passo de `x` no CLUT id.** Então
  a paleta de 256 entradas de uma pele é uma **grade de dezesseis sub-paletas de
  16**, e `H.COL` anda `x` dentro dela enquanto `SKIN` anda `y` de uma linha para
  a outra. A cabeça amostra `(16, 480)` e `(144, 480)`, que são a sub-paleta 1 e
  a 9 dessa grade. O que esta task fecha é o que o renderizador faz com isso; o
  endereçamento já está medido dos dois lados.

---

## Objetivo

Saber como a cor chega ao boneco, e portanto o que o renderizador tem de fazer.

---

## Critério de conclusão

- [x] Medido, a partir de `load_state` e com leitura de RAM **e** de VRAM: o
      que muda é **o CLUT id da primitiva, byte 2, e mais nada**. Nenhum byte de
      vértice se move, em nenhum dos seis pares campo × slot; e a paleta em VRAM
      não é reescrita — um passo de `H.COL` move zero das 256 entradas.
- [x] **Um passo de cada vez, recarregando o state entre eles.** Todo
      `field_diff` recarrega o state antes, e o `--palettes` recarrega antes de
      andar cada campo.
- [x] Mesma medição para `H.COL` e `H.F.COL.`, que são candidatos a paleta pela
      matriz do Superpack. **A matriz escrita aqui estava errada por uma
      janela**: era `65892 + raça*512 + tipo*32`, e o PDF do `zeta`, lido em vez
      de resumido, começa em **65.924** — `65924 + raça*512 + tipo*32`. Os 32
      bytes de diferença são a coluna 0 de cada registro, que é a janela de pele
      **nua** e não serve a cabelo nenhum. Corrigido 2026-09-15, e o controle
      `skin-matrix-at-the-record` planta exatamente esta versão errada.
- [x] **A matriz do Superpack é conferida** — quatro raças × oito tipos —, e
      confirmada contra o disco: as 32 células caem dentro do registro da sua
      própria raça, alinhadas em janela de 16 entradas, nas colunas 1..8
      (`python tools/looks/skin.py --check-image`).
- [x] O resultado diz, em uma frase, o que o `viewer.py` da Fase 5 precisa
      implementar: **textura com CLUT e só isso** — o índice sai do texel, e a
      cor sai da **janela de dezesseis entradas** que o CLUT id da primitiva
      nomeia dentro do registro de 256, nunca do registro inteiro.

---

## Log de Execução

**Executado em:** 2026-09-15

### Resumo

A incógnita (d) está fechada, e a resposta é maior do que "é paleta": **um
registro de 256 entradas não é uma paleta, é uma fileira de dezesseis CLUTs de
4 bits**, e os três campos de cor da tela são **duas coordenadas** dessa grade.
`SKIN` anda a linha, `H.COL` e `H.F.COL.` andam a coluna, e a grade fecha
exata: uma janela de pele nua, oito de cabelo, sete de barba.

Medido dos dois lados, com o state recarregado antes de cada passo.

### O lado da RAM: byte 2, e nada mais

`python tools/looks/oracle.py --fields SKIN H.COL H.F.COL.`, nos dois slots:

```text
  SKIN, slot 1 (goalkeeper): 196 byte(s)
      /BIN/EDT_MOD.BIN section 11: 4 byte(s), at byte [2] of the primitive
      ... sections 16, 17, 18, 19 ...
      /BIN/MODEL.BIN section 24: 8 byte(s), at byte [2] of the primitive
          +15162 primitive 0: 1 -> 65      +15354 primitive 8: 9 -> 73
      /BIN/EDT_MOD.BIN: list 1 owns section(s) [11, 16, 17, 18, 19]
  SKIN, slot 2 (outfield player): 326 byte(s)
      /BIN/EDT_MOD.BIN: list 0 owns section(s) [0, 3, 4, 5, 6, 7, 8]
  H.COL, slot 1 e slot 2: 7 byte(s) em MODEL.BIN seção 24, byte [2]
          +15162 primitive  0: 1 -> 2      +15498 primitive 14: 1 -> 2
          +15186 primitive  1: 1 -> 2      +15546 primitive 16: 1 -> 2
          +15258 primitive  4: 1 -> 2      +15570 primitive 17: 1 -> 2
          +15378 primitive  9: 1 -> 2
  H.F.COL., slot 1 e slot 2: 2 byte(s), byte [2]
          +15354 primitive  8: 9 -> 10     +15474 primitive 13: 9 -> 10
```

**Nenhum byte de vértice se moveu em nenhum dos seis pares campo × slot.** Todo
acerto cai no byte 2 da primitiva, que é o byte baixo do CLUT id. `SKIN` soma
`0x40` — uma linha de VRAM inteira — e os outros dois somam `1`, que é uma
janela de dezesseis entradas.

E `H.COL` move **sete** primitivas da cabeça, não as duas do cabelo: as duas do
`HAIR` mais cinco. `H.F.COL.` move exatamente as duas do `FACE` — o que diz, de
passagem, que **`FACE` é a barba**, e não o rosto.

### O lado da GPU: a paleta é a do arquivo, e não se mexe

`python tools/looks/oracle.py --palettes` (comando novo):

```text
  every CLUT row of /BIN/DAT2D.BIN against VRAM, resolved the way a renderer resolves it
      row 480: 0 of 256 entr(y/ies) differ, 0 that no record covers
      ... 21 linhas, todas 0 ...
      row 511: 0 of 256 entr(y/ies) differ, 0 that no record covers
  one step of H.COL moved 0 of the 256 entries of the palette in VRAM
  the windows each field reaches, read out of RAM per press
      SKIN      4 value(s): row 480 col 1, row 481 col 1, row 482 col 1, row 483 col 1
      H.COL     8 value(s): row 480 col 1 .. row 480 col 8
      H.F.COL.  7 value(s): row 480 col 9 .. row 480 col 15
oracle --palettes: ok
```

Três coisas de uma vez: **o arquivo é o que o console desenha** (as 267 paletas
batem entrada por entrada), **a paleta não é reescrita** (um passo move zero
entradas), e **o alcance de cada campo foi andado até as duas pontas**, não
deduzido.

### Duas coisas que a primeira corrida mostrou

- **A linha 484 parecia quebrada e não estava.** Comparada contra o registro
  largo em (0, 484), a VRAM diferia em **71** das 256 entradas. O motivo é que
  seis registros de 16 entradas ficam **por cima** dele no mesmo endereço de
  VRAM — e o que a GPU guarda são os estreitos. Resolvendo cada `x` pelo
  `texture.covering`, que já prefere o mais estreito, dá **zero**. O desempate
  que a LOOKS-TASK-10 escolheu por elegância é o que o console faz, e agora está
  medido.
- **Os campos travam nas pontas.** A primeira versão do `walk_field` andava para
  a direita esperando o ciclo voltar ao início, e o quarto `Right` no `SKIN`
  deixou o id em `0x78c1` — lido como pressão ignorada, e a corrida morreu num
  `NotArrived`. Não há volta: o campo trava. O comando passou a andar até a
  ponta de baixo e depois até a de cima, que é o que mede um alcance sem supor
  quantos valores ele tem.

### O que a testemunha de fora diz, lida em vez de resumida

O PDF do `zeta` foi aberto de novo, e a tabela dele começa em **65.924**, não em
65.892: `Tipo A` da `Raza Blanca` é uma janela **adiante** do registro. A matriz
que o critério desta task trazia — `65892 + raça*512 + tipo*32` — estava errada
por 32 bytes, e os 32 bytes são a coluna 0, que é a janela de pele nua e não
serve a cabelo nenhum. Com a base certa, as 32 células caem todas dentro do
registro da sua própria raça, nas colunas 1..8 — exatamente as oito que o
`H.COL` alcança na tela.

O tutorial diz *"estos son los 5 colores para cambiar el cabello"*, e são
**seis**: entradas 2, 5, 12, 13, 14 e 15, iguais nos quatro registros.

E a tabela do CARP, no mesmo lugar, transcreve os oito campos do quarto registro
certos e **erra a própria aritmética**: escreve 67.248 onde os campos dizem
67.428.

### A dúvida que fica, e para quem

`beard_colour` tem **três bits** no `src/core/Player.cpp` — oito valores — e a
tela anda **sete**. A grade explica o sete (as colunas de barba vão da 9 à 15 e
não há décima sexta), mas o que o jogo faz com um `beard_colour` 7 gravado no
registro do jogador não foi medido. Encaminhado para a
[`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md), que é a
dos domínios, com a linha escrita lá.

### Gates medidos

```text
python tools/looks/selftest.py --quiet
  modules:  0 failure(s)
  rules:    0 failure(s)      ..... rule 1 swept 12 file(s), 7295 line(s)
  controls: 0 failure(s)      ..... 23 of 23 controls red
  looks_selftest: 0 failure(s)
```

```text
python tools/looks/skin.py --check            ->  skin.py: 0 failure(s)
python tools/looks/skin.py --check-image      ->  skin --check-image: ok
python tools/looks/oracle.py --palettes       ->  oracle --palettes: ok
python tools/looks/oracle.py --check          ->  oracle.py: 0 failure(s)
python tools/looks/texture.py --check         ->  texture.py: 0 failure(s)
python tools/looks/texture.py --check-image   ->  texture --check-image: ok
python tools/looks/atlas.py --check           ->  atlas.py: 0 failure(s)
python tools/looks/atlas.py --check-image     ->  atlas --check-image: ok
python tools/looks/pieces.py --check          ->  pieces.py: 0 failure(s)
python tools/looks/pieces.py --check-image    ->  pieces --check-image: ok
python tools/looks/modelfile.py --check-image ->  ok
python tools/looks/section.py --check         ->  section: self_check ok
python tools/check_tasks.py                   ->  123 task(s), ok
```

Os dois controles novos são os dois jeitos de perder este veredito sem sintoma:
`skin-matrix-at-the-record` começa a matriz de cabelo no registro em vez de uma
janela adiante — e aí o tipo A pega a janela de pele nua e todos os outros
pegam a do vizinho —, e `skin-window-unaligned-ok` faz o `column_of` arredondar
em vez de recusar, e as dezesseis entradas que ele devolve atravessam duas cores
e continuam desenhando.

Toda leitura de disco saiu do **japonês**, por `WE2002_LOOKS_IMAGE` e pela
guarda do `iso_source`; o emulador bootou o `.cue` **inglês**, e dele não se leu
textura nenhuma. O Superpack foi **lido onde está**, e nada dele entrou no git.
`roms/` só foi lida. A janela do emulador foi para −32000 na abertura, como
manda o `CLAUDE.md`.

### Arquivos criados/modificados

- `tools/looks/skin.py` — **novo**. A grade: `grid()`, `clut_id()`, `window()`,
  `column_of()`, `matrix()`, `check_matrix()`, `entries()`, `moving_entries()`,
  `named_windows()`, a tabela `FIELDS` com o que cada campo anda e até onde, o
  `self_check()` com os casos vermelhos, e `--check`, `--check-image`, `--report`
- `tools/looks/oracle.py` — o comando `--palettes`: `clut_address()`,
  `walk_field()`, `vram_region()` e `check_palettes()`
- `tools/looks/atlas.py` — `read_png()`, porque o `read_vram_region` do fork
  responde com um PNG e não com halfwords; mais o round-trip contra o
  `write_png()` no `self_check()`
- `tools/looks/layout.py` — `SKIN_PALETTES`, `HAIR_MATRIX_FIRST`,
  `HAIR_MATRIX_RACE_STEP`, `HAIR_MATRIX_KIND_STEP`, `HAIR_MATRIX_KINDS`,
  `BARE_SKIN_COLUMN`, `HAIR_COLUMN`, `BEARD_COLUMN` e `HAIR_COLOUR_PRIMITIVES`
- `tools/looks/section.py` — `CLUT_IN_PRIMITIVE`, que era um `+ 2` solto e
  passou a ser endereçável de fora
- `tools/looks/controls.py` — `skin-matrix-at-the-record` e
  `skin-window-unaligned-ok`, mais o literal do `section-primitive-is-colours`
  acompanhando a constante nova
- `tools/looks/selftest.py` — `skin` no `MODULES`
- `docs/PLAN-LOOKS-PY.md` — §6(d) fechada com a grade e a tabela dos três
  campos; §1.7 com a grade e a confirmação pela VRAM, mais o erro de aritmética
  do CARP; §5.2 trocando "cor de primitiva" pelo CLUT id; §5.5 com os dois
  controles de paleta; §3.2 listando `atlas.py`, `skin.py` e `pieces.py`
- `docs/prompts/perfil-looks.md` — duas armadilhas novas (os campos travam nas
  pontas; estreito ganha do largo na VRAM), os dois gates novos na tabela, e a
  grade nas verificações da Fase 3
- `docs/tasks/looks/13-campos-e-dominios-de-looks.md`,
  `14-tabela-de-montagem.md`, `15-visualizador-opengl.md` — os
  encaminhamentos, escritos nos arquivos de destino
- `docs/tasks/looks/progresso.md` — a linha e o checklist

### Problemas encontrados

Os dois de cima — a linha 484 e o travamento nas pontas —, e mais um de escopo:
o bullet do Contexto que dizia que o terceiro controle negativo da §5.5 estava
em aberto **já estava vencido**: a LOOKS-TASK-10 plantou o
`texture-clut-any-record` no mesmo dia. Corrigido no próprio bullet, e esta task
acrescentou o segundo jeito de errar a paleta em vez de repetir o primeiro.
