---
id: CORR-K3D-013
---

# CORR-K3D-013 — FRAME_SLACK sozinho não sustenta "mesmo referencial"

Origin: [K3D-TASK-07](/docs/tasks/kits-3d/07-medir-geometria-edt-mod.md)

## Problem

O G3 conclui, a partir da [K3D-TASK-07](/docs/tasks/kits-3d/07-medir-geometria-edt-mod.md), que cada seção do `MODEL.BIN` mora no referencial da peça
dela — logo a matriz é a certa —, porque o deslocamento de ICP só de translação dá 0,7 a
1,9. O próprio controle da task mostra que essa métrica não enxerga um deslocamento de
20 unidades quando há outra peça no lugar: com todo braço movido 20 em y, as seções 99 e
100 saem com deslocamento 2,2 e 2,0, abaixo da folga de 3,0. Só são acusadas porque a
peça mais próxima mudou. O docstring de `FRAME_SLACK` ("with every arm moved 20 units the
run fails") esconde isso.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms --plant-edt-arms | grep -E "section +(99|100) "
  section  99 -> forearm a   (nearest EDT section 14 at 5.7, other part 14.2), frame offset 2.2 (+1.0,+1.8,+0.9)
  section 100 -> forearm b   (nearest EDT section 15 at 5.8, other part 14.2), frame offset 2.0 (+0.2,+1.8,-0.9)
  FAIL  section 99: on forearm a, the rule says upper arm a
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms --plant-edt-arms | grep -c "units out of"
11
```

## Root cause

Hipótese, coerente com a saída da planta: `frame_offset` é iteração de ponto mais
próximo a partir de zero e assenta no mínimo local da peça mais próxima, qualquer que
seja. Resíduo pequeno diz "está sobre alguma peça de braço", não "não se moveu".

## Fix

Em `tools/kits/oracle.py`, medir o referencial contra a peça atribuída só — reportar o
deslocamento até a peça de `ARM_PIECES`, não até a mais próxima, ou acrescentar um limite
de distância ajustada mais estrito —, e plantar um deslocamento que mantém a peça mais
próxima e quebra o referencial. Reescrever o G3 e o docstring de `FRAME_SLACK` de acordo.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- docs/KITS-AJUSTES-3D.md

## Verificação

```sh
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms --plant-edt-arms | grep -c "units out of"
```

Tem de contar toda seção plantada (18). Hoje conta 11.

## Log de Execução

- 2026-10-08 — triagem inline: **REPRODUCED**. Com a planta, `grep -c "units out of"` dava 11.
- `oracle.py`: `arm_match` mede o deslocamento contra a peça que `ARM_PIECES` dá à seção (a
  seção mais próxima com esse nome), não contra a mais próxima; `arms_report` passa a regra. O
  controle passou de 20 em y para `ARM_PLANT_SHIFT = (8, 0, 0)`: toda seção mantém a peça mais
  próxima e só o referencial a recusa. Docstrings de `FRAME_SLACK`/`ARM_PLANT_SHIFT` e o G3
  reescritos.
- Verificação:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms --plant-edt-arms | grep -c "units out of"
18
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms --plant-edt-arms | grep -c FAIL
18
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms | tail -1
  ok    every sleeve and armband section is in its EDT_MOD.BIN piece's frame (offset 1.9 at most, slack 3.0)
```

  A corrida sem planta imprime as mesmas 24 linhas que o G3 transcreve. `selftest.py`:
  `kits_selftest: 0 failure(s)`; `controls.py`: `controls: 34 of 34 red`.
- **Closed** — commit `a63b444` (2026-10-08): fix(kits): measure the arm frame offset against the rule's piece
  - Files (`git show --name-status a63b444`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/CORR-K3D-013.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/oracle.py`
