---
id: CORR-MCR-027
title: "Correção: \"as faixas válidas começam todas em 0x02044\" é falso como escrito, e o que se mediu é outra coisa"
type: correção
category: engenharia-reversa
status: pendente
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

- [ ] a busca reproduzida sobre os seis cartões distintos dá os números que o
      doc afirma (faixas, início mínimo, fim mínimo)
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
