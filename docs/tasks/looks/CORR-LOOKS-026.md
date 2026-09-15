---
id: CORR-LOOKS-026
title: "Correção: a grade dá conta do que os três campos alcançam, não do que o registro é — 948 primitivas moram na coluna 1 e não andam com campo nenhum"
type: correção
category: textura
status: pendente
depends_on: []
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

- [ ] o `--check-image` imprime, por coluna, quem a amostra, e a coluna 1
      aparece com as 948
- [ ] nenhum lugar diz que as dezesseis colunas estão explicadas pelos três
      campos
- [ ] existe asserção de que nove das dezoito primitivas da cabeça não são
      movidas por campo de cor nenhum, e de que a 4 é a exceção ao "linha ×
      coluna"
- [ ] a LOOKS-TASK-09 registra as nove como o que falta nomear na cabeça
- [ ] `python tools/looks/skin.py --check` e `--check-image` verdes
- [ ] `python tools/looks/selftest.py` verde, com todos os controles vermelhos
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
