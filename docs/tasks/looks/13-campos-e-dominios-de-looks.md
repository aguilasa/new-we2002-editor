---
id: LOOKS-TASK-13
title: "`looks.py` — os doze campos, seus domínios e os rótulos"
type: implementação
category: núcleo
phase: 4
depends_on: ["LOOKS-TASK-09"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.9"
status: pendente
---

# LOOKS-TASK-13: Os campos e seus domínios

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.9.
- **Esta é a task barata do ciclo**, e é de propósito: o lado dos bits já tem
  **quatro implementações concordando** — `src/core/Player.cpp`,
  `src/app/Commands.cpp` (`kHair[32]`, `kSkin[4]`, `kLetters[8]`),
  `tools/mcr/domains.py` e o fonte `en_we2000edit` do Superpack.
- Não é engenharia reversa. É transcrição conferida.

---

- **Dois dos doze campos não entram no render, e isso está medido.** Em
  2026-09-15 a [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md)
  rodou `python tools/looks/oracle.py --fields NAT AGE HEIG` nos dois slots:
  **`NAT` e `AGE` não tocam um único byte** de `EDT_MOD.BIN`, de `MODEL.BIN` ou
  de qualquer TMD — o `AGE` move quatro bytes em toda a RAM. `HEIG` também não
  toca a geometria carregada, mas mexe na lista de display, ou seja **é escala
  na hora de desenhar**. Os três continuam sendo campos do registro e desta
  task; o que mudou é que se sabe quais têm efeito visual.
- **E os rótulos da tela, na ordem em que ela os mostra**, já estão no
  `oracle.ROWS`: `DEFAUL, NAT, SKIN, HAIR, H.COL, FACE, H.F.COL., HEIG, BODY,
  AGE, BOOTS, FOOT`. São **posições de linha**, postas ali para saber quantas
  vezes apertar `Down`; o domínio e o significado de cada um continuam sendo o
  assunto desta task, contra o `src/core/Player.cpp`.

---

- **Dois domínios ganharam testemunha independente**, em 2026-09-15
  ([`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md)): a tabela
  do tutorial do `zeta` enumera **8 tipos de cor de cabelo** (A a H) × **4
  raças** (*blanca, amarilla, canela, negra*), e os endereços que ela dá são os
  que a LOOKS-TASK-10 mediu no disco. Isso é uma **quinta** implementação
  concordando com `kSkin[4]` e `kLetters[8]` — e, ao contrário das outras
  quatro, esta não é código: é endereço de paleta.
- **`FACE` mexe em duas primitivas, não numa.** As primitivas 8 e 13 da seção 24
  do `MODEL.BIN`, passo `+0x10` no `v`, nos dois save states. É o par irmão do
  `HAIR` (primitivas 1 e 14, passo `+0x20`), e os quatro amostram a **mesma**
  imagem do `DAT2D.BIN`, a do offset 3.568.

---

- **Três domínios já estão medidos na tela, e um deles discorda do
  `Player.cpp`.** Andados de ponta a ponta em 2026-09-15 pela
  [`LOOKS-TASK-12`](/docs/tasks/looks/12-pele-paleta-ou-vertice.md), por
  `python tools/looks/oracle.py --palettes`, lendo o CLUT id na RAM depois de
  cada tecla:

  | campo | valores na tela | bits no `src/core/Player.cpp` |
  |---|---:|---:|
  | `SKIN` | **4** | 2 (`skin_colour`) |
  | `H.COL` | **8** | 3 (`hair_colour`) |
  | `H.F.COL.` | **7** | 3 (`beard_colour`) — oito |

  A terceira linha é o trabalho: **a tela oferece sete e o campo comporta
  oito.** A grade de paletas explica por que sete — as colunas de barba vão da
  9 à 15 e a décima sexta não existe —, mas o que o jogo faz com um
  `beard_colour` 7 gravado no registro do jogador **não foi medido**, e é
  pergunta desta task.
- **Campo desta tela trava nas pontas; não dá a volta.** O quarto `Right` no
  `SKIN` deixa o valor onde o terceiro o pôs. Domínio se mede andando até a
  ponta de baixo e depois até a de cima — contar ciclo aqui acusa falha que não
  houve.
- **`FACE` é a barba, não o rosto.** `FACE` e `H.F.COL.` movem **as mesmas duas
  primitivas** da seção 24 (8 e 13), que amostram a folha de cabelo do offset
  3.568 — e o `Player.cpp` tem `beard_style` e `beard_colour` lado a lado, nos
  bits que sobram ao lado de `hair_style` e `hair_colour`. O rótulo da tela e o
  nome do campo não são a mesma coisa, e aqui é o nome que está certo.

---

## Objetivo

`tools/looks/looks.py`: a tupla de aparência, com domínio e rótulo de cada
campo, e a conversão de e para os 12 bytes.

---

## Critério de conclusão

- [ ] Os doze campos da tela representados, com os domínios medidos: 4 peles,
      **32 cabelos** (`A1`…`P1`), 8 cores de cabelo, 7 barbas, 7 cores de
      barba, 8 corpos, 8 chuteiras, altura a partir de 148, idade a partir de
      15, e o pé.
- [ ] Decodificação dos 12 bytes **conferida campo a campo** contra
      `src/core/Player.cpp`, com o cross-check no `self_check()`.
- [ ] A tupla de texto do corpus (`A-I3-A-F-A`) é lida e escrita — é o formato
      dos 50 JPGs da LOOKS-TASK-18 e do `--looks` da UI.
- [ ] Os registros no disco (`/SELECT.BIN` offset **157.164**, 1.242 × 12 B)
      são conferidos: a contagem tem de fechar com o tamanho do arquivo. **É
      opinião de terceiro até esta task medir.**
- [ ] `self_check()` com caso vermelho.

---

## Log de Execução

*(preencher ao executar)*
