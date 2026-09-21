---
id: LOOKS-TASK-18
title: "Os 50 renders do Superpack como corpus independente"
type: verificação
category: oráculo
phase: 6
depends_on: [LOOKS-TASK-17]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#5.4"
reviewed_on: 2026-09-16
review_commit: null
done_on: 2026-09-16
done_commit: 0efd5e2
---

# LOOKS-TASK-18: O corpus dos cinquenta

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §5.4.
- `MCR\We DB - polipoli\Faces\` tem **50 JPGs**, dos quais **49 nomeados
  pela tupla exata**: `A-I3-A-F-A` é pele A, cabelo I3, cor A, barba F, cor de
  barba A. O quinquagésimo é o `0.jpg` do terceiro bullet.
- **O caminho é relativo a `Superpackv6\We2002\`, não à raiz da coletânea** —
  `Superpackv6\MCR` não existe. Medido na
  [`LOOKS-TASK-01`](/docs/tasks/looks/01-base-legal-e-linhagem.md) em
  2026-09-14, junto com a correção dos números da §2 do plano.
- **São 50 arquivos, mas 49 tuplas.** O quinquagésimo se chama `0.jpg` e não
  tem tupla no nome — conferido na mesma data, `50 .jpg`, o primeiro em ordem
  sendo `0.jpg` e o segundo `A-A1-A-A-A.jpg`. Quem executar esta task decide o
  que ele é (referência do default? descarte?) antes de contar cobertura: um
  parser que exija tupla no nome **quebra** nele, e um que o ignore em silêncio
  reporta 50 onde mediu 49.
- **O valor deles é serem de outra pessoa.** O confronto da LOOKS-TASK-17 usa o
  mesmo caminho de código dos dois lados em parte do percurso; um corpus
  externo pega erro sistemático que ele não pegaria.
- **Não entram no git** (§2). Ficam apontados por variável de ambiente, como as
  outras fixtures do repositório.

---

- **As 49 tuplas já foram parseadas, e a cobertura medida — por comando.**
  `python tools/looks/looks.py --corpus <pasta>`, ou com a pasta em
  `WE2002_LOOKS_CORPUS`. **Não copie os números daqui: rode.** Esta
  transcrição é de 2026-09-15
  ([`CORR-LOOKS-027`](/docs/tasks/looks/CORR-LOOKS-027.md)), e a cobertura
  muda com a pasta que a variável apontar.

  ```text
  refused: 0.jpg -- '0' has 1 part(s) and a tuple has 5: skin_colour, ...
  50 .jpg   parsed: 49   refused: 1   round-trip to its own name: 49
     skin_colour    4 of  4 value(s) covered
     hair_style     9 of 32 value(s) covered
     hair_colour    4 of  8 value(s) covered
     beard_style    6 of  8 value(s) covered
     beard_colour   2 of  8 value(s) covered
  ```

  As 49 formatam de volta para o próprio nome, e o `0.jpg` **recusa com a
  mensagem certa** em vez de virar índice zero — que é o caso que o terceiro
  bullet deste Contexto pedia para não passar em silêncio. A cobertura está
  medida e é baixa onde importa: **9 dos 32 cabelos**, e duas das oito cores de
  barba. Conclusão de cobertura sobre o corpus inteiro é conclusão sobre esse
  pedaço.

---

- **Quantas das 50 o visualizador consegue desenhar já está medido, e é menos
  que a cobertura de parse.** 2026-09-16
  ([`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md)),
  `python tools/looks/scene.py --corpus <pasta>`: **31 desenhadas, 19
  recusadas** — 13 por `FACE=F`, 3 por `FACE=G`, 2 pelo estilo `H1`, que o
  `HAIR_MAP` não alcançou, e o `0.jpg`. **Rode, não copie**: o número é da
  pasta que a variável apontar. **Remedido em 2026-09-16, depois da
  [`CORR-LOOKS-048`](/docs/tasks/looks/CORR-LOOKS-048.md): 47 desenhadas, 3
  recusadas** — as duas de `H1` e o `0.jpg`. As 16 de `F` e `G` desenham.
- **A métrica da LOOKS-TASK-17 existe e tem nome:** interseção de histogramas
  de cor de 15 bits (`confront.histogram`, `confront.intersection`,
  `confront.verdict`), com o teto de liderança impresso ao lado. **Os JPGs não
  são o PSX**: compressão com perda não guarda cor de 15 bits exata, então
  quantizar como a 17 quantiza e esperar as mesmas cores é o erro a evitar — o
  que a 17 mediu é que o **quadro do emulador** traz as cores exatas, não que
  um render de terceiro traz.
- **A tela da barba alcança SETE valores nos dois slots**, medido em 2026-09-16
  pela [`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md)
  (`confront.py --reach FACE`). A primeira das duas hipóteses abaixo caiu: não
  é editor gravando o campo direto. A tabela recusa `F` e `G` por outra razão,
  e é defeito: [`CORR-LOOKS-044`](/docs/tasks/looks/CORR-LOOKS-044.md).
- **As 16 recusas de barba são medição que falta, não limite.** Hipótese
  resolvida: a varredura da LOOKS-TASK-14 parou cedo — mediu a faixa dos dois
  quads da seção 24, que vai até 4, e escreveu isso como alcance da tela. Desde
  a CORR-LOOKS-044 a recusa diz o que é: `FACE=F is value 5: the screen offers
  it -- it reaches 7 -- and what it writes was not measured`. O que destrava as
  16 é `oracle.py --patched FACE` nos dois slots — pode ser outra seção, como o
  `HAIR` era. Aqui continua entrando como conta: comparar 31 e chamar de "o
  corpus" é dizer 50 onde se mediu 31. **Destravado em 2026-09-16** pela
  [`CORR-LOOKS-048`](/docs/tasks/looks/CORR-LOOKS-048.md): era outra seção —
  `F` e `G` desenham o gêmeo da cabeça —, e a conta agora é 47 de 50.

---

## Objetivo

Usar o corpus para procurar erro sistemático, não para produzir um número
bonito.

---

## Critério de conclusão

- [x] Tuplas e cobertura, pelo `looks.py --corpus`: 49 parseiam, 1 recusa;
      9 de 32 cabelos, 4 de 4 peles, 6 de 8 barbas (a tela oferece 7), 4 de 8
      cores de cabelo, 2 de 8 cores de barba. **O `0.jpg` é um quadro branco**
      — uma cor só, nenhuma figura —, e fica fora da conta; o `corpus.py` diz
      isso a cada corrida, e distingue "branco" de "nome que não é tupla".
- [x] Comparado contra os 49 com tupla, pela métrica da LOOKS-TASK-17
      (`confront.intersection` e `confront.verdict`), com o passo que o JPEG
      exige escrito e sem limiar à mão. 47 desenham, 2 recusam (`H1`).
- [x] Piores casos **olhados**: a tira `work/looks-corpus/worst.png`, que a
      ferramenta grava, com os seis piores lado a lado com o nosso render.
- [x] A divergência que não se explica por pose ou câmera virou
      [`CORR-LOOKS-049`](/docs/tasks/looks/CORR-LOOKS-049.md), com as seis
      tuplas nomeadas.
- [x] Sem `WE2002_LOOKS_CORPUS` nem pasta por argumento, `corpus.py --score`
      sai **77** com a mensagem que nomeia a variável.

---

## Log de Execução

**Executado em:** 2026-09-16 — **CONCLUÍDA**.

### O que se aprendeu

**Uma métrica sobre dado de terceiro, sem um controle de verdade conhecida ao
lado, não diz de quem é a falha.** Na matriz de 47 renders, 35 JPEGs não ficam
em primeiro, e isso parecia render errado. Os quadros **do emulador** da
LOOKS-TASK-17 — cores exatas, tupla conhecida — contra a mesma matriz põem a
própria verdade em 3º e 4º. Histograma de cor resolve **cor** e não **forma**:
câmera e pose mexem na proporção entre as cores mais do que um estilo de cabelo
mexe. O veredito passou a ser por campo, e **foi escrito depois da primeira
corrida lida** — dito no código e aqui, porque a razão é o controle, não o
número.

**O JPEG pede um passo a mais, e o passo não precisa de limiar.** Compressão
com perda tira pixel da cor exata da paleta — e mais num rosto de pixel art do
que num fundo liso, então um limiar medido no fundo erraria por baixo. Cada
pixel vai para a cor mais próxima de onde poderia ter vindo — a paleta que
desenhamos, **ou** o fundo e a camisa lidos do próprio JPEG, que não contam. O
sumidouro evita escolher o número.

**O corpus achou o que existe para achar: um erro sistemático.** Agrupando a
nota de cada JPEG contra o próprio render, só um grupo despenca — **outra
cabeça com outra pele, 0,411** — e olhando as seis piores a pele nova pinta a
testa e deixa o rosto na pele `A`. São os índices de cor medidos na seção 24 e
emprestados às outras cabeças desde a CORR-LOOKS-034, que ela mesma chamou de
suposição. O confronto da LOOKS-TASK-17 não pegava: as cinco tuplas dele não
tinham pele diferente de `A` em cabeça diferente de `A1`.

### As corridas

Na árvore de `0efd5e2`, com os renders refeitos nela; a saída é idêntica, linha
a linha, à do `--score` sobre os renders da corrida anterior.

```text
$ python tools/looks/looks.py --corpus <pasta>
   refused: 0.jpg -- '0' has 1 part(s) and a tuple has 5: ...
50 .jpg   parsed: 49   refused: 1   round-trip to its own name: 49
   skin_colour    4 of  4 value(s) covered
   hair_style     9 of 32 value(s) covered
   hair_colour    4 of  8 value(s) covered
   beard_style    6 of  8 value(s) covered
   beard_colour   2 of  8 value(s) covered
looks --corpus: ok

$ python tools/looks/corpus.py --run <pasta>
      50 file(s): 49 tuple(s), 1 blank, 0 other
      0.jpg -- a blank picture: one colour and no figure; not a tuple (...), left out of the score
      our side: 47 drawn, 2 refused, 81 colour(s) drawn in all
      refused A-H1-A-A-A -- ... hair style H1 wrote nothing to either model file ...
      refused D-H1-A-A-A -- ... hair style H1 wrote nothing to either model file ...
      the 47-way matrix, confront.verdict: 9 win, 3 ranked, 35 not first -- shape is beyond the metric, see the control
      control A-A1-A-A-A   the emulator's own frame ranks its tuple 4 of 47
      control A-A1-C-A-A   the emulator's own frame ranks its tuple 3 of 47
      control A-I3-A-A-A   the emulator's own frame ranks its tuple 3 of 47
      control B-A1-A-A-A   the emulator's own frame ranks its tuple 1 of 47
      the control, 4 picture(s), the best render agrees on: skin_colour 4/4, hair_colour 4/4,
          beard_colour 0/0, hair_style 2/4 (reported), beard_style 3/4 (reported)
      the corpus, 47 picture(s), the best render agrees on: skin_colour 47/47, hair_colour 47/47,
          beard_colour 26/26, hair_style 26/47 (reported), beard_style 23/47 (reported)
      self-score, grouped by head and skin:
        hair style A1     skin A       9 picture(s), mean 0.721, lowest 0.660
        hair style A1     skin not A  14 picture(s), mean 0.641, lowest 0.540
        hair style not A1 skin A      12 picture(s), mean 0.697, lowest 0.544
        hair style not A1 skin not A  12 picture(s), mean 0.411, lowest 0.266
      the 6 lowest self-scores -- drawn beside ours in <raiz>\work\looks-corpus\worst.png:
        D-I3-A-A-A   own 0.266  best D-A1-A-A-A   0.553  shape: hair_style disagree, beard_style agree
        C-I3-A-C-A   own 0.312  best C-A1-A-A-A   0.671  shape: hair_style disagree, beard_style disagree
        B-I3-A-A-A   own 0.316  best B-A1-A-A-A   0.730  shape: hair_style disagree, beard_style agree
        C-I3-A-A-A   own 0.317  best C-A1-A-A-A   0.719  shape: hair_style disagree, beard_style agree
        C-K1-A-E-A   own 0.344  best C-A1-A-A-A   0.609  shape: hair_style disagree, beard_style disagree
        C-O1-A-A-A   own 0.353  best C-A1-A-C-A   0.707  shape: hair_style disagree, beard_style disagree
corpus: ok

$ python tools/looks/corpus.py --score           # sem a variável
corpus: skipped -- no corpus folder: pass one, or point WE2002_LOOKS_CORPUS at ...
exit 77
```

*(A transcrição acima é da árvore desta task. Desde a
[`CORR-LOOKS-050`](/docs/tasks/looks/CORR-LOOKS-050.md) a linha de campo diz
"the best-scoring render carries the name's letter for", e a tabela de grupos é
julgada: o grupo "not A1 / not A" sai `EXPECTED`, pelo resíduo da
[`CORR-LOOKS-049`](/docs/tasks/looks/CORR-LOOKS-049.md), e sem o resíduo o
`corpus:` fica vermelho.)*

**Olhadas, as seis:** no JPEG o rosto inteiro está na pele do nome; no nosso,
só a faixa de cima. Em `C-I3-A-C-A` e `C-K1-A-E-A` o JPEG tem barba e o nosso
não. `scene.py --tuple B-I3-A-A-A` imprime `colour borrowed 9`, e
`B-A1-A-A-A`, 0.

### Gates medidos

```text
$ python tools/looks/selftest.py --quiet        # na arvore de 0efd5e2
  ..... rule 1 swept 20 file(s), 15168 line(s)
  ..... 57 of 57 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/<modelfile|texture|atlas|skin|looks|assembly|pieces|scene>.py --check-image
  8 de 8: ok
$ python tools/looks/oracle.py --check      oracle.py: 0 failure(s)
$ python tools/looks/confront.py --check    confront.py: 0 failure(s)
$ python tools/looks/corpus.py --check      corpus.py: 0 failure(s)
$ python tools/check_tasks.py               check_tasks: 123 task(s), ok
```

Controles de 54 para 57: `corpus-ties-to-palette`,
`corpus-beard-colour-always-seen` e `corpus-shape-judged`.

### Problemas encontrados, e para onde foram

- **Os índices de cor emprestados da seção 24 erram nas outras cabeças** —
  [`CORR-LOOKS-049`](/docs/tasks/looks/CORR-LOOKS-049.md), Alta. **Consertado
  em 2026-09-16:** índices medidos por cabeça; o grupo "not A1 / not A" sobe
  de 0,411 para 0,659.
- **Nenhum confronto do ciclo testemunha forma** — estilo de cabelo e barba —,
  e isso vai para a §6 como aberto, escrito na
  [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md).
- **As duas recusas de `H1`** continuam o que eram; o mapa não alcança o
  estilo, e nada nesta task mede isso.

### Arquivos criados/modificados

Commit `0efd5e2`:

- `tools/looks/corpus.py` — novo
- `tools/looks/controls.py` — três controles
- `tools/looks/selftest.py` — `corpus` na lista de módulos
- `docs/PLAN-LOOKS-PY.md` — §3.2 e §5.4 com a tabela por campo e o achado
- `docs/prompts/perfil-looks.md` — armadilha 30 e duas linhas de gate
- `docs/tasks/looks/20-reconciliacao-e-entregaveis.md` — a quarta incógnita
  aberta, escrita na task de destino
- `docs/tasks/looks/CORR-LOOKS-049.md` e
  `docs/tasks/looks/correcoes-progresso.md` — a correção aberta

Commit seguinte: este Log, o frontmatter, `docs/tasks/looks/progresso.md` e
`tools/looks/corpus.py` — três linhas da docstring reescritas sem mudar de
tamanho, porque traziam uma proporção tirada de sonda descartável ("cerca de
metade") e a regra do ciclo é número de ferramenta. O gate remedido depois
delas dá o mesmo: 20 arquivos, 15.168 linhas, 57 de 57.
