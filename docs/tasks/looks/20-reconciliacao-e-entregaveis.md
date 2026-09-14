---
id: LOOKS-TASK-20
title: "Reconciliação do plano, `perfil-looks.md` e os entregáveis"
type: documentação
category: fechamento
phase: 7
depends_on: ["LOOKS-TASK-19"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §9"
status: pendente
---

# LOOKS-TASK-20: Reconciliação e fechamento

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §9.
- A regra do repositório: **o que a execução muda no plano, muda na seção que
  mudou**, não num apêndice de erratas. O banner do plano indexa as mudanças.
- As incógnitas da §6 ou foram respondidas, ou continuam abertas **com a razão
  medida** — nenhuma das duas coisas pode ficar implícita.

---

## Objetivo

Fechar o ciclo com plano, perfil e entregáveis batendo com o que existe no
disco.

---

## Critério de conclusão

- [ ] Cada incógnita da §6 tem veredito escrito: respondida (com a medição) ou
      aberta (com a razão e o que a destravaria).
- [ ] Cada afirmação da §1 que a execução tiver desmentido está **corrigida no
      lugar**, com a data e o que ela dizia antes.
- [ ] `perfil-looks.md` reflete as armadilhas que o ciclo realmente encontrou,
      e não só as previstas. **Duas já têm conserto medido**, encaminhadas
      pela [`LOOKS-TASK-04`](/docs/tasks/looks/04-formato-de-secao.md) em
      2026-09-14:
      - a **armadilha 2** diz “o par de zeros que separa grupos”; são **8
        bytes no `MODEL.BIN` e 12 nas duas primeiras folgas do
        `EDT_MOD.BIN`**, então a regra é *corrida de palavras zero*, e a
        forma fixa é que produz o `nPrim` na casa dos bilhões (§1.4);
      - a **armadilha 3** diz que varrer o `EDT_MOD.BIN` sem a lista
        “pega uma seção e para”. Com a regra da corrida a varredura
        **acha as onze e termina no EOF exato**; a lista continua
        necessária, mas pela **ordem** — que é outra (§1.5). Reescrever a
        armadilha pelo motivo certo vale mais que apagá-la.
- [ ] A definição de pronto da §0 é percorrida item a item, com o resultado de
      cada um.
- [ ] `python tools/check_tasks.py` verde, e a conferência de link do
      [.claude/rules/links.md](../../../.claude/rules/links.md) sem linha nova.
- [ ] `NOTICE.md` conferido contra o que o projeto de fato usou.
- [ ] **O `CLAUDE.md` ganha a seção do `looks`.** Ele descreve cinco
      projetos e não menciona o sexto — nem as duas variáveis da §4.5 do
      plano (`WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE`), nem o
      `work/venv-looks/`, nem os alvos de `ctest`. Encaminhado pela
      [`LOOKS-TASK-02`](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md)
      em 2026-09-14, que criou as duas variáveis e o venv: documentar no
      plano era o critério dela, e o `CLAUDE.md` é o arquivo que quem chega
      lê primeiro.

---

## Log de Execução

*(preencher ao executar)*
