---
id: LOOKS-TASK-16
title: "`ui_check.py` — a UI julgada de fora, e o alvo `looks_ui`"
type: implementação
category: verificação
phase: 5
depends_on: ["LOOKS-TASK-15"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §4.4"
status: pendente
---

# LOOKS-TASK-16: Os contratos da UI

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §4.4 e
  §3.3.
- Molde pronto: o `tools/mcr/ui_check.py` julga a UI **de fora**, por contrato
  legível por máquina, e substitui os pontos que abririam modal.
- **A armadilha do ciclo do `.mcr` vale aqui inteira:** o `mcr_ui` passava com
  a janela sozinha quando faltava a fixture, e imprimia um `note:` que ninguém
  lia. Alvo que passa sem medir é pior do que alvo que pula.

---

- **A janela e os três comandos que o gate dirige já existem**, desde
  2026-09-16 ([`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md)):
  `ui/app.py --smoke`, `--looks <tupla> --screenshot <png>` e
  `--compare <png> <png>`, este último devolvendo quantos pixels diferem e em
  que porcentagem — é o que fecha o segundo critério abaixo sem escrever um
  comparador novo. O `--smoke` e o `--screenshot` **imprimem as contagens** do
  que desenharam (primitivas, texturizadas, superfícies, triângulos): um quadro
  em branco e um boneco escrevem PNG do mesmo tamanho, e só os números separam
  os dois antes de alguém olhar.
- **Medido no dia, para o gate ter piso:** `A-A1-A-A-A` contra `B-A1-A-A-A`
  difere em **47,13%** dos pixels e contra `A-A1-C-A-A` em **17,17%** — a
  cabeça sozinha, 640x640. Duas tuplas iguais dariam 0,00%.
- **Uma tupla pode ser RECUSADA, e isso não é falha da janela.** Três estilos de
  cabelo e os valores de barba acima de `E` saem como recusa da tabela de
  montagem, com a mensagem dela e **saída 2**. O gate tem de distinguir recusa
  de queda: `--smoke` e `--screenshot` saem 0, recusa sai 2, e falta de venv ou
  de imagem sai 77.
- **Peças cinza são esperadas**, e o gate não pode julgá-las como quadro
  errado: 237 das 593 primitivas da figura inteira amostram páginas que não
  estão no `DAT2D.BIN` — são o uniforme, que mora nos 105 `TEX_*.BIN`.

---

## Objetivo

`tools/looks/ui_check.py` mede o que a janela realmente fez, e pula quando não
pode medir.

---

## Critério de conclusão

- [ ] O gate roda `--smoke` e `--screenshot`, e **julga o PNG**: tamanho, e que
      ele não é quadro em branco.
- [ ] Duas tuplas visivelmente diferentes produzem **imagens diferentes** — é o
      que impede o gate de passar desenhando sempre o mesmo boneco.
- [ ] Sem venv ou sem display, **pula com 77** e a mensagem nomeia o que falta.
- [ ] **Não existe caminho em que o alvo passe sem ter medido.** Se faltar
      imagem, ele pula; não passa com `note:`.
- [ ] Achado o venv por busca para cima, como o `mcr/ui_check.py` faz.

---

## Log de Execução

*(preencher ao executar)*
