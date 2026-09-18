---
id: LOOKS-TASK-32
title: "Incógnita (p) — o ciclo da caminhada: quadros por passada, interpolação e balanço"
type: investigação
category: oráculo
phase: 11
depends_on: ["LOOKS-TASK-26"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (p)"
status: pendente
---

# LOOKS-TASK-32: O ciclo da caminhada

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (p) e §10.4.
- **Nenhum número da gravação do usuário vale aqui.** Vídeo de tela tem a
  cadência do gravador; quem conta é o `frame_step`.
- **Animar num ritmo inventado produz caminhada bonita e errada.**
- **Duas perguntas que parecem uma:** quantos quadros o jogo leva para repetir
  a pose, e quantos quadros-chave o `ANIME.BIN` guarda. Se forem diferentes, o
  jogo interpola, e a regra se mede.
- **O tronco balança na gravação.** Raiz da animação ou câmera muda onde o
  balanço mora.

- **A interpolação já está medida pela metade, e é desta task fechar.** Em
  2026-09-18 a [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md)
  contou, sobre 16 capturas e 192 peças desenhadas: **96 trazem ângulos que o
  `ANIME.BIN` guarda inteiro por inteiro, e 96 trazem ângulos que quadro
  nenhum do arquivo guarda.** Metade dos quadros que o jogo mostra é
  construída.
  - **Não é a média dos vizinhos na lista:** testado contra o quadro anterior e
    o seguinte da mesma animação, `(a + b) >> 1`, **0 de 96**.
  - **O código que mistura é `0x80011F90`…**, e ele faz `lhu` de um ângulo,
    `lh` de outro a partir de um segundo ponteiro, soma e `sra 1` — uma média
    de dois, halfword a halfword. De onde vem o segundo ponteiro é o que falta.
  - Quem mede isso mede também o ritmo: `python tools/looks/anime.py
    --against-pose` imprime os três números a cada corrida, e
    `oracle.py --pose <SLOT> <N>` grava a captura com o ângulo e o quadro
    tocado **ao lado de cada peça**.

---

## Objetivo

Medir o ciclo da caminhada em quadros do jogo, e fazer o `anime.py` devolver a
pose de **qualquer** quadro do ciclo igual à do jogo.

---

## Critério de conclusão

- [ ] O período: a primeira volta de todas as matrizes ao quadro 0, contada
      por `frame_step`, nos dois slots — e o comando que conta.
- [ ] Quadros-chave contra quadros desenhados: iguais, ou a interpolação
      medida, com o arredondamento do ponto fixo.
- [ ] `anime.py --frame N` reproduz o jogo **exatamente** em pelo menos oito N
      espalhados pelo ciclo, fora os quadros-chave.
- [ ] O balanço atribuído: raiz da animação, ou câmera.
- [ ] Controle negativo: interpolar pelo quadro-chave vizinho errado fica
      vermelho.
- [ ] §10.3 (p) com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
