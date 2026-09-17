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
