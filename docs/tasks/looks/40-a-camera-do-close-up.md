---
id: LOOKS-TASK-40
title: "A câmera do close-up — o painel aproxima na cabeça quando a linha é de cabeça"
type: implementação
category: render
phase: 10
depends_on: ["LOOKS-TASK-28"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (o)"
status: pendente
---

# LOOKS-TASK-40: A câmera do close-up

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (o) e a §10 sobre a câmera.
- **Saiu da [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md)**, dividida em 2026-09-21 a pedido do usuário; o
  pedido vinha da [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md).
- **Medido pela [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md):** com o cursor numa linha de cabeça
  (`HAIR`, por exemplo) o jogo aproxima a câmera na cabeça e gira o boneco,
  um ângulo por captura que a carga de câmera do GTE **não** traz — a câmera
  que vale ali se deriva das próprias peças (`oracle.camera_from_pieces`), e
  o `oracle.py --camera SLOT LINHA` a mede.
- **A janela desenha sempre a câmera de corpo inteiro**, medida com o cursor
  em `NAT`.
- **Antes da [`LOOKS-TASK-33`](/docs/tasks/looks/33-a-janela-animada.md)**: as duas mexem na câmera do painel, e a
  janela animada precisa saber qual câmera vale em cada linha.

---

## Objetivo

O painel troca para a câmera do close-up quando o cursor está numa linha de
cabeça, e volta à de corpo inteiro nas outras, como o jogo.

---

## Critério de conclusão

- [ ] Quais linhas aproximam, medido no jogo nos dois slots, e a câmera de
      cada uma escrita em `work/looks-camera/`.
- [ ] A janela troca de câmera ao mover o cursor, e a troca é por linha, não
      por palpite.
- [ ] `confront.py --silhouette` no close-up de cada linha que aproxima, nos
      dois slots, dentro do limiar da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md), com o controle do
      jogo contra si mesmo.
- [ ] Um controle plantado (a janela que não troca de câmera) fica vermelho.

---

## Log de Execução

*(preencher ao executar)*
