---
id: LOOKS-TASK-27
title: "As peças no lugar — `scene.py` aplica a pose, e o painel da tela mostra o boneco montado"
type: implementação
category: render
phase: 9
depends_on: ["LOOKS-TASK-22", "LOOKS-TASK-26"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.4"
status: pendente
---

# LOOKS-TASK-27: O boneco montado

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1, §10.4 e §6 (e).
- **É o primeiro pedido do usuário:** o jogador **montado**, no painel da tela
  `LOOKS SET` da [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md), não em prateleira.
- **A regra 3 continua:** a pose sai do núcleo (`anime.py` → `scene.py`); a
  `ui/` só desenha.
- **A prateleira não some.** É o jeito de olhar uma peça isolada, e o `S` a
  alterna; o que muda é o default.
- **O que a [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md)
  mediu em 2026-09-18 e esta task tem de honrar:**
  - **a transformação por peça é absoluta** — a câmera composta com a volta da
    peça —, então montar não é compor hierarquia: é aplicar doze
    transformações prontas. O esqueleto do jogo **não é rígido** (cinco juntas
    se separam, o resto não), e supor uma cadeia anatômica é inventar;
  - **a tela desenha DUAS chuteiras e só UMA carrega matriz.** As seções 9 e 10
    são lidas as duas (watchpoint de leitura, uma corrida por seção, 2 e 2, com
    seção desenhada de controle), e a passada tem uma carga só para a 9. A
    segunda chuteira é desenhada **reaproveitando a rotação que já está no
    GTE**. Uma montagem que espere uma matriz por peça desenhada deixa um pé
    para trás ou o põe no lugar errado — **medir onde a segunda chuteira cai é
    desta task**, e a captura da 25 não a nomeia;
  - **`y` cresce para baixo** (cabeça em `y = −8`, pé mais baixo em `y = 60`),
    de acordo com o `UP = -1` que o `scene.py` já usa, e **nenhuma matriz tem
    determinante negativo** — o espelho das peças `b` está na geometria.

---

## Objetivo

O `scene.py` monta a figura aplicando a pose do quadro pedido a cada peça, e o
painel da tela `LOOKS SET` abre com o boneco montado.

---

## Critério de conclusão

- [ ] `scene.from_image(..., frame=N)` devolve os pontos transformados pela
      pose do quadro N; `scene.shelf` continua disponível.
- [ ] `ui/app.py --frame N`; sem ele, o quadro de referência da [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md).
- [ ] **Conferido contra o jogo, peça a peça:** a ordem relativa dos centros
      (cabeça sobre o tronco, pés sob as pernas, braços dos dois lados) como
      asserção do `scene.py --check-image`, não olho.
- [ ] Captura olhada no Log, nos dois slots.
- [ ] `ui_check.py` julga a figura montada e continua reprovando quadro em
      branco e tupla que não chega ao desenho.
- [ ] Controle negativo: a hierarquia invertida fica vermelha.

---

## Log de Execução

*(preencher ao executar)*
