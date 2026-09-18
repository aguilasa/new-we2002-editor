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

- **O jogo MISTURA matrizes, e medir isso é desta task.** Medido em 2026-09-18
  pela [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md), sobre
  96 peças julgadas (de 192 capturadas — oito capturas não param no
  desempacotamento) nos dois slots:
  - **os ângulos vêm sempre do arquivo** — 96 de 96, inteiro por inteiro, no
    par que o jogo está lendo. Uma versão anterior desta linha dizia que
    metade dos quadros era construída, e aquilo era artefato da ponte errada
    (o quadro que o estado nomeia, que erra no goleiro);
  - **mas 6 das 96 matrizes não são a volta de par nenhum do arquivo** —
    varredura de todos os pares, `anime.no_pair_explains()`. O caminho que as
    produz é `0x80011F90`: ele **soma a matriz recém-construída com a que o
    jogo guardou e desloca um bit** (`sra 1`), meia-palavra a meia-palavra, e
    quem escolhe esse caminho é o byte em `0x0(s3)`;
  - as seis eram todas de **um passe só**, e as peças que vieram do quadro
    anterior da animação — o passe atravessou a troca de quadro. **De onde vem
    a segunda matriz da soma é o que falta**, e é o que decide o ritmo.
  - As ferramentas já entregam o que essa medição precisa:
    `oracle.py --pose <SLOT> <N>` grava, por peça, o ângulo e **o par que o
    jogo leu**; `anime.py --against-pose` separa exatas, misturadas e
    inexplicadas a cada corrida.

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
