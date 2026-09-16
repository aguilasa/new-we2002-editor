---
id: CORR-LOOKS-042
title: "Correção: os quads de cabelo saem uma linha curtos — o jogo desenha v 15 onde o disco guarda 14"
type: correção
category: render
status: pendente
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

- [ ] `confront.py --score` sobre as capturas da LOOKS-TASK-17 dá `stored 7`
      e `stored, one row off 0`
- [ ] um caso sintético no `self_check` com o `v` das quatro quinas
- [ ] controle negativo vermelho

## Log de Execução

*(preencher ao executar)*
