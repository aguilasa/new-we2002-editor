---
id: CORR-LOOKS-018
title: "Correção: a página de textura declara a profundidade da CLUT, e 1.039 das 2.841 primitivas dizem 8 bits — o plano só registra 4"
type: correção
category: engenharia-reversa
status: done
depends_on: []
origin: LOOKS-TASK-08
severity: high
done_on: 2026-09-15
done_commit: "2273318"
---

# CORR-LOOKS-018: a palavra de página traz a profundidade, e ela não é sempre 4 bits

## Problema identificado

A task releu a primitiva e acertou o formato: bytes 6..7 são a **página de
textura** do `POLY_FT4`. O que ela registrou dessa palavra foram as coordenadas
de VRAM — `0x18`, `0x1A` e `0x99` como (512, 256), (640, 256) e (576, 256) — e
essa parte reproduz exatamente.

Mas o campo diz mais do que a posição. No `tpage` do hardware, **os bits 7-8 são
a profundidade de cor**, e os três valores medidos **não concordam**:

| `tpage` | VRAM | bits 7-8 | primitivas |
| --- | --- | --- | --- |
| `0x0018` | (512, 256) | 0 — **4 bits** | 1.666 |
| `0x001A` | (640, 256) | 0 — **4 bits** | 136 |
| `0x0099` | (576, 256) | 1 — **8 bits** | **1.039** |

**1.039 das 2.841 primitivas — 36,6% — amostram em CLUT de 8 bits**, e no
`EDT_MOD.BIN` elas são a **maioria**: 666 de 1.074.

O plano registra só o outro valor, e em dois lugares:

- **§1.6**, no lado que a task manteve: *"`get_gpu_state --aspect draw`
  responde **`texture_color_mode: "4-bit CLUT"`**"*. É uma amostra de um
  desenho num instante, e vira a única frase do plano sobre profundidade;
- **§1.7**: *"As 23 imagens saem inteiras — **128×128 a 4 bpp cada**"*.

Nada em `tools/looks/` guarda a informação: o `Primitive.tpage_vram` usa os bits
0-3 e o 4 e **descarta os 5 a 11 sem uma palavra** — profundidade e
semitransparência junto. O valor cru fica no atributo `tpage`, então o dado não
se perde; o que se perde é a **conclusão**, e é ela que a Fase 3 vai ler.

**Por que isso custa caro adiante, e não é zelo:** CLUT de 4 bits tem 16
entradas (32 bytes); a de 8 bits tem 256 (512 bytes). A
[`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md) vai caçar a
lista de paletas do `DAT2D.BIN` **por marcador**, e um varredor que assuma 16
entradas acha paletas onde elas não estão e lê 1/16 da que existe — sem
mensagem nenhuma, que é a assinatura de erro que este ciclo inteiro tenta
evitar. A [`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md) e o
renderizador da Fase 5 dependem da mesma escolha.

**Um segundo fato da mesma palavra, e que reforça o primeiro:** das três
páginas, **só a primeira tem entrada no `DAT2D.BIN`**. O `bin_archive.py` lista
imagens em (512, 256) e (544, 256), e nenhuma em (576, 256) nem em (640, 256) —
as linhas 256 do `DAT2D` são só essas duas, mais (896, 256) e (928, 256). Então
1.175 das 2.841 primitivas amostram de páginas que **não vêm do arquivo que a
§1.7 descreve**, e isso também não está escrito.

Nada disso desmente o veredito da task, que está medido pelos dois lados. É a
propriedade descartada em silêncio ao lado dele.

## Evidência

Remedido nesta revisão, direto do disco japonês, pelo `section.py` commitado:

```text
$ python <script desta revisão, sobre layout/section/iso_source>
/BIN/EDT_MOD.BIN
   tpage 0x0018    408 prim  vram (512, 256)  depth=4-bit CLUT abr=0
   tpage 0x0099    666 prim  vram (576, 256)  depth=8-bit CLUT abr=0
/BIN/MODEL.BIN
   tpage 0x0018   1258 prim  vram (512, 256)  depth=4-bit CLUT abr=0
   tpage 0x001a    136 prim  vram (640, 256)  depth=4-bit CLUT abr=0
   tpage 0x0099    373 prim  vram (576, 256)  depth=8-bit CLUT abr=0
```

A conta bate com a da task pelos outros eixos, e é a mesma corrida:

```text
primitives per file: {'/BIN/EDT_MOD.BIN': 1074, '/BIN/MODEL.BIN': 1767} total 2841
bytes 10,11,14,15 all zero: 2841 of 2841
byte3 values: {120: 1520, 121: 645, 122: 540, 127: 136}
clut high byte: {'0x78': 1520, '0x79': 645, '0x7a': 540, '0x7f': 136}
```

A decodificação é a do hardware, os mesmos bits que o `tpage_vram` já usa:

```text
bits 0-3  X da página  (x64)        0x99 & 0x0F = 9   -> 576
bit  4    Y da página  (x256)      (0x99 >> 4) & 1 = 1 -> 256
bits 5-6  semitransparência        (0x99 >> 5) & 3 = 0
bits 7-8  profundidade             (0x99 >> 7) & 3 = 1 -> 8 bits
```

E as linhas de VRAM que o `DAT2D.BIN` ocupa em y=256:

```text
$ MSYS_NO_PATHCONV=1 python tools/pes2/bin_archive.py ls \
    roms/japanese-shift-jis.bin --file /BIN/DAT2D.BIN
    image @      8  vram ( 512, 256)     <- a página 0x18
    image @   3568  vram ( 544, 256)
    image @  58792  vram ( 896, 256)
    image @  62328  vram ( 928, 256)
       (nenhuma em 576, 256 nem em 640, 256)
```

## Causa raiz

A releitura da primitiva registrou **onde** a página está e não **como** ela é
amostrada; o `tpage_vram` usa cinco bits dos doze e o resto sai do registro sem
ninguém notar que um deles contradiz a única frase do plano sobre profundidade.

## Correção

### Arquivo: `tools/looks/section.py`

O `Primitive` ganha a leitura completa do campo, ao lado do `tpage_vram` que já
existe — `tpage_depth` (0 = 4 bits, 1 = 8 bits, 2 = 15 bits diretos) e
`tpage_abr` —, com o comentário dizendo que a profundidade decide a **largura
da CLUT** e que os dois valores aparecem neste disco. O `self_check()` afirma os
dois nas duas páginas que o sintético carrega, e o valor de 8 bits entra no
`build_section()` de propósito: filler que só conhece 4 bits deixaria passar um
consumidor que assumisse 16 entradas.

### Arquivo: `docs/PLAN-LOOKS-PY.md`

- **§1.6** — ao lado de *"páginas de textura em VRAM (512, 256), (640, 256) e
  (576, 256)"*, a contagem por página **e a profundidade de cada uma**, com a
  observação de que o `get_gpu_state` responde `4-bit CLUT` porque amostra um
  desenho, e não o arquivo inteiro. As duas afirmações são verdadeiras e a
  segunda não generaliza.
- **§1.7** — a frase *"128×128 a 4 bpp cada"* passa a dizer o que o
  `bin_archive.py` de fato imprime (`128x128 px 4bpp / 64x128 8bpp` — a
  interpretação depende da profundidade), e ganha que **duas das três páginas
  que a geometria nomeia não têm entrada no `DAT2D.BIN`**, com a pergunta de
  onde elas vêm encaminhada à Fase 3.

### Arquivo: `docs/tasks/looks/10-lista-de-cluts-do-dat2d.md`

O critério ganha a linha que decide a task: a lista de paletas tem de acomodar
**as duas larguras**, e a busca por marcador diz qual encontrou. Varredura que
assuma 16 entradas é o erro silencioso desta fase.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/section.py` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/tasks/looks/10-lista-de-cluts-do-dat2d.md` | modificar |

## Verificação

- [x] `Primitive` expõe a profundidade e a semitransparência, e o `self_check()`
      afirma as duas para `0x0018` e para `0x0099`
- [x] a §1.6 diz quantas primitivas há em cada página e com que profundidade,
      com os números saindo de comando e não de prosa
- [x] a §1.7 não afirma 4 bpp para tudo, e registra as duas páginas sem entrada
      no `DAT2D.BIN`
- [x] `python tools/looks/selftest.py` verde, com os 11 controles vermelhos
- [x] `python tools/looks/modelfile.py --check-image` continua `ok`
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-15

### Resumo do que foi feito

A `Primitive` passou a ler a palavra de página inteira: `tpage_depth` (bits
7-8) e `tpage_abr` (bits 5-6), ao lado do `tpage_vram` que já usava os cinco
bits de posição. O docstring da propriedade diz o que ela decide — **a largura
da paleta**, 16 entradas contra 256 — e não só o que ela é, porque é a
consequência que a Fase 3 precisa ler.

O `self_check()` afirma as duas profundidades, e a de 8 bits entra por uma
seção construída com `tpage=0x0099`: filler que só conhecesse 4 bits deixaria
passar um consumidor que assumisse dezesseis entradas.

### A contagem, remedida antes de escrever

```text
/BIN/EDT_MOD.BIN
   tpage 0x0018    408 prim  vram (512, 256)  depth=4-bit CLUT abr=0
   tpage 0x0099    666 prim  vram (576, 256)  depth=8-bit CLUT abr=0
/BIN/MODEL.BIN
   tpage 0x0018   1258 prim  vram (512, 256)  depth=4-bit CLUT abr=0
   tpage 0x001a    136 prim  vram (640, 256)  depth=4-bit CLUT abr=0
   tpage 0x0099    373 prim  vram (576, 256)  depth=8-bit CLUT abr=0
total primitives: 2841
```

Idêntica à da CORR: **1.039 de 2.841 a 8 bits**, e no `EDT_MOD.BIN` a maioria
(666 de 1.074). A semitransparência é zero nas três páginas — dito porque um
campo lido e sempre zero é informação, e um campo não lido não é.

E as linhas de y=256 do `DAT2D.BIN`, do `bin_archive.py` commitado:

```text
image @      8  vram ( 512, 256)   128x128 px 4bpp / 64x128 8bpp
image @   3568  vram ( 544, 256)   128x128 px 4bpp / 64x128 8bpp
image @  58792  vram ( 896, 256)   128x128 px 4bpp / 64x128 8bpp
image @  62328  vram ( 928, 256)   128x128 px 4bpp / 64x128 8bpp
```

Nem (576, 256) nem (640, 256). **A própria saída da ferramenta já trazia as
duas leituras do mesmo bloco** — `128x128 px 4bpp / 64x128 8bpp` — e a §1.7
tinha escolhido uma delas sozinha.

### O que mudou no plano

A §1.6 ganhou a tabela de página × profundidade × contagem, e a frase do
`get_gpu_state` ganhou a ressalva de que é **amostra de um desenho num
instante**: as duas afirmações são verdadeiras e só a segunda generaliza. A
§1.7 deixou de dizer "128×128 a 4 bpp cada" e passou a dizer o que o comando
imprime, mais as duas páginas sem entrada no arquivo — 1.175 primitivas
amostrando de fora dele, pergunta encaminhada à Fase 3.

A [`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md) recebeu os
números no Contexto e a exigência no critério: o varredor **acomoda as duas
larguras** e diz qual encontrou.

### Problemas encontrados

Nenhum. O veredito da task não muda — o que estava faltando era a propriedade
descartada ao lado dele.

### Arquivos criados/modificados

- `tools/looks/section.py` — `Primitive.tpage_depth`, `Primitive.tpage_abr`, e
  as asserções das duas profundidades no `self_check()`
- `docs/PLAN-LOOKS-PY.md` — §1.6 (a tabela e a ressalva) e §1.7 (as duas
  leituras e as páginas ausentes)
- `docs/tasks/looks/10-lista-de-cluts-do-dat2d.md` — Contexto e critério
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-018.md` — este arquivo
