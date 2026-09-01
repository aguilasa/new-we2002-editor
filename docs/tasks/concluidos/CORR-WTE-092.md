---
id: CORR-WTE-092
title: "Correção: dois handlers sem estímulo — o ramo do reserva e o arrasto de bola"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-092: os dois estímulos que o harness não sabia produzir

## Problema identificado

Dois `aberto` não esperavam código nem decisão: esperavam que **alguém os
disparasse**.

- **`MainForm.mostrar_jugadorClick`** atende dois botões e escolhe o par de
  listas pelo `Sender.Name`. O `golden-15-ficha` entra só pelo titular; o ramo
  do reserva não tinha régua. Despacho por nome erra em **silêncio**: com o ramo
  trocado a ficha abre com o jogador do lado errado, a tela fica plausível, e só
  a gravação denuncia.
- **`estrategia.bolaMouseDown`** começa o arrasto de uma bola no campinho, e o
  harness inteiro só sabia `clique`, `duplo`, `tecla` e `texto` — **nenhum
  `mousedown` em `wte/tools/*.sh`**. Clique não exercita handler que chama
  `BeginDrag`.

## Correção

### O verbo `arrasta`

`roteiro.sh` ganhou `! arrasta X0 Y0 X1 Y1` no único ponto de despacho:
`mousedown`, **três** passos intermediários com `--sync`, `mouseup`. Os passos
não são enfeite — um salto único não produz `OnMouseMove` nenhum em gtk2, e o
widget nunca vê o ponteiro em trânsito.

### `golden-20-ficha-reserva`

Entra pelo `mostrar_jugador_2` (492,402) e grava pelo `Comple.`. A ordem é
load-bearing: aquele botão e a `lista_jugadores_2` nascem desabilitados e só o
`lista_equipos_2Change` os habilita.

### `golden-21-arrasto`

Arrasta uma bola e aceita. Os 30 bytes de formação saem da posição dos
componentes, então bola que anda vira X e Y diferentes.

## Evidência — e as três vezes que um gate quase passou medindo nada

**Esta é a parte que vale guardar.** As duas réguas passaram *antes* de estarem
certas, e o que as pegou foi sempre a mesma pergunta: *comparado com uma corrida
sem estímulo, mudou alguma coisa?*

| Tentativa | O trace dizia | Os bytes diziam |
|---|---|---|
| arrasto na coordenada do `.lfm` | `campoMouseMove`, **nenhum** `bolaMouseDown` | idêntico a sem estímulo |
| arrasto para outra zona | `bolaMouseDown`, 3 `bolaMouseMove`, `bolaEndDrag` | **idêntico a sem estímulo** |
| arrasto dentro da zona 4 | idem | **2 bytes** — o X e o Y da bola, a dez de distância |

A segunda linha é a mais instrutiva: o handler **disparava**, o trace parecia
saudável, e o gate estava medindo zero. Soltar fora da zona da própria bola
devolve a bola ao lugar — é o que "zona" quer dizer, e é o retângulo que o
próprio `bolaMouseDown` mostra.

E a primeira tem causa própria: **a coordenada da bola não sai do `.lfm`.** Lá a
`bola7` está em (248,120) e mede 15×14; em execução as onze medem 10×10 e estão
onde a `PreencheTelaDeTatica` as pôs, conforme a formação do time. As
coordenadas do roteiro foram **medidas** nas capturas do
`compara_tela.sh --malha 2`, onde os dois lados dão as mesmas onze posições.

Para o ramo do reserva a mesma pergunta teve outra forma: os dois roteiros
gravam em **lugares diferentes**, o que prova que o ramo certo foi tomado.

| Corrida | `388567` | `388807` |
|---|---|---|
| ROM intocada | `0xba` | `0xb7` |
| titular (`golden-18`) | **`0x3f`** | `0xb7` |
| reserva (`golden-20`) | `0xba` | **`0x3f`** |

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/roteiro.sh` | modificar (verbo `arrasta`) |
| `wte/tests/roteiros/golden-2{0,1}-*.txt` e `.port.txt` | criar |
| `wte/tests/roteiros/README.md` | modificar (o dialeto) |
| `wte/tools/check_fase4.py` | modificar (`GOLDEN_DE`) |
| `wte/re/spec/MainForm.mostrar_jugadorClick.md`, `estrategia.bolaMouseDown.md` | modificar |

## Verificação

- [x] `make -C wte check` verde; `test_roteiro.py` verde com o verbo novo
- [x] `golden-20` e `golden-21`, **controle e golden** cada um: byte-idêntico
- [x] cada estímulo confrontado com uma corrida **sem estímulo** — o do arrasto
      muda 2 bytes, o do reserva escreve noutro registro
- [x] `roms/` intocada — cópias em `work/par/`

## Log de Execução

- **Executado em:** 2026-08-24

- **Resumo:** o placar da fase 4 foi de **89 para 91 de 96**. Sobram três, e um
  deles é da WTE-TASK-32.

  **A lição, e ela é geral:** um gate verde não prova que o estímulo aconteceu.
  Se os dois lados não fizerem nada, os dois concordam. Toda régua nova precisa
  de um terceiro ponto — a corrida **sem** o estímulo — e a pergunta é se ela
  difere. Isso custou duas corridas aqui e teria custado um veredito falso.

- **Problemas encontrados:** os três da tabela acima. A coluna `tentativas` do
  `fase-4-golden.tsv` registra **1** para os dois roteiros, e isso é deliberado:
  o que falhou duas vezes foi a *autoria* do roteiro, não o gate. O roteiro como
  está commitado passou de primeira nos dois modos; as tentativas descartadas
  eram outro estímulo, e ficam registradas aqui em vez de virarem número sobre a
  estabilidade do harness.
