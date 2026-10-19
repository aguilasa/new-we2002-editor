---
id: KRP-TASK-26
---

# KRP-TASK-26 — Desfazer a KRP-TASK-13 e fechar a fase 4a

## Goal

O fechamento da fase 4 sai do plano e a fase 4a fica fechada: a linha "Feito na fase 4" do §4, que a [KRP-TASK-13](/docs/tasks/kits-replay/13-fechamento-da-fase-4.md) escreveu, dá lugar ao que a fase 4a deixou (o goleiro do `EDT_MOD.BIN` de volta); a tabela do §10 ganha a linha da 4a; os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 4a do perfil rodam de novo na HEAD.

## Arquivos a criar ou modificar

- In:
  - `docs/PLAN-KITS-REPLAY.md` (§4: a linha "Feito na fase 4" substituída pelo resultado da 4a; §10: a linha da fase 4a)
- Out:
  - código novo
  - o conserto do link da CORR-KRP-027 que a KRP-TASK-13 fez: fica

## Done criteria

- [ ] `grep -n "Feito na fase 4" docs/PLAN-KITS-REPLAY.md`: toda ocorrência está marcada como desfeita, datada, e o §4 traz "Feito na fase 4a" com o goleiro do `EDT_MOD.BIN`
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`
- [ ] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução
