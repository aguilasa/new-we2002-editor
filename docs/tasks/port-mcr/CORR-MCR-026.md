---
id: CORR-MCR-026
title: "Correção: a regra da soma é creditada a sete cartões independentes e dois de terceiros, e a medição dá seis padrões distintos e um de terceiro"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-MCR-026: sete cartões independentes, dos quais três são o mesmo arquivo

## Problema identificado

O peso probatório da regra da soma — a única coisa que torna a task seguinte
(marcar e desmarcar os desbloqueios) exequível — está declarado em duas
frases, e as duas contam amostra repetida como amostra nova:

- [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md):57 — "`k = 0x8a` em
  **sete** cartões independentes, dois deles de terceiros."
- [`/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md`](/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md):167
  e :318 — "sete cartões independentes (os quatro acima, os dois `first-boot`
  e o `29939`, de terceiro)" / "sete cartões independentes, dois deles de
  terceiros".

Duas coisas não batem, e a segunda o próprio arquivo já derruba quatro linhas
acima (:163, "`a1`, `a2` e o `we2002-ptbr-first-boot.mcr` são o mesmo md5"):

1. **`a1` e `a2` não são cartões independentes** — são byte a byte o
   `we2002-ptbr-first-boot.mcr`. Contá-los infla sete onde há **seis padrões
   distintos**. E "os quatro acima" nomeia **cinco** rótulos (`a1`, `a2`,
   `b-nome`, `c-opcao`, `c-opcao2`).
2. **Só um cartão é de terceiro**, o `29939`. O
   [`mcr/README.md`](../../../mcr/README.md):184 diz do outro candidato, em
   letra: o `we2002-english-first-boot.mcr` "não veio de pacote de terceiro nem
   de editor".

A mesma contagem por arquivo aparece em :186 para o campo de alta entropia —
"zero nos **três** cartões de primeira execução" —, e cartões de primeira
execução são **dois**: o inglês e o PT-BR. O terceiro seria `a1`, que é o
segundo.

## Evidência

A regra vale — não é isso que está em questão. Oito arquivos medidos, todos
`k = 0x8a`, e três deles o mesmo cartão:

```
english   k=0x8a byte=0xd9   md5 72626c3b
ptbr      k=0x8a byte=0x8f   md5 e2de493f
29939     k=0x8a byte=0x84   md5 3fb86323   <- o unico de terceiro
a1        k=0x8a byte=0x8f   md5 e2de493f   <- = ptbr
a2        k=0x8a byte=0x8f   md5 e2de493f   <- = ptbr
b-nome    k=0x8a byte=0x8f   md5 560cfe8a
c-opcao   k=0x8a byte=0xad   md5 0f927635
c-opcao2  k=0x8a byte=0xac   md5 aea74ef6
```

`work/cards/ptbr-original.mcr` (= `ptbr`) e `work/cards/ptbr-antes-do-v2.mcr`
(= `c-opcao2`) são mais duas cópias, e não entram na conta por isso.

O campo de alta entropia, nos três cartões que a frase cita:

```
0x02035..43 english  000000000000000000000000000000  zero
0x02035..43 ptbr     000000000000000000000000000000  zero
0x02035..43 29939    fe67ff0b4051787f7f7f009efe66ff  NAO zero
```

O `29939` **não** é de primeira execução — o próprio arquivo o lista, quatro
linhas abaixo, entre as gravações que preencheram o campo.

E os outros dois cartões de terceiro com `BISLPM-87056WEW` não corroboram nada:
são saves `D2A` e `D0A`, não `OPT`, e a regra não vale neles (`k=0xff` e
`k=0xec`). Vale registrar o vizinho que apareceu na mesma varredura: os quatro
`BESLES-039xxPES-OPT` de PES2 dão **`k = 0x89`**, o que reforça a forma da
regra em outra release.

## Causa raiz

A série de amostras foi contada por arquivo em `work/cards/`, e três dos
arquivos são o mesmo cartão — o que a própria task mediu ao provar que a
gravação é determinística.

## Correção

### Arquivo: `docs/MCR-DESBLOQUEIOS.md`

Linha 57: **seis cartões distintos, um deles de terceiro**, dizendo que oito
arquivos foram medidos e três deles são o mesmo cartão — a determinismo da
gravação é o motivo, e é resultado, não perda. Se valer citar o reforço, os
quatro `PES-OPT` de PES2 com `k = 0x89`.

Linha 69: **dois** cartões de primeira execução, e que o `29939` entra ali
apenas como o caso que mostra o campo preenchido.

### Arquivo: `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md`

As mesmas duas contagens, em :167, :174, :186 e :318, mais o "os quatro acima"
que nomeia cinco rótulos.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/MCR-DESBLOQUEIOS.md` | modificar |
| `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md` | modificar |

## Verificação

- [x] `md5sum mcr/we2002-*.mcr work/cards/*.mcr` e a contagem do doc dizem o
      mesmo número de padrões distintos
- [x] `grep -n "sete\|três cartões de primeira" docs/MCR-DESBLOQUEIOS.md
      docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md` não sobra afirmação
      contada por arquivo
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-10

**Resumo do que foi feito:**

As duas contagens passaram a ser por **padrão distinto**, e não por arquivo.
`k = 0x8a` vale em **seis cartões distintos**, um deles de terceiro — o
`29939`; oito arquivos foram medidos, e três deles são o mesmo cartão porque a
gravação é determinística, que é resultado desta task e não amostra perdida. As
duas cópias de `work/cards/` (`ptbr-original`, `ptbr-antes-do-v2`) ficaram
nomeadas como cópias.

O campo de alta entropia é zero nos **dois** cartões de primeira execução — o
inglês e o PT-BR —, e o `29939` entra ali como o caso oposto, de campo
preenchido. No mapa, "os quatro acima" que nomeava cinco rótulos virou "cinco
arquivos novos, três padrões distintos".

**Medido de brinde, e escrito:** a forma da regra reaparece em outra release —
os `BESLES-039xxPES-OPT` de PES2 em `mcr/` dão `k = 0x89` na mesma faixa. São
**cinco** arquivos, não quatro como a evidência desta CORR dizia: `17738`,
`18432`, `22507`, `29818` e `7110`, com cinco md5 distintos. O número escrito
no doc é o medido.

**Problemas encontrados:**

Nenhum. A regra não estava em questão e continua valendo; o que estava errado
era só o peso probatório declarado.

Uma armadilha de reprodução vale registrar: a soma **exclui** o próprio byte de
soma, e medir sem excluí-lo dá `k` variando de cartão para cartão (`0x4f`,
`0x05`, `0x23`…) — o que parece derrubar a regra. O bloco "Reproduzir" do mapa
já faz certo, zerando `d[C]` antes de somar.

**Medições:**

| medida | número |
|---|---|
| arquivos medidos com save `BISLPM-87056WEW-OPT` | **8** (mais 2 cópias em `work/cards/`) |
| padrões distintos (md5) | **6** |
| de terceiro | **1** (`pro-evolution-soccer-2.29939.gme`) |
| `k` nos seis | `0x8a` em todos |
| campo `0x02035..43` zerado | **2** cartões (inglês, PT-BR) — mais `a1`/`a2`/`ptbr-original`, que são o PT-BR |
| `BESLES-039xxPES-OPT` de PES2 | **5** arquivos, `k = 0x89` |
| `roms/`, `mcr/`, `work/cards/` | intocados (leitura pura) |

**Arquivos criados/modificados:**

- `docs/MCR-DESBLOQUEIOS.md` — as duas contagens, e o reforço do `k = 0x89`
- `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md` — as mesmas contagens em
  :157, :167, :174, :186 e :318
