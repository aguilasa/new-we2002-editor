---
id: CORR-LOOKS-049
title: "Correção: nas cabeças que não são A1, a pele pinta só a testa e a barba não aparece — os índices emprestados da seção 24 erram"
type: correção
category: render
status: done
depends_on: []
origin: LOOKS-TASK-18
severity: high
done_on: 2026-09-16
done_commit: a82f922
---

# CORR-LOOKS-049: `COLOUR BY BORROWED INDEX` está medido errado, pelo corpus

## Problema identificado

As quatro linhas de cor (`SKIN`, `H.COL`, `H.F.COL.`, `FACE`) têm os índices de
primitiva medidos na **seção 24**, a cabeça do estilo `A1`. Desde a
[`CORR-LOOKS-034`](/docs/tasks/looks/CORR-LOOKS-034.md) eles são aplicados às
outras doze cabeças **por empréstimo**, e cada parte assim tocada sai marcada
`COLOUR BY BORROWED INDEX` — a própria correção disse que isso era suposição.

O corpus de terceiro mediu a suposição, e ela está errada. Nas cabeças que não
são `A1`, com pele diferente de `A`:

- a pele nova pinta **a testa** e o rosto fica na pele `A`;
- a barba do nome não aparece no nosso render (`C-I3-A-C-A`, `C-K1-A-E-A`).

Nomeadas, as seis piores do corpus: `D-I3-A-A-A`, `C-I3-A-C-A`, `B-I3-A-A-A`,
`C-I3-A-A-A`, `C-K1-A-E-A` e `C-O1-A-A-A`.

## Evidência

```text
$ python tools/looks/corpus.py --score <pasta>
      self-score, grouped by head and skin:
        hair style A1     skin A       9 picture(s), mean 0.721, lowest 0.660
        hair style A1     skin not A  14 picture(s), mean 0.641, lowest 0.540
        hair style not A1 skin A      12 picture(s), mean 0.697, lowest 0.544
        hair style not A1 skin not A  12 picture(s), mean 0.411, lowest 0.266
      the 6 lowest self-scores -- drawn beside ours in <raiz>\work\looks-corpus\worst.png:
        D-I3-A-A-A   own 0.266  best D-A1-A-A-A   0.553 ...
        C-I3-A-C-A   own 0.312  best C-A1-A-A-A   0.671 ...
        B-I3-A-A-A   own 0.316  best B-A1-A-A-A   0.730 ...
        C-I3-A-A-A   own 0.317  best C-A1-A-A-A   0.719 ...
        C-K1-A-E-A   own 0.344  best C-A1-A-A-A   0.609 ...
        C-O1-A-A-A   own 0.353  best C-A1-A-C-A   0.707 ...

$ python tools/looks/scene.py --tuple B-I3-A-A-A      colour borrowed    9
$ python tools/looks/scene.py --tuple B-A1-A-A-A      colour borrowed    0
```

Um efeito de **interação**: cabeça não-`A1` sozinha (0,697) e pele não-`A`
sozinha (0,641) custam pouco; as duas juntas derrubam a média para **0,411**.
É o desenho de um erro de índice — pele certa em primitiva errada —, não de
pose nem de câmera, que custariam o mesmo nos quatro grupos. A tira
`worst.png` foi olhada: o JPEG tem o rosto inteiro na pele do nome, o nosso tem
só a faixa de cima.

## Causa raiz

Os índices `layout.SKIN_COLOUR_PRIMITIVES`, `HAIR_COLOUR_PRIMITIVES` e
`FACE_PRIMITIVES` são posições **dentro da seção 24**. As outras cabeças não
têm o mesmo número de primitivas (a 34 desenha 23, a 24 desenha 18), e a mesma
posição cai em outra parte da malha.

## Correção

### Arquivo: `tools/looks/layout.py` e `tools/looks/assembly.py`

Medir, por cabeça, quais primitivas cada linha de cor move — a irmã do
`oracle.py --writes HAIR`, que nomeou os quads de cabelo das quatro cabeças do
`HAIR_QUADS`: um breakpoint de escrita no CLUT id enquanto a linha é andada, em
cada uma das treze. Enquanto uma cabeça não tiver os índices dela, as linhas de
cor nela **recusam** em vez de pintar por empréstimo — a mesma escolha do
`head_of` para os três estilos não medidos.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | os índices de cor por cabeça, com a medição ao lado |
| `tools/looks/assembly.py` | usar os da cabeça; recusar onde faltarem |
| `tools/looks/controls.py` | controle que volte ao empréstimo |

## Verificação

- [x] `corpus.py --score` **verde sem o resíduo** `(False, False)` em
      `corpus.GROUP_RESIDUES` — o gate da
      [`CORR-LOOKS-050`](/docs/tasks/looks/CORR-LOOKS-050.md): com o conserto o
      grupo deixa de ser outlier, e o resíduo tem de sair (ele mesmo fica
      vermelho se sobrar); se as tuplas do grupo saírem como recusa, o grupo
      some do corpus e o resíduo sai pelo mesmo motivo
- [x] `scene.py --tuple B-I3-A-A-A` sem `colour borrowed`
- [x] controle negativo vermelho

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

A evidência reproduz em `faa9e1d`: grupo "not A1 / not A" com média 0,411,
`scene.py --tuple B-I3-A-A-A` com `colour borrowed 9` e `B-A1-A-A-A` com 0.

**A medição, e as duas voltas até ela ficar certa.**

1. `oracle.py --patched SKIN 2 <26 tuplas>` (a da CORR-LOOKS-048, uma tupla em
   cada cabeça e uma no gêmeo de cada) **morreu na 4ª partida**, `A-B2-A-F-A`:
   de `E` para `F` a célula de valor mexe 0,0029, abaixo dos 0,004 do
   `VALUE_MOVED` — `F` é `E` sem a barra de baixo. É a armadilha 28. O
   `confront.route` passou a provar cada tecla de valor pela **máscara de
   glifo** (`confront.press_value`).
2. Relançada, a corrida de `SKIN` terminou (26 min), e a união passo a passo
   **não fechava**: na seção 24 a primitiva 7 mudava no passo 1 e nunca mais,
   e a tecla além da ponta ainda escrevia. Leituras 20 quadros separadas pegam
   a cabeça no meio da reescrita (armadilha 18). As corridas de `H.COL` e
   `H.F.COL.` foram interrompidas e o emulador derrubado.
3. **`oracle.py --colour`**, novo: anda a linha até a ponta de baixo e até a de
   cima, e em cada ponta lê o `MODEL.BIN` até duas leituras **300 quadros**
   separadas concordarem; a primitiva é da linha onde o CLUT id (ou, no `FACE`,
   o texcoord entre `A` e `E`) difere entre as pontas. Piloto em 24 e 34, depois
   as quatro linhas: `SKIN`, `H.COL` e `H.F.COL.` nas 26 partidas do slot 2,
   `FACE` nas 13 cabeças pares, e `SKIN` e `H.COL` em seis partidas do slot 1.

```text
$ python tools/looks/oracle.py --colour SKIN 2 A-A1-A-A-A A-I1-A-A-A      # piloto, 2 min 6 s
  SKIN on slot 2 from A-A1-A-A-A: CLUT ids that differ between the two settled ends
      section 24: (0, 1, 2, 4, 5, 7, 8, 9, 12, 13, 14, 15, 16, 17)
  SKIN on slot 2 from A-I1-A-A-A: CLUT ids that differ between the two settled ends
      section 34: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22)

$ python tools/looks/oracle.py --colour H.COL 2 <26 tuplas>     (trecho)
  H.COL on slot 2 from A-A1-A-A-A      section 24: (0, 1, 2, 4, 5, 7, 9, 12, 14, 15, 16, 17)
  H.COL on slot 2 from A-A1-A-F-A      section 25: (0, 1, 2, 4, 5, 7, 9, 14, 15, 17)
  H.COL on slot 2 from A-I1-A-A-A      section 34: (0, 1, 2, 5, 8, 9, 12, 13, 15, 16, 17, 19, 20, 21, 22)

$ python tools/looks/oracle.py --colour H.F.COL. 2 <26 tuplas>  (trecho)
  H.F.COL. on slot 2 from A-A1-A-A-A   section 24: (8, 13)
  H.F.COL. on slot 2 from A-A1-A-F-A   section 25: (8, 12, 13, 16)
  H.F.COL. on slot 2 from A-I1-A-A-A   section 34: (7, 10, 11)

$ python tools/looks/oracle.py --colour FACE 2 <13 tuplas>      (trecho)
  FACE on slot 2 from A-A1-A-A-A       section 24: (8, 13)
  FACE on slot 2 from A-B2-A-A-A       section 26: (4, 7)
  FACE on slot 2 from A-L1-A-A-A       section 46: (6, 7, 8)

slot 1 (SKIN e H.COL, A-A1-A-A-A, A-I1-A-A-A, A-L1-A-F-A): as seis listas
iguais às do slot 2 -- conferidas por script contra a tabela antes de escrevê-la
```

A tabela inteira — 26 cabeças em três linhas, 13 no `FACE` — está no
`layout.COLOUR_PRIMITIVES`, gerada das quatro transcrições.

**A medição corrige também a seção 24.** `SKIN_COLOUR_PRIMITIVES` dizia 8 e são
**14**; `HAIR_COLOUR_PRIMITIVES` dizia 7 e são **12**. A união dos três campos,
que a CORR-LOOKS-026 escreveu como nove de dezoito com a primitiva 4 de exceção
ao "linha × coluna", é **quatorze**, as de `H.COL` andam todas com a linha, e
quatro primitivas — 3, 6, 10 e 11 — não andam com campo nenhum. Mesma causa: as
listas antigas foram lidas no meio da reescrita.

### O código

- `layout.py` — `COLOUR_PRIMITIVES` por linha e por seção; os dois índices da
  24 passam a sair da tabela, com o valor antigo e a data no docstring.
- `assembly.py` — `colour_primitives(row, head)` resolve os índices da cabeça
  desenhada e **recusa** cabeça fora da tabela; saíram `HEAD_COLOUR_MEASURED`,
  `colour_is_measured`, o `borrowed` do `draw_list` e a marca
  `COLOUR BY BORROWED INDEX`. Asserções: o `SKIN` na 34 são as dezoito da 34;
  toda cabeça e todo gêmeo têm as três linhas; os quads de barba do gêmeo estão
  entre os que a cor de barba dele move; cabeça não medida recusa.
- `scene.py` — sem o campo `colour_borrowed`; o `--check-image` confere que a
  pele `B` na 34 move exatamente a linha da tabela.
- `skin.py` — os asserts dos "nove" e da primitiva 4 viraram os quatorze e as
  quatro, com a razão.
- `oracle.py` — `--colour`; `confront.py` — `press_value` na rota.
- `corpus.py` — o `GROUP_RESIDUES` ficou vazio: o gate da CORR-LOOKS-050 ficou
  vermelho pedindo a remoção, que é o comportamento combinado.
- `controls.py` — `assembly-colour-stays-on-24` seguiu para a linha nova;
  novo `assembly-colour-borrowed-from-24`.

### Gates

```text
$ python tools/looks/corpus.py --run          # com o resíduo ainda lá
        hair style A1     skin A       9 picture(s), mean 0.721, lowest 0.660
        hair style A1     skin not A  14 picture(s), mean 0.641, lowest 0.540
        hair style not A1 skin A      12 picture(s), mean 0.713, lowest 0.660
        hair style not A1 skin not A  12 picture(s), mean 0.659, lowest 0.466
      GROUP OUTLIER hair style not A1, skin not A: the residue still exempts it, and the group is not an outlier -- remove the residue (CORR-LOOKS-049)
corpus: 2 failure(s)

$ python tools/looks/corpus.py --score        # sem o resíduo
      (os mesmos quatro grupos)
corpus: ok
      (work/looks-corpus/worst.png olhada: rosto inteiro na pele do nome, barba visível)

$ python tools/looks/scene.py --check-image
      skin B on section 34 moves primitive(s) [0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22]
scene --check-image: ok
$ python tools/looks/skin.py --check-image
the head is 18 primitive(s); the three colour fields move 14 of them
    not moved: 3, 6, 10, 11
skin --check-image: ok
$ python tools/looks/assembly.py --check-image       assembly --check-image: ok
$ python tools/looks/assembly.py --corpus            rho = 0.80 (the floor is 0.80) -- assembly --corpus: ok
$ python tools/looks/looks.py --corpus               looks --corpus: ok
$ python tools/looks/scene.py --corpus               47 drawn, 3 refused
$ python tools/looks/confront.py --render && python tools/looks/confront.py --score
  slot 2: 3 win, 2 ranked, 0 expected, 0 unexplained
  slot 1: 3 win, 2 ranked, 0 expected, 0 unexplained
$ python tools/looks/ui_check.py
looks_ui: 3 of 3 negative control(s) red, and the window drew every tuple it was asked for
$ python tools/looks/controls.py --only assembly-colour-borrowed-from-24
  RED    assembly-colour-borrowed-from-24 assembly.py :: colour_primitives
$ python tools/looks/selftest.py --quiet
  ..... 60 of 60 controls red
looks_selftest: 0 failure(s)
```

`roms/` intocada; os dois save states só carregados; o emulador foi encerrado
em todas as corridas, e derrubado à mão (`fork.py kill`) quando as corridas
passo a passo foram interrompidas.

### Problemas encontrados

- **A forma passo a passo do `--patched` não serve para dizer o que um campo
  move**, e isso já tinha produzido os números errados da seção 24. O
  `--patched` continua certo para o que faz — onde um valor escreve —; para
  "quais primitivas", é o `--colour`. Registrado na armadilha 18 do perfil.
- **O grupo `A1` / pele não-`A` continua em 0,641**, e só passa porque o piso
  dos outros grupos inclui o 0,466 do `D-I3-A-A-A`. As piores agora são quase
  todas pele `D` (0,540 a 0,551). Não é índice — a 24 foi medida —, e fica
  como leitura para quem olhar a pele `D` do corpus, não como CORR: a tira não
  mostra rosto na pele errada.

### Arquivos criados/modificados

- `tools/looks/layout.py`, `assembly.py`, `scene.py`, `skin.py`, `oracle.py`,
  `confront.py`, `corpus.py`, `controls.py`
- `docs/PLAN-LOOKS-PY.md` — §5.4 (o conserto e o resíduo que saiu), §6(c)
  (o empréstimo) e a tabela e o parágrafo dos "nove", corrigidos no lugar com a
  data
- `docs/tasks/looks/14-tabela-de-montagem.md` e
  `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` — notas datadas
- `docs/prompts/perfil-looks.md` — a armadilha 18 e a linha do `--colour`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
