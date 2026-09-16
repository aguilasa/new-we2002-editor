---
id: CORR-LOOKS-028
title: "Correção: o `draw_list` joga fora a segunda faixa que o `HAIR_MAP` mediu, e não diz"
type: correção
category: núcleo
status: concluído
depends_on: []
---

# CORR-LOOKS-028: a segunda faixa do cabelo é descartada em silêncio

## Problema identificado

O `assembly.HAIR_MAP` guarda, por estilo, **a seção e as faixas** em que os
quads reescritos caíram — e para dez dos 29 estilos mapeados são **duas ou
mais**. O `draw_list` aplica a **primeira** e ignora o resto:

```python
# tools/looks/assembly.py, dentro de draw_list()
quads = layout.HAIR_QUADS.get(chosen)
if quads:
    plan.setdefault((layout.MODEL, chosen), {})[quads] = (
        HEAD_BAND, bands[0])
```

`bands[0]` é escolha, não medição: nada mediu **qual quad recebe qual faixa**,
e o comentário ao lado explica a outra decisão (por que só quatro seções levam
faixa), não esta. A própria task diz o que se faz nesse caso — o `head_of`
**recusa** os três estilos que não escreveram nada em vez de devolver a cabeça
do `A`, "que desenharia perfeitamente e seria de outro". Aqui a mesma dúvida
desenha perfeitamente e não recusa nada.

O alcance prático hoje é **um estilo**, e é o que torna o conserto barato: dos
dez de faixa múltipla, só o `B1` mora numa seção cujos quads o
`layout.HAIR_QUADS` nomeia. Nos outros nove o `draw_list` não aplica faixa
nenhuma, porque `quads` é `None`.

## Evidência

O mapa, lido do módulo:

```text
multi-band entries in HAIR_MAP:
  B1  section 26  bands (0, 1)  quads known: (1, 3)
  C1  section 30  bands (0, 1)  quads known: None
  D1  section 48  bands (0, 1)  quads known: None
  E2  section 54  bands (0, 1)  quads known: None
  F1  section 52  bands (0, 1, 3)  quads known: None
  G1  section 28  bands (0, 1)  quads known: None
  J1  section 36  bands (0, 1)  quads known: None
  K1  section 32  bands (0, 1, 3, 4)  quads known: None
  O1  section 44  bands (0, 1)  quads known: None
  P1  section 50  bands (0, 1)  quads known: None
```

A lista de desenho do `B1`, com os dois quads (1 e 3) da seção 26 na **mesma**
faixa:

```text
python tools/looks/assembly.py --tuple A-B1-A-A-A
    /BIN/MODEL.BIN     section 26  image 3568   palette (144, 480, 16)   band +0  x2
    /BIN/MODEL.BIN     section 26  image 3568   palette (16, 480, 16)    band +0  x2
```

`band +0` nos quatro, quando a medição registrou as faixas **0 e 1**. A faixa 1
não aparece em lugar nenhum da lista.

E o `--writes` já lê as duas coisas no mesmo acerto — `a0` é a primitiva e `a2`
é a faixa —, tanto que a saída transcrita na task nomeia as duas juntas:

```text
  B4   MODEL.BIN section 26: primitive 1 band 5, primitive 3 band 1, ...
```

## Causa raiz

O `HAIR_MAP` foi medido pelo `--patched`, que diz **quais faixas** a seção
passou a usar mas não qual quad ficou com qual; o `draw_list` precisava de uma
faixa por quad e pegou a primeira, sem registrar que a escolha não é medida.

## Correção

### Arquivo: `tools/looks/assembly.py`

Duas saídas, e a segunda serve enquanto a primeira não é medida:

1. **Medir**, que é barato porque a corrida já existe: o `oracle.py --writes`
   nomeia primitiva e faixa no mesmo acerto do breakpoint. Guardar
   `{primitiva: faixa}` em vez de uma tupla de faixas para os estilos cujos
   quads o `layout.HAIR_QUADS` conhece, e aplicar cada quad com a sua.
2. **Enquanto não estiver medido**, tratar faixa múltipla como o `head_of`
   trata estilo mudo: `BadAssembly` com a razão, ou — se a v1 precisar
   desenhar o `B1` — aplicar `bands[0]` com o comentário dizendo que a
   atribuição quad↔faixa **não foi medida**, e um caso vermelho que fique
   verde no dia em que for.

Também vale nomear o número no módulo, ao lado de `HAIR_MAP_SILENT` e
`HAIR_MAP_SECTIONS`, para que preencher a medição tenha de passar por aqui:
quantos estilos têm mais de uma faixa (dez) e quantos deles alcançam o
`draw_list` (um).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/assembly.py` | modificar |
| `tools/looks/controls.py` | modificar (o caso vermelho da atribuição não medida) |
| `docs/PLAN-LOOKS-PY.md` | modificar (§6(c): o resíduo ganha esta linha) |
| `docs/tasks/looks/14-tabela-de-montagem.md` | modificar (o resíduo encaminhado) |

## Verificação

- [x] `python tools/looks/assembly.py --check` verde, com o caso novo vermelho
      quando plantado (`assembly-band-choice-silent`)
- [x] `python tools/looks/assembly.py --check-image` verde
- [x] `python tools/looks/assembly.py --tuple A-B1-A-A-A` **marca** a linha:
      aplica a primeira faixa e diz, ali mesmo, que a atribuição quad↔faixa não
      foi medida — nunca um `band +0` igual aos outros
- [x] `python tools/looks/selftest.py --quiet` verde, 33 de 33 controles
      vermelhos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

A evidência reproduz: dez estilos de faixa múltipla, e só o `B1` com quads
conhecidos.

```text
B1  section 26  bands (0, 1)  quads known: (1, 3)
C1  section 30  bands (0, 1)  quads known: None
...  (dez ao todo; nos outros nove o draw_list não aplica faixa nenhuma)
```

A v1 desenha o `B1`, então o caminho escolhido foi o segundo da CORR — aplicar
`bands[0]` **dizendo que a atribuição não foi medida**, em vez de recusar um
estilo que o jogo tem. O que mudou é que a escolha deixou de ser invisível:

```text
$ python tools/looks/assembly.py --tuple A-B1-A-A-A
    /BIN/MODEL.BIN  section 26  image 3568  palette (16, 480, 16)  band +0  x2
        BAND NOT MEASURED: the style also landed in band(s) 1, and which quad
        takes which was never measured
```

A marca viaja com a primitiva (`band_unmeasured` em cada parte da lista de
desenho), não com uma nota de rodapé: são as duas primitivas do
`layout.HAIR_QUADS[26]` — 1 e 3 — e nenhuma outra linha da lista é tocada.

### Os dois números têm nome, e é por eles que a medição vai passar

`HAIR_MAP_MULTI_BAND = 10` e `HAIR_MAP_BANDS_UNMEASURED = 1`, asseridos no
`self_check()` contra o próprio `HAIR_MAP` cruzado com o `layout.HAIR_QUADS`.
O segundo sobe assim que o `--writes` nomear os quads das outras nove seções —
**antes** de a atribuição quad↔faixa ser medida —, que é exatamente o momento
em que alguém precisa ser avisado.

E a medição que falta é de uma corrida só: o breakpoint do `--writes` lê `a0`,
a primitiva, e `a2`, a faixa, no **mesmo** acerto. O par sai junto; ninguém o
pediu ainda.

Controle novo, `assembly-band-choice-silent`: o `unmeasured_bands` devolvendo
sempre vazio. Vermelho.

### Problemas encontrados

Nenhum. A varredura de discrepância não puxou nada além dos dois documentos
que a própria CORR previa.

### Arquivos criados/modificados

- `tools/looks/assembly.py` — `multi_band_styles()`, `unmeasured_bands()`, os
  dois números, a marca em cada parte da lista de desenho e a linha do
  `--tuple`
- `tools/looks/controls.py` — o controle `assembly-band-choice-silent`
- `docs/PLAN-LOOKS-PY.md` — §6(c), o resíduo da faixa por quad
- `docs/tasks/looks/14-tabela-de-montagem.md` — o mesmo no critério
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-028.md` — este arquivo
