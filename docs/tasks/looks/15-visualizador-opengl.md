---
id: LOOKS-TASK-15
title: "`ui/viewer.py` e `ui/app.py` — `QOpenGLWidget`, câmera orbital e uma tupla na tela"
type: implementação
category: ui
phase: 5
depends_on: ["LOOKS-TASK-14"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §3.2"
status: pendente
---

# LOOKS-TASK-15: O visualizador

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §3.2, §3.3
  (regra 3) e §4.3.
- **`QOpenGLWidget`, não Qt3D nem rasterizador em Python.** O Qt3D é módulo
  grande e meio abandonado no Qt6 (§4b do
  [PLAN-STADIUMS.md](/docs/PLAN-STADIUMS.md)); rasterizar em Python puro é
  inviável sem `numpy`, que **não está instalado** e cuja instalação é decisão
  do dono da máquina.
- A UI **não conhece endereço** e o núcleo **não conhece Qt**.

---

## Objetivo

Uma janela que desenha o boneco de uma tupla de LOOKS, e que se deixa dirigir
de fora.

---

## Critério de conclusão

- [ ] `ui/viewer.py` desenha as peças com `QOpenGLWidget`, câmera orbital, e os
      modos sólido e wireframe.
- [ ] A cor chega pelo caminho que a LOOKS-TASK-12 decidiu.
- [ ] `ui/app.py --looks A-I3-A-F-A` monta e desenha aquela tupla.
- [ ] `--smoke` abre a janela, pinta um quadro e sai com 0.
- [ ] `--screenshot out.png` grava a imagem **fora da tela** — `:98` no Linux,
      janela em −32000 no Windows (§4.3). Nenhuma janela aparece para o
      usuário.
- [ ] Varredura: nenhum `import layout` em `ui/`; e depois de importar o núcleo
      inteiro, `PySide6` não está em `sys.modules`.

---

## Log de Execução

*(preencher ao executar)*
