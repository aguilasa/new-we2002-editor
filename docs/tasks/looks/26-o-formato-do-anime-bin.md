---
id: LOOKS-TASK-26
title: "`anime.py` — o formato do `ANIME.BIN`, medido contra a pose capturada"
type: implementação
category: formato
phase: 9
depends_on: ["LOOKS-TASK-25"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (l)"
status: pendente
---

# LOOKS-TASK-26: O formato do `ANIME.BIN`

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (l), e o rito da Fase 1 (§1.4).
- **Só começa se a [`LOOKS-TASK-24`](/docs/tasks/looks/24-de-onde-vem-a-pose.md) disse que a pose vem do `ANIME.BIN`.** Se disse outra
  coisa, esta task muda de arquivo e de título, e isso se registra aqui antes.
- **O gabarito é a [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md).** Matriz de determinante 1 e boneco em pé é
  plausível, não certo.
- **As regras da Fase 1 valem inteiras:** endereço só no `layout.py`; contagem
  com o offset de partida; varredura que não chega ao EOF é errada; módulo novo
  com `self_check()` e caso vermelho.

---

## Objetivo

Um `tools/looks/anime.py` que lê o `ANIME.BIN` do disco japonês, diz o que cada
entrada do cabeçalho nomeia, e devolve, para a animação da tela e um quadro,
**as mesmas matrizes que o jogo carregou**.

---

## Critério de conclusão

- [ ] `anime.py` com `self_check()` sem imagem, e `--check-image` que pula
      com 77 e está na lista do `cli.py check` (o self-check dele falha se não
      estiver).
- [ ] O cabeçalho lido e a estrutura varrida **até o EOF exato**, com o offset
      de partida ao lado de cada contagem.
- [ ] Qual entrada é a caminhada da tela, medido — não escolhido pelo tamanho.
- [ ] **As matrizes do quadro N da [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md) reproduzidas exatamente**, nas onze
      peças e na cabeça, nos dois slots.
- [ ] Dois controles negativos — ordem de campo e escala —, vermelhos pela
      própria causa.
- [ ] §10.3 (l) com o formato medido.

---

## Log de Execução

*(preencher ao executar)*
