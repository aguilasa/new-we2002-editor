---
id: KITS-TASK-41
---

# KITS-TASK-41 — Fechamento da fase 10

## Goal

A fase 10 e o ciclo conferidos na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [x] `ctest -R kits` na HEAD
- [x] As verificações da fase 10 do perfil, refeitas com comando
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

As KITS-TASK-42 e 43 entraram na fase 10 em 2026-10-05, depois desta task. O `depends_on` dela não as cita, porque o CLI não o reescreve. A `order` do ciclo as põe antes da 40 e desta, e o fechamento confere as duas como `done`. O mesmo vale para as KITS-TASK-44 a 47, abertas em 2026-10-06.

## Log de Execução

### 2026-10-07 — conferência na HEAD `4fbd2ed`

Estado do ciclo (`rite status --cycle kits`): 46 tasks feitas e esta em curso, fila de revisão vazia, nenhum fix aberto. As KITS-TASK-42 a 47 estão `done` e revisadas.

**`ctest -R kits`** (com `WE2002_LOOKS_IMAGE`, `WE2002_LOOKS_DRIVE_IMAGE`, `WE2002_KITS_ED_IMAGE`, `:98`):

```
18: kits_selftest: 0 failure(s)
19: kits_image: 0 failure(s)
21: kits_ui: 0 failure(s)
100% tests passed, 0 tests failed out of 4
```

**Verificações da fase 10 do perfil**, uma por uma:

1. **Texto novo no catálogo, nas duas línguas.** O selftest dá `2 language(s), 55 key(s) each: en-US, pt-BR` e `language: 0 failure(s)`. A varredura de literais fora de `tr()` está no mesmo `kits_selftest`, verde.
2. **O reset devolve o quadro de abertura.** O `kits_ui` dá `ok    Reset view and a double click after --yaw 0 --pitch 30 are the 3D as it opens, and the turn alone is not (double-click ae85c85db2de, opened ae85c85db2de, reset ae85c85db2de, turned acfaaac39894)`. As duas plantas do reset seguem vermelhas: o `kits_ui` tem 32 linhas de planta, e `kits_ui: 0 failure(s)`.
3. **Costas, número, braçadeira e manga só com a regra medida no jogo.**
   - `oracle.py --back 5 --page 576 --tag 14 --panels`, ao vivo: `ok    every panel holds the shirt back and its centred number`.
   - `--attach 5`: `ok    the figure is MODEL.BIN's, and section 93 takes the place of 97`.
   - `--attach-matrix 5`: `ok    long sleeves: every worn section has its own matrix, and section 93 is drawn where 97 is`.
   - `--attach-matrix 6 --sleeve-length short`: `ok    short sleeves: ... section 90 is drawn where 4 is`.
   - `--match-pose 5 --check`: `ok    tools/kits/core/match_pose.json is what this run measures`.
   - `--match-silhouette 5 --tag 14`: `ok    both figures within IoU 0.700 of the game's (worst 0.800 ...)`.
   - Os quatro com `--frame-json` sobre as capturas em `work/kits-oracle/`. O que não tem regra fica desligado com a frase (`kits_ui`: `ok    the dressing boxes: ... the dressings with no rule off with the sentence, in en-US and pt-BR`).
4. **Save state novo é decisão do usuário.** Os dois de partida são os que o usuário gravou: `sha256sum work/kits-states/SLPM-87056_5.sav` começa por `c08b761ad75bccc2`, e o `_6`, por `773aed606178d96a`, os mesmos registrados nas KITS-TASK-39 e 46.
5. **Manga longa só com o jogador de linha.** O mesmo juiz dos checkboxes afirma o checkbox escondido com o goleiro, e a planta `'Long sleeves always shown'` falha nele.

**`rite check --cycle kits`:** 0 erros. Dos dois avisos, um era desta task, a `depends_on` sem as KITS-TASK-42 a 47. Corrigi com `rite set KITS-TASK-41 --depends-on ...`. O outro é da KITS-TASK-20 (fase 4, sem a 36), e a CLI recusa mudá-lo: `rite: KITS-TASK-20 is done: its dependencies were the order it ran in`. Fica como aviso histórico, sem item aberto.

