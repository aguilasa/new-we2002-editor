---
id: CORR-LOOKS-042
title: "Correção: os quads de cabelo saem uma linha curtos — o jogo desenha v 15 onde o disco guarda 14"
type: correção
category: render
status: concluído
depends_on: []
---

# CORR-LOOKS-042: a faixa de cabelo é aplicada sobre o `v` do disco, e o jogo reescreve o `v`

## Problema identificado

O confronto da [`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md)
leu a display list do jogo no quadro de referência (`A-A1-A-A-A`, slot 2) e
casou os pacotes de quad texturizado com as primitivas da seção 24. **Duas**
delas só casam com folga de uma linha em `v` — e são exatamente as duas do
`layout.HAIR_QUADS[24]`, as primitivas 1 e 14.

A causa está escrita no próprio `layout.HAIR_QUAD_STORE`: a instrução do jogo
grava `v = faixa * 16 + 15` nas quinas 0 e 2 e `faixa * 16 + 1` nas quinas 1
e 3. O disco guarda **14** nas quinas 0 e 2. O `scene.part_for` soma a faixa
ao `v` **do disco**, então desenha o quad de cabelo uma linha de texel mais
curto que o jogo, em toda faixa e nas quatro cabeças do `HAIR_QUADS`.

## Evidência

```text
$ python tools/looks/confront.py --score     # sobre as capturas de --run
  the diagonal: 539 textured quad packet(s) in the two bands, and the head's 18 primitive(s):
      stored                   5
      untangled                0
      stored, one row off      2
      ...
```

O `ROW_SLACK = 1` do `confront.py` existe por causa deste caso, e a docstring
dele registra os dois valores. Sem a folga, as duas primitivas saem `absent`.

## Causa raiz

A LOOKS-TASK-14 mediu **em que faixa** cada estilo cai e **quais primitivas**
o jogo reescreve, e o `draw_list` modela isso como "somar `faixa * 16` ao `v`".
O `v` que o jogo escreve não é o do disco mais um deslocamento: é um valor
absoluto, e o disco começa uma linha abaixo.

## Correção

### Arquivo: `tools/looks/assembly.py` e `tools/looks/scene.py`

Para as primitivas do `HAIR_QUADS` da cabeça escolhida, o `v` desenhado sai da
regra do store — `faixa * ATLAS_BAND + 1` e `+ 15`, nas quinas que a
disassembly nomeia — e não do disco. As constantes 1 e 15 moram no `layout.py`,
ao lado do `HAIR_QUAD_STORE`, que é quem as mediu.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | modificar — as duas linhas do store como constante |
| `tools/looks/assembly.py` e/ou `tools/looks/scene.py` | modificar |
| `tools/looks/controls.py` | um controle que volte ao `v` do disco |

## Verificação

- [x] `confront.py --score` sobre as capturas da LOOKS-TASK-17 dá `stored 7`
      e `stored, one row off 0`
- [x] um caso sintético no `self_check` com o `v` das quatro quinas
- [x] controle negativo vermelho (`assembly-hair-v-from-disc`)

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

A evidência reproduz nas capturas da LOOKS-TASK-17, sem emulador:

```text
$ python tools/looks/confront.py --score      # antes
      stored                   5
      stored, one row off      2
```

E o disco mostra que a regra não é só da seção 24 — as **quatro** cabeças do
`HAIR_QUADS` guardam linhas diferentes das que o store escreve:

```text
section 24 primitive  1  ((188, 14), (188, 1), (199, 14), (199, 1))
section 26 primitive  1  ((188, 14), (188, 0), (198, 14), (195, 1))
section 34 primitive  0  ((176, 15), (178, 2), (184, 15), (184, 2))
section 46 primitive  0  ((208, 79), (209, 66), (215, 79), (214, 66))
```

O store escreve `faixa * 16 + 15` nas quinas 0 e 2 e `faixa * 16 + 1` nas 1 e
3. Isso virou `layout.HAIR_QUAD_ROWS = (15, 1, 15, 1)`, ao lado do
`HAIR_QUAD_STORE`, e `assembly.hair_texcoords()` devolve as quatro `(u, v)` com
`u` do arquivo e `v` **absoluto**. O `draw_list` manda essas coordenadas para
as primitivas do `HAIR_QUADS` da cabeça escolhida, e o `scene.part_for` desenha
com elas em vez de somar a faixa ao `v` do disco.

O confronto passou a comparar a display list do jogo com o que **desenhamos**,
não com o arquivo cru:

```text
$ python tools/looks/confront.py --score      # depois
      stored                   7
      stored, one row off      0
      verdict: the game draws the STORED order
```

### O que mudou na tela

Os quads de cabelo mudam de linha, então os percentuais do `looks_ui` andaram:
`B-A1` 47,13% → **48,29%**, `A-A1-C` 17,17% → **15,81%**, `B-I3` 14,54% →
**13,66%**. Os três pisos (40, 12, 10) continuam com folga. Os números velhos
estavam escritos como medição no `ui_check.py` e na LOOKS-TASK-16 —
reconciliados em commit próprio.

### Problemas encontrados

Nenhum no conserto. O `ROW_SLACK` do `confront.py` ficou, com a razão
atualizada: um "one row off" diferente de zero é exatamente como um `v`
desenhado voltaria a divergir do jogo, e ele é impresso.

### Arquivos criados/modificados

- `tools/looks/layout.py` — `HAIR_QUAD_ROWS`
- `tools/looks/assembly.py` — `hair_texcoords()`, as coordenadas no
  `draw_list` e o caso sintético
- `tools/looks/scene.py` — `part_for` desenha com as coordenadas do store
- `tools/looks/confront.py` — a diagonal contra o que desenhamos; a razão do
  `ROW_SLACK`
- `tools/looks/controls.py` — `assembly-hair-v-from-disc`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-042.md` — este arquivo
