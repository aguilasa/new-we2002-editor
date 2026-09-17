---
id: LOOKS-TASK-22
title: "A tela `LOOKS SET` na janela — doze linhas trocáveis, e o boneco redesenhado a cada troca"
type: implementação
category: ui
phase: 8
depends_on: ["LOOKS-TASK-21"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.4"
status: pendente
---

# LOOKS-TASK-22: A tela `LOOKS SET` na janela

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1 e §10.4 (1).
- **É o pedido do usuário, e roda sobre a v1 como ela está.** As linhas de cor,
  cabelo, barba e chuteira já andam no `assembly.py`; o boneco ainda sai em
  prateleira até a [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) o montar dentro do mesmo painel.
- **A tabela vem da [`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md).** A janela não conhece texto de valor nenhum que o
  `screen.py` não tenha.
- **A regra 3 continua:** a `ui/` não conhece endereço nem lê disco; troca de
  valor vira tupla, e a tupla vai ao `scene.py`.
- **Recusa é visível, nunca silenciosa.** `HAIR H1` não foi medido e o
  `assembly` recusa: a janela diz isso na caixa de ajuda e **não** desenha a
  cabeça de outro estilo no lugar — é a falha que o projeto existe para não
  cometer (§0, item 3).
- **Nenhuma janela aparece nos gates** (−32000 no Windows, `:98` no Linux); só
  o `.\make.ps1 looks` abre visível.

---

## Objetivo

O `ui/app.py` abre a tela `LOOKS SET`: as doze linhas com o texto do jogo, o
cursor, a caixa de ajuda, a placa de posição, e o boneco no painel redesenhado a
cada valor trocado — começando dos valores do slot 1 ou do slot 2.

---

## Critério de conclusão

- [ ] `tools/looks/ui/looks_set.py` com o arranjo medido na [`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md); o
      `ui/app.py` o abre por default, e `--state 1` / `--state 2` carregam os
      valores iniciais, a figura e a placa de cada slot.
- [ ] Setas: ↑/↓ movem o cursor, ←/→ trocam o valor, com o travamento e a
      volta que a [`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md) mediu; o boneco se redesenha a cada troca.
- [ ] Recusa: o valor que o `assembly` recusa aparece na tela e na ajuda, e o
      painel não desenha nada no lugar.
- [ ] **O gate julga por tecla:** o `ui_check.py` dirige a janela fora da tela
      com teclas sintéticas do Qt, anda cada linha até as duas pontas, e exige
      que o texto mostrado seja o do `screen.py`, que a tupla enviada ao
      `scene.py` mude e que a ponta trave.
- [ ] **Tecla contra tecla com o jogo** (§10.4 (1)): uma sequência de teclas a
      partir do `load_state` nos dois lados, e o texto das doze linhas igual —
      com o controle da mesma sequência duas vezes no jogo.
- [ ] Captura da nossa janela ao lado da captura do emulador, olhadas, no Log.
- [ ] `.\make.ps1 looks` abre a tela; `-State 1|2` escolhe o slot, e o `help`
      diz os controles.

---

## Log de Execução

*(preencher ao executar)*
