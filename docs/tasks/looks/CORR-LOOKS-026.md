---
id: CORR-LOOKS-026
title: "Correção: a grade dá conta do que os três campos alcançam, não do que o registro é — 948 primitivas moram na coluna 1 e não andam com campo nenhum"
type: correção
category: textura
status: done
depends_on: []
origin: LOOKS-TASK-12
severity: medium
done_on: 2026-09-15
done_commit: db56eb8
---

# CORR-LOOKS-026: as dezesseis colunas estão "explicadas" por três campos que não alcançam a maioria de quem as usa

## Problema identificado

O veredito da task está certo e é forte: a cor vem de CLUT, o registro de 256
entradas é uma fileira de dezesseis janelas de 16, `SKIN` anda a linha e
`H.COL`/`H.F.COL.` andam a coluna. Isso reproduz inteiro.

O que não se sustenta é o **fecho** — a afirmação de que a grade está toda
explicada:

```text
the sixteen columns of a skin record, accounted for
    column   0      the bare-skin window
    columns  1..8   H.COL, 8 value(s)
    columns  9..15  H.F.COL., 7 value(s)
    16 of 16 column(s) spoken for
```

A conta é sobre **o que os três campos alcançam**, e está sendo lida como o que
cada coluna **é**. Medido:

1. **948 primitivas amostram a linha 480, coluna 1** — *"hair colour 1"* pela
   tabela acima —, em **50 seções do `MODEL.BIN`**. A cabeça responde por
   **16**; as outras 932 não são cabelo de ninguém, e nenhum dos três campos as
   toca.
2. **Nove primitivas da própria cabeça não andam com campo nenhum.** A união dos
   três diffs é `{0, 1, 4, 8, 9, 13, 14, 16, 17}` — nove de dezoito. As outras
   nove ficam na linha 480, coluna 1, **inclusive depois de trocar a pele**: o
   jogador de pele negra desenha essas nove janelas na paleta da pele *branca*.
3. **A primitiva 4 anda com `H.COL` e não anda com `SKIN`.** É a única exceção
   ao "linha × coluna" em toda a cabeça: as outras seis que o `H.COL` move
   também seguem a linha quando a pele muda; a 4 fica pregada na 480.

Nada disso desmente a resposta da incógnita (d), e por isso a criticidade é
Média: o renderizador que a task manda escrever — *"o índice sai do texel, e a
cor sai da janela que o CLUT id da primitiva nomeia"* — lê o CLUT de cada
primitiva e acerta os três casos sozinho. O risco está na **frase**, e é o risco
que a [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md) corre em
seguida: quem escrever a tabela de montagem a partir de "colunas 1..8 são as
oito cores de cabelo" mapeia 932 primitivas de `MODEL.BIN` para uma cor de
cabelo que elas não têm, e o resultado **desenha perfeitamente**. É a armadilha
das oito listas de nome de time do PES2 outra vez, no eixo da paleta.

E as nove primitivas paradas são, por si, um achado que vale escrever: elas
dizem que **parte da cabeça não é pele** — olho, boca, sobrancelha, o que for —,
e que quem as nomear fecha a §6(b) num ponto que a
[`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md) deixou em
aberto, porque lá a cabeça entrou como uma peça só.

## Evidência

Os três diffs ao vivo, reproduzidos nesta revisão a partir de `load_state`, nos
dois slots (idênticos nos dois):

```text
SKIN      /BIN/MODEL.BIN section 24: 8 byte(s), byte [2]
            primitive  0: 1 -> 65     primitive  9: 1 -> 65
            primitive  1: 1 -> 65     primitive 13: 9 -> 73
            primitive  8: 9 -> 73     primitive 14: 1 -> 65
                                      primitive 16: 1 -> 65
                                      primitive 17: 1 -> 65
H.COL     /BIN/MODEL.BIN section 24: 7 byte(s), byte [2]
            primitive  0, 1, 4, 9, 14, 16, 17:  1 -> 2
H.F.COL.  /BIN/MODEL.BIN section 24: 2 byte(s), byte [2]
            primitive  8: 9 -> 10     primitive 13: 9 -> 10
```

`{0,1,8,9,13,14,16,17} ∪ {0,1,4,9,14,16,17} ∪ {8,13}` = **nove** de dezoito, e a
**4** está no segundo conjunto e não no primeiro.

E quem mais mora na coluna 1, medido do disco com o `section.py` commitado:

```text
primitives sampling row 480 column 1: 948   {'/BIN/MODEL.BIN': 948}
sections: 50
   /BIN/MODEL.BIN section 46: 31      section 41: 27
   /BIN/MODEL.BIN section 40: 29      section 45: 27
   /BIN/MODEL.BIN section 44: 29      section 50: 25
   /BIN/MODEL.BIN section 47: 29      section 28: 24
   /BIN/MODEL.BIN section 24 (a cabeça): 16
```

Nenhuma no `EDT_MOD.BIN`: as peças do corpo vivem na coluna **0**, que é a que a
tabela chama de pele nua — essa parte bate exatamente.

**O resto da task reproduz inteiro**, e vale dizer o que foi conferido para a
criticidade ficar clara: as 21 linhas de VRAM iguais entrada por entrada, o
`one step of H.COL moved 0 of the 256 entries`, os alcances `4 / 8 / 7` andados
até as duas pontas (`0x7801..0x78c1`, `0x7801..0x7808`, `0x7809..0x780f`), as
seis entradas que diferem entre as colunas de cabelo (`[2, 5, 12, 13, 14, 15]`)
nos quatro registros, as 32 células da matriz do `zeta` caindo nas colunas 1..8,
e — do lado da cena — a linha 4 do `PALETAS Dat2d.bin.txt` do CARP escrevendo
mesmo `67248` onde os campos dizem 67.428.

## Causa raiz

O `named_windows()` conta as colunas que os três campos alcançam e fecha em
dezesseis; ninguém perguntou quem mais amostra cada coluna, que é uma varredura
de disco que o módulo já sabe fazer.

## Correção

### Arquivo: `tools/looks/skin.py`

1. O bloco *"the sixteen columns of a skin record, accounted for"* passa a
   imprimir, por coluna, **quantas primitivas a amostram e de que arquivo** — o
   módulo já varre os dois arquivos para a tabela `(row, column)` logo acima, e
   é a mesma conta.
2. A linha de fecho deixa de dizer que dezesseis de dezesseis estão explicadas
   e passa a dizer o que é verdade: **os três campos alcançam as dezesseis
   colunas; a coluna 1 é também a janela de repouso de 948 primitivas em 50
   seções do `MODEL.BIN`**.
3. Asserção nova, barata, no `--check-image`: a união das primitivas que os três
   campos movem na seção da cabeça é **nove de dezoito**, e a 4 anda com `H.COL`
   e não com `SKIN`. Hoje o módulo afirma o conjunto de cada campo; o que falta é
   afirmar o que **não** se move, que é o que esta CORR descobriu por subtração.

### Arquivo: `docs/tasks/looks/09-nomear-as-onze-pecas.md`

A cabeça entrou lá como **uma** peça. As nove primitivas que nenhum campo de cor
move são a pergunta seguinte, e o método é o mesmo: trocar a opção e ver o que
muda. Uma linha, no arquivo de destino.

### Arquivo: `docs/PLAN-LOOKS-PY.md`

A §6(d) e a §1.7 trazem a grade; a ressalva entra ali, junto com as 948 — não
como erro, como o que a grade **não** diz.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/skin.py` | modificar |
| `docs/tasks/looks/09-nomear-as-onze-pecas.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |

## Verificação

- [x] o `--check-image` imprime, por coluna, quem a amostra, e a coluna 1
      aparece com as 948 em 50 seções
- [x] nenhum lugar diz que as dezesseis colunas estão explicadas pelos três
      campos — a §1.7, a §6(d), a LOOKS-TASK-14 e o `skin.py` dizem
      **alcançam**
- [x] existe asserção de que nove das dezoito primitivas da cabeça não são
      movidas por campo de cor nenhum, e de que a 4 é a exceção ao "linha ×
      coluna"
- [x] a LOOKS-TASK-09 registra as nove como o que falta nomear na cabeça
- [x] `python tools/looks/skin.py --check` e `--check-image` verdes
- [x] `python tools/looks/selftest.py` verde, 24 de 24 controles vermelhos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-15

### Resumo do que foi feito

A evidência reproduziu dos dois lados antes de qualquer edição. Do disco, com
o `section.py` commitado:

```text
row 480 col 1 total: 948 {'/BIN/MODEL.BIN': 948}
sections: 50
head: 16
head primitive count: 18
```

E do jogo rodando, `oracle.py --fields SKIN` e `--fields SKIN H.COL H.F.COL.`,
a partir de `load_state` nos dois slots — idênticos nos dois:

```text
SKIN      /BIN/MODEL.BIN section 24: 8 byte(s), at byte [2] of the primitive
          primitive 0, 1, 9, 14, 16, 17: 1 -> 65    primitive 8, 13: 9 -> 73
H.COL     /BIN/MODEL.BIN section 24: 7 byte(s)
          primitive 0, 1, 4, 9, 14, 16, 17: 1 -> 2
H.F.COL.  /BIN/MODEL.BIN section 24: 2 byte(s)
          primitive 8: 9 -> 10     primitive 13: 9 -> 10
```

### O bloco de fecho passou a imprimir as duas contagens lado a lado

A esquerda é o que os campos **alcançam**; a direita é quem **repousa** ali. O
fecho antigo tinha só a esquerda, e por isso fechava:

```text
the sixteen columns of the first skin row: what reaches them, and who rests in them
    column  0   no colour field steps here 296 in 12 section(s) of /BIN/EDT_MOD.BIN, 150 in 28 section(s) of /BIN/MODEL.BIN
    column  1   H.COL = 0          948 in 50 section(s) of /BIN/MODEL.BIN
    column  2   H.COL = 1          no primitive names it
    ...
    column  9   H.F.COL. = 0       126 in 38 section(s) of /BIN/MODEL.BIN
    column 10   H.F.COL. = 1       no primitive names it
    ...
    the three fields reach 16 of 16 column(s)
    column 1 is ALSO where 948 primitive(s) rest, and 16 of them are the head: a name taken from the field alone gives the other 932 a hair colour they do not have
```

**E a tabela inteira diz mais do que a CORR pediu:** as colunas **2..8 e
10..15 não têm primitiva nenhuma no disco**. As oito cores de cabelo existem
como destino de tecla, não como estado gravado — o disco só repousa em 0, 1 e
9. Isso está no plano junto com as 948.

### O que **não** se move virou asserção

A CORR achou as nove por subtração, e subtração não deixa rastro em saída
nenhuma. Agora o `skin.py` guarda o conjunto medido do `SKIN` em
`layout.SKIN_COLOUR_PRIMITIVES`, cruza os três no `self_check()` — nove de
dezoito, e a **4** anda com `H.COL` e não com `SKIN` — e o `--check-image`
imprime as duas listas contra o que o disco diz que a cabeça é:

```text
the head is 18 primitive(s); the three colour fields move 9 of them
    moved:   0, 1, 4, 8, 9, 13, 14, 16, 17
    not moved: 2, 3, 5, 6, 7, 10, 11, 12, 15  -- these keep the pale skin's row through every step of all three fields
```

Controle negativo novo, `skin-union-of-one-field`: a união dos três campos
tomada como a lista do último. Vermelho.

### Problemas encontrados

Nenhum no conserto. A varredura de discrepância puxou um arquivo que a lista
da CORR não previa — a [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md)
repetia *"a grade fecha exata: 1 + 8 + 7 = 16"*, que é exatamente a frase de
que ela é a vítima. Reconciliada em commit próprio.

### Arquivos criados/modificados

- `tools/looks/layout.py` — `SKIN_COLOUR_PRIMITIVES`, o conjunto medido do
  `SKIN`, com o cruzamento como razão de existir
- `tools/looks/skin.py` — `column_owners()`, `moved_by_colour()`,
  `unmoved_head()`, o bloco de fecho com as duas contagens, e as asserções
- `tools/looks/controls.py` — o controle `skin-union-of-one-field`
- `docs/tasks/looks/09-nomear-as-onze-pecas.md` — as nove como o que falta
  nomear na cabeça
- `docs/PLAN-LOOKS-PY.md` — §1.7 e §6(d)
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-026.md` — este arquivo
