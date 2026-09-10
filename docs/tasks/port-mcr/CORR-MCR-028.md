---
id: CORR-MCR-028
title: "Correção: o mapa diz que três imagens de roms/ declaram SLPM-87056, e são cinco"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-MCR-028: são cinco as imagens que declaram `SLPM-87056`

## Problema identificado

[`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md):3 abre dizendo que a
medição é

> sobre a release japonesa `SLPM-87056` (as três imagens de `roms/` declaram
> esse código)

São **cinco** arquivos em `roms/` que declaram o código, e a lista importa
porque é ela que diz sobre qual imagem um resultado vale: a European Deluxe —
que os golden tests do `newWe2002` usam como imagem canônica — é uma delas, e
não é intuitivo.

## Evidência

```
roms/golden-european-deluxe.bin            SLPM_870.56
roms/japanese-shift-jis.bin                SLPM_870.56
roms/we2002-pt-br.bin                      SLPM_870.56
roms/ptbr-remaster.bin                     SLPM_870.56
roms/we2002-english/we2002-english.bin     SLPM_870.56
```

(`head -c 400000 <img> | strings -n 8 | grep -oE 'SLPM_?[0-9._]{5,}'`, leitura
pura.)

## Causa raiz

A frase contou as imagens que a task usou — a inglesa e as duas PT-BR — como se
fossem todas as que carregam o código.

## Correção

### Arquivo: `docs/MCR-DESBLOQUEIOS.md`

Dizer **cinco**, ou — melhor — nomear as duas que a medição usou
(`we2002-english/we2002-english.bin` e `we2002-pt-br.bin`) e deixar o código
como o que elas declaram, sem afirmar quantas mais o declaram.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/MCR-DESBLOQUEIOS.md` | modificar |

## Verificação

- [x] a varredura de `SLPM_870.56` sobre `roms/` e a frase do doc dizem o mesmo
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-10

**Resumo do que foi feito:**

A abertura do mapa passou a **nomear as duas imagens que a medição usou** —
`roms/we2002-english/we2002-english.bin` e `roms/we2002-pt-br.bin` —, que é a
informação que faltava: é ela que diz sobre qual disco um resultado vale. O
número total ficou como parêntese, cinco, com a European Deluxe dos golden
tests do `newWe2002` nomeada, porque não é intuitivo que ela declare o código
japonês.

**A varredura puxou a mesma contagem em outros dois lugares**, os dois deste
ciclo e os dois com o mesmo `cdrom:SLPM_870.56`: a §5.6 do
[`PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) e o veredito do console na
[MCR-TASK-13](/docs/tasks/port-mcr/13-oraculo-e-veredito.md). Ali o ponto da
frase não é a lista, é o **código de produto diferente** do da fixture
(`BISLPM-86600WEW-OPT`), então só o número mudou — para cinco, medido junto
com a segunda string.

**Problemas encontrados:**

Nenhum. Vale registrar o que a segunda medição acrescentou: as cinco imagens
não só declaram o mesmo código, como **escrevem o mesmo nome de save** — três
ocorrências de `BISLPM-87056WEW-OPT` em cada uma —, o que sustenta a frase da
MCR-TASK-13 melhor do que a contagem sustentava.

Uma armadilha de shell: `find roms -name '*.bin'` num laço sem `-print0` se
parte nos nomes com espaço das releases de PES2, e o laço vira uma cascata de
`head: cannot open 'Pro'`. A varredura foi refeita com `-print0`.

**Medições:**

| medida | número |
|---|---|
| `.bin` em `roms/` que declaram `SLPM_870.56` | **5** |
| dos quais a medição usou | **2** (`we2002-english`, `we2002-pt-br`) |
| ocorrências de `BISLPM-87056WEW-OPT` em cada uma das cinco | **3** |
| `cdrom:SLPM_870.56` em cada uma das cinco | **1** |
| `roms/` | intocada (leitura pura, `head -c` + `strings`) |

**Arquivos criados/modificados:**

- `docs/MCR-DESBLOQUEIOS.md` — a abertura nomeia as duas imagens usadas
- `docs/PLAN-MCR-PY.md` — cinco na §5.6 (discrepância que a varredura revelou)
- `docs/tasks/port-mcr/13-oraculo-e-veredito.md` — cinco no veredito do console
