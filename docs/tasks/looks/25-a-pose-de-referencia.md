---
id: LOOKS-TASK-25
title: "A pose de referência — as matrizes de cada peça num quadro contado, e a hierarquia"
type: investigação
category: oráculo
phase: 9
depends_on: ["LOOKS-TASK-24"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (k)"
status: pendente
---

# LOOKS-TASK-25: A pose de referência

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (k) e §10.4 (2).
- **Esta captura é o gabarito da Fase 9.** O leitor do `ANIME.BIN`
  ([`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md)) se mede contra ela; sem ela, um leitor plausível passa.
- **Quadro contado, nunca "depois de uns segundos".** `load_state`, `pause`, e
  `frame_step` N vezes.
- **Ponto fixo é inteiro.** Gravada como inteiros 4.12, a comparação de depois
  é exata.
- **A hierarquia não se deduz da anatomia.** Se a matriz do antebraço é
  absoluta ou composta com a do braço, mede-se: a translação da filha varia com
  a rotação da mãe, ou não varia.

---

## Objetivo

Gravar, para um quadro N contado a partir do `load_state`, a matriz de rotação
e a translação que o jogo usa em **cada peça desenhada** — as onze da figura e a
cabeça —, e dizer qual peça é filha de qual.

---

## Critério de conclusão

- [ ] `oracle.py --pose <SLOT> <N>` grava em `work/looks-pose/` um JSON por
      quadro, com matriz e translação **inteiras** de cada peça, a peça nomeada
      pelo `pieces.py` e o N ao lado.
- [ ] **Repetível:** duas capturas do mesmo N idênticas número a número; e
      dois N diferentes, diferentes — sem isso a captura pode ler uma
      constante.
- [ ] A hierarquia medida, com a evidência.
- [ ] A convenção escrita: ordem de aplicação, escala 4.12, e o sinal de `y`
      contra o `UP = -1` do `scene.py`.
- [ ] Os dois slots.
- [ ] §10.3 (k) com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
