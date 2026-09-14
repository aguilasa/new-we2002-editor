---
id: LOOKS-TASK-17
title: "Confronto — nosso quadro contra o quadro do emulador, na mesma tupla"
type: verificação
category: oráculo
phase: 6
depends_on: ["LOOKS-TASK-16"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §5.3"
status: pendente
---

# LOOKS-TASK-17: O confronto com o gabarito vivo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §5.3 e
  §5.6.
- **A diferença não precisa ser zero, e não vai ser.** A §5.6 já diz por quê: a
  pose vem do `ANIME.BIN`, que está fora de escopo, e a câmera do jogo muda por
  campo. Nosso render é pose neutra e câmera livre.
- *Um número que ninguém olhou não é verificação.* A diferença tem de ser
  **medida, registrada e explicada**.

---

## Objetivo

Fechar o laço: mesma tupla dos dois lados, e um número que se possa acompanhar
ao longo do projeto.

---

## Critério de conclusão

- [ ] O ciclo roda: escolher a tupla na tela por `press_button`, capturar por
      `take_screenshot`, renderizar a mesma tupla, comparar.
- [ ] Ao menos **três tuplas** confrontadas, e não uma — uma só não distingue
      acerto de coincidência.
- [ ] A métrica é nomeada e justificada, e o número registrado por tupla.
- [ ] Cada fonte de diferença é **atribuída**: pose, câmera, resolução, filtro.
      O que sobrar sem explicação é achado, e vira CORR ou task.
- [ ] O confronto é **repetível**: a tupla, a rota e o comando ficam
      versionados, como os roteiros de `tools/par/` fazem para o golden.

---

## Log de Execução

*(preencher ao executar)*
