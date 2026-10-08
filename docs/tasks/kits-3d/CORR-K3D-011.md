---
id: CORR-K3D-011
---

# CORR-K3D-011 — Regra do disco ARM_PIECES sem gate no kits_image

Origin: [K3D-TASK-07](/docs/tasks/kits-3d/07-medir-geometria-edt-mod.md)

## Problem

Nenhum gate roda a medição da [K3D-TASK-07](/docs/tasks/kits-3d/07-medir-geometria-edt-mod.md) sobre o disco. `--edt-arms` não é chamado pelo
`selftest.py --image`, pelo `ctest` nem pelo `controls.py`. Os dois controles do catálogo
plantam defeito só em `arm_side` e `frame_offset`, que os casos sintéticos do selftest
usam com o próprio dicionário `rule`. Uma entrada errada em `ARM_PIECES` — a tabela de
onde a K3D-TASK-10 vai desenhar — deixa todo gate verde; só a pega quem rodar o oráculo
à mão.

## Evidência

```text
$ grep -rn "run_edt_arms\|ARM_PIECES" tools/kits/selftest.py tests/
(nada)
$ T=$(mktemp -d); git archive HEAD tools | tar -x -C $T; cd $T
$ python3 -c "p='tools/kits/oracle.py'; s=open(p).read(); open(p,'w').write(s.replace('93: \"upper arm b\", 95','93: \"upper arm a\", 95'))"
$ WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms | tail -1
  FAIL  section 93: on upper arm b, the rule says upper arm a      (rc=1)
$ WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image --quiet | tail -1
figure: 0 failure(s)      (rc=0)
```

## Root cause

A task acrescentou uma opção ao oráculo e casos sintéticos ao selftest, mas não ligou a
corrida no disco — 0,14 s, sem emulador — ao `selftest.py --image` (o `kits_image`).

## Fix

No `run_image` de `tools/kits/selftest.py`, conferir que `oracle.run_edt_arms(image)`
devolve 0 e que a corrida plantada devolve 1. No `tools/kits/controls.py`, uma entrada
que troca um valor de `ARM_PIECES` e espera a linha FAIL dessa conferência.

## Arquivos a criar ou modificar

- tools/kits/selftest.py
- tools/kits/controls.py

## Verificação

Com a planta de `ARM_PIECES[93]` acima numa cópia da árvore,
`WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image --quiet`
tem de sair diferente de zero. Hoje sai 0.

## Log de Execução

- 2026-10-08 — triagem: **REPRODUCED**, à mão. O `rite reproduce` roda cada linha da Evidência
  em separado, então o `cd $T` não valeu e a planta de `ARM_PIECES[93]` caiu na árvore do
  repositório; desfeita antes de qualquer edição (`git diff` sem a linha 93). Refeita numa cópia
  no scratchpad: `oracle.py --edt-arms` acusa a seção 93 e `selftest.py --image --quiet` termina
  em `figure: 0 failure(s)`, exit 0.
- `selftest.py`: `_edt_arms_checks` no `kits_image` — `oracle.run_edt_arms` sai 0 no disco, a
  corrida plantada sai 1 com uma linha `units out of` por seção de `ARM_PIECES`, e o juiz recusa a
  regra com a 93 trocada. O `controls.py` não ganhou entrada: ele roda a cópia sem o disco
  (`env.pop("WE2002_LOOKS_IMAGE")`), e por isso o vermelho visto mora no próprio `kits_image`.
- Verificação, com a planta da Evidência numa cópia da árvore:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image --quiet
  FAIL  oracle --edt-arms: every sleeve and armband section sits where ARM_PIECES says  exit 1; FAIL  section 93: on upper arm b, the rule says upper arm a
figure: 0 failure(s)
rc=1
```

  Na árvore sem planta: `ok    oracle --edt-arms: every sleeve and armband section sits where ARM_PIECES says`, `rc=0`.
  `controls.py`: `controls: 34 of 34 red`.
- **Closed** — commit `6cfab4a` (2026-10-08): test(kits): run oracle --edt-arms on the disc in kits_image
  - Files (`git show --name-status 6cfab4a`):
    - `M docs/tasks/kits-3d/CORR-K3D-011.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/selftest.py`
