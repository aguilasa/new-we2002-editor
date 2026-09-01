---
id: PES2-TASK-10
title: "Fechamento da Fase 3 — o registro de jogador"
type: fechamento
category: verificação
phase: 3
depends_on: ["PES2-TASK-06", "PES2-TASK-07", "PES2-TASK-08", "PES2-TASK-09"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §7 (entregável da Fase 3)"
status: pendente
---

# PES2-TASK-10: Fechamento da Fase 3

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §7 — o entregável da Fase 3 é
  *"estrutura do registro de jogador"*.
- **Fase não fecha por soma de tasks.** Fecha quando o entregável existe e
  está verificado; esta task é onde isso se afirma com número.

---

## Objetivo

Consolidar as quatro tasks anteriores num documento único e verificado:
**estrutura do registro de jogador — campo, deslocamento, largura em bits e
domínio** — no cartão **e** no disco, com a relação entre os dois escrita.

### O que entra

| Vem de | O que |
|---|---|
| PES2-TASK-06 | os campos, pelo diferencial de cartão |
| PES2-TASK-07 | onde o mesmo registro mora no disco |
| PES2-TASK-08 | se há índice, e portanto se renomear pode crescer |
| PES2-TASK-09 | os elencos de clube, e a segunda família de nomes |

### O portão

Cada campo declarado tem de passar pelo teste da §4.1 — **o oráculo é o jogo
rodando**:

> um `poke` nele muda o que a tela mostra, do jeito previsto.

Campo que só foi visto no cartão e nunca no disco entra na tabela **marcado
como tal**, não como fechado. Campo mapeado "por analogia com o WE2002" não
entra (§4.4, §6.9).

---

## Critério de conclusão

- [ ] Seção nova no plano com a tabela de campos, cada linha com a evidência.
- [ ] Contagem: quantos campos a tela de edição expõe, quantos estão
      mapeados, quantos verificados por `poke`. Os três números, não um.
- [ ] O que ficou aberto, nomeado — e, para cada um, a via.
- [ ] `ctest -R pes2` verde, com o que a fase acrescentou registrado no
      `check_image.py`.
- [ ] O `docs/PES2-AJUSTES.md` §7 atualizado, ou aposentado se o backlog
      tiver migrado inteiro para as tasks.

---

## Log de Execução

*(a preencher)*
