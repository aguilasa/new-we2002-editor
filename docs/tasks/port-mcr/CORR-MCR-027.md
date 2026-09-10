---
id: CORR-MCR-027
title: "Correção: \"as faixas válidas começam todas em 0x02044\" é falso como escrito, e o que se mediu é outra coisa"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-MCR-027: as faixas da soma não começam todas no mesmo byte

## Problema identificado

[`/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md`](/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md):175
descreve a busca que achou a regra assim:

> as faixas válidas para `0x02102` **começam todas em `0x02044`** — o byte logo
> depois do campo de alta entropia —, e as de `0x02202` **começam todas em
> `0x02186`**, onde a anterior termina.

Reproduzindo a busca, as faixas consistentes são **milhares**, e começam em
qualquer byte entre o citado e o próprio byte de soma. O que a medição sustenta
é o **limite inferior**: nenhuma faixa consistente começa **antes** de
`0x02044` (ou de `0x02186`), o que é o achado interessante e é outra frase.

A diferença não é de estilo. Quem ler a frase como está e for procurar "a"
faixa vai achar 23.875 candidatas e concluir que a busca não fecha; e vai
perder o que ela de fato fixa — que o campo de alta entropia fica **fora** da
soma, que é o que permite deixá-lo zerado.

## Evidência

Busca de faixa `(a, b)` com `k` consistente nos seis cartões distintos, `a` no
bloco 1 e `b` até o fim do bloco 2:

```
cand 0x02102: 23875 faixas consistentes; inicios = 0x2044, 0x2045, 0x2046, ...
    a=0x02044 b=0x02186 k=0x8a
    a=0x02044 b=0x02187 k=0x8a
cand 0x02202: 27250 faixas; inicio minimo=0x02186, fim minimo=0x04e30
cand 0x0216d: 0 faixas
cand 0x02205: 0 faixas
```

O `0x02202` merece nota à parte: com a busca limitada a `b < 0x2400` ele dá
**zero** soluções, e só aparece quando a janela vai até o fim do bloco 2. O
fim mínimo medido é `0x04e30` — mais forte que o "não foi determinado" do mapa,
e é informação que a task seguinte usa para saber que a segunda soma cobre a
área de jogador.

Os dois descartes (`0x0216d`, `0x02205`) reproduzem exatamente como escrito:
zero faixas.

## Causa raiz

A frase relata o menor início como se fosse o único, e a janela da busca
original não alcançava o fim da segunda faixa.

## Correção

### Arquivo: `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md`

Trocar "começam todas em" por "nenhuma começa antes de", com o número de
faixas consistentes ao lado, e dizer o que isso fixa: o campo de alta entropia
está fora da soma.

### Arquivo: `docs/MCR-DESBLOQUEIOS.md`

Onde ele diz do `0x02202` "o fim dela não foi determinado", acrescentar o
limite medido: `b >= 0x04e30`, com a nota de que uma busca que pare em
`0x02400` não acha o `0x02202` — armadilha que custa a conclusão errada de que
o segundo byte não é soma.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md` | modificar |
| `docs/MCR-DESBLOQUEIOS.md` | modificar |

## Verificação

- [x] a busca reproduzida sobre os seis cartões distintos dá os números que o
      doc afirma (faixas, início mínimo, fim mínimo)
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-10

**Resumo do que foi feito:**

"Começam todas em `0x02044`" virou o que a medição sustenta: **nenhuma faixa
consistente começa antes de** `0x02044`, com o número de faixas ao lado —
23.875 para `0x02102`, 27.250 para `0x02202` — numa tabela de três colunas
(faixas, início mínimo, fim mínimo). A frase agora diz o que o limite inferior
fixa: **o campo de alta entropia está fora da soma**, que é o que permite
deixá-lo zerado.

O `MCR-DESBLOQUEIOS.md` ganhou o limite medido do segundo bloco —
`b >= 0x04e30`, logo a segunda soma cobre a área de jogador — nas duas
frases onde o fim aparecia como "não determinado", e a armadilha da janela:
**uma busca que pare em `0x02400` acha zero faixas para o `0x02202`** e conclui
que ele não é soma.

**A busca entrou no bloco "Reproduzir"**, que só tinha a receita da sonda. Ela
não é força-bruta: `k` de `[a, b)` é `2*byte[C] - (P[b] - P[a])`, então dois
cartões concordam quando a diferença dos prefixos deles é constante, e os
8.192 × 16.384 pares viram uma busca em dicionário — segundos, sem `numpy`,
que não está instalado nesta máquina.

**Problemas encontrados:**

Nenhum. A reprodução deu os quatro números da CORR na primeira corrida, e o
trecho como ficou escrito no doc foi rodado verbatim depois de colado.

Duas coisas que o `0x02202` não tem, e que o doc agora não sugere ter: um `k`
único — ele varia com a faixa (`0xa2` em `[0x02186, 0x04e30)`) — e um fim ao
byte.

**Medições:**

| candidato | faixas consistentes | início mínimo | fim mínimo |
|---|---:|---|---|
| `0x02102` | **23.875** | `0x02044` | `0x02186` |
| `0x02202` | **27.250** | `0x02186` | **`0x04e30`** |
| `0x0216d` | **0** | — | — |
| `0x02205` | **0** | — | — |

Janela da busca: `a` em `[0x2000, 0x4000)`, `b` em `(a, 0x6000]`, seis cartões
distintos. O trecho do doc reproduz os quatro resultados como escritos.
`roms/`, `mcr/` e `work/cards/` intocados.

**Arquivos criados/modificados:**

- `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md` — o limite inferior no
  lugar do "começam todas em", a tabela, e a nota da janela
- `docs/MCR-DESBLOQUEIOS.md` — `b >= 0x04e30` nas duas frases, a armadilha da
  janela curta, e a busca no bloco "Reproduzir"
