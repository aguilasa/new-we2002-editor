---
id: CORR-LOOKS-043
title: "Correção: o goleiro desenha qualquer estilo de cabelo como família A, e não recusa"
type: correção
category: render
status: pendente
depends_on: []
---

# CORR-LOOKS-043: a recusa do `head_of` só vale para a figura 0

## Problema identificado

Na figura 0 (jogador de linha) o `assembly.head_of` **recusa** os estilos que o
`HAIR_MAP` não alcançou — `A-H1-A-A-A` sai com saída 2. Na figura 1 (goleiro)
o `sections_of` nem consulta o mapa: devolve a seção 24 do disco para qualquer
estilo. O resultado é o que o ciclo inteiro existe para não fazer: **um `I3` ou
um `H1` desenhado como `A1`, perfeitamente e em silêncio**.

A docstring do `sections_of` chama isso de "lacuna nomeada", e é — no código.
Na tela não há nome nenhum: nem recusa, nem nota na cena.

## Evidência

Confronto da [`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md),
slot 1:

```text
$ python tools/looks/confront.py --score
  slot 2 A-H1-A-A-A: our side refuses -- app: A-H1-A-A-A refuses -- hair style H1 ...
  ...
  slot 1, figure 1: histogram intersection over the 34 colour(s) our side draws
      our own renders, pairwise: ... A-A1-A-A-A~A-H1-A-A-A 1.000,
          A-A1-A-A-A~A-I3-A-A-A 1.000, ... A-H1-A-A-A~A-I3-A-A-A 1.000, ...
      A-I3-A-A-A   EXPECTED    the goalkeeper's head: ...
      A-H1-A-A-A   EXPECTED    the goalkeeper's head: ...
```

O slot 2 imprime a recusa do `H1`; o slot 1 não imprime recusa nenhuma.

Três tuplas de estilos diferentes, três renders com o **mesmo** histograma de
cor — interseção 1,000 entre cada par.
O `confront.EXPECTED` as marca como resíduo para o gate não mentir, e aponta
para esta correção.

## Causa raiz

O mapa foi medido só no slot 2. A decisão de deixar a figura 1 com a cabeça do
disco estava certa como limite de medição e errada como comportamento: o
limite virou desenho em vez de virar recusa.

## Correção

### Arquivo: `tools/looks/assembly.py`

Duas saídas honestas, e escolher entre elas é desta correção:

1. a figura 1 **recusa** qualquer estilo que não seja o da cabeça do disco,
   com mensagem que diga que o mapa é do jogador de linha; ou
2. medir o mapa no slot 1 (`oracle.py --patched HAIR` no goleiro) e dar à
   figura 1 o `HAIR_MAP` dela.

A 1 fecha o defeito; a 2 fecha o resíduo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/assembly.py` | modificar |
| `tools/looks/confront.py` | tirar os dois itens do `EXPECTED` quando o desfecho permitir |
| `tools/looks/controls.py` | controle que devolva a cabeça do disco à figura 1 |

## Verificação

- [ ] `app.py --figure 1 --looks A-I3-A-A-A` recusa com saída 2, ou desenha a
      cabeça medida
- [ ] `confront.py --score 1` sem `EXPECTED` para o goleiro, ou com a razão
      nova
- [ ] controle negativo vermelho

## Log de Execução

*(preencher ao executar)*
