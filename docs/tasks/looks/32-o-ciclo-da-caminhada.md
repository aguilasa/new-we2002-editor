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

- **A interpolação NÃO está medida, e o que esta linha dizia era artefato.**
  Em 2026-09-18 a [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md)
  escreveu aqui que *"96 de 192 peças trazem ângulos que o `ANIME.BIN` não
  guarda"*, e portanto que metade dos quadros era construída. **Remedido no
  mesmo dia:** com a ponte certa — `s0` na instrução `0x80011D48`, o ponteiro
  que o jogo está lendo, e não o quadro que o estado nomeia — são **96 de 96**
  que vêm do arquivo, inteiro por inteiro. Nada aqui diz que o jogo interpola.
- **O que continua valendo como pista:** o código em `0x80011F90` soma dois
  valores halfword a halfword e desloca um bit (`sra 1`) sobre a matriz recém
  construída, e o dispatch em `0x80011DA0` tem **dez** variantes de
  desempacotamento, algumas das quais andam o ponteiro do par de ±8 e ±16.
  Quem medir o ritmo mede também isso; e a pergunta "o jogo interpola?" se
  responde contando quadros com `frame_step`, não por ângulo que não achou par.

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
