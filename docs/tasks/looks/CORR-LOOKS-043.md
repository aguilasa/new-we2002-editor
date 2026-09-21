---
id: CORR-LOOKS-043
title: "Correção: o goleiro desenha qualquer estilo de cabelo como família A, e não recusa"
type: correção
category: render
status: done
depends_on: []
origin: LOOKS-TASK-17
severity: medium
done_on: 2026-09-16
done_commit: 6b6b671
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

- [x] `app.py --figure 1 --looks A-I3-A-A-A` recusa com saída 2
- [x] `confront.py --score` sem `EXPECTED` para o goleiro — o `EXPECTED` ficou
      vazio
- [x] controle negativo vermelho (`assembly-goalkeeper-draws-any-style`)

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

**Saída 1, a recusa** — a que fecha o defeito. A 2, medir o mapa no goleiro,
fecha o resíduo e continua aberta: é uma corrida de `oracle.py --patched HAIR`
no slot 1, e não entrou neste lote.

O `goalkeeper_head()` recusa, para a figura 1, todo estilo que não seja o da
cabeça do disco — `DISC_STYLE = 0`, o `A1` —, e o `sections_of` o chama
sempre que recebe uma tupla para uma figura que não é a 0:

```text
$ <venv>/python tools/looks/ui/app.py --figure 1 --looks A-I3-A-A-A --screenshot …
app: A-I3-A-A-A refuses -- hair style I3 on figure 1: HAIR_MAP was measured on
the outfield player only, and the goalkeeper's heads (MODEL.BIN 74..105) were
never walked -- figure 1 draws the disc's own head, which is A1, and nothing else
exit=2

$ … --figure 1 --looks A-A1-A-A-A
exit=0
```

### O confronto, re-julgado

O lado **nosso** da corrida salva da LOOKS-TASK-17 foi renderizado de novo —
o mesmo laço com que o `confront.run` começa, sem emulador —, e as capturas do
jogo ficaram como estavam:

```text
slot 1 A-I3-A-A-A: our side refuses -- … on figure 1 …
slot 1 A-H1-A-A-A: our side refuses -- … on figure 1 …
      A-A1-A-A-A   RANKED   first by 0.016 over A-A1-A-B-E …
      B-A1-A-A-A   WIN      by 0.536 over A-A1-A-A-A
      A-A1-C-A-A   WIN      by 0.265 over A-A1-A-A-A
      A-A1-A-B-E   RANKED   first by 0.010 over A-A1-A-A-A …
slot 1: 2 win, 2 ranked, 0 expected, 0 unexplained
confront: ok
```

`EXPECTED` virou `{}`: não sobrou resíduo a desculpar. O mecanismo continua —
o `verdict()` ganhou um parâmetro `expected`, e o `self_check()` o exercita com
um resíduo sintético, porque mecanismo que nada exercita não é mecanismo.

### Problemas encontrados

Um, pequeno e anotado: o `confront.run` apaga o PNG velho antes de renderizar e
**não** apaga o `.refused` velho, então uma tupla que passasse de recusada a
desenhada ficaria com os dois. Não acontece neste lote — a direção aqui é a
contrária —, e o script de re-render usado acima apaga os dois.

### Arquivos criados/modificados

- `tools/looks/assembly.py` — `DISC_STYLE`, `goalkeeper_head()`, a chamada no
  `sections_of` e as três asserções
- `tools/looks/confront.py` — `EXPECTED` vazio, `verdict(expected=)`, e o caso
  sintético do resíduo
- `tools/looks/controls.py` — `assembly-goalkeeper-draws-any-style`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-043.md` — este arquivo

*(preencher ao executar)*
