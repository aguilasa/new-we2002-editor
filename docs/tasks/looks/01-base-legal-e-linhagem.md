---
id: LOOKS-TASK-01
title: "Base legal e linhagem — `we3d` (MIT), Superpack e o fonte `en_we2000edit`"
type: documentação
category: legal
phase: 0
depends_on: []
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §2"
status: pendente
---

# LOOKS-TASK-01: Base legal e linhagem

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §2.
- Este projeto se apoia em três materiais de fora, com três situações legais
  **diferentes**, e misturá-las é o erro a evitar.
- O repositório já tem o hábito: o [NOTICE.md](../../../NOTICE.md) registra o
  `WECompressor` e o `Easy-Mcr` do mesmo jeito.

---

## Objetivo

Registrar a linhagem **antes** de qualquer linha de código, para que nenhuma
fase seguinte precise parar para decidir se pode usar o que está usando.

---

## Critério de conclusão

- [ ] `NOTICE.md` ganha a seção do projeto `looks`, distinguindo os três casos:
      **`Darkensses/we3d` é MIT** e entra com crédito; o **Superpack v6** é
      coletânea de terceiros **sem licença**; o fonte **`en_we2000edit`**
      (Haplo/polipoli) não tem licença e serve como *testemunha*, não como
      código a copiar.
- [ ] Fica escrito que **nada do Superpack entra no git** — nem arquivo, nem
      transcrição longa —, na mesma regra de `roms/` e do `we-team-editor.exe`.
- [ ] O `.gitignore` é conferido: nenhum caminho do Superpack e nenhum
      `work/venv-looks/` pode ser versionado por descuido.
- [ ] A §2 do plano e este arquivo não se contradizem.

---

## Log de Execução

*(preencher ao executar)*
