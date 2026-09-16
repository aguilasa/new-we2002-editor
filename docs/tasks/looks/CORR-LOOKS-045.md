---
id: CORR-LOOKS-045
title: "Correção: o veredito `ranked` aceita qualquer liderança acima de zero, e a razão escrita só cobre teto pequeno"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-LOOKS-045: o piso do confronto é zero, e a justificativa diz outra coisa

## Problema identificado

O `confront.verdict` tem três desfechos para a tupla certa numa linha da
matriz:

```python
if right - wrong >= MARGIN:
    out[game] = ("win", ...)
elif right > wrong:
    out[game] = ("ranked", ...)      # não falha
else:
    out[game] = ("unexplained", ...) # falha
```

Então o gate só falha quando a tupla certa **empata ou perde**. Qualquer
liderança acima de zero passa — como `win` se for de 0,02 ou mais, como
`ranked` se for menor.

O nível `ranked` foi acrescentado **depois** de a primeira corrida ser lida, e
tanto o código quanto o Log dizem isso com honestidade, apoiados num limite:

> for normalised histograms, `I(g, a) - I(g, b) <= 1 - I(a, b)` … Measured on
> 2026-09-16: our reference and our `A-A1-A-B-E` are 0.961 alike … so the most
> either can lead the other by is 0.039, and a MARGIN of 0.02 asks for half the
> ceiling … A lead under MARGIN is therefore printed with that ceiling beside
> it, and does not fail

O limite está certo — conferi: `min(g, a) − min(g, b) ≤ max(a − b, 0)` ponto a
ponto, e a soma dá `1 − I(a, b)`. **O que não confere é a regra que ele
justifica.** O argumento vale para um teto de 0,039, onde 0,02 é metade do
possível. O código não consulta o teto: aplica `ranked` a **qualquer** liderança
abaixo de 0,02, inclusive onde os nossos dois renders distam 0,5 e uma
liderança de 0,001 é um cara-ou-coroa.

A frase do Log — "a razão é o limite, não o número" — descreve a intenção. O
código usa o número.

## Evidência

Os dois `ranked` da corrida real são justamente o par de teto 0,039, então os
veredictos de hoje estão certos:

```text
$ python tools/looks/confront.py --score        (duas vezes, saída idêntica)
      A-A1-A-A-A   RANKED   first by 0.016 over A-A1-A-B-E, whose render ours
                            is 0.039 apart from -- the most any lead can be
      A-A1-A-B-E   RANKED   first by 0.010 over A-A1-A-A-A, whose render ours
                            is 0.039 apart from -- the most any lead can be
```

O defeito é o que a mesma regra faz com um teto grande. Chamando o `verdict` do
módulo commitado com dois renders que distam 0,5 e uma liderança de 0,001:

```text
X ('ranked', 'first by 0.001 over Y, whose render ours is 0.500 apart from
              -- the most any lead can be')
Y ('win', 'by 0.800 over X')
```

**Passa** — e a própria mensagem imprime o número que desmente a passagem: a
liderança poderia ser 0,5 e foi 0,001.

Não é hipótese distante. Na matriz de hoje o par `A-I3-A-A-A`/`A-A1-A-A-A` tem
teto **0,204** (os renders distam 0,796) e ganha por 0,028 — um pouco acima da
margem. Uma mudança no render que o levasse para 0,015 sairia `ranked` verde,
com 7% do teto usado.

## Causa raiz

O `ranked` foi escrito para o único par em que a margem pedia metade do teto, e
a condição ficou `right > wrong` em vez de ser a comparação com o teto que a
docstring usa para justificá-lo.

## Correção

### Arquivo: `tools/looks/confront.py`

Fazer a regra dizer o que a justificativa diz: `ranked` só quando a margem é
inalcançável **por causa do teto** — por exemplo, quando a liderança é pelo
menos metade do teto (`right − wrong >= (1 − alike) / 2`), ou quando o próprio
teto está abaixo de `2 × MARGIN`. Fora disso, liderança abaixo da margem é
`unexplained`, como era antes da primeira corrida.

Escolher a forma exata é da execução; o que ela tem de preservar é que os dois
`ranked` reais (teto 0,039, lideranças 0,016 e 0,010) continuem passando, e que
o caso de teto 0,5 com liderança 0,001 falhe.

### Arquivo: `tools/looks/controls.py`

Um controle que devolva a condição a `right > wrong` e exija o vermelho — com um
caso de teto grande no `self_check()`, que é o que o controle
`confront-margin-ignored` de hoje não alcança: ele troca a margem por `-1.0`,
o que transforma **derrotas** em vitória e fica vermelho por isso, não por uma
liderança fraca sob teto largo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/confront.py` | modificar |
| `tools/looks/controls.py` | modificar |
| `docs/tasks/looks/17-confronto-com-o-emulador.md` | modificar (a frase do nível `ranked`) |
| `docs/PLAN-LOOKS-PY.md` | modificar, se a §5.3 descrever a regra |

## Verificação

- [ ] `python tools/looks/confront.py --score` verde, com os mesmos dois
      `ranked` e os mesmos três `win` do slot 2
- [ ] `verdict` com teto 0,5 e liderança 0,001 devolve `unexplained`
- [ ] o controle novo fica vermelho
- [ ] `python tools/looks/selftest.py --quiet` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
