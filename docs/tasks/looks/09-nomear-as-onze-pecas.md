---
id: LOOKS-TASK-09
title: "Incógnita (b) — nomear as onze peças pelo emulador, não pelo tamanho"
type: engenharia-reversa
category: formato
phase: 2
depends_on: ["LOOKS-TASK-08"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §6"
status: pendente
---

# LOOKS-TASK-09: Qual peça é qual

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §6,
  incógnita (b), e §1.5.
- Onze peças: cinco duplas de contagem idêntica mais uma sozinha. **Nomeá-las
  pelo tamanho é palpite.**
- A tela ajuda de graça: ela **fecha a câmera no rosto** em `SKIN` e `HAIR`, e
  **abre o corpo** em `BODY`. Isso já separa cabeça de tronco sem medir nada.
- **Comece por `load_state`.** Os dois states de 2026-09-14 põem o jogo na tela
  de edição: **slot 1 goleiro, slot 2 jogador de linha**, os dois no disco
  inglês. Recarregar entre medições dá baseline byte a byte idêntico, e é o que
  faz o diff medir só o que você mudou.
- **A RAM se lê por MCP vivo.** O `savestate.py` não alcança a RAM nesta
  máquina: sem CLI `zstd` e sem o módulo `zstandard`, ele lê cabeçalho e para.
- **O slot 1 é goleiro e o slot 2 é jogador de linha.** Goleiro tem luva e
  manga comprida; a diferença entre os dois já aponta quais peças são de
  uniforme.

---

- **As duas listas do `EDT_MOD.BIN` já têm dono, e isso poda metade do
  trabalho.** Medido em 2026-09-14 pela
  [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) com
  `python tools/looks/oracle.py --fields SKIN`: trocar `SKIN` no **slot 1
  (goleiro)** reescreve as seções 11, 16, 17, 18 e 19, que são as da **lista
  1**; no **slot 2 (jogador de linha)**, as seções 0, 3, 4, 5, 6, 7 e 8, que
  são as da **lista 0**. Interseção vazia. **Lista 0 é o jogador de linha,
  lista 1 é o goleiro** — e as peças que cada uma nomeia já estão separadas por
  boneco antes de esta task começar.
- **A `MODEL.BIN` seção 24 é a cabeça, e é compartilhada.** `HAIR`, `FACE` e
  `SKIN` escrevem os três nela, e só nela dentro do `MODEL.BIN`. É a primeira
  peça que esta task pode nomear sem trocar nada.
- **Sobram duas faixas de buffer por nomear.** Cada campo move de 130 a 320
  bytes que caem **fora** dos dois arquivos de modelo, e eles se concentram em
  `0x80153000+` e `0x80162000+` — a `0xF000` uma da outra, e **não** cópias uma
  da outra (15,3% de bytes iguais). Nomeá-las é o que separa "a geometria
  carregada" de "a geometria que a GPU desenhou", e é trabalho desta task.

---

## Objetivo

Cada uma das onze peças com nome medido, e o critério que sustentou o nome.

---

## Critério de conclusão

- [ ] Cada peça tem nome — cabeça, cabelo, tronco, braço, antebraço, coxa,
      perna, pé, ou o que a medição mostrar —, e ao lado **como se soube**.
- [ ] Cada medição parte de `load_state`, e **é repetida** a partir dele: o
      mesmo gesto duas vezes tem de dar o mesmo diff.
- [ ] As onze peças são levantadas nos **dois slots**, e a diferença entre
      goleiro e jogador de linha fica registrada — é o que separa peça de
      uniforme de peça de corpo.
- [ ] O método é trocar a opção no jogo e ver o que muda, não deduzir do
      número de vértices.
- [ ] Fica medido se **`HAIR` troca a peça** (malha nova) ou só a paleta. A
      tela sugere malha — `A1` → `B3` mudou o cabelo de curto para comprido —,
      mas sugestão não é medição.
- [ ] Fica medido o que `NAT` e `AGE` fazem, se é que fazem alguma coisa
      (§5.6, item 3).
- [ ] Fica medido o que `HEIG` e `BODY` fazem: escala, peça diferente, ou as
      duas coisas.
- [ ] A dupla de contagem idêntica é confirmada como **espelho esquerda/direita**,
      ou desmentida.

---

## Log de Execução

*(preencher ao executar)*
