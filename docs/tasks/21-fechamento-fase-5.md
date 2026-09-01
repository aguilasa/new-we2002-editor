---
id: PES2-TASK-21
title: "Fechamento da Fase 5 — o portão da Fase 6"
type: fechamento
category: verificação
phase: 5
depends_on: ["PES2-TASK-04", "PES2-TASK-18", "PES2-TASK-20"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §0 (definição de pronto)"
status: pendente
---

# PES2-TASK-21: Fechamento da Fase 5

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §0, definição de pronto, e §5,
  Fase 6 — *"As três condições da §0 são o portão."*
- **Esta task é o portão.** Depois dela se decide linguagem e UI; antes
  dela, não.

---

## Objetivo

Verificar as três condições, cada uma com a medida ao lado.

| # | Condição | De onde vem a evidência |
|---|---|---|
| 1 | `pes2_map.json` versionado que localize, por campo, o **conjunto de cópias** | PES2-TASK-18 |
| 2 | uma ferramenta `pes2_poke` que altere um campo pelo mapa e o resultado **apareça na tela do emulador**, no menu certo, sem travar | PES2-TASK-02 e 04, agora dirigidas pelo mapa |
| 3 | round-trip: ler tudo pelo mapa, regravar sem editar, `.bin` **byte a byte idêntico** | PES2-TASK-20 |

A condição 2 merece nota: a PES2-TASK-04 a cumpriu para **um** campo, o nome
de time, com o gravador da PES2-TASK-02. Aqui ela vale para o `poke`
**dirigido pelo mapa** — que é outro programa, e precisa ser reexercitado em
pelo menos um campo de cada família (texto, numérico, campo de bits, cor).

---

## Critério de conclusão

- [ ] As três condições verificadas, com o número de cada uma.
- [ ] O `poke` pelo mapa exercitado em quatro famílias de campo, com captura.
- [ ] `ctest -R pes2` verde inteiro.
- [ ] Estado do plano atualizado: cabeçalho, §5 e §7, dizendo o que está
      fechado — com a mesma disciplina que a §3 do `PES2-AJUSTES.md` cobrou
      quando o cabeçalho dizia "nenhuma fase executada" com a Fase 0 pronta.
- [ ] Se alguma condição não passar, a Fase 6 **não começa** — e o que falta
      fica escrito aqui.

---

## Log de Execução

*(a preencher)*
