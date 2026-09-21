---
id: CORR-LOOKS-039
title: "Correção: os pares do `looks_ui` nunca saem da família A, e o defeito da CORR-LOOKS-034 passou por eles"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-16
severity: medium
done_on: 2026-09-16
done_commit: 3c65af4
---

# CORR-LOOKS-039: o gate da UI mede a única cabeça em que o código funcionava

## Problema identificado

O `ui_check.PAIRS` confronta duas tuplas contra a referência:

```python
REFERENCE = "A-A1-A-A-A"
PAIRS = (
    ("B-A1-A-A-A", "SKIN", 40.0),
    ("A-A1-C-A-A", "H.COL", 12.0),
)
```

As três são da família `A`, que veste a seção 24 — **a única cabeça a que as
linhas de cor chegavam** até a [`CORR-LOOKS-034`](/docs/tasks/looks/CORR-LOOKS-034.md).
O defeito era exatamente esse: `SKIN`, `H.COL`, `H.F.COL.` e `FACE` endereçados
a `(MODEL.BIN, 24)` enquanto a cabeça desenhada é a que o `head_of()` escolhe,
de modo que 29 dos 32 estilos saíam sem cor nenhuma.

O `looks_ui` rodou verde o tempo todo. Quem achou o defeito foi a revisão, à
mão. A CORR-034 acrescentou o caso cruzado ao `scene.py --check-image` e
**não** ao gate da UI, que continua com os mesmos dois pares da família `A`.

Um gate cuja escolha de amostra evita a região defeituosa não é um gate mais
fraco: é um gate que não cobre o que diz cobrir.

## Evidência

Replantando o defeito da CORR-034 — `where_head = HEAD` de volta no `edits()` —
numa cópia da árvore, e rodando os dois gates sobre ela:

```text
$ python <cópia>/tools/looks/ui_check.py
  A-A1-A-A-A vs B-A1-A-A-A (SKIN): 193050 of 409600 (47.13%), floor 40.0%
  A-A1-A-A-A vs A-A1-C-A-A (H.COL): 70336 of 409600 (17.17%), floor 12.0%
looks_ui: 3 of 3 negative control(s) red, and the window drew every tuple it
          was asked for
exit=0

$ cd <cópia> && python tools/looks/scene.py --check-image
scene --check-image: 2 problem(s)
    a skin changed no surface on a head that is not section 24, so the colour
    rows are addressed to a section this tuple does not draw
    no part of a non-A head is marked as taking colour by a borrowed index
```

O gate do núcleo fica **vermelho** e o gate da UI passa **verde**, na mesma
árvore, no mesmo defeito.

E o par que faltava já está medido, na verificação da própria CORR-034:
`A-I3-A-A-A` contra `B-I3-A-A-A` move **14,54%** dos pixels da cabeça, bem
acima do piso de 40% que o `SKIN` usa hoje na família `A`… e é por isso que o
piso não se copia: a cabeça `I3` responde menos que a `A1`, e um par novo traz
piso próprio, medido.

## Causa raiz

Os pares foram escolhidos na LOOKS-TASK-16 a partir dos números que a
LOOKS-TASK-15 tinha deixado medidos, e os dois que ela tinha medido eram da
família `A`.

## Correção

### Arquivo: `tools/looks/ui_check.py`

Acrescentar ao `PAIRS` **pelo menos um par de cabeça não-`A`** — `B-I3-A-A-A`
contra a referência `A-I3-A-A-A` é o medido —, o que implica ou uma segunda
referência, ou trocar `PAIRS` por uma lista de `(base, outra, linha, piso)`
para que cada par diga de onde parte. O piso de cada par novo sai da corrida,
como os dois de hoje saíram, e vem com a data ao lado.

E um controle negativo que reponha o `where_head = HEAD`: se o gate da UI tem
de cobrir esse defeito, tem de ficar vermelho quando ele volta. É a diferença
entre cobrir e coincidir.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/ui_check.py` | modificar |
| `docs/tasks/looks/16-contratos-da-ui.md` | modificar (os pares e os pisos do Log) |

## Verificação

- [x] `python tools/looks/ui_check.py` verde, com um par de cabeça não-`A`
- [x] o mesmo gate fica **vermelho** com `where_head = HEAD` replantado —
      `exit=1`, e antes deste conserto saía `exit=0`
- [x] cada piso novo tem a corrida que o mediu escrita ao lado
- [x] `python tools/looks/selftest.py --quiet` verde, 40 de 40 controles
      vermelhos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

A evidência reproduz, e com o defeito replantado in loco:

```text
$ python tools/looks/ui_check.py          # com where_head = HEAD de volta
looks_ui: 3 of 3 negative control(s) red, and the window drew every tuple …
exit=0
$ python tools/looks/scene.py --check-image
scene --check-image: 2 problem(s)
```

O `PAIRS` virou `(de onde parte, com quem compara, a linha, o piso)` — cada par
diz a própria base — e ganhou o terceiro:

```text
A-A1-A-A-A vs B-A1-A-A-A (SKIN):  193050 of 409600 (47.13%), floor 40.0%
A-A1-A-A-A vs A-A1-C-A-A (H.COL):  70336 of 409600 (17.17%), floor 12.0%
A-I3-A-A-A vs B-I3-A-A-A (SKIN):   59548 of 409600 (14.54%), floor 10.0%
```

**O piso do terceiro é dele, e é por isso que não se copia:** a cabeça `I3`
responde a uma troca de pele com 14,54% da imagem, e os 40% da `A1` reprovariam
um visualizador que funciona.

### A prova de que agora cobre

Replantado o `where_head = HEAD` na árvore e rodado o gate inteiro:

```text
A-I3-A-A-A vs B-I3-A-A-A (SKIN): 0 of 409600 pixel(s) differ (0.00%), floor 10.0%
FAIL: B-I3-A-A-A moves SKIN and differs from A-I3-A-A-A in 0.00% of the
      pixels, under the 10.0% floor -- the tuple did not reach the picture
exit=1
```

Antes deste conserto, a mesma árvore com o mesmo defeito saía **0**. É a
diferença entre cobrir e coincidir.

### O controle negativo não cabe no `controls.py`, e a razão está medida

O motor de controles roda `<módulo>.py --check`, que no `ui_check.py` é o
`self_check()` — a metade sintética, que julga imagens plantadas em memória e
**não** abre janela nem lê disco. Um controle que mexe no `assembly.py` não
alcança esse caminho. O que cobre o defeito é o gate inteiro, e a corrida
acima é a medição dele; o que entrou no `self_check()` foram duas asserções
sobre a **forma** dos pares: que cada um diz de onde parte, e que ao menos um
parte de cabeça que não é a da seção 24 — de modo que apagar o terceiro par
fica vermelho sem precisar de janela.

### Problemas encontrados

Nenhum.

### Arquivos criados/modificados

- `tools/looks/ui_check.py` — `PAIRS` com base por par, o par `I3`, os três
  usos que liam a referência fixa, e as duas asserções de forma
- `docs/tasks/looks/16-contratos-da-ui.md` — o contexto e o critério
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-039.md` — este arquivo
