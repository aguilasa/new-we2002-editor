---
id: CORR-LOOKS-024
title: "Correção: a §1.7 do plano ainda diz que o cabelo está no offset 8 e que 1.175 primitivas amostram fora do arquivo — as duas a task 11 desmentiu"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-LOOKS-024: o plano guarda, na seção anterior, as afirmações que a §1.8 acabou de derrubar

## Problema identificado

A regra deste ciclo é que **o plano se corrige na seção que muda**, e não num
apêndice. A §1.8 foi reescrita com o veredito, e ficou boa. Mas ela é a seção
**seguinte**, e a §1.7 — que é o `fonte_de_verdade` da
[`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md) e a seção que
o Contexto da própria task 11 manda ler — continua afirmando duas coisas que
esta execução mediu de outro jeito. São **três** claims, contando uma conta que
não fecha na §1.8:

**1. A tabela de rótulos da §1.7 traduz o CARP como se fosse verdade.** Linha
632-634, sem nenhuma ressalva:

```markdown
| offset | VRAM | rótulo do CARP |
| 8 | (512, 256) | *"Pelos Cuerpos y botines"* — cabelos, corpos e chuteiras |
| 3.568 | (544, 256) | *"Caras"* — rostos |
```

O *"cabelos"* da primeira linha é **o erro que a task 11 derrubou** — e não é
citação do CARP, é a tradução que o plano acrescentou. Quem ler a §1.7 e parar
ali sai com a resposta errada da contradição que a §1.8 resolve 120 linhas
adiante. O rótulo do CARP tem de continuar transcrito (é o objeto do confronto),
mas marcado como o que é.

**2. "1.175 das 2.841 primitivas amostram de páginas que não vêm deste
arquivo"** (linha 622-626) — medido de novo, são **1.039**, e a diferença não é
arredondamento: são as **136** primitivas da página `0x1A`, que amostram sim um
registro deste arquivo. O que mudou foi o método, e foi esta task que o trouxe:
contar por **base de página** não é contar por **texel**. Uma página de 4 bits
cobre 256 texels e as imagens têm 128, então um `u` alto atravessa para o
registro seguinte — que é o argumento inteiro da §1.8.

As 136 são as primitivas das seções **0 e 1 do `MODEL.BIN`**, com `u` 130..186 e
`v` 130..187: VRAM x 672..686, y 386..443, **dentro** do registro em 10.248
(672, 384). É a mesma imagem que a §1.8 lista como a terceira que a geometria
amostra. As duas seções do plano contam o mesmo conjunto de dois jeitos e não se
falam.

**3. A §1.8 diz "seis" onde a ferramenta diz "três", e a conta não fecha:**

> Das 23 imagens, a geometria amostra **três**: 8, 3.568 e 10.248. As outras
> vinte não têm veredito, e o `atlas.py --labels` as imprime pelo que são —
> **seis** com o rótulo do CARP marcado *scene opinion*, **dezessete** sem
> rótulo nenhum.

6 + 17 = 23, e o conjunto descrito tem **20**. A tabela `DAT2D_SCENE_LABELS` tem
mesmo seis linhas, mas três delas caem nos registros já medidos (8, 3.568 e
10.248), então o que sai marcado *scene opinion* são **três**. É o que o comando
imprime.

## Evidência

O que a ferramenta desta task diz, rodada nesta revisão:

```text
$ python tools/looks/atlas.py --check-image
  2841 primitive(s) over both model files, 23 image record(s)
  1802 primitive-record pairing(s) land in this file, 1039 land outside every record in it
  ...
      @ 10248 vram ( 672, 384)   136 primitive(s)  measured      not the player: only MODEL.BIN sections 0 and 1 sample it
  3 of 23 record(s) carry a measured label; 3 carry the scene's opinion and 17 carry none
```

`1039 + 136 = 1175`, que é de onde vem o número da §1.7 — e as 136, remedidas
aqui a partir do disco:

```text
tpage 0x1a primitives per MODEL section: {0: 88, 1: 48} total 136
u range 130..186   v range 130..187
    -> VRAM x = 640 + u/4 = 672..686,  y = 256 + v = 386..443
    -> dentro do registro @10248, vram (672, 384), 32x128
```

E o veredito da §1.8, que a §1.7 não acompanha:

```text
  primitive  1 -- HAIR moves it -- samples the record at 3568
  primitive 14 -- HAIR moves it -- samples the record at 3568
  primitive  8 -- FACE moves it -- samples the record at 3568
  primitive 13 -- FACE moves it -- samples the record at 3568
```

**O resto da task reproduz inteiro**, e por isso a criticidade é Média: as 18
primitivas da cabeça com `u` 16..62 na primeira metade e 152..199 na segunda, as
quatro que `HAIR` e `FACE` movem, os 85,7% e 9,2% do BMP contra o disco — e os
**100,0%** contra o `DAT2D.BIN` do próprio `zeta`, que remedi por fora e
confirma byte a byte —, os 105 `TEX_*.BIN`, e o `--fields FACE` ao vivo com as
**oito** linhas das primitivas 8 e 13, que é o conserto do `hits[:4]`.

## Causa raiz

A §1.8 foi escrita com o veredito e a §1.7 ficou como estava, embora as duas
falem dos mesmos registros — e uma delas conte por base de página, que é o
método que esta task substituiu.

## Correção

### Arquivo: `docs/PLAN-LOOKS-PY.md`

1. **§1.7, tabela de rótulos** — a coluna continua sendo *"rótulo do CARP"*, mas
   a linha do 8 perde a tradução *"cabelos"* e ganha o ponteiro: medido em
   2026-09-15, o cabelo é o 3.568 (§1.8). A do 3.568 idem, pelo outro lado.
2. **§1.7, o parágrafo das páginas ausentes** — o número passa a ser o medido
   por texel (**1.039**), com a frase que explica a diferença: as 136 da página
   `0x1A` atravessam para o registro em 10.248, e contar por base de página as
   dava como ausentes. Vale escrever a regra ao lado, porque é a que a Fase 4
   vai usar: **o que resolve um registro é o texel, não a base da página.**
3. **§1.8** — "seis" vira "três", ou a frase passa a dizer o que quer dizer: a
   tabela do CARP tem seis linhas, três das quais já não são opinião porque
   foram medidas.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-LOOKS-PY.md` | modificar |

## Verificação

- [x] a §1.7 não traduz mais o rótulo do 8 como "cabelos", e aponta para a §1.8
- [x] o número da §1.7 é **1.039**, com a explicação das 136
- [x] a §1.8 diz três, e 3 + 3 + 17 = 23 fecha na frase como fecha no comando
- [x] `python tools/looks/atlas.py --check-image` continua `ok` e é a fonte dos
      três números
- [x] `python tools/looks/selftest.py` verde, 21 de 21 controles vermelhos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-15

### Resumo do que foi feito

As três afirmações foram corrigidas **na seção que muda**, que é a §1.7 — e não
por nota na §1.8, que já estava certa.

**A tabela de rótulos** ganhou uma quarta coluna e perdeu a tradução. A do meio
passou a ser transcrição pura do rótulo de terceiro, que é o objeto do
confronto; o que foi medido tem coluna própria:

| offset | VRAM | rótulo do CARP | o que foi medido |
|---:|---|---|---|
| 8 | (512, 256) | *"Pelos Cuerpos y botines"* | **não é o cabelo** |
| 3.568 | (544, 256) | *"Caras"* | **cabelo e rosto**, os dois |
| 7.456 | (512, 384) | *"Cuerpo"* | sem veredito |

**O número passou a ser 1.039**, com a regra que explica a diferença escrita ao
lado — porque é a regra que a Fase 4 vai usar: **o que resolve um registro é o
texel, não a base da página**. As 136 da página `0x1A` atravessam para o
registro em 10.248, e contar por base de página as dava como ausentes:

```text
tpage 0x1a primitives per MODEL section: {0: 88, 1: 48} total 136
u range 130..186   v range 130..187
    -> VRAM x = 640 + u/4 = 672..686,  y = 256 + v = 386..443
    -> dentro do registro @10248, vram (672, 384)
```

`1.039 + 136 = 1.175`, que é exatamente o número velho.

**E a §1.8 passou a dizer três.** A conta que não fechava — 6 + 17 = 23 sobre um
conjunto de 20 — vira 3 medidas + 3 de opinião + 17 sem rótulo, que é o que o
comando imprime:

```text
  3 of 23 record(s) carry a measured label; 3 carry the scene's opinion and 17 carry none
```

A `DAT2D_SCENE_LABELS` tem mesmo seis linhas; três delas caem nos registros já
medidos, e opinião sobre o que foi medido deixa de ser o que a imagem carrega.

### Problemas encontrados

Nenhum. Os três números saem do `atlas.py --check-image`, que a task entregou e
que continua `ok`; o que faltava era a seção anterior concordar com ele.

### Arquivos criados/modificados

- `docs/PLAN-LOOKS-PY.md` — §1.7 (a tabela de rótulos e o 1.039 com a regra do
  texel) e §1.8 (três, e a conta que fecha)
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-024.md` — este arquivo
