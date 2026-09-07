---
id: MCR-TASK-02
title: "Base legal, linhagem e o SHA fixado do upstream"
type: documentação
category: processo
phase: 0
depends_on: ["MCR-TASK-01"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §2"
status: pendente
---

# MCR-TASK-02: Base legal e linhagem

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §2.
- O upstream **não tem licença** — sem `LICENSE`, sem cabeçalho de fonte,
  `"license": null` na API do GitHub, e um `<Copyright>Copyright © 2023</Copyright>`
  no `.vbproj`. O usuário decidiu portar literalmente, ciente disso, em
  2026-09-07.
- O repositório já vive nessa posição com `legacy/mfc/` (Moriero 2002,
  thyddralisk 2015), e por isso **não tem `LICENSE`**. A linhagem mora em
  [`NOTICE.md`](../../../NOTICE.md).

---

## Objetivo

Deixar a posição legível para quem chegar depois: de onde veio cada coisa, o
que é transcrição e o que é medição nossa, e por que o método aqui difere do
método do ciclo `wte/`.

---

## Critério de conclusão

- [ ] `NOTICE.md` com a entrada do upstream: autor (Zetaprog), URL, **SHA
      `30af1fe59cf96beee3b066f6cdfcb1b6f3df37cc`**, data (2026-05-27), e a
      constatação de que não há licença.
- [ ] O parágrafo que registra **a diferença de método**: no ciclo `wte/` o
      editor do Obocaman foi tratado como binário a medir, nunca a transcrever;
      aqui há fonte e o dono decidiu transcrever. As duas razões lado a lado —
      sem isso um leitor futuro conclui que a regra mudou sozinha.
- [ ] O upstream clonado em `work/easy-mcr/` (gitignored), com o inventário de
      arquivos e tamanhos registrado no Log — o repo tem 5 commits num dia só e
      pode sumir.
- [ ] Registrado o que **não entra**, e por quê: `BD.accdb`, as faces `.bmp`,
      os binários de `bin/`, o `.pfx` de assinatura e o cache do WebView2.
- [ ] Conferido que `.gitignore` cobre `work/` (já cobre) e que nada do
      upstream entrou: `git status` limpo depois do clone.

---

## Log de Execução

*(a preencher)*
