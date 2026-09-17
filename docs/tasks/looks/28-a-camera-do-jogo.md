---
id: LOOKS-TASK-28
title: "A câmera do jogo — projeção medida, e a silhueta como testemunha de forma"
type: implementação
category: oráculo
phase: 9
depends_on: ["LOOKS-TASK-27"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (m)"
status: pendente
---

# LOOKS-TASK-28: A câmera do jogo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (m), §10.4 (3) e §6 (h).
- **Sem a câmera do jogo, comparar desenho mede a câmera.**
- **Esta task fecha a §6 (h).** Figura montada na pose do jogo e mesma
  projeção: a silhueta passa a ser comparável, e forma ganha testemunha.
- **O controle já existe:** a captura do emulador se repete em zero pixel a
  partir do `load_state` (§5.3). O limiar sai do controle, escrito depois de
  medido e dito que foi.

---

## Objetivo

Medir a projeção e a câmera da tela `LOOKS SET`, aplicá-las no painel, e
comparar a silhueta do nosso quadro com a do emulador no mesmo quadro N.

---

## Critério de conclusão

- [ ] `H`, o deslocamento de tela e a matriz de câmera lidos do GTE por
      breakpoint, com o comando que os lê.
- [ ] O painel desenha com eles, no tamanho do painel do jogo.
- [ ] `confront.py --silhouette <SLOT> <N>`: máscara nos dois quadros e a
      diferença impressa.
- [ ] **Controles antes do teste:** emulador contra emulador no mesmo N dá
      zero; em N deslocado dá diferença; limiar escrito a partir dos dois.
- [ ] Três estilos de cabelo diferentes, dois slots: a silhueta concorda, e um
      estilo trocado de propósito discorda.
- [ ] §6 (h) e §10.3 (m) com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
