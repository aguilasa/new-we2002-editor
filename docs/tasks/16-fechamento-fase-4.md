---
id: PES2-TASK-16
title: "Fechamento da Fase 4 — o resto do banco"
type: fechamento
category: verificação
phase: 4
depends_on: ["PES2-TASK-11", "PES2-TASK-12", "PES2-TASK-13", "PES2-TASK-14", "PES2-TASK-15"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §7 (entregável da Fase 4)"
status: pendente
---

# PES2-TASK-16: Fechamento da Fase 4

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §7 — o entregável da Fase 4 é
  *"estrutura de time, formação, uniforme, bandeira, Master League"*.
- **O portão da fase é o da §4.1**, e o plano é explícito: *"Cada campo fecha
  com `poke` verificado no emulador — nenhum entra no mapa por analogia."*

---

## Objetivo

Consolidar as cinco tasks anteriores, e declarar o que está fechado e o que
não está — com número dos dois lados.

### A conta que esta task tem de fechar

| Eixo | Mapeado | Verificado por `poke` | Aberto |
|---|---|---|---|
| elenco por time | | | |
| formação | | | |
| uniforme e cores | | | |
| bandeira | | | |
| Master League | | | |

Uma linha por eixo, com os três números. Célula vazia não é resposta.

### O que fazer com o que ficou aberto

Cada campo aberto entra na Fase 5 **como lacuna declarada no mapa**, não como
omissão. O `pes2_map.json` que a PES2-TASK-17 desenha tem de saber dizer
"este campo existe e não está mapeado" — que é diferente de não mencioná-lo.

---

## Critério de conclusão

- [ ] A tabela acima preenchida, no plano.
- [ ] Nenhum campo declarado fechado sem `poke` verificado.
- [ ] O que ficou aberto, nomeado, com a via e o custo estimado.
- [ ] `ctest -R pes2` verde.
- [ ] Se a estatística empacou em algum eixo e a PES2-TASK-01 continua sem
      decisão, dizer aqui **qual** eixo a desmontagem destravaria.

---

## Log de Execução

*(a preencher)*
