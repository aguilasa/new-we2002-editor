---
id: LOOKS-TASK-24
title: "Incógnita (j) — de onde vem a pose: `ANIME.BIN`, código ou outra tabela"
type: investigação
category: oráculo
phase: 9
depends_on: ["LOOKS-TASK-20"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (j)"
status: pendente
---

# LOOKS-TASK-24: De onde vem a pose

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.2 e §10.3 (j), e §6 (e).
- **É a task de maior risco da v2, e abre a Fase 9 pelo mesmo motivo que a
  [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) veio antes da Fase 3:** um leitor de formato escrito para o arquivo
  errado lê perfeitamente e desenha outra coisa. Que a caminhada sai do
  `ANIME.BIN` é hipótese **pelo nome do arquivo**, e nada mais.
- **O `ANIME.BIN` é cru** — 396.804 B, form1, sem LZSS, cabeçalho de 204
  palavras de ponteiro KSEG0 (§10.2) —, então, se estiver em RAM, está byte a
  byte, como os dois arquivos de modelo estavam (§1.3).
- **Onde a matriz entra.** Na PSX a pose de uma peça chega ao GTE como matriz
  de rotação 3×3 em ponto fixo 4.12 e um vetor de translação, carregados antes
  de os vértices daquela peça serem transformados. Um breakpoint nessa carga,
  com a peça identificada pela primitiva que vem a seguir, diz **de onde os
  números saíram** — a técnica do `layout.HAIR_QUAD_STORE` da [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md), um nível
  acima.
- **Toda medição começa em `load_state`**, nos dois slots. O boneco anima:
  diff de memória sem baseline mede a animação inteira.

---

## Objetivo

Dizer, com evidência, **de onde vêm as matrizes que posicionam cada peça** na
tela `LOOKS SET`, e se o `ANIME.BIN` está entre as fontes — antes de qualquer
leitor de pose existir.

---

## Critério de conclusão

- [ ] O `ANIME.BIN` está ou não em RAM nessa tela, **por conteúdo**: o
      arquivo inteiro contra a memória no endereço que o cabeçalho deriva
      (`layout.derive_base()`), com a base no `layout.py` e o digest japonês na
      guarda dos dois discos.
- [ ] Onde o GTE recebe a matriz de cada peça: o endereço da instrução, por
      breakpoint de execução, e **quais peças** passam por ela num quadro.
- [ ] **De onde os nove números e a translação saem** — breakpoint de leitura
      sobre a faixa do `ANIME.BIN`, ou o registrador seguido até a origem. O
      veredito distingue "medi e é isto" de "não achei o contrário".
- [ ] Nos dois slots, e o que diferir entre goleiro e jogador de linha dito.
- [ ] O comando que reproduz no `oracle.py`, com 77 sem as variáveis e os
      states, na tabela de gates do perfil.
- [ ] §10.3 (j) do plano com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
