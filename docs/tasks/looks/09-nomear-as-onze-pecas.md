---
id: LOOKS-TASK-09
title: "Incógnita (b) — nomear as onze peças pelo emulador, não pelo tamanho"
type: engenharia-reversa
category: formato
phase: 2
depends_on: ["LOOKS-TASK-08"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §6"
status: pendente
---

# LOOKS-TASK-09: Qual peça é qual

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §6,
  incógnita (b), e §1.5.
- Onze peças: cinco duplas de contagem idêntica mais uma sozinha. **Nomeá-las
  pelo tamanho é palpite.**
- A tela ajuda de graça: ela **fecha a câmera no rosto** em `SKIN` e `HAIR`, e
  **abre o corpo** em `BODY`. Isso já separa cabeça de tronco sem medir nada.

---

## Objetivo

Cada uma das onze peças com nome medido, e o critério que sustentou o nome.

---

## Critério de conclusão

- [ ] Cada peça tem nome — cabeça, cabelo, tronco, braço, antebraço, coxa,
      perna, pé, ou o que a medição mostrar —, e ao lado **como se soube**.
- [ ] O método é trocar a opção no jogo e ver o que muda, não deduzir do
      número de vértices.
- [ ] Fica medido se **`HAIR` troca a peça** (malha nova) ou só a paleta. A
      tela sugere malha — `A1` → `B3` mudou o cabelo de curto para comprido —,
      mas sugestão não é medição.
- [ ] Fica medido o que `NAT` e `AGE` fazem, se é que fazem alguma coisa
      (§5.6, item 3).
- [ ] Fica medido o que `HEIG` e `BODY` fazem: escala, peça diferente, ou as
      duas coisas.
- [ ] A dupla de contagem idêntica é confirmada como **espelho esquerda/direita**,
      ou desmentida.

---

## Log de Execução

*(preencher ao executar)*
