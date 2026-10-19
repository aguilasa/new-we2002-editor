---
id: CORR-KRP-032
---

# CORR-KRP-032 — §4 data o desfazer em 2026-10-18, dia da decisão; o revert é de 2026-10-19

Origin: [KRP-TASK-25](/docs/tasks/concluidos/kits-replay/25-desfazer-a-krp-task-12-goleiro-volta-ao-edt-mod.md)

## Problem

A §4 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#4) diz "Desfeito em 2026-10-18". O commit
de revert e o `done_on` da task são de 2026-10-19; 2026-10-18 é o dia da decisão do usuário (Notas da
task). Como está escrita, a frase data o desfazer um dia antes de ele acontecer.

## Evidência

```text
$ git log -1 --format=%ad --date=short afbcf78c
2026-10-19
$ grep -n "Desfeito em" docs/PLAN-KITS-REPLAY.md
357:**Desfeito em 2026-10-18, por decisão do usuário**
```

## Root cause

(Hipótese.) A data da decisão foi copiada como data do desfazer.

## Fix

Na §4 do `docs/PLAN-KITS-REPLAY.md`, escrever "Desfeito em 2026-10-19, por decisão do usuário de
2026-10-18", ou equivalente.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-REPLAY.md`

## Verificação

```sh
grep -c "Desfeito em 2026-10-19" docs/PLAN-KITS-REPLAY.md
```

Hoje imprime 0. Depois do conserto tem de imprimir 1.

## Log de Execução

### 2026-10-19

Reprodução (`rite reproduce --all --cycle kits-replay`, HEAD `ab98809b`): `git log -1 --format=%ad
--date=short afbcf78c` deu `2026-10-19`, e `grep -n "Desfeito em" docs/PLAN-KITS-REPLAY.md` deu
`357:**Desfeito em 2026-10-18, por decisão do usuário**`.

Conserto: a frase da §4 virou `**Desfeito em 2026-10-19, por decisão do usuário de 2026-10-18**`. As
outras datas 2026-10-18 do plano e do perfil são de decisão do usuário e ficam.

Verificação:

```text
$ grep -c "Desfeito em 2026-10-19" docs/PLAN-KITS-REPLAY.md
1
```
- **Closed** — commit `928d3446` (2026-10-19): docs(kits): date the undo of phase 4 on the revert day, not the decision day
  - Files (`git show --name-status 928d3446`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/CORR-KRP-032.md`
