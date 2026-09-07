---
id: MCR-TASK-12
title: "Gravação pela UI: ficha, formação e dorsais"
type: implementação
category: ui
phase: 3
depends_on: ["MCR-TASK-11"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §3"
status: pendente
---

# MCR-TASK-12: A UI em gravação

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §3 e §5.1.
- **O gate da MCR-TASK-10 é pré-requisito duro.** Gravação pela tela sem gate é
  a combinação que perde cartão do usuário.
- **O veredito do `0x6500` (MCR-TASK-13) muda o que esta tela desenha**: se for
  capitão, há um campo "capitão"; se for o sexto cobrador, há seis cobradores.
  Descobrir depois é refazer a tela.

---

## Objetivo

Editar e gravar pela janela, com a garantia de que o arquivo gravado continua
passando no round-trip.

---

## Critério de conclusão

- [ ] Edição de ficha, de dorsal, de papel e de posição no campo (arrastar),
      todas indo para o modelo e de lá para os bytes.
- [ ] **Gravar sempre em cópia por padrão**; sobrescrever o original exige
      confirmação explícita.
- [ ] O arquivo gravado pela UI passa no `mcr roundtrip` — a tela não pode
      produzir cartão que o núcleo recuse.
- [ ] Uma edição medida ponta a ponta: mudar um atributo pela tela muda
      exatamente os bytes previstos, e nada mais.
- [ ] O `0x6500` desenhado conforme o veredito da MCR-TASK-13, ou ausente se
      ela ainda não tiver fechado.
- [ ] Captura de tela no `:98`, antes e depois, anexada ao Log.
- [ ] Diálogo, confirmação e mensagem de erro da gravação **em en-US**, como o
      resto da UI (§3.5).

---

## Log de Execução

*(a preencher)*
